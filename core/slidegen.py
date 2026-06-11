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
    image: src, x, y, width, height, is_background, border_radius, opacity,
           object_fit, filter, blur, shadow, border, overlay, focus_point
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
  accent bars, thin rules, oversized ghost numbers/letters at 5-10% opacity)
  -> content cards/panels -> imagery with intentional filter+overlay ->
  icon badges -> typography. Aim for 14-24 elements.
- Typography hierarchy must be dramatic: one oversized anchor (a 100-200pt
  ghost number, a 54-72pt headline, or a 60-90pt stat) per slide.
- Extract numbers from the content and showcase them BIG (stat treatment),
  don't bury them in sentences.
- Asymmetry beats symmetry: vary card sizes, offset images, use 40/60 or
  30/70 splits, bleed one element off-canvas.
- Every card/panel gets breathing room: consistent internal padding (>=24px),
  consistent corner radii, aligned baselines across siblings.
"""

# Composition archetypes — rotated so adjacent slides never share a skeleton.
_ARCHETYPES_BY_LAYOUT = {
    "title_only": [
        ("full-bleed hero", "Full-canvas image (filter + dark overlay 55-70) or deep color field, "
         "kicker caption with letterspacing, 58-72pt title on the left 55%, thin accent rule, "
         "one-line subtitle. Optional oversized ghost glyph bleeding off the right edge."),
        ("split hero", "Left 45%: color panel with kicker, huge title, accent bar. Right 55%: "
         "full-height image with filter and palette-tinted overlay. One floating accent shape "
         "crossing the seam."),
    ],
    "bullets": [
        ("stat band", "Pull the numbers out of the bullets and set them 60-90pt across a band of "
         "3-4 stat blocks (number + thin divider + 2-line caption each). Side or bottom: one "
         "supporting image panel or icon-accented insight card."),
        ("icon card grid", "Each bullet becomes a card: rounded panel (subtle tint or stroke), "
         "ellipse icon badge, 4-6 word heading, short caption. Asymmetric grid — one card 1.5x "
         "wider or taller than the others."),
        ("numbered editorial", "Vertical list with oversized ghost numbers 01/02/03 (90-140pt, "
         "8-12% opacity) behind each row, left accent bars, heading + caption per row. Right "
         "30-40%: full-height image with overlay."),
        ("split feature", "Left 40%: full-height image, palette overlay, one stat or kicker "
         "overlaid on it. Right 60%: bullets as compact mini-cards with icon badges, staggered "
         "x-offsets so rows don't form a flat list."),
    ],
    "two_column": [
        ("dual panel", "Two contrasting panels (one tinted/filled, one outlined or white) with "
         "column headers + icon badges; bullets split between them as aligned rows. A vertical "
         "divider or floating badge bridges the two."),
        ("versus split", "Hard 50/50 split with opposing background tones, oversized column "
         "labels, mirrored row layout, central circular 'VS'/theme badge overlapping the seam."),
    ],
    "three_column": [
        ("three cards", "Three equal cards with top icon badges, bold 3-5 word headings, "
         "captions, and a footer accent bar each; middle card elevated (taller or tinted) for "
         "rhythm."),
    ],
    "timeline": [
        ("horizontal timeline", "Baseline connector line with circle year-badges, alternating "
         "labels above/below, accent dot for the 'now' marker, years set 26-34pt bold. Ghost "
         "year (e.g. 2026) oversized in the background."),
        ("vertical milestones", "Left rail with connector line and numbered/year badges, each "
         "milestone a row card to the right; final milestone highlighted with filled accent "
         "panel."),
    ],
    "chart": [
        ("chart + callout", "Chart on one side (55-65% width), headline insight as a big-stat "
         "callout card beside it, supporting points as small icon rows under the callout."),
    ],
    "quote": [
        ("editorial quote", "Oversized quotation-mark glyph (180-260pt text or shapes, low "
         "opacity), 34-44pt italic quote centered-left, attribution caption with accent rule, "
         "muted full-bleed image or deep color field behind."),
    ],
    "table": [
        ("framed table", "Table inside a framed panel with a heading row above it, one key-number "
         "callout chip beside/above the table, accent header treatment."),
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


def _palette_is_auto(config: dict) -> bool:
    """True when no palette is pinned — 'auto', empty, or omitted."""
    return str((config or {}).get("palette") or "auto").strip().lower() == "auto"


async def _design_plan(client, model, system, outline, archetypes, usage_acc,
                       palette_auto: bool = False) -> dict:
    """One deck-wide Opus thinking call → {slide_number: plan_text}."""
    listing = "\n".join(
        f"  slide {i}: [{s.get('layout','bullets')}] archetype \"{a[0]}\" — {s.get('title','')}"
        for i, (s, a) in enumerate(zip(outline.get("slides", []), archetypes), start=1)
    )
    palette_clause = ""
    if palette_auto:
        palette_clause = (
            "PALETTE IS AUTO: before planning slides, pick the single palette from "
            "11-visual-design-guide.md that best fits this topic's mood and subject "
            "(do not default to Midnight Executive). Name it and its exact hexes in "
            "deck_notes; every slide plan must use only that palette so the deck "
            "stays consistent.\n\n"
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
        "Decide deck-wide rhythm deliberately: where imagery clusters, where pure "
        "typography breathes, how dark/light alternation lands."
    )
    resp = await client.messages.create(
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


def assign_archetypes(slides: list) -> list:
    """Pick a composition archetype per slide, rotating within each layout type
    so adjacent slides (and repeated layouts) never share a skeleton."""
    counters: dict[str, int] = {}
    out = []
    for s in slides:
        layout = s.get("layout", "bullets")
        pool = _ARCHETYPES_BY_LAYOUT.get(layout, _ARCHETYPES_BY_LAYOUT["bullets"])
        i = counters.get(layout, 0)
        out.append(pool[i % len(pool)])
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
    brief = f"""DESIGN BRIEF (identical for every slide of this deck):
  Deck title: {outline.get('title', 'Untitled')}
  Deck subtitle: {outline.get('subtitle', '')}
  Total slides: {len(outline.get('slides', []))}
  Density: {config.get('density', 'Standard')}
  Audience: {config.get('audience', 'Executive Leadership')}
  Tone: {config.get('tone', '') or 'none specified'}
  Font Family: {config.get('fontFamily', 'Trebuchet MS')} (do NOT use Google fonts)
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


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
async def _generate_one(client, model, system, outline, slide_entry, slide_number,
                        usage_acc: list, archetype: tuple, neighbors: str,
                        plan_text: str | None = None, think: bool = True) -> dict:
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
    for attempt in range(1 + RETRIES_PER_SLIDE):
        try:
            resp = await client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS_PER_SLIDE,
                system=system,
                # both tools always — identical prefix = cache hits across calls
                tools=[SLIDE_TOOL, DESIGN_PLAN_TOOL],
                messages=[{
                    "role": "user",
                    "content": _slide_user_message(outline, slide_entry, slide_number,
                                                   archetype, neighbors, plan_text),
                }],
                **kwargs,
            )
            usage_acc.append(resp.usage)
            spec = next((b.input for b in resp.content if b.type == "tool_use"), None)
            if spec is None:
                raise ValueError("model returned no emit_slide call")
            # fail fast here so a broken spec retries while we're still parallel
            expand_slide_spec(spec, deck_title="probe", slide_number=slide_number,
                              deck_id="probe", timestamp=0)
            return spec
        except Exception as e:
            last_err = e
            print(f"  [slide-{slide_number}] attempt {attempt + 1} failed: {e}")
    raise RuntimeError(f"slide {slide_number} failed after retries: {last_err}")


async def generate_deck_per_slide(outline: dict, config: dict | None = None,
                                  run_dir: Path | None = None,
                                  mode: str | None = None) -> tuple[dict, dict]:
    """
    Generate a full deck with one parallel API call per slide.
    mode: fast | premium | director (default: env SLIDEGEN_MODE or 'director').
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
    archetypes = assign_archetypes(slides)
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
        # Deck-wide thinking call + executor-cache warmer run concurrently;
        # the warmer finishes in seconds, so the executors all hit cache.
        print(f"  [slidegen] art director planning {len(slides)} slides "
              f"(effort={THINKING_EFFORT}; warming executor cache in parallel)")
        plans, _ = await asyncio.gather(
            _design_plan(client, model, system, outline, archetypes, usage_acc,
                         palette_auto=_palette_is_auto(config)),
            _warm_executor_cache(client, model, system, usage_acc),
        )
        t_warm = time.time() - t0
        print(f"  [slidegen] plan ready in {t_warm:.1f}s — "
              f"executing {len(slides)} slides in parallel")
        specs = list(await asyncio.gather(*[
            _generate_one(client, model, system, outline, entry, i, usage_acc,
                          archetypes[i-1], neighbors_of(i),
                          plan_text=plans.get(i), think=False)
            for i, entry in enumerate(slides, start=1)
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
        (run_dir / "slidegen_stats.json").write_text(
            json.dumps(stats, indent=2), encoding="utf-8")
        if plans:
            (run_dir / "design_plan.json").write_text(
                json.dumps(plans, indent=2), encoding="utf-8")
    return merged, stats
