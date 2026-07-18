"""
Batch evaluation harness — generate N decks across diverse topics with the
visual-QA loop ON, then aggregate every QA problem into one manifest so we can
see which defects recur ACROSS the whole set (not just one deck).

Each deck lands in workspace/eval/<NN-slug>/ (its own merged_deck.json,
deck.pptx, preview.html, qa_report.json, qa/ screenshots). A final re-render +
screenshot pass writes final/slide-N.png reflecting the post-regeneration deck.

Usage:  python scripts/run_eval.py            # all topics, 6 slides each
        python scripts/run_eval.py --slides 6 --limit 20
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["SLIDEGEN_VISUAL_QA"] = "1"  # turn the judge->regenerate loop ON

from core.config import WORKSPACE, VALIDATOR, preflight          # noqa: E402
from core.planner import generate_outline                        # noqa: E402
from core.slidegen import generate_deck_per_slide, warm_static_prefix  # noqa: E402
from core.visual_qa import render_preview, screenshot_slides     # noqa: E402
from core.pptx_exporter import export_slides_to_pptx             # noqa: E402

TOPICS = [
    "Quantum computing for enterprise CIOs",
    "Q3 SaaS revenue and retention review",
    "The Mediterranean diet and longevity",
    "Solo travel through Patagonia",
    "The global rise of specialty matcha",
    "Teaching kids financial literacy",
    "CRISPR gene editing, explained",
    "Series A pitch: an AI logistics startup",
    "An ocean plastic cleanup nonprofit",
    "The evolution of Formula 1 aerodynamics",
    "The 2026 luxury real estate market",
    "Sustainable fashion supply chains",
    "The business of esports",
    "Carbon capture technology overview",
    "Building a personal brand on LinkedIn",
    "The history of jazz in New Orleans",
    "A remote-team productivity playbook",
    "Electric vehicle battery breakthroughs",
    "Mindfulness for busy professionals",
    "The future of space tourism",
]

CONFIG = {
    "density": "Standard", "audience": "Executive Leadership",
    "tone": "confident, premium", "fontFamily": "auto", "fontSize": "Medium",
    "palette": "auto", "imageSource": "pexels", "pageNumbers": True,
}


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


async def run_one(topic: str, idx: int, slides: int) -> dict:
    run_dir = WORKSPACE / "eval" / f"{idx:02d}-{slug(topic)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    rec = {"idx": idx, "topic": topic, "dir": str(run_dir), "slides": slides}
    t0 = time.time()
    try:
        outline, _ = await asyncio.gather(
            generate_outline(topic, slides, run_dir=run_dir),
            warm_static_prefix(),
        )
        deck, stats = await generate_deck_per_slide(outline, CONFIG, run_dir=run_dir)
        rec["stats"] = stats

        merged = run_dir / "merged_deck.json"
        val = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                             capture_output=True, text=True)
        rec["validation_pass"] = val.returncode == 0
        rec["validation_warnings"] = [ln.strip() for ln in val.stdout.splitlines()
                                      if ln.strip().startswith("!")]

        await export_slides_to_pptx(deck, run_dir / "deck.pptx")

        # final re-render + screenshot (reflects post-regeneration deck)
        preview = render_preview(merged)
        await screenshot_slides(preview, run_dir / "final")

        qa_path = run_dir / "qa_report.json"
        if qa_path.exists():
            rec["qa"] = json.loads(qa_path.read_text(encoding="utf-8"))
        rec["ok"] = True
    except Exception as e:
        rec["ok"] = False
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc()
    rec["seconds"] = round(time.time() - t0, 1)
    print(f"[eval] {idx:02d}/{len(TOPICS)} {'OK ' if rec.get('ok') else 'ERR'} "
          f"{topic}  ({rec['seconds']}s)", flush=True)
    return rec


def aggregate(records: list) -> dict:
    prob_by_type = Counter()
    prob_by_type_sev = Counter()
    scores = []
    total_slides = 0
    failing_slides = 0
    regenerated = 0
    examples = {}  # type -> list of (topic, where, fix)
    for r in records:
        qa = r.get("qa") or {}
        for s in qa.get("slides", []):
            total_slides += 1
            scores.append(s.get("score", 0))
            if not s.get("pass", True):
                failing_slides += 1
            for p in s.get("problems", []):
                t = p.get("type", "other")
                prob_by_type[t] += 1
                prob_by_type_sev[f"{t}/{p.get('severity','?')}"] += 1
                examples.setdefault(t, [])
                if len(examples[t]) < 6:
                    examples[t].append({"topic": r["topic"],
                                        "severity": p.get("severity"),
                                        "where": p.get("where"),
                                        "fix": p.get("fix")})
        regenerated += len((r.get("stats") or {}).get("qa", {}).get("regenerated", [])) \
            if isinstance((r.get("stats") or {}).get("qa"), dict) else 0

    return {
        "decks_total": len(records),
        "decks_ok": sum(1 for r in records if r.get("ok")),
        "slides_judged": total_slides,
        "slides_failing": failing_slides,
        "avg_score": round(sum(scores) / len(scores), 2) if scores else None,
        "score_hist": dict(sorted(Counter(scores).items())),
        "problems_by_type": dict(prob_by_type.most_common()),
        "problems_by_type_severity": dict(prob_by_type_sev.most_common()),
        "examples": examples,
    }


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", type=int, default=6)
    ap.add_argument("--limit", type=int, default=len(TOPICS))
    args = ap.parse_args()

    preflight()
    (WORKSPACE / "eval").mkdir(parents=True, exist_ok=True)
    topics = TOPICS[: args.limit]
    print(f"[eval] generating {len(topics)} decks x {args.slides} slides "
          f"with SLIDEGEN_VISUAL_QA=1", flush=True)

    records = []
    for i, topic in enumerate(topics, start=1):
        records.append(await run_one(topic, i, args.slides))
        (WORKSPACE / "eval" / "manifest.json").write_text(
            json.dumps({"records": records}, indent=2), encoding="utf-8")

    summary = aggregate(records)
    out = {"summary": summary, "records": records}
    (WORKSPACE / "eval" / "manifest.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print("\n[eval] ===== AGGREGATE =====")
    print(json.dumps(summary, indent=2))
    print(f"\n[eval] manifest -> {WORKSPACE / 'eval' / 'manifest.json'}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    asyncio.run(main())
