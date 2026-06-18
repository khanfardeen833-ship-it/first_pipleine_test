"""
Per-slide parallel deck generation — no build.py, no agent SDK, no subprocess.

Each slide is one direct Anthropic API call that returns a compact "slide spec"
via a forced tool call (schema-enforced). The spec holds only the creative
decisions; deck_builder.py expands it deterministically into the full Bildory
JSON in-process. Slides share a cached system prefix (skills + design brief +
outline), so call 1 pays the cache write and the parallel rest pay cache reads.

Flow:
  outline + config
    -> slide 1 call   (warms prompt cache)
    -> slides 2..N    (parallel, cache hits)
    -> expand each spec through Deck/Slide primitives  (id_offset per slide)
    -> merge_presentations  (existing merger, unchanged)
"""

import asyncio
import hashlib
import inspect
import json
import os
import time
from pathlib import Path

import anthropic

from core.config import (
    CORE_SKILLS, ELEM_SKILLS, SKILLS_INDEX,
    CORE_SKILL_FILES, ELEMENT_SKILL_FILES, PROMPTS_DIR, DECK_BUILDER_API,
)
from core.merger import merge_presentations
from deck_builder import Deck

ID_OFFSET_PER_SLIDE = 100   # each slide owns a 100-wide element ID / zIndex band
MAX_TOKENS_PER_SLIDE = 9000
MAX_TOKENS_PLAN = 16000
THINKING_EFFORT = "high"    # adaptive thinking = the design deliberation the
                            # agent path gets for free; forced tool_choice
                            # would disable it, so we use auto + instruction
RETRIES_PER_SLIDE = 2
MIN_ELEMENTS_PER_SLIDE = 14   # premium floor — thin slides are rejected and retried

# Generation modes (env SLIDEGEN_MODE overrides):
#   fast     — forced tool call, no thinking, no plan. ~31s / ~$0.5
#   premium  — every slide thinks (effort=high). Best per-slide deliberation
#              but 8x redundant thinking. ~120s / ~$1.3
#   director — ONE deck-wide Opus thinking call writes a per-slide design
#              plan, then slides execute it in parallel without thinking.
#              Global design coherence, no redundant thinking. (default)
DEFAULT_MODE = "director"

# ---------------------------------------------------------------------------
# Forced tool — the model must emit a slide spec matching this schema.
# Element fields beyond "kind" mirror deck_builder kwargs 1:1; the expander
# whitelists them against the actual method signatures.
# ---------------------------------------------------------------------------
SLIDE_TOOL = {
    "name": "emit_slide",
    "description": (
        "Emit the complete design spec for one slide. Element fields use the "
        "deck_builder parameter names exactly (x, y, width, height, color, "
        "fill, font_size, style, shadow, overlay, ...). Omit any field whose "
        "value equals its documented default."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "background": {"type": "string", "description": "slide background color hex"},
            "elements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "kind": {
                            "type": "string",
                            "enum": ["text", "shape", "icon", "image", "chart", "table"],
                        },
                    },
                    "required": ["kind"],
                    "additionalProperties": True,
                },
            },
        },
        "required": ["background", "elements"],
    },
}

# Per-kind: (builder method name, ordered required positional spec fields)
_KIND_DISPATCH = {
    "text":  ("add_text",  ["text"]),
    "shape": ("add_shape", ["shape_type"]),
    "icon":  ("add_icon",  ["icon_name"]),
    "image": ("add_image", ["src"]),
    "chart": ("add_chart", ["chart_type", "chart_config"]),
    "table": ("add_table", ["cells"]),
}

# Friendly aliases the model might use for the positional field
_FIELD_ALIASES = {
    "shape": "shape_type",
    "icon": "icon_name",
    "name": "icon_name",
    "url": "src",
    "content": "text",
}


def _allowed_kwargs():
    from deck_builder import Slide
    allowed = {}
    for kind, (method, _) in _KIND_DISPATCH.items():
        params = inspect.signature(getattr(Slide, method)).parameters
        allowed[kind] = {p for p in params if p not in ("self",)}
    return allowed


_ALLOWED = _allowed_kwargs()


# ---------------------------------------------------------------------------
# Spec -> Bildory JSON (deterministic, in-process)
# ---------------------------------------------------------------------------
def expand_slide_spec(
    spec: dict,
    *,
    deck_title: str,
    slide_number: int,
    deck_id: str,
    timestamp: int,
) -> dict:
    """Expand one slide spec into a full single-slide Bildory deck dict."""
    deck = Deck(
        deck_title,
        id_offset=(slide_number - 1) * ID_OFFSET_PER_SLIDE,
        deck_id=deck_id,
        timestamp=timestamp,
    )
    slide = deck.add_slide(
        slide_id=f"slide-{slide_number}",
        background=spec.get("background", "#ffffff"),
    )
    for el in spec.get("elements", []):
        el = {_FIELD_ALIASES.get(k, k): v for k, v in el.items()}
        kind = el.pop("kind", None)
        if kind not in _KIND_DISPATCH:
            raise ValueError(f"unknown element kind: {kind!r}")
        # Image src is supplied by resolve_image_queries() from the element's
        # `query` after specs land; tolerate its absence here (e.g. the
        # per-slide validation probe runs before resolution).
        if kind == "image" and not el.get("src"):
            el["src"] = ""
        method, positional = _KIND_DISPATCH[kind]
        args = [el.pop(field) for field in positional]
        kwargs = {k: v for k, v in el.items() if k in _ALLOWED[kind]}
        getattr(slide, method)(*args, **kwargs)
    return deck.to_dict()


# ---------------------------------------------------------------------------
# Prompt assembly — large stable prefix + per-deck block, both cache-marked
# ---------------------------------------------------------------------------
def _skills_block() -> str:
    sections = ["### SKILLS INDEX\n" + SKILLS_INDEX.read_text(encoding="utf-8")]
    for fname in CORE_SKILL_FILES:
        sections.append(f"### {fname}\n" + (CORE_SKILLS / fname).read_text(encoding="utf-8"))
    for fname in ELEMENT_SKILL_FILES:
        sections.append(f"### {fname}\n" + (ELEM_SKILLS / fname).read_text(encoding="utf-8"))
    sections.append("### deck_builder parameter reference\n"
                    + DECK_BUILDER_API.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(sections)


_SPEC_INSTRUCTIONS = """\
You design ONE presentation slide per request and return it via the emit_slide tool.

SPEC FORMAT:
- "background": slide background color (hex).
- "elements": array in z-order (first = bottom). Each element has "kind"
  (text | shape | icon | image | chart | table) plus the deck_builder
  parameters for that primitive, using the exact parameter names:
    text:  text, type (title|subtitle|heading|subheading|paragraph|caption),
           x, y, width, height, color, font_size, font_weight, line_height,
           font_family, text_align, rotation, style
    shape: shape_type, x, y, width, height, fill, stroke, stroke_width,
           opacity, rotation
    icon:  icon_name, x, y, size, color, opacity, rotation
    image: query, x, y, width, height, is_background, border_radius, opacity,
           rotation, object_fit, filter, blur, scale_x, scale_y, shadow,
           border, overlay, crop_ratio, crop_rect, focus_point
           (use "query": 2-5 literal subject words, e.g. "bubble tea pastel
           cups" — a real Pexels search fills in src. NEVER hand-write a
           photos/{id} URL: a guessed id returns a random, irrelevant photo.)
    chart: chart_type, chart_config, x, y, width, height
    table: cells, x, y, col_widths, row_heights, font_size, table_color,
           table_bg, table_bold, table_italic, table_align

RULES:
- Canvas is 1280x720. Follow all design skills above exactly as if writing
  deck_builder calls — same quality bar, same palettes, same layout rules.
- NEVER include a field whose value equals its documented default
  (see OMIT DEFAULTS reference). shadow/border/overlay/style are partial
  dicts merged over defaults.
- Apply the DESIGN BRIEF below to every slide so the deck looks coherent.
- Use the slide outline entry you are given as the content plan.
- Think through the composition first, then call emit_slide exactly once.

PREMIUM DESIGN REQUIREMENTS — this is a paid, agency-grade deck:
- Follow the COMPOSITION ARCHETYPE assigned in the request. It dictates the
  slide's structural skeleton; never fall back to a plain bullet list.
- Layer deliberately: background field -> decorative geometry (offset panels,
  accent bars, thin rules) -> content cards/panels -> imagery with intentional
  filter+overlay -> icon badges -> typography. Aim for 18-30 elements; 14 is
  the HARD MINIMUM for every slide — including title, quote, and closing
  slides. Specs with fewer than 14 elements are rejected and regenerated.
- Reach the element count with purposeful layers, never clutter. The premium
  toolkit: kicker chip (small outlined/filled rect + letterspaced caption),
  thin accent rules (2-4px shapes), corner frame ticks, layered offset panels
  behind content blocks, vertical divider lines between columns, ellipse icon
  badges, a stat ribbon (number + label pairs separated by thin dividers),
  duotone image panels, and the page-number caption.
- Typography hierarchy must be dramatic: one oversized anchor (a 54-72pt
  headline or a 60-90pt stat) per slide.
- Ghost glyphs (oversized background numbers/letters) are a rationed garnish,
  not a default: only add one where the ART DIRECTOR PLAN explicitly calls for
  it, at 4-7% opacity maximum, placed in genuinely empty canvas — NEVER under
  or touching body text, stats, cards, or other content.
- Extract numbers from the content and showcase them BIG (stat treatment),
  don't bury them in sentences.
- Asymmetry beats symmetry: vary card sizes, offset images, use 40/60 or
  30/70 splits, bleed one image or shape off-canvas (never text).
- Every card/panel gets breathing room: consistent internal padding (>=24px),
  consistent corner radii, aligned baselines across siblings.

LEGIBILITY IS NON-NEGOTIABLE — violating any of these fails the slide:
- Text elements must never overlap each other or sit under decorative
  elements. Size every text box to its content (height >= number of lines x
  font_size x line_height) before placing neighbors.
- ALL text stays fully inside the safe zone: x >= 48, y >= 48,
  x + width <= 1232, y + height <= 672. Only images and shapes may bleed
  off-canvas. Page-number captions sit at y <= 672 too.
- Stat labels and card captions are 3-7 words and wrap to at most 2 lines —
  if a label needs 3 lines, shorten the wording, don't shrink the font.
- Text placed over a photo requires a dark overlay (opacity 45-70) or a solid
  color panel behind it — never raw text on a busy image.
"""

# Composition archetypes — rotated so adjacent slides never share a skeleton.
_ARCHETYPES_BY_LAYOUT = {
    "title_only": [
        ("full-bleed hero", "Full-canvas image (filter + dark overlay 55-70) or deep color field, "
         "kicker chip (outlined rect + letterspaced caption), 58-72pt title on the left 55%, thin "
         "accent rule, one-line subtitle. Layer it rich: corner frame ticks (4 thin shapes), a "
         "bottom stat ribbon (3 number+label pairs with thin vertical dividers), a second scrim "
         "panel for depth, page caption. Optional ghost glyph at 4-6% opacity in empty canvas "
         "only. Target 16-20 elements."),
        ("split hero", "Left 45%: color panel with kicker chip, huge title, accent bar, 2-3 "
         "supporting caption rows with tiny icon badges. Right 55%: full-height image with "
         "filter and palette-tinted overlay plus a floating stat chip card overlapping the seam. "
         "Corner ticks or a thin frame inset on the panel side. Target 16-20 elements."),
        ("editorial masthead", "Magazine-cover feel: an ULTRA-large display title (72-92pt) set "
         "low-left against generous whitespace, a top metadata rule (letterspaced section / date / "
         "edition split by thin vertical dividers), a hairline baseline grid (2-3 thin rules), a "
         "small corner monogram or logotype, and one restrained accent mark. Imagery optional and "
         "muted. Premium through scale + emptiness. Target 14-18 elements."),
        ("centered monolith", "Symmetric luxury: title perfectly centered on a deep color field, "
         "a hairline rectangle framing the composition with inset margins, a small crest/monogram "
         "or icon above the title, a letterspaced kicker below a short centered accent rule, and a "
         "one-line subtitle. Corner ticks at all four corners. No photo — restraint reads "
         "expensive. Target 14-17 elements."),
    ],
    "bullets": [
        ("stat band", "Pull the numbers out of the bullets and set them 60-90pt across a band of "
         "3-4 stat blocks (number + thin divider + 2-line caption each). Side or bottom: one "
         "supporting image panel or icon-accented insight card."),
        ("icon card grid", "Each bullet becomes a card: rounded panel (subtle tint or stroke), "
         "ellipse icon badge, 4-6 word heading, short caption. Asymmetric grid — one card 1.5x "
         "wider or taller than the others."),
        ("numbered editorial", "Vertical list with refined number labels 01/02/03 (24-32pt, "
         "accent color, full opacity) in the left gutter of each row — clear of the row text — "
         "left accent bars, heading + caption per row. Right 30-40%: full-height image with "
         "overlay."),
        ("split feature", "Left 40%: full-height image, palette overlay, one stat or kicker "
         "overlaid on it. Right 60%: bullets as compact mini-cards with icon badges, staggered "
         "x-offsets so rows don't form a flat list."),
        ("editorial index", "Luxury report contents-page feel: each bullet is a full-width row "
         "with a refined right-aligned number or short value, a hairline rule separating rows, "
         "a small letterspaced label on the left and a one-line description, generous vertical "
         "rhythm. A thin accent rule and section kicker up top. Whitespace-forward, no cards."),
        ("feature + sidebar", "One DOMINANT insight on the left 58-62% — oversized number or "
         "heading (60-90pt) with a short supporting line and an accent rule — beside a hairline-"
         "ruled sidebar of 2-3 secondary points (small icon + label + caption). Strong hierarchy: "
         "one hero idea, the rest deliberately quieter."),
    ],
    "two_column": [
        ("dual panel", "Two contrasting panels (one tinted/filled, one outlined or white) with "
         "column headers + icon badges; bullets split between them as aligned rows. A vertical "
         "divider or floating badge bridges the two."),
        ("versus split", "Hard 50/50 split with opposing background tones, oversized column "
         "labels, mirrored row layout, central circular 'VS'/theme badge overlapping the seam."),
        ("indexed ledger", "Editorial two-column ledger: a heavy left label rail (an oversized "
         "vertical word, large 01/02, or a tall accent bar) anchors the slide; the right side "
         "stacks the two column contents as rows divided by hairline rules with letterspaced "
         "headers and aligned values. Restrained, grid-locked, premium."),
    ],
    "three_column": [
        ("three cards", "Three equal cards with top icon badges, bold 3-5 word headings, "
         "captions, and a footer accent bar each; middle card elevated (taller or tinted) for "
         "rhythm."),
        ("offset trio", "Three columns at staggered vertical offsets (a descending or zig-zag "
         "step), alternating filled vs. outlined treatment, a thin through-line or connecting "
         "dots linking their badge centers, oversized 01/02/03 numerals behind each heading. "
         "One column carries a photo strip or tint for weight."),
        ("ribbon trio", "A continuous top ribbon/band spanning all three columns carries the "
         "kicker; below it three blocks each lead with a 60-90pt number or icon medallion, a "
         "3-5 word heading and 2-line caption, divided by thin vertical rules. Optional bottom "
         "photo strip bleeding off-canvas for energy."),
    ],
    "timeline": [
        ("horizontal timeline", "Baseline connector line with circle year-badges, alternating "
         "labels above/below, accent dot for the 'now' marker, years set 26-34pt bold. "
         "Optional ghost year at 4-6% opacity in an empty corner, clear of all labels."),
        ("vertical milestones", "Left rail with connector line and numbered/year badges, each "
         "milestone a row card to the right; final milestone highlighted with filled accent "
         "panel."),
        ("stepped ascent", "Milestones climb left-to-right on an ascending diagonal connector, "
         "each node a year badge with the step elevated higher than the last (a rising-trajectory "
         "feel), labels in alternating clean caption blocks, the final 'now' node enlarged with a "
         "filled accent ring. Thin guide rules underneath for polish."),
    ],
    "chart": [
        ("chart + callout", "Chart on one side (55-65% width), headline insight as a big-stat "
         "callout card beside it, supporting points as small icon rows under the callout."),
        ("hero chart", "Chart is the hero — 70-80% width, set on a subtle tinted plot panel with "
         "a clear title; a horizontal ribbon of 2-3 stat callouts (number + 2-line caption + thin "
         "dividers) runs along the top or bottom. Minimal side text; let the data dominate."),
        ("split data story", "Left half: the chart over a tinted panel. Right half: a stacked "
         "narrative — the single bold takeaway line (28-36pt) on top, then 3 insight rows with "
         "icon badges and short captions. A vertical accent rule splits the two halves."),
    ],
    "quote": [
        ("editorial quote", "Oversized quotation-mark glyph (180-260pt text or shapes, low "
         "opacity), 34-44pt italic quote centered-left on a layered offset panel, attribution "
         "caption with accent rule and a small ellipse initial-badge, muted full-bleed image or "
         "deep color field behind. Flank with thin frame rules, corner ticks, and 2-3 small "
         "proof chips (metric + label) along the bottom. Target 15-18 elements."),
        ("centered statement", "No image — a huge centered 40-56pt statement on a deep color "
         "field, with generous breathing room. Tiny letterspaced attribution below a short accent "
         "rule. Minimal flanking marks (a pair of corner ticks or one low-opacity glyph). "
         "Confidence through restraint and scale."),
        ("portrait quote", "Left 40%: full-height portrait/subject image with a palette-tinted "
         "overlay and a small initial-badge. Right 60%: the quote (30-40pt) on a layered offset "
         "panel, attribution with accent rule, and 2 small proof chips. A floating quotation mark "
         "overlaps the image seam."),
    ],
    "table": [
        ("framed table", "Table inside a framed panel with a heading row above it, one key-number "
         "callout chip beside/above the table, accent header treatment."),
        ("comparison matrix", "Table as a comparison grid: accent-filled header row, zebra row "
         "tints for scanability, and ONE highlighted winning column or row (stronger accent tint "
         "+ a small badge/checkmark) so the recommendation pops. Row-label column slightly wider."),
        ("scorecard grid", "Table read as a scorecard: each data cell pairs its value with a tiny "
         "icon, rating dot, or tier chip; bold accent header band; a floating key-number callout "
         "chip overlapping a top corner of the frame. Generous cell padding."),
    ],
}


DESIGN_PLAN_TOOL = {
    "name": "emit_design_plan",
    "description": "Emit the deck-wide design plan: one detailed entry per slide.",
    "input_schema": {
        "type": "object",
        "properties": {
            "deck_notes": {
                "type": "string",
                "description": "Deck-wide design decisions: exact hex usage, type scale, "
                               "card/corner/padding system, recurring motifs.",
            },
            "slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "slide_number": {"type": "integer"},
                        "plan": {
                            "type": "string",
                            "description": "60-140 words: composition skeleton, the oversized "
                                           "typographic anchor, background, accent usage, image "
                                           "subject + filter/overlay treatment (or none), and "
                                           "what makes this slide structurally distinct.",
                        },
                    },
                    "required": ["slide_number", "plan"],
                },
            },
        },
        "required": ["slides"],
    },
}


_NOTES_RE = None  # compiled lazily (re imported below)


def _parse_partial_plan(buf: str) -> tuple[str | None, dict[int, str]]:
    """Parse a PARTIAL emit_design_plan tool-input JSON string.
    Returns (deck_notes or None, {slide_number: plan}) for the slide entries
    that are already complete in the buffer — used to launch slide executors
    while the art director is still writing the rest of the plan."""
    import re
    global _NOTES_RE
    if _NOTES_RE is None:
        _NOTES_RE = re.compile(r'"deck_notes"\s*:\s*"((?:[^"\\]|\\.)*)"')

    notes = None
    m = _NOTES_RE.search(buf)
    if m:
        try:
            notes = json.loads('"' + m.group(1) + '"')
        except ValueError:
            notes = None

    entries: dict[int, str] = {}
    i = buf.find('"slides"')
    i = buf.find("[", i) if i != -1 else -1
    if i == -1:
        return notes, entries
    depth, start, in_str, esc_next = 0, None, False, False
    for j in range(i + 1, len(buf)):
        c = buf[j]
        if in_str:
            if esc_next:
                esc_next = False
            elif c == "\\":
                esc_next = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            if depth == 0:
                start = j
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(buf[start:j + 1])
                    if "slide_number" in obj and "plan" in obj:
                        entries[int(obj["slide_number"])] = obj["plan"]
                except (ValueError, TypeError):
                    pass
                start = None
        elif c == "]" and depth == 0:
            break
    return notes, entries


def _palette_is_auto(config: dict) -> bool:
    """True when no palette is pinned — 'auto', empty, or omitted."""
    return str((config or {}).get("palette") or "auto").strip().lower() == "auto"


def _font_is_auto(config: dict) -> bool:
    """True when no font is pinned — 'auto', empty, or omitted."""
    return str((config or {}).get("fontFamily") or "auto").strip().lower() == "auto"


async def _design_plan(client, model, system, outline, archetypes, usage_acc,
                       palette_auto: bool = False, font_auto: bool = False,
                       on_entry=None) -> dict:
    """One deck-wide Opus thinking call → {slide_number: plan_text}.

    With on_entry set, the response is STREAMED and on_entry(slide_number,
    plan_text) fires as soon as that slide's plan entry is complete in the
    partial JSON — so slide executors start while the plan is still being
    written. Entries only stream once deck_notes is known (it precedes the
    slides array in the schema); otherwise everything launches at the end.
    Same model/prompt/output either way — pure pipelining."""
    listing = "\n".join(
        f"  slide {i}: [{s.get('layout','bullets')}] archetype \"{a[0]}\" — {s.get('title','')}"
        for i, (s, a) in enumerate(zip(outline.get("slides", []), archetypes), start=1)
    )
    palette_clause = ""
    if palette_auto:
        palette_clause = (
            "PALETTE IS AUTO: before planning, choose the ONE palette from the 14 in "
            "11-visual-design-guide.md whose MOOD matches this topic, then commit to it "
            "deck-wide. Match by subject, not by habit:\n"
            "  - Playful / consumer / food & drink / lifestyle / kids / social / events "
            "→ bright & saturated: Coral Energy, Cherry Bold, Teal Trust, Ocean Gradient.\n"
            "  - Wellness / nature / heritage / craft / education → Forest & Moss, "
            "Sage Calm, Warm Terracotta, Berry & Cream.\n"
            "  - Tech / product / SaaS / data → Graphite & Electric, Midnight Executive, "
            "Ocean Gradient.\n"
            "  - Premium / finance / luxury / executive / consulting → Noir & Champagne, "
            "Deep Navy & Gold, Charcoal Minimal, Ivory Editorial.\n"
            "Do NOT default to a dark or premium palette for a light, playful, or "
            "everyday topic — a fun subject in Noir & Champagne reads wrong. Reserve "
            "near-black/metallic palettes for genuinely premium subjects. Name the chosen "
            "palette and its exact hexes in deck_notes; every slide uses only it.\n\n"
        )
    if font_auto:
        palette_clause += (
            "FONT IS AUTO: pick the heading/body pairing from the Typography "
            "Pairings table in 11-visual-design-guide.md that matches this topic's "
            "mood (PowerPoint-safe fonts only). Name both fonts in deck_notes; "
            "every slide must use that pairing.\n\n"
        )
    msg = (
        "You are the ART DIRECTOR for this deck. Think through the entire deck's "
        "design as one coherent system, then call emit_design_plan exactly once.\n\n"
        f"SLIDES AND ASSIGNED ARCHETYPES:\n{listing}\n\n"
        f"{palette_clause}"
        "For every slide write a precise, executable plan (60-140 words) following its "
        "archetype and the PREMIUM DESIGN REQUIREMENTS: composition skeleton with rough "
        "geometry, the oversized typographic anchor (what + size range), background and "
        "accent hexes from the palette, image subject + filter/overlay treatment (or "
        "'no image'), and the one distinctive touch that separates it from its neighbors. "
        "Plan every slide — title, quote, and closer included — dense enough to land "
        "18-30 layered elements (hard floor 14): enumerate the decorative layers "
        "(kicker chips, accent rules, corner ticks, offset panels, icon badges, stat "
        "ribbons, dividers), not just the content blocks. "
        "Decide deck-wide rhythm deliberately: where imagery clusters, where pure "
        "typography breathes, how dark/light alternation lands.\n\n"
        "Premium reads as RESTRAINT: generous whitespace, disciplined alignment, "
        "high contrast, one metallic or sharp accent used sparingly. Ration ghost "
        "glyphs to at most 2 slides in the whole deck (title and/or closer) — most "
        "slides get none. Keep stat labels to 3-7 words. Every text element must "
        "land fully inside the 48px safe zone (x 48-1232, y 48-672); plan layouts "
        "so nothing forces text to the canvas edge."
    )
    request = dict(
        model=model,
        max_tokens=MAX_TOKENS_PLAN,
        thinking={"type": "adaptive"},
        extra_body={"output_config": {"effort": THINKING_EFFORT}},
        system=system,
        # same tools array as the executor calls — tools are part of the cached
        # prefix, so any difference would invalidate the cache for all slides
        tools=[SLIDE_TOOL, DESIGN_PLAN_TOOL],
        tool_choice={"type": "auto"},
        messages=[{"role": "user", "content": msg}],
    )
    if on_entry is not None:
        buf, streamed = "", set()
        async with client.messages.stream(**request) as stream:
            async for event in stream:
                if (getattr(event, "type", "") == "content_block_delta"
                        and getattr(event.delta, "type", "") == "input_json_delta"):
                    buf += event.delta.partial_json
                    notes_p, entries = _parse_partial_plan(buf)
                    if notes_p is None:
                        continue
                    for n, plan_text in entries.items():
                        if n not in streamed:
                            streamed.add(n)
                            on_entry(n, f"DECK-WIDE SYSTEM: {notes_p}\n\n"
                                        f"THIS SLIDE: {plan_text}")
            resp = await stream.get_final_message()
    else:
        resp = await client.messages.create(**request)
    usage_acc.append(resp.usage)
    plan = next((b.input for b in resp.content if b.type == "tool_use"), None)
    if plan is None:
        raise ValueError("art director returned no emit_design_plan call")
    notes = plan.get("deck_notes", "")
    out = {}
    for entry in plan.get("slides", []):
        text = entry["plan"]
        if notes:
            text = f"DECK-WIDE SYSTEM: {notes}\n\nTHIS SLIDE: {text}"
        out[int(entry["slide_number"])] = text
    return out


async def warm_static_prefix() -> None:
    """1-token call that caches the outline-INDEPENDENT prefix (tools + skills
    block). Fire this concurrently with outline generation: by the time the
    art director call starts, its ~60k-token skills prefix is a cache read
    instead of a fresh prefill — saves ~5s on the plan call. Non-fatal."""
    try:
        client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
        system = [{
            "type": "text",
            "text": _skills_block() + "\n\n---\n\n" + _SPEC_INSTRUCTIONS,
            "cache_control": {"type": "ephemeral"},
        }]
        await client.messages.create(
            model=model, max_tokens=1, system=system,
            tools=[SLIDE_TOOL, DESIGN_PLAN_TOOL],
            messages=[{"role": "user", "content": "warm"}],
        )
    except Exception as e:
        print(f"  [slidegen] static prefix warm failed (non-fatal): {e}")


async def _warm_executor_cache(client, model, system, usage_acc) -> None:
    """1-token call with the executors' EXACT settings (forced tool, no
    thinking) so their cache entry exists before they fan out. The cache
    prefix is keyed on tools + tool_choice + thinking config, so the art
    director's cache entry is unusable by the executors."""
    resp = await client.messages.create(
        model=model,
        max_tokens=1,
        system=system,
        tools=[SLIDE_TOOL, DESIGN_PLAN_TOOL],
        tool_choice={"type": "tool", "name": "emit_slide"},
        messages=[{"role": "user", "content": "warm"}],
    )
    usage_acc.append(resp.usage)


def _deck_seed(outline: dict) -> int:
    """Stable per-deck offset derived from the title, so two decks pick different
    archetypes for layouts that appear only once (chart/table/quote). Stable hash
    (not Python's salted hash) → same topic reproduces, different topics vary."""
    title = (outline or {}).get("title", "") or ""
    return int(hashlib.sha1(title.encode("utf-8")).hexdigest(), 16)


def assign_archetypes(slides: list, seed: int = 0) -> list:
    """Pick a composition archetype per slide, rotating within each layout type
    so adjacent slides (and repeated layouts) never share a skeleton. `seed`
    shifts each layout's starting point so single-occurrence layouts differ
    across decks instead of always landing on the first archetype."""
    counters: dict[str, int] = {}
    out = []
    for s in slides:
        layout = s.get("layout", "bullets")
        pool = _ARCHETYPES_BY_LAYOUT.get(layout, _ARCHETYPES_BY_LAYOUT["bullets"])
        i = counters.get(layout, 0)
        out.append(pool[(i + seed) % len(pool)])
        counters[layout] = i + 1
    return out


def build_slidegen_system(outline: dict, config: dict) -> list:
    """System blocks: [stable skills prefix (cached), per-deck brief (cached)]."""
    config = config or {}
    if _palette_is_auto(config):
        palette_line = (
            "AUTO — the ART DIRECTOR PLAN names the deck palette; follow it "
            "exactly. If no plan is given, choose the single best-fitting palette "
            "from 11-visual-design-guide.md for this topic and use it on every slide"
        )
    else:
        palette_line = f"{config.get('palette')} (from 11-visual-design-guide.md)"
    if _font_is_auto(config):
        font_line = (
            "AUTO — the ART DIRECTOR PLAN names the heading/body pairing; follow "
            "it exactly. If no plan is given, pick the Typography Pairings entry "
            "from 11-visual-design-guide.md that fits the topic (never Google fonts)"
        )
    else:
        font_line = f"{config.get('fontFamily')} (do NOT use Google fonts)"
    brief = f"""DESIGN BRIEF (identical for every slide of this deck):
  Deck title: {outline.get('title', 'Untitled')}
  Deck subtitle: {outline.get('subtitle', '')}
  Total slides: {len(outline.get('slides', []))}
  Density: {config.get('density', 'Standard')}
  Audience: {config.get('audience', 'Executive Leadership')}
  Tone: {config.get('tone', '') or 'none specified'}
  Font Family: {font_line}
  Font Size: {config.get('fontSize', 'Medium')}
  Palette: {palette_line}
  Image Source: {config.get('imageSource', 'pexels')}
  Page Numbers: {config.get('pageNumbers', True)} (caption bottom-right, "NN / NN")

FULL DECK OUTLINE (for narrative + visual-rhythm context):
{json.dumps(outline, indent=2)}
"""
    return [
        {
            "type": "text",
            "text": _skills_block() + "\n\n---\n\n" + _SPEC_INSTRUCTIONS,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": brief,
            "cache_control": {"type": "ephemeral"},
        },
    ]


def _slide_user_message(outline: dict, slide_entry: dict, slide_number: int,
                        archetype: tuple, neighbors: str,
                        plan_text: str | None = None) -> str:
    total = len(outline.get("slides", []))
    name, desc = archetype
    plan_block = ""
    if plan_text:
        plan_block = (
            f"\nART DIRECTOR PLAN — execute this precisely; all creative "
            f"decisions are already made:\n{plan_text}\n"
        )
    return (
        f"Design slide {slide_number} of {total}.\n\n"
        f"OUTLINE ENTRY:\n{json.dumps(slide_entry, indent=2)}\n\n"
        f"COMPOSITION ARCHETYPE (mandatory skeleton): {name}\n{desc}\n"
        f"{plan_block}\n"
        f"Adjacent slides use: {neighbors} — this slide must read as a clearly "
        f"different structure at a glance.\n\n"
        f"CONSTRAINTS:\n"
        f"- slideId is \"slide-{slide_number}\"; element IDs and zIndex are handled "
        f"for you — never include id/zIndex fields\n"
        f"- Background per the outline 'bg' hint and the deck palette\n"
        f"- Emit the spec via emit_slide."
    )


_SAFE_CLAMP_MAX = 40  # px — nudge small violations only; bigger = intentional


def _clamp_text_safe_zone(merged: dict) -> int:
    """Deterministically nudge text elements fully inside the 48px safe zone
    (48..1232 x, 48..672 y) when they overshoot by <= _SAFE_CLAMP_MAX px —
    the classic offender is the page-number caption a few px below the line.
    Larger violations are left alone (and get caught by validation/QA).
    Returns the number of elements moved. Geometry lives in the changelog."""
    fixed = 0
    for s in merged["files"]["changelog"]["slides"].values():
        for eid, rec in s.get("elements", {}).items():
            if not eid.startswith("text"):
                continue
            pos = rec.get("position") or {}
            x, y = pos.get("x", 0), pos.get("y", 0)
            w, h = rec.get("width", 0), rec.get("height", 0)
            nx, ny = x, y
            if x + w > 1232 and (x + w) - 1232 <= _SAFE_CLAMP_MAX:
                nx = 1232 - w
            if nx < 48 and 48 - nx <= _SAFE_CLAMP_MAX:
                nx = 48
            if nx + w > 1232:           # can't satisfy both edges — leave it
                nx = x
            if y + h > 672 and (y + h) - 672 <= _SAFE_CLAMP_MAX:
                ny = 672 - h
            if ny < 48 and 48 - ny <= _SAFE_CLAMP_MAX:
                ny = 48
            if ny + h > 672:
                ny = y
            if (nx, ny) != (x, y):
                pos["x"], pos["y"] = nx, ny
                fixed += 1
    return fixed


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
async def _generate_one(client, model, system, outline, slide_entry, slide_number,
                        usage_acc: list, archetype: tuple, neighbors: str,
                        plan_text: str | None = None, think: bool = True,
                        qa_feedback: str | None = None) -> dict:
    last_err = None
    if think:
        # adaptive thinking needs tool_choice auto; forced tool would disable it
        kwargs = {
            "thinking": {"type": "adaptive"},
            "extra_body": {"output_config": {"effort": THINKING_EFFORT}},
            "tool_choice": {"type": "auto"},
        }
    else:
        kwargs = {"tool_choice": {"type": "tool", "name": "emit_slide"}}
    feedback = ""
    for attempt in range(1 + RETRIES_PER_SLIDE):
        try:
            content = _slide_user_message(outline, slide_entry, slide_number,
                                          archetype, neighbors, plan_text)
            if qa_feedback:
                content += f"\n\nVISUAL QA FEEDBACK on the previous version of this slide:\n{qa_feedback}"
            if feedback:
                content += f"\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED: {feedback}"
            resp = await client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS_PER_SLIDE,
                system=system,
                # both tools always — identical prefix = cache hits across calls
                tools=[SLIDE_TOOL, DESIGN_PLAN_TOOL],
                messages=[{"role": "user", "content": content}],
                **kwargs,
            )
            usage_acc.append(resp.usage)
            spec = next((b.input for b in resp.content if b.type == "tool_use"), None)
            if spec is None:
                raise ValueError("model returned no emit_slide call")
            # fail fast here so a broken spec retries while we're still parallel
            expand_slide_spec(spec, deck_title="probe", slide_number=slide_number,
                              deck_id="probe", timestamp=0)
            n_elements = len(spec.get("elements", []))
            if n_elements < MIN_ELEMENTS_PER_SLIDE and attempt < RETRIES_PER_SLIDE:
                feedback = (
                    f"only {n_elements} elements — the premium floor is "
                    f"{MIN_ELEMENTS_PER_SLIDE}. Keep the same composition but layer "
                    f"it richer: kicker chip, accent rules, corner ticks, offset "
                    f"panels, icon badges, stat ribbon, dividers, page caption."
                )
                print(f"  [slide-{slide_number}] attempt {attempt + 1} too thin "
                      f"({n_elements} elements) — regenerating richer")
                continue
            return spec
        except Exception as e:
            last_err = e
            print(f"  [slide-{slide_number}] attempt {attempt + 1} failed: {e}")
    raise RuntimeError(f"slide {slide_number} failed after retries: {last_err}")


async def generate_deck_per_slide(outline: dict, config: dict | None = None,
                                  run_dir: Path | None = None,
                                  mode: str | None = None,
                                  on_deck_ready=None) -> tuple[dict, dict]:
    """
    Generate a full deck with one parallel API call per slide.
    mode: fast | premium | director (default: env SLIDEGEN_MODE or 'director').
    on_deck_ready: optional async callback(merged, stats) invoked the moment
    the first merged deck is written — BEFORE the visual QA loop — so callers
    can deliver the deck immediately and patch the QA-improved slides after.
    Returns (merged_deck_dict, stats).
    """
    config = config or {}
    mode = mode or os.environ.get("SLIDEGEN_MODE", DEFAULT_MODE)
    if mode not in ("fast", "premium", "director"):
        raise ValueError(f"unknown SLIDEGEN_MODE: {mode!r}")
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    slides = outline.get("slides", [])
    if not slides:
        raise ValueError("outline has no slides")

    system = build_slidegen_system(outline, config)
    usage_acc: list = []
    archetypes = assign_archetypes(slides, seed=_deck_seed(outline))
    think = mode == "premium"

    def neighbors_of(i):  # 1-based slide number
        names = []
        if i >= 2:
            names.append(f"slide {i-1}: {archetypes[i-2][0]}")
        if i < len(slides):
            names.append(f"slide {i+1}: {archetypes[i][0]}")
        return "; ".join(names) or "none"

    t0 = time.time()
    plans: dict = {}

    if mode == "director":
        # The plan call STREAMS: each slide's executor launches the moment its
        # plan entry is complete, overlapping slide generation with the rest
        # of the planning. Executors gate on the cache warmer so every one of
        # them hits the prompt cache instead of racing to write it.
        print(f"  [slidegen] art director planning {len(slides)} slides "
              f"(effort={THINKING_EFFORT}; streaming — slides start as their "
              f"plan entries land)")
        warm_task = asyncio.create_task(
            _warm_executor_cache(client, model, system, usage_acc))
        slide_tasks: dict[int, asyncio.Task] = {}

        async def _run_slide(i: int, plan_text: str | None):
            await warm_task  # cache entry must exist before executors fan out
            return await _generate_one(client, model, system, outline,
                                       slides[i - 1], i, usage_acc,
                                       archetypes[i - 1], neighbors_of(i),
                                       plan_text=plan_text, think=False)

        def _launch(i: int, plan_text: str | None):
            if 1 <= i <= len(slides) and i not in slide_tasks:
                print(f"  [slidegen] plan for slide {i} ready "
                      f"({time.time() - t0:.1f}s) — executing")
                slide_tasks[i] = asyncio.create_task(_run_slide(i, plan_text))

        try:
            plans = await _design_plan(client, model, system, outline,
                                       archetypes, usage_acc,
                                       palette_auto=_palette_is_auto(config),
                                       font_auto=_font_is_auto(config),
                                       on_entry=_launch)
        except BaseException:
            for t in slide_tasks.values():
                t.cancel()
            warm_task.cancel()
            raise
        t_warm = time.time() - t0
        print(f"  [slidegen] plan complete in {t_warm:.1f}s — "
              f"{len(slide_tasks)}/{len(slides)} slides started early")
        for i in range(1, len(slides) + 1):
            _launch(i, plans.get(i))  # anything the stream didn't catch
        specs = list(await asyncio.gather(*[
            slide_tasks[i] for i in range(1, len(slides) + 1)
        ]))
    else:
        # Warm the cache with slide 1, then fan out the rest in parallel.
        print(f"  [slidegen] slide 1/{len(slides)} (cache warm-up, mode={mode})")
        first_spec = await _generate_one(client, model, system, outline,
                                         slides[0], 1, usage_acc,
                                         archetypes[0], neighbors_of(1), think=think)
        t_warm = time.time() - t0
        print(f"  [slidegen] slides 2..{len(slides)} in parallel "
              f"(warm-up took {t_warm:.1f}s)")
        rest = await asyncio.gather(*[
            _generate_one(client, model, system, outline, entry, i, usage_acc,
                          archetypes[i-1], neighbors_of(i), think=think)
            for i, entry in enumerate(slides[1:], start=2)
        ])
        specs = [first_spec] + list(rest)
    t_gen = time.time() - t0

    # Resolve image-element `query` strings into real Pexels URLs BEFORE download
    # (the model can't guess valid photo IDs, so a fabricated src is a random
    # photo). Must finish before prefetch so the cache pulls the resolved URLs.
    from core.pexels import resolve_image_queries
    await resolve_image_queries(specs)

    # Download every referenced image into run_dir/images/ while we expand and
    # merge — the QA renderer and the PPTX exporter both reuse the local copies.
    prefetch_task = None
    if run_dir is not None:
        from core.image_cache import prefetch_images
        prefetch_task = asyncio.create_task(
            prefetch_images(specs, Path(run_dir)))

    # Deterministic expansion + merge (existing merger, via temp files)
    now = int(time.time() * 1000)
    deck_id = f"deck-{now}"
    title = outline.get("title", "Untitled")
    part_paths = []
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="slidegen-"))
    for i, spec in enumerate(specs, start=1):
        part = expand_slide_spec(spec, deck_title=title, slide_number=i,
                                 deck_id=deck_id, timestamp=now)
        p = tmp / f"slide-{i}.json"
        p.write_text(json.dumps(part), encoding="utf-8")
        part_paths.append(p)
    merged = merge_presentations(part_paths)
    merged["presentation"]["description"] = outline.get("subtitle", "")
    clamped = _clamp_text_safe_zone(merged)
    if clamped:
        print(f"  [slidegen] auto-clamped {clamped} text element(s) into the safe zone")
    t_total = time.time() - t0

    stats = {
        "mode": mode,
        "slides": len(slides),
        "warmup_seconds": round(t_warm, 1),
        "generation_seconds": round(t_gen, 1),
        "total_seconds": round(t_total, 1),
        "input_tokens": sum(u.input_tokens for u in usage_acc),
        "output_tokens": sum(u.output_tokens for u in usage_acc),
        "cache_write": sum(getattr(u, "cache_creation_input_tokens", 0) or 0 for u in usage_acc),
        "cache_read": sum(getattr(u, "cache_read_input_tokens", 0) or 0 for u in usage_acc),
        "api_calls": len(usage_acc),
    }
    # Opus pricing: in $5/M, out $25/M, 5m-cache write $6.25/M, read $0.5/M
    stats["cost_usd"] = round(
        stats["input_tokens"] * 5 / 1e6
        + stats["output_tokens"] * 25 / 1e6
        + stats["cache_write"] * 6.25 / 1e6
        + stats["cache_read"] * 0.5 / 1e6, 4)

    if run_dir is not None:
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "merged_deck.json").write_text(
            json.dumps(merged, indent=2), encoding="utf-8")
        if plans:
            (run_dir / "design_plan.json").write_text(
                json.dumps(plans, indent=2), encoding="utf-8")
        if prefetch_task is not None:
            await prefetch_task  # manifest must exist before QA render / export

        # Deliver-then-patch: hand the deck to the caller NOW; the QA loop
        # below improves slides in place and the caller patches afterwards.
        if on_deck_ready is not None:
            try:
                await on_deck_ready(merged, stats)
            except Exception as e:
                print(f"  [slidegen] on_deck_ready callback failed (non-fatal): {e}")

        # ── Visual QA loop: screenshot + vision judge, regenerate failures ──
        if os.environ.get("SLIDEGEN_VISUAL_QA", "0") == "1":
            from core.image_cache import prefetch_images
            from core.visual_qa import run_visual_qa, format_feedback, print_report

            t_qa = time.time()
            report = await run_visual_qa(run_dir, outline=outline, plans=plans)
            print_report(report)
            failing = [r for r in report["slides"] if not r["pass"]]
            qa_stats = {
                "initial_scores": {r["slide_number"]: r["score"]
                                   for r in report["slides"]},
                "regenerated": [], "reverted": [],
                "judge_tokens": dict(report["tokens"]),
            }

            if failing:
                nums = [r["slide_number"] for r in failing]
                print(f"  [visual-qa] regenerating slide(s) {nums} with feedback")
                old_specs = {n: specs[n - 1] for n in nums}
                new_specs = await asyncio.gather(*[
                    _generate_one(client, model, system, outline,
                                  slides[r["slide_number"] - 1],
                                  r["slide_number"], usage_acc,
                                  archetypes[r["slide_number"] - 1],
                                  neighbors_of(r["slide_number"]),
                                  plan_text=plans.get(r["slide_number"]),
                                  think=False,
                                  qa_feedback=format_feedback(r))
                    for r in failing
                ])

                def _remerge():
                    m = merge_presentations(part_paths)
                    m["presentation"]["description"] = outline.get("subtitle", "")
                    _clamp_text_safe_zone(m)
                    (run_dir / "merged_deck.json").write_text(
                        json.dumps(m, indent=2), encoding="utf-8")
                    return m

                def _write_part(n, spec):
                    specs[n - 1] = spec
                    part = expand_slide_spec(spec, deck_title=title,
                                             slide_number=n,
                                             deck_id=deck_id, timestamp=now)
                    part_paths[n - 1].write_text(json.dumps(part),
                                                 encoding="utf-8")

                await resolve_image_queries(new_specs)  # query -> real Pexels URL
                for r, spec in zip(failing, new_specs):
                    _write_part(r["slide_number"], spec)
                    qa_stats["regenerated"].append(r["slide_number"])
                await prefetch_images(new_specs, run_dir)  # new image URLs
                merged = _remerge()

                # re-judge only the regenerated slides; revert any that got worse
                report2 = await run_visual_qa(run_dir, outline=outline,
                                              plans=plans,
                                              only_slides=set(nums))
                new_by_n = {r["slide_number"]: r for r in report2["slides"]}
                old_by_n = {r["slide_number"]: r for r in failing}
                reverted = False
                for n in nums:
                    if new_by_n[n]["score"] < old_by_n[n]["score"]:
                        print(f"  [visual-qa] slide {n} got worse "
                              f"({old_by_n[n]['score']} -> {new_by_n[n]['score']}) "
                              f"— keeping original")
                        _write_part(n, old_specs[n])
                        qa_stats["reverted"].append(n)
                        reverted = True
                if reverted:
                    merged = _remerge()
                qa_stats["final_scores"] = {
                    n: (old_by_n[n]["score"] if n in qa_stats["reverted"]
                        else new_by_n[n]["score"])
                    for n in nums
                }
                qa_stats["judge_tokens"]["input"] += report2["tokens"]["input"]
                qa_stats["judge_tokens"]["output"] += report2["tokens"]["output"]

            qa_stats["seconds"] = round(time.time() - t_qa, 1)
            stats["visual_qa"] = qa_stats
            stats["total_seconds"] = round(time.time() - t0, 1)
            print(f"  [visual-qa] done in {qa_stats['seconds']}s — "
                  f"regenerated {len(qa_stats['regenerated'])}, "
                  f"reverted {len(qa_stats['reverted'])}")

        (run_dir / "slidegen_stats.json").write_text(
            json.dumps(stats, indent=2), encoding="utf-8")
    return merged, stats
