"""Isolated test: does gpt-image-1 produce flat-3D corporate illustrations under
OPENAI_IMAGE_STYLE? Bypasses the planner — feeds image elements with baked
prompts straight into generate_image_queries."""
import asyncio, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()   # standalone script: load .env like the real pipeline entry points do

from core.openai_images import generate_image_queries

RUN = Path(__file__).resolve().parents[1] / "workspace" / f"illus-test-{int(time.time())}"
RUN.mkdir(parents=True, exist_ok=True)

# Two elements with concrete illustration prompts (what a layout spec would bake in)
specs = [{
    "elements": [
        {"kind": "image", "width": 640, "height": 640,
         "image_prompt": "a friendly 3D illustration of a desktop monitor showing "
                         "colorful bar charts and an upward trend line, a gold "
                         "trophy beside it, a compass and green check-mark badges"},
        {"kind": "image", "width": 640, "height": 640,
         "image_prompt": "a friendly 3D illustration of a rocket launching from a "
                         "laptop with coins and a target, growth concept"},
    ],
}]

STYLE = ("flat 3D isometric vector illustration, modern corporate style, bright "
         "blue and cyan color scheme with soft pastel tones, clean solid white "
         "background, smooth rounded 3D shapes, subtle soft shadows, friendly "
         "professional")


async def main():
    print(f"[test] run dir: {RUN}")
    print(f"[test] OPENAI_IMAGE_STYLE-equivalent passed as style=...")
    n = await generate_image_queries(specs, RUN, style=STYLE)
    print(f"[test] generated {n} image(s)")
    for p in sorted((RUN / "images").glob("*.png")):
        print(f"  {p}  ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
