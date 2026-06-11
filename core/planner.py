"""
Slide outline generator — Gamma-quality, PPT-ready.

Produces a structured JSON outline where every bullet is exactly
what will appear on the slide — short, specific, scannable.
"""

import json
import os
import time
from pathlib import Path

import anthropic


DEFAULT_OUTLINE_MODEL = "claude-haiku-4-5"


_OUTLINE_SYSTEM = """\
You are a presentation content expert. You create slide outlines for PowerPoint \
and Google Slides. Your output IS the slide content — every bullet will appear \
directly on the slide, exactly as you write it.

Respond with ONLY valid JSON — no markdown fences, no commentary.

━━━ SCHEMA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every slide uses the exact same JSON structure — no exceptions:

{
  "title": "<deck title — punchy, 5-8 words>",
  "subtitle": "<one sentence — what the audience will learn or walk away with>",
  "slides": [
    {
      "slide_number": 1,
      "title": "<slide heading — 4-7 words, specific>",
      "subtitle": "<optional one-line subheading, or null>",
      "layout": "<title_only | bullets | two_column | three_column | chart | table | quote | timeline>",
      "bullets": ["<bullet 1>", "<bullet 2>", "<bullet 3>"],
      "bg": "<dark | light>"
    }
  ]
}

━━━ LAYOUT GUIDE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALL layouts use the same "bullets" array. The layout field tells the frontend how to display them.

title_only   No bullets (empty array). Just title + subtitle.
bullets      2-4 bullet points displayed as a list.
two_column   4-6 bullets — frontend splits them evenly into two columns.
             Write bullets so first half = left column, second half = right column.
three_column Exactly 3 bullets — each becomes one card/column.
chart        2-4 bullets — first is the headline insight, rest are supporting data points.
table        3-5 bullets — first bullet is the row data (use commas to separate columns).
quote        2 bullets — first is the quote text, second is "— Name, Title, Company".
timeline     3-5 bullets — each is "YEAR: what happened".

━━━ SLIDE TITLE QUALITY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Make titles specific and opinionated. Never generic.

✗  "AI Overview"
✗  "Current Trends"
✓  "AI in 2026: From Hype to Enterprise Reality"
✓  "Trend 1: The Rise of Agentic AI"
✓  "The Shifting AI Landscape: 2025 vs. 2026"
✓  "The Deflating AI Bubble and Economic Impact"
✓  "AI for Science and National Security"

━━━ BULLET QUALITY — THIS IS THE MOST IMPORTANT SECTION ━━━━━━━━━━━━━━━━━━━
Bullets ARE the slide text. They must be:
  • SHORT — 8 to 15 words maximum per bullet
  • SPECIFIC — real names, real numbers, real events
  • VARIED — mix stats, observations, examples, and quotes within a slide
  • PPT-STYLE — scannable phrases, not full article paragraphs

USE THESE PREFIXES to add variety and clarity:
  "2025:" / "2026:"     — year-labeled facts
  "Example:"            — concrete real-world instance
  "Key insight:"        — sharp takeaway
  "Note:"               — important caveat
  "vs."                 — contrast or comparison within a bullet
  Quoted terms          — wrap concepts in "quotes" to signal they are coined terms

NEVER use "LEFT: ... | RIGHT: ..." in bullets — use the "columns" field for two_column slides.

GOOD BULLET EXAMPLES (study these carefully):
  "2025: Focus on AGI debates and model-layer breakthroughs."
  "2026: Shift to enterprise integration and tangible ROI."
  "AI agents moving from reactive tasks to proactive assistance."
  "\"Anticipate and deliver\" model transforming knowledge work."
  "Example: Sales reps receiving real-time insights during customer calls."
  "58% limited physical AI use today; projected 80% in two years."
  "Asia Pacific leading early implementation."
  "Training humanoid robots with vast datasets of human movements."
  "Chinese LLMs like DeepSeek-R1 challenging US dominance."
  "IBM's vision: everyone becomes an 'AI composer.'"
  "84% confident in AI ROI; only 25% expect full orchestration by 2026."
  "Similarities to dot-com bubble: high valuations, hype over profits."
  "OpenAI and Google DeepMind establishing AI for science teams."
  "EU's Tech Sovereignty Package driving new data residency requirements."
  "Nations deploying AI under their own laws, infrastructure, and data."

BAD BULLET EXAMPLES (never write like this):
  ✗ "Artificial intelligence adoption is increasing significantly across industries."
  ✗ "The enterprise AI market is experiencing considerable growth."
  ✗ "Organizations need to adapt their strategies to incorporate AI tools."
  ✗ "There are various challenges associated with scaling AI responsibly."

━━━ STRUCTURAL RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Slide 1: layout=title_only (opening statement slide)
- Last slide: layout=title_only or layout=bullets (closing / call to action)
- 2-4 bullets per slide (never more than 4)
- Alternate dark and light backgrounds for visual rhythm
- For trend-based topics: use "Trend N: [Name]" format for trend slide titles
- Build a logical story arc: context → trends/insights → challenges → outlook/cta
- Use real company names: OpenAI, Anthropic, Google DeepMind, Nvidia, Microsoft,
  IBM, Meta, DeepSeek, Tesla, Salesforce, Palantir, etc.
- Reference real events: EU AI Act, DeepSeek-R1, GPT-4o, Gemini 2.0, etc.
"""


async def generate_outline(user_prompt: str, total_slides: int, run_dir=None) -> dict:
    """
    Generate a Gamma-quality slide outline using the configured fast model.

    Every bullet in the returned JSON is ready to appear directly on a slide.
    If run_dir is provided, saves outline.json there too.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_message = (
        f"Create a {total_slides}-slide presentation outline.\n\n"
        f"TOPIC:\n{user_prompt}\n\n"
        f"RULES:\n"
        f"- Exactly {total_slides} slides\n"
        f"- Slide 1 must be layout=title_only\n"
        f"- Last slide must be layout=title_only or layout=bullets\n"
        f"- Every bullet must be 8-15 words — real slide text, not summaries\n"
        f"- Use real company names, product names, statistics, and current events\n"
        f"- Mix bullet styles: year-labeled facts, examples, quotes, stats, observations\n"
        f"- Trend topics: label slides 'Trend N: [Name]'\n"
        f"- 2-4 bullets per slide\n"
        f"- LAYOUT VARIETY IS MANDATORY: use at least 4 distinct layout types "
        f"across the deck; no more than a third of slides may be layout=bullets; "
        f"never two identical layouts back-to-back. Prefer two_column, "
        f"three_column, timeline, chart, quote, or table wherever the content fits\n\n"
        f"Return ONLY the JSON object."
    )

    model = os.environ.get("ANTHROPIC_OUTLINE_MODEL", DEFAULT_OUTLINE_MODEL)

    print(f"\n--- planning {total_slides} slides ({model}) ---")
    t0 = time.time()

    response = await client.messages.create(
        model=model,
        max_tokens=8000,
        system=_OUTLINE_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )

    elapsed = time.time() - t0
    raw = response.content[0].text.strip()

    # Strip markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # Extract first {...} block in case of any trailing text
    brace_start = raw.find("{")
    brace_end   = raw.rfind("}")
    if brace_start != -1 and brace_end != -1:
        raw = raw[brace_start:brace_end + 1]

    try:
        outline = json.loads(raw)
    except json.JSONDecodeError:
        # Try a second pass via the API asking for clean JSON
        repair_response = await client.messages.create(
            model=model,
            max_tokens=8000,
            system="Return ONLY valid JSON. Fix any syntax errors. No markdown, no commentary.",
            messages=[
                {"role": "user", "content": f"Fix this broken JSON and return it clean:\n\n{raw}"}
            ],
        )
        repaired = repair_response.content[0].text.strip()
        if repaired.startswith("```"):
            repaired = repaired.split("```")[1]
            if repaired.startswith("json"):
                repaired = repaired[4:]
            repaired = repaired.strip()
        outline = json.loads(repaired)

    # Normalise — every slide gets the same flat fields
    for i, slide in enumerate(outline.get("slides", []), start=1):
        slide.setdefault("slide_number", i)
        slide.setdefault("subtitle", None)
        slide.setdefault("layout", "bullets")
        slide.setdefault("bg", "dark" if i % 2 == 1 else "light")
        # Support legacy field names
        if "bullets" not in slide:
            slide["bullets"] = slide.pop("points", slide.pop("key_points", []))
        # Drop any stray columns/visual/headline fields from old schema
        for old_field in ("columns", "visual", "headline", "narrative_role",
                          "speaker_note", "type", "key_points", "points"):
            slide.pop(old_field, None)
        # Repair: if model still emitted LEFT:|RIGHT: strings, flatten into plain bullets
        cleaned = []
        for b in slide.get("bullets", []):
            if "LEFT:" in b and "RIGHT:" in b and "|" in b:
                parts = b.split("|")
                cleaned.append(parts[0].replace("LEFT:", "").strip())
                cleaned.append(parts[1].replace("RIGHT:", "").strip())
            elif b.startswith("LEFT:") or b.startswith("RIGHT:"):
                cleaned.append(b.replace("LEFT:", "").replace("RIGHT:", "").strip())
            else:
                cleaned.append(b)
        slide["bullets"] = cleaned

    in_tok  = response.usage.input_tokens
    out_tok = response.usage.output_tokens

    print(f"  done in {elapsed:.1f}s  ({in_tok} in / {out_tok} out)")

    if run_dir is not None:
        p = Path(run_dir) / "outline.json"
        p.write_text(json.dumps(outline, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  saved -> {p.name}")

    return outline


def print_outline(outline: dict) -> None:
    """Print the outline exactly like a Gamma-style preview."""
    width = 66
    print(f"\n{'='*width}")
    print(f"  {outline.get('title', 'Untitled')}")
    if outline.get("subtitle"):
        print(f"  {outline['subtitle']}")
    print(f"{'='*width}")
    for s in outline.get("slides", []):
        bg = "[dark]" if s.get("bg") == "dark" else "[light]"
        layout = s.get("layout", "bullets")
        print(f"\n  {s['title']}  [{layout}] {bg}")
        if s.get("subtitle"):
            print(f"  {s['subtitle']}")
        for b in s.get("bullets", []):
            print(f"  • {b}")
    print(f"\n{'='*width}\n")
