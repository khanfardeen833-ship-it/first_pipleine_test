import json
import time

NOW = int(time.time() * 1000)
CREATED_AT = "2026-05-25T00:00:00.000Z"

# ---------- color palette ----------
BG_DARK = "#0B1020"
BG_GRAPHITE = "#1E293B"
BG_PAPER = "#F8FAFC"
INK = "#1E293B"
DATA_BLUE = "#2563EB"
CYAN = "#06B6D4"
VIOLET = "#7C3AED"
GREEN = "#22C55E"
AMBER = "#F59E0B"
RED = "#EF4444"
PAPER = "#F8FAFC"
GRID = "#CBD5E1"
MUTED = "#64748b"
DIM = "#94a3b8"

COUNTER = 0
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- builders ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color=INK, font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Inter",
              text_transform="none", font_style="normal"):
    DEFAULTS = {
        "title":      (60, 700, 1.05),
        "subtitle":   (40, 600, 1.35),
        "heading":    (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph":  (22, 700, 1.50),
        "caption":    (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None:   fs = font_size
    if font_weight is not None: fw = font_weight
    if line_height is not None: lh = line_height
    content_record = {
        "id": text_id, "content": text, "type": type_,
        "originalType": type_, "groupId": None, "formattedContent": text
    }
    changelog_record = {
        "slideId": slide_id, "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0, "zIndex": zidx,
        "style": {
            "fontSize": fs, "fontFamily": font_family, "color": color,
            "textAlign": text_align, "lineHeight": lh, "letterSpacing": letter_spacing,
            "fontWeight": fw, "fontStyle": font_style, "textDecoration": "none",
            "textTransform": text_transform, "isCode": False, "listStyle": "none",
            "link": "", "backgroundColor": "transparent", "background": "none",
            "WebkitBackgroundClip": "unset", "WebkitTextFillColor": "unset",
            "backgroundClip": "unset", "listLevel": 1,
            "paragraphSpacingBefore": 0, "paragraphSpacingAfter": 0,
            "textOutlineColor": "#000000", "textOutlineWidth": 0,
            "textTransformEffect": "none", "textTransformRadius": 220,
            "textVerticalAlign": "baseline", "curveEnabled": False,
            "curveValue": 26, "shadowType": "none", "shadowOffset": 22,
            "shadowDirection": -45, "shadowBlur": 0,
            "shadowTransparency": 40, "shadowColor": "#000000"
        },
        "formattedContent": text,
        "animation": {"enter": "none", "exit": "fade", "duration": 550,
                      "delay": 0, "trigger": "both", "typewriterMode": "character"},
        "enterAnimation": "none", "exitAnimation": "fade",
        "animationEffect": "none", "animationDurationMs": 550,
        "animationDelayMs": 0, "animationTrigger": "both",
        "animationTypewriterMode": "character", "updatedAt": now
    }
    return content_record, changelog_record

def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx, now,
               fill=DATA_BLUE, stroke=None, stroke_width=0, opacity=1, rotation=0):
    if stroke is None:
        stroke = fill
    content = {"id": shape_id, "slideId": slide_id, "groupId": None}
    cl = {
        "slideId": slide_id, "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": rotation,
        "zIndex": zidx, "opacity": opacity,
        "shapeType": shape_type, "fill": fill, "stroke": stroke,
        "strokeWidth": stroke_width, "updatedAt": now
    }
    return content, cl

def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=64, color=DATA_BLUE, opacity=1):
    content = {"id": icon_id, "slideId": slide_id, "groupId": None,
               "iconName": icon_name, "iconSource": "lucide"}
    cl = {
        "slideId": slide_id, "position": {"x": x, "y": y},
        "width": size, "height": size, "rotation": 0,
        "zIndex": zidx, "color": color, "opacity": opacity,
        "updatedAt": now
    }
    return content, cl

def make_chart(chart_id, slide_id, chart_type, x, y, w, h, zidx, now, chart_config):
    content = {"id": chart_id, "slideId": slide_id, "groupId": None,
               "svgDataUrl": "", "chartType": chart_type, "chartConfig": chart_config}
    cl = {
        "slideId": slide_id, "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "updatedAt": now, "chartType": chart_type
    }
    return content, cl

# ---------- registries ----------
SLIDE_IDS = [f"slide-{i+1}" for i in range(5)]
text_by_slide = {sid: [] for sid in SLIDE_IDS}
all_shapes = []
all_icons = []
all_charts = []
all_images = []
all_tables = []
changelog_slides = {sid: {"elements": {}} for sid in SLIDE_IDS}

def add_text(slide_id, text, type_, x, y, w, h, **kw):
    n = next_id(); tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kw)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

def add_shape(slide_id, shape_type, x, y, w, h, **kw):
    n = next_id(); sid_ = f"shape-{n}"
    c, cl = make_shape(sid_, slide_id, shape_type, x, y, w, h, n, NOW, **kw)
    all_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid_] = cl

def add_icon(slide_id, icon_name, x, y, **kw):
    n = next_id(); iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kw)
    all_icons.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

def add_chart(slide_id, chart_type, x, y, w, h, cfg):
    n = next_id(); cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, NOW, cfg)
    all_charts.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl


# ============================================================
# SLIDE 1 — The Hidden Geometry of Data (cinematic hero)
# ============================================================
sid = "slide-1"

# Decorative constellation of data points
points = [
    (160, 100, 6, CYAN, 0.65),
    (220, 150, 4, CYAN, 0.45),
    (300, 88, 9, VIOLET, 0.85),
    (380, 178, 5, CYAN, 0.55),
    (460, 112, 7, DATA_BLUE, 0.7),
    (540, 198, 4, CYAN, 0.4),
    (620, 78, 6, VIOLET, 0.6),
    (740, 160, 5, CYAN, 0.5),
    (820, 100, 8, DATA_BLUE, 0.8),
    (900, 190, 4, CYAN, 0.5),
    (980, 120, 6, VIOLET, 0.7),
    (1080, 92, 5, CYAN, 0.55),
    (1140, 180, 7, DATA_BLUE, 0.6),
    (140, 540, 5, CYAN, 0.5),
    (240, 600, 7, VIOLET, 0.7),
    (340, 560, 4, CYAN, 0.4),
    (440, 620, 6, DATA_BLUE, 0.6),
    (560, 580, 5, CYAN, 0.5),
    (660, 640, 8, VIOLET, 0.8),
    (760, 600, 4, CYAN, 0.4),
    (860, 560, 6, DATA_BLUE, 0.7),
    (960, 622, 5, CYAN, 0.5),
    (1060, 580, 7, VIOLET, 0.7),
    (1160, 540, 5, CYAN, 0.6),
    (80, 320, 4, CYAN, 0.4),
    (1180, 380, 5, VIOLET, 0.5),
    (1100, 280, 6, DATA_BLUE, 0.5),
    (96, 470, 5, CYAN, 0.45),
]
for px, py, sz, col, op in points:
    add_shape(sid, "circle", px, py, sz, sz, fill=col, opacity=op)

# Faint connection arcs (very subtle)
add_shape(sid, "line", 300, 92, 160, 90, fill=CYAN, stroke=CYAN, stroke_width=1, opacity=0.18)
add_shape(sid, "line", 820, 108, 160, 80, fill=VIOLET, stroke=VIOLET, stroke_width=1, opacity=0.15)
add_shape(sid, "line", 240, 600, 200, 40, fill=CYAN, stroke=CYAN, stroke_width=1, opacity=0.18)

# Chapter mark / brand caption
add_text(sid, "01 / 15", "caption", 80, 56, 200, 22,
         color=DIM, font_size=12, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=3, text_transform="uppercase")
add_text(sid, "DATA SCIENCE FUNDAMENTALS", "caption", 808, 56, 400, 22,
         color=DIM, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=4,
         text_align="right", text_transform="uppercase")

# Hairline above title
add_shape(sid, "rectangle", 580, 264, 120, 1, fill=CYAN, opacity=0.55)

# Title
add_text(sid, "The Hidden Geometry of Data", "title", 80, 288, 1120, 100,
         color=PAPER, font_size=82, font_weight=600, line_height=1.05,
         font_family="Playfair Display", text_align="center", letter_spacing=-1)

# Subtitle
add_text(sid, "Statistics  •  Probability  •  Models  •  Decisions", "subtitle", 80, 408, 1120, 32,
         color=CYAN, font_size=16, font_weight=500,
         font_family="Inter", text_align="center", letter_spacing=6,
         text_transform="uppercase")

# Bottom rule + chapter caption
add_shape(sid, "rectangle", 580, 638, 120, 1, fill=GRID, opacity=0.4)
add_text(sid, "A CINEMATIC PRIMER  /  CHAPTER ONE", "caption", 80, 656, 1120, 18,
         color=MUTED, font_size=11, font_weight=600,
         font_family="JetBrains Mono", text_align="center", letter_spacing=4,
         text_transform="uppercase")

# Floating mathematical annotations (mono)
add_text(sid, "μ = 0.42", "caption", 96, 220, 120, 16,
         color="#475569", font_size=11, font_weight=400, font_family="JetBrains Mono")
add_text(sid, "σ² = 1.28", "caption", 1040, 220, 140, 16,
         color="#475569", font_size=11, font_weight=400,
         font_family="JetBrains Mono", text_align="right")
add_text(sid, "P(X | θ)", "caption", 96, 500, 120, 16,
         color="#475569", font_size=11, font_weight=400, font_family="JetBrains Mono")
add_text(sid, "ŷ = β₀ + β₁x", "caption", 1024, 500, 156, 16,
         color="#475569", font_size=11, font_weight=400,
         font_family="JetBrains Mono", text_align="right")


# ============================================================
# SLIDE 2 — Data Science as a Decision Engine (editorial light)
# ============================================================
sid = "slide-2"

# Subtle paper grid line (top)
add_shape(sid, "rectangle", 80, 102, 1120, 1, fill=GRID, opacity=0.6)

# Top eyebrow
add_text(sid, "02 / PIPELINE", "caption", 80, 60, 300, 18,
         color=DATA_BLUE, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "FROM SIGNAL  →  STRATEGY", "caption", 800, 60, 400, 18,
         color=MUTED, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=4,
         text_align="right", text_transform="uppercase")

# Headline
add_text(sid, "Data Science as a Decision Engine", "title", 80, 128, 900, 64,
         color=INK, font_size=48, font_weight=700, line_height=1.1,
         font_family="Inter Tight", letter_spacing=-1)

# Subhead / lede
add_text(sid,
         "Every dataset is a pipeline that turns observation into action — through statistics, probability, modeling, and disciplined evaluation.",
         "paragraph", 80, 208, 760, 56,
         color="#475569", font_size=18, font_weight=400, line_height=1.5,
         font_family="Inter")

# Pipeline (5 stages, horizontally arranged)
stages = [
    ("01", "RAW DATA",    "Tables, logs, signals",         DATA_BLUE),
    ("02", "STATISTICS",  "Center, spread, shape",         CYAN),
    ("03", "PROBABILITY", "Likelihood & uncertainty",      VIOLET),
    ("04", "MODEL",       "Regression, classification",    GREEN),
    ("05", "DECISION",    "Action grounded in evidence",   AMBER),
]

card_w = 168
card_h = 168
gap = 24
total_w = 5 * card_w + 4 * gap
start_x = (1280 - total_w) // 2  # center
start_y = 320

for i, (num, label, sub, accent) in enumerate(stages):
    cx = start_x + i * (card_w + gap)
    # card background
    add_shape(sid, "rectangle", cx, start_y, card_w, card_h, fill="#ffffff", opacity=1, stroke=GRID, stroke_width=1)
    # accent bar at top
    add_shape(sid, "rectangle", cx, start_y, card_w, 4, fill=accent, opacity=1)
    # number
    add_text(sid, num, "caption", cx + 18, start_y + 18, 60, 16,
             color=accent, font_size=11, font_weight=700,
             font_family="JetBrains Mono", letter_spacing=2)
    # label
    add_text(sid, label, "heading", cx + 18, start_y + 60, card_w - 36, 32,
             color=INK, font_size=18, font_weight=700,
             font_family="Inter Tight", letter_spacing=0.5, text_transform="uppercase")
    # sublabel
    add_text(sid, sub, "caption", cx + 18, start_y + 100, card_w - 36, 50,
             color="#475569", font_size=13, font_weight=400, line_height=1.4,
             font_family="Inter")
    # connector arrow between cards
    if i < 4:
        ax = cx + card_w + 4
        ay = start_y + card_h // 2 - 1
        add_shape(sid, "rectangle", ax, ay, gap - 8, 2, fill=GRID, opacity=1)
        add_shape(sid, "triangle", ax + gap - 12, ay - 5, 8, 12, fill=GRID, opacity=1, rotation=90)

# Example panel (bottom)
ex_x, ex_y, ex_w, ex_h = 80, 540, 1120, 116
add_shape(sid, "rectangle", ex_x, ex_y, ex_w, ex_h, fill=BG_DARK, opacity=1)
add_shape(sid, "rectangle", ex_x, ex_y, 4, ex_h, fill=AMBER, opacity=1)

add_text(sid, "APPLIED EXAMPLE", "caption", ex_x + 28, ex_y + 22, 240, 16,
         color=AMBER, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid,
         "Predicting customer churn from behavioral signals",
         "subheading", ex_x + 28, ex_y + 46, 700, 32,
         color=PAPER, font_size=22, font_weight=600,
         font_family="Inter Tight")
add_text(sid,
         "Sessions, recency, plan tier, support tickets  →  P(churn | X) ∈ [0,1]",
         "caption", ex_x + 28, ex_y + 80, 800, 18,
         color="#94a3b8", font_size=13, font_weight=400, font_family="JetBrains Mono")
# right-side stat
add_text(sid, "0.87", "title", ex_x + ex_w - 200, ex_y + 24, 168, 60,
         color=AMBER, font_size=52, font_weight=700,
         font_family="Inter Tight", text_align="right")
add_text(sid, "ROC-AUC", "caption", ex_x + ex_w - 200, ex_y + 86, 168, 16,
         color=DIM, font_size=11, font_weight=600,
         font_family="JetBrains Mono", text_align="right", letter_spacing=3,
         text_transform="uppercase")


# ============================================================
# SLIDE 3 — Statistics: Turning Noise into Signal
# ============================================================
sid = "slide-3"

# Eyebrow
add_text(sid, "03 / STATISTICS", "caption", 80, 60, 300, 18,
         color=DATA_BLUE, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "CENTER · SPREAD · SHAPE", "caption", 800, 60, 400, 18,
         color=MUTED, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=4,
         text_align="right", text_transform="uppercase")

add_shape(sid, "rectangle", 80, 102, 1120, 1, fill=GRID, opacity=0.6)

# Title
add_text(sid, "Turning Noise into Signal", "title", 80, 128, 1120, 64,
         color=INK, font_size=48, font_weight=700, line_height=1.1,
         font_family="Playfair Display", font_style="normal", letter_spacing=-1)

# Lede
add_text(sid,
         "Three lenses describe any distribution: where it sits, how far it spreads, and how it leans.",
         "paragraph", 80, 196, 900, 28,
         color="#475569", font_size=18, font_weight=400, line_height=1.5,
         font_family="Inter")

# Three panels
panel_y = 252
panel_h = 340
panels = [
    {"x": 80,  "w": 360, "title": "CENTER",  "sub": "Mean & median",  "accent": DATA_BLUE,
     "formula": "x̄ = Σxᵢ / n",
     "note": "Where the data lives. Mean follows arithmetic; median resists outliers."},
    {"x": 460, "w": 360, "title": "SPREAD",  "sub": "Variance & σ",   "accent": CYAN,
     "formula": "σ² = Σ(xᵢ - x̄)² / n",
     "note": "How tightly observations cluster. Standard deviation scales with the data."},
    {"x": 840, "w": 360, "title": "SHAPE",   "sub": "Skew & kurtosis", "accent": VIOLET,
     "formula": "γ₁ = E[(X-μ)³] / σ³",
     "note": "Symmetry vs. lean. A long right tail signals rare-but-large events."},
]
for p in panels:
    px, pw = p["x"], p["w"]
    # card
    add_shape(sid, "rectangle", px, panel_y, pw, panel_h, fill="#ffffff", stroke=GRID, stroke_width=1)
    # accent
    add_shape(sid, "rectangle", px, panel_y, 4, panel_h, fill=p["accent"])
    # eyebrow
    add_text(sid, p["title"], "caption", px + 24, panel_y + 22, pw - 48, 16,
             color=p["accent"], font_size=11, font_weight=700,
             font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
    # subhead
    add_text(sid, p["sub"], "subheading", px + 24, panel_y + 46, pw - 48, 28,
             color=INK, font_size=22, font_weight=700,
             font_family="Inter Tight")
    # formula card
    add_shape(sid, "rectangle", px + 24, panel_y + 86, pw - 48, 36, fill=BG_PAPER)
    add_text(sid, p["formula"], "caption", px + 36, panel_y + 92, pw - 72, 24,
             color=INK, font_size=15, font_weight=500,
             font_family="JetBrains Mono")

# Visual: CENTER (dot plot) - panel 1
dp_y = panel_y + 152
dp_x = 100
dot_xs = [12, 38, 60, 82, 92, 116, 142, 156, 178, 202, 224, 246, 268, 286, 308]
for dx in dot_xs:
    add_shape(sid, "circle", dp_x + dx, dp_y, 8, 8, fill=DATA_BLUE, opacity=0.7)
# axis
add_shape(sid, "rectangle", dp_x, dp_y + 28, 320, 1, fill=GRID, opacity=1)
# mean line
add_shape(sid, "rectangle", dp_x + 158, dp_y - 20, 2, 56, fill=AMBER, opacity=1)
add_text(sid, "x̄", "caption", dp_x + 148, dp_y - 38, 24, 16,
         color=AMBER, font_size=13, font_weight=700, font_family="JetBrains Mono")
add_text(sid, panels[0]["note"], "caption", 104, panel_y + 240, 312, 60,
         color="#475569", font_size=13, font_weight=400, line_height=1.5,
         font_family="Inter")

# Visual: SPREAD (histogram bars) - panel 2
hp_x = 484
hp_y_base = panel_y + 200
heights = [8, 16, 28, 44, 64, 80, 84, 76, 56, 40, 24, 14, 8]
bar_w = 18
gap_b = 4
for i, hh in enumerate(heights):
    bx = hp_x + i * (bar_w + gap_b)
    add_shape(sid, "rectangle", bx, hp_y_base - hh, bar_w, hh, fill=CYAN, opacity=0.85)
add_shape(sid, "rectangle", hp_x, hp_y_base + 1, len(heights) * (bar_w + gap_b) - gap_b, 1, fill=GRID)
# variance band markers
add_shape(sid, "rectangle", hp_x + 88, hp_y_base - 90, 2, 96, fill=AMBER, opacity=0.7)
add_shape(sid, "rectangle", hp_x + 198, hp_y_base - 90, 2, 96, fill=AMBER, opacity=0.7)
add_text(sid, "−σ", "caption", hp_x + 76, hp_y_base + 6, 24, 16,
         color=AMBER, font_size=11, font_weight=600, font_family="JetBrains Mono")
add_text(sid, "+σ", "caption", hp_x + 188, hp_y_base + 6, 24, 16,
         color=AMBER, font_size=11, font_weight=600, font_family="JetBrains Mono")
add_text(sid, panels[1]["note"], "caption", 484, panel_y + 240, 312, 60,
         color="#475569", font_size=13, font_weight=400, line_height=1.5,
         font_family="Inter")

# Visual: SHAPE (skewed histogram) - panel 3
sk_x = 864
sk_y_base = panel_y + 200
sk_heights = [22, 64, 88, 80, 64, 50, 40, 30, 22, 18, 14, 10, 6]
for i, hh in enumerate(sk_heights):
    bx = sk_x + i * (bar_w + gap_b)
    col = VIOLET if i < 4 else (VIOLET if i < 8 else "#a78bfa")
    op = 0.95 if i < 4 else 0.7
    add_shape(sid, "rectangle", bx, sk_y_base - hh, bar_w, hh, fill=col, opacity=op)
add_shape(sid, "rectangle", sk_x, sk_y_base + 1, len(sk_heights) * (bar_w + gap_b) - gap_b, 1, fill=GRID)
# tail callout
add_shape(sid, "circle", sk_x + 240, sk_y_base - 12, 6, 6, fill=RED, opacity=0.9)
add_text(sid, "long tail", "caption", sk_x + 232, sk_y_base - 36, 80, 14,
         color=RED, font_size=10, font_weight=600, font_family="JetBrains Mono")
add_text(sid, panels[2]["note"], "caption", 864, panel_y + 240, 312, 60,
         color="#475569", font_size=13, font_weight=400, line_height=1.5,
         font_family="Inter")

# Bottom example ribbon
rib_y = 612
add_shape(sid, "rectangle", 80, rib_y, 1120, 60, fill=BG_DARK)
add_shape(sid, "rectangle", 80, rib_y, 4, 60, fill=DATA_BLUE)
add_text(sid, "EXAMPLE", "caption", 108, rib_y + 22, 120, 16,
         color=DATA_BLUE, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "Daily app session duration —  median 4.2 min,  σ = 6.8 min,  right-skewed by power users.",
         "caption", 240, rib_y + 22, 940, 16,
         color=PAPER, font_size=14, font_weight=400, font_family="Inter")


# ============================================================
# SLIDE 4 — The Shape of Uncertainty (cinematic dark)
# ============================================================
sid = "slide-4"

# Eyebrow
add_text(sid, "04 / DISTRIBUTION", "caption", 80, 60, 300, 18,
         color=CYAN, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "THE NORMAL CURVE", "caption", 800, 60, 400, 18,
         color=DIM, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=4,
         text_align="right", text_transform="uppercase")
add_shape(sid, "rectangle", 80, 102, 1120, 1, fill="#334155", opacity=1)

# Title
add_text(sid, "The Shape of Uncertainty", "title", 80, 128, 900, 80,
         color=PAPER, font_size=64, font_weight=600, line_height=1.05,
         font_family="Playfair Display", letter_spacing=-1)

# Narrative caption (left)
add_text(sid,
         "Order hides inside noise. The normal distribution lets us reason about what is typical, what is rare, and how confident any single estimate truly is.",
         "paragraph", 80, 232, 460, 120,
         color="#cbd5e1", font_size=18, font_weight=400, line_height=1.55,
         font_family="Inter")

# Inline equation card
add_shape(sid, "rectangle", 80, 372, 460, 56, fill="#111a36", stroke=CYAN, stroke_width=1, opacity=1)
add_text(sid, "f(x) = (1 / σ√2π) · e^(−(x−μ)² / 2σ²)", "caption", 96, 388, 432, 24,
         color=CYAN, font_size=14, font_weight=500,
         font_family="JetBrains Mono")

# Real-world micro-label
add_text(sid, "DELIVERY TIMES — TYPICAL DAY",
         "caption", 80, 448, 460, 16,
         color="#94a3b8", font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=3, text_transform="uppercase")

# Bell curve chart (right)
chart_cfg = {
    "tooltip": {"trigger": "item"},
    "xAxis": {
        "type": "category",
        "data": ["−3σ", "−2σ", "−σ", "μ", "+σ", "+2σ", "+3σ"],
        "axisLine": {"lineStyle": {"color": "#475569"}},
        "axisLabel": {"color": "#94a3b8", "fontSize": 12}
    },
    "yAxis": {
        "type": "value",
        "axisLine": {"show": False},
        "axisLabel": {"show": False},
        "splitLine": {"lineStyle": {"color": "#1e293b"}}
    },
    "series": [{
        "type": "line",
        "data": [0.4, 5.4, 24.2, 39.9, 24.2, 5.4, 0.4],
        "smooth": True,
        "symbol": "circle",
        "symbolSize": 6,
        "lineStyle": {"color": CYAN, "width": 3},
        "itemStyle": {"color": CYAN},
        "areaStyle": {"color": CYAN, "opacity": 0.18}
    }],
    "backgroundColor": "transparent",
    "color": [CYAN],
    "animation": False,
    "textStyle": {"color": "#cbd5e1", "fontSize": 14, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["−3σ", "−2σ", "−σ", "μ", "+σ", "+2σ", "+3σ"],
        "series": [{"name": "Density", "data": [0.4, 5.4, 24.2, 39.9, 24.2, 5.4, 0.4]}]
    },
    "properties": {
        "showXAxis": True, "showYAxis": False, "showDataLabels": False,
        "showLegend": False, "showLabelName": True, "showLabelValue": False,
        "labelFontSize": 12, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None,
    "isDarkMode": True,
    "customSeriesColors": {"0": CYAN},
    "textColor": "#cbd5e1",
    "isMonochrome": False
}
add_chart(sid, "line", 580, 220, 620, 280, chart_cfg)

# Mean marker on top of chart
add_shape(sid, "rectangle", 884, 232, 2, 240, fill=AMBER, opacity=0.7)
add_text(sid, "μ", "caption", 876, 212, 24, 18,
         color=AMBER, font_size=14, font_weight=700, font_family="JetBrains Mono")

# Four inset metric cards (bottom)
metrics = [
    ("MEAN",       "μ",   "Center of mass",        DATA_BLUE),
    ("MEDIAN",     "x̃",   "Middle observation",    CYAN),
    ("VARIANCE",   "σ²",  "Average squared spread", VIOLET),
    ("STD DEV",    "σ",   "Spread in real units",   AMBER),
]
m_y = 540
m_w = 264
m_gap = 24
m_start = (1280 - 4 * m_w - 3 * m_gap) // 2
m_h = 132
for i, (label, sym, sub, col) in enumerate(metrics):
    mx = m_start + i * (m_w + m_gap)
    add_shape(sid, "rectangle", mx, m_y, m_w, m_h, fill="#111a36", stroke="#1e293b", stroke_width=1)
    add_shape(sid, "rectangle", mx, m_y, m_w, 3, fill=col)
    add_text(sid, label, "caption", mx + 20, m_y + 18, m_w - 40, 14,
             color=col, font_size=10, font_weight=700,
             font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
    add_text(sid, sym, "title", mx + 20, m_y + 38, m_w - 40, 56,
             color=PAPER, font_size=44, font_weight=600,
             font_family="Playfair Display")
    add_text(sid, sub, "caption", mx + 20, m_y + 100, m_w - 40, 16,
             color="#94a3b8", font_size=12, font_weight=400, font_family="Inter")

# Footer caption
add_text(sid, "1σ ≈ 68%   •   2σ ≈ 95%   •   3σ ≈ 99.7%",
         "caption", 80, 686, 1120, 16,
         color="#64748b", font_size=11, font_weight=600,
         font_family="JetBrains Mono", text_align="center", letter_spacing=4, text_transform="uppercase")


# ============================================================
# SLIDE 5 — Probability: The Language of Possibility
# ============================================================
sid = "slide-5"

# Eyebrow
add_text(sid, "05 / PROBABILITY", "caption", 80, 60, 300, 18,
         color=VIOLET, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "CONDITIONAL · BAYESIAN", "caption", 800, 60, 400, 18,
         color="#94a3b8", font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=4,
         text_align="right", text_transform="uppercase")
add_shape(sid, "rectangle", 80, 102, 1120, 1, fill="#334155", opacity=1)

# Title
add_text(sid, "The Language of Possibility", "title", 80, 128, 1000, 80,
         color=PAPER, font_size=58, font_weight=600, line_height=1.05,
         font_family="Playfair Display", letter_spacing=-1)

# Subline
add_text(sid,
         "Probability is how a model speaks about the future when it cannot speak with certainty.",
         "paragraph", 80, 220, 760, 28,
         color="#cbd5e1", font_size=18, font_weight=400, line_height=1.5,
         font_family="Inter")

# ----- LEFT: probability tree -----
# Tree spans roughly x: 80–660, y: 280–620
tree_left = 80
tree_top = 280

# Node positions (cx, cy)
root = (tree_left + 40, 440)
mid_up = (tree_left + 240, 340)
mid_dn = (tree_left + 240, 540)
leaf_uu = (tree_left + 480, 300)   # mobile + click
leaf_ud = (tree_left + 480, 380)   # mobile + no click
leaf_du = (tree_left + 480, 500)   # desktop + click
leaf_dd = (tree_left + 480, 580)   # desktop + no click

# Connector lines (using line shape — bbox from corner-to-corner)
def connector(slide, p1, p2, color=VIOLET, opacity=0.7):
    x = min(p1[0], p2[0])
    y = min(p1[1], p2[1])
    w = max(abs(p2[0] - p1[0]), 2)
    h = max(abs(p2[1] - p1[1]), 2)
    # use thin rectangle rotated for tilt — approximate via line shape
    add_shape(slide, "line", x, y, w, h, fill=color, stroke=color, stroke_width=2, opacity=opacity)

connector(sid, root, mid_up, color=VIOLET, opacity=0.55)
connector(sid, root, mid_dn, color=VIOLET, opacity=0.55)
connector(sid, mid_up, leaf_uu, color=CYAN, opacity=0.55)
connector(sid, mid_up, leaf_ud, color="#475569", opacity=0.4)
connector(sid, mid_dn, leaf_du, color=CYAN, opacity=0.55)
connector(sid, mid_dn, leaf_dd, color="#475569", opacity=0.4)

# Nodes (circles)
def node(slide, cxcy, r, fill, stroke=None, stroke_width=2):
    cx, cy = cxcy
    add_shape(slide, "circle", cx - r, cy - r, r * 2, r * 2, fill=fill,
              stroke=stroke if stroke else fill, stroke_width=stroke_width)

node(sid, root,    20, "#0B1020", stroke=VIOLET, stroke_width=2)
node(sid, mid_up,  16, "#0B1020", stroke=VIOLET, stroke_width=2)
node(sid, mid_dn,  16, "#0B1020", stroke=VIOLET, stroke_width=2)
node(sid, leaf_uu, 12, CYAN, stroke=CYAN, stroke_width=0)
node(sid, leaf_ud, 12, "#475569", stroke="#475569", stroke_width=0)
node(sid, leaf_du, 12, CYAN, stroke=CYAN, stroke_width=0)
node(sid, leaf_dd, 12, "#475569", stroke="#475569", stroke_width=0)

# Node labels
add_text(sid, "USER", "caption", root[0] - 60, root[1] + 32, 120, 16,
         color=PAPER, font_size=11, font_weight=700,
         font_family="JetBrains Mono", text_align="center", letter_spacing=2)

add_text(sid, "MOBILE", "caption", mid_up[0] - 60, mid_up[1] - 38, 120, 14,
         color=PAPER, font_size=11, font_weight=700,
         font_family="JetBrains Mono", text_align="center", letter_spacing=2)
add_text(sid, "P = 0.62", "caption", mid_up[0] - 60, mid_up[1] + 24, 120, 14,
         color="#94a3b8", font_size=11, font_weight=400,
         font_family="JetBrains Mono", text_align="center")

add_text(sid, "DESKTOP", "caption", mid_dn[0] - 60, mid_dn[1] - 38, 120, 14,
         color=PAPER, font_size=11, font_weight=700,
         font_family="JetBrains Mono", text_align="center", letter_spacing=2)
add_text(sid, "P = 0.38", "caption", mid_dn[0] - 60, mid_dn[1] + 24, 120, 14,
         color="#94a3b8", font_size=11, font_weight=400,
         font_family="JetBrains Mono", text_align="center")

# Leaf labels
add_text(sid, "CLICK", "caption", leaf_uu[0] + 20, leaf_uu[1] - 16, 80, 14,
         color=CYAN, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "P = 0.32", "caption", leaf_uu[0] + 20, leaf_uu[1] + 2, 100, 14,
         color="#cbd5e1", font_size=11, font_weight=400,
         font_family="JetBrains Mono")

add_text(sid, "NO CLICK", "caption", leaf_ud[0] + 20, leaf_ud[1] - 16, 100, 14,
         color="#94a3b8", font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "P = 0.68", "caption", leaf_ud[0] + 20, leaf_ud[1] + 2, 100, 14,
         color="#94a3b8", font_size=11, font_weight=400,
         font_family="JetBrains Mono")

add_text(sid, "CLICK", "caption", leaf_du[0] + 20, leaf_du[1] - 16, 80, 14,
         color=CYAN, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "P = 0.18", "caption", leaf_du[0] + 20, leaf_du[1] + 2, 100, 14,
         color="#cbd5e1", font_size=11, font_weight=400,
         font_family="JetBrains Mono")

add_text(sid, "NO CLICK", "caption", leaf_dd[0] + 20, leaf_dd[1] - 16, 100, 14,
         color="#94a3b8", font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "P = 0.82", "caption", leaf_dd[0] + 20, leaf_dd[1] + 2, 100, 14,
         color="#94a3b8", font_size=11, font_weight=400,
         font_family="JetBrains Mono")

# Tree caption
add_text(sid, "WILL A USER CLICK?", "caption", 80, 632, 580, 16,
         color=VIOLET, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "Branching probabilities by device — joint events live at the leaves.",
         "caption", 80, 654, 580, 16,
         color="#94a3b8", font_size=12, font_weight=400, font_family="Inter")

# ----- RIGHT: Bayes formula card + comparison -----
right_x = 720
# Bayes card
add_shape(sid, "rectangle", right_x, 280, 480, 168, fill="#111a36", stroke=VIOLET, stroke_width=1)
add_shape(sid, "rectangle", right_x, 280, 480, 3, fill=VIOLET)
add_text(sid, "BAYES' RULE", "caption", right_x + 24, 296, 280, 16,
         color=VIOLET, font_size=11, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=4, text_transform="uppercase")
add_text(sid, "P(A | B) = P(B | A) · P(A) / P(B)",
         "subheading", right_x + 24, 322, 432, 32,
         color=PAPER, font_size=22, font_weight=500,
         font_family="JetBrains Mono")
add_text(sid,
         "Update belief A given new evidence B — the engine of every probabilistic model.",
         "caption", right_x + 24, 376, 432, 56,
         color="#cbd5e1", font_size=14, font_weight=400, line_height=1.5,
         font_family="Inter")

# Two comparison cards
cmp_y = 472
cmp_w = 232
cmp_h = 156
# Card A — joint
add_shape(sid, "rectangle", right_x, cmp_y, cmp_w, cmp_h, fill="#111a36", stroke="#1e293b", stroke_width=1)
add_shape(sid, "rectangle", right_x, cmp_y, cmp_w, 3, fill=CYAN)
add_text(sid, "JOINT", "caption", right_x + 18, cmp_y + 16, cmp_w - 36, 14,
         color=CYAN, font_size=10, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=3, text_transform="uppercase")
add_text(sid, "P(Mobile ∩ Click)", "caption", right_x + 18, cmp_y + 36, cmp_w - 36, 18,
         color=PAPER, font_size=14, font_weight=600, font_family="JetBrains Mono")
add_text(sid, "0.198", "title", right_x + 18, cmp_y + 60, cmp_w - 36, 48,
         color=CYAN, font_size=36, font_weight=700, font_family="Inter Tight")
add_text(sid, "= 0.62 × 0.32", "caption", right_x + 18, cmp_y + 116, cmp_w - 36, 14,
         color="#94a3b8", font_size=12, font_weight=400, font_family="JetBrains Mono")

# Card B — conditional
cmp_x2 = right_x + cmp_w + 16
add_shape(sid, "rectangle", cmp_x2, cmp_y, cmp_w, cmp_h, fill="#111a36", stroke="#1e293b", stroke_width=1)
add_shape(sid, "rectangle", cmp_x2, cmp_y, cmp_w, 3, fill=AMBER)
add_text(sid, "CONDITIONAL", "caption", cmp_x2 + 18, cmp_y + 16, cmp_w - 36, 14,
         color=AMBER, font_size=10, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=3, text_transform="uppercase")
add_text(sid, "P(Click | Mobile)", "caption", cmp_x2 + 18, cmp_y + 36, cmp_w - 36, 18,
         color=PAPER, font_size=14, font_weight=600, font_family="JetBrains Mono")
add_text(sid, "0.32", "title", cmp_x2 + 18, cmp_y + 60, cmp_w - 36, 48,
         color=AMBER, font_size=36, font_weight=700, font_family="Inter Tight")
add_text(sid, "≈ 1.78× desktop", "caption", cmp_x2 + 18, cmp_y + 116, cmp_w - 36, 14,
         color="#94a3b8", font_size=12, font_weight=400, font_family="JetBrains Mono")

# Pull quote at bottom right
add_text(sid, "“ Probability is the calculus of careful guessing. ”",
         "caption", right_x, 644, 480, 22,
         color="#cbd5e1", font_size=14, font_weight=400, line_height=1.4,
         font_family="Playfair Display", font_style="normal", text_align="left")


# ============================================================
# ASSEMBLE FILES
# ============================================================
slide_bg = {
    "slide-1": BG_DARK,
    "slide-2": BG_PAPER,
    "slide-3": BG_PAPER,
    "slide-4": BG_DARK,
    "slide-5": BG_GRAPHITE,
}

content_slides = []
base_slides = []
for i, sid_ in enumerate(SLIDE_IDS):
    content_slides.append({
        "id": sid_,
        "order": i,
        "layoutId": "blank-canvas",
        "backgroundColor": slide_bg[sid_],
        "textElements": text_by_slide[sid_]
    })
    base_slides.append({
        "id": sid_,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    })

content = {
    "slides": content_slides,
    "imageElements": all_images,
    "shapeElements": all_shapes,
    "chartElements": all_charts,
    "tableElements": all_tables,
    "iconElements": all_icons,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

base_layout = {
    "version": "v1",
    "slides": base_slides,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

changelog = {
    "version": "2.0",
    "slides": changelog_slides
}

# ----- counts -----
total_text = sum(len(v) for v in text_by_slide.values())
total_elements = (
    total_text + len(all_images) + len(all_shapes) +
    len(all_charts) + len(all_tables) + len(all_icons)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch1-{NOW}",
        "title": "Data Science Fundamentals",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": total_elements,
        "createdAt": CREATED_AT,
        "updatedAt": CREATED_AT,
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": base_layout,
        "changelog": changelog
    }
}

OUT = "deck.json"
with open(OUT, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"WROTE {OUT}")
print(f"slides: 5")
print(f"elements: {total_elements}")
print(f"  text: {total_text}")
print(f"  shapes: {len(all_shapes)}")
print(f"  charts: {len(all_charts)}")
print(f"  icons: {len(all_icons)}")
print(f"  images: {len(all_images)}")
