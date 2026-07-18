"""
Merges parallel batch JSONs into a single Bildory presentation JSON.
Each batch generates non-overlapping slide IDs and element ID ranges,
so the merge is a straight concatenation with no renumbering.
"""

import json
import time
from pathlib import Path


# Element arrays that live at files.content level (not inside slides)
_CONTENT_ARRAY_KEYS = [
    "imageElements",
    "shapeElements",
    "chartElements",
    "tableElements",
    "iconElements",
    "embedElements",
    "smartDiagramElements",
    "groupElements",
]


def _count_elements(content: dict) -> int:
    total = sum(len(s.get("textElements", [])) for s in content.get("slides", []))
    for key in _CONTENT_ARRAY_KEYS:
        total += len(content.get(key, []))
    return total


def merge_presentations(batch_json_paths: list) -> dict:
    batches = []
    for p in batch_json_paths:
        with open(p, encoding="utf-8") as f:
            batches.append(json.load(f))

    if not batches:
        raise ValueError("No batch JSONs to merge")

    first = batches[0]
    merged_content   = first["files"]["content"]
    merged_layout    = first["files"]["baseLayout"]
    merged_changelog = first["files"]["changelog"]
    merged_pres      = first["presentation"]

    for batch in batches[1:]:
        c  = batch["files"]["content"]
        bl = batch["files"]["baseLayout"]
        cl = batch["files"]["changelog"]

        merged_content["slides"].extend(c.get("slides", []))

        for key in _CONTENT_ARRAY_KEYS:
            if key not in merged_content:
                merged_content[key] = []
            merged_content[key].extend(c.get(key, []))

        if "slides" in bl:
            merged_layout["slides"].extend(bl["slides"])

        # changelog.slides is a dict keyed by slide ID — no conflicts by design
        if "slides" in cl:
            if "slides" not in merged_changelog:
                merged_changelog["slides"] = {}
            merged_changelog["slides"].update(cl["slides"])

    # order must match array index exactly
    for i, slide in enumerate(merged_content["slides"]):
        slide["order"] = i

    slide_count   = len(merged_content["slides"])
    element_count = _count_elements(merged_content)
    merged_pres["slideCount"]   = slide_count
    merged_pres["elementCount"] = element_count
    first["exportedAt"]          = int(time.time() * 1000)

    return first


# ---------------------------------------------------------------------------
# Editor-import format
#
# The merged deck above is the *split* Bildory format (files.content +
# files.changelog — content strings and geometry kept apart). The bildory
# editor's "Import JSON" button wants the *flat* format instead: a top-level
# slides[] where every element carries its content AND its design together.
# core/storage._build_slides delegates here so this collapse has one home.
# ---------------------------------------------------------------------------

# content-array key -> element `type` the editor keys renderers off of.
_ARRAY_TYPE_MAP = {
    "shapeElements": "shape",
    "iconElements":  "icon",
    "chartElements": "chart",
    "tableElements": "table",
    "imageElements": "image",
    "embedElements": "embed",
}


def build_editor_slides(deck: dict) -> list:
    """Split (files.content/changelog) deck -> flat slides[].elements[]."""
    files     = deck.get("files", {})
    content   = files.get("content", {})
    changelog = files.get("changelog", {}).get("slides", {})

    # element id -> {type, ...content fields}  (non-text elements)
    elem_content: dict[str, dict] = {}
    for array_key, type_name in _ARRAY_TYPE_MAP.items():
        for rec in content.get(array_key, []):
            elem_content[rec["id"]] = {
                "type": type_name,
                **{k: v for k, v in rec.items() if k != "id"},
            }

    slides = []
    for slide in content.get("slides", []):
        slide_id = slide["id"]
        cl_elems = changelog.get(slide_id, {}).get("elements", {})
        text_lookup = {t["id"]: t for t in slide.get("textElements", [])}

        elements = []
        for elem_id, cl_data in cl_elems.items():
            merged = {"id": elem_id}

            if elem_id in text_lookup:
                t = text_lookup[elem_id]
                merged["type"]             = t.get("type", "text")
                merged["content"]          = t.get("content", "")
                merged["formattedContent"] = t.get("formattedContent", "")
            elif elem_id in elem_content:
                merged.update(elem_content[elem_id])

            # overlay geometry/style; drop bookkeeping fields
            for k, v in cl_data.items():
                if k not in ("slideId", "updatedAt"):
                    merged[k] = v

            elements.append(merged)

        elements.sort(key=lambda e: e.get("zIndex", 0))
        slides.append({
            "id":              slide_id,
            "order":           slide.get("order", 0),
            "layoutId":        slide.get("layoutId", "blank-canvas"),
            "backgroundColor": slide.get("backgroundColor", "#ffffff"),
            "elements":        elements,
        })

    slides.sort(key=lambda s: s.get("order", 0))
    return slides


def build_editor_deck(deck: dict) -> dict:
    """Wrap the flat slides into the editor's import shape. If `deck` is
    already flat (has a top-level slides[] and no files), pass it through."""
    if isinstance(deck.get("slides"), list) and "files" not in deck:
        return deck
    pres = deck.get("presentation", {}) or {}
    return {
        "presentationId": pres.get("id") or pres.get("presentationId") or "",
        "title":          pres.get("title", ""),
        "slides":         build_editor_slides(deck),
    }


def write_deck_outputs(deck: dict, run_dir) -> None:
    """Write both on-disk deck artifacts: merged_deck.json (split, used by the
    PPTX exporter / HTML preview) and editor_deck.json (flat, importable in the
    editor's Import JSON). Keeping them together means the editor file never
    goes stale relative to the merged deck."""
    from pathlib import Path
    from core.layout_fix import normalize_layout
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Deterministic geometry cleanup (icon-to-badge snap, panel-grow) before the
    # deck is persisted — runs ahead of validate.py and the visual-QA loop.
    deck, layout_fixes = normalize_layout(deck)
    if layout_fixes:
        print(f"  layout_fix: {len(layout_fixes)} geometry fix(es)")
        for f in layout_fixes:
            print(f"    - {f}")

    (run_dir / "merged_deck.json").write_text(
        json.dumps(deck, indent=2), encoding="utf-8")
    (run_dir / "editor_deck.json").write_text(
        json.dumps(build_editor_deck(deck), ensure_ascii=False, indent=2),
        encoding="utf-8")
