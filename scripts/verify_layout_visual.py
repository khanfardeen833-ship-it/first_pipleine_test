"""
Visual A/B verification for core/layout.py.

Builds a deck of deliberately MESSY slides (each stressing one normalization
stage, plus one slide of INTENTIONAL layering that must be preserved), then
renders + screenshots the deck twice — once WITHOUT normalization, once WITH —
using the project's own editor-faithful preview + Playwright screenshotter.

Output (workspace/_layout_verify/):
    before/slide-N.png   after/slide-N.png     side-by-side to eyeball
    report.txt           per-element geometry diff and stage tally

    python scripts/verify_layout_visual.py
"""
import asyncio
import copy
import json
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from core.slidegen import expand_slide_spec           # noqa: E402
from core.merger import merge_presentations           # noqa: E402
from core.layout import normalize_layout, _geom       # noqa: E402
from core.visual_qa import render_preview, screenshot_slides  # noqa: E402

CARD = "#12294a"
DARK = "#0B1F3A"

# --------------------------------------------------------------------------
# Messy slides — each name documents the flaw(s) planted.
# --------------------------------------------------------------------------
def messy_slides():
    return [
        # 1) drift + uneven card gaps + unequal card heights (snap/align/space)
        {"name": "drift+gaps+sizes", "background": DARK, "elements": [
            {"kind": "text", "x": 47, "y": 46, "width": 300, "height": 34,
             "type": "caption", "text": "PLATFORM"},
            {"kind": "text", "x": 45, "y": 92, "width": 760, "height": 92,
             "type": "title", "text": "Three Core Pillars"},
            {"kind": "shape", "shape_type": "rectangle", "x": 63, "y": 301, "width": 321, "height": 260, "fill": CARD},
            {"kind": "shape", "shape_type": "rectangle", "x": 411, "y": 299, "width": 318, "height": 250, "fill": CARD},
            {"kind": "shape", "shape_type": "rectangle", "x": 741, "y": 302, "width": 322, "height": 258, "fill": CARD},
            {"kind": "text", "x": 83, "y": 331, "width": 260, "height": 46, "text": "Speed"},
            {"kind": "text", "x": 431, "y": 329, "width": 260, "height": 46, "text": "Scale"},
            {"kind": "text", "x": 761, "y": 330, "width": 260, "height": 46, "text": "Trust"},
        ]},
        # 2) safe-zone violations: title off top-left, body overflowing right edge
        {"name": "safe-zone", "background": DARK, "elements": [
            {"kind": "text", "x": 12, "y": 8, "width": 700, "height": 90,
             "type": "title", "text": "Edge Bleeding Title"},
            {"kind": "text", "x": 980, "y": 300, "width": 420, "height": 220,
             "type": "paragraph",
             "text": "This paragraph starts far right and overflows the canvas edge well past the safe margin so it would be clipped."},
        ]},
        # 3) two opaque text blocks colliding (overlap must be resolved)
        {"name": "text-collision", "background": DARK, "elements": [
            {"kind": "text", "x": 120, "y": 200, "width": 360, "height": 120,
             "type": "heading", "text": "Overlapping Heading One"},
            {"kind": "text", "x": 300, "y": 250, "width": 360, "height": 120,
             "type": "heading", "text": "Overlapping Heading Two"},
        ]},
        # 4) INTENTIONAL layering — nothing here should move: ghost numeral behind
        #    a card, a text label on the card, an outline frame around it.
        {"name": "intentional-layering", "background": DARK, "elements": [
            {"kind": "text", "x": 90, "y": 180, "width": 260, "height": 300,
             "type": "title", "text": "01", "opacity": 0.08},
            {"kind": "shape", "shape_type": "rectangle", "x": 120, "y": 240, "width": 520, "height": 300, "fill": CARD},
            {"kind": "shape", "shape_type": "rectangle", "x": 120, "y": 240, "width": 520, "height": 300,
             "fill": "transparent", "stroke": "#37E29A", "stroke_width": 2},
            {"kind": "text", "x": 150, "y": 280, "width": 460, "height": 60,
             "type": "heading", "text": "Layered Card Title"},
            {"kind": "text", "x": 150, "y": 360, "width": 460, "height": 120,
             "type": "paragraph", "text": "Caption sitting inside the framed card."},
        ]},
    ]


def build_deck(slides, *, normalize):
    """Expand a list of slide specs into a merged deck dict; optionally run
    normalize_layout first. Returns (deck, total_report_len)."""
    parts, tmp = [], Path(tempfile.mkdtemp(prefix="layout-verify-"))
    fixes = 0
    for i, s in enumerate(slides, start=1):
        spec = {"background": s["background"], "elements": copy.deepcopy(s["elements"])}
        if normalize:
            _, rep = normalize_layout(spec)
            fixes += len(rep)
        part = expand_slide_spec(spec, deck_title="Layout Verify",
                                 slide_number=i, deck_id="verify", timestamp=0)
        p = tmp / f"slide-{i}.json"
        p.write_text(json.dumps(part), encoding="utf-8")
        parts.append(p)
    deck = merge_presentations(parts)
    return deck, fixes


def _positions(deck):
    """slide -> {element_id: (x, y, w, h)} from the changelog (final geometry)."""
    out = {}
    for sid, body in deck["files"]["changelog"]["slides"].items():
        for eid, el in body["elements"].items():
            pos = el.get("position", {})
            out.setdefault(sid, {})[eid] = (
                pos.get("x"), pos.get("y"), el.get("width"), el.get("height"))
    return out


async def main():
    out = _ROOT / "workspace" / "_layout_verify"
    (out / "before").mkdir(parents=True, exist_ok=True)
    (out / "after").mkdir(parents=True, exist_ok=True)
    slides = messy_slides()

    before, _ = build_deck(slides, normalize=False)
    after, fixes = build_deck(slides, normalize=True)

    bjson = out / "before" / "deck.json"
    ajson = out / "after" / "deck.json"
    bjson.write_text(json.dumps(before), encoding="utf-8")
    ajson.write_text(json.dumps(after), encoding="utf-8")

    # render + screenshot both
    for tag, j in (("before", bjson), ("after", ajson)):
        html = render_preview(j)
        shots = await screenshot_slides(html, out / tag)
        print(f"[{tag}] screenshotted {len(shots)} slides -> {out / tag}")

    # geometry diff report
    bpos, apos = _positions(before), _positions(after)
    lines = [f"Layout normalization applied {fixes} correction(s) total.\n"]
    for idx, s in enumerate(slides, start=1):
        sid = f"slide-{idx}"
        lines.append(f"=== slide {idx}: {s['name']} ===")
        b, a = bpos.get(sid, {}), apos.get(sid, {})
        for eid in b:
            if b[eid] != a.get(eid):
                lines.append(f"  {eid}: {b[eid]} -> {a.get(eid)}")
        moved = sum(1 for eid in b if b[eid] != a.get(eid))
        lines.append(f"  ({moved}/{len(b)} elements adjusted)\n")
    report = "\n".join(lines)
    (out / "report.txt").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"PNGs: {out/'before'}  and  {out/'after'}")


if __name__ == "__main__":
    asyncio.run(main())
