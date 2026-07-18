"""
Deterministic post-generation geometry cleanup.

The deck format has no parent/child containment or auto-layout: every element
(a panel, each text line, each circle badge, each icon) is an independent box
whose x/y/width/height the model authors by hand. Two failure modes follow when
that hand-arithmetic is slightly off:

  1. An icon lands outside the circle/ellipse "badge" it was meant to sit in
     (one wrong coordinate detaches it — see slide-7 icon-612 vs shape-611).
  2. A text box overflows the bottom of the panel that visually contains it,
     because the model budgeted the panel height for one line but the copy
     wrapped to two (see slide-8 descriptions spilling past shape-705).

Two more overlap fixes target the same collision class:

  3. A kicker/eyebrow caption stacked on top of its title (same `y`) is lifted to
     sit above it — or, if the title is flush to the safe zone, the title is
     pushed down instead (see slide-9 "DEMOCRATS" over the title).
  4. A body paragraph overlapping a small (non-background) image is dropped below
     the image (see slide-9 portrait over the "AOC, Bernie…" copy).

Every fix follows the same rule: mutate only when there's clearance, otherwise
leave the collision flagged for the visual-QA regenerate loop — never shove
elements into new collisions. All fixes act directly on the changelog geometry
records (the single source of truth read by both merged_deck.json and
editor_deck.json — see core/merger.build_editor_slides). `normalize_layout`
mutates `deck` in place and returns (deck, fixes) where `fixes` is a list of
human-readable strings describing every change made or collision left flagged.
"""

from __future__ import annotations

# --- canvas / tuning constants ------------------------------------------------
CANVAS_W = 1280
CANVAS_H = 720
SAFE_TOP = 48
SAFE_BOTTOM = CANVAS_H - 48   # 672

# Icon-to-badge snapping.
ICON_MAX_BADGE_RATIO = 3.0   # a badge may be up to 3x the icon; larger => not a badge
SNAP_EPS = 1.5               # ignore sub-pixel offsets already centered

# Container-grow.
CONTAIN_TOL = 2              # slack when deciding an element sits inside a panel
GROW_PAD = 8                 # breathing room added below the lowest overflowing text
GROW_MAX_BOTTOM = CANVAS_H   # never grow a panel past the canvas edge
MIN_CONTENT_W = 140          # narrower text is a label/page-number, not a content column

# Overlap de-clashing.
KICKER_GAP = 8               # gap between a kicker/eyebrow caption and its title
IMG_TEXT_GAP = 12            # gap when dropping a paragraph below its image
IMG_MAX_SIDE = 256           # larger images are treated as scene/background, not thumbnails
OVERLAP_TOL = 2              # ignore hairline touches


# --- geometry helpers ---------------------------------------------------------

def _box(el: dict):
    """(x, y, w, h) for a changelog element record, or None if ungeometried."""
    pos = el.get("position")
    if not isinstance(pos, dict):
        return None
    x, y = pos.get("x"), pos.get("y")
    w, h = el.get("width"), el.get("height")
    if None in (x, y, w, h):
        return None
    return x, y, w, h


def _center(b):
    x, y, w, h = b
    return x + w / 2, y + h / 2


def _intersects(a, b):
    """Do axis-aligned boxes a=(x,y,w,h) and b=(x,y,w,h) overlap (area > 0)?"""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _kind(eid: str, el: dict) -> str:
    """Coarse element kind from id prefix (matches the deck's id convention)."""
    return eid.split("-", 1)[0]


def _first_blocker(elements: dict, band, skip_ids, mover_box=None):
    """Return the id of the first element that occupies `band`, or None if the
    band is clear. Skips ids in `skip_ids`, zero-area hairlines, and anything the
    mover already overlaps at its current position (`mover_box`) — an element the
    mover already sits on is intended backdrop, not a new collision."""
    for oe, oel in elements.items():
        if oe in skip_ids:
            continue
        ob = _box(oel)
        if ob is None or ob[2] <= 1 or ob[3] <= 1:   # hairline rules/dividers never block
            continue
        if mover_box is not None and _intersects(ob, mover_box):
            continue
        if _intersects(band, ob):
            return oe
    return None


# --- fix 1: snap icons onto their circle/ellipse badges -----------------------

def _snap_icons(elements: dict, sid: str, fixes: list):
    icons, badges = [], []
    for eid, el in elements.items():
        b = _box(el)
        if b is None:
            continue
        if _kind(eid, el) == "icon":
            icons.append((eid, el, b))
        elif el.get("shapeType") in ("circle", "ellipse"):
            badges.append((eid, el, b))
    if not icons or not badges:
        return

    # Candidate (icon, badge) pairs: the badge must be able to contain the icon
    # and be badge-sized (not a huge decorative disc), and their centers must be
    # close enough that this is plausibly the icon's own badge rather than a
    # neighbour's. Cap = the badge's own diameter keeps neighbouring badges out.
    candidates = []
    for ie, iel, ib in icons:
        icx, icy = _center(ib)
        iw, ih = ib[2], ib[3]
        for be, bel, bb in badges:
            bw, bh = bb[2], bb[3]
            if bw < iw or bh < ih:
                continue
            if bw > iw * ICON_MAX_BADGE_RATIO or bh > ih * ICON_MAX_BADGE_RATIO:
                continue
            bcx, bcy = _center(bb)
            dist = ((icx - bcx) ** 2 + (icy - bcy) ** 2) ** 0.5
            if dist > max(bw, bh):
                continue
            candidates.append((dist, ie, iel, ib, be, bb))

    # Greedy nearest-first assignment; each icon and badge used at most once.
    candidates.sort(key=lambda c: c[0])
    used_icons, used_badges = set(), set()
    for dist, ie, iel, ib, be, bb in candidates:
        if ie in used_icons or be in used_badges:
            continue
        used_icons.add(ie)
        used_badges.add(be)
        if dist <= SNAP_EPS:
            continue  # already centred
        bx, by, bw, bh = bb
        iw, ih = ib[2], ib[3]
        tx = round(bx + (bw - iw) / 2)
        ty = round(by + (bh - ih) / 2)
        iel["position"]["x"] = tx
        iel["position"]["y"] = ty
        fixes.append(
            f"{sid}: snapped {ie} onto {be} "
            f"(was {ib[0]},{ib[1]} -> {tx},{ty}, off by {dist:.0f}px)"
        )


# --- fix 2: grow a panel to enclose text that overflows its bottom ------------

def _sits_inside(panel, box):
    """True if `box` belongs to `panel`: horizontally within it and starting
    within its vertical span. Bottom overflow is allowed — that is exactly the
    case we grow to enclose, and inner content (dividers, cards) that extends
    below the panel bottom still counts as the panel's own content, not an
    obstacle to growing it."""
    px, py, pw, ph = panel
    bx, by, bw, bh = box
    if bx < px - CONTAIN_TOL or bx + bw > px + pw + CONTAIN_TOL:
        return False
    if by < py - CONTAIN_TOL:
        return False
    if by >= py + ph:            # starts below the panel — not inside it
        return False
    return True


def _grow_panels(elements: dict, sid: str, fixes: list):
    # Panels: filled rectangles big enough to act as containers.
    panels = []
    for eid, el in elements.items():
        b = _box(el)
        if b is None:
            continue
        st = el.get("shapeType")
        fill = (el.get("fill") or "").lower()
        if st not in ("rectangle", "roundedRectangle", "roundRect"):
            continue
        if fill in ("", "none", "transparent"):
            continue
        if b[2] < 120 or b[3] < 48:   # too small to be a panel
            continue
        panels.append((eid, el, b))
    if not panels:
        return

    texts = [
        (eid, el, _box(el))
        for eid, el in elements.items()
        if _kind(eid, el) == "text" and _box(el) is not None
    ]

    for pe, pel, pb in panels:
        px, py, pw, ph = pb
        p_bottom = py + ph
        overflowing = []
        for te, tel, tb in texts:
            if not _sits_inside(pb, tb):
                continue
            if tb[2] < MIN_CONTENT_W:   # a label/page-number, not body copy
                continue
            if tb[1] + tb[3] > p_bottom + CONTAIN_TOL:
                overflowing.append((te, tb))
        if not overflowing:
            continue

        need_bottom = max(tb[1] + tb[3] for _, tb in overflowing) + GROW_PAD
        new_h = need_bottom - py

        # Collision: nothing that is NOT part of this panel may occupy the band
        # we are about to fill (old bottom -> new bottom, across the panel width).
        # Anything that sits inside the panel is its own content; zero-area
        # hairlines and any backdrop the panel already sits on never obstruct.
        band = (px, p_bottom, pw, need_bottom - p_bottom)
        skip = {pe} | {te for te, _ in overflowing if te}
        skip |= {eid for eid, el in elements.items()
                 if _box(el) and _sits_inside(pb, _box(el))}
        blocked_by = _first_blocker(elements, band, skip, mover_box=pb)

        ids = ", ".join(te for te, _ in overflowing)
        if need_bottom > GROW_MAX_BOTTOM:
            fixes.append(
                f"{sid}: {ids} overflow {pe} but need bottom {need_bottom:.0f} "
                f"> canvas {GROW_MAX_BOTTOM} — left for visual-QA"
            )
            continue
        if blocked_by is not None:
            fixes.append(
                f"{sid}: {ids} overflow {pe} but grow band hits {blocked_by} "
                f"— left for visual-QA"
            )
            continue

        pel["height"] = round(new_h)
        fixes.append(
            f"{sid}: grew {pe} to enclose {ids} "
            f"(h {ph} -> {round(new_h)}, bottom {p_bottom} -> {round(need_bottom)})"
        )


# --- fix 3: lift a kicker/eyebrow caption off the title it overlaps -----------

def _fix_kicker_title(elements: dict, sid: str, fixes: list, text_types: dict):
    captions, titles = [], []
    for eid, el in elements.items():
        b = _box(el)
        if b is None:
            continue
        t = text_types.get(eid)
        if t == "caption":
            captions.append((eid, el, b))
        elif t in ("title", "heading"):
            titles.append((eid, el, b))
    if not captions or not titles:
        return

    for ce, cel, cb in captions:
        # The caption's own title is the one it overlaps and starts at/above.
        title = None
        for te, tel, tb in titles:
            if _intersects(cb, tb) and cb[1] <= tb[1] + OVERLAP_TOL:
                title = (te, tel, tb)
                break
        if title is None:
            continue
        te, tel, tb = title
        cx, cy, cw, ch = cb
        tx, ty, tw, th = tb

        # Preferred: move the caption up so it sits fully above the title.
        new_cy = ty - ch - KICKER_GAP
        if new_cy >= SAFE_TOP:
            cel["position"]["y"] = new_cy
            fixes.append(
                f"{sid}: lifted kicker {ce} above title {te} "
                f"(y {cy} -> {new_cy})"
            )
            continue

        # No room above (title flush to safe zone): push the title down instead,
        # but only if the band it moves into is clear.
        delta = cy + ch + KICKER_GAP - ty
        band = (tx, ty + th, tw, delta)
        blocked_by = _first_blocker(elements, band, {te, ce}, mover_box=tb)
        if blocked_by is not None or ty + th + delta > SAFE_BOTTOM:
            reason = blocked_by or "canvas edge"
            fixes.append(
                f"{sid}: kicker {ce} overlaps title {te} but no room to separate "
                f"({reason}) — left for visual-QA"
            )
            continue
        tel["position"]["y"] = ty + delta
        fixes.append(
            f"{sid}: pushed title {te} below kicker {ce} (y {ty} -> {ty + delta})"
        )


# --- fix 4: drop a paragraph off the small image it overlaps ------------------

def _declash_image_text(elements, sid, fixes, text_types, img_bg):
    images = []
    for eid, el in elements.items():
        b = _box(el)
        if b is None or _kind(eid, el) != "image":
            continue
        if img_bg.get(eid):                       # full-bleed background: overlap is intended
            continue
        if b[2] > IMG_MAX_SIDE or b[3] > IMG_MAX_SIDE:
            continue
        images.append((eid, el, b))
    if not images:
        return

    texts = [
        (eid, el, _box(el))
        for eid, el in elements.items()
        if text_types.get(eid) in ("paragraph", "heading") and _box(el) is not None
    ]

    for te, tel, tb in texts:
        for ie, iel, ib in images:
            if not _intersects(tb, ib):
                continue
            tx, ty, tw, th = tb
            new_y = ib[1] + ib[3] + IMG_TEXT_GAP   # drop below the image
            if new_y <= ty:                        # already clear / above — leave it
                break
            moved = (tx, new_y, tw, th)
            blocked_by = _first_blocker(elements, moved, {te, ie}, mover_box=tb)
            if blocked_by is not None or new_y + th > SAFE_BOTTOM:
                reason = blocked_by or "canvas edge"
                fixes.append(
                    f"{sid}: text {te} overlaps image {ie} but can't drop below "
                    f"({reason}) — left for visual-QA"
                )
                break
            tel["position"]["y"] = new_y
            fixes.append(
                f"{sid}: moved text {te} below image {ie} (y {ty} -> {new_y})"
            )
            break


# --- entry point --------------------------------------------------------------

def _build_lookups(deck: dict):
    """text id -> type and image id -> isBackground, from the content records."""
    content = deck.get("files", {}).get("content", {})
    text_types = {}
    for slide in content.get("slides", []):
        for t in slide.get("textElements", []):
            text_types[t.get("id")] = t.get("type")
    img_bg = {
        im.get("id"): bool(im.get("isBackground"))
        for im in content.get("imageElements", [])
    }
    return text_types, img_bg


def normalize_layout(deck: dict):
    """Apply deterministic geometry fixes to `deck` (mutated in place).

    Returns (deck, fixes). Safe to call on any split-format deck; a deck without
    a changelog is returned untouched with an empty fix list.
    """
    fixes: list = []
    slides = (
        deck.get("files", {})
        .get("changelog", {})
        .get("slides", {})
    )
    if not isinstance(slides, dict):
        return deck, fixes

    text_types, img_bg = _build_lookups(deck)

    for sid, body in slides.items():
        elements = body.get("elements")
        if not isinstance(elements, dict):
            continue
        _snap_icons(elements, sid, fixes)
        _grow_panels(elements, sid, fixes)
        _fix_kicker_title(elements, sid, fixes, text_types)
        _declash_image_text(elements, sid, fixes, text_types, img_bg)

    return deck, fixes
