"""
Standalone unit tests for core/layout.py — no pytest needed:

    python scripts/test_layout.py

Each layout stage is exercised in isolation, then the full normalize_layout()
pipeline, plus the invariants that make normalization safe (idempotence,
anchors preserved, element count unchanged).
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import layout as L  # noqa: E402

_passed = _failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ok  {name}")
    else:
        _failed += 1
        print(f"FAIL  {name}  {detail}")


def geom(el):
    return L._geom(el)


# --------------------------------------------------------------------------
def test_snap():
    els = [{"kind": "shape", "x": 63, "y": 47, "width": 201, "height": 99}]
    L.snap_to_grid(els, [0], L.LayoutReport())
    check("snap: near-grid drift quantised", geom(els[0]) == (64, 48, 200, 96))

    # On an 8px grid every value is <=4px from a line, so snapping fires but the
    # move must always be tiny — that is the "barely noticeable" guarantee.
    els = [{"kind": "shape", "x": 137, "y": 250, "width": 303, "height": 197}]
    before = geom(els[0])
    L.snap_to_grid(els, [0], L.LayoutReport())
    moved = max(abs(a - b) for a, b in zip(geom(els[0]), before))
    check("snap: displacement never exceeds half a grid unit", moved <= L.BASE / 2,
          f"moved {moved}px from {before} to {geom(els[0])}")


def test_align():
    # three "cards" whose left edges drifted by a few px -> should share one x
    els = [
        {"kind": "shape", "x": 100, "y": 120, "width": 200, "height": 150},
        {"kind": "shape", "x": 104, "y": 320, "width": 200, "height": 150},
        {"kind": "shape", "x": 97,  "y": 520, "width": 200, "height": 150},
    ]
    L.align_edges(els, [0, 1, 2], L.LayoutReport())
    xs = {geom(e)[0] for e in els}
    check("align: near left edges collapse to one", len(xs) == 1, f"xs={xs}")

    # widely different left edges must NOT be force-aligned
    els = [
        {"kind": "shape", "x": 100, "y": 120, "width": 200, "height": 150},
        {"kind": "shape", "x": 700, "y": 120, "width": 200, "height": 150},
    ]
    L.align_edges(els, [0, 1], L.LayoutReport())
    check("align: distant edges preserved",
          geom(els[0])[0] == 100 and geom(els[1])[0] == 700)


def test_equalize():
    els = [
        {"kind": "shape", "x": 100, "y": 120, "width": 200, "height": 150},
        {"kind": "shape", "x": 340, "y": 120, "width": 200, "height": 138},
        {"kind": "shape", "x": 580, "y": 120, "width": 200, "height": 144},
    ]
    L.align_edges(els, [0, 1, 2], L.LayoutReport())
    hs = {geom(e)[3] for e in els}
    check("equalize: near-equal row heights unified", len(hs) == 1, f"hs={hs}")


def test_spacing():
    # gaps 31 / 27 / 35 -> uniform, outer edges fixed
    els = [
        {"kind": "shape", "x": 100, "y": 300, "width": 150, "height": 150},
        {"kind": "shape", "x": 281, "y": 300, "width": 150, "height": 150},
        {"kind": "shape", "x": 458, "y": 300, "width": 150, "height": 150},
        {"kind": "shape", "x": 643, "y": 300, "width": 150, "height": 150},
    ]
    left0 = geom(els[0])[0]
    right_last = geom(els[-1])[0] + geom(els[-1])[2]
    L.normalize_spacing(els, [0, 1, 2, 3], L.LayoutReport())
    gs = [geom(e) for e in els]
    gaps = [round(gs[k + 1][0] - (gs[k][0] + gs[k][2])) for k in range(3)]
    check("spacing: gaps evened", max(gaps) - min(gaps) <= 1, f"gaps={gaps}")
    check("spacing: outer span preserved",
          geom(els[0])[0] == left0
          and abs((geom(els[-1])[0] + geom(els[-1])[2]) - right_last) <= 1)


def test_overlap():
    # two opaque text blocks overlapping -> separated
    els = [
        {"kind": "text", "x": 100, "y": 100, "width": 300, "height": 80, "text": "A"},
        {"kind": "text", "x": 260, "y": 130, "width": 300, "height": 80, "text": "B"},
    ]
    rep = L.LayoutReport()
    L.resolve_overlaps(els, [0, 1], rep)
    ox, oy = L._intersection(geom(els[0]), geom(els[1]))
    check("overlap: text/text collision cleared", ox <= L.MIN_OVERLAP or oy <= L.MIN_OVERLAP,
          f"ox={ox} oy={oy}")

    # text over a shape (a card label) is intentional -> untouched
    els = [
        {"kind": "shape", "x": 100, "y": 100, "width": 400, "height": 200, "fill": "#222"},
        {"kind": "text", "x": 130, "y": 150, "width": 300, "height": 80, "text": "label"},
    ]
    before = [geom(e) for e in els]
    L.resolve_overlaps(els, [0, 1], L.LayoutReport())
    check("overlap: text-on-card layering preserved",
          [geom(e) for e in els] == before)


def test_safe_zone():
    els = [{"kind": "text", "x": 20, "y": 10, "width": 400, "height": 80, "text": "T"}]
    L.enforce_safe_zone(els, [0], L.LayoutReport())
    x, y, w, h = geom(els[0])
    check("safe: text pushed inside margin", x >= L.SAFE and y >= L.SAFE)

    els = [{"kind": "text", "x": 1000, "y": 100, "width": 400, "height": 80, "text": "T"}]
    L.enforce_safe_zone(els, [0], L.LayoutReport())
    x, y, w, h = geom(els[0])
    check("safe: overflow pulled back inside right margin",
          x + w <= L.CANVAS_W - L.SAFE + 0.5)


def test_anchors_preserved():
    els = [
        {"kind": "motif", "motif_type": "aurora"},                     # no geometry
        {"kind": "image", "x": 0, "y": 0, "width": 1280, "height": 720,
         "is_background": True},                                       # backdrop
        {"kind": "image", "x": 900, "y": -40, "width": 500, "height": 800},  # bleed
        {"kind": "text", "x": 61, "y": 47, "width": 300, "height": 80, "text": "x"},
    ]
    before = [dict(e) for e in els]
    _, rep = L.normalize_layout({"background": "#000", "elements": els})
    check("anchors: motif untouched", els[0] == before[0])
    check("anchors: is_background image untouched", els[1] == before[1])
    check("anchors: bleeding image untouched", els[2] == before[2])
    check("anchors: normal text WAS adjusted", els[3] != before[3])
    check("anchors: element count unchanged", len(els) == len(before))


def test_idempotent():
    spec = {"background": "#000", "elements": [
        {"kind": "shape", "x": 63, "y": 47, "width": 201, "height": 99, "fill": "#111"},
        {"kind": "shape", "x": 341, "y": 47, "width": 199, "height": 101, "fill": "#111"},
        {"kind": "text", "x": 66, "y": 300, "width": 400, "height": 80, "text": "hi"},
    ]}
    L.normalize_layout(spec)
    snapshot = [geom(e) for e in spec["elements"]]
    _, rep2 = L.normalize_layout(spec)   # second run should be a no-op
    check("idempotent: second pass makes no changes", len(rep2) == 0,
          f"second pass did {len(rep2)}: {rep2.summary()}")
    check("idempotent: geometry stable",
          [geom(e) for e in spec["elements"]] == snapshot)


def main():
    for t in (test_snap, test_align, test_equalize, test_spacing,
              test_overlap, test_safe_zone, test_anchors_preserved,
              test_idempotent):
        print(f"\n[{t.__name__}]")
        t()
    print(f"\n{_passed} passed, {_failed} failed")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
