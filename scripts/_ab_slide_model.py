"""
A/B harness: Opus vs Sonnet-5 as the SLIDE model (design-plan + executors),
judge held constant. Answers the only question that matters — can a cheaper,
faster model draw the slides while the QA loop keeps FINAL quality equal?

For each topic it generates the outline ONCE, then draws it twice (Opus,
Sonnet-5) into separate run dirs, and reports three head-to-head columns:
  QUALITY  — avg final per-slide QA score (post-regeneration), + #regens
  COST     — all-in cost_usd/deck (slide model + judge)
  TIME     — wall-clock total_seconds/deck

Decision rule (printed at the end): adopt Sonnet only if its final quality
matches Opus AND net cost + time are lower.

Usage:  python scripts/_ab_slide_model.py --slides 6 "topic one" "topic two" ...
Nothing is committed; runs go to workspace/ab-*.
"""
import sys, os, json, time, argparse, asyncio
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import WORKSPACE, preflight            # noqa: E402 (loads .env)
from core.planner import generate_outline               # noqa: E402
from core.slidegen import generate_deck_per_slide       # noqa: E402

OPUS = "claude-opus-4-8"
SONNET = "claude-sonnet-5"

DEFAULT_TOPICS = [
    "photosynthesis process",
    "quarterly SaaS revenue review",
    "luxury mechanical watch launch",
    "urban transit network redesign",
]
CONFIG = {"density": "Standard", "audience": "Executive Leadership",
          "tone": "confident, premium", "fontFamily": "auto",
          "fontSize": "Medium", "palette": "auto", "imageSource": "pexels",
          "pageNumbers": True}


def quality(stats: dict):
    """avg final per-slide score (regenerated slides use their post-fix score)."""
    vq = stats.get("visual_qa", {}) or {}
    init = {int(k): v for k, v in vq.get("initial_scores", {}).items()}
    fin = {int(k): v for k, v in vq.get("final_scores", {}).items()}
    eff = {n: fin.get(n, init.get(n)) for n in init}
    avg = round(sum(eff.values()) / len(eff), 2) if eff else None
    return avg, len(vq.get("regenerated", []) or []), eff


async def draw(outline, model, run_dir):
    os.environ["SLIDEGEN_SLIDE_MODEL"] = model
    t = time.time()
    _, stats = await generate_deck_per_slide(outline, CONFIG, run_dir=run_dir)
    q, regens, _ = quality(stats)
    return {"model": model, "cost": stats.get("cost_usd"),
            "gen_cost": stats.get("gen_cost_usd"),
            "secs": stats.get("total_seconds") or round(time.time() - t, 1),
            "quality": q, "regens": regens}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*", default=None)
    ap.add_argument("--slides", type=int, default=6)
    args = ap.parse_args()
    topics = args.topics or DEFAULT_TOPICS
    preflight()

    stamp = int(time.time())
    rows = []
    for ti, topic in enumerate(topics, 1):
        print(f"\n########## TOPIC {ti}/{len(topics)}: {topic!r} ##########")
        base = WORKSPACE / f"ab-{stamp}-t{ti}"
        base.mkdir(parents=True, exist_ok=True)
        # outline ONCE — both models draw identical content
        outline = await generate_outline(topic, args.slides, run_dir=base)
        try:
            o = await draw(outline, OPUS, base / "opus")
            s = await draw(outline, SONNET, base / "sonnet")
        except Exception as e:
            print(f"  [ab] topic failed: {type(e).__name__}: {e}")
            continue
        rows.append({"topic": topic, "opus": o, "sonnet": s})
        print(f"  OPUS   q={o['quality']} regens={o['regens']} "
              f"cost=${o['cost']} time={o['secs']}s")
        print(f"  SONNET q={s['quality']} regens={s['regens']} "
              f"cost=${s['cost']} time={s['secs']}s")

    if not rows:
        print("\n[ab] no successful topics — nothing to compare"); return

    def avg(side, key):
        vals = [r[side][key] for r in rows if r[side].get(key) is not None]
        return round(sum(vals) / len(vals), 3) if vals else None

    oq, sq = avg("opus", "quality"), avg("sonnet", "quality")
    oc, sc = avg("opus", "cost"), avg("sonnet", "cost")
    ot, st = avg("opus", "secs"), avg("sonnet", "secs")

    if None in (oq, sq, oc, sc, ot, st):
        print("\n[ab] incomplete metrics (a run missing QA/cost). Raw rows:")
        print(json.dumps(rows, indent=2))
        print(f"  averages: opus q={oq} cost={oc} secs={ot} | "
              f"sonnet q={sq} cost={sc} secs={st}")
        return

    print("\n===================== A/B SUMMARY =====================")
    print(f"  topics compared : {len(rows)}  ({args.slides} slides each)")
    print(f"  {'':14}{'OPUS':>12}{'SONNET-5':>12}{'delta':>12}")
    print(f"  {'quality(avg)':14}{oq:>12}{sq:>12}{round(sq-oq,2):>12}")
    print(f"  {'cost/deck':14}{('$%.4f'%oc):>12}{('$%.4f'%sc):>12}"
          f"{('%.0f%%'%(100*(sc-oc)/oc)):>12}")
    print(f"  {'time/deck(s)':14}{ot:>12}{st:>12}"
          f"{('%.0f%%'%(100*(st-ot)/ot)):>12}")
    print("=======================================================")
    cheaper = sc < oc; faster = st < ot; quality_held = sq >= oq - 0.3
    verdict = ("ADOPT Sonnet-5" if (cheaper and faster and quality_held)
               else "KEEP Opus")
    print(f"  DECISION: {verdict}")
    print(f"    quality held (>= Opus-0.3): {quality_held}  "
          f"(Opus {oq} vs Sonnet {sq})")
    print(f"    cheaper: {cheaper}   faster: {faster}")

    out = WORKSPACE / f"ab-{stamp}-summary.json"
    out.write_text(json.dumps(
        {"rows": rows, "avg": {"opus": {"q": oq, "cost": oc, "secs": ot},
                               "sonnet": {"q": sq, "cost": sc, "secs": st}},
         "verdict": verdict}, indent=2), encoding="utf-8")
    print(f"  saved: {out}")


if __name__ == "__main__":
    asyncio.run(main())
