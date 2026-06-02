#!/usr/bin/env python3
"""Build slides 11-15 for 'Shipping Intelligence: ML Deployment in Production'."""
import json
import time

NOW = int(time.time() * 1000)
COUNTER = 600  # element IDs start at 601

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

def nextz_from_id(n):
    return n  # zIndex matches element id number

# ---------- helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              font_family="Inter", text_align="left", letter_spacing=0):
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
               fill="#2563EB", stroke=None, stroke_width=0, opacity=1):
    if stroke is None:
        stroke = fill
    content_record = {"id": shape_id, "slideId": slide_id, "groupId": None}
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
              size=64, color="#22D3EE", opacity=1):
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
               font_size=18, table_color="#F8FAFC", table_bg="#0B1F3A"):
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


# ---------- registries ----------
slides_content = []
slides_baselayout = []
text_elements_by_slide = {}  # slide_id -> [content records]
shape_elements = []
image_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}  # slide_id -> {"elements": {...}}

def init_slide(slide_id, order, bg_color="#111827"):
    slides_content.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg_color, "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    text_elements_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    z = nextz_from_id(n)
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, z, NOW, **kwargs)
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    z = nextz_from_id(n)
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, z, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid


def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    z = nextz_from_id(n)
    c, cl = make_icon(iid, slide_id, icon_name, x, y, z, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = next_id()
    cid = f"chart-{n}"
    z = nextz_from_id(n)
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, z, NOW, chart_config)
    chart_elements.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl
    return cid


def add_table(slide_id, x, y, col_widths, row_heights, cells, **kwargs):
    n = next_id()
    tid = f"table-{n}"
    z = nextz_from_id(n)
    c, cl = make_table(tid, slide_id, x, y, z, NOW, col_widths, row_heights, cells, **kwargs)
    table_elements.append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


# Color palette
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


# =========================================================
# SLIDE 11 — Feedback Loops That Learn
# =========================================================
sid = "slide-11"
init_slide(sid, 0, bg_color=GRAPHITE)

# Background subtle navy panel
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=GRAPHITE)
# Soft accent strip top
add_shape(sid, "rectangle", 0, 0, 1280, 4, fill=CYAN, opacity=0.6)

# Top mono label
add_text(sid, "CHAPTER 11  /  CONTINUOUS LEARNING SYSTEMS", "caption",
         80, 56, 600, 20, color=CYAN, font_family="IBM Plex Mono",
         font_size=12, font_weight=500, letter_spacing=3)

# Title
add_text(sid, "Feedback Loops", "title",
         80, 96, 760, 84, color=CLOUD, font_family="Inter",
         font_size=72, font_weight=700, line_height=1.0)
add_text(sid, "That Learn.", "title",
         80, 176, 760, 84, color=CYAN, font_family="Inter",
         font_size=72, font_weight=700, line_height=1.0)

# Subtitle
add_text(sid,
         "Production becomes a learning ecosystem — not a static endpoint.",
         "subheading",
         80, 280, 720, 32, color=MIST, font_family="Inter",
         font_size=20, font_weight=400, line_height=1.4)

# Center flywheel: circle in middle-right area
cx, cy, r = 940, 400, 200

# Outer ring
add_shape(sid, "circle", cx - r, cy - r, r*2, r*2,
          fill=GRAPHITE, stroke=CYAN, stroke_width=2, opacity=0.9)
# Inner ring
add_shape(sid, "circle", cx - 100, cy - 100, 200, 200,
          fill=NAVY, stroke=VIOLET, stroke_width=1, opacity=0.8)

# Center label
add_text(sid, "MODEL", "caption",
         cx - 80, cy - 24, 160, 18, color=CYAN, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=4, text_align="center")
add_text(sid, "FLYWHEEL", "subheading",
         cx - 100, cy - 6, 200, 28, color=CLOUD, font_family="Inter",
         font_size=22, font_weight=600, text_align="center")
add_text(sid, "v2.0", "caption",
         cx - 60, cy + 26, 120, 18, color=AMBER, font_family="IBM Plex Mono",
         font_size=12, font_weight=500, letter_spacing=2, text_align="center")

# 6 nodes around the circle: predictions, actions, labels, evaluation, retraining, redeployment
import math
nodes = [
    ("PREDICTIONS", "Inference at scale", 0),       # right
    ("USER ACTIONS", "Behavior signals", 60),
    ("LABELS", "Annotation queue", 120),
    ("EVALUATION", "Offline + online", 180),       # left
    ("RETRAINING", "Pipeline trigger", 240),
    ("REDEPLOYMENT", "Canary → prod", 300),
]
node_size = 14
for label, sub, deg in nodes:
    rad = math.radians(deg - 90)  # start top
    nx = cx + int(r * math.cos(rad)) - node_size//2
    ny = cy + int(r * math.sin(rad)) - node_size//2
    # node dot
    add_shape(sid, "circle", nx, ny, node_size, node_size,
              fill=CYAN, opacity=1)
    # label position offset further out
    lx = cx + int((r + 30) * math.cos(rad))
    ly = cy + int((r + 30) * math.sin(rad))
    # decide alignment based on angle
    if math.cos(rad) > 0.3:
        tx, ta = lx, "left"
    elif math.cos(rad) < -0.3:
        tx, ta = lx - 180, "right"
    else:
        tx, ta = lx - 90, "center"

    add_text(sid, label, "caption",
             tx, ly - 14, 180, 16, color=CLOUD, font_family="IBM Plex Mono",
             font_size=11, font_weight=600, letter_spacing=2, text_align=ta)
    add_text(sid, sub, "caption",
             tx, ly + 4, 180, 14, color=MIST, font_family="Inter",
             font_size=11, font_weight=400, text_align=ta)

# Version chips on left side
add_text(sid, "VERSION TRAJECTORY", "caption",
         80, 360, 360, 16, color=AMBER, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=3)

# version cards
versions = [("v1.8", "baseline", MIST), ("v1.9", "+6.4% recall", CYAN), ("v2.0", "production", GREEN)]
for i, (v, note, col) in enumerate(versions):
    vy = 396 + i * 60
    add_shape(sid, "rectangle", 80, vy, 360, 48,
              fill=NAVY, stroke=col, stroke_width=1, opacity=0.95)
    add_text(sid, v, "subheading",
             100, vy + 12, 80, 24, color=col, font_family="IBM Plex Mono",
             font_size=18, font_weight=600)
    add_text(sid, note, "caption",
             190, vy + 16, 240, 18, color=CLOUD, font_family="Inter",
             font_size=14, font_weight=400)

# Italic closing line bottom
add_text(sid,
         "The best systems improve because production teaches them.",
         "paragraph",
         80, 624, 760, 28, color=CYAN, font_family="Inter",
         font_size=18, font_weight=500, line_height=1.4)

# Footer caption
add_text(sid, "BILDORY  ·  SHIPPING INTELLIGENCE  ·  11/15", "caption",
         80, 680, 600, 16, color=MIST, font_family="IBM Plex Mono",
         font_size=10, font_weight=500, letter_spacing=3)


# =========================================================
# SLIDE 12 — The Production Control Room
# =========================================================
sid = "slide-12"
init_slide(sid, 1, bg_color=GRAPHITE)

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=GRAPHITE)
add_shape(sid, "rectangle", 0, 0, 1280, 4, fill=CYAN, opacity=0.7)

# Top label and title
add_text(sid, "CHAPTER 12  /  OBSERVABILITY", "caption",
         80, 56, 600, 18, color=CYAN, font_family="IBM Plex Mono",
         font_size=12, font_weight=500, letter_spacing=3)

add_text(sid, "The Production Control Room.", "title",
         80, 90, 1120, 64, color=CLOUD, font_family="Inter",
         font_size=52, font_weight=700, line_height=1.05)

add_text(sid,
         "Live signals, live decisions. Monitoring turns deployment into an operating system.",
         "paragraph",
         80, 168, 900, 26, color=MIST, font_family="Inter",
         font_size=18, font_weight=400, line_height=1.4)

# Central Model Health console (large card)
add_shape(sid, "rectangle", 80, 224, 720, 384,
          fill=NAVY, stroke=CYAN, stroke_width=1, opacity=0.95)

# Console header
add_text(sid, "MODEL HEALTH CONSOLE", "caption",
         104, 248, 400, 16, color=CYAN, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=3)

# Live indicator dot
add_shape(sid, "circle", 760, 248, 12, 12, fill=GREEN)
add_text(sid, "LIVE", "caption",
         714, 248, 40, 16, color=GREEN, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=2, text_align="right")

add_text(sid, "fraud-detector  ·  v2.0", "subheading",
         104, 274, 600, 32, color=CLOUD, font_family="Inter",
         font_size=24, font_weight=600)
add_text(sid, "Region: us-east-1   ·   Replicas: 12   ·   Deployed: 2026-05-18 14:22 UTC",
         "caption", 104, 312, 600, 16, color=MIST, font_family="IBM Plex Mono",
         font_size=12, font_weight=400)

# Sparkline chart inside console
spark_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {"type": "category",
              "data": ["00:00","02:00","04:00","06:00","08:00","10:00","12:00","14:00","16:00","18:00","20:00","22:00"],
              "axisLine": {"lineStyle": {"color": "#475569"}},
              "axisLabel": {"color": "#94a3b8", "fontSize": 10},
              "splitLine": {"show": False}},
    "yAxis": {"type": "value",
              "axisLine": {"lineStyle": {"color": "#475569"}},
              "axisLabel": {"color": "#94a3b8", "fontSize": 10},
              "splitLine": {"lineStyle": {"color": "#1e293b"}}},
    "grid": {"left": 40, "right": 16, "top": 16, "bottom": 28},
    "series": [{"type": "line", "data": [42, 44, 41, 45, 48, 52, 58, 61, 59, 56, 51, 47],
                "smooth": True, "symbol": "none",
                "lineStyle": {"width": 2, "color": "#22D3EE"},
                "areaStyle": {"color": "#22D3EE", "opacity": 0.18}}],
    "backgroundColor": "transparent",
    "color": ["#22D3EE"],
    "animation": False,
    "textStyle": {"color": "#F8FAFC", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": ["00:00","02:00","04:00","06:00","08:00","10:00","12:00","14:00","16:00","18:00","20:00","22:00"],
                  "series": [{"name": "Requests/s", "data": [42,44,41,45,48,52,58,61,59,56,51,47]}]},
    "properties": {"showXAxis": True, "showYAxis": True, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 12, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#22D3EE"},
    "textColor": "#F8FAFC", "isMonochrome": False
}
add_chart(sid, "line", 104, 360, 672, 224, spark_cfg)

# bottom timestamp inside console
add_text(sid, "PREDICTIONS / SECOND  ·  TRAILING 24H", "caption",
         104, 588, 400, 14, color=MIST, font_family="IBM Plex Mono",
         font_size=10, font_weight=500, letter_spacing=2)

# 4 KPI cards on right side, 2x2 grid
kpis = [
    ("LATENCY p95", "47ms", "↓ 6ms vs baseline", GREEN),
    ("THROUGHPUT", "61k/s", "+12% week", CYAN),
    ("ERROR RATE", "0.04%", "within SLA", GREEN),
    ("DRIFT SCORE", "0.18", "warn @ 0.25", AMBER),
]
for i, (label, value, delta, col) in enumerate(kpis):
    row = i // 2
    colx = i % 2
    kx = 824 + colx * 196
    ky = 224 + row * 196
    add_shape(sid, "rectangle", kx, ky, 180, 180,
              fill=NAVY, stroke=col, stroke_width=1, opacity=0.95)
    add_text(sid, label, "caption",
             kx + 16, ky + 16, 148, 14, color=MIST, font_family="IBM Plex Mono",
             font_size=10, font_weight=600, letter_spacing=2)
    add_text(sid, value, "title",
             kx + 16, ky + 50, 148, 56, color=col, font_family="Inter",
             font_size=42, font_weight=700, line_height=1.0)
    add_text(sid, delta, "caption",
             kx + 16, ky + 130, 148, 32, color=CLOUD, font_family="Inter",
             font_size=12, font_weight=400, line_height=1.3)

# Footer
add_text(sid,
         "Monitoring turns deployment into an operating system.",
         "paragraph", 80, 632, 800, 26, color=CYAN, font_family="Inter",
         font_size=18, font_weight=500)
add_text(sid, "BILDORY  ·  12/15", "caption",
         1080, 680, 140, 16, color=MIST, font_family="IBM Plex Mono",
         font_size=10, font_weight=500, letter_spacing=3, text_align="right")


# =========================================================
# SLIDE 13 — Drift Is the Silent Failure
# =========================================================
sid = "slide-13"
init_slide(sid, 2, bg_color="#0F172A")

add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#0F172A")
add_shape(sid, "rectangle", 0, 0, 1280, 4, fill=AMBER, opacity=0.7)

# Top label
add_text(sid, "CHAPTER 13  /  DISTRIBUTION SHIFT", "caption",
         80, 56, 600, 18, color=AMBER, font_family="IBM Plex Mono",
         font_size=12, font_weight=500, letter_spacing=3)

# Title across the top
add_text(sid, "Drift Is the Silent Failure.", "title",
         80, 90, 1120, 64, color=CLOUD, font_family="Inter",
         font_size=52, font_weight=700, line_height=1.05)

add_text(sid,
         "Models do not break loudly. They drift quietly while the world rearranges itself.",
         "paragraph", 80, 168, 1000, 26, color=MIST, font_family="Inter",
         font_size=18, font_weight=400)

# Two side-by-side panels
# Left: Training distribution
add_shape(sid, "rectangle", 80, 224, 540, 304,
          fill=NAVY, stroke="#334155", stroke_width=1, opacity=0.95)
add_text(sid, "TRAINING WORLD", "caption",
         104, 244, 300, 14, color=CYAN, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=3)
add_text(sid, "Stable distribution", "subheading",
         104, 268, 400, 28, color=CLOUD, font_family="Inter",
         font_size=20, font_weight=600)

# Histogram chart
train_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {"type": "category",
              "data": ["μ-3","μ-2","μ-1","μ","μ+1","μ+2","μ+3"],
              "axisLine": {"lineStyle": {"color": "#475569"}},
              "axisLabel": {"color": "#94a3b8", "fontSize": 10},
              "splitLine": {"show": False}},
    "yAxis": {"type": "value", "show": False,
              "axisLine": {"show": False},
              "axisLabel": {"show": False},
              "splitLine": {"show": False}},
    "grid": {"left": 16, "right": 16, "top": 16, "bottom": 28},
    "series": [{"type": "bar", "data": [4, 12, 28, 42, 28, 12, 4],
                "itemStyle": {"color": "#22D3EE"}, "barWidth": "60%"}],
    "backgroundColor": "transparent",
    "color": ["#22D3EE"],
    "animation": False,
    "textStyle": {"color": "#F8FAFC", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": ["μ-3","μ-2","μ-1","μ","μ+1","μ+2","μ+3"],
                  "series": [{"name": "Train", "data": [4,12,28,42,28,12,4]}]},
    "properties": {"showXAxis": True, "showYAxis": False, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 12, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#22D3EE"},
    "textColor": "#F8FAFC", "isMonochrome": False
}
add_chart(sid, "bar", 104, 312, 488, 168, train_cfg)

add_text(sid, "PSI = 0.00   ·   KL = 0.00   ·   STABLE", "caption",
         104, 492, 400, 16, color=MIST, font_family="IBM Plex Mono",
         font_size=11, font_weight=500, letter_spacing=2)

# Right: Production distribution
add_shape(sid, "rectangle", 660, 224, 540, 304,
          fill=NAVY, stroke=AMBER, stroke_width=1, opacity=0.95)
add_text(sid, "PRODUCTION WORLD", "caption",
         684, 244, 300, 14, color=AMBER, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=3)
add_text(sid, "Distribution drift detected", "subheading",
         684, 268, 460, 28, color=CLOUD, font_family="Inter",
         font_size=20, font_weight=600)

prod_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {"type": "category",
              "data": ["μ-3","μ-2","μ-1","μ","μ+1","μ+2","μ+3"],
              "axisLine": {"lineStyle": {"color": "#475569"}},
              "axisLabel": {"color": "#94a3b8", "fontSize": 10},
              "splitLine": {"show": False}},
    "yAxis": {"type": "value", "show": False,
              "axisLine": {"show": False},
              "axisLabel": {"show": False},
              "splitLine": {"show": False}},
    "grid": {"left": 16, "right": 16, "top": 16, "bottom": 28},
    "series": [{"type": "bar", "data": [2, 6, 14, 26, 36, 24, 8],
                "itemStyle": {"color": "#F59E0B"}, "barWidth": "60%"}],
    "backgroundColor": "transparent",
    "color": ["#F59E0B"],
    "animation": False,
    "textStyle": {"color": "#F8FAFC", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": ["μ-3","μ-2","μ-1","μ","μ+1","μ+2","μ+3"],
                  "series": [{"name": "Prod", "data": [2,6,14,26,36,24,8]}]},
    "properties": {"showXAxis": True, "showYAxis": False, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 12, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#F59E0B"},
    "textColor": "#F8FAFC", "isMonochrome": False
}
add_chart(sid, "bar", 684, 312, 488, 168, prod_cfg)

add_text(sid, "PSI = 0.27   ·   KL = 0.18   ·   ALERT", "caption",
         684, 492, 400, 16, color=AMBER, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=2)

# Central divergence line (vertical)
add_shape(sid, "rectangle", 638, 224, 2, 304, fill=AMBER, opacity=0.7)
# divergence diamond
add_shape(sid, "rectangle", 626, 360, 28, 28, fill="#0F172A",
          stroke=AMBER, stroke_width=2, opacity=1)
add_text(sid, "Δ", "subheading",
         626, 363, 28, 24, color=AMBER, font_family="Inter",
         font_size=20, font_weight=700, text_align="center")

# Bottom row: 4 drift type callouts
drift_types = [
    ("FEATURE DRIFT", "Inputs change shape", VIOLET),
    ("CONCEPT DRIFT", "Target relationships shift", CYAN),
    ("LABEL DRIFT", "Class balance evolves", AMBER),
    ("PREDICTION DRIFT", "Output distribution shifts", CRIMSON),
]
for i, (label, sub, col) in enumerate(drift_types):
    bx = 80 + i * 280
    add_shape(sid, "rectangle", bx, 552, 264, 96,
              fill=NAVY, stroke=col, stroke_width=1, opacity=0.95)
    # left accent bar
    add_shape(sid, "rectangle", bx, 552, 4, 96, fill=col)
    add_text(sid, label, "caption",
             bx + 20, bx and 568, 240, 16, color=col, font_family="IBM Plex Mono",
             font_size=11, font_weight=600, letter_spacing=2)
    add_text(sid, sub, "paragraph",
             bx + 20, 596, 230, 40, color=CLOUD, font_family="Inter",
             font_size=15, font_weight=400, line_height=1.3)

# Footer
add_text(sid, "BILDORY  ·  13/15", "caption",
         1080, 680, 140, 16, color=MIST, font_family="IBM Plex Mono",
         font_size=10, font_weight=500, letter_spacing=3, text_align="right")


# =========================================================
# SLIDE 14 — Optimizing for Speed, Cost, and Trust
# =========================================================
sid = "slide-14"
init_slide(sid, 3, bg_color=CLOUD)

add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=CLOUD)
add_shape(sid, "rectangle", 0, 0, 1280, 4, fill=GRAPHITE, opacity=1)

# Top label
add_text(sid, "CHAPTER 14  /  OPTIMIZATION PLAYBOOK", "caption",
         80, 56, 600, 18, color=SIGNAL, font_family="IBM Plex Mono",
         font_size=12, font_weight=500, letter_spacing=3)

# Title
add_text(sid, "Speed.  Cost.  Trust.", "title",
         80, 90, 1120, 64, color=GRAPHITE, font_family="Inter",
         font_size=52, font_weight=700, line_height=1.05)

add_text(sid,
         "Three optimization frontiers — pursued together, not in sequence.",
         "paragraph", 80, 168, 1000, 26, color="#475569", font_family="Inter",
         font_size=18, font_weight=400)

# Three column matrix: Performance, Cost, Reliability
columns = [
    {
        "title": "PERFORMANCE",
        "subtitle": "Lower latency. Higher throughput.",
        "color": SIGNAL,
        "icon": "Zap",
        "techniques": [
            ("Quantization", "INT8 / FP16", "−42% p95"),
            ("Batching", "Dynamic micro-batch", "+3.4× QPS"),
            ("Distillation", "Teacher → student", "−61% size"),
        ],
    },
    {
        "title": "COST",
        "subtitle": "Right-sized infrastructure.",
        "color": GREEN,
        "icon": "TrendingDown",
        "techniques": [
            ("Autoscaling", "HPA on req/sec", "−38% spend"),
            ("Caching", "Embedding LRU", "−27% calls"),
            ("Hardware mix", "GPU + CPU lanes", "1.9× $/req"),
        ],
    },
    {
        "title": "RELIABILITY",
        "subtitle": "Trust under load.",
        "color": VIOLET,
        "icon": "Shield",
        "techniques": [
            ("Canary rollout", "5 → 25 → 100%", "0 incidents"),
            ("Rollback safety", "Auto-revert SLO", "<90s MTTR"),
            ("Shadow traffic", "Pre-prod replay", "99.97% SLA"),
        ],
    },
]

col_w = 384
gap = 16
start_x = 80

for i, c in enumerate(columns):
    cx = start_x + i * (col_w + gap)

    # Column header card
    add_shape(sid, "rectangle", cx, 224, col_w, 96,
              fill=GRAPHITE, opacity=1)
    # Accent bar top
    add_shape(sid, "rectangle", cx, 224, col_w, 4, fill=c["color"])

    # Icon
    add_icon(sid, c["icon"], cx + 24, 248, size=40, color=c["color"])

    add_text(sid, c["title"], "caption",
             cx + 80, 248, col_w - 100, 16, color=c["color"], font_family="IBM Plex Mono",
             font_size=12, font_weight=600, letter_spacing=3)
    add_text(sid, c["subtitle"], "subheading",
             cx + 80, 270, col_w - 100, 28, color=CLOUD, font_family="Inter",
             font_size=18, font_weight=500)

    # 3 technique cards under header
    for j, (name, detail, metric) in enumerate(c["techniques"]):
        ty = 336 + j * 100
        add_shape(sid, "rectangle", cx, ty, col_w, 88,
                  fill="#ffffff", stroke=MIST, stroke_width=1, opacity=1)
        # left accent bar
        add_shape(sid, "rectangle", cx, ty, 4, 88, fill=c["color"], opacity=0.7)

        add_text(sid, name, "subheading",
                 cx + 20, ty + 14, col_w - 40, 24, color=GRAPHITE,
                 font_family="Inter", font_size=18, font_weight=600)
        add_text(sid, detail, "caption",
                 cx + 20, ty + 40, col_w - 140, 16, color="#64748B",
                 font_family="IBM Plex Mono", font_size=12, font_weight=500)
        # metric badge right side
        add_shape(sid, "rectangle", cx + col_w - 124, ty + 38, 104, 28,
                  fill=c["color"], opacity=0.12)
        add_text(sid, metric, "caption",
                 cx + col_w - 124, ty + 44, 104, 18, color=c["color"],
                 font_family="IBM Plex Mono", font_size=12, font_weight=600,
                 letter_spacing=1, text_align="center")

# Footer
add_text(sid,
         "Optimization is a loop, not a checklist — each pass earns the next.",
         "paragraph", 80, 660, 800, 22, color="#475569", font_family="Inter",
         font_size=16, font_weight=500)
add_text(sid, "BILDORY  ·  14/15", "caption",
         1080, 686, 140, 16, color="#64748B", font_family="IBM Plex Mono",
         font_size=10, font_weight=500, letter_spacing=3, text_align="right")


# =========================================================
# SLIDE 15 — From Model to Living System
# =========================================================
sid = "slide-15"
init_slide(sid, 4, bg_color=NAVY)

add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=NAVY)

# Subtle gradient accent shapes (soft glow)
add_shape(sid, "circle", -200, -200, 700, 700, fill=SIGNAL, opacity=0.08)
add_shape(sid, "circle", 800, 400, 700, 700, fill=CYAN, opacity=0.08)

add_shape(sid, "rectangle", 0, 0, 1280, 4, fill=CYAN, opacity=0.7)

# Top label
add_text(sid, "CHAPTER 15  /  CLOSING TRANSMISSION", "caption",
         80, 56, 600, 18, color=CYAN, font_family="IBM Plex Mono",
         font_size=12, font_weight=500, letter_spacing=3)

# Title
add_text(sid, "From Model", "title",
         80, 96, 760, 84, color=CLOUD, font_family="Inter",
         font_size=72, font_weight=700, line_height=1.0)
add_text(sid, "to Living System.", "title",
         80, 176, 760, 84, color=CYAN, font_family="Inter",
         font_size=72, font_weight=700, line_height=1.0)

# Central lifecycle loop (horizontal across middle)
# Outer track shape
add_shape(sid, "rectangle", 80, 304, 1120, 220,
          fill="#0a1730", stroke=CYAN, stroke_width=1, opacity=0.6)

# Lifecycle 6 stages
stages = [
    ("DATA", "ingestion + lineage", "Database", VIOLET),
    ("TRAINING", "experimentation", "Cpu", SIGNAL),
    ("REGISTRY", "governed artifacts", "Archive", CYAN),
    ("DEPLOYMENT", "canary + rollout", "Rocket", GREEN),
    ("MONITORING", "drift + SLO", "Activity", AMBER),
    ("FEEDBACK", "labels + retrain", "RefreshCw", CYAN),
]

stage_w = 168
stage_gap = 16
total_w = len(stages) * stage_w + (len(stages) - 1) * stage_gap
sx0 = (1280 - total_w) // 2

for i, (name, sub, icon, col) in enumerate(stages):
    sx = sx0 + i * (stage_w + stage_gap)
    sy = 332
    # card
    add_shape(sid, "rectangle", sx, sy, stage_w, 164,
              fill=GRAPHITE, stroke=col, stroke_width=1, opacity=0.95)
    # top accent
    add_shape(sid, "rectangle", sx, sy, stage_w, 3, fill=col)
    # icon centered
    add_icon(sid, icon, sx + (stage_w - 48) // 2, sy + 20, size=48, color=col)
    # stage number
    add_text(sid, f"0{i+1}", "caption",
             sx + 12, sy + 12, 32, 14, color=MIST, font_family="IBM Plex Mono",
             font_size=10, font_weight=500, letter_spacing=2)
    # name
    add_text(sid, name, "subheading",
             sx, sy + 80, stage_w, 24, color=CLOUD, font_family="Inter",
             font_size=16, font_weight=600, text_align="center")
    # sub
    add_text(sid, sub, "caption",
             sx + 8, sy + 110, stage_w - 16, 32, color=MIST, font_family="Inter",
             font_size=12, font_weight=400, line_height=1.3, text_align="center")

    # connector arrow between stages
    if i < len(stages) - 1:
        ax = sx + stage_w
        ay = sy + 80
        add_shape(sid, "rectangle", ax, ay, stage_gap, 2, fill=CYAN, opacity=0.7)

# Governance layer above
add_shape(sid, "rectangle", 80, 264, 1120, 32, fill="#0a1730",
          stroke=VIOLET, stroke_width=1, opacity=0.9)
add_text(sid, "HUMAN GOVERNANCE  ·  POLICY  ·  SECURITY  ·  COMPLIANCE  ·  EXPERIMENTATION",
         "caption", 80, 272, 1120, 16, color=VIOLET, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=4, text_align="center")

# Business outcomes layer below
add_shape(sid, "rectangle", 80, 528, 1120, 32, fill="#0a1730",
          stroke=GREEN, stroke_width=1, opacity=0.9)
add_text(sid, "BUSINESS OUTCOMES  ·  REVENUE  ·  RELIABILITY  ·  TRUST  ·  CONTINUOUS IMPROVEMENT",
         "caption", 80, 536, 1120, 16, color=GREEN, font_family="IBM Plex Mono",
         font_size=11, font_weight=600, letter_spacing=4, text_align="center")

# Closing keynote line
add_text(sid, "Deployment is not the finish line —",
         "subheading", 80, 588, 1120, 32, color=CLOUD, font_family="Inter",
         font_size=24, font_weight=400, line_height=1.3)
add_text(sid, "it is the operating system of intelligence.",
         "subheading", 80, 622, 1120, 32, color=CYAN, font_family="Inter",
         font_size=24, font_weight=600, line_height=1.3)

# Footer caption
add_text(sid, "BILDORY  ·  SHIPPING INTELLIGENCE  ·  END  ·  15/15", "caption",
         80, 684, 1120, 16, color=MIST, font_family="IBM Plex Mono",
         font_size=10, font_weight=500, letter_spacing=4, text_align="right")


# =========================================================
# Wire up content slides with their text elements
# =========================================================
for s in slides_content:
    s["textElements"] = text_elements_by_slide[s["id"]]

# Element count
element_count = (
    sum(len(text_elements_by_slide[s["id"]]) for s in slides_content)
    + len(image_elements) + len(shape_elements) + len(chart_elements)
    + len(table_elements) + len(icon_elements)
)

slide_count = len(slides_content)

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
        "_id": f"deck-shipping-intelligence-batch3-{NOW}",
        "title": "Shipping Intelligence: ML Deployment in Production (Slides 11-15)",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": slide_count,
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

filename = "deck.json"
with open(filename, "w") as f:
    json.dump(deck, f, indent=2)

print(f"Output: {filename}, {slide_count} slides, {element_count} elements")
