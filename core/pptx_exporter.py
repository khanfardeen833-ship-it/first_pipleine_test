"""
Convert full deck structure to .pptx file using the Node.js export script.
"""

import asyncio
import json
from copy import deepcopy
from pathlib import Path

_SCRIPT = Path(__file__).parent.parent / "scripts" / "export_pptx.js"


def _image_srcs(deck: dict):
    """Yield (setter, src) for every image src in either the split or flat deck
    shape, so callers can rewrite motif SVGs -> PNGs in place."""
    content = (deck.get("files", {}) or {}).get("content", {}) or {}
    for rec in content.get("imageElements") or []:
        if isinstance(rec.get("src"), str):
            yield rec
    for slide in deck.get("slides") or []:
        for el in slide.get("elements") or []:
            if el.get("type") in ("image", "gif") and isinstance(el.get("src"), str):
                yield el


async def _rasterize_motifs(deck_data: dict) -> dict:
    """Swap any motif SVG-data-URI background for a PNG data URI (PowerPoint
    renders SVG poorly). No-op if there are none / Playwright is unavailable."""
    svg_uris = [r["src"] for r in _image_srcs(deck_data)
                if r["src"].startswith("data:image/svg+xml")]
    if not svg_uris:
        return deck_data
    from core.motifs import rasterize_svg_data_uris
    mapping = await rasterize_svg_data_uris(list(dict.fromkeys(svg_uris)))
    if not mapping:
        return deck_data
    deck_data = deepcopy(deck_data)
    for rec in _image_srcs(deck_data):
        if rec["src"] in mapping:
            rec["src"] = mapping[rec["src"]]
    return deck_data


async def export_slides_to_pptx(deck_data: dict, output_path: Path) -> Path:
    """
    Write full deck structure to a temp JSON file, call Node.js export script.

    Args:
        deck_data: Full deck dictionary with files.content.slides, files.changelog, etc.
                   (the merged_deck.json structure)
        output_path: Where to write the .pptx file

    Returns the output_path on success. Raises RuntimeError if Node exits non-zero.
    """
    deck_data = await _rasterize_motifs(deck_data)
    tmp = output_path.parent / "_deck_export_tmp.json"
    tmp.write_text(json.dumps(deck_data), encoding="utf-8")

    try:
        proc = await asyncio.create_subprocess_exec(
            "node", str(_SCRIPT), str(tmp), str(output_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode(errors="replace").strip()
            raise RuntimeError(f"pptxgenjs exited {proc.returncode}: {err_msg}")

        return output_path
    finally:
        tmp.unlink(missing_ok=True)
