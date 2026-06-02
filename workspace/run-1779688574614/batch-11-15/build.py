import json
import time
import os

NOW = int(time.time() * 1000)

# ---------- ID + zIndex counters ----------
COUNTER = 600  # first element will be 601

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#D8DEE9", font_size=None, font_weight=None, line_height=None,
              font_family="Inter", text_align="left", letter_spacing=0,
              font_style="normal", text_transform="none"):
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
        "slideId": slide_id,
        "position": {"x": x, "y": y},
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
               fill="#151B2E", stroke=None, stroke_width=0, opacity=1):
    if stroke is None:
        stroke = fill
    content_record = {
        "id": shape_id, "slideId": slide_id, "groupId": None
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "opacity": opacity,
        "shapeType": shape_type,
        "fill": fill, "stroke": stroke, "strokeWidth": stroke_width,
        "updatedAt": now
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=48, color="#00D4FF", opacity=1):
    content_record = {
        "id": icon_id, "slideId": slide_id, "groupId": None,
        "iconName": icon_name, "iconSource": "lucide"
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": size, "height": size, "rotation": 0,
        "zIndex": zidx, "color": color, "opacity": opacity,
        "updatedAt": now
    }
    return content_record, changelog_record


def make_chart(chart_id, slide_id, chart_type, x, y, w, h, zidx, now, chart_config):
    content_record = {
        "id": chart_id, "slideId": slide_id, "groupId": None,
        "svgDataUrl": "", "chartType": chart_type,
        "chartConfig": chart_config
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "updatedAt": now,
        "chartType": chart_type
    }
    return content_record, changelog_record


# ---------- Master collections ----------
slides_content = []
slides_baselayout = []
text_by_slide = {}
shape_elements = []
image_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}


def add_slide(slide_id, order, bg):
    slides_content.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg, "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl


def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl


def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = next_id()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, NOW, chart_config)
    chart_elements.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl


# ============================================================
# SLIDE 11 — Proof in the Metrics
# ============================================================
S = "slide-11"
add_slide(S, 0, "#090A0F")

# subtle grid panel background
add_shape(S, "rectangle", 0, 0, 1280, 720, fill="#090A0F", opacity=1)
# top hairline
add_shape(S, "rectangle", 48, 56, 1184, 1, fill="#2a2f3d", opacity=1)
# bottom hairline
add_shape(S, "rectangle", 48, 664, 1184, 1, fill="#2a2f3d", opacity=1)

# Editorial cover line
add_text(S, "OPTIMIZATION VERIFIED  /  RUN 014", "caption",
         48, 28, 600, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_transform="uppercase")
add_text(S, "BENCHMARK · 2026.05", "caption",
         900, 28, 332, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_align="right", text_transform="uppercase")

# Title block left side
add_text(S, "Proof", "title",
         48, 88, 700, 96, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=96, font_weight=700, line_height=1.0)
add_text(S, "in the metrics.", "title",
         48, 178, 700, 64, color="#00D4FF",
         font_family="Canela", font_size=56, font_weight=400, font_style="italic", line_height=1.05)

add_text(S, "Every gain measured. Every regression ruled out. The optimization holds under audit.", "paragraph",
         48, 264, 560, 60, color="#A6A29A",
         font_family="Inter", font_size=18, font_weight=400, line_height=1.55)

# Right side: editorial run-meta column
add_text(S, "TEST WINDOW", "caption",
         900, 100, 332, 16, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "72h continuous · 14M ops", "paragraph",
         900, 120, 332, 28, color="#D8DEE9",
         font_family="IBM Plex Sans", font_size=18, font_weight=500, line_height=1.4)

add_text(S, "ENVIRONMENT", "caption",
         900, 168, 332, 16, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "prod-mirror · region-eu · k8s", "paragraph",
         900, 188, 332, 28, color="#D8DEE9",
         font_family="IBM Plex Sans", font_size=18, font_weight=500, line_height=1.4)

add_text(S, "CONFIDENCE", "caption",
         900, 236, 332, 16, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "p < 0.001 · n = 14,200,000", "paragraph",
         900, 256, 332, 28, color="#22C55E",
         font_family="IBM Plex Sans", font_size=18, font_weight=600, line_height=1.4)

# 2x2 KPI grid
def kpi_card(x, y, label, value, unit, delta, accent, icon_name):
    add_shape(S, "rectangle", x, y, 280, 200, fill="#0F1320", opacity=1)
    add_shape(S, "rectangle", x, y, 280, 2, fill=accent, opacity=1)
    # label
    add_text(S, label, "caption",
             x + 20, y + 18, 240, 16, color="#A6A29A", font_family="JetBrains Mono",
             font_size=11, letter_spacing=2, text_transform="uppercase")
    # icon
    add_icon(S, icon_name, x + 220, y + 14, size=28, color=accent)
    # giant number
    add_text(S, value, "title",
             x + 20, y + 56, 240, 80, color="#F7F8FA",
             font_family="Neue Haas Grotesk Display", font_size=64, font_weight=700, line_height=1.0)
    # unit
    add_text(S, unit, "caption",
             x + 20, y + 138, 240, 22, color="#D8DEE9",
             font_family="IBM Plex Sans", font_size=14, font_weight=500, letter_spacing=1, text_transform="uppercase")
    # delta
    add_text(S, delta, "paragraph",
             x + 20, y + 164, 240, 24, color=accent,
             font_family="JetBrains Mono", font_size=14, font_weight=600, line_height=1.3)

kpi_card(48,  348, "LATENCY P95",  "84",   "MS  · DOWN FROM 312",      "▼ 73%  faster",      "#22C55E", "TrendingDown")
kpi_card(344, 348, "THROUGHPUT",   "4.6",  "M REQ/MIN  · UP FROM 1.9", "▲ 142%  capacity",   "#00D4FF", "TrendingUp")
kpi_card(640, 348, "COMPUTE COST", "0.21", "USD / 1K REQ  · WAS 0.74", "▼ 72%  cheaper",     "#FFB020", "Coins")
kpi_card(936, 348, "RELIABILITY",  "99.99","% UPTIME  · SLO MET",      "▲ 4 nines reached",  "#7C3AED", "ShieldCheck")

# Bottom timeline strip
add_shape(S, "rectangle", 48, 596, 1184, 1, fill="#2a2f3d", opacity=1)
add_text(S, "BASELINE", "caption",
         48, 612, 200, 14, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2)
add_text(S, "OPTIMIZED", "caption",
         1032, 612, 200, 14, color="#00D4FF", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_align="right")
# timeline line
add_shape(S, "rectangle", 48, 632, 1184, 2, fill="#2563FF", opacity=0.6)
add_shape(S, "circle", 40, 624, 16, 16, fill="#A6A29A")
add_shape(S, "circle", 1224, 624, 16, 16, fill="#22C55E")

# bottom-right verified seal
add_text(S, "PASS · SIGNED 05.25.26", "caption",
         48, 642, 600, 16, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "page 011 / 015", "caption",
         900, 642, 332, 16, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_align="right", text_transform="uppercase")


# ============================================================
# SLIDE 12 — The Velocity Verdict
# ============================================================
S = "slide-12"
add_slide(S, 1, "#090A0F")

# top hairline + caption
add_shape(S, "rectangle", 48, 56, 1184, 1, fill="#2a2f3d")
add_text(S, "012 — THE VELOCITY VERDICT", "caption",
         48, 28, 600, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_transform="uppercase")
add_text(S, "TELEMETRY · LIVE BENCHMARK", "caption",
         900, 28, 332, 22, color="#00D4FF", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_align="right", text_transform="uppercase")

# Headline
add_text(S, "The verdict", "title",
         48, 80, 800, 80, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=72, font_weight=700, line_height=1.0)
add_text(S, "is measured in milliseconds.", "title",
         48, 156, 1100, 56, color="#A6A29A",
         font_family="Canela", font_size=40, font_weight=400, font_style="italic", line_height=1.0)

# Right corner monospaced status
add_text(S, "STATUS", "caption",
         1040, 80, 192, 14, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_align="right")
add_text(S, "● OPTIMIZED", "paragraph",
         1040, 96, 192, 24, color="#22C55E",
         font_family="JetBrains Mono", font_size=16, font_weight=600, text_align="right")

# Dashboard panel (top 65% area: y=224 to y=480 ~ height 256)
add_shape(S, "rectangle", 48, 224, 1184, 264, fill="#0F1320")
add_shape(S, "rectangle", 48, 224, 1184, 2, fill="#00D4FF", opacity=0.7)

# Chart axis labels and title
add_text(S, "BENCHMARK TRACE  /  REQUESTS PER SECOND", "caption",
         72, 244, 600, 16, color="#D8DEE9", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "BASELINE ── ", "caption",
         800, 244, 200, 16, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2)
add_text(S, "OPTIMIZED ──", "caption",
         1000, 244, 200, 16, color="#00D4FF", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2)

# Line chart
chart_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": ["00s", "10s", "20s", "30s", "40s", "50s", "60s", "70s", "80s", "90s"],
        "axisLine": {"lineStyle": {"color": "#2a2f3d"}},
        "axisLabel": {"color": "#A6A29A", "fontSize": 11, "fontFamily": "JetBrains Mono"}
    },
    "yAxis": {
        "type": "value",
        "axisLine": {"lineStyle": {"color": "#2a2f3d"}},
        "axisLabel": {"color": "#A6A29A", "fontSize": 11, "fontFamily": "JetBrains Mono"},
        "splitLine": {"lineStyle": {"color": "#1a1f2e"}}
    },
    "grid": {"left": 50, "right": 30, "top": 20, "bottom": 30},
    "series": [
        {"type": "line", "name": "Baseline", "data": [820, 850, 790, 880, 760, 900, 810, 870, 830, 800],
         "smooth": True, "lineStyle": {"color": "#A6A29A", "width": 2, "type": "dashed"},
         "itemStyle": {"color": "#A6A29A"}, "symbol": "none"},
        {"type": "line", "name": "Optimized", "data": [2400, 2680, 3100, 3400, 3850, 4200, 4380, 4520, 4600, 4640],
         "smooth": True, "lineStyle": {"color": "#00D4FF", "width": 3},
         "itemStyle": {"color": "#00D4FF"}, "symbol": "circle", "symbolSize": 6,
         "areaStyle": {"color": "#00D4FF", "opacity": 0.12}}
    ],
    "backgroundColor": "transparent",
    "color": ["#A6A29A", "#00D4FF"],
    "animation": False,
    "textStyle": {"color": "#D8DEE9", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["00s","10s","20s","30s","40s","50s","60s","70s","80s","90s"],
        "series": [
            {"name": "Baseline", "data": [820,850,790,880,760,900,810,870,830,800]},
            {"name": "Optimized", "data": [2400,2680,3100,3400,3850,4200,4380,4520,4600,4640]}
        ]
    },
    "properties": {
        "showXAxis": True, "showYAxis": True, "showDataLabels": False,
        "showLegend": False, "showLabelName": True, "showLabelValue": False,
        "labelFontSize": 12, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None,
    "isDarkMode": True,
    "customSeriesColors": {"0": "#A6A29A", "1": "#00D4FF"},
    "textColor": "#D8DEE9",
    "isMonochrome": False
}
add_chart(S, "line", 72, 270, 1136, 200, chart_cfg)

# Bottom 3 KPI cards (y = 504, h = 168)
def verdict_card(x, y, label, value, unit, delta, accent):
    add_shape(S, "rectangle", x, y, 384, 168, fill="#0F1320")
    add_shape(S, "rectangle", x, y, 2, 168, fill=accent)
    add_text(S, label, "caption",
             x + 24, y + 20, 340, 14, color="#A6A29A", font_family="JetBrains Mono",
             font_size=11, letter_spacing=2, text_transform="uppercase")
    add_text(S, value, "title",
             x + 24, y + 50, 340, 72, color="#F7F8FA",
             font_family="Neue Haas Grotesk Display", font_size=64, font_weight=700, line_height=1.0)
    add_text(S, unit, "caption",
             x + 24, y + 116, 340, 18, color="#D8DEE9",
             font_family="IBM Plex Sans", font_size=13, font_weight=500, letter_spacing=1, text_transform="uppercase")
    add_text(S, delta, "paragraph",
             x + 24, y + 138, 340, 22, color=accent,
             font_family="JetBrains Mono", font_size=14, font_weight=600, line_height=1.2)

verdict_card(48,  504, "LATENCY",        "84ms",   "P95 RESPONSE TIME",            "▼ 228ms vs baseline",  "#22C55E")
verdict_card(448, 504, "THROUGHPUT",     "4.64M",  "REQUESTS / MINUTE",            "▲ 5.7× sustained",     "#00D4FF")
verdict_card(848, 504, "COST PER RUN",   "$0.21",  "PER 1,000 REQUESTS",           "▼ 72% efficiency win", "#FFB020")

# bottom hairline + caption
add_shape(S, "rectangle", 48, 696, 1184, 1, fill="#2a2f3d")


# ============================================================
# SLIDE 13 — Bottlenecks Become Blueprints
# ============================================================
S = "slide-13"
add_slide(S, 2, "#090A0F")

# Top caption
add_shape(S, "rectangle", 48, 56, 1184, 1, fill="#2a2f3d")
add_text(S, "013 — BOTTLENECKS BECOME BLUEPRINTS", "caption",
         48, 28, 700, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_transform="uppercase")
add_text(S, "ARCHITECTURE TEARDOWN", "caption",
         900, 28, 332, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_align="right", text_transform="uppercase")

# Headline
add_text(S, "Bottlenecks become blueprints.", "title",
         48, 80, 1184, 64, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=52, font_weight=700, line_height=1.05)
add_text(S, "Friction we measured is friction we redesigned. Every red node is now a documented improvement.", "paragraph",
         48, 152, 900, 28, color="#A6A29A",
         font_family="Canela", font_size=20, font_weight=400, font_style="italic", line_height=1.4)

# Vertical divider
add_shape(S, "rectangle", 638, 208, 1, 432, fill="#2a2f3d")

# Left column header — BEFORE
add_text(S, "BEFORE", "caption",
         72, 216, 540, 16, color="#FFB020", font_family="JetBrains Mono",
         font_size=12, letter_spacing=3, text_transform="uppercase")
add_text(S, "Friction Map", "heading",
         72, 236, 540, 36, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=28, font_weight=600)

# Left panel background
add_shape(S, "rectangle", 72, 288, 540, 320, fill="#1a1108", opacity=0.6)
add_shape(S, "rectangle", 72, 288, 540, 1, fill="#FFB020", opacity=0.4)

# Friction nodes (red/amber)
def bottleneck_node(cx, cy, label, severity, color):
    add_shape(S, "circle", cx-20, cy-20, 40, 40, fill=color, opacity=0.25)
    add_shape(S, "circle", cx-8, cy-8, 16, 16, fill=color, opacity=1)
    add_text(S, label, "caption",
             cx + 16, cy - 10, 180, 16, color="#F7F8FA",
             font_family="IBM Plex Sans", font_size=13, font_weight=600)
    add_text(S, severity, "caption",
             cx + 16, cy + 6, 180, 14, color="#FFB020",
             font_family="JetBrains Mono", font_size=11, letter_spacing=1)

# connector line bg
add_shape(S, "rectangle", 96, 348, 1, 220, fill="#2a2f3d")
add_shape(S, "rectangle", 96, 348, 480, 1, fill="#2a2f3d")
add_shape(S, "rectangle", 96, 460, 480, 1, fill="#2a2f3d")
add_shape(S, "rectangle", 96, 568, 480, 1, fill="#2a2f3d")

bottleneck_node(120, 348, "DB Query Lock",      "412ms · CRIT", "#ef4444")
bottleneck_node(120, 408, "Cache Miss Storm",   "287ms · HIGH", "#FFB020")
bottleneck_node(120, 468, "Serial Render Path", "198ms · HIGH", "#FFB020")
bottleneck_node(120, 528, "N+1 Lookups",        "164ms · MED",  "#FFB020")
bottleneck_node(120, 588, "Cold-start Network", "94ms  · MED",  "#FFB020")

# Bottom amber summary
add_text(S, "TOTAL FRICTION", "caption",
         400, 588, 200, 14, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_align="right")
add_text(S, "1,155 ms", "heading",
         400, 604, 200, 28, color="#FFB020",
         font_family="JetBrains Mono", font_size=22, font_weight=700, text_align="right")

# Right column header — AFTER
add_text(S, "AFTER", "caption",
         668, 216, 540, 16, color="#00D4FF", font_family="JetBrains Mono",
         font_size=12, letter_spacing=3, text_transform="uppercase")
add_text(S, "Optimized Architecture", "heading",
         668, 236, 540, 36, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=28, font_weight=600)

# Right panel background
add_shape(S, "rectangle", 668, 288, 540, 320, fill="#0a1620", opacity=0.6)
add_shape(S, "rectangle", 668, 288, 540, 1, fill="#00D4FF", opacity=0.5)

# Blueprint clean nodes
def clean_node(cx, cy, label, gain):
    add_shape(S, "circle", cx-12, cy-12, 24, 24, fill="#00D4FF", opacity=0.2)
    add_shape(S, "circle", cx-5, cy-5, 10, 10, fill="#22C55E")
    add_text(S, label, "caption",
             cx + 18, cy - 10, 200, 16, color="#F7F8FA",
             font_family="IBM Plex Sans", font_size=13, font_weight=600)
    add_text(S, gain, "caption",
             cx + 18, cy + 6, 200, 14, color="#22C55E",
             font_family="JetBrains Mono", font_size=11, letter_spacing=1)

# clean connector grid
add_shape(S, "rectangle", 692, 348, 1, 220, fill="#2a3a4d")
add_shape(S, "rectangle", 692, 348, 480, 1, fill="#2a3a4d")
add_shape(S, "rectangle", 692, 460, 480, 1, fill="#2a3a4d")
add_shape(S, "rectangle", 692, 568, 480, 1, fill="#2a3a4d")

clean_node(716, 348, "Indexed Read Replica",     "▼ 408ms")
clean_node(716, 408, "Predictive Edge Cache",    "▼ 273ms")
clean_node(716, 468, "Parallel Render Pipeline", "▼ 186ms")
clean_node(716, 528, "Batch + Prefetch DAG",     "▼ 158ms")
clean_node(716, 588, "Warm Pool · Async I/O",    "▼ 84ms")

add_text(S, "OPTIMIZED FRICTION", "caption",
         950, 588, 240, 14, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_align="right")
add_text(S, "46 ms", "heading",
         950, 604, 240, 28, color="#22C55E",
         font_family="JetBrains Mono", font_size=22, font_weight=700, text_align="right")

# Bottom result strip
add_shape(S, "rectangle", 48, 656, 1184, 1, fill="#2a2f3d")
add_text(S, "BLUEPRINT DELTA", "caption",
         48, 670, 300, 14, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "−96.0%  COMPOSITE LATENCY  ·  +5.7×  THROUGHPUT  ·  +4 NINES  RELIABILITY", "paragraph",
         48, 688, 1184, 22, color="#D8DEE9",
         font_family="JetBrains Mono", font_size=14, font_weight=600, letter_spacing=1)


# ============================================================
# SLIDE 14 — Proof Under Pressure
# ============================================================
S = "slide-14"
add_slide(S, 3, "#090A0F")

# subtle violet shadow corner
add_shape(S, "rectangle", 0, 0, 600, 720, fill="#150A24", opacity=0.5)

# Top caption row
add_shape(S, "rectangle", 48, 56, 1184, 1, fill="#2a2f3d")
add_text(S, "014 — PROOF UNDER PRESSURE", "caption",
         48, 28, 600, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_transform="uppercase")
add_text(S, "STRESS TEST · TIER-1 LOAD", "caption",
         900, 28, 332, 22, color="#FFB020", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_align="right", text_transform="uppercase")

# Headline
add_text(S, "Proof under", "title",
         48, 84, 800, 88, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=80, font_weight=700, line_height=1.0)
add_text(S, "pressure.", "title",
         48, 168, 800, 88, color="#7C3AED",
         font_family="Canela", font_size=72, font_weight=400, font_style="italic", line_height=1.0)
add_text(S, "Stability held. Recovery measured in seconds. The system bent — it did not break.", "paragraph",
         48, 264, 700, 28, color="#A6A29A",
         font_family="Inter", font_size=18, font_weight=400, line_height=1.5)

# Right edge meta
add_text(S, "PEAK LOAD REACHED", "caption",
         900, 84, 332, 14, color="#A6A29A", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_align="right")
add_text(S, "12.4M req/min", "heading",
         900, 102, 332, 32, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=26, font_weight=700, text_align="right")
add_text(S, "● THRESHOLD HOLD", "caption",
         900, 142, 332, 16, color="#22C55E",
         font_family="JetBrains Mono", font_size=12, letter_spacing=2, text_align="right")

# Central graph panel
add_shape(S, "rectangle", 48, 320, 824, 296, fill="#0a0d1a")
add_shape(S, "rectangle", 48, 320, 824, 2, fill="#7C3AED", opacity=0.6)

add_text(S, "LATENCY UNDER LOAD  /  P50 · P95 · P99", "caption",
         72, 340, 600, 14, color="#D8DEE9", font_family="JetBrains Mono",
         font_size=11, letter_spacing=2, text_transform="uppercase")

# Stability threshold line label
add_text(S, "── STABILITY THRESHOLD  120ms", "caption",
         600, 340, 260, 14, color="#22C55E", font_family="JetBrains Mono",
         font_size=11, letter_spacing=1, text_align="right")

# Stress chart
chart_cfg2 = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": ["1k", "10k", "50k", "100k", "500k", "1M", "3M", "6M", "9M", "12M"],
        "axisLine": {"lineStyle": {"color": "#2a2f3d"}},
        "axisLabel": {"color": "#A6A29A", "fontSize": 11, "fontFamily": "JetBrains Mono"}
    },
    "yAxis": {
        "type": "value", "max": 200,
        "axisLine": {"lineStyle": {"color": "#2a2f3d"}},
        "axisLabel": {"color": "#A6A29A", "fontSize": 11, "fontFamily": "JetBrains Mono", "formatter": "{value}ms"},
        "splitLine": {"lineStyle": {"color": "#1a1f2e"}}
    },
    "grid": {"left": 56, "right": 28, "top": 24, "bottom": 30},
    "series": [
        {"type": "line", "name": "P99", "data": [62, 68, 74, 79, 88, 96, 104, 112, 116, 118],
         "smooth": True, "lineStyle": {"color": "#7C3AED", "width": 2},
         "itemStyle": {"color": "#7C3AED"}, "symbol": "none",
         "areaStyle": {"color": "#7C3AED", "opacity": 0.10}},
        {"type": "line", "name": "P95", "data": [44, 48, 52, 56, 62, 68, 74, 80, 84, 86],
         "smooth": True, "lineStyle": {"color": "#00D4FF", "width": 2},
         "itemStyle": {"color": "#00D4FF"}, "symbol": "none"},
        {"type": "line", "name": "P50", "data": [22, 24, 26, 28, 30, 32, 34, 36, 37, 38],
         "smooth": True, "lineStyle": {"color": "#22C55E", "width": 2},
         "itemStyle": {"color": "#22C55E"}, "symbol": "none"}
    ],
    "backgroundColor": "transparent",
    "color": ["#7C3AED", "#00D4FF", "#22C55E"],
    "animation": False,
    "textStyle": {"color": "#D8DEE9", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["1k","10k","50k","100k","500k","1M","3M","6M","9M","12M"],
        "series": [
            {"name": "P99", "data": [62,68,74,79,88,96,104,112,116,118]},
            {"name": "P95", "data": [44,48,52,56,62,68,74,80,84,86]},
            {"name": "P50", "data": [22,24,26,28,30,32,34,36,37,38]}
        ]
    },
    "properties": {
        "showXAxis": True, "showYAxis": True, "showDataLabels": False,
        "showLegend": False, "showLabelName": True, "showLabelValue": False,
        "labelFontSize": 12, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None,
    "isDarkMode": True,
    "customSeriesColors": {"0": "#7C3AED", "1": "#00D4FF", "2": "#22C55E"},
    "textColor": "#D8DEE9",
    "isMonochrome": False
}
add_chart(S, "line", 72, 364, 776, 240, chart_cfg2)

# Floating test-condition cards (right column)
def stress_card(x, y, label, value, unit, accent):
    add_shape(S, "rectangle", x, y, 248, 64, fill="#0F1320")
    add_shape(S, "rectangle", x, y, 2, 64, fill=accent)
    add_text(S, label, "caption",
             x + 16, y + 10, 220, 12, color="#A6A29A", font_family="JetBrains Mono",
             font_size=10, letter_spacing=2, text_transform="uppercase")
    add_text(S, value, "heading",
             x + 16, y + 26, 160, 32, color="#F7F8FA",
             font_family="Neue Haas Grotesk Display", font_size=24, font_weight=700)
    add_text(S, unit, "caption",
             x + 180, y + 36, 56, 14, color=accent,
             font_family="JetBrains Mono", font_size=11, font_weight=600, text_align="right")

stress_card(896, 320, "LOAD",          "12.4M",  "req/min",  "#FFB020")
stress_card(896, 392, "CONCURRENCY",   "84,000", "sessions", "#00D4FF")
stress_card(896, 464, "FAILURE RATE",  "0.003",  "%",        "#22C55E")
stress_card(896, 536, "RECOVERY TIME", "1.4",    "seconds",  "#7C3AED")

# Bottom strip
add_shape(S, "rectangle", 48, 648, 1184, 1, fill="#2a2f3d")
add_text(S, "TEST: chaos-mode · region-failover · burst+1200% · cold-start ×3", "caption",
         48, 664, 800, 16, color="#A6A29A",
         font_family="JetBrains Mono", font_size=12, letter_spacing=1)
add_text(S, "VERDICT: HOLD", "caption",
         900, 664, 332, 16, color="#22C55E",
         font_family="JetBrains Mono", font_size=12, letter_spacing=2, text_align="right", text_transform="uppercase")


# ============================================================
# SLIDE 15 — Faster Is a New Standard
# ============================================================
S = "slide-15"
add_slide(S, 4, "#090A0F")

# Warm horizon gradient strip (bottom)
add_shape(S, "rectangle", 0, 540, 1280, 180, fill="#1a1208", opacity=0.7)
add_shape(S, "rectangle", 0, 538, 1280, 2, fill="#FFB020", opacity=0.7)
# faint blue edge light at top
add_shape(S, "rectangle", 0, 0, 1280, 4, fill="#2563FF", opacity=0.5)

# Top caption row
add_text(S, "015 — CLOSING STATEMENT", "caption",
         48, 28, 600, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_transform="uppercase")
add_text(S, "FAST OPTIMIZATION TEST · END", "caption",
         900, 28, 332, 22, color="#A6A29A", font_family="JetBrains Mono",
         font_size=12, letter_spacing=2, text_align="right", text_transform="uppercase")
add_shape(S, "rectangle", 48, 56, 1184, 1, fill="#2a2f3d")

# Massive monumental serif statement
add_text(S, "Faster", "title",
         48, 124, 1184, 160, color="#F7F8FA",
         font_family="Neue Haas Grotesk Display", font_size=140, font_weight=700, line_height=1.0)
add_text(S, "is a new standard.", "title",
         48, 270, 1184, 100, color="#FFB020",
         font_family="Canela", font_size=88, font_weight=400, font_style="italic", line_height=1.0)

# Editorial closing italic line
add_text(S, "Optimization is no longer a phase.", "paragraph",
         48, 396, 1184, 32, color="#D8DEE9",
         font_family="Canela", font_size=24, font_weight=400, font_style="italic", line_height=1.3)
add_text(S, "It is the operating system.", "paragraph",
         48, 428, 1184, 32, color="#00D4FF",
         font_family="Canela", font_size=24, font_weight=500, font_style="italic", line_height=1.3)

# Thin divider above metrics row
add_shape(S, "rectangle", 48, 560, 1184, 1, fill="#3a2f1a")

# Final impact metrics row
def final_metric(x, label, value, unit, color):
    add_text(S, label, "caption",
             x, 580, 380, 14, color="#A6A29A", font_family="JetBrains Mono",
             font_size=11, letter_spacing=2, text_transform="uppercase")
    add_text(S, value, "title",
             x, 600, 380, 56, color="#F7F8FA",
             font_family="Neue Haas Grotesk Display", font_size=48, font_weight=700, line_height=1.0)
    add_text(S, unit, "caption",
             x, 654, 380, 16, color=color,
             font_family="JetBrains Mono", font_size=12, font_weight=600, letter_spacing=2, text_transform="uppercase")

final_metric(48,  "LATENCY",     "−73%",   "engineered down",   "#22C55E")
final_metric(448, "THROUGHPUT",  "5.7×",   "sustained capacity","#00D4FF")
final_metric(848, "COST",        "−72%",   "per request",       "#FFB020")

# Bottom-most signature hairline
add_shape(S, "rectangle", 48, 696, 1184, 1, fill="#2a2f3d")
add_text(S, "SIGNED · OPTIMIZATION ENGINE  ·  2026.05.25", "caption",
         48, 702, 600, 14, color="#A6A29A",
         font_family="JetBrains Mono", font_size=11, letter_spacing=2, text_transform="uppercase")
add_text(S, "015 / 015", "caption",
         900, 702, 332, 14, color="#A6A29A",
         font_family="JetBrains Mono", font_size=11, letter_spacing=2, text_align="right")


# ============================================================
# Assemble final JSON
# ============================================================
for s in slides_content:
    s["textElements"] = text_by_slide[s["id"]]

element_count = (
    sum(len(v) for v in text_by_slide.values()) +
    len(image_elements) + len(shape_elements) + len(chart_elements) +
    len(table_elements) + len(icon_elements)
)

content_file = {
    "slides": slides_content,
    "imageElements": image_elements,
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": table_elements,
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baselayout_file = {
    "version": "v1",
    "slides": slides_baselayout,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

changelog_file = {
    "version": "2.0",
    "slides": changelog_slides
}

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Fast Optimization Test",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": element_count,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baselayout_file,
        "changelog": changelog_file
    }
}

out_path = "deck.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)

print(f"Wrote {out_path}")
print(f"slideCount={deck['presentation']['slideCount']}")
print(f"elementCount={element_count}")
print(f"text={sum(len(v) for v in text_by_slide.values())} shape={len(shape_elements)} icon={len(icon_elements)} chart={len(chart_elements)} table={len(table_elements)} image={len(image_elements)}")
