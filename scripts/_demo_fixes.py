"""Forced demo of two layout fixes: split-feature (full-image overlay, no half
seam) and light-art-panel-close (deliberate art panel, no random scatter / ghost
over title). Monkeypatches assign_archetypes so those layouts are guaranteed to
appear; runs with layout-selection OFF."""
import asyncio, json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.config import WORKSPACE, VALIDATOR, preflight
import core.slidegen as sg

OUTLINE = {
    "title": "The Future of Sustainable Energy",
    "subtitle": "Navigating the transition to clean power.",
    "slides": [
        {"slide_number": 1, "layout": "title_only", "bg": "dark",
         "title": "The Energy Transition Is Now",
         "subtitle": "Building a sustainable, competitive future.", "bullets": []},
        {"slide_number": 2, "layout": "bullets", "bg": "dark",
         "title": "Supply Chain Bottlenecks", "subtitle": "The critical challenge ahead.",
         "bullets": ["Demand outpaces supply: rare-earth demand exceeds supply 30% by 2025.",
                     "Concentrated processing: China controls 80% of critical minerals.",
                     "Immature recycling: 90% of lithium still ends up in landfills."]},
        {"slide_number": 3, "layout": "bullets", "bg": "dark",
         "title": "Grid Modernization", "subtitle": "Where investment is flowing.",
         "bullets": ["Storage: grid-scale batteries down 40% in cost since 2022.",
                     "Smart grids: AI-balanced load cuts waste 18%.",
                     "Interconnection: 2,000 GW of projects awaiting grid access."]},
        {"slide_number": 4, "layout": "closing", "bg": "light",
         "title": "Let's Build",
         "subtitle": "Contact us to explore renewable energy solutions.",
         "bullets": ["hello@sustainable.energy  ·  sustainable.energy"]},
    ],
}

# name -> (name, body) from the (edited) library
def arch(name):
    for lst in sg._ARCHETYPES_BY_LAYOUT.values():
        for a in lst:
            if a[0] == name:
                return a
    raise SystemExit(f"archetype {name!r} not found")

FORCED = [arch("circular subject hero"), arch("split feature"),
          arch("split feature"), arch("light art-panel close")]
sg.assign_archetypes = lambda slides, seed=0: FORCED  # force the fix-target layouts


async def main():
    preflight()
    run_dir = WORKSPACE / f"run-demofix-{int(time.time()*1000)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[demofix] run dir: {run_dir}")
    print("[demofix] forced:", [a[0] for a in FORCED])
    config = {"tone": "premium, confident, forward-looking", "palette": "Deep Navy & Gold",
              "fontFamily": "auto", "audience": "Executives", "pageNumbers": True,
              "image_provider": "openai"}
    deck, stats = await sg.generate_deck_per_slide(OUTLINE, config, run_dir=run_dir)
    print(f"[demofix] cost=${stats.get('cost_usd')}  slides={stats.get('slides')}")
    merged = run_dir / "merged_deck.json"
    r = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                       capture_output=True, text=True)
    print(f"[demofix] validation: {'PASS' if r.returncode == 0 else 'FAIL'}")
    subprocess.run([sys.executable, "scripts/render_html_preview.py", str(merged)])
    from core.visual_qa import screenshot_slides
    shots = await screenshot_slides(run_dir / "preview.html", run_dir / "shots")
    print("[demofix] shots:", {i: str(p) for i, p in shots.items()})
    print(f"[demofix] DONE -> {run_dir}")


if __name__ == "__main__":
    asyncio.run(main())
