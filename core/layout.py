"""
core/layout.py — deterministic layout normalization.

AI decides design INTENT; this module guarantees pixel-level EXECUTION. It runs
AFTER the LLM emits a slide spec and BEFORE expansion/validation, making the
SMALLEST corrections needed for clean geometry:

    snap   — quantise sub-grid drift to a baseline grid (design tokens)
    align  — lock edges / sizes that were clearly meant to match
    space  — even out inconsistent gaps in a row/column of siblings
    overlap— separate elements that collide unintentionally
    safe   — keep text inside the safe zone and content inside the canvas

It is deliberately CONSERVATIVE. Every correction is bounded by a tight
tolerance, so intentional composition is preserved: layered text on panels,
badges on cards, ghost numerals, offset panels, and deliberate full-bleed
imagery are all left alone. Backdrops (motifs, ``is_background`` / full-bleed
images) and large intentionally-bleeding elements are treated as fixed anchors
and are never moved or resized. The user should barely notice normalization ran.

It never redesigns a slide: it does not add/remove/reorder elements, change the
archetype, or infer new layouts — it only refines the geometry the model chose.

Public API
----------
    spec, report = normalize_layout(spec)   # corrects spec in place, returns it
    report.summary()                        # human-readable list of corrections
    report.unresolved                       # problems geometry alone can't fix
                                            # (caller may escalate to visual QA)

Each stage below is a pure function over the element list and the set of movable
indices, so it can be unit-tested in isolation (see scripts/test_layout.py).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Design tokens — the single source of truth for the geometry system.
# ---------------------------------------------------------------------------
CANVAS_W = 1280
CANVAS_H = 720
SAFE = 48                 # hard safe-zone margin for text (matches validate.py)
BASE = 8                  # baseline grid unit everything snaps toward

# Tolerances: a correction only fires when the element is ALREADY within this
# distance of "correct" — so we tidy drift without relocating a composition.
SNAP_TOL = 5              # snap a coordinate to the grid only within this many px
ALIGN_TOL = 14            # edges within this are treated as intended-aligned
SIZE_TOL = 16             # sizes within this are treated as intended-equal
SPACING_TOL = 6           # gaps differing by more than this are "inconsistent"
MIN_OVERLAP = 6           # ignore sub-this overlaps (touching / hairline kiss)
CONTAIN_FRAC = 0.88       # smaller box this-much inside larger => intentional nest
MAX_MOVE = 160            # never shove an element further than this to de-overlap
BACKDROP_COVERAGE = 0.62  # >= this fraction of canvas + edge touch => backdrop
BLEED_MIN_AREA = 0.10     # a bleeding element this big is intentional, not a slip
PANEL_MIN_AREA = 0.05     # a filled shape >= this fraction of canvas is a card /
                          # background panel that content may legitimately sit on;
                          # anything smaller is a badge/bar/accent that must NOT
                          # land on top of a text or icon block

_MEDIA_KINDS = {"image", "chart", "table"}


def _round(v):
    return int(round(v))


def _snap_val(v):
    """Nearest grid multiple if within SNAP_TOL, else v unchanged."""
    n = round(v / BASE) * BASE
    return n if abs(n - v) <= SNAP_TOL else v


# ---------------------------------------------------------------------------
# Geometry accessor — one uniform (x, y, w, h) view over every element kind.
# ---------------------------------------------------------------------------
def _geom(el):
    """Return (x, y, w, h) as floats, or None if the element isn't a box we can
    normalise (no position, or a full-bleed motif with no explicit geometry)."""
    try:
        if "x" not in el or "y" not in el:
            return None
        x = float(el["x"]); y = float(el["y"])
        if el.get("kind") == "icon":
            s = float(el.get("size", 64))
            return x, y, s, s
        if "width" not in el or "height" not in el:
            return None
        return x, y, float(el["width"]), float(el["height"])
    except (TypeError, ValueError):
        return None


def _set_geom(el, x, y, w, h):
    el["x"] = _round(x)
    el["y"] = _round(y)
    if el.get("kind") == "icon":
        el["size"] = _round((w + h) / 2.0)
    else:
        el["width"] = _round(w)
        el["height"] = _round(h)


# ---------------------------------------------------------------------------
# Classification — which elements are fixed anchors vs. normalisable content.
# ---------------------------------------------------------------------------
def _is_backdrop(el, g):
    """Full-bleed background art: motif, is_background image, or anything that
    blankets most of the canvas from an edge. Never touched."""
    if el.get("kind") == "motif":
        return True
    if el.get("kind") == "image" and el.get("is_background"):
        return True
    x, y, w, h = g
    coverage = (w * h) / (CANVAS_W * CANVAS_H)
    touches = x <= 2 or y <= 2 or x + w >= CANVAS_W - 2 or y + h >= CANVAS_H - 2
    return coverage >= BACKDROP_COVERAGE and touches


def _is_bleed(el, g):
    """A large non-text element that intentionally runs off a canvas edge — a
    common premium technique. Preserved exactly (treated as a fixed anchor)."""
    if el.get("kind") == "text":
        return False
    x, y, w, h = g
    off = x < -1 or y < -1 or x + w > CANVAS_W + 1 or y + h > CANVAS_H + 1
    big = (w * h) / (CANVAS_W * CANVAS_H) >= BLEED_MIN_AREA
    return off and big


def _priority(el, g):
    """Higher = more anchored (moved last / least). Used for overlap resolution:
    when two elements collide, the LOWER-priority one yields."""
    kind = el.get("kind")
    if el.get("opacity", 1) < 0.35:
        return 0                                   # ghost / watermark: decorative
    if kind == "image":
        area = (g[2] * g[3]) / (CANVAS_W * CANVAS_H)
        return 5 if area >= 0.18 else 4            # hero image outranks body text
    if kind in _MEDIA_KINDS:
        return 4
    if kind == "text":
        return 3
    if kind == "shape":
        return 2
    return 1                                        # icon & everything else


def _movable_indices(elements):
    """Indices of elements this layer may adjust (everything except backdrops
    and intentional bleed anchors)."""
    out = []
    for i, el in enumerate(elements):
        g = _geom(el)
        if g is None:
            continue
        if _is_backdrop(el, g) or _is_bleed(el, g):
            continue
        out.append(i)
    return out


# ---------------------------------------------------------------------------
# Report — records every correction so the pipeline can log/escalate.
# ---------------------------------------------------------------------------
class LayoutReport:
    def __init__(self):
        self.corrections = []   # list of (stage, index, detail)
        self.unresolved = []    # list of (index_a, index_b, detail)

    def add(self, stage, index, detail):
        self.corrections.append((stage, index, detail))

    def flag(self, a, b, detail):
        self.unresolved.append((a, b, detail))

    def __len__(self):
        return len(self.corrections)

    def summary(self):
        lines = [f"{s}: el#{i} {d}" for (s, i, d) in self.corrections]
        lines += [f"UNRESOLVED: el#{a}+el#{b} {d}" for (a, b, d) in self.unresolved]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Shared helper — greedy 1-D clustering of near-equal values.
# ---------------------------------------------------------------------------
def _cluster(pairs, tol):
    """pairs: list of (index, value). Returns list of clusters (each a list of
    (index, value)) where every member is within `tol` of the cluster's spread."""
    pairs = sorted(pairs, key=lambda t: t[1])
    clusters, cur = [], []
    for idx, val in pairs:
        if cur and (val - cur[0][1] > tol or val - cur[-1][1] > tol):
            clusters.append(cur)
            cur = []
        cur.append((idx, val))
    if cur:
        clusters.append(cur)
    return clusters


# ===========================================================================
# STAGE 1 — SNAP : quantise drift to the baseline grid (design tokens).
# ===========================================================================
def snap_to_grid(elements, movable, report):
    for i in movable:
        g = _geom(elements[i])
        if g is None:
            continue
        x, y, w, h = g
        nx, ny, nw, nh = _snap_val(x), _snap_val(y), _snap_val(w), _snap_val(h)
        if (nx, ny, nw, nh) != (x, y, w, h):
            _set_geom(elements[i], nx, ny, max(1, nw), max(1, nh))
            report.add("snap", i, f"->({_round(nx)},{_round(ny)},"
                                  f"{_round(nw)},{_round(nh)})")


# ===========================================================================
# STAGE 2 — ALIGN : lock edges & sizes that were clearly meant to match.
# ===========================================================================
def align_edges(elements, movable, report):
    """Snap near-aligned edges to a shared line (first-wins per axis so an
    element is never tugged twice horizontally or twice vertically), then
    equalise the size of repeated siblings sharing a row/column."""
    def edge_val(g, key):
        x, y, w, h = g
        return {"left": x, "right": x + w, "cx": x + w / 2,
                "top": y, "bottom": y + h, "cy": y + h / 2}[key]

    def apply_edge(i, key, rep):
        g = _geom(elements[i])
        x, y, w, h = g
        if key == "left":     x = rep
        elif key == "right":  x = rep - w
        elif key == "cx":     x = rep - w / 2
        elif key == "top":    y = rep
        elif key == "bottom": y = rep - h
        elif key == "cy":     y = rep - h / 2
        if (x, y) != (g[0], g[1]):
            _set_geom(elements[i], x, y, w, h)
            report.add("align", i, f"{key}->{_round(rep)}")

    locked = {"x": set(), "y": set()}
    for key in ("left", "right", "cx", "top", "bottom", "cy"):
        axis = "x" if key in ("left", "right", "cx") else "y"
        pairs = [(i, edge_val(_geom(elements[i]), key)) for i in movable]
        for cl in _cluster(pairs, ALIGN_TOL):
            members = [i for (i, _) in cl if i not in locked[axis]]
            if len(members) < 2:
                continue
            rep = _snap_val(round(sum(edge_val(_geom(elements[i]), key)
                                      for i in members) / len(members)))
            for i in members:
                apply_edge(i, key, rep)
                locked[axis].add(i)

    _equalize_siblings(elements, movable, report)


def _equalize_siblings(elements, movable, report):
    """Repeated same-kind elements that share a row (top edge) get equal height
    (and equal width when already close); those sharing a column (left edge) get
    equal width. Position is preserved — only size changes."""
    def groups_by(edge_key):
        pairs = [(i, _geom(elements[i])) for i in movable]
        buckets = {}
        for i, g in pairs:
            val = g[1] if edge_key == "top" else g[0]
            buckets.setdefault(elements[i].get("kind"), []).append((i, val))
        out = []
        for kind, items in buckets.items():
            for cl in _cluster(items, ALIGN_TOL):
                if len(cl) >= 2:
                    out.append([i for (i, _) in cl])
        return out

    def equalize(group, dim):  # dim: 'w' or 'h'
        vals = [(_geom(elements[i])[2] if dim == "w" else _geom(elements[i])[3])
                for i in group]
        if max(vals) - min(vals) > SIZE_TOL:
            return
        med = _snap_val(round(sorted(vals)[len(vals) // 2]))
        for i in group:
            x, y, w, h = _geom(elements[i])
            nw, nh = (med, h) if dim == "w" else (w, med)
            if (nw, nh) != (w, h):
                _set_geom(elements[i], x, y, nw, nh)
                report.add("equalize", i, f"{dim}->{med}")

    for group in groups_by("top"):        # a row -> equal height (+ width if near)
        equalize(group, "h")
        equalize(group, "w")
    for group in groups_by("left"):       # a column -> equal width
        equalize(group, "w")


# ===========================================================================
# STAGE 3 — SPACING : even out inconsistent gaps in a row/column of siblings.
# ===========================================================================
def normalize_spacing(elements, movable, report):
    """A row/column of >=3 same-kind siblings with uneven gaps is redistributed
    to a single uniform gap while KEEPING the outer edges (overall span) fixed —
    so the composition's footprint and centre never move."""
    def run(axis):  # axis 'x' (rows share top) or 'y' (columns share left)
        share_key = "top" if axis == "x" else "left"
        pos_i, size_i = (0, 2) if axis == "x" else (1, 3)
        pairs = {}
        for i in movable:
            g = _geom(elements[i])
            val = g[1] if share_key == "top" else g[0]
            pairs.setdefault(elements[i].get("kind"), []).append((i, val))
        for kind, items in pairs.items():
            for cl in _cluster(items, ALIGN_TOL):
                ids = [i for (i, _) in cl]
                if len(ids) < 3:
                    continue
                ids.sort(key=lambda i: _geom(elements[i])[pos_i])
                gs = [_geom(elements[i]) for i in ids]
                gaps = [gs[k + 1][pos_i] - (gs[k][pos_i] + gs[k][size_i])
                        for k in range(len(gs) - 1)]
                if min(gaps) < 0:                       # overlapping -> not spacing
                    continue
                if max(gaps) - min(gaps) <= SPACING_TOL:  # already even
                    continue
                span = (gs[-1][pos_i] + gs[-1][size_i]) - gs[0][pos_i]
                total = sum(g[size_i] for g in gs)
                gap = (span - total) / (len(gs) - 1)
                if gap < 0:
                    continue
                cursor = gs[0][pos_i]
                for k, i in enumerate(ids):
                    x, y, w, h = _geom(elements[i])
                    npos = cursor
                    if axis == "x" and abs(npos - x) > 0.5:
                        _set_geom(elements[i], npos, y, w, h)
                        report.add("spacing", i, f"x->{_round(npos)}")
                    elif axis == "y" and abs(npos - y) > 0.5:
                        _set_geom(elements[i], x, npos, w, h)
                        report.add("spacing", i, f"y->{_round(npos)}")
                    cursor += (w if axis == "x" else h) + gap
    run("x")
    run("y")


# ===========================================================================
# STAGE 4 — OVERLAP : separate elements that collide unintentionally.
# ===========================================================================
def _intersection(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    return ox, oy


def _contains(outer, inner):
    ox, oy = _intersection(outer, inner)
    if ox <= 0 or oy <= 0:
        return False
    inner_area = inner[2] * inner[3]
    return inner_area > 0 and (ox * oy) / inner_area >= CONTAIN_FRAC


def _is_frame(el):
    return el.get("kind") == "shape" and \
        str(el.get("fill", "")).lower() in ("transparent", "none", "")


def _is_panel(el, g):
    """A large filled shape acting as a background card/panel. Content (text,
    icons) placed on top of it is intentional composition, not a collision."""
    if el.get("kind") != "shape" or _is_frame(el):
        return False
    return (g[2] * g[3]) / (CANVAS_W * CANVAS_H) >= PANEL_MIN_AREA


def _layering_ok(a, b, ga, gb):
    """True when the overlap is intentional composition, not a collision."""
    if a.get("opacity", 1) < 0.5 or b.get("opacity", 1) < 0.5:
        return True                                   # ghost / overlay layering
    ka, kb = a.get("kind"), b.get("kind")
    media = {ka, kb} & _MEDIA_KINDS
    if media and (ka in _MEDIA_KINDS) != (kb in _MEDIA_KINDS):
        return True                                   # content over a photo/chart
    if _is_frame(a) or _is_frame(b):
        return True                                   # outline frame around things
    # Content (text/icon) over a shape is intentional ONLY when the shape is a
    # genuine card/panel, or the content is (near-)fully nested inside it — a
    # label within a bar, an icon centred on a badge. A small shape merely
    # crossing a text/icon block (accent bar over a heading, badge dropped on a
    # paragraph) is a real collision and must be separated.
    if "shape" in (ka, kb) and ({"text", "icon"} & {ka, kb}):
        shape_el, shape_g = (a, ga) if ka == "shape" else (b, gb)
        other_g = gb if ka == "shape" else ga
        if _is_panel(shape_el, shape_g):
            return True                               # content on a card/panel
        if _contains(shape_g, other_g):
            return True                               # content nested within shape
        return False                                  # small shape crossing content
    if _contains(ga, gb) or _contains(gb, ga):
        return True                                   # nested (label in panel)
    return False


def resolve_overlaps(elements, movable, report):
    """Nudge the lower-priority element out of an unintended collision by the
    smallest move along the shallower overlap axis. Bounded and non-cascading:
    a few passes, capped displacement, and anything still stuck is flagged for
    visual QA rather than shoved around."""
    for _ in range(3):
        changed = False
        pairs = []
        for a_pos in range(len(movable)):
            for b_pos in range(a_pos + 1, len(movable)):
                i, j = movable[a_pos], movable[b_pos]
                ga, gb = _geom(elements[i]), _geom(elements[j])
                ox, oy = _intersection(ga, gb)
                if ox > MIN_OVERLAP and oy > MIN_OVERLAP and \
                        not _layering_ok(elements[i], elements[j], ga, gb):
                    pairs.append((ox * oy, i, j))
        pairs.sort(reverse=True)
        for _area, i, j in pairs:
            ga, gb = _geom(elements[i]), _geom(elements[j])
            ox, oy = _intersection(ga, gb)
            if ox <= MIN_OVERLAP or oy <= MIN_OVERLAP:
                continue                              # already separated this pass
            # lower priority yields; on a tie the earlier (lower z-order) element
            # moves, keeping the later/topmost element where the model placed it
            pi, pj = _priority(elements[i], ga), _priority(elements[j], gb)
            mover, anchor = (i, j) if pi <= pj else (j, i)
            gm, gan = _geom(elements[mover]), _geom(elements[anchor])
            mx, my, mw, mh = gm
            if ox <= oy:                              # push horizontally
                delta = ox + BASE
                if (mx + mw / 2) < (gan[0] + gan[2] / 2):
                    delta = -delta
                nx = mx + delta
            else:                                     # push vertically
                delta = oy + BASE
                if (my + mh / 2) < (gan[1] + gan[3] / 2):
                    delta = -delta
                my_new = my + delta
                nx = None
            if ox <= oy:
                if abs(nx - mx) > MAX_MOVE:
                    report.flag(i, j, "overlap exceeds max move")
                    continue
                _set_geom(elements[mover], nx, my, mw, mh)
            else:
                if abs(my_new - my) > MAX_MOVE:
                    report.flag(i, j, "overlap exceeds max move")
                    continue
                _set_geom(elements[mover], mx, my_new, mw, mh)
            report.add("overlap", mover, f"moved to clear el#{anchor}")
            changed = True
        if not changed:
            break


# ===========================================================================
# STAGE 5 — SAFE ZONE : final guarantee. Text inside the 48px margin, other
# content inside the canvas. (Runs LAST so earlier moves can't reintroduce a
# violation.)
# ===========================================================================
def enforce_safe_zone(elements, movable, report):
    for i in movable:
        el = elements[i]
        g = _geom(el)
        x, y, w, h = g
        if el.get("kind") == "text":
            lo_x, lo_y = SAFE, SAFE
            hi_x, hi_y = CANVAS_W - SAFE, CANVAS_H - SAFE
            if w > hi_x - lo_x:
                w = hi_x - lo_x                       # too wide -> let text wrap
            if h > hi_y - lo_y:
                h = hi_y - lo_y
            x = min(max(x, lo_x), hi_x - w)
            y = min(max(y, lo_y), hi_y - h)
        else:                                          # keep content on-canvas
            if w <= CANVAS_W:
                x = min(max(x, 0), CANVAS_W - w)
            if h <= CANVAS_H:
                y = min(max(y, 0), CANVAS_H - h)
        if (x, y, w, h) != g:
            _set_geom(el, x, y, w, h)
            report.add("safe", i, f"clamped to ({_round(x)},{_round(y)},"
                                  f"{_round(w)},{_round(h)})")


# ===========================================================================
# ORCHESTRATOR
# ===========================================================================
def normalize_layout(spec, *, report=None):
    """Run all five stages over one slide spec, mutating element geometry in
    place. Returns (spec, LayoutReport). Safe zone runs last so it can't be
    undone by an earlier stage."""
    report = report or LayoutReport()
    if not isinstance(spec, dict):
        return spec, report
    elements = spec.get("elements")
    if not isinstance(elements, list) or len(elements) < 1:
        return spec, report

    movable = _movable_indices(elements)
    if not movable:
        return spec, report

    snap_to_grid(elements, movable, report)
    align_edges(elements, movable, report)
    normalize_spacing(elements, movable, report)
    resolve_overlaps(elements, movable, report)
    enforce_safe_zone(elements, movable, report)     # final guarantee
    return spec, report
