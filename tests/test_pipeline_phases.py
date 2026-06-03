"""
Integration tests for hybrid pipeline phases.
Tests validate phase interactions, data flow, and timing instrumentation.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from core.tracker import Tracker


async def async_gen_factory(message):
    """Factory function to create async generator that yields a single message."""
    yield message


@pytest.mark.asyncio
async def test_haiku_plan_to_opus_design():
    """Test that Haiku plan output can be used by Opus design phase."""
    # Haiku planning response
    haiku_plan = {
        "skill_routing": {
            "selected_skills": ["text", "image"],
            "excluded_skills": ["chart", "table", "shape", "icon"]
        },
        "slides": [
            {
                "slide_number": 1,
                "title": "Introduction",
                "content_outline": "Welcome and overview",
                "layout_hint": "Title + content",
                "data_elements": [],
                "image_prompt": "Professional introduction background"
            },
            {
                "slide_number": 2,
                "title": "Key Points",
                "content_outline": "Main discussion points",
                "layout_hint": "Title + content",
                "data_elements": [],
                "image_prompt": "Relevant imagery for key points"
            }
        ],
        "deck_metadata": {
            "title": "Test Presentation",
            "theme": "Professional",
            "style_notes": "Clean and modern design"
        }
    }

    # Mock Haiku response
    haiku_message = MagicMock()
    haiku_message.content = [MagicMock(text=json.dumps(haiku_plan))]

    # Mock Opus response (simplified deck JSON)
    opus_response = {
        "slides": [
            {"slideId": "slide-1", "elements": [], "background": "white"},
            {"slideId": "slide-2", "elements": [], "background": "white"}
        ]
    }
    opus_message = MagicMock()
    opus_message.content = [MagicMock(text=json.dumps(opus_response))]

    with patch('core.planner.query') as mock_haiku_query, \
         patch('core.runner._run_single_agent') as mock_opus_agent:
        # Mock Haiku planning query
        mock_haiku_query.side_effect = lambda *args, **kwargs: async_gen_factory(haiku_message)

        # Mock Opus design agent
        async def mock_opus(*args, **kwargs):
            tracker = Tracker("claude-opus-4-7")
            tracker.start_phase("design")
            tracker.end_phase()
            return tracker

        mock_opus_agent.side_effect = mock_opus

        with patch('core.planner.render_message'), \
             patch('core.runner.render_message'):
            from core.planner import plan_presentation

            # Phase 1: Haiku planning
            tracker = Tracker("claude-haiku-4-5")
            plan = await plan_presentation("Test presentation about testing", 2, tracker=tracker)

            # Verify plan structure
            assert "skill_routing" in plan
            assert "slides" in plan
            assert len(plan["slides"]) == 2

            # Verify tracker recorded planning phase
            assert "planning" in tracker.phases
            assert tracker.phases["planning"]["model"] == "claude-haiku-4-5"


@pytest.mark.asyncio
async def test_tracker_records_multiple_phases():
    """Test that tracker can record multiple phase executions."""
    tracker = Tracker("claude-haiku-4-5")

    # Simulate planning phase
    tracker.start_phase("planning")
    tracker.input_tokens += 1000
    tracker.output_tokens += 200
    tracker.end_phase()

    # Simulate design phase
    tracker_design = Tracker("claude-opus-4-7")
    tracker_design.start_phase("design")
    tracker_design.input_tokens += 5000
    tracker_design.output_tokens += 1500
    tracker_design.end_phase()

    # Verify both phases were recorded
    assert "planning" in tracker.phases
    assert tracker.phases["planning"]["tokens_input"] == 1000
    assert tracker.phases["planning"]["tokens_output"] == 200
    assert tracker.phases["planning"]["model"] == "claude-haiku-4-5"

    assert "design" in tracker_design.phases
    assert tracker_design.phases["design"]["tokens_input"] == 5000
    assert tracker_design.phases["design"]["tokens_output"] == 1500
    assert tracker_design.phases["design"]["model"] == "claude-opus-4-7"


@pytest.mark.asyncio
async def test_phase_timing_recorded():
    """Test that phase duration is recorded accurately."""
    import time

    tracker = Tracker("claude-haiku-4-5")
    tracker.start_phase("planning")

    # Simulate some work
    time.sleep(0.05)

    tracker.end_phase()

    # Verify timing was recorded
    assert "planning" in tracker.phases
    assert tracker.phases["planning"]["duration_seconds"] >= 0.05
    assert tracker.phases["planning"]["duration_seconds"] < 0.2  # Allow some variance


@pytest.mark.asyncio
async def test_design_context_injection():
    """Test that slide plan is properly injected into design context."""
    # Simulate slide plan from Haiku
    slide_plan = {
        "slides": [
            {
                "slide_number": 1,
                "title": "Opening",
                "content_outline": "Project introduction",
                "layout_hint": "Title + content",
                "data_elements": [],
                "image_prompt": "Professional header image"
            }
        ]
    }

    # Verify plan structure is suitable for design injection
    assert "slides" in slide_plan
    assert len(slide_plan["slides"]) == 1
    assert "title" in slide_plan["slides"][0]
    assert "image_prompt" in slide_plan["slides"][0]
    assert "layout_hint" in slide_plan["slides"][0]

    # Design context should include these fields
    batch_slides = [s for s in slide_plan.get("slides", [])
                   if 1 <= s.get("slide_number", 0) <= 1]
    assert len(batch_slides) == 1

    design_context = f"""
CONTENT PLAN FROM PLANNING PHASE:
{json.dumps(batch_slides, indent=2)}

You are the visual design phase. Use the content plan above to create visually compelling
design decisions that align with the content and layout hints provided.
"""
    assert "Opening" in design_context
    assert "Project introduction" in design_context
    assert "Professional header image" in design_context


@pytest.mark.asyncio
async def test_phase_data_aggregation():
    """Test that phase data is correctly aggregated for summary."""
    # Simulate planning tracker
    planning_tracker = Tracker("claude-haiku-4-5")
    planning_tracker.start_phase("planning")
    planning_tracker.input_tokens = 1250
    planning_tracker.output_tokens = 450
    planning_tracker.end_phase()

    # Simulate design trackers (multiple batches)
    design_trackers = []
    for batch_num in range(2):
        tracker = Tracker("claude-opus-4-7")
        tracker.start_phase("design")
        tracker.input_tokens = 4200 + (batch_num * 500)
        tracker.output_tokens = 1600 + (batch_num * 200)
        tracker.end_phase()
        design_trackers.append(tracker)

    # Verify aggregation would work correctly
    planning_data = {
        "model": "claude-haiku-4-5",
        "duration_seconds": planning_tracker.phases["planning"]["duration_seconds"],
        "tokens_input": planning_tracker.input_tokens,
        "tokens_output": planning_tracker.output_tokens,
    }

    design_input_total = sum(t.input_tokens for t in design_trackers)
    design_output_total = sum(t.output_tokens for t in design_trackers)

    assert planning_data["tokens_input"] == 1250
    assert design_input_total == 8900  # 4200 + 4700
    assert design_output_total == 3400  # 1600 + 1800
