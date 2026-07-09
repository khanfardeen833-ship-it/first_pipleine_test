"""
Procedural SVG motif engine — generates decorative full-bleed background
graphics (plexus, dot-grid, hexagons, waves, flow-lines) as pure SVG.

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


_GENERATORS = {
    "plexus": _plexus,
    "dot_grid": _dot_grid,
    "hexagons": _hexagons,
    "waves": _waves,
    "flow": _flow,
}
MOTIF_TYPES = tuple(_GENERATORS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_motif(type="plexus", *, width=1280, height=720, palette="green_tech",
                   density=0.7, glow=0.8, safe_area=None, seed=0):
    """Return a full-bleed SVG string for one motif.

    type      : plexus | dot_grid | hexagons | waves | flow
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
