"""
Visual QA loop — screenshot rendered slides and judge them with a vision model.

Pipeline:
  merged_deck.json -> preview.html (scripts/render_html_preview.py, editor-
  faithful) -> headless Chromium screenshot per slide (Playwright) -> one
  parallel vision call per slide returning a structured review (forced tool)
  -> qa_report.json.

Used standalone:
    python core/visual_qa.py workspace/<run>/merged_deck.json

or from slidegen (SLIDEGEN_VISUAL_QA=1) to regenerate failing slides with the
judge's findings as feedback.

Judge model: env ANTHROPIC_QA_MODEL (default claude-sonnet-4-6 — vision
scoring doesn't need the design-generation model).
"""

import asyncio
import base64
import importlib.util
import json
import os
import sys
from pathlib import Path

import anthropic

_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QA_MODEL = "claude-sonnet-4-6"
PASS_SCORE = 7          # pass = score >= PASS_SCORE and no high-severity problems
JUDGE_MAX_TOKENS = 1500


# ---------------------------------------------------------------------------
# Step 1 — render: merged_deck.json -> preview.html (reuse the preview script)
# ---------------------------------------------------------------------------
def render_preview(merged_json: Path) -> Path:
    spec = importlib.util.spec_from_file_location(
        "render_html_preview", _ROOT / "scripts" / "render_html_preview.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main(str(merged_json))
    return merged_json.parent / "preview.html"


# ---------------------------------------------------------------------------
# Step 2 — screenshot every .slide div at native 1280x720
# ---------------------------------------------------------------------------
async def screenshot_slides(preview_html: Path, out_dir: Path,
                            only_slides: set[int] | None = None) -> dict[int, Path]:
    from playwright.async_api import async_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    shots: dict[int, Path] = {}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        # viewport >= 1328 wide so the preview's fit() keeps scale = 1
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(preview_html.resolve().as_uri())
        try:
            await page.wait_for_load_state("networkidle", timeout=25_000)
        except Exception:
            pass  # remote images may dribble in; screenshot what we have
        # ECharts is inlined into the preview (no CDN), so paint is local and
        # fast — but give the layout+canvas a beat to settle before shooting.
        await page.wait_for_timeout(1200)  # echarts paint (animation is off)

        slides = await page.query_selector_all(".slide")
        for i, el in enumerate(slides, start=1):
            if only_slides and i not in only_slides:
                continue
            await el.scroll_into_view_if_needed()
            path = out_dir / f"slide-{i}.png"
            await el.screenshot(path=str(path))
            shots[i] = path
        await browser.close()
    return shots


# ---------------------------------------------------------------------------
# Step 3 — vision judge, one parallel call per slide
# ---------------------------------------------------------------------------
REVIEW_TOOL = {
    "name": "emit_review",
    "description": "Emit the structured visual review for one rendered slide.",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "integer", "minimum": 1, "maximum": 10,
                "description": "10 = flawless agency-grade slide, 7 = acceptable, "
                               "<=6 = needs regeneration",
            },
            "problems": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": [
                            "overlap", "contrast", "crowding", "cut_off",
                            "palette_violation", "misalignment",
                            "broken_image", "other"]},
                        "severity": {"type": "string",
                                     "enum": ["low", "medium", "high"]},
                        "where": {"type": "string",
                                  "description": "what + where on the slide"},
                        "fix": {"type": "string",
                                "description": "concrete instruction for the "
                                               "designer regenerating the slide"},
                    },
                    "required": ["type", "severity", "where", "fix"],
                },
            },
        },
        "required": ["score", "problems"],
    },
}

_JUDGE_SYSTEM = """\
You are a ruthless visual QA reviewer for AI-generated presentation slides.
You are shown a 1280x720 screenshot of ONE rendered slide plus the content it
was meant to convey and the art director's plan for it. Judge ONLY what is
visible in the image. Call emit_review exactly once.

DEFECTS TO HUNT (in priority order):
1. overlap — text colliding with other text, or text sitting on decorative
   elements/images in a way that hurts readability.
2. contrast — text or icons too close in color to their background; text on a
   photo without a sufficient overlay/panel behind it.
3. cut_off — text clipped by the slide edge or visibly truncated mid-word;
   labels wrapping awkwardly into 3+ lines.
4. crowding — elements touching with no breathing room, margins ignored,
   content pressed against the slide edge.
5. broken_image — missing/failed image (browser broken-image icon or empty
   frame where the plan calls for a photo).
6. palette_violation — colors that clash with the slide's evident palette.
7. misalignment — sibling cards/columns/rows with inconsistent edges, sizes,
   or baselines for no deliberate reason.

NOT DEFECTS (the style is intentional — do not penalize):
- Images or color shapes bleeding off the canvas edge (only TEXT must stay in).
- Asymmetric layouts, oversized stat numbers, dramatic dark palettes.
- A faint oversized background glyph at very low opacity in empty canvas.
- Stock photos that are generic but on-topic.

SCORING: 10 = could ship from a design agency untouched. 8-9 = minor nits
only. 7 = acceptable, no medium/high defects. 5-6 = one or more clear defects
a manager would notice. <=4 = obviously broken (overlapping/clipped text,
broken image, unreadable contrast).

Be precise in "where" (e.g. "the '96%' stat label, bottom-left card") and
actionable in "fix" (e.g. "shorten the label to 2 lines and move the card up
20px"). Report at most the 5 worst problems.
"""


def _judge_user_content(png_path: Path, slide_number: int, total: int,
                        outline_entry: dict | None, plan_text: str | None) -> list:
    b64 = base64.standard_b64encode(png_path.read_bytes()).decode()
    context = f"Slide {slide_number} of {total}.\n"
    if outline_entry:
        context += f"\nINTENDED CONTENT (outline entry):\n{json.dumps(outline_entry, indent=2)}\n"
    if plan_text:
        context += f"\nART DIRECTOR PLAN (the intent — deviations from it are fine unless they look bad):\n{plan_text}\n"
    context += "\nReview the screenshot and call emit_review."
    return [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                     "data": b64}},
        {"type": "text", "text": context},
    ]


async def _judge_one(client, model, png_path: Path, slide_number: int, total: int,
                     outline_entry: dict | None, plan_text: str | None,
                     usage_acc: list) -> dict:
    resp = await client.messages.create(
        model=model,
        max_tokens=JUDGE_MAX_TOKENS,
        system=_JUDGE_SYSTEM,
        tools=[REVIEW_TOOL],
        tool_choice={"type": "tool", "name": "emit_review"},
        messages=[{"role": "user",
                   "content": _judge_user_content(png_path, slide_number, total,
                                                  outline_entry, plan_text)}],
    )
    usage_acc.append(resp.usage)
    review = next(b.input for b in resp.content if b.type == "tool_use")
    has_high = any(p.get("severity") == "high" for p in review.get("problems", []))
    review["slide_number"] = slide_number
    review["pass"] = review["score"] >= PASS_SCORE and not has_high
    return review


def format_feedback(review: dict) -> str:
    """Turn a failing review into regeneration feedback for the slide executor."""
    lines = [f"A visual QA review of your rendered slide scored it "
             f"{review['score']}/10. Keep the same composition archetype and "
             f"palette, but fix every problem below:"]
    for p in review.get("problems", []):
        lines.append(f"- [{p['severity']} {p['type']}] {p['where']} -> FIX: {p['fix']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
async def run_visual_qa(run_dir: Path, outline: dict | None = None,
                        plans: dict | None = None,
                        only_slides: set[int] | None = None) -> dict:
    """
    Render + screenshot + judge every slide of run_dir/merged_deck.json.
    Returns {"slides": [review...], "passed": bool, "tokens": {...}}.
    Writes qa_report.json and qa/slide-N.png into run_dir.
    """
    run_dir = Path(run_dir)
    merged = run_dir / "merged_deck.json"
    if not merged.exists():
        raise FileNotFoundError(merged)

    if outline is None and (run_dir / "outline.json").exists():
        outline = json.loads((run_dir / "outline.json").read_text(encoding="utf-8"))
    if plans is None and (run_dir / "design_plan.json").exists():
        raw = json.loads((run_dir / "design_plan.json").read_text(encoding="utf-8"))
        plans = {int(k): v for k, v in raw.items()}
    plans = plans or {}
    entries = {i: e for i, e in
               enumerate((outline or {}).get("slides", []), start=1)}

    preview = render_preview(merged)
    shots = await screenshot_slides(preview, run_dir / "qa", only_slides)
    total = len(json.loads(merged.read_text(encoding="utf-8"))
                ["files"]["content"]["slides"])

    model = os.environ.get("ANTHROPIC_QA_MODEL", DEFAULT_QA_MODEL)
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    usage_acc: list = []
    reviews = await asyncio.gather(*[
        _judge_one(client, model, png, n, total, entries.get(n), plans.get(n),
                   usage_acc)
        for n, png in sorted(shots.items())
    ])

    report = {
        "model": model,
        "slides": sorted(reviews, key=lambda r: r["slide_number"]),
        "passed": all(r["pass"] for r in reviews),
        "tokens": {
            "input": sum(u.input_tokens for u in usage_acc),
            "output": sum(u.output_tokens for u in usage_acc),
        },
    }
    out = run_dir / "qa_report.json"
    existing = json.loads(out.read_text(encoding="utf-8")) if (only_slides and out.exists()) else None
    if existing:  # partial re-judge: merge over the previous report
        by_n = {r["slide_number"]: r for r in existing["slides"]}
        for r in report["slides"]:
            by_n[r["slide_number"]] = r
        report["slides"] = [by_n[k] for k in sorted(by_n)]
        report["passed"] = all(r["pass"] for r in report["slides"])
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def print_report(report: dict) -> None:
    print(f"\n  visual QA ({report['model']}) — "
          f"{'PASS' if report['passed'] else 'FAIL'}")
    for r in report["slides"]:
        flag = "ok " if r["pass"] else "FIX"
        print(f"    [{flag}] slide {r['slide_number']}: {r['score']}/10")
        for p in r.get("problems", []):
            print(f"          - {p['severity']:6} {p['type']:18} {p['where']}")
            print(f"            fix: {p['fix']}")


if __name__ == "__main__":
    sys.path.insert(0, str(_ROOT))
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from dotenv import load_dotenv
    load_dotenv()
    if len(sys.argv) < 2:
        print("usage: python core/visual_qa.py workspace/<run>/merged_deck.json")
        sys.exit(2)
    target = Path(sys.argv[1])
    result = asyncio.run(run_visual_qa(target.parent))
    print_report(result)
    print(f"\n  report: {target.parent / 'qa_report.json'}")
