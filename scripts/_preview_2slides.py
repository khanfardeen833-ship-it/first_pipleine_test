"""Regenerate ONLY the two flagged slides for preview: the split-feature
'Supply Chain Bottlenecks' (was a half-blue image seam) and the
light-art-panel-close 'Let's Build' (was a random shape scatter). Forces those
two layouts so the fixes are what we see."""
import asyncio, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.config import WORKSPACE, VALIDATOR, preflight
import core.slidegen as sg

OUTLINE = {
    "title": "The Future of Sustainable Energy",
    "subtitle": "Navigating the transition to clean power.",
    "slides": [
        {"slide_number": 1, "layout": "bullets", "bg": "dark",
         "title": "Supply Chain Bottlenecks", "subtitle": "The critical challenge ahead.",
         "bullets": ["Demand outpaces supply: rare-earth demand exceeds supply 30% by 2025.",
                     "Concentrated processing: China controls 80% of critical minerals.",
                     "Immature recycling: 90% of lithium still ends up in landfills."]},
        {"slide_number": 2, "layout": "closing", "bg": "light",
         "title": "Let's Build",
         "subtitle": "Contact us to explore renewable energy solutions.",
         "bullets": ["hello@sustainable.energy  ·  sustainable.energy"]},
    ],
}


def arch(name):
    for lst in sg._ARCHETYPES_BY_LAYOUT.values():
        for a in lst:
            if a[0] == name:
                return a
    raise SystemExit(f"archetype {name!r} not found")


FORCED = [arch("split feature"), arch("light art-panel close")]
sg.assign_archetypes = lambda slides, seed=0: FORCED


async def main():
    preflight()
    run_dir = WORKSPACE / f"run-preview2-{int(time.time()*1000)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[preview2] run dir: {run_dir}")
    print("[preview2] forced:", [a[0] for a in FORCED])
    config = {"tone": "premium, confident, forward-looking", "palette": "Deep Navy & Gold",
              "fontFamily": "auto", "audience": "Executives", "pageNumbers": True,
              "image_provider": "openai"}
    deck, stats = await sg.generate_deck_per_slide(OUTLINE, config, run_dir=run_dir)
    print(f"[preview2] cost=${stats.get('cost_usd')}")
    merged = run_dir / "merged_deck.json"
    r = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                       capture_output=True, text=True)
    print(f"[preview2] validation: {'PASS' if r.returncode == 0 else 'FAIL'}")
    subprocess.run([sys.executable, "scripts/render_html_preview.py", str(merged)])
    from core.visual_qa import screenshot_slides
    shots = await screenshot_slides(run_dir / "preview.html", run_dir / "shots")
    for i, p in sorted(shots.items()):
        print(f"[preview2] slide {i}: {p}")
    print(f"[preview2] DONE -> {run_dir}")


if __name__ == "__main__":
    asyncio.run(main())
