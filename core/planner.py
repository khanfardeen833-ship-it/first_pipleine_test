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
You are a world-class presentation writer. Think like the team behind Gamma, \
Andreessen Horowitz memos, and TED Talk scripts — clear, opinionated, grounded \
in what is actually happening right now.

Respond with ONLY valid JSON — no markdown fences, no commentary.

━━━ OUTPUT SCHEMA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "title": "<punchy deck title — 5-8 words, provocative or insightful>",
  "subtitle": "<one sentence that expands the title — what the audience will learn>",
  "theme": "<urgent|innovative|analytical|inspiring|cautionary>",
  "audience": "<executives|investors|engineers|general|students|policymakers>",
  "slides": [
    {
      "slide_number": 1,
      "title": "<slide title — clear, specific, 4-7 words>",
      "type": "<hero|trend|context|stat|comparison|challenges|outlook|closing>",
      "points": [
        "<point 1 — one clear, natural sentence>",
        "<point 2>",
        "<point 3>"
      ],
      "speaker_note": "<what the presenter should say in 1-2 sentences — the 'why this matters'>",
      "visual": "<what to show: chart type / layout / key visual element>",
      "bg": "<light|dark>"
    }
  ]
}

━━━ SLIDE TYPES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
hero        Opening slide. Bold provocative statement. Sets the stage.
context     Before/after, then/now, landscape overview. 2-3 framing points.
trend       "Trend N: [Name]" — one major shift. 2-3 concrete signals of it.
stat        One big number tells the whole story. Surround with context.
comparison  Two sides: old vs new, leaders vs laggards, us vs them.
challenges  The real problems, tensions, risks. Honest and grounded.
outlook     What happens next. Predictions with reasoning, not just hope.
closing     Final thought. What the audience should do or remember.

━━━ CONTENT QUALITY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TITLE quality:
✗ "Artificial Intelligence Overview"
✓ "AI in 2026: From Hype to Enterprise Reality"
✓ "The Shifting AI Landscape: 2025 vs. 2026"

POINTS quality — short, natural, specific. Mix data + narrative + examples:
✗ "Adoption is increasing across industries."
✓ "2025: Focus on AGI debates and model-layer breakthroughs."
✓ "58% of companies report limited use of physical AI today, projected to reach 80% in two years."
✓ "Chinese LLMs like DeepSeek-R1 are challenging US dominance."
✓ "IBM's vision: everyone becomes an 'AI composer.'"
✓ "Example: Sales reps receiving real-time insights and actions during customer calls."

Points must be:
- Short (under 20 words each)
- Either a real data point, a named example, or a sharp observation
- Conversational — not consultant-speak
- 2-3 per slide (never more than 4)

NAMED ENTITIES — always use real names when possible:
Companies: OpenAI, Anthropic, Google DeepMind, Microsoft, Nvidia, IBM, Meta, DeepSeek
People: Sam Altman, Demis Hassabis, Jensen Huang, Satya Nadella
Products: GPT-4o, Claude 3.5, Gemini Ultra, Llama 3, DeepSeek-R1
Events/laws: EU AI Act, US Executive Order on AI, NIST AI RMF, China's Gen-AI Rules

SPEAKER NOTES — this is the insight the presenter adds verbally:
✗ "This slide talks about AI trends."
✓ "The key tension here is speed vs. control — most companies are moving fast on AI but still haven't figured out governance."

━━━ STRUCTURE RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Slide 1: always type=hero
- Last slide: always type=closing
- Alternate dark/light backgrounds
- Trend decks: use "Trend N: [Name]" as title for trend slides
- Tell a complete story: context → trends → challenges → outlook → action
- Never repeat the same slide type 3 times in a row
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
        f"- Slide 1 must be type=hero\n"
        f"- Slide {total_slides} must be type=closing\n"
        f"- Use real company names, products, and current events — no generic placeholders\n"
        f"- Each point must be a short, natural sentence (under 20 words)\n"
        f"- Mix data points, named examples, and sharp observations in the points\n"
        f"- speaker_note tells the presenter what to say verbally about each slide\n"
        f"- Tell a complete story across all {total_slides} slides\n\n"
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

    # Normalise: ensure required fields always present
    for i, slide in enumerate(outline.get("slides", []), start=1):
        slide.setdefault("slide_number", i)
        slide.setdefault("speaker_note", "")
        slide.setdefault("bg", "dark" if i % 2 == 1 else "light")
        # support both 'points' (new) and 'key_points' (legacy) field names
        if "key_points" in slide and "points" not in slide:
            slide["points"] = slide.pop("key_points")

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
    print(f"\n{'='*66}")
    print(f"  {outline.get('title', 'Untitled')}")
    print(f"  {outline.get('subtitle', '')}")
    print(f"  theme={outline.get('theme','')}  audience={outline.get('audience','')}")
    print(f"{'='*66}")
    for s in outline.get("slides", []):
        bg_tag = "[dark]" if s.get("bg") == "dark" else "[light]"
        print(f"\n  Slide {s['slide_number']:>2} — {s['title']}  [{s.get('type','?')}]  {bg_tag}")
        for pt in s.get("points", s.get("key_points", [])):
            print(f"    • {pt}")
        if s.get("speaker_note"):
            print(f"    ↳ {s['speaker_note']}")
    print(f"\n{'='*66}\n")
