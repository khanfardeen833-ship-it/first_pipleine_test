"""
Procedural SVG motif engine — generates decorative full-bleed background
graphics (plexus, dot-grid, hexagons, waves, flow-lines, plus the premium
families aurora, topography, rings and circuit) as pure SVG.

You are not generating an image; you are generating geometry. Each motif is a
recipe over shared pieces:
  - a SEEDED rng  (reproducible: same seed -> same art; +1 -> different art)
  - PLACEMENT     (random / grid / nearest-neighbour graph)
  - EFFECTS       (glow via feGaussianBlur, gradient fills, opacity)
  - CONSTRAINTS   (palette, density, a text-SAFE-AREA the motif keeps sparse)

Glow and gradient are baked INTO the SVG, so every renderer (preview.html, the
editor, and — once rasterised — PPTX) shows it by treating the result as an
ordinary background image. Nothing downstream needs a "glow" feature.

Public API:
    svg = generate_motif("plexus", width=1280, height=720,
                         palette="green_tech", density=0.7, glow=0.8,
                         safe_area="right", seed=12345)
    uri = motif_data_uri("plexus", ...)   # data:image/svg+xml;base64,... for an
                                           # image element `src`
"""

import base64
import math
import random

# ---------------------------------------------------------------------------
# Palettes — bg is a 2-stop gradient; accent drives nodes/lines; glow is the
# halo colour. Add your own or pass a dict with the same keys.
# ---------------------------------------------------------------------------
PALETTES = {
    "green_tech":  {"bg": ["#0C2E2B", "#061A19"], "accent": "#37E29A", "accent2": "#8CF5C4", "glow": "#37E29A"},
    "blue_cyber":  {"bg": ["#0A1F3C", "#050E1F"], "accent": "#3E9BFA", "accent2": "#8FD0FF", "glow": "#3E9BFA"},
    "purple_night":{"bg": ["#1E1140", "#0C0722"], "accent": "#B57BFF", "accent2": "#E0C6FF", "glow": "#B57BFF"},
    "amber_dark":  {"bg": ["#2A1C0B", "#160E05"], "accent": "#F2B138", "accent2": "#FFD98A", "glow": "#F2B138"},
    "slate_ice":   {"bg": ["#1C2430", "#0C1017"], "accent": "#8FB2CC", "accent2": "#D7E6F2", "glow": "#AFD0E8"},
    "crimson_dark":{"bg": ["#33101A", "#1A0710"], "accent": "#F2557A", "accent2": "#FFA9BF", "glow": "#F2557A"},
    # --- premium palettes: deeper base gradients, restrained luxe accents -----
    "onyx_gold":        {"bg": ["#161513", "#050504"], "accent": "#E8C169", "accent2": "#F7E4AC", "glow": "#E8C169"},
    "royal_indigo":     {"bg": ["#1A1B3A", "#090A1C"], "accent": "#7C83FF", "accent2": "#BBBEFF", "glow": "#7C83FF"},
    "deep_ocean":       {"bg": ["#07242E", "#03111A"], "accent": "#2FD4C4", "accent2": "#A0F0E7", "glow": "#2FD4C4"},
    "graphite_platinum":{"bg": ["#23262B", "#0F1114"], "accent": "#AEB7C2", "accent2": "#E9EFF5", "glow": "#C9D3DE"},
    "wine_gold":        {"bg": ["#2E0F1B", "#15070F"], "accent": "#C9A24B", "accent2": "#F1D68E", "glow": "#D8B35E"},
    "emerald_noir":     {"bg": ["#08241C", "#03120F"], "accent": "#34D399", "accent2": "#A2EFCC", "glow": "#34D399"},
    "sapphire_rose":    {"bg": ["#0E1A3A", "#060A1E"], "accent": "#FF8FB1", "accent2": "#FFC9DA", "glow": "#8FB8FF"},
    # --- light editorial palettes (for the data_horizon collage motif) --------
    "ivory_gold":       {"bg": ["#F7F3E9", "#FCFBF6"], "accent": "#BF9B30", "accent2": "#3D3A34", "glow": "#BF9B30"},
    "pearl_slate":      {"bg": ["#F3F5F7", "#FCFCFD"], "accent": "#9AA3B2", "accent2": "#2B303B", "glow": "#9AA3B2"},
    "linen_sage":       {"bg": ["#F3F4EE", "#FBFBF7"], "accent": "#7E8C6A", "accent2": "#39402F", "glow": "#7E8C6A"},
}


def _resolve_palette(palette):
    if isinstance(palette, dict):
        p = dict(PALETTES["green_tech"])
        p.update(palette)
        return p
    return PALETTES.get(palette, PALETTES["green_tech"])


# ---------------------------------------------------------------------------
# Shared SVG scaffolding
# ---------------------------------------------------------------------------
def _defs(pal, glow_strength):
    """Background gradient + a reusable glow filter (blur amount scales with the
    glow knob)."""
    blur = round(1.5 + glow_strength * 6.5, 2)
    soft = round(3 + glow_strength * 10, 2)
    return (
        '<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{pal["bg"][0]}"/>'
        f'<stop offset="1" stop-color="{pal["bg"][1]}"/>'
        '</linearGradient>'
        f'<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur stdDeviation="{blur}" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
        f'<filter id="soft" x="-120%" y="-120%" width="340%" height="340%">'
        f'<feGaussianBlur stdDeviation="{soft}"/>'
        '</filter>'
        '</defs>'
    )


def _open(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">')


def _bg(w, h):
    return f'<rect width="{w}" height="{h}" fill="url(#bg)"/>'


def _density_at(safe_area, w, h, strength=0.9):
    """Returns d(x,y) in [0.08,1] — high where nodes are welcome, low in the
    text-safe area so titles stay legible (dense one side, sparse the other)."""
    def d(x, y):
        if safe_area == "right":   t = x / w
        elif safe_area == "left":  t = 1 - x / w
        elif safe_area == "top":   t = y / h
        elif safe_area == "bottom":t = 1 - y / h
        elif safe_area == "center":
            # sparse through the central vertical band (keeps a centred title
            # clean), dense out toward both side margins
            t = 1 - min(1.0, abs(x - w / 2) / (w / 2))
        else:                       return 1.0
        return max(0.08, 1.0 - t * strength)
    return d


def _scatter(rng, w, h, n, safe_area, bleed=40):
    """Rejection-sample n points biased away from the safe area; allow a little
    bleed off every edge so the motif runs past the slide border."""
    d = _density_at(safe_area, w, h)
    pts, guard = [], 0
    while len(pts) < n and guard < n * 40:
        guard += 1
        x = rng.uniform(-bleed, w + bleed)
        y = rng.uniform(-bleed, h + bleed)
        xc, yc = min(max(x, 0), w), min(max(y, 0), h)
        if rng.random() < d(xc, yc):
            pts.append((x, y))
    return pts


def _biased_point(rng, w, h, d, bleed=0.1):
    """One point, rejection-biased away from the safe area (allowing `bleed`
    fraction off each edge). Falls back to a plain uniform sample."""
    for _ in range(30):
        x = rng.uniform(-bleed * w, (1 + bleed) * w)
        y = rng.uniform(-bleed * h, (1 + bleed) * h)
        if rng.random() < d(min(max(x, 0), w), min(max(y, 0), h)):
            return x, y
    return rng.uniform(0, w), rng.uniform(0, h)


def _contour_pts(cx, cy, base_r, harmonics, steps=140):
    """Closed loop of `steps` points, radius = base_r perturbed by a few sine
    harmonics — one topographic contour ring."""
    pts = []
    for s in range(steps):
        ang = math.tau * s / steps
        rr = base_r + sum(a * math.sin(f * ang + p) for (a, f, p) in harmonics)
        pts.append(f'{cx + rr*math.cos(ang):.1f},{cy + rr*math.sin(ang):.1f}')
    return " ".join(pts)


# ---------------------------------------------------------------------------
# Motif 1 — PLEXUS  (random placement + nearest-neighbour graph + glow)
# ---------------------------------------------------------------------------
def _plexus(rng, w, h, pal, density, glow, safe_area):
    n = int(55 + density * 120)                 # 55..175 nodes
    pts = _scatter(rng, w, h, n, safe_area)
    max_dist = (w * 0.11) * (0.7 + density * 0.6)
    k = 3 if density < 0.6 else 4

    # nearest-neighbour edges (dedup by ordered pair)
    edges = set()
    for i, (x1, y1) in enumerate(pts):
        nbrs = sorted(
            ((math.hypot(x1 - x2, y1 - y2), j) for j, (x2, y2) in enumerate(pts) if j != i)
        )[:k]
        for dist, j in nbrs:
            if dist <= max_dist:
                edges.add((min(i, j), max(i, j)))

    parts = []
    # lines — shorter = brighter, all softly glowing (depth cue)
    parts.append(f'<g filter="url(#glow)" stroke="{pal["accent"]}" fill="none">')
    for i, j in edges:
        x1, y1 = pts[i]; x2, y2 = pts[j]
        dist = math.hypot(x1 - x2, y1 - y2)
        op = round(max(0.06, 0.5 - dist / (max_dist * 2.2)), 3)
        sw = round(0.6 + (1 - dist / max_dist) * 0.9, 2)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     f'stroke-width="{sw}" stroke-opacity="{op}"/>')
    parts.append('</g>')

    # node halos (soft blur)
    parts.append(f'<g fill="{pal["glow"]}" filter="url(#soft)">')
    radii = []
    for (x, y) in pts:
        bright = rng.random()
        r = 1.6 + bright * 3.2 + density * 0.6
        radii.append((r, bright))
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*3.2:.1f}" '
                     f'opacity="{0.10 + bright*0.22*glow:.3f}"/>')
    parts.append('</g>')

    # node cores + highlights
    parts.append('<g>')
    for (x, y), (r, bright) in zip(pts, radii):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{pal["accent"]}" '
                     f'opacity="{0.55 + bright*0.45:.3f}"/>')
        if bright > 0.68:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.42:.1f}" '
                         f'fill="{pal["accent2"]}" opacity="0.95"/>')
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 2 — DOT GRID  (grid placement + jitter + random size/opacity/removal)
# ---------------------------------------------------------------------------
def _dot_grid(rng, w, h, pal, density, glow, safe_area):
    step = int(64 - density * 28)               # tighter grid at high density
    d = _density_at(safe_area, w, h, strength=0.85)
    parts = [f'<g fill="{pal["accent"]}">']
    y = step // 2
    while y < h + step:
        x = step // 2
        while x < w + step:
            jx = x + rng.uniform(-step*0.18, step*0.18)
            jy = y + rng.uniform(-step*0.18, step*0.18)
            keep = rng.random() < d(min(max(jx,0),w), min(max(jy,0),h)) * 0.9
            if keep:
                r = rng.uniform(1.4, 3.6)
                op = round(rng.uniform(0.15, 0.9), 3)
                glow_dot = rng.random() < 0.12 * glow
                if glow_dot:
                    parts.append(f'<circle cx="{jx:.1f}" cy="{jy:.1f}" r="{r*3:.1f}" '
                                 f'fill="{pal["glow"]}" opacity="{0.25*glow:.3f}" filter="url(#soft)"/>')
                parts.append(f'<circle cx="{jx:.1f}" cy="{jy:.1f}" r="{r:.1f}" opacity="{op}"/>')
            x += step
        y += step
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 3 — HEXAGONS  (hex tessellation + random remove/glow/connect)
# ---------------------------------------------------------------------------
def _hex_points(cx, cy, r):
    pts = []
    for a in range(6):
        ang = math.radians(60 * a)
        pts.append(f'{cx + r*math.cos(ang):.1f},{cy + r*math.sin(ang):.1f}')
    return " ".join(pts)


def _hexagons(rng, w, h, pal, density, glow, safe_area):
    r = 46 - density * 16                        # cell size
    dx = r * 1.5
    dy = r * math.sqrt(3)
    d = _density_at(safe_area, w, h, strength=0.85)
    parts = [f'<g fill="none" stroke="{pal["accent"]}">']
    col = 0
    x = -r
    while x < w + r:
        offset = (dy / 2) if col % 2 else 0
        y = -r + offset
        while y < h + r:
            keep = rng.random() < d(min(max(x,0),w), min(max(y,0),h))
            if keep:
                pts = _hex_points(x, y, r)
                op = round(rng.uniform(0.10, 0.5), 3)
                if rng.random() < 0.14 * glow:
                    parts.append(f'<polygon points="{pts}" stroke="{pal["glow"]}" '
                                 f'stroke-width="1.6" opacity="{0.6*glow:.3f}" filter="url(#glow)"/>')
                parts.append(f'<polygon points="{pts}" stroke-width="1" opacity="{op}"/>')
            y += dy
        x += dx
        col += 1
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 4 — WAVES  (stacked sine curves + gradient + glow + particles)
# ---------------------------------------------------------------------------
def _waves(rng, w, h, pal, density, glow, safe_area):
    lines = int(4 + density * 8)
    parts = ['<g fill="none">']
    for i in range(lines):
        base_y = h * (0.15 + 0.75 * i / max(1, lines - 1))
        amp = rng.uniform(18, 60) * (0.6 + density)
        freq = rng.uniform(1.2, 3.0)
        phase = rng.uniform(0, math.tau)
        op = round(rng.uniform(0.12, 0.5), 3)
        pts = []
        steps = 60
        for s in range(steps + 1):
            x = w * s / steps
            y = base_y + amp * math.sin(freq * math.tau * s / steps + phase)
            pts.append(f'{x:.1f},{y:.1f}')
        path = "M" + " L".join(pts)
        parts.append(f'<polyline points="{" ".join(pts)}" stroke="{pal["accent"]}" '
                     f'stroke-width="1.4" opacity="{op}" filter="url(#glow)"/>')
        # particles riding the wave
        for _ in range(int(3 + density * 5)):
            s = rng.randint(0, steps)
            x = w * s / steps
            y = base_y + amp * math.sin(freq * math.tau * s / steps + phase)
            rr = rng.uniform(1.6, 3.4)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr*2.6:.1f}" '
                         f'fill="{pal["glow"]}" opacity="{0.22*glow:.3f}" filter="url(#soft)"/>')
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{pal["accent2"]}"/>')
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 5 — FLOW LINES  (drifting curves + particles)
# ---------------------------------------------------------------------------
def _flow(rng, w, h, pal, density, glow, safe_area):
    lines = int(6 + density * 12)
    parts = ['<g fill="none">']
    for _ in range(lines):
        y0 = rng.uniform(0, h)
        drift = rng.uniform(-h*0.25, h*0.25)
        wob = rng.uniform(10, 45)
        freq = rng.uniform(1.0, 2.4)
        phase = rng.uniform(0, math.tau)
        op = round(rng.uniform(0.10, 0.4), 3)
        pts = []
        steps = 50
        for s in range(steps + 1):
            t = s / steps
            x = w * t
            y = y0 + drift * t + wob * math.sin(freq * math.tau * t + phase)
            pts.append(f'{x:.1f},{y:.1f}')
        parts.append(f'<polyline points="{" ".join(pts)}" stroke="{pal["accent"]}" '
                     f'stroke-width="1.1" opacity="{op}" filter="url(#glow)"/>')
        for _ in range(rng.randint(1, 3)):
            s = rng.randint(0, steps)
            t = s / steps
            x = w * t
            y = y0 + drift * t + wob * math.sin(freq * math.tau * t + phase)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" fill="{pal["accent2"]}" '
                         f'opacity="0.9"/>')
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 6 — AURORA  (soft layered mesh-gradient orbs — Linear/Stripe hero look)
# ---------------------------------------------------------------------------
def _aurora(rng, w, h, pal, density, glow, safe_area):
    """Big, soft radial-gradient orbs that overlap and bloom over the dark
    field — the modern 'mesh gradient' background. Colours fade to fully
    transparent, so no filter is needed and it rasterises cleanly to PNG."""
    d = _density_at(safe_area, w, h, strength=0.95)
    n = int(4 + density * 5)                     # 4..9 orbs
    cols = [pal["accent"], pal["accent2"], pal["glow"]]
    defs, orbs = [], []
    for i in range(n):
        cx, cy = _biased_point(rng, w, h, d, bleed=0.15)
        rad = rng.uniform(0.30, 0.62) * w
        col = cols[i % len(cols)]
        gid = f"aur{i}"
        peak = round((0.30 + 0.45 * glow) * (0.55 + 0.45 * rng.random()), 3)
        defs.append(
            f'<radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0" stop-color="{col}" stop-opacity="{peak}"/>'
            f'<stop offset="55%" stop-color="{col}" stop-opacity="{peak*0.32:.3f}"/>'
            f'<stop offset="100%" stop-color="{col}" stop-opacity="0"/>'
            '</radialGradient>')
        orbs.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="url(#{gid})"/>')
    return '<defs>' + "".join(defs) + '</defs><g>' + "".join(orbs) + '</g>'


# ---------------------------------------------------------------------------
# Motif 7 — TOPOGRAPHY  (concentric perturbed contour rings around peaks)
# ---------------------------------------------------------------------------
def _topography(rng, w, h, pal, density, glow, safe_area):
    d = _density_at(safe_area, w, h, strength=0.95)
    peaks = [_biased_point(rng, w, h, d, bleed=0.05)
             for _ in range(2 if density < 0.55 else 3)]
    rings = int(9 + density * 13)
    r_max = w * 0.62
    parts = [f'<g fill="none" stroke="{pal["accent"]}" stroke-linejoin="round">']
    for (cx, cy) in peaks:
        harm = [(rng.uniform(0.05, 0.11), rng.randint(2, 3), rng.uniform(0, math.tau)),
                (rng.uniform(0.02, 0.05), rng.randint(4, 6), rng.uniform(0, math.tau))]
        for k in range(1, rings + 1):
            base = r_max * k / rings
            pts = _contour_pts(cx, cy, base, [(a*base, f, p) for (a, f, p) in harm])
            fade = 1 - k / rings
            op = round(0.10 + 0.28 * fade, 3)
            sw = round(0.8 + 0.7 * fade, 2)
            if k % 5 == 0 and glow > 0:
                parts.append(f'<polygon points="{pts}" stroke="{pal["glow"]}" '
                             f'stroke-width="{sw}" opacity="{0.45*glow:.3f}" filter="url(#glow)"/>')
            parts.append(f'<polygon points="{pts}" stroke-width="{sw}" opacity="{op}"/>')
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 8 — RINGS  (concentric orbital arcs around an off-canvas focus)
# ---------------------------------------------------------------------------
def _rings(rng, w, h, pal, density, glow, safe_area):
    """Orbital rings expanding from a focus pushed OFF the non-text edge, so the
    tight (busy) rings stay away from the title and only wide, sparse arcs sweep
    across the safe area."""
    focus = {"right": (-0.05*w, h*0.5), "left": (1.05*w, h*0.5),
             "top": (w*0.5, 1.05*h), "bottom": (w*0.5, -0.05*h)}
    cx, cy = focus.get(safe_area, (w*0.16, h*0.9))
    n = int(7 + density * 12)
    step = (w * 0.92) / n
    parts = ['<g fill="none">']
    for i in range(1, n + 1):
        r = step * i
        op = round(max(0.06, 0.42 - 0.02 * i), 3)
        sw = round(0.7 + rng.uniform(0, 0.8), 2)
        glowing = rng.random() < 0.3 * glow
        col = pal["glow"] if glowing else pal["accent"]
        filt = ' filter="url(#glow)"' if glowing else ''
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="{col}" '
                     f'stroke-width="{sw}" opacity="{op}"{filt}/>')
        if rng.random() < 0.5:                       # a satellite riding the ring
            ang = rng.uniform(0, math.tau)
            nx, ny = cx + r * math.cos(ang), cy + r * math.sin(ang)
            rr = rng.uniform(2.0, 3.6)
            parts.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{rr*2.4:.1f}" '
                         f'fill="{pal["glow"]}" opacity="{0.28*glow:.3f}" filter="url(#soft)"/>')
            parts.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{rr:.1f}" fill="{pal["accent2"]}"/>')
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 9 — CIRCUIT  (PCB-style Manhattan traces with pads/vias)
# ---------------------------------------------------------------------------
def _circuit(rng, w, h, pal, density, glow, safe_area):
    d = _density_at(safe_area, w, h, strength=0.85)
    n = int(10 + density * 22)
    pads = []
    parts = [f'<g stroke="{pal["accent"]}" fill="none" '
             'stroke-linejoin="round" stroke-linecap="round">']
    for _ in range(n):
        x, y = _biased_point(rng, w, h, d, bleed=0.0)
        px, py = x, y
        path, horiz = [f'M{px:.1f} {py:.1f}'], rng.random() < 0.5
        for _s in range(rng.randint(2, 5)):
            leg = rng.uniform(w * 0.04, w * 0.16) * rng.choice((-1, 1))
            if horiz: px += leg
            else:     py += leg
            path.append(f'L{px:.1f} {py:.1f}')
            horiz = not horiz
        d_attr = " ".join(path)
        op = round(rng.uniform(0.12, 0.4), 3)
        sw = round(rng.uniform(0.8, 1.5), 2)
        if rng.random() < 0.22 * glow:
            parts.append(f'<path d="{d_attr}" stroke="{pal["glow"]}" '
                         f'stroke-width="{sw+0.6:.2f}" opacity="{0.5*glow:.3f}" filter="url(#glow)"/>')
        parts.append(f'<path d="{d_attr}" stroke-width="{sw}" opacity="{op}"/>')
        pads += [(x, y, op), (px, py, op)]
    parts.append('</g><g>')
    for (x, y, op) in pads:
        if rng.random() < 0.35:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(4.5,7):.1f}" '
                         f'fill="{pal["glow"]}" opacity="{0.25*glow:.3f}" filter="url(#soft)"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(2.2,3.8):.1f}" '
                     f'fill="{pal["accent"]}" opacity="{min(0.9, op+0.3):.3f}"/>')
    parts.append('</g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Motif 10 — DATA HORIZON  (light editorial "analytics collage": a perspective
# vanishing-point grid, symmetric decorative data-viz glyphs, and a corner
# frame — the premium report / marketing-metrics look. Best on a LIGHT palette
# with a gold accent + charcoal ink; keeps the centre clear for a serif title.)
# ---------------------------------------------------------------------------
def _dh_donut(rng, cx, cy, s, gold, ink):
    r = s * 0.5
    sw = max(2.0, s * 0.16)
    a0 = rng.uniform(0, math.tau)
    frac = rng.uniform(0.28, 0.5)
    a1 = a0 + frac * math.tau
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if frac > 0.5 else 0
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
            f'stroke="{ink}" stroke-width="{sw:.1f}" opacity="0.32"/>'
            f'<path d="M{x0:.1f} {y0:.1f} A{r:.1f} {r:.1f} 0 {large} 1 {x1:.1f} {y1:.1f}" '
            f'fill="none" stroke="{gold}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')


def _dh_bars(rng, cx, cy, s, gold, ink):
    n = 5
    bw = s * 0.14
    gap = s * 0.08
    total = n * bw + (n - 1) * gap
    x = cx - total / 2
    base = cy + s * 0.5
    hi = rng.randint(0, n - 1)
    out = []
    for i in range(n):
        bh = s * (0.3 + 0.6 * rng.random())
        col = gold if i == hi else ink
        op = 0.9 if i == hi else 0.42
        out.append(f'<rect x="{x:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" '
                   f'height="{bh:.1f}" fill="{col}" opacity="{op:.2f}"/>')
        x += bw + gap
    return "".join(out)


def _dh_line(rng, cx, cy, s, gold, ink, *, rising=True, dashed=False):
    """Zig-zag line chart with node dots — the ascending 'mountain' motif."""
    n = rng.randint(5, 7)
    span = s * 2.2
    x0 = cx - span / 2
    step = span / (n - 1)
    trend = 1 if rising else -1
    pts, y = [], cy + trend * s * 0.5
    for i in range(n):
        y += -trend * rng.uniform(0.05, 0.35) * s + rng.uniform(-0.12, 0.12) * s
        pts.append((x0 + i * step, y))
    col = gold if rng.random() < 0.5 else ink
    dash = ' stroke-dasharray="5 4"' if dashed else ''
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out = [f'<polyline points="{poly}" fill="none" stroke="{col}" '
           f'stroke-width="1.6" opacity="0.7"{dash}/>']
    for x, y in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s*0.05:.1f}" '
                   f'fill="#FFFFFF" stroke="{col}" stroke-width="1.4"/>')
    return "".join(out)


def _dh_ruled(rng, cx, cy, s, gold, ink):
    """Stack of ruled lines standing in for text — varied widths, a gold one."""
    out = []
    y = cy - s * 0.4
    for i in range(rng.randint(3, 4)):
        lw = s * rng.uniform(0.9, 1.8)
        col = gold if i == 0 else ink
        op = 0.6 if i == 0 else 0.3
        out.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{lw:.1f}" '
                   f'height="{max(2,s*0.06):.1f}" rx="1.5" fill="{col}" opacity="{op:.2f}"/>')
        y += s * 0.28
    return "".join(out)


def _dh_dots(rng, cx, cy, s, gold, ink):
    """Small matrix of dots/squares, a few filled gold/ink."""
    cols, rows = 6, 4
    step = s * 0.22
    out = []
    for r in range(rows):
        for c in range(cols):
            x, y = cx + c * step, cy + r * step
            fill = rng.random()
            if fill < 0.12:
                out.append(f'<rect x="{x-2:.1f}" y="{y-2:.1f}" width="4" height="4" fill="{gold}"/>')
            elif fill < 0.24:
                out.append(f'<rect x="{x-2:.1f}" y="{y-2:.1f}" width="4" height="4" fill="{ink}" opacity="0.6"/>')
            else:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.4" fill="{ink}" opacity="0.3"/>')
    return "".join(out)


def _dh_sparkpanel(rng, cx, cy, s, gold, ink):
    """A framed panel with a filled area sparkline."""
    w0, h0 = s * 2.0, s * 1.2
    x, y = cx - w0 / 2, cy - h0 / 2
    n = 9
    step = w0 / (n - 1)
    ys = [y + h0 * (0.35 + 0.5 * rng.random()) for _ in range(n)]
    line = " ".join(f"{x+i*step:.1f},{yy:.1f}" for i, yy in enumerate(ys))
    area = f"{x:.1f},{y+h0:.1f} " + line + f" {x+w0:.1f},{y+h0:.1f}"
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w0:.1f}" height="{h0:.1f}" '
            f'rx="4" fill="none" stroke="{ink}" stroke-width="1" opacity="0.25"/>'
            f'<polygon points="{area}" fill="{gold}" opacity="0.12"/>'
            f'<polyline points="{line}" fill="none" stroke="{gold}" stroke-width="1.6"/>')


def _dh_frame(w, h, gold, ink):
    m = 30           # border inset
    b = 56           # corner bracket arm length
    sw = 2.2
    P = [f'<rect x="{m}" y="{m}" width="{w-2*m}" height="{h-2*m}" fill="none" '
         f'stroke="{gold}" stroke-width="1" opacity="0.4"/>']
    for cx, cy, sx, sy in ((m, m, 1, 1), (w-m, m, -1, 1),
                           (m, h-m, 1, -1), (w-m, h-m, -1, -1)):
        P.append(f'<path d="M{cx:.0f} {cy+sy*b:.0f} L{cx:.0f} {cy:.0f} L{cx+sx*b:.0f} {cy:.0f}" '
                 f'fill="none" stroke="{gold}" stroke-width="{sw}"/>')
        # small square notch just inside each corner
        P.append(f'<rect x="{cx+sx*14-4:.0f}" y="{cy+sy*14-4:.0f}" width="8" height="8" '
                 f'fill="none" stroke="{ink}" stroke-width="1.2" opacity="0.5"/>')
    # mid-edge tick clusters (left & right): three dots + a short dash
    for ex in (m, w - m):
        for k, dy in enumerate((-14, 0, 14)):
            P.append(f'<circle cx="{ex:.0f}" cy="{h/2+dy:.0f}" r="1.6" fill="{ink}" opacity="0.5"/>')
        P.append(f'<line x1="{ex:.0f}" y1="{h/2-30:.0f}" x2="{ex:.0f}" y2="{h/2-24:.0f}" '
                 f'stroke="{gold}" stroke-width="2"/>')
    return "".join(P)


def _data_horizon(rng, w, h, pal, density, glow, safe_area):
    gold, ink = pal["accent"], pal["accent2"]
    P = []

    # 1) perspective grid — rays converging on a vanishing point below the title
    vx, vy = w * 0.5, h * 0.86
    n_rays = int(20 + density * 20)
    for i in range(n_rays):
        t = i / (n_rays - 1)
        ex = -w * 0.18 + t * (w * 1.36)
        op = 0.04 + 0.12 * (abs(t - 0.5) * 2)        # faint toward the centre
        col = gold if i % 3 else ink
        P.append(f'<line x1="{vx:.1f}" y1="{vy:.1f}" x2="{ex:.1f}" y2="{h*1.02:.1f}" '
                 f'stroke="{col}" stroke-width="1" opacity="{op:.3f}"/>')
    for k in range(1, 7):                            # perspective floor lines
        yy = vy + (h - vy) * (k / 7) ** 1.7
        P.append(f'<line x1="0" y1="{yy:.1f}" x2="{w}" y2="{yy:.1f}" '
                 f'stroke="{gold}" stroke-width="1" opacity="{0.05+0.03*k:.3f}"/>')

    # 2) two mirrored ascending 'mountain' line-charts flanking the centre
    P.append(_dh_line(rng, w * 0.30, h * 0.66, 90, gold, ink, rising=False))
    P.append(_dh_line(rng, w * 0.30, h * 0.60, 80, gold, ink, rising=False, dashed=True))
    P.append(_dh_line(rng, w * 0.70, h * 0.66, 90, gold, ink, rising=True))
    P.append(_dh_line(rng, w * 0.70, h * 0.60, 80, gold, ink, rising=True, dashed=True))

    # 3) symmetric glyph clusters in the side margins (left set, mirrored right)
    left = [
        (0.13, 0.20, _dh_dots, 42),
        (0.14, 0.31, _dh_donut, 60),
        (0.15, 0.42, _dh_line, 52),
        (0.13, 0.55, _dh_ruled, 60),
        (0.11, 0.74, _dh_bars, 80),
    ]
    glyphs = list(left) + [(1 - fx, fy, fn, s) for (fx, fy, fn, s) in left]
    # tweak the mirrored side so it isn't a literal clone: bottom-right becomes
    # the framed sparkline panel (as in a report cover) instead of bars
    right_specials = {9: _dh_sparkpanel}
    for idx, (fx, fy, fn, s) in enumerate(glyphs):
        fn = right_specials.get(idx, fn)
        P.append(f'<g>{fn(rng, w*fx, h*fy, s, gold, ink)}</g>')

    # 4) corner frame + edge ticks
    P.append(_dh_frame(w, h, gold, ink))
    return "".join(P)


_GENERATORS = {
    "plexus": _plexus,
    "dot_grid": _dot_grid,
    "hexagons": _hexagons,
    "waves": _waves,
    "flow": _flow,
    "aurora": _aurora,
    "topography": _topography,
    "rings": _rings,
    "circuit": _circuit,
    "data_horizon": _data_horizon,
}
MOTIF_TYPES = tuple(_GENERATORS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_motif(type="plexus", *, width=1280, height=720, palette="green_tech",
                   density=0.7, glow=0.8, safe_area=None, seed=0):
    """Return a full-bleed SVG string for one motif.

    type      : plexus | dot_grid | hexagons | waves | flow
                | aurora | topography | rings | circuit | data_horizon
    palette   : a PALETTES key or a dict {bg:[c1,c2], accent, accent2, glow}
    density   : 0..1  — how busy the motif is
    glow      : 0..1  — halo intensity
    safe_area : None | "left" | "right" | "top" | "bottom" — kept sparse for text
    seed      : same seed -> identical art; change it for a different layout
    """
    if type not in _GENERATORS:
        raise ValueError(f"unknown motif type {type!r}; choose from {MOTIF_TYPES}")
    pal = _resolve_palette(palette)
    rng = random.Random(seed)
    density = max(0.0, min(1.0, density))
    glow = max(0.0, min(1.0, glow))
    body = _GENERATORS[type](rng, width, height, pal, density, glow, safe_area)
    return (_open(width, height) + _defs(pal, glow) + _bg(width, height)
            + body + '</svg>')


def motif_data_uri(type="plexus", **kw):
    """Return a data:image/svg+xml;base64 URI usable directly as an image `src`
    (renders in preview.html and the editor with no extra support)."""
    svg = generate_motif(type, **kw)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _decode_svg_data_uri(uri: str) -> str:
    head, _, data = uri.partition(",")
    if "base64" in head:
        return base64.b64decode(data).decode("utf-8")
    import urllib.parse
    return urllib.parse.unquote(data)


async def rasterize_svg_data_uris(uris, width=1280, height=720) -> dict:
    """Map each `data:image/svg+xml` URI -> a `data:image/png;base64` URI via a
    headless browser. PowerPoint's SVG support is unreliable, so the PPTX
    exporter swaps motif SVGs for PNGs. Best-effort: returns {} if Playwright is
    not installed (the SVG is then left as-is)."""
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return {}
    out = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height},
                                      device_scale_factor=2)
        for uri in uris:
            try:
                svg = _decode_svg_data_uri(uri)
                await page.set_content(
                    f'<!doctype html><html><body style="margin:0">{svg}</body></html>')
                await page.wait_for_timeout(150)
                png = await page.screenshot(type="png")
                out[uri] = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
            except Exception:
                pass
        await browser.close()
    return out
