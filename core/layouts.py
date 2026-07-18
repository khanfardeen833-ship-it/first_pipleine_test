"""
Layout library + two-stage layout selection.

Composition archetypes ("layouts") live as one .md file each under
skills/layouts/<layout_type>/, with a small frontmatter block:

    ---
    id: full-bleed-hero
    name: full-bleed hero
    layout_type: title_only
    order: 0
    description: Opening hero — full-bleed image or deep color field, kicker chip, 58-72pt title on one side.
    ---
    <full composition spec — the exact text the slide executor follows>

WHY two stages (see skills/00-index.md):
  Stage 1 — select_layouts(): a cheap Haiku call is shown ONLY the lightweight
  INDEX (id + one-line description per layout, ~20 tokens each) plus the core
  design rules, and returns one layout id per slide. This scales to 100+
  layouts without ever putting all of them in a prompt.
  Stage 2 — slidegen inlines ONLY the SELECTED layouts' full specs into its
  cached system prefix; every parallel slide of the run shares that one prefix.

Backward compatibility: layout types not yet migrated to files fall back to the
legacy in-code archetype dict (passed in from core.slidegen). Their one-line
index description is derived from the first sentence of the spec. When every
type is migrated, the legacy dict is empty and this module is the sole source.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

import anthropic

from core.config import LAYOUTS_DIR

# Frontmatter fields every FILE layout must define (legacy layouts derive them).
_REQUIRED_FM = ("id", "name", "layout_type", "description")


@dataclass(frozen=True)
class Layout:
    id: str            # stable slug, used in Stage-1 selection JSON
    name: str          # human display name (matches the old archetype name)
    layout_type: str   # outline layout bucket: title_only | bullets | ...
    description: str    # one-line "when to use" — the index entry
    body: str          # full composition spec (single flowed paragraph)
    order: int         # position within its layout_type (rotation order)
    source: str        # "file" | "legacy"


# ---------------------------------------------------------------------------
# Parsing / normalization
# ---------------------------------------------------------------------------
def _parse_frontmatter(path: Path) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Frontmatter is the block between the
    first two '---' lines; keys are simple 'key: value' pairs."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path.name}: missing '---' frontmatter opener")
    fm: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if line.strip():
            key, sep, val = line.partition(":")
            if sep:
                fm[key.strip()] = val.strip()
        i += 1
    if i >= len(lines):
        raise ValueError(f"{path.name}: frontmatter not terminated with '---'")
    body = "\n".join(lines[i + 1:])
    return fm, body


def _flow(body: str) -> str:
    """Collapse a soft-wrapped prose spec to one spaced paragraph. Archetype
    specs are single-paragraph; files are wrapped only for readability, so
    joining wrapped lines with a space reproduces the original string."""
    return re.sub(r"\s*\n\s*", " ", body).strip()


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _first_sentence(text: str, limit: int = 170) -> str:
    """Derive a one-line index description from a legacy spec's first sentence."""
    t = _flow(text)
    m = re.search(r"(.+?[.!?])(?:\s|$)", t)
    s = m.group(1) if m else t
    return (s[: limit].rstrip() + "…") if len(s) > limit else s


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_file_layouts() -> list[Layout]:
    """Load every skills/layouts/**/*.md file. Raises loudly (used by preflight)
    if a file is missing a required frontmatter field or has a bad layout_type."""
    out: list[Layout] = []
    if not LAYOUTS_DIR.exists():
        return out
    for path in sorted(LAYOUTS_DIR.rglob("*.md")):
        fm, body = _parse_frontmatter(path)
        missing = [k for k in _REQUIRED_FM if not fm.get(k)]
        if missing:
            raise ValueError(
                f"{path.name}: missing frontmatter field(s): {', '.join(missing)}")
        if not _flow(body):
            raise ValueError(f"{path.name}: empty layout body")
        out.append(Layout(
            id=fm["id"], name=fm["name"], layout_type=fm["layout_type"],
            description=fm["description"], body=_flow(body),
            order=int(fm.get("order", 0)), source="file",
        ))
    return out


def build_library(legacy: dict | None) -> dict[str, Layout]:
    """id -> Layout. File layouts win; any layout_type NOT present in files is
    filled from the legacy in-code archetype dict {type: [(name, body), ...]}."""
    layouts = load_file_layouts()
    migrated = {l.layout_type for l in layouts}
    for ltype, arch in (legacy or {}).items():
        if ltype in migrated:
            continue
        for i, (name, body) in enumerate(arch):
            layouts.append(Layout(
                id=_slugify(name), name=name, layout_type=ltype,
                description=_first_sentence(body), body=body,
                order=i, source="legacy",
            ))
    lib: dict[str, Layout] = {}
    for l in layouts:
        if l.id in lib:
            raise ValueError(
                f"duplicate layout id {l.id!r} "
                f"({lib[l.id].layout_type} vs {l.layout_type})")
        lib[l.id] = l
    return lib


def _ordered(lib: dict[str, Layout]) -> list[Layout]:
    return sorted(lib.values(), key=lambda x: (x.layout_type, x.order))


def archetypes_by_layout(lib: dict[str, Layout]) -> dict[str, list[tuple[str, str]]]:
    """Rebuild the legacy {layout_type: [(name, body), ...]} dict from the
    library, preserving per-type order — keeps assign_archetypes() (the seed=0
    fallback) and scripts/_showcase_archetypes.py working unchanged."""
    out: dict[str, list[tuple[str, str]]] = {}
    for l in _ordered(lib):
        out.setdefault(l.layout_type, []).append((l.name, l.body))
    return out


def layout_index_text(lib: dict[str, Layout]) -> str:
    """The lightweight Stage-1 index: one '- id [type]: description' line each."""
    return "\n".join(
        f"- {l.id} [{l.layout_type}]: {l.description}" for l in _ordered(lib))


# ---------------------------------------------------------------------------
# Stage 1 — layout selection
# ---------------------------------------------------------------------------
SELECT_TOOL = {
    "name": "select_layouts",
    "description": "Choose the single best composition layout for every slide "
                   "in the deck, using the layout library index.",
    "input_schema": {
        "type": "object",
        "properties": {
            "slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "slide_number": {"type": "integer"},
                        "layout_id": {
                            "type": "string",
                            "description": "a layout id copied verbatim from the index",
                        },
                    },
                    "required": ["slide_number", "layout_id"],
                },
            },
        },
        "required": ["slides"],
    },
}


def fallback_selection(outline: dict, lib: dict[str, Layout],
                       seed: int = 0) -> dict[int, str]:
    """Deterministic seed=0 assignment — the exact rotation assign_archetypes()
    used to do, expressed over the library. Rotates within each slide's outline
    layout_type; unknown types fall back to the 'bullets' pool."""
    by_type: dict[str, list[Layout]] = {}
    for l in _ordered(lib):
        by_type.setdefault(l.layout_type, []).append(l)
    default_pool = by_type.get("bullets") or next(iter(by_type.values()))
    counters: dict[str, int] = {}
    out: dict[int, str] = {}
    for i, s in enumerate(outline.get("slides", []), start=1):
        lt = s.get("layout", "bullets")
        pool = by_type.get(lt) or default_pool
        idx = counters.get(lt, 0)
        out[i] = pool[(idx + seed) % len(pool)].id
        counters[lt] = idx + 1
    return out


async def select_layouts(outline: dict, lib: dict[str, Layout], *,
                         core_rules: str = "", model: str | None = None,
                         usage_acc: list | None = None
                         ) -> tuple[dict[int, str], str]:
    """Stage 1. Returns ({slide_number: layout_id}, source) where source is
    'selected' (the model chose) or 'fallback' (seed=0 default set).

    The model sees only the lightweight index + core rules. Any unknown id, a
    missing slide, or an API/parse error does NOT silently drop the slide — it
    aborts the selection and falls back to the deterministic seed=0 set."""
    slides = outline.get("slides", [])
    if not slides:
        return {}, "fallback"
    model = model or os.environ.get("ANTHROPIC_OUTLINE_MODEL", "claude-haiku-4-5")

    system = (
        "You are the ART DIRECTOR picking the composition layout for each slide "
        "of ONE presentation deck.\n\n"
        "LAYOUT LIBRARY INDEX  (format: id [type]: when to use)\n"
        f"{layout_index_text(lib)}\n"
    )
    if core_rules:
        system += "\n---\n\nCORE DESIGN RULES\n" + core_rules

    listing = "\n".join(
        f"  slide {s.get('slide_number', i)}: [{s.get('layout', 'bullets')}] "
        f"{s.get('title', '')}"
        for i, s in enumerate(slides, start=1))
    msg = (
        f"DECK: {outline.get('title', '')} — {outline.get('subtitle', '')}\n\n"
        f"SLIDES ({len(slides)}):\n{listing}\n\n"
        "For EACH slide choose the ONE best layout_id from the index whose "
        "'when to use' fits the slide's content and its [type] hint.\n"
        "RULES:\n"
        "- Prefer a layout whose [type] matches the slide's type hint; choose a "
        "different type only when it clearly fits the content better.\n"
        "- ADJACENT SLIDES MUST NOT SHARE A LAYOUT: no two consecutive slides "
        "may use the same layout_id, and vary the structural skeleton across the "
        "deck so nothing repeats back-to-back (this is what stops every slide "
        "from looking alike).\n"
        "- Reuse a layout elsewhere in the deck only when the content genuinely "
        "repeats; overall aim for a varied set (typically 8-15 distinct layouts).\n"
        "- Return exactly one entry per slide, covering every slide number.\n"
        "Emit your choices via the select_layouts tool."
    )

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    try:
        resp = await client.messages.create(
            model=model, max_tokens=2048, system=system,
            tools=[SELECT_TOOL],
            tool_choice={"type": "tool", "name": "select_layouts"},
            messages=[{"role": "user", "content": msg}],
        )
        if usage_acc is not None:
            usage_acc.append(resp.usage)
        payload = next((b.input for b in resp.content if b.type == "tool_use"), None)
        if not payload:
            raise ValueError("no select_layouts tool call returned")

        chosen: dict[int, str] = {}
        for entry in payload.get("slides", []):
            n = int(entry["slide_number"])
            lid = str(entry["layout_id"]).strip()
            if lid not in lib:
                raise ValueError(f"slide {n}: unknown layout_id {lid!r}")
            chosen[n] = lid
        missing = [i for i in range(1, len(slides) + 1) if i not in chosen]
        if missing:
            raise ValueError(f"selection did not cover slide(s) {missing}")
        return chosen, "selected"
    except Exception as e:
        print(f"  [layouts] Stage-1 selection failed ({e}); "
              f"using seed=0 fallback set")
        return fallback_selection(outline, lib, seed=0), "fallback"


def selected_layouts_block(layouts: list[Layout]) -> str:
    """The Stage-2 system block: full specs for ONLY the selected layouts."""
    parts = [
        "### SELECTED LAYOUTS FOR THIS DECK",
        "Each slide's request names one of these as its COMPOSITION ARCHETYPE. "
        "Follow the matching spec below exactly as that slide's structural "
        "skeleton.",
    ]
    for l in layouts:
        parts.append(f"## {l.name}  [{l.layout_type}]\n{l.body}")
    return "\n\n".join(parts)


def estimate_tokens(text: str) -> int:
    """Cheap heuristic token estimate (~4 chars/token) — avoids a count_tokens
    round-trip. Labeled 'est' wherever it is logged."""
    return (len(text) + 3) // 4
