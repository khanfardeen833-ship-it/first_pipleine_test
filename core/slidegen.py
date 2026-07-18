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
import random
import re
import time
from pathlib import Path

import anthropic

from core.config import (
    CORE_SKILLS, ELEM_SKILLS, SKILLS_INDEX,
    CORE_SKILL_FILES, ELEMENT_SKILL_FILES, PROMPTS_DIR, DECK_BUILDER_API,
)
from core.layouts import (
    build_library, archetypes_by_layout, select_layouts,
    selected_layouts_block, estimate_tokens,
)
from core.merger import merge_presentations, write_deck_outputs
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
                            "enum": ["text", "shape", "icon", "image", "chart", "table", "motif"],
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
    "motif": ("add_motif", ["motif_type"]),
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
        if kind == "motif":
            el.setdefault("motif_type", "plexus")
            # Per-(run,slide) seed so the motif varies between runs but is stable
            # within one (probe + final + QA expand to the same art).
            el.setdefault("seed", (int(timestamp) + slide_number * 131) & 0xFFFFF)
        method, positional = _KIND_DISPATCH[kind]
        args = [el.pop(field) for field in positional]
        kwargs = {k: v for k, v in el.items() if k in _ALLOWED[kind]}
        getattr(slide, method)(*args, **kwargs)
    return deck.to_dict()


# ---------------------------------------------------------------------------
# Prompt assembly — compact slidegen skill pack + per-deck block, cache-marked
# ---------------------------------------------------------------------------
# Slidegen-only compact skill pack
#
# The slidegen model emits a compact spec (background + elements[] of
# deck_builder kwargs); deck_builder.Deck deterministically builds the dual
# content/changelog records and assigns zIndex. So instructions that teach
# hand-assembly of the Bildory format are UNREACHABLE for this generator:
#   - 00-index.md      : "read this first / read only what you need" routing —
#                        inert here (all files are injected unconditionally)
#   - 08-changelog-sync: deck_builder syncs the dual records automatically
#   - 09-zindex-rules  : deck_builder assigns globally-unique zIndex
#   - per-element "content record" / "changelog record" JSON dumps and
#     make_*() helper functions — the model never writes these
#
# The shared files under skills/ are left byte-for-byte untouched (the legacy
# `agent` engine in core/prompt.py still loads the full set via config.py).
# This pack is a pure function of those files: every RETAINED instruction is
# the original text verbatim; we only drop provably-unreachable sections/lines.
# ---------------------------------------------------------------------------
SLIDEGEN_CORE_SKILL_FILES = [
    "01-envelope.md",
    "10-design-rules.md",
    "11-visual-design-guide.md",
    "12-visual-richness.md",
]  # excludes 08-changelog-sync, 09-zindex-rules (unreachable for slidegen)

SLIDEGEN_ELEMENT_SKILL_FILES = ELEMENT_SKILL_FILES  # same 6, boilerplate stripped

# h2 sections (## ...) whose content teaches hand-assembly of the raw format
_DROP_SECTION_PREFIXES = ("content record", "changelog record", "helper function")

# individual lines that are wholly about records/fields the model never emits
_DROP_LINE_SUBSTRINGS = (
    "must be globally unique",       # zIndex uniqueness cross-refs
    "27 style field", "all 27",      # "all 27 style fields required" (contradicts omit-defaults)
    "animation fields are duplicated",
    "formattedcontent",
    "updatedat",
    "09-zindex-rules", "08-changelog-sync",
)


def _strip_legacy_boilerplate(md: str) -> str:
    """Remove hand-assembly boilerplate from an element skill file. Retained
    text is byte-identical to the source; only whole legacy sections and
    unambiguously-legacy lines are dropped."""
    out, skipping = [], False
    for ln in md.splitlines():
        stripped = ln.lstrip()
        if stripped.startswith("## "):
            title = stripped[3:].strip().lower()
            skipping = any(title.startswith(p) for p in _DROP_SECTION_PREFIXES)
            if skipping:
                continue
        if skipping:
            continue
        if any(sub in ln.lower() for sub in _DROP_LINE_SUBSTRINGS):
            continue
        out.append(ln)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out))          # tidy gaps
    text = re.sub(r"(?:\n---\s*)+\n*\Z", "\n", text)           # trailing rules
    return text.strip() + "\n"


def _skills_block() -> str:
    """Compact slidegen skills prefix (see the compact-pack note above)."""
    sections = []
    for fname in SLIDEGEN_CORE_SKILL_FILES:
        sections.append(f"### {fname}\n" + (CORE_SKILLS / fname).read_text(encoding="utf-8"))
    for fname in SLIDEGEN_ELEMENT_SKILL_FILES:
        raw = (ELEM_SKILLS / fname).read_text(encoding="utf-8")
        sections.append(f"### {fname}\n" + _strip_legacy_boilerplate(raw))
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
           font_family, text_align, rotation, opacity, style
           (opacity < 1 for watermark/ghost numerals and faint labels)
    shape: shape_type, x, y, width, height, fill, stroke, stroke_width,
           opacity, rotation
           (frame/outline: fill="transparent" + stroke + stroke_width; NEVER an
           opaque-filled shape over an image — it hides the photo)
    icon:  icon_name, x, y, size, color, opacity, rotation
    image: query, image_prompt, x, y, width, height, is_background,
           border_radius, opacity, rotation, object_fit, filter, blur,
           scale_x, scale_y, shadow, border, overlay, crop_ratio, crop_rect,
           focus_point
           (use "query": 2-5 literal subject words, e.g. "bubble tea pastel
           cups" — a real Pexels search fills in src. NEVER hand-write a
           photos/{id} URL: a guessed id returns a random, irrelevant photo.
           OPTIONALLY also add "image_prompt": one vivid descriptive sentence
           of the ideal photo — used verbatim when AI image generation is on,
           ignored for stock search.)
    chart: chart_type, chart_config, x, y, width, height
    table: cells, x, y, col_widths, row_heights, font_size, table_color,
           table_bg, table_bold, table_italic, table_align
    motif: motif_type (plexus|hexagons|waves|dot_grid|flow|aurora|topography|
           rings|circuit|data_horizon), bg (deck's darkest hex), accent (bright
           palette hex), accent2 (second hex — the ink/charcoal for data_horizon),
           density (0-1), glow_strength (0-1),
           safe_area ("left"|"right"|"top"|"bottom"|"center" — kept sparse for
           your title). A full-bleed procedural background (glowing network mesh,
           hex field, waves…) baked as one image — use it as the BOTTOM element
           on title/section/closing slides instead of a plain color field.
           Put the title on the safe_area side. data_horizon is the LIGHT
           editorial one: a cream field with a gold perspective grid + charcoal
           data-viz glyphs + corner frame — use bg = a light cream hex, accent =
           gold, accent2 = charcoal, safe_area = "center", and centre a SERIF
           title over it.

RULES:
- Canvas is 1280x720. Follow all design skills above exactly as if writing
  deck_builder calls — same quality bar, same palettes, same layout rules.
- NEVER include a field whose value equals its documented default
  (see OMIT DEFAULTS reference). shadow/border/overlay/style are partial
  dicts merged over defaults.
- All geometry and style values are plain NUMBERS, never CSS strings:
  letter_spacing/letterSpacing, font_size, line_height, width, height, x, y,
  opacity, rotation are numeric (e.g. letter_spacing: 2, NOT "2px").
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
- Icon badges, index numerals (01/02/03), and oversized stat numbers get their
  OWN clear space — never place them on top of, or touching, a heading, title,
  subtitle, or the words of any text run. Keep a >=16px gap between a badge/
  numeral and adjacent text; if a card is too tight to hold a badge AND its
  heading without collision, drop the badge rather than stacking them.
- A row of cards/panels is ONE set: give every card in the row identical width
  AND identical height, with aligned top and bottom edges. Never let one card
  be taller or bleed past the row while its siblings stop short.
- Emit EVERY text block the plan calls for — kicker, title, subtitle, body, and
  the CTA/closing row. Never leave a planned column or half of the slide empty;
  if content is sparse, enlarge and space it, do not drop it. Set the slide
  background to the shade the plan specifies (light vs dark) — do not invert it.
- ALL text stays fully inside the safe zone: x >= 48, y >= 48,
  x + width <= 1232, y + height <= 672. Only images and shapes may bleed
  off-canvas. Page-number captions sit at y <= 672 too.
- Stat labels and card captions are 3-7 words and wrap to at most 2 lines —
  if a label needs 3 lines, shorten the wording, don't shrink the font.
- Text placed over a photo requires a dark overlay (opacity 45-70) or a solid
  color panel behind it — never raw text on a busy image.
- CONTRAST: anything the reader must actually read (body copy, stat labels,
  captions) uses a near-full-strength ink color against its background. Never
  set body/label text in a faint mid-grey (e.g. #9AA3B2) — reserve muted greys
  for hairlines, dividers, and decoration only, never for readable text.
- SIZE TEXT BOXES FOR THE WORST CASE: assume the copy wraps to one MORE line
  than you expect and add ~10px vertical slack, so nothing clips or collides at
  render time. Never butt a text box's bottom edge against the element below it.
- DENSITY NEVER BEATS CLARITY: hitting the element count must not push spacing
  below the minimums (>=24px padding inside cards, >=16px between separate
  elements). If a region is too tight to hold everything cleanly, use fewer,
  larger elements — a clean 15-element slide beats a crammed 25-element one.
"""


# Composition archetypes ("layouts") — one .md file each under skills/layouts/,
# loaded into the library. _ARCHETYPES_BY_LAYOUT rebuilds the legacy
# {layout_type: [(name, body), ...]} shape from it so assign_archetypes() and
# scripts/_showcase_archetypes.py keep working unchanged. build_library(None)
# has no in-code fallback — every layout must be a file (preflight enforces it).
_LAYOUT_LIB = build_library(None)
_ARCHETYPES_BY_LAYOUT = archetypes_by_layout(_LAYOUT_LIB)


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


# ---------------------------------------------------------------------------
# Per-run art-direction variety — so the SAME topic doesn't produce the same
# palette / background / type every time. Randomised per run and offered to the
# art director as the LEAD choice, overridable only on a genuine mood clash.
# (These land in the design-plan user message, which is NOT part of the cached
# system prefix, so varying them per run is free of cache cost. Layout skeletons
# already vary via _run_seed; this varies the *theme* the same way.)
# ---------------------------------------------------------------------------
_ALL_PALETTES = [
    "Midnight Executive", "Forest & Moss", "Coral Energy", "Warm Terracotta",
    "Ocean Gradient", "Charcoal Minimal", "Teal Trust", "Berry & Cream",
    "Sage Calm", "Cherry Bold", "Noir & Champagne", "Deep Navy & Gold",
    "Graphite & Electric", "Ivory Editorial", "Fresh Greens",
]

# Weighted toward restraint (solid fields + photography read premium for most
# subjects); geometric motif families stay gated to genuinely technical topics
# and deliberately steer AWAY from the over-used plexus look.
_BACKGROUND_OPTIONS = [
    "NO motif — solid palette color fields + photography + generous whitespace",
    "NO motif — solid palette color fields + photography + generous whitespace",
    "the ATMOSPHERIC 'aurora' motif only (soft blurred gradient orbs, low-contrast "
    "ambient light — never a hard geometric pattern)",
    "the EDITORIAL-LIGHT 'data_horizon' motif on title/section/closing (cream field "
    "+ gold horizon grid + a large serif title)",
    "ONE GEOMETRIC motif family — pick a FRESH one this run from hexagons, waves, "
    "dot_grid, flow, topography, rings or circuit (avoid plexus unless nothing else "
    "fits) — ONLY if the topic is genuinely technical",
]

_FONT_PAIRINGS = [
    "Georgia / Calibri (Editorial / Premium)",
    "Century Gothic / Calibri Light (Geometric / Design)",
    "Segoe UI / Segoe UI Light (Tech / Digital)",
    "Cambria / Calibri (Sharp / Executive)",
    "Arial Black / Arial (Bold / Impactful)",
    "Palatino Linotype / Garamond (Elegant / Luxury)",
    "Trebuchet MS / Calibri Light (Modern / Clean)",
]


def _variety_directive(palette_auto: bool, font_auto: bool) -> str:
    """A randomised lead palette/background/type suggestion for THIS run, so
    successive decks on one topic never look identical. Overridable by the art
    director only on a genuine mood clash."""
    token = random.randrange(1 << 30)
    lines = [
        f"VARIETY DIRECTIVE (run token {token}): decks on the SAME topic must NOT "
        "look alike run-to-run. For THIS deck, lead with the choices below and "
        "commit to them deck-wide. Deviate ONLY if one genuinely clashes with the "
        "subject's mood — and if so, pick a fresh alternative you would not "
        "normally default to. Do NOT fall back to the over-used dark-navy + "
        "blue-plexus tech look unless the lead palette below is itself a dark one."
    ]
    if palette_auto:
        lines.append(f"  - Lead palette (use unless it clashes): {random.choice(_ALL_PALETTES)}")
    lines.append(f"  - Background system this run: {random.choice(_BACKGROUND_OPTIONS)}")
    if font_auto:
        lines.append(f"  - Type pairing this run: {random.choice(_FONT_PAIRINGS)}")
    return "\n".join(lines) + "\n\n"


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
    palette_clause += (
        "BACKGROUND SYSTEM (decide FIRST, state it in deck_notes as "
        "\"Background system: ...\"):\n"
        "A `motif` is a full-bleed generative graphic. Two tiers:\n"
        "  GEOMETRIC (plexus | hexagons | waves | dot_grid | flow | topography | "
        "rings | circuit) — glowing meshes, hex/wave fields, contour lines, "
        "orbital rings, PCB traces. These fit ONLY genuinely technical subjects: "
        "tech, software/SaaS, data/analytics, energy/grid, security/cyber, crypto/"
        "blockchain, AI/ML, telecom, engineering. (circuit = hardware/embedded; "
        "rings/topography = data/systems/geo.)\n"
        "  ATMOSPHERIC (aurora) — soft, blurred mesh-gradient orbs, no visible "
        "geometry. This is the one motif refined enough for premium non-technical "
        "decks too: modern brand, product launches, finance/fintech, luxury-tech. "
        "Use it sparingly and low-contrast so it reads as ambient light, not a "
        "pattern.\n"
        "  EDITORIAL LIGHT (data_horizon) — a CREAM field with a gold "
        "perspective 'data horizon' grid, symmetric charcoal data-viz glyphs "
        "(mini donuts, bars, line charts, sparklines, ruled lines, dot matrices) "
        "and an ornate corner frame. This is the premium REPORT / METRICS look — "
        "ideal for marketing, analytics, data, research, finance, strategy and "
        "business-review decks. Use it on the title/section/closing slides with "
        "bg = a light cream hex (e.g. #F7F3E9), accent = gold (e.g. #BF9B30), "
        "accent2 = charcoal (e.g. #3D3A34), safe_area = \"center\", and centre a "
        "large SERIF title over it (dark charcoal) with a short gold subtitle. "
        "On a data_horizon slide place NO photos and NO opaque panels over the "
        "motif — the cream collage IS the composition; let the serif title and "
        "the motif's own glyphs carry it. Content slides stay on the same cream "
        "field with charcoal/gold ink.\n"
        "For EVERYTHING ELSE — food, travel, heritage, health, human stories — "
        "the DEFAULT IS NO MOTIF; restraint (solid fields, photography, "
        "whitespace, serif type) reads more premium.\n"
        "  - If (and only if) the topic is clearly in the technical family: choose "
        "ONE motif family for the whole deck and use it as a full-bleed background "
        "ONLY on the opening/title slide, any section-divider, and the closing "
        "slide — NEVER behind body-text/content slides. On those slides add a "
        "`motif` element (bg = the deck's DARKEST hex, accent = a bright palette "
        "hex, safe_area = the side the title sits on) as the bottom layer, then "
        "keep that text side clean. State the family + hexes in deck_notes.\n"
        "  - Otherwise: \"Background system: none (solid fields + photography).\" "
        "Do NOT place any motif; plan clean color fields and imagery instead.\n\n"
    )
    msg = (
        "You are the ART DIRECTOR for this deck. Think through the entire deck's "
        "design as one coherent system, then call emit_design_plan exactly once.\n\n"
        f"SLIDES AND ASSIGNED ARCHETYPES:\n{listing}\n\n"
        f"{palette_clause}"
        f"{_variety_directive(palette_auto, font_auto)}"
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
        # [plan-instr] additive-only latency instrumentation. All timestamps on
        # ONE time.monotonic() clock relative to plan_call_started. No control
        # flow or behavior changes — every print is a pure side effect.
        _pi_t0 = time.monotonic()
        def _pi():  # seconds since plan_call_started
            return time.monotonic() - _pi_t0
        _pi_thinking_seen = False
        _pi_first_json = None      # thinking_phase boundary (silent time upper bound)
        _pi_first_entry = None     # time_to_first_entry
        _pi_first_launch = None    # dead_serial_time (first executor launched)
        _pi_last_entry = None      # for entry_spread / tail_after_last_entry
        print("[plan-instr] plan_call_started t=0.000", flush=True)
        async with client.messages.stream(**request) as stream:
            async for event in stream:
                _pi_etype = getattr(event, "type", "")
                _pi_delta = getattr(event, "delta", None)
                _pi_dtype = getattr(_pi_delta, "type", "")
                if (not _pi_thinking_seen and _pi_etype == "content_block_delta"
                        and _pi_dtype == "thinking_delta"):
                    _pi_thinking_seen = True
                    print(f"[plan-instr] first_thinking_delta t={_pi():.3f}",
                          flush=True)
                if (_pi_etype == "content_block_delta"
                        and _pi_dtype == "input_json_delta"):
                    if _pi_first_json is None:
                        _pi_first_json = _pi()
                        # thinking_phase = silent time before the first
                        # input_json_delta = UPPER BOUND on thinking (this SDK
                        # path does not surface thinking deltas separately).
                        print(f"[plan-instr] first_json_delta t={_pi_first_json:.3f} "
                              f"thinking_phase={_pi_first_json:.3f}s "
                              f"(silent upper-bound; thinking_delta_seen="
                              f"{_pi_thinking_seen})", flush=True)
                    buf += event.delta.partial_json
                    notes_p, entries = _parse_partial_plan(buf)
                    if notes_p is None:
                        continue
                    for n, plan_text in entries.items():
                        if n not in streamed:
                            if _pi_first_entry is None:
                                _pi_first_entry = _pi()
                                print(f"[plan-instr] first_plan_entry_parsed n={n} "
                                      f"t={_pi_first_entry:.3f} "
                                      f"time_to_first_entry={_pi_first_entry:.3f}s",
                                      flush=True)
                            else:
                                print(f"[plan-instr] entry_parsed n={n} "
                                      f"t={_pi():.3f}", flush=True)
                            _pi_last_entry = _pi()
                            streamed.add(n)
                            if _pi_first_launch is None:
                                _pi_first_launch = _pi()
                                print(f"[plan-instr] first_slide_executor_launched "
                                      f"n={n} t={_pi_first_launch:.3f} "
                                      f"dead_serial_time={_pi_first_launch:.3f}s",
                                      flush=True)
                            on_entry(n, f"DECK-WIDE SYSTEM: {notes_p}\n\n"
                                        f"THIS SLIDE: {plan_text}")
            resp = await stream.get_final_message()
        _pi_wall = _pi()
        print(f"[plan-instr] plan_call_completed t={_pi_wall:.3f}", flush=True)
        _pi_tte = _pi_first_entry if _pi_first_entry is not None else -1.0
        _pi_spread = ((_pi_last_entry - _pi_first_entry)
                      if (_pi_first_entry is not None
                          and _pi_last_entry is not None) else -1.0)
        _pi_dead = _pi_first_launch if _pi_first_launch is not None else -1.0
        _pi_think = _pi_first_json if _pi_first_json is not None else -1.0
        _pi_json_phase = ((_pi_wall - _pi_first_json)
                          if _pi_first_json is not None else -1.0)
        _pi_tail = ((_pi_wall - _pi_last_entry)
                    if _pi_last_entry is not None else -1.0)
        print(f"[plan-instr] SUMMARY time_to_first_entry={_pi_tte:.3f}s "
              f"entry_spread={_pi_spread:.3f}s dead_serial_time={_pi_dead:.3f}s "
              f"thinking_phase={_pi_think:.3f}s "
              f"json_emission_phase={_pi_json_phase:.3f}s "
              f"plan_wall={_pi_wall:.3f}s tail_after_last_entry={_pi_tail:.3f}s",
              flush=True)
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


def _run_seed(outline: dict) -> int:
    """Archetype rotation offset. RANDOM per run by default, so the SAME topic
    yields DIFFERENT layouts each time — the archetypes are inspiration the model
    riffs on, not a fixed template. Override with the SLIDEGEN_SEED env var:
      SLIDEGEN_SEED=<int>   pin an exact rotation (reproducible output)
      SLIDEGEN_SEED=title   restore the old title-stable behaviour
    """
    env = os.environ.get("SLIDEGEN_SEED", "").strip()
    if env:
        if env.lower() == "title":
            return _deck_seed(outline)
        try:
            return int(env)
        except ValueError:
            pass
    return random.randrange(1 << 30)


def _unmask_framed_images(merged: dict) -> int:
    """Safety net for the 'empty framed box' bug: shapes have no unfilled mode,
    so the model sometimes fakes a picture-frame with an opaque fill-colour
    rectangle laid ON TOP of an image — which hides the photo entirely. When a
    bordered, opaque shape sits ABOVE an image and covers most of it, drop its
    fill to 'transparent' so the frame keeps its border and the photo shows
    through. Only touches clearly-a-frame shapes (strokeWidth > 0)."""
    changelog = merged.get("files", {}).get("changelog", {}).get("slides", {})
    fixed = 0
    for sl in changelog.values():
        els = sl.get("elements", {})
        images = [r for eid, r in els.items() if eid.startswith("image")]
        if not images:
            continue
        for eid, r in els.items():
            if not eid.startswith("shape"):
                continue
            fill = str(r.get("fill", "")).lower()
            if fill in ("transparent", "none", ""):
                continue
            if (r.get("opacity", 1) or 1) < 0.9:
                continue
            if (r.get("strokeWidth", 0) or 0) <= 0:
                continue  # only unmask shapes that are clearly a frame (bordered)
            sx, sy = r["position"]["x"], r["position"]["y"]
            sw, sh = r.get("width", 0), r.get("height", 0)
            for ir in images:
                if ir.get("zIndex", 0) >= r.get("zIndex", 0):
                    continue  # frame must sit ABOVE the image to hide it
                ix, iy = ir["position"]["x"], ir["position"]["y"]
                iw, ih = ir.get("width", 0), ir.get("height", 0)
                ox = max(0, min(sx + sw, ix + iw) - max(sx, ix))
                oy = max(0, min(sy + sh, iy + ih) - max(sy, iy))
                if ox * oy >= 0.85 * max(1, iw * ih):  # covers most of the photo
                    r["fill"] = "transparent"
                    fixed += 1
                    break
    return fixed


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


def build_slidegen_system(outline: dict, config: dict,
                          selected_layouts: list | None = None) -> list:
    """System blocks, each cached (ephemeral):
      1. stable skills prefix        — outline-independent; warmed globally by
                                       warm_static_prefix(), a cache read every run
      2. selected layouts (optional) — the Stage-1 picks' full specs, per run
      3. per-deck design brief       — per run

    Block 1's text is byte-identical to warm_static_prefix()'s, so the global
    warm still hits. Ordering is most-stable-first so the prefix cache holds."""
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
    blocks = [
        {
            "type": "text",
            "text": _skills_block() + "\n\n---\n\n" + _SPEC_INSTRUCTIONS,
            "cache_control": {"type": "ephemeral"},
        },
    ]
    if selected_layouts:
        blocks.append({
            "type": "text",
            "text": selected_layouts_block(selected_layouts),
            "cache_control": {"type": "ephemeral"},
        })
    blocks.append({
        "type": "text",
        "text": brief,
        "cache_control": {"type": "ephemeral"},
    })
    return blocks


def _slide_user_message(outline: dict, slide_entry: dict, slide_number: int,
                        archetype: tuple, neighbors: str,
                        plan_text: str | None = None,
                        layout_in_prefix: bool = False) -> str:
    total = len(outline.get("slides", []))
    name, desc = archetype
    if layout_in_prefix:
        # Full spec lives in the cached SELECTED LAYOUTS block — reference it by
        # name instead of repeating the body in every slide's user message.
        arch_block = (
            f"COMPOSITION ARCHETYPE (mandatory skeleton): {name}\n"
            f"→ Follow the full '{name}' spec under SELECTED LAYOUTS in the "
            f"system prompt, exactly, as this slide's structural skeleton.\n"
        )
    else:
        arch_block = f"COMPOSITION ARCHETYPE (mandatory skeleton): {name}\n{desc}\n"
    plan_block = ""
    if plan_text:
        plan_block = (
            f"\nART DIRECTOR PLAN — execute this precisely; all creative "
            f"decisions are already made:\n{plan_text}\n"
        )
    return (
        f"Design slide {slide_number} of {total}.\n\n"
        f"OUTLINE ENTRY:\n{json.dumps(slide_entry, indent=2)}\n\n"
        f"{arch_block}"
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
_GHOST_MIN_FONT = 80  # px — decorative "ghost glyph" display text is this big+
_GHOST_MAX_OPACITY = 0.15  # ghost glyphs are faint washes


def _clamp_text_safe_zone(merged: dict) -> int:
    """Deterministically nudge text elements fully inside the 48px safe zone
    (48..1232 x, 48..672 y) when they overshoot by <= _SAFE_CLAMP_MAX px —
    the classic offender is the page-number caption a few px below the line.
    Larger violations are left alone (and get caught by validation/QA).

    Ghost glyphs (huge, faint decorative display text) are an exception: an
    off-canvas bleed reads as an accidental mid-glyph crop, so they get an
    unbounded clamp budget and are pulled fully inside — unless the glyph is
    larger than the safe zone itself, in which case it's a deliberate full-bleed
    wash and is left alone. Returns the number of elements moved. Geometry lives
    in the changelog."""
    fixed = 0
    for s in merged["files"]["changelog"]["slides"].values():
        for eid, rec in s.get("elements", {}).items():
            if not eid.startswith("text"):
                continue
            pos = rec.get("position") or {}
            x, y = pos.get("x", 0), pos.get("y", 0)
            w, h = rec.get("width", 0), rec.get("height", 0)
            st = rec.get("style") or {}
            fs = st.get("fontSize", 0) or 0
            op = rec.get("opacity", st.get("opacity", 1))
            op = 1 if op is None else op
            ghost = fs >= _GHOST_MIN_FONT and op <= _GHOST_MAX_OPACITY
            budget = 10_000 if ghost else _SAFE_CLAMP_MAX
            nx, ny = x, y
            if x + w > 1232 and (x + w) - 1232 <= budget:
                nx = 1232 - w
            if nx < 48 and 48 - nx <= budget:
                nx = 48
            if nx + w > 1232:           # can't satisfy both edges — leave it
                nx = x
            if y + h > 672 and (y + h) - 672 <= budget:
                ny = 672 - h
            if ny < 48 and 48 - ny <= budget:
                ny = 48
            if ny + h > 672:
                ny = y
            if (nx, ny) != (x, y):
                pos["x"], pos["y"] = nx, ny
                fixed += 1
    return fixed


# --- single-line label fit (kicker chips / captions) -----------------------
_LABEL_FONT_FLOOR = 9   # px — don't shrink caption text below this
_ADV_UPPER = 0.62       # avg glyph advance ÷ font size, letterspaced caps
_ADV_MIXED = 0.52       # avg glyph advance ÷ font size, mixed case


def _num(v, default: float = 0.0) -> float:
    """Coerce a style value to a float. Tolerates CSS-ish strings ("2px",
    "0.05em") by taking the leading number. Post-process robustness only —
    the canonical style values are numeric (deck_builder defaults)."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.match(r"\s*(-?\d+(?:\.\d+)?)", v)
        if m:
            return float(m.group(1))
    return default


def _est_line_width(text: str, font_size: float, letter_spacing: float) -> float:
    """Rough one-line rendered width (px) for a proportional font. Deliberately
    a slight over-estimate so the fit guard errs toward no-wrap."""
    text = text or ""
    n = len(text)
    if n == 0:
        return 0.0
    upper = sum(1 for c in text if c.isupper() or not c.isalpha()) >= 0.7 * n
    adv = font_size * (_ADV_UPPER if upper else _ADV_MIXED)
    return n * adv + n * (letter_spacing or 0)


def _fit_single_line_labels(merged: dict) -> int:
    """Kicker chips / captions are single-line labels sitting on a small filled
    rect. When the caption is wider than its box it wraps to a second line that
    clips out the bottom of the chip (the classic 'TREND 01 — CLIMATE' bug).
    Shrink the fontSize (keeping letterSpacing) until the text fits one line;
    as a last resort drop letterSpacing. Floored at _LABEL_FONT_FLOOR so it
    stays legible. Returns the number of elements adjusted."""
    # element id -> (content string, semantic type) from the content file
    meta = {}
    for s in merged["files"]["content"].get("slides", []):
        for te in s.get("textElements", []):
            meta[te.get("id")] = (te.get("content") or "", te.get("type") or "")

    fixed = 0
    for s in merged["files"]["changelog"]["slides"].values():
        for eid, rec in s.get("elements", {}).items():
            if not eid.startswith("text"):
                continue
            content, ttype = meta.get(eid, ("", ""))
            st = rec.get("style") or {}
            fs = _num(st.get("fontSize", 0))
            ls = _num(st.get("letterSpacing", 0))
            lh = _num(st.get("lineHeight", 1.3), 1.3)
            w = rec.get("width", 0) or 0
            h = rec.get("height", 0) or 0
            # single-line label: a caption whose box is ~one line tall
            if ttype != "caption" or not content or w <= 0 or fs <= 0:
                continue
            if h > fs * lh * 1.8:      # box is multi-line by design — leave it
                continue
            budget = w * 0.98
            if _est_line_width(content, fs, ls) <= budget:
                continue
            nfs, nls = fs, ls
            while nfs > _LABEL_FONT_FLOOR and _est_line_width(content, nfs, nls) > budget:
                nfs -= 1
            if _est_line_width(content, nfs, nls) > budget and nls > 0:
                nls = 0             # last resort: give up the letterspacing
            if (nfs, nls) != (fs, ls):
                st["fontSize"], st["letterSpacing"] = nfs, nls
                fixed += 1
    return fixed


# --- card-grid alignment ---------------------------------------------------
import statistics as _stats

_CARD_MIN_W, _CARD_MAX_W = 180, 620   # panel-sized rects (not chips or full-bleed bg)
_CARD_MIN_H, _CARD_MAX_H = 110, 560
_ALIGN_MAX_DY = 60                    # only correct modest top-stagger
_GROW_MAX = 90                        # only grow a short card by this much


def _cards_on_slide(els: dict) -> list:
    """Rectangle shapes that look like content cards (not chips, rules, or
    full-bleed backgrounds). Returns [eid, rec, x, y, w, h]."""
    out = []
    for eid, rec in els.items():
        if not eid.startswith("shape") or rec.get("shapeType") != "rectangle":
            continue
        pos = rec.get("position") or {}
        x, y = pos.get("x", 0), pos.get("y", 0)
        w, h = rec.get("width", 0), rec.get("height", 0)
        if not (_CARD_MIN_W <= w <= _CARD_MAX_W) or not (_CARD_MIN_H <= h <= _CARD_MAX_H):
            continue
        if x <= 14:                    # left rail / edge-anchored full-bleed
            continue
        out.append([eid, rec, x, y, w, h])
    return out


def _translate_card_content(els: dict, card_eid: str, card_ids: set,
                            x: int, y: int, w: int, h: int, dy: int, moved: set):
    """Move every element whose center sits inside the card's original rect by
    dy (so a card's label/number/icon/accent travels with it). Skips other
    cards and anything already moved this slide."""
    for eid, rec in els.items():
        if eid == card_eid or eid in card_ids or eid in moved:
            continue
        pos = rec.get("position") or {}
        cx = pos.get("x", 0) + (rec.get("width", 0) / 2)
        cy = pos.get("y", 0) + (rec.get("height", 0) / 2)
        if x <= cx <= x + w and y <= cy <= y + h:
            pos["y"] = pos.get("y", 0) + dy
            moved.add(eid)


def _align_card_grids(merged: dict) -> int:
    """Sibling cards in a row should share a top edge and height. Generation
    sometimes staggers their tops or leaves unequal heights, which reads as
    misalignment (the #1 QA defect cluster). Detect rows of same-width cards
    (vertical spans overlapping >=50%) and snap each to the row's median top +
    max height, translating each card's overlaid content with it. Conservative:
    only uniform-width rows, only modest stagger, only within the canvas."""
    fixed = 0
    for s in merged["files"]["changelog"]["slides"].values():
        els = s.get("elements", {})
        cards = _cards_on_slide(els)
        if len(cards) < 2:
            continue
        card_ids = {c[0] for c in cards}
        cards.sort(key=lambda c: c[3])               # by top y
        rows: list[list] = []
        for c in cards:
            for row in rows:
                r = row[0]
                ov = min(c[3] + c[5], r[3] + r[5]) - max(c[3], r[3])
                if ov > 0 and ov >= 0.5 * min(c[5], r[5]):
                    row.append(c)
                    break
            else:
                rows.append([c])
        moved: set = set()
        for row in rows:
            if len(row) < 2:
                continue
            widths = [c[4] for c in row]
            med_w = _stats.median(widths)
            if med_w <= 0 or (max(widths) - min(widths)) > 0.25 * med_w:
                continue                             # non-uniform → likely intentional
            tops = [c[3] for c in row]
            heights = [c[5] for c in row]
            if max(tops) - min(tops) <= 4 and max(heights) - min(heights) <= 4:
                continue                             # already aligned
            target_top = round(_stats.median(tops))
            target_h = max(heights)
            for eid, rec, x, y, w, h in row:
                pos = rec["position"]
                dy = target_top - y
                if dy != 0 and abs(dy) <= _ALIGN_MAX_DY and 0 <= target_top \
                        and target_top + max(target_h, h) <= 712:
                    _translate_card_content(els, eid, card_ids, x, y, w, h, dy, moved)
                    pos["y"] = target_top
                    y = target_top
                    fixed += 1
                if h < target_h and (target_h - h) <= _GROW_MAX and (y + target_h) <= 712:
                    rec["height"] = target_h
    return fixed


# ---------------------------------------------------------------------------
# Retry instrumentation (metrics only — never affects generation)
# ---------------------------------------------------------------------------
def _log_attempt(retry_log, phase, slide_number, attempt, *, outcome,
                 reason, elements, usage, thin=False):
    """Record one generation attempt for retry metrics.

    Pure instrumentation: no-op when retry_log is None, and never alters the
    caller's control flow. `outcome` is 'accepted' | 'retry' | 'error'.
    """
    if retry_log is None:
        return

    def _u(name):
        return (getattr(usage, name, 0) or 0) if usage is not None else 0

    retry_log.append({
        "phase": phase,               # "generate" | "qa"
        "slide": slide_number,
        "attempt": attempt,           # 1-based
        "outcome": outcome,
        "reason": reason,             # "below_element_floor" | <exception str> | None
        "elements": elements,         # element count the model returned (None on error)
        "thin": thin,                 # accepted despite being below the floor (last attempt)
        "input_tokens": _u("input_tokens"),
        "output_tokens": _u("output_tokens"),
        "cache_write": _u("cache_creation_input_tokens"),
        "cache_read": _u("cache_read_input_tokens"),
    })


def _summarize_retries(retry_log: list) -> dict:
    """Aggregate per-attempt records into deck-level retry metrics."""
    def _agg(events):
        by_slide: dict = {}
        for e in events:
            by_slide.setdefault(e["slide"], []).append(e)
        first_try = retried_slides = retry_calls = thin_retries = error_retries = 0
        wasted = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
        per_slide = []
        for n, evs in sorted(by_slide.items()):
            evs.sort(key=lambda x: x["attempt"])
            non_accepted = [e for e in evs if e["outcome"] != "accepted"]
            accepted = next((e for e in evs if e["outcome"] == "accepted"), None)
            retry_calls += len(non_accepted)
            for e in non_accepted:
                if e["reason"] == "below_element_floor":
                    thin_retries += 1
                else:
                    error_retries += 1
                wasted["input"] += e["input_tokens"]
                wasted["output"] += e["output_tokens"]
                wasted["cache_write"] += e["cache_write"]
                wasted["cache_read"] += e["cache_read"]
            if non_accepted:
                retried_slides += 1
            else:
                first_try += 1
            per_slide.append({
                "slide": n,
                "attempts": len(evs),
                "retries": len(non_accepted),
                "succeeded": accepted is not None,
                "final_elements": accepted["elements"] if accepted else None,
                "reasons": [e["reason"] for e in non_accepted],
            })
        # same Opus rates used for stats["cost_usd"]: in $5/M, out $25/M,
        # 5m-cache write $6.25/M, read $0.5/M
        extra_cost = round(
            wasted["input"] * 5 / 1e6
            + wasted["output"] * 25 / 1e6
            + wasted["cache_write"] * 6.25 / 1e6
            + wasted["cache_read"] * 0.5 / 1e6, 4)
        return {
            "slides": len(by_slide),
            "accepted_first_try": first_try,
            "slides_requiring_retries": retried_slides,
            "total_retry_calls": retry_calls,
            "thin_retries": thin_retries,
            "error_retries": error_retries,
            "wasted_tokens": wasted,
            "extra_cost_usd": extra_cost,
            "per_slide": per_slide,
        }

    gen = [e for e in retry_log if e["phase"] == "generate"]
    qa = [e for e in retry_log if e["phase"] == "qa"]
    out = {"generate": _agg(gen)}
    if qa:
        out["qa"] = _agg(qa)
    return out


def _print_retry_summary(summary: dict) -> None:
    g = summary["generate"]
    print("=" * 30)
    print("Retry Summary")
    print(f"Slides: {g['slides']}")
    print(f"Slides accepted first try: {g['accepted_first_try']}")
    print(f"Slides requiring retries: {g['slides_requiring_retries']}")
    print(f"Total retry calls: {g['total_retry_calls']}")
    print(f"  - below element floor: {g['thin_retries']}")
    print(f"  - errors: {g['error_retries']}")
    print(f"Extra API cost due to retries: ~${g['extra_cost_usd']:.4f} (estimated)")
    for s in g["per_slide"]:
        if s["retries"]:
            reasons = ", ".join(str(r) for r in s["reasons"])
            print(f"  slide {s['slide']}: {s['retries']} retr(y/ies) over "
                  f"{s['attempts']} attempt(s), "
                  f"{'accepted' if s['succeeded'] else 'FAILED'}, "
                  f"final_elements={s['final_elements']}, reasons=[{reasons}]")
    if "qa" in summary:
        q = summary["qa"]
        print(f"QA-phase regeneration retries: {q['total_retry_calls']} "
              f"(extra ~${q['extra_cost_usd']:.4f})")
    print("=" * 30)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
async def _generate_one(client, model, system, outline, slide_entry, slide_number,
                        usage_acc: list, archetype: tuple, neighbors: str,
                        plan_text: str | None = None, think: bool = True,
                        qa_feedback: str | None = None,
                        retry_log: list | None = None,
                        phase: str = "generate",
                        layout_in_prefix: bool = False) -> dict:
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
        usage = None  # this attempt's token usage, for retry accounting
        try:
            content = _slide_user_message(outline, slide_entry, slide_number,
                                          archetype, neighbors, plan_text,
                                          layout_in_prefix=layout_in_prefix)
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
            usage = resp.usage
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
                _log_attempt(retry_log, phase, slide_number, attempt + 1,
                             outcome="retry", reason="below_element_floor",
                             elements=n_elements, usage=usage)
                continue
            _log_attempt(retry_log, phase, slide_number, attempt + 1,
                         outcome="accepted", reason=None,
                         elements=n_elements, usage=usage,
                         thin=n_elements < MIN_ELEMENTS_PER_SLIDE)
            return spec
        except Exception as e:
            last_err = e
            print(f"  [slide-{slide_number}] attempt {attempt + 1} failed: {e}")
            _log_attempt(retry_log, phase, slide_number, attempt + 1,
                         outcome="error", reason=str(e)[:160],
                         elements=None, usage=usage)
    raise RuntimeError(f"slide {slide_number} failed after retries: {last_err}")


def _image_style(config: dict) -> str:
    """A short style string fed to the AI image generator so every image shares
    the deck's mood/palette (cohesion = premium)."""
    bits = []
    tone = (config.get("tone") or "").strip()
    if tone:
        bits.append(tone)
    pal = config.get("palette")
    if isinstance(pal, str) and pal.strip().lower() not in ("", "auto"):
        bits.append(f"{pal.strip()} color palette")
    return ", ".join(bits)


def _backfill_image_prompts(specs: list, outline: dict) -> int:
    """Safety net: an image element with neither `query` nor `image_prompt`
    resolves to an empty src and renders as a blank box. When the planner emits
    one, derive a prompt from that slide's own title/subtitle so it still gets a
    picture (Pexels query or AI illustration) instead of a hole. Returns the
    count backfilled."""
    slides = outline.get("slides", [])
    deck_title = outline.get("title", "") or "the topic"
    n = 0
    for i, spec in enumerate(specs):
        s = slides[i] if i < len(slides) else {}
        subject = (s.get("title") or s.get("subtitle") or deck_title).strip()
        for el in (spec or {}).get("elements", []):
            if el.get("kind") != "image":
                continue
            if not (str(el.get("query") or "").strip()
                    or str(el.get("image_prompt") or "").strip()):
                el["query"] = subject
                el["image_prompt"] = f"a clean modern illustration representing {subject}"
                n += 1
    return n


async def _resolve_images(specs: list, run_dir, config: dict) -> None:
    """Fill image-element `src`s using the configured provider.

    IMAGE_PROVIDER / config['image_provider']:
      - "pexels" (default): stock search only.
      - "openai" | "ai":    generate bespoke images with gpt-image-1, then let
                            Pexels backfill anything generation left unresolved.
      - "auto":             use AI when OPENAI_API_KEY is set, else Pexels.
    Pexels always runs last as the fallback (it only touches elements that still
    carry a `query`, which the AI pass clears on success)."""
    provider = (config.get("image_provider")
                or os.environ.get("IMAGE_PROVIDER", "pexels")).lower()
    use_ai = provider in ("openai", "ai", "gpt", "gpt-image") or (
        provider == "auto" and os.environ.get("OPENAI_API_KEY"))
    if use_ai and run_dir is not None:
        try:
            from core.openai_images import generate_image_queries
            await generate_image_queries(specs, run_dir,
                                         style=_image_style(config))
        except Exception as e:  # noqa: BLE001 — fall through to Pexels
            print(f"  [images] AI generation error ({e}); falling back to Pexels")
    from core.pexels import resolve_image_queries
    await resolve_image_queries(specs)


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

    usage_acc: list = []
    retry_log: list = []   # per-attempt retry metrics (instrumentation only)

    # ── Stage 1: layout selection (SLIDEGEN_LAYOUT_SELECT=1, the default) ──
    # Fires the moment the outline is in hand (callers start warm_static_prefix()
    # concurrently, so this overlaps the tail of that warm). A cheap Haiku call
    # picks one library layout per slide from the lightweight index; ONLY those
    # selected layouts' full specs are inlined into the cached system prefix.
    # SLIDEGEN_LAYOUT_SELECT=0 restores the legacy deterministic rotation (every
    # archetype body rides in the per-slide user message) — used for A/B.
    use_select = os.environ.get("SLIDEGEN_LAYOUT_SELECT", "1").strip().lower() \
        not in ("0", "false", "no", "off")
    if use_select:
        core_rules = (CORE_SKILLS / "10-design-rules.md").read_text(encoding="utf-8")
        selection, sel_source = await select_layouts(
            outline, _LAYOUT_LIB, core_rules=core_rules, usage_acc=usage_acc)
        archetypes = [(_LAYOUT_LIB[selection[i]].name, _LAYOUT_LIB[selection[i]].body)
                      for i in range(1, len(slides) + 1)]
        seen: dict = {}   # distinct selected layouts, first-seen order → prefix
        for i in range(1, len(slides) + 1):
            seen.setdefault(selection[i], _LAYOUT_LIB[selection[i]])
        distinct = list(seen.values())
        system = build_slidegen_system(outline, config, selected_layouts=distinct)
        sys_tokens = estimate_tokens("".join(b["text"] for b in system))
        print(f"  [layouts] Stage-1 {sel_source}: {len(distinct)} distinct "
              f"layout(s) across {len(slides)} slides — "
              f"{', '.join(l.id for l in distinct)}")
        for i in range(1, len(slides) + 1):
            print(f"    slide {i}: {selection[i]}")
        print(f"  [layouts] assembled system prompt ~{sys_tokens} tokens (est)")
        if run_dir is not None:
            Path(run_dir).mkdir(parents=True, exist_ok=True)
            (Path(run_dir) / "layout_selection.json").write_text(
                json.dumps({
                    "source": sel_source,
                    "per_slide": {str(i): selection[i]
                                  for i in range(1, len(slides) + 1)},
                    "distinct": [l.id for l in distinct],
                    "system_prompt_tokens_est": sys_tokens,
                }, indent=2), encoding="utf-8")
    else:
        seed = _run_seed(outline)
        archetypes = assign_archetypes(slides, seed=seed)
        system = build_slidegen_system(outline, config)
        print(f"  [slidegen] layout selection OFF — archetype seed={seed} "
              f"(set SLIDEGEN_SEED={seed} to reproduce this layout set)")
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
                                       plan_text=plan_text, think=False,
                                       retry_log=retry_log,
                                       layout_in_prefix=use_select)

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
                                         archetypes[0], neighbors_of(1), think=think,
                                         retry_log=retry_log,
                                         layout_in_prefix=use_select)
        t_warm = time.time() - t0
        print(f"  [slidegen] slides 2..{len(slides)} in parallel "
              f"(warm-up took {t_warm:.1f}s)")
        rest = await asyncio.gather(*[
            _generate_one(client, model, system, outline, entry, i, usage_acc,
                          archetypes[i-1], neighbors_of(i), think=think,
                          retry_log=retry_log, layout_in_prefix=use_select)
            for i, entry in enumerate(slides[1:], start=2)
        ])
        specs = [first_spec] + list(rest)
    t_gen = time.time() - t0

    # Safety net: give any query-less image element a prompt from its slide so it
    # renders a picture instead of an empty box (must run before resolution).
    _bf = _backfill_image_prompts(specs, outline)
    if _bf:
        print(f"  [images] backfilled {_bf} image element(s) missing a query/prompt")

    # Resolve image-element `query` strings into real srcs BEFORE download. The
    # provider (Pexels stock search, or AI generation) is chosen by config/env;
    # AI writes local files + manifest, then Pexels backfills any failures.
    # Must finish before prefetch so the cache pulls the resolved srcs.
    await _resolve_images(specs, run_dir, config)

    # Download every referenced image into run_dir/images/ while we expand and
    # merge — the QA renderer and the PPTX exporter both reuse the local copies.
    prefetch_task = None
    if run_dir is not None:
        from core.image_cache import prefetch_images
        prefetch_task = asyncio.create_task(
            prefetch_images(specs, Path(run_dir)))

    # Deterministic layout normalization — the LLM decided design INTENT; this
    # pass guarantees clean EXECUTION (snap/align/spacing/overlap/safe-zone)
    # before expansion. Conservative: only sub-tolerance drift is corrected.
    from core.layout import normalize_layout
    layout_fixes = layout_unresolved = 0
    for i, spec in enumerate(specs, start=1):
        _, rep = normalize_layout(spec)
        layout_fixes += len(rep)
        layout_unresolved += len(rep.unresolved)
        if rep.unresolved:
            print(f"  [layout] slide {i}: {len(rep.unresolved)} overlap(s) "
                  f"deterministic fixes couldn't resolve — left for visual QA")
    if layout_fixes:
        print(f"  [slidegen] layout normalization applied {layout_fixes} "
              f"correction(s); {layout_unresolved} left for visual QA")

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
    fitted = _fit_single_line_labels(merged)
    if fitted:
        print(f"  [slidegen] shrank {fitted} caption/kicker label(s) to fit one line")
    aligned = _align_card_grids(merged)
    if aligned:
        print(f"  [slidegen] aligned {aligned} card(s) into their row grid")
    clamped = _clamp_text_safe_zone(merged)
    if clamped:
        print(f"  [slidegen] auto-clamped {clamped} text element(s) into the safe zone")
    unmasked = _unmask_framed_images(merged)
    if unmasked:
        print(f"  [slidegen] unmasked {unmasked} image(s) hidden behind an opaque frame")
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
        # Writes merged_deck.json (split) + editor_deck.json (flat, importable
        # in the editor's Import JSON).
        write_deck_outputs(merged, run_dir)
        if plans:
            (run_dir / "design_plan.json").write_text(
                json.dumps(plans, indent=2), encoding="utf-8")
        if prefetch_task is not None:
            await prefetch_task  # manifest must exist before QA render / export
            # Deterministic broken-image guard (no vision model): a 404/flaky URL
            # is simply absent from the manifest and would render as a broken
            # image. Retry the fetch once — catches transient failures — and warn
            # on any that remain, so a broken image doesn't silently ship when the
            # visual-QA pass is off. Renderers resolve by URL->manifest at render
            # time, so a late manifest update needs no re-merge.
            from core.image_cache import load_manifest, image_urls_from_specs
            _man = load_manifest(run_dir)
            _broken = [u for u in image_urls_from_specs(specs) if u not in _man]
            if _broken:
                print(f"  [images] {len(_broken)} image(s) failed to cache — "
                      f"retrying fetch")
                _man = await prefetch_images(specs, Path(run_dir))
                _broken = [u for u in image_urls_from_specs(specs)
                           if u not in _man]
                if _broken:
                    print(f"  [images] WARNING: {len(_broken)} image(s) still "
                          f"unresolved after retry (may render broken): "
                          f"{_broken[:3]}")

        # Deliver-then-patch: hand the deck to the caller NOW; the QA loop
        # below improves slides in place and the caller patches afterwards.
        if on_deck_ready is not None:
            try:
                await on_deck_ready(merged, stats)
            except Exception as e:
                print(f"  [slidegen] on_deck_ready callback failed (non-fatal): {e}")

        # ── Visual QA loop: screenshot + vision judge, regenerate failures ──
        # Visual QA on by default; set SLIDEGEN_VISUAL_QA=0 to disable. It is
        # the only reliable catcher of visual issues (overlaps/contrast/broken
        # images). Guarded so a missing Playwright/browser degrades to shipping
        # the deck without QA rather than crashing generation.
        _qa = os.environ.get("SLIDEGEN_VISUAL_QA", "1").strip().lower()
        if _qa not in ("0", "false", "no", "off", ""):
            try:
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
                                      qa_feedback=format_feedback(r),
                                      retry_log=retry_log, phase="qa",
                                      layout_in_prefix=use_select)
                        for r in failing
                    ])

                    def _remerge():
                        m = merge_presentations(part_paths)
                        m["presentation"]["description"] = outline.get("subtitle", "")
                        _fit_single_line_labels(m)
                        _align_card_grids(m)
                        _clamp_text_safe_zone(m)
                        _unmask_framed_images(m)
                        write_deck_outputs(m, run_dir)
                        return m

                    def _write_part(n, spec):
                        specs[n - 1] = spec
                        normalize_layout(spec)   # same geometry guarantee on QA rerun
                        part = expand_slide_spec(spec, deck_title=title,
                                                 slide_number=n,
                                                 deck_id=deck_id, timestamp=now)
                        part_paths[n - 1].write_text(json.dumps(part),
                                                     encoding="utf-8")

                    await _resolve_images(new_specs, run_dir, config)  # query -> src
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
                    new_specs_by_n = {r["slide_number"]: sp
                                      for r, sp in zip(failing, new_specs)}
                    qa_stats["judge_tokens"]["input"] += report2["tokens"]["input"]
                    qa_stats["judge_tokens"]["output"] += report2["tokens"]["output"]

                    # Keep the better of {original, first regen} per slide, tracked as
                    # the running best so still-bad slides can be retried.
                    best = {}
                    for n in nums:
                        if new_by_n[n]["score"] >= old_by_n[n]["score"]:
                            best[n] = {"spec": new_specs_by_n[n],
                                       "score": new_by_n[n]["score"],
                                       "entry": new_by_n[n]}
                        else:
                            print(f"  [visual-qa] slide {n} got worse "
                                  f"({old_by_n[n]['score']} -> {new_by_n[n]['score']}) "
                                  f"— keeping original")
                            best[n] = {"spec": old_specs[n],
                                       "score": old_by_n[n]["score"],
                                       "entry": old_by_n[n]}
                            qa_stats["reverted"].append(n)
                    for n in nums:                          # disk == running best
                        _write_part(n, best[n]["spec"])

                    # Escalated retry: a visibly-broken slide (score <= SEVERE, e.g.
                    # missing content / bad overlaps) must not ship. Keep regenerating
                    # it with the latest judge feedback, keeping the best version, until
                    # it clears the bar or we exhaust MAX_ATTEMPTS total tries per slide.
                    SEVERE = int(os.environ.get("SLIDEGEN_QA_SEVERE_MAX", "4"))
                    MAX_ATTEMPTS = max(1, int(
                        os.environ.get("SLIDEGEN_QA_MAX_ATTEMPTS", "3")))
                    attempt = 1                             # the first regen already ran
                    while attempt < MAX_ATTEMPTS:
                        severe = [n for n in nums if best[n]["score"] <= SEVERE]
                        if not severe:
                            break
                        attempt += 1
                        print(f"  [visual-qa] escalated retry {attempt}/{MAX_ATTEMPTS} "
                              f"for severe slide(s) {severe} (score <= {SEVERE})")
                        cand = await asyncio.gather(*[
                            _generate_one(client, model, system, outline,
                                          slides[n - 1], n, usage_acc,
                                          archetypes[n - 1], neighbors_of(n),
                                          plan_text=plans.get(n), think=False,
                                          qa_feedback=format_feedback(best[n]["entry"]),
                                          retry_log=retry_log, phase="qa",
                                          layout_in_prefix=use_select)
                            for n in severe])
                        cand_by_n = dict(zip(severe, cand))
                        await _resolve_images(cand, run_dir, config)
                        for n in severe:
                            _write_part(n, cand_by_n[n])
                        await prefetch_images(cand, run_dir)
                        _remerge()
                        rep = await run_visual_qa(run_dir, outline=outline,
                                                  plans=plans, only_slides=set(severe))
                        rep_by_n = {r["slide_number"]: r for r in rep["slides"]}
                        qa_stats["judge_tokens"]["input"] += rep["tokens"]["input"]
                        qa_stats["judge_tokens"]["output"] += rep["tokens"]["output"]
                        for n in severe:
                            if rep_by_n[n]["score"] > best[n]["score"]:
                                best[n] = {"spec": cand_by_n[n],
                                           "score": rep_by_n[n]["score"],
                                           "entry": rep_by_n[n]}
                                qa_stats.setdefault("escalated", [])
                                if n not in qa_stats["escalated"]:
                                    qa_stats["escalated"].append(n)
                            else:
                                _write_part(n, best[n]["spec"])   # revert to best

                    merged = _remerge()
                    qa_stats["final_scores"] = {n: best[n]["score"] for n in nums}

                qa_stats["seconds"] = round(time.time() - t_qa, 1)
                stats["visual_qa"] = qa_stats
                stats["total_seconds"] = round(time.time() - t0, 1)
                print(f"  [visual-qa] done in {qa_stats['seconds']}s — "
                      f"regenerated {len(qa_stats['regenerated'])}, "
                      f"reverted {len(qa_stats['reverted'])}")


            except Exception as _qa_err:
                print(f"  [visual-qa] skipped — unavailable or failed "
                      f"({type(_qa_err).__name__}: {_qa_err}); shipping deck "
                      f"without QA (install playwright to enable).")
        stats["retries"] = _summarize_retries(retry_log)
        _print_retry_summary(stats["retries"])
        (run_dir / "slidegen_stats.json").write_text(
            json.dumps(stats, indent=2), encoding="utf-8")
    else:
        stats["retries"] = _summarize_retries(retry_log)
        _print_retry_summary(stats["retries"])
    return merged, stats
