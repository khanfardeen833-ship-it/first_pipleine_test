import json
import time

NOW = int(time.time() * 1000)
DECK_ID = f"deck-batch2-{NOW}"

COUNTER = 300

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------- helpers ----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Inter"):
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
            "fontWeight": fw, "fontStyle": "normal", "textDecoration": "none",
            "textTransform": "none", "isCode": False, "listStyle": "none",
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
               fill="#c67c3a", stroke=None, stroke_width=0, opacity=1):
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
              size=80, color="#22D3EE", opacity=1):
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


def make_table(table_id, slide_id, x, y, zidx, now,
               col_widths, row_heights, cells,
               font_size=16, table_color="#F8FAFC", table_bg="#111827"):
    content_record = {
        "id": table_id, "slideId": slide_id, "groupId": None,
        "type": "table",
        "position": {"x": x, "y": y},
        "zIndex": zidx,
        "cells": cells,
        "colWidths": col_widths,
        "rowHeights": row_heights,
        "tableFontSize": font_size,
        "tableBold": False, "tableItalic": False,
        "tableAlign": "left",
        "tableColor": table_color, "tableBg": table_bg
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "zIndex": zidx,
        "updatedAt": now,
        "style": {"colWidths": col_widths, "rowHeights": row_heights}
    }
    return content_record, changelog_record


# ---------- accumulators ----------

slides_content = []
slides_baselayout = []
text_by_slide = {}
shapes_content = []
images_content = []
icons_content = []
charts_content = []
tables_content = []
changelog_slides = {}


def init_slide(slide_id, order, bg):
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
    return tid


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shapes_content.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid


def add_icon(slide_id, name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, name, x, y, n, NOW, **kwargs)
    icons_content.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


def add_chart(slide_id, chart_type, x, y, w, h, config):
    n = next_id()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, NOW, config)
    charts_content.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl
    return cid


def add_table(slide_id, x, y, col_widths, row_heights, cells, **kwargs):
    n = next_id()
    tid = f"table-{n}"
    c, cl = make_table(tid, slide_id, x, y, n, NOW, col_widths, row_heights, cells, **kwargs)
    tables_content.append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


# ---------- color palette ----------
GRAPHITE = "#111827"
NAVY = "#0B1F3A"
CLOUD = "#F8FAFC"
MIST = "#E5E7EB"
SIGNAL = "#2563EB"
CYAN = "#22D3EE"
GREEN = "#10B981"
AMBER = "#F59E0B"
CRIMSON = "#DC2626"
VIOLET = "#7C3AED"
PANEL = "#1F2937"
PANEL_LIGHT = "#374151"
SLATE = "#9CA3AF"


# =====================================================================
# SLIDE 6 — Training, Testing, and the Release Gate
# =====================================================================
SID = "slide-6"
init_slide(SID, 5, GRAPHITE)

# subtle panel grid background hint
add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=GRAPHITE)
# left vertical accent rail
add_shape(SID, "rectangle", 0, 0, 6, 720, fill=SIGNAL)

# top eyebrow label
add_text(SID, "RELEASE GATE  ·  06", "caption",
         48, 48, 360, 20,
         color=CYAN, font_size=12, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=3)

# headline
add_text(SID, "Training, Testing, and the Release Gate.", "title",
         48, 80, 1100, 76,
         color=CLOUD, font_size=52, font_weight=700, line_height=1.1)

# subtitle
add_text(SID, "Disciplined quality assurance before a model is allowed into the real world.", "subtitle",
         48, 168, 1100, 36,
         color=SLATE, font_size=20, font_weight=400, line_height=1.3)

# ---- LEFT PANEL: Experiment Tracking ----
add_shape(SID, "rectangle", 48, 232, 568, 320,
          fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)

add_text(SID, "EXPERIMENT REGISTRY", "caption",
         72, 256, 400, 18,
         color=CYAN, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

add_text(SID, "Candidate evaluation results", "heading",
         72, 280, 520, 32,
         color=CLOUD, font_size=22, font_weight=600)

# experiment table
exp_cells = {
    "0-0": {"text": "RUN", "bold": True, "bg": "#0F172A", "color": CYAN},
    "0-1": {"text": "AUC", "bold": True, "bg": "#0F172A", "color": CYAN},
    "0-2": {"text": "P95 ms", "bold": True, "bg": "#0F172A", "color": CYAN},
    "0-3": {"text": "STATUS", "bold": True, "bg": "#0F172A", "color": CYAN},
    "1-0": {"text": "exp-0142", "bold": False, "bg": PANEL, "color": CLOUD},
    "1-1": {"text": "0.872", "bold": False, "bg": PANEL, "color": CLOUD},
    "1-2": {"text": "84", "bold": False, "bg": PANEL, "color": CLOUD},
    "1-3": {"text": "PASS", "bold": True, "bg": PANEL, "color": GREEN},
    "2-0": {"text": "exp-0151", "bold": False, "bg": "#1A2332", "color": CLOUD},
    "2-1": {"text": "0.891", "bold": False, "bg": "#1A2332", "color": CLOUD},
    "2-2": {"text": "92", "bold": False, "bg": "#1A2332", "color": CLOUD},
    "2-3": {"text": "PASS", "bold": True, "bg": "#1A2332", "color": GREEN},
    "3-0": {"text": "exp-0163", "bold": False, "bg": PANEL, "color": CLOUD},
    "3-1": {"text": "0.903", "bold": False, "bg": PANEL, "color": CLOUD},
    "3-2": {"text": "118", "bold": False, "bg": PANEL, "color": AMBER},
    "3-3": {"text": "REVIEW", "bold": True, "bg": PANEL, "color": AMBER},
    "4-0": {"text": "exp-0177", "bold": True, "bg": "#1A2332", "color": CYAN},
    "4-1": {"text": "0.918", "bold": True, "bg": "#1A2332", "color": CYAN},
    "4-2": {"text": "76", "bold": True, "bg": "#1A2332", "color": CYAN},
    "4-3": {"text": "PROMOTED", "bold": True, "bg": "#1A2332", "color": CYAN},
}
add_table(SID, 72, 328, [180, 110, 110, 144], [38, 36, 36, 36, 36],
          exp_cells, font_size=14, table_color=CLOUD, table_bg=PANEL)

# ---- RIGHT PANEL: Readiness Gates ----
add_shape(SID, "rectangle", 648, 232, 584, 320,
          fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)

add_text(SID, "DEPLOYMENT READINESS", "caption",
         672, 256, 400, 18,
         color=GREEN, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

add_text(SID, "Pre-flight checklist", "heading",
         672, 280, 520, 32,
         color=CLOUD, font_size=22, font_weight=600)

gates = [
    ("CheckCircle", "Bias & fairness audit", "subgroup parity within 2.1%", GREEN),
    ("CheckCircle", "Robustness validation", "adversarial test suite passed", GREEN),
    ("CheckCircle", "Security review", "SBOM signed, secrets scanned", GREEN),
    ("Clock",       "Latency benchmarks", "p95 < 100 ms @ 200 RPS", AMBER),
    ("CheckCircle", "Rollback verified", "v1.7 hot-restore < 30 s", GREEN),
]
for i, (icn, label, sub, clr) in enumerate(gates):
    gy = 328 + i * 42
    add_icon(SID, icn, 680, gy, size=22, color=clr)
    add_text(SID, label, "paragraph", 712, gy - 2, 280, 24,
             color=CLOUD, font_size=15, font_weight=600, line_height=1.4)
    add_text(SID, sub, "caption", 1000, gy + 2, 220, 20,
             color=SLATE, font_size=11, font_weight=500,
             font_family="IBM Plex Mono")

# ---- BOTTOM: Promotion pipeline dev → staging → canary → production ----
add_text(SID, "PROMOTION PATH", "caption",
         48, 580, 300, 18,
         color=SLATE, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

stages = [
    ("dev",         "training cluster",    PANEL_LIGHT, CLOUD),
    ("staging",     "shadow traffic",       SIGNAL,     CLOUD),
    ("canary",      "5% live traffic",      VIOLET,     CLOUD),
    ("production",  "100% rollout",         GREEN,      "#0F172A"),
]
sx = 48
sw = 268
gap = 24
for i, (label, sub, fill, txt) in enumerate(stages):
    x0 = sx + i * (sw + gap)
    add_shape(SID, "rectangle", x0, 608, sw, 64, fill=fill)
    add_text(SID, label.upper(), "paragraph", x0 + 20, 618, sw - 40, 24,
             color=txt, font_size=14, font_weight=700,
             font_family="IBM Plex Mono", letter_spacing=2)
    add_text(SID, sub, "caption", x0 + 20, 644, sw - 40, 20,
             color=txt, font_size=11, font_weight=500, line_height=1.2)
    if i < 3:
        ax = x0 + sw + 2
        add_icon(SID, "ChevronRight", ax, 624, size=20, color=CYAN)


# =====================================================================
# SLIDE 7 — Deployment Patterns in Motion
# =====================================================================
SID = "slide-7"
init_slide(SID, 6, NAVY)

add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=NAVY)
# top accent
add_shape(SID, "rectangle", 0, 0, 1280, 4, fill=SIGNAL)

add_text(SID, "DEPLOYMENT  ·  07", "caption",
         48, 48, 360, 20,
         color=CYAN, font_size=12, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=3)

add_text(SID, "Deployment Patterns in Motion.", "title",
         48, 80, 1100, 76,
         color=CLOUD, font_size=52, font_weight=700, line_height=1.1)

add_text(SID, "Four production strategies — chosen by traffic shape, latency budget, and rollback risk.", "subtitle",
         48, 168, 1180, 32,
         color=SLATE, font_size=18, font_weight=400, line_height=1.3)

# 4 cards in a row
cards = [
    {
        "icon": "Database",
        "color": CYAN,
        "title": "Batch Inference",
        "desc": "Scheduled scoring at scale. Optimized for throughput, not latency.",
        "meta": [("WHEN",  "nightly · weekly"),
                 ("LATENCY","minutes"),
                 ("STACK", "Spark · Airflow")],
    },
    {
        "icon": "Zap",
        "color": SIGNAL,
        "title": "Real-Time API",
        "desc": "Synchronous predictions per request. Tight p95 budget, autoscaled.",
        "meta": [("WHEN",  "user-facing"),
                 ("LATENCY","< 100 ms"),
                 ("STACK", "gRPC · Triton")],
    },
    {
        "icon": "EyeOff",
        "color": VIOLET,
        "title": "Shadow Mode",
        "desc": "Mirror live traffic to a candidate model. Compare without exposure.",
        "meta": [("WHEN",  "pre-launch"),
                 ("LATENCY","async log"),
                 ("STACK", "Kafka · S3")],
    },
    {
        "icon": "GitBranch",
        "color": GREEN,
        "title": "Canary Release",
        "desc": "Route a small % of traffic to v-next. Promote on green, rollback on red.",
        "meta": [("WHEN",  "every release"),
                 ("LATENCY","prod-equal"),
                 ("STACK", "Istio · LaunchDarkly")],
    },
]

cx = 48
cw = 280
cgap = 16
cy = 232

for i, card in enumerate(cards):
    x0 = cx + i * (cw + cgap)
    # card panel
    add_shape(SID, "rectangle", x0, cy, cw, 416, fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)
    # accent stripe
    add_shape(SID, "rectangle", x0, cy, cw, 4, fill=card["color"])
    # icon
    add_icon(SID, card["icon"], x0 + 24, cy + 32, size=44, color=card["color"])
    # number
    add_text(SID, f"0{i+1}", "caption",
             x0 + cw - 60, cy + 32, 40, 24,
             color=SLATE, font_size=14, font_weight=600,
             font_family="IBM Plex Mono", text_align="right")
    # title
    add_text(SID, card["title"], "heading",
             x0 + 24, cy + 100, cw - 48, 32,
             color=CLOUD, font_size=22, font_weight=700, line_height=1.2)
    # description
    add_text(SID, card["desc"], "paragraph",
             x0 + 24, cy + 144, cw - 48, 90,
             color=SLATE, font_size=14, font_weight=400, line_height=1.5)
    # divider
    add_shape(SID, "rectangle", x0 + 24, cy + 248, cw - 48, 1, fill=PANEL_LIGHT)
    # meta rows
    for j, (k, v) in enumerate(card["meta"]):
        my = cy + 268 + j * 42
        add_text(SID, k, "caption",
                 x0 + 24, my, 100, 16,
                 color=SLATE, font_size=10, font_weight=600,
                 font_family="IBM Plex Mono", letter_spacing=2)
        add_text(SID, v, "paragraph",
                 x0 + 24, my + 16, cw - 48, 22,
                 color=card["color"], font_size=13, font_weight=500,
                 font_family="IBM Plex Mono")

# bottom caption
add_text(SID, "Each pattern is a contract between risk tolerance and rollout velocity.", "caption",
         48, 676, 900, 22,
         color=SLATE, font_size=13, font_weight=400)


# =====================================================================
# SLIDE 8 — The Production Pulse
# =====================================================================
SID = "slide-8"
init_slide(SID, 7, GRAPHITE)

add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=GRAPHITE)
# top rail
add_shape(SID, "rectangle", 0, 0, 1280, 4, fill=GREEN)

add_text(SID, "OBSERVABILITY  ·  08", "caption",
         48, 48, 360, 20,
         color=GREEN, font_size=12, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=3)

add_text(SID, "The Production Pulse.", "title",
         48, 80, 1100, 76,
         color=CLOUD, font_size=52, font_weight=700, line_height=1.1)

add_text(SID, "Live signals from the model in flight — latency, errors, throughput, confidence.", "subtitle",
         48, 168, 1180, 32,
         color=SLATE, font_size=18, font_weight=400, line_height=1.3)

# Central Model Health panel
add_shape(SID, "rectangle", 48, 232, 760, 360,
          fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)

add_text(SID, "MODEL HEALTH  ·  prod/v1.9", "caption",
         72, 256, 400, 18,
         color=CYAN, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

add_text(SID, "p95 latency over last 24h", "heading",
         72, 280, 520, 32,
         color=CLOUD, font_size=20, font_weight=600)

add_text(SID, "HEALTHY", "caption",
         700, 264, 100, 22,
         color=GREEN, font_size=12, font_weight=700,
         font_family="IBM Plex Mono", letter_spacing=2, text_align="right")

# main line chart
hours = [f"{h:02d}:00" for h in range(0, 24, 2)]
latency_data = [72, 75, 71, 68, 70, 74, 82, 88, 91, 86, 79, 76]
chart_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category", "data": hours,
        "axisLine": {"lineStyle": {"color": SLATE}},
        "axisLabel": {"color": SLATE, "fontSize": 11, "fontFamily": "IBM Plex Mono"},
        "splitLine": {"show": False}
    },
    "yAxis": {
        "type": "value",
        "axisLine": {"lineStyle": {"color": SLATE}},
        "axisLabel": {"color": SLATE, "fontSize": 11, "fontFamily": "IBM Plex Mono"},
        "splitLine": {"lineStyle": {"color": "#1F2937", "type": "dashed"}}
    },
    "series": [{
        "type": "line", "data": latency_data, "smooth": True,
        "lineStyle": {"color": CYAN, "width": 3},
        "itemStyle": {"color": CYAN},
        "areaStyle": {"color": "rgba(34,211,238,0.18)"},
        "symbol": "circle", "symbolSize": 6
    }],
    "grid": {"left": 50, "right": 24, "top": 24, "bottom": 36},
    "backgroundColor": "transparent",
    "color": [CYAN],
    "animation": False,
    "textStyle": {"color": CLOUD, "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": hours, "series": [{"name": "p95 ms", "data": latency_data}]},
    "properties": {
        "showXAxis": True, "showYAxis": True, "showDataLabels": False,
        "showLegend": False, "showLabelName": True, "showLabelValue": False,
        "labelFontSize": 12, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": CYAN},
    "textColor": CLOUD, "isMonochrome": False
}
add_chart(SID, "line", 64, 320, 728, 256, chart_cfg)

# annotation
add_text(SID, "spike at 14:00 — autoscaler added 4 replicas, recovered in 9 min", "caption",
         72, 560, 720, 20,
         color=AMBER, font_size=11, font_weight=500,
         font_family="IBM Plex Mono")

# ---- KPI cards on the right ----
kpis = [
    ("Clock",      "P95 LATENCY",     "84",  "ms",         "+2 vs 24h",  CYAN),
    ("AlertCircle","ERROR RATE",      "0.21","%",          "-0.04",      GREEN),
    ("Activity",   "THROUGHPUT",      "2.4", "k req/s",    "+180",       SIGNAL),
    ("BarChart2",  "PREDICTIONS/MIN", "144", "k",          "stable",     VIOLET),
]
kx = 832
kw = 400
kh = 84
gap_k = 8
ky0 = 232
for i, (icn, label, val, unit, delta, clr) in enumerate(kpis):
    y0 = ky0 + i * (kh + gap_k)
    add_shape(SID, "rectangle", kx, y0, kw, kh, fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)
    add_shape(SID, "rectangle", kx, y0, 4, kh, fill=clr)
    add_icon(SID, icn, kx + 20, y0 + 22, size=24, color=clr)
    add_text(SID, label, "caption",
             kx + 56, y0 + 14, 200, 16,
             color=SLATE, font_size=10, font_weight=600,
             font_family="IBM Plex Mono", letter_spacing=2)
    add_text(SID, val, "title",
             kx + 56, y0 + 32, 180, 44,
             color=CLOUD, font_size=36, font_weight=700, line_height=1.1,
             font_family="IBM Plex Mono")
    add_text(SID, unit, "caption",
             kx + 200, y0 + 48, 100, 22,
             color=SLATE, font_size=14, font_weight=500,
             font_family="IBM Plex Mono")
    add_text(SID, delta, "caption",
             kx + kw - 120, y0 + 48, 100, 22,
             color=clr, font_size=12, font_weight=600,
             font_family="IBM Plex Mono", text_align="right")

# bottom caption
add_text(SID, "Monitoring turns deployment into an operating system.", "caption",
         48, 676, 900, 22,
         color=SLATE, font_size=13, font_weight=400)


# =====================================================================
# SLIDE 9 — Drift in the Wild
# =====================================================================
SID = "slide-9"
init_slide(SID, 8, NAVY)

add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=NAVY)
# top rail
add_shape(SID, "rectangle", 0, 0, 1280, 4, fill=AMBER)

add_text(SID, "DRIFT  ·  09", "caption",
         48, 48, 360, 20,
         color=AMBER, font_size=12, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=3)

add_text(SID, "Drift in the Wild.", "title",
         48, 80, 1100, 76,
         color=CLOUD, font_size=52, font_weight=700, line_height=1.1)

add_text(SID, "The world your model trained on is not the world it serves.", "subtitle",
         48, 168, 1180, 32,
         color=SLATE, font_size=18, font_weight=400, line_height=1.3)

# central divergence rule
add_shape(SID, "rectangle", 638, 232, 4, 280, fill=AMBER, opacity=0.6)
add_icon(SID, "AlertTriangle", 624, 364, size=32, color=AMBER)

# LEFT panel — Training World
add_shape(SID, "rectangle", 48, 232, 568, 280,
          fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)

add_text(SID, "TRAINING WORLD", "caption",
         72, 256, 300, 18,
         color=CYAN, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

add_text(SID, "stable distribution · curated", "heading",
         72, 280, 520, 28,
         color=CLOUD, font_size=18, font_weight=600)

train_curve = [4, 9, 18, 32, 48, 62, 70, 64, 50, 34, 18, 8, 3]
train_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category", "data": [str(i) for i in range(len(train_curve))],
        "axisLine": {"lineStyle": {"color": "transparent"}},
        "axisLabel": {"show": False},
        "splitLine": {"show": False}
    },
    "yAxis": {
        "type": "value",
        "axisLine": {"lineStyle": {"color": "transparent"}},
        "axisLabel": {"show": False},
        "splitLine": {"show": False}
    },
    "series": [{
        "type": "line", "data": train_curve, "smooth": True,
        "lineStyle": {"color": CYAN, "width": 3},
        "itemStyle": {"color": CYAN},
        "areaStyle": {"color": "rgba(34,211,238,0.30)"},
        "symbol": "none"
    }],
    "grid": {"left": 8, "right": 8, "top": 8, "bottom": 8},
    "backgroundColor": "transparent",
    "color": [CYAN], "animation": False,
    "textStyle": {"color": CLOUD, "fontSize": 11, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": [str(i) for i in range(len(train_curve))],
                  "series": [{"name": "train", "data": train_curve}]},
    "properties": {"showXAxis": False, "showYAxis": False, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 11, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": CYAN},
    "textColor": CLOUD, "isMonochrome": False
}
add_chart(SID, "line", 72, 320, 520, 160, train_cfg)

add_text(SID, "PSI 0.02  ·  KL 0.01  ·  baseline", "caption",
         72, 488, 520, 18,
         color=SLATE, font_size=11, font_weight=500,
         font_family="IBM Plex Mono")

# RIGHT panel — Production World
add_shape(SID, "rectangle", 664, 232, 568, 280,
          fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)

add_text(SID, "PRODUCTION WORLD", "caption",
         688, 256, 300, 18,
         color=AMBER, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

add_text(SID, "shifting distribution · live", "heading",
         688, 280, 520, 28,
         color=CLOUD, font_size=18, font_weight=600)

prod_curve = [12, 24, 38, 48, 52, 50, 44, 48, 56, 62, 56, 38, 18]
prod_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category", "data": [str(i) for i in range(len(prod_curve))],
        "axisLine": {"lineStyle": {"color": "transparent"}},
        "axisLabel": {"show": False},
        "splitLine": {"show": False}
    },
    "yAxis": {
        "type": "value",
        "axisLine": {"lineStyle": {"color": "transparent"}},
        "axisLabel": {"show": False},
        "splitLine": {"show": False}
    },
    "series": [{
        "type": "line", "data": prod_curve, "smooth": True,
        "lineStyle": {"color": AMBER, "width": 3},
        "itemStyle": {"color": AMBER},
        "areaStyle": {"color": "rgba(245,158,11,0.30)"},
        "symbol": "none"
    }],
    "grid": {"left": 8, "right": 8, "top": 8, "bottom": 8},
    "backgroundColor": "transparent",
    "color": [AMBER], "animation": False,
    "textStyle": {"color": CLOUD, "fontSize": 11, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": [str(i) for i in range(len(prod_curve))],
                  "series": [{"name": "prod", "data": prod_curve}]},
    "properties": {"showXAxis": False, "showYAxis": False, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 11, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": AMBER},
    "textColor": CLOUD, "isMonochrome": False
}
add_chart(SID, "line", 688, 320, 520, 160, prod_cfg)

add_text(SID, "PSI 0.27  ·  KL 0.18  ·  threshold breached", "caption",
         688, 488, 520, 18,
         color=AMBER, font_size=11, font_weight=500,
         font_family="IBM Plex Mono")

# Three callouts at bottom
callouts = [
    ("Layers",     "Feature Drift",       "input distributions evolve  ·  PSI > 0.20", VIOLET),
    ("Compass",    "Concept Drift",       "the relationship X→Y changes underneath",   AMBER),
    ("ShieldOff",  "Data Quality Decay",  "schemas, nulls, and upstream contracts erode", CRIMSON),
]
cox = 48
cow = 384
cogap = 16
coy = 540
for i, (icn, title, sub, clr) in enumerate(callouts):
    x0 = cox + i * (cow + cogap)
    add_shape(SID, "rectangle", x0, coy, cow, 124, fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)
    add_shape(SID, "rectangle", x0, coy, 4, 124, fill=clr)
    add_icon(SID, icn, x0 + 20, coy + 20, size=28, color=clr)
    add_text(SID, title, "heading",
             x0 + 64, coy + 22, cow - 80, 28,
             color=CLOUD, font_size=18, font_weight=700)
    add_text(SID, sub, "paragraph",
             x0 + 20, coy + 70, cow - 40, 44,
             color=SLATE, font_size=13, font_weight=400, line_height=1.4)


# =====================================================================
# SLIDE 10 — Guardrails Before the Fall
# =====================================================================
SID = "slide-10"
init_slide(SID, 9, GRAPHITE)

add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=GRAPHITE)
# accent rail
add_shape(SID, "rectangle", 0, 0, 1280, 4, fill=VIOLET)

add_text(SID, "RESILIENCE  ·  10", "caption",
         48, 48, 360, 20,
         color=VIOLET, font_size=12, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=3)

add_text(SID, "Guardrails Before the Fall.", "title",
         48, 80, 1100, 76,
         color=CLOUD, font_size=52, font_weight=700, line_height=1.1)

add_text(SID, "Production ML is not just prediction — it is controlled decisioning.", "subtitle",
         48, 168, 1180, 32,
         color=SLATE, font_size=18, font_weight=400, line_height=1.3)

# Six-stage guardrail pipeline
stages = [
    ("Inbox",        "Request",       "user / service input",      SIGNAL),
    ("ShieldCheck",  "Validation",    "schema · auth · rate limit", CYAN),
    ("Cpu",          "Inference",     "primary model · v1.9",       VIOLET),
    ("Scale",        "Policy Checks", "bias · safety · confidence", AMBER),
    ("LifeBuoy",     "Fallback",      "rules · v1.7 · human queue", CRIMSON),
    ("Send",         "Response",      "decision delivered",         GREEN),
]

# pipeline geometry
px = 48
pw = 184
pgap = 16
py = 244
ph = 240

# connecting baseline
add_shape(SID, "rectangle", px + 32, py + ph + 12, 1280 - 2 * px - 64, 2, fill=PANEL_LIGHT)

for i, (icn, label, sub, clr) in enumerate(stages):
    x0 = px + i * (pw + pgap)

    # node panel
    add_shape(SID, "rectangle", x0, py, pw, ph, fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)
    # top stripe
    add_shape(SID, "rectangle", x0, py, pw, 4, fill=clr)
    # step number
    add_text(SID, f"0{i+1}", "caption",
             x0 + 16, py + 16, 60, 18,
             color=SLATE, font_size=11, font_weight=600,
             font_family="IBM Plex Mono", letter_spacing=2)
    # icon centered
    add_icon(SID, icn, x0 + (pw // 2) - 24, py + 56, size=48, color=clr)
    # label
    add_text(SID, label, "heading",
             x0 + 12, py + 124, pw - 24, 28,
             color=CLOUD, font_size=18, font_weight=700, text_align="center")
    # sublabel
    add_text(SID, sub, "caption",
             x0 + 12, py + 156, pw - 24, 60,
             color=SLATE, font_size=11, font_weight=500, line_height=1.4,
             font_family="IBM Plex Mono", text_align="center")

    # connector chevron
    if i < 5:
        cx0 = x0 + pw - 4
        add_icon(SID, "ChevronRight", cx0, py + ph + 2, size=20, color=clr)

# Lower band: quarantine + governance metadata
add_shape(SID, "rectangle", 48, 528, 1184, 96, fill=PANEL, stroke=PANEL_LIGHT, stroke_width=1)
add_shape(SID, "rectangle", 48, 528, 4, 96, fill=VIOLET)

add_text(SID, "GOVERNANCE LAYER", "caption",
         72, 548, 280, 18,
         color=VIOLET, font_size=11, font_weight=600,
         font_family="IBM Plex Mono", letter_spacing=2)

gov = [
    ("Lock",    "Auth & PII redaction"),
    ("Eye",     "Audit log per decision"),
    ("Repeat",  "Reversible side effects"),
    ("Users",   "Human-in-the-loop queue"),
]
gx = 72
gw = 270
for i, (icn, label) in enumerate(gov):
    x0 = gx + i * gw
    add_icon(SID, icn, x0, 580, size=22, color=CYAN)
    add_text(SID, label, "paragraph",
             x0 + 32, 582, gw - 40, 22,
             color=CLOUD, font_size=14, font_weight=500)

# bottom editorial line
add_text(SID, "Every layer is permission to say no — and the architecture to recover gracefully.", "caption",
         48, 668, 1184, 22,
         color=SLATE, font_size=12, font_weight=400, font_family="Inter")


# =====================================================================
# ASSEMBLE
# =====================================================================

# attach text elements into slides
for slide in slides_content:
    slide["textElements"] = text_by_slide[slide["id"]]

# count elements
text_count = sum(len(text_by_slide[s["id"]]) for s in slides_content)
total_elements = (text_count + len(shapes_content) + len(images_content)
                  + len(icons_content) + len(charts_content) + len(tables_content))

content_file = {
    "slides": slides_content,
    "imageElements": images_content,
    "shapeElements": shapes_content,
    "chartElements": charts_content,
    "tableElements": tables_content,
    "iconElements": icons_content,
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

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": DECK_ID,
        "title": "Shipping Intelligence — Slides 6–10",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": total_elements,
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

OUT = "deck_batch_6_10.json"
with open(OUT, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Output: {OUT}, {len(slides_content)} slides, {total_elements} elements")
