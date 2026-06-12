"""
Generate a full premium deck for any topic — real pipeline, no MongoDB.

Runs: planner outline (Haiku) -> slidegen director mode -> validate ->
deck.pptx + preview.html, all into workspace/<run_id>/.

Usage:
    python scripts/run_topic.py "luxury electric hypercar launch" [--slides 10]
"""

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import WORKSPACE, VALIDATOR, preflight  # noqa: E402  (loads .env)
from core.planner import generate_outline, print_outline  # noqa: E402
from core.slidegen import generate_deck_per_slide         # noqa: E402

CONFIG = {
    "density": "Standard",
    "audience": "Executive Leadership",
    "tone": "confident, premium",
    "fontFamily": "auto",
    "fontSize": "Medium",
    "palette": "auto",
    "imageSource": "pexels",
    "pageNumbers": True,
}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", help="presentation topic / prompt")
    parser.add_argument("--slides", type=int, default=10)
    args = parser.parse_args()

    preflight()
    run_id = f"run-topic-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[topic] run dir: {run_dir}")
    print(f"[topic] generating {args.slides}-slide outline...")
    outline = await generate_outline(args.topic, args.slides, run_dir=run_dir)
    print_outline(outline)

    deck, stats = await generate_deck_per_slide(outline, CONFIG, run_dir=run_dir)
    print(f"[topic] stats: {json.dumps(stats, indent=2)}")

    merged = run_dir / "merged_deck.json"
    result = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                            capture_output=True, text=True)
    print(result.stdout)
    print(f"[topic] validation: {'PASS' if result.returncode == 0 else 'FAIL'}")

    from core.pptx_exporter import export_slides_to_pptx
    pptx_path = run_dir / "deck.pptx"
    await export_slides_to_pptx(deck, pptx_path)
    print(f"[topic] pptx: {pptx_path}  ({pptx_path.stat().st_size:,} bytes)")

    preview = subprocess.run([sys.executable, "scripts/render_html_preview.py", str(merged)],
                             capture_output=True, text=True)
    print(preview.stdout.strip())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    asyncio.run(main())
