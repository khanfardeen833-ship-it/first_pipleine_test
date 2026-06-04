"""
Slide outline generator.

Produces a structured JSON outline for every slide before the full
design phase runs. The outline is saved to outline.json in the run
directory so the frontend can display it immediately.

Uses claude-haiku-4-5 (fast + cheap) — typically finishes in 10-20s.
"""

import json
import os
import time
from pathlib import Path

import anthropic


_OUTLINE_SYSTEM = """\
You are a presentation strategist. Given a topic and slide count, return a
JSON outline with one entry per slide.

Respond with ONLY valid JSON — no markdown fences, no commentary.

Schema:
{
  "title": "<deck title>",
  "slides": [
    {
      "slide_number": 1,
      "title": "<concise slide title>",
      "type": "<hero|stat|chart|table|comparison|three_column|timeline|quote|closing>",
      "headline": "<one punchy insight sentence>",
      "key_points": ["<point 1>", "<point 2>", "<point 3>"],
      "visual": "<short description of the visual: chart type, layout, key graphic>",
      "bg": "<light|dark>"
    }
  ]
}

Rules:
- Alternate light and dark backgrounds for visual rhythm
- Vary slide types — don't repeat the same type more than twice in a row
- key_points: 2-4 concise bullets
- headline: max 12 words, action-oriented
- visual: one sentence only
"""


async def generate_outline(user_prompt: str, total_slides: int, run_dir=None) -> dict:
    """
    Generate a slide-by-slide outline using Haiku.

    If run_dir is provided, saves outline.json there too.
    Raises on API error so the caller can decide whether to abort or proceed.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_message = (
        f"Create a {total_slides}-slide presentation outline for:\n\n{user_prompt}\n\n"
        f"Return exactly {total_slides} slides in the JSON array."
    )

    print(f"\n--- planning {total_slides} slides (haiku) ---")
    plan_start = time.time()

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=_OUTLINE_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )

    elapsed = time.time() - plan_start
    raw = response.content[0].text.strip()

    # Strip markdown fences if model wrapped the JSON anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    outline = json.loads(raw)

    # Normalise: ensure slide_number is always present
    for i, slide in enumerate(outline.get("slides", []), start=1):
        slide.setdefault("slide_number", i)

    in_tok  = response.usage.input_tokens
    out_tok = response.usage.output_tokens
    cost    = (in_tok * 0.8 + out_tok * 4.0) / 1_000_000   # Haiku pricing

    print(f"  outline ready in {elapsed:.1f}s  "
          f"({in_tok} in / {out_tok} out tokens, ~${cost:.4f})")

    # Save to disk only if a run_dir is provided
    if run_dir is not None:
        outline_path = run_dir / "outline.json"
        with open(outline_path, "w", encoding="utf-8") as f:
            json.dump(outline, f, indent=2)
        print(f"  saved -> {outline_path.name}")

    return outline


def print_outline(outline: dict) -> None:
    """Pretty-print the outline to the console."""
    print(f"\n{'='*60}")
    print(f"  DECK: {outline.get('title', 'Untitled')}")
    print(f"{'='*60}")
    for s in outline.get("slides", []):
        bg_tag = "[dark]" if s.get("bg") == "dark" else "[light]"
        print(f"\n  Slide {s['slide_number']:>2} — {s['title']}  {bg_tag}")
        print(f"           Type: {s.get('type', '?')}")
        print(f"       Headline: {s.get('headline', '')}")
        for pt in s.get("key_points", []):
            print(f"            - {pt}")
        print(f"         Visual: {s.get('visual', '')}")
    print(f"\n{'='*60}\n")
