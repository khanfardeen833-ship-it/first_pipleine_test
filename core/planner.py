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
You are a senior presentation strategist. Your outlines are used directly to \
generate slide decks — every field must be precise, specific, and data-driven.

Respond with ONLY valid JSON — no markdown, no commentary, no code fences.

━━━ OUTPUT SCHEMA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "title": "<short, bold deck title — 4-6 words max>",
  "theme": "<one-word tone: urgent|innovative|authoritative|inspiring|analytical>",
  "audience": "<who this is for: executives|investors|engineers|general|customers>",
  "slides": [
    {
      "slide_number": 1,
      "title": "<concise slide title — 4-6 words>",
      "type": "<see TYPES below>",
      "narrative_role": "<hook|problem|evidence|insight|solution|proof|objection|cta>",
      "headline": "<one specific claim — include a number if possible — max 12 words>",
      "key_points": ["<specific data point or action>", "..."],
      "visual": "<precise visual instruction — chart type, axes, key data, layout>",
      "bg": "<light|dark>"
    }
  ]
}

━━━ SLIDE TYPES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
hero         Opening statement or closing statement slide. Bold typography only.
             Use for: slide 1 (always) and optionally the final slide.
stat         One number IS the entire message. Put the number in the headline.
             Example headline: "Diagnoses improved by 94%"
chart        Trend, growth, or comparison data. Specify chart type in visual.
             Example visual: "Line chart: x=2020-2030, y=0-100%, two lines EV vs ICE"
comparison   Two sides: before/after, old/new, us/them. Two-column layout.
three_column Three parallel pillars of equal importance. Icon + title + body each.
table        Structured rows × columns data. Specify column headers in visual.
timeline     Sequential events or phases. Specify 3-5 milestones with dates.
quote        One specific person's exact words that validate the slide's claim.
             Include the person's name and title in key_points.
closing      Final call-to-action. What should the audience do RIGHT NOW?

━━━ HEADLINE QUALITY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every headline must make ONE specific, surprising claim.
Include a real number whenever possible.

✗ BAD  "AI is transforming healthcare"
✓ GOOD "AI matches radiologists in detecting breast cancer — 94.5% accuracy"

✗ BAD  "The market is growing rapidly"
✓ GOOD "EV market hits $623B in 2024, tripling in 3 years"

✗ BAD  "We need to act on climate change"
✓ GOOD "18 months to prevent 1.5°C — the window closes in 2026"

━━━ KEY POINTS QUALITY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Specific, data-driven, no vague claims. 2-4 points per slide.

✗ BAD  "Adoption is growing rapidly"
✓ GOOD "Enterprise AI spend: $67B in 2024, up 28% YoY (Gartner)"

✗ BAD  "Customers are satisfied"
✓ GOOD "NPS score jumped from 34 to 71 after AI rollout"

━━━ VISUAL QUALITY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Describe exactly what to draw — designer should need no imagination to execute.

✗ BAD  "Chart showing growth over time"
✓ GOOD "Area chart: x=2019-2024, y=0-500M users, shaded area under curve, \
label at 2024 peak '487M'"

✗ BAD  "Three boxes with icons"
✓ GOOD "Three cards left-to-right: (1) Battery icon + '1000mi range' (2) Bolt \
icon + '15min charge' (3) Dollar icon + '$45k avg price'. Dark card, white text."

━━━ NARRATIVE RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Slide 1: always hero + narrative_role=hook
- Last slide: always closing + narrative_role=cta
- Build a clear arc: hook → problem → evidence → insight → solution → proof → cta
- Alternate dark/light backgrounds for visual rhythm
- Never repeat the same slide type more than twice consecutively
"""


async def generate_outline(user_prompt: str, total_slides: int, run_dir=None) -> dict:
    """
    Generate a slide-by-slide outline using Haiku.

    If run_dir is provided, saves outline.json there too.
    Raises on API error so the caller can decide whether to abort or proceed.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_message = (
        f"Create a {total_slides}-slide presentation outline.\n\n"
        f"TOPIC / BRIEF:\n{user_prompt}\n\n"
        f"REQUIREMENTS:\n"
        f"- Exactly {total_slides} slides\n"
        f"- Slide 1 must be type=hero, narrative_role=hook\n"
        f"- Slide {total_slides} must be type=closing, narrative_role=cta\n"
        f"- Every headline must contain a specific number or data point\n"
        f"- Every visual description must be specific enough to draw without guessing\n"
        f"- Build a clear story arc across all {total_slides} slides\n\n"
        f"Return ONLY the JSON object."
    )

    _MODEL  = "claude-sonnet-4-6"          # Sonnet for outline quality
    _IN_PX  = 3.0 / 1_000_000              # $3 / M input tokens
    _OUT_PX = 15.0 / 1_000_000             # $15 / M output tokens

    print(f"\n--- planning {total_slides} slides (sonnet) ---")
    plan_start = time.time()

    response = await client.messages.create(
        model=_MODEL,
        max_tokens=8000,
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

    # Normalise: ensure required fields are always present
    for i, slide in enumerate(outline.get("slides", []), start=1):
        slide.setdefault("slide_number", i)
        slide.setdefault("narrative_role", "")
        slide.setdefault("bg", "dark" if i % 2 == 1 else "light")

    in_tok  = response.usage.input_tokens
    out_tok = response.usage.output_tokens
    cost    = in_tok * _IN_PX + out_tok * _OUT_PX

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
    print(f"\n{'='*64}")
    print(f"  DECK:     {outline.get('title', 'Untitled')}")
    print(f"  Theme:    {outline.get('theme', '')}   Audience: {outline.get('audience', '')}")
    print(f"{'='*64}")
    for s in outline.get("slides", []):
        bg_tag  = "[dark]" if s.get("bg") == "dark" else "[light]"
        role    = s.get("narrative_role", "")
        print(f"\n  Slide {s['slide_number']:>2} — {s['title']}  {bg_tag}  ({role})")
        print(f"     type: {s.get('type', '?')}")
        print(f" headline: {s.get('headline', '')}")
        for pt in s.get("key_points", []):
            print(f"      pt: {pt}")
        print(f"   visual: {s.get('visual', '')}")
    print(f"\n{'='*64}\n")
