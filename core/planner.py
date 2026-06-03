"""
Haiku planning phase: generates detailed slide plan for Opus design phase.
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions

from core.config import WORKSPACE
from core.tracker import Tracker
from core.renderer import render_message
from core.router import route_skills


async def plan_presentation(user_request: str, total_slides: int, tracker=None) -> dict:
    """
    Phase 1: Haiku planning phase.
    Analyzes user request, routes skills, and creates detailed slide plan.

    Args:
        user_request: User's presentation topic/request (e.g., "Build me a 10-slide deck about coffee")
        total_slides: Total number of slides to generate

    Returns:
        {
            "skill_routing": {
                "selected_skills": ["text", "chart", "image"],
                "excluded_skills": ["table", "icon", "shape"]
            },
            "slides": [
                {
                    "slide_number": 1,
                    "title": "Coffee: A Global Perspective",
                    "content_outline": "Introduction to coffee cultivation, origin, and industry overview",
                    "layout_hint": "Title + content slide",
                    "data_elements": [],
                    "image_prompt": "High-quality coffee plantation landscape with morning light"
                },
                ...
            ],
            "deck_metadata": {
                "title": "The Complete Guide to Coffee",
                "theme": "Professional with warm earth tones",
                "style_notes": "Modern, photography-focused, data visualization for charts"
            }
        }
    """

    # Phase 1: Route skills once (will be reused for all batches)
    selected_skills = route_skills(user_request)
    excluded_skills = {
        "02-text-element.md", "03-shape-element.md", "04-image-element.md",
        "05-icon-element.md", "06-chart-element.md", "07-table-element.md"
    } - {f"{skill.replace('_', '-').replace('.md', '')}-element.md"
         if not skill.endswith('-element.md') else skill
         for skill in selected_skills}

    # Build simple planning prompt (no element skills needed)
    planning_prompt = f"""
You are the planning and content phase for a presentation generator.

User Request: {user_request}
Total Slides: {total_slides}

Your task: Create a detailed content plan for {total_slides} slides.

Return ONLY valid JSON (no markdown, no code blocks, raw JSON) with this exact structure:
{{
    "skill_routing": {{
        "selected_skills": {json.dumps(sorted(list(selected_skills)))},
        "excluded_skills": {json.dumps(sorted([s.replace('-element.md', '').replace('-', '_') for s in excluded_skills if s != "02-text-element.md"]))}
    }},
    "slides": [
        {{
            "slide_number": 1,
            "title": "Slide Title Here",
            "content_outline": "Brief content outline for this slide",
            "layout_hint": "Which layout type (title_content, two_column, image_left, etc.)",
            "data_elements": [],
            "image_prompt": "If images needed: detailed visual description for image generation"
        }},
        ...
    ],
    "deck_metadata": {{
        "title": "Presentation Title",
        "theme": "Design theme (e.g., Professional, Creative, Minimalist)",
        "style_notes": "Key visual style guidance for the design phase"
    }}
}}

Requirements:
- Generate {total_slides} slides with logical flow
- Each slide must have: slide_number, title, content_outline, layout_hint, data_elements (array), image_prompt
- image_prompt should be detailed for the design phase to use when creating images
- Include slide numbers from 1 to {total_slides}
- Return ONLY the JSON object, no additional text
"""

    # Create temporary run directory for planning phase
    run_id = f"plan-{int(time.time() * 1000)}"
    plan_dir = WORKSPACE / run_id
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Simple system prompt for planning (no element skills)
    planning_system_prompt = """You are a presentation content planner.
Your job is to analyze user requests and create detailed structured plans for presentation generation.
Always respond with valid JSON only - no explanations, no markdown, just raw JSON."""

    # Write system prompt to file (Windows 32KB limit)
    sp_file = plan_dir / "_system_prompt.md"
    sp_file.write_text(planning_system_prompt, encoding="utf-8")

    # Use provided tracker or create new one
    if not tracker:
        tracker = Tracker("claude-haiku-4-5")

    # Set up options for Haiku
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        system_prompt={
            "type": "file",
            "path": str(sp_file),
            "cache_control": {"type": "ephemeral"}
        },
        allowed_tools=["Read", "Write", "Bash"],
        cwd=str(plan_dir),
        permission_mode="acceptEdits",
    )

    print(f"\n  [planning] starting Haiku planning phase")

    # Track phase timing
    if tracker:
        tracker.start_phase("planning")

    # Query Haiku for plan
    plan_json_text = ""
    try:
        async for message in query(prompt=planning_prompt, options=options):
            render_message(message, tracker)

            # Capture text responses that might contain JSON
            if hasattr(message, 'content') and message.content:
                for block in message.content if isinstance(message.content, list) else [message.content]:
                    if hasattr(block, 'text'):
                        plan_json_text += block.text
    except Exception as e:
        print(f"\n  [planning] exception: {e}")
        if tracker:
            tracker.last_error = str(e)
        raise
    finally:
        if tracker:
            tracker.end_phase()

    # Parse JSON response
    try:
        # Remove markdown code blocks if present
        plan_json_text = re.sub(r'^```(?:json)?\s*', '', plan_json_text)
        plan_json_text = re.sub(r'\s*```$', '', plan_json_text)
        plan_json_text = plan_json_text.strip()

        slide_plan = json.loads(plan_json_text)

        # Validate structure
        assert "slides" in slide_plan, "Missing 'slides' key in plan"
        assert "skill_routing" in slide_plan, "Missing 'skill_routing' key in plan"
        assert "deck_metadata" in slide_plan, "Missing 'deck_metadata' key in plan"
        assert len(slide_plan["slides"]) == total_slides, \
            f"Expected {total_slides} slides, got {len(slide_plan['slides'])}"

        print(f"  [planning] plan generated: {len(slide_plan['slides'])} slides")
        print(f"  [planning] skills selected: {slide_plan['skill_routing']['selected_skills']}")

        return slide_plan

    except json.JSONDecodeError as e:
        print(f"\n  [planning] JSON parse error: {e}")
        print(f"  [planning] raw response: {plan_json_text[:200]}")
        raise ValueError(f"Haiku did not return valid JSON: {e}")
    except AssertionError as e:
        print(f"\n  [planning] validation error: {e}")
        raise ValueError(f"Plan structure invalid: {e}")
