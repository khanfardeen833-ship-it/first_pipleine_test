"""
One-shot premium deck test for the slidegen engine.

Skips Azure enhance + MongoDB: feeds a hand-written outline straight into
generate_deck_per_slide (director mode), validates the merged deck, and
exports deck.pptx — all into workspace/<run_id>/.

Usage:
    python scripts/run_premium_test.py
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import WORKSPACE, VALIDATOR, preflight  # noqa: E402  (loads .env)
from core.slidegen import generate_deck_per_slide        # noqa: E402

OUTLINE = {
    "title": "Skyline Collection",
    "subtitle": "Luxury Real Estate Portfolio — 2026 Investor Briefing",
    "slides": [
        {
            "slide_number": 1,
            "title": "Skyline Collection",
            "subtitle": "Luxury Real Estate Portfolio — 2026 Investor Briefing",
            "layout": "title_only",
            "bullets": [],
            "bg": "dark",
        },
        {
            "slide_number": 2,
            "title": "2025 Portfolio Performance",
            "layout": "bullets",
            "bullets": [
                "$842M assets under management, up 34% year over year",
                "96% occupancy across 28 flagship properties",
                "11.8% average net rental yield, best in segment",
                "4 new markets entered: Dubai, Lisbon, Miami, Singapore",
            ],
            "bg": "light",
        },
        {
            "slide_number": 3,
            "title": "Two Engines of Growth",
            "layout": "two_column",
            "bullets": [
                "Residential: 18 ultra-prime villas and penthouses",
                "Residential: $310M pipeline, 92% pre-sold off-plan",
                "Residential: average resale premium of 27%",
                "Commercial: 10 boutique office and retail assets",
                "Commercial: 8.4-year weighted average lease term",
                "Commercial: 100% green-certified by end of 2026",
            ],
            "bg": "dark",
        },
        {
            "slide_number": 4,
            "title": "Revenue Trajectory",
            "layout": "chart",
            "bullets": [
                "Revenue doubles by 2027 on current acquisition pace",
                "2023: $96M — 2024: $148M — 2025: $214M — 2026E: $305M — 2027E: $428M",
                "Recurring rental income now 61% of total revenue",
            ],
            "bg": "light",
        },
        {
            "slide_number": 5,
            "title": "What Sets Skyline Apart",
            "layout": "three_column",
            "bullets": [
                "Design-led: every property by award-winning architects, 9 international design prizes",
                "Data-driven: proprietary valuation engine screens 12,000 listings per quarter",
                "White-glove: 24/7 concierge asset management, 98 NPS from owners",
            ],
            "bg": "dark",
        },
        {
            "slide_number": 6,
            "title": "The Road to 2028",
            "layout": "timeline",
            "bullets": [
                "2024: Crossed $500M AUM, launched commercial division",
                "2025: Entered 4 global gateway markets",
                "2026: $1B AUM target, first branded residences tower breaks ground",
                "2027: REIT conversion and public listing window",
                "2028: 50 flagship assets across 12 cities",
            ],
            "bg": "light",
        },
        {
            "slide_number": 7,
            "title": "What Our Investors Say",
            "layout": "quote",
            "bullets": [
                "Skyline is the only manager that delivered above-target returns every single year we have been invested.",
                "— Elena Marchetti, CIO, Meridian Family Office",
            ],
            "bg": "dark",
        },
        {
            "slide_number": 8,
            "title": "Build the Skyline With Us",
            "subtitle": "Series C closes Q3 2026 — reserve your allocation",
            "layout": "title_only",
            "bullets": [],
            "bg": "dark",
        },
    ],
}

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
    preflight()
    run_id = f"run-premium-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "outline.json").write_text(json.dumps(OUTLINE, indent=2), encoding="utf-8")

    print(f"[premium-test] run dir: {run_dir}")
    deck, stats = await generate_deck_per_slide(OUTLINE, CONFIG, run_dir=run_dir)
    print(f"[premium-test] stats: {json.dumps(stats, indent=2)}")

    merged = run_dir / "merged_deck.json"
    result = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                            capture_output=True, text=True)
    print(result.stdout)
    print(f"[premium-test] validation: {'PASS' if result.returncode == 0 else 'FAIL'}")

    from core.pptx_exporter import export_slides_to_pptx
    pptx_path = run_dir / "deck.pptx"
    await export_slides_to_pptx(deck, pptx_path)
    print(f"[premium-test] pptx: {pptx_path}  ({pptx_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    asyncio.run(main())
