"""TEMP showcase: force the new archetypes into one deck so we can eyeball them.
Hand-written outline + a monkeypatch of assign_archetypes (no core changes)."""
import asyncio, json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.config import WORKSPACE, VALIDATOR, preflight
import core.slidegen as sg

# --- hand outline: each slide's layout matches the archetype we want to show ---
OUTLINE = {
    "title": "Lumen: Sleep, Reimagined",
    "subtitle": "A premium sleep & wellness app that adapts to your night.",
    "slides": [
        {"slide_number": 1, "layout": "title_only", "bg": "light",
         "title": "Lumen: Sleep, Reimagined",
         "subtitle": "The bedside companion that learns how you rest.", "bullets": []},
        {"slide_number": 2, "layout": "three_column", "bg": "light",
         "title": "Three Pillars of Better Sleep",
         "subtitle": "Everything Lumen does ladders up to these.",
         "bullets": ["Sense: passive sleep-stage tracking, no wearable required.",
                     "Soothe: adaptive soundscapes tuned to your heart rate.",
                     "Shift: gentle wake windows aligned to your lightest sleep."]},
        {"slide_number": 3, "layout": "three_column", "bg": "light",
         "title": "How Lumen Works",
         "subtitle": "From first night to lasting routine.",
         "bullets": ["Learn: 3 nights to model your personal sleep rhythm.",
                     "Adapt: nightly soundscape + wake window auto-tuned.",
                     "Improve: weekly insights turn data into better habits."]},
        {"slide_number": 4, "layout": "bullets", "bg": "light",
         "title": "What Members Get",
         "subtitle": "One membership, the full night handled.",
         "bullets": ["Adaptive soundscapes: 200+ tracks that respond in real time.",
                     "Smart alarm: wakes you in your lightest 20-minute window.",
                     "Sleep score: a single number, explained in plain language.",
                     "Wind-down: a guided 10-minute routine personalized nightly."]},
        {"slide_number": 5, "layout": "title_only", "bg": "light",
         "title": "Designed for the Bedside",
         "subtitle": "Calm hardware, calmer nights.", "bullets": []},
        {"slide_number": 6, "layout": "closing", "bg": "dark",
         "title": "Rest Easy — Start Tonight",
         "subtitle": "Your best night's sleep is one tap away.",
         "bullets": ["hello@lumen.sleep  ·  lumen.sleep/start"]},
    ],
}

WANT = [
    ("title_only", "circular cutout hero"),
    ("three_column", "tri-circle overlap"),
    ("three_column", "pill-header ghost trio"),
    ("bullets", "numbered card rail"),
    ("title_only", "photo-card + offset panel"),
    ("closing", "dark glow close"),
]


def pick(layout, name):
    return next(a for a in sg._ARCHETYPES_BY_LAYOUT[layout] if a[0] == name)


FORCED = [pick(l, n) for l, n in WANT]
sg.assign_archetypes = lambda slides, seed=0: FORCED  # monkeypatch


async def main():
    preflight()
    run_dir = WORKSPACE / f"run-showcase-{int(time.time() * 1000)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[showcase] run dir: {run_dir}")
    print("[showcase] forcing archetypes:")
    for i, a in enumerate(FORCED, 1):
        print(f"   slide {i}: {a[0]}")

    config = {"tone": "calm, premium, modern", "palette": "auto",
              "fontFamily": "auto", "audience": "Consumers", "pageNumbers": True}
    deck, stats = await sg.generate_deck_per_slide(OUTLINE, config, run_dir=run_dir)
    print(f"[showcase] cost=${stats.get('cost_usd')}  slides={stats.get('slides')}")

    merged = run_dir / "merged_deck.json"
    r = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                       capture_output=True, text=True)
    print(f"[showcase] validation: {'PASS' if r.returncode == 0 else 'FAIL'}")
    subprocess.run([sys.executable, "scripts/render_html_preview.py", str(merged)])
    print(f"[showcase] DONE -> {run_dir}")


if __name__ == "__main__":
    asyncio.run(main())
