"""
Local artifact dumps for inspection.

Writes the outline (stage 1) and the final deck JSON (stage 2) into a single
per-presentation folder so both can be eyeballed side by side:

    output/<presentation_id>/
        outline.json   — the approved outline used as the design brief
        deck.json      — the final merged deck stored in MongoDB

Keyed on presentation_id (shared across both stages) so the two files always
land together even though they are produced at different times.
"""

import json
import os
import time
from pathlib import Path

from core.config import PROJECT_DIR


def _base_dir() -> Path:
    # Override with LOCAL_OUTPUT_DIR if set, else <project>/output
    override = os.environ.get("LOCAL_OUTPUT_DIR")
    return Path(override) if override else (PROJECT_DIR / "output")


def _folder(presentation_id: str) -> Path:
    d = _base_dir() / str(presentation_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def dump_outline(presentation_id: str, prompt: str, outline: dict) -> Path:
    """Write outline.json (+ a small meta) for a presentation."""
    folder = _folder(presentation_id)
    path = folder / "outline.json"
    path.write_text(json.dumps(outline, indent=2, ensure_ascii=False), encoding="utf-8")
    (folder / "meta.json").write_text(
        json.dumps(
            {
                "presentation_id": str(presentation_id),
                "prompt": prompt,
                "outline_written_at": int(time.time() * 1000),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"[local_dump] outline -> {path}")
    return path


def dump_deck(presentation_id: str, deck: dict) -> Path:
    """Write deck.json (final merged deck) into the same folder as the outline."""
    folder = _folder(presentation_id)
    path = folder / "deck.json"
    path.write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[local_dump] deck -> {path}")
    return path
