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
from core.slidegen import generate_deck_per_slide, warm_static_prefix  # noqa: E402

DEFAULT_CONFIG = {
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
    parser = argparse.ArgumentParser(
        description="Generate a full deck for any topic. Override the look with "
                    "--palette / --tone without editing the script.",
        epilog='Example: python scripts/run_topic.py "the joy of donuts" --slides 8 '
               '--tone "playful, vibrant, fun" '
               '--palette "Cherry Bold" '
               '(palette: a name from skills/core/11-visual-design-guide.md, '
               '"auto" to let the art director choose, or a full custom hex spec).',
    )
    parser.add_argument("topic", help="presentation topic / prompt")
    parser.add_argument("--slides", type=int, default=10)
    parser.add_argument("--palette", default=None,
                        help='palette name, "auto", or a custom hex description')
    parser.add_argument("--tone", default=None,
                        help='deck tone, e.g. "playful, vibrant" or "confident, premium"')
    parser.add_argument("--audience", default=None, help="target audience")
    parser.add_argument("--font", default=None,
                        help='font family, or "auto" to let the director pick')
    parser.add_argument("--images", default=None,
                        choices=["pexels", "openai", "auto"],
                        help='image source: "pexels" stock (default), "openai" '
                             'AI-generated (gpt-image-1, needs OPENAI_API_KEY), '
                             'or "auto" (AI when a key is present)')
    args = parser.parse_args()

    config = dict(DEFAULT_CONFIG)
    if args.palette:
        config["palette"] = args.palette
    if args.tone:
        config["tone"] = args.tone
    if args.audience:
        config["audience"] = args.audience
    if args.font:
        config["fontFamily"] = args.font
    if args.images:
        config["image_provider"] = args.images

    preflight()
    run_id = f"run-topic-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[topic] run dir: {run_dir}")
    print(f"[topic] generating {args.slides}-slide outline "
          f"(warming prompt cache in parallel)...")
    # Warm the static skills prefix as a background task while the outline
    # generates AND while Stage-1 layout selection runs — so the art director
    # call starts from a cache read. Stage-1 selection (inside
    # generate_deck_per_slide) needs the outline, so it fires the moment the
    # outline returns and overlaps the tail of this warm.
    warm_task = asyncio.create_task(warm_static_prefix())
    outline = await generate_outline(args.topic, args.slides, run_dir=run_dir)
    print_outline(outline)

    print(f"[topic] palette={config['palette']!r}  tone={config['tone']!r}")
    deck, stats = await generate_deck_per_slide(outline, config, run_dir=run_dir)
    if not warm_task.done():   # normally finished long ago; don't leak the task
        warm_task.cancel()
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
