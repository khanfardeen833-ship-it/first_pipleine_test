"""
Convert full deck structure to .pptx file using the Node.js export script.
"""

import asyncio
import json
from pathlib import Path

_SCRIPT = Path(__file__).parent.parent / "scripts" / "export_pptx.js"


async def export_slides_to_pptx(deck_data: dict, output_path: Path) -> Path:
    """
    Write full deck structure to a temp JSON file, call Node.js export script.

    Args:
        deck_data: Full deck dictionary with files.content.slides, files.changelog, etc.
                   (the merged_deck.json structure)
        output_path: Where to write the .pptx file

    Returns the output_path on success. Raises RuntimeError if Node exits non-zero.
    """
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
