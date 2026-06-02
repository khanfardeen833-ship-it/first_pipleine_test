import json, time

NOW = int(time.time() * 1000)
COUNTER = 300

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None,
              line_height=None, text_align="left"):
    DEFAULTS = {
        "title":      (60, 700, 1.05),
        "subtitle":   (40, 600, 1.35),
        "heading":    (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph":  (22, 700, 1.50),
        "caption":    (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None: fs = font_size
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
            "fontSize": fs, "fontFamily": "Space Grotesk", "color": color,
            "textAlign": text_align, "lineHeight": lh, "letterSpacing": 0,
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
    if stroke is None: stroke = fill
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
              size=80, color="#c67c3a", opacity=1):
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
        "svgDataUrl": "", "chartType": chart_type, "chartConfig": chart_config
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "updatedAt": now, "chartType": chart_type
    }
    return content_record, changelog_record

def make_table(table_id, slide_id, x, y, zidx, now,
               col_widths, row_heights, cells,
               font_size=20, table_color="#1c1917", table_bg="#ffffff"):
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

# ---------- Containers ----------
content_slides = []
text_by_slide = {}
shape_content = []
image_content = []
icon_content = []
chart_content = []
table_content = []
changelog_slides = {}

def init_slide(slide_id, order, bg):
    content_slides.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg, "textElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

def add_text(slide_id, text, type_, x, y, w, h, **kw):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kw)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

def add_shape(slide_id, shape_type, x, y, w, h, **kw):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kw)
    shape_content.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

def add_icon(slide_id, icon_name, x, y, **kw):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kw)
    icon_content.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = next_id()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, NOW, chart_config)
    chart_content.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl

def add_table(slide_id, x, y, col_widths, row_heights, cells, **kw):
    n = next_id()
    tid = f"table-{n}"
    c, cl = make_table(tid, slide_id, x, y, n, NOW, col_widths, row_heights, cells, **kw)
    table_content.append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

# =====================================================
# SLIDE 6 — AI in Healthcare
# =====================================================
sid = "slide-6"
init_slide(sid, 0, "#f5f0e8")

# Accent bar
add_shape(sid, "rectangle", 48, 48, 8, 80, fill="#c67c3a")
# Section label
add_text(sid, "TREND 06 — HEALTHCARE", "caption", 72, 56, 400, 24, color="#c67c3a")
add_text(sid, "AI matches radiologists at human-level accuracy", "title",
         48, 96, 1184, 140, font_size=52, line_height=1.1)
add_text(sid,
         "Across CT, MRI, and X-ray modalities, AI diagnostic systems now exceed average specialist accuracy — cutting time-to-diagnosis by 64%.",
         "paragraph", 48, 252, 1184, 80, font_size=22, font_weight=500, line_height=1.5)

# Chart - bar comparison
chart_config = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": ["CT Scan", "MRI", "X-Ray", "Ultrasound", "Pathology"],
        "axisLabel": {"color": "#1c1917", "fontSize": 14}
    },
    "yAxis": {
        "type": "value",
        "axisLabel": {"color": "#1c1917", "fontSize": 14}
    },
    "series": [
        {"type": "bar", "name": "Radiologists", "data": [82, 79, 85, 77, 81]},
        {"type": "bar", "name": "AI Systems",   "data": [94, 91, 96, 89, 95]}
    ],
    "backgroundColor": "transparent",
    "color": ["#1c1917", "#c67c3a"],
    "animation": False,
    "textStyle": {"color": "#1c1917", "fontSize": 14, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["CT Scan","MRI","X-Ray","Ultrasound","Pathology"],
        "series": [
            {"name": "Radiologists", "data": [82,79,85,77,81]},
            {"name": "AI Systems",   "data": [94,91,96,89,95]}
        ]
    },
    "properties": {"showXAxis": True, "showYAxis": True, "showDataLabels": False,
                   "showLegend": True, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 14, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": False,
    "customSeriesColors": {"0": "#1c1917", "1": "#c67c3a"},
    "textColor": "#1c1917", "isMonochrome": False
}
add_chart(sid, "bar", 48, 352, 720, 320, chart_config)

# Right side stats
add_shape(sid, "rectangle", 800, 352, 432, 320, fill="#ffffff", opacity=1)
add_text(sid, "+73%", "title", 824, 376, 384, 80, font_size=72, color="#c67c3a")
add_text(sid, "Faster diagnosis vs. 2024", "subheading", 824, 460, 384, 32, font_weight=500)
add_text(sid, "12,400+", "heading", 824, 512, 384, 48, font_size=44, color="#1c1917")
add_text(sid, "Hospitals deploying AI tools globally", "caption", 824, 568, 384, 24, font_weight=500)
add_text(sid, "Source: WHO Digital Health Report 2026", "caption", 824, 632, 384, 24,
         color="#666666", font_size=14)

# =====================================================
# SLIDE 7 — Edge AI Explosion
# =====================================================
sid = "slide-7"
init_slide(sid, 1, "#1c1917")

add_text(sid, "TREND 07 — EDGE COMPUTE", "caption", 48, 56, 400, 24, color="#c67c3a")
add_text(sid, "AI leaves the cloud and moves to the device", "title",
         48, 96, 1184, 140, color="#ffffff", font_size=52, line_height=1.1)
add_text(sid,
         "Sub-1B parameter models now power on-device assistants, vision, and translation — without ever touching a data center.",
         "paragraph", 48, 252, 1184, 60, color="#f5f0e8", font_size=22, font_weight=500)

# 4 stat cards
cards_x = [48, 352, 656, 960]
icons = ["Cpu", "Smartphone", "Zap", "Lock"]
stats = ["8.2B", "<50ms", "92%", "100%"]
labels = ["Edge AI devices shipping in 2026",
          "Median on-device inference latency",
          "Reduction in cloud API calls",
          "Of inference happens privately"]

for i in range(4):
    add_shape(sid, "rectangle", cards_x[i], 360, 272, 300,
              fill="#2a2520", opacity=1)
    add_icon(sid, icons[i], cards_x[i] + 24, 384, size=56, color="#c67c3a")
    add_text(sid, stats[i], "title", cards_x[i] + 24, 456, 224, 80,
             color="#ffffff", font_size=48)
    add_text(sid, labels[i], "paragraph", cards_x[i] + 24, 540, 224, 100,
             color="#f5f0e8", font_size=18, font_weight=500, line_height=1.4)

# =====================================================
# SLIDE 8 — Global AI Regulation
# =====================================================
sid = "slide-8"
init_slide(sid, 2, "#ffffff")

add_shape(sid, "rectangle", 48, 48, 8, 80, fill="#c67c3a")
add_text(sid, "TREND 08 — REGULATION", "caption", 72, 56, 400, 24, color="#c67c3a")
add_text(sid, "Four AI superpowers, four very different rulebooks", "title",
         48, 96, 1184, 140, font_size=44, line_height=1.15)
add_text(sid,
         "By mid-2026, the regulatory landscape has fractured along regional priorities — enterprise compliance teams now manage 3–5 parallel frameworks.",
         "paragraph", 48, 240, 1184, 60, font_size=20, font_weight=500, line_height=1.45)

# Table - regulatory comparison
header_style = {"bold": True, "bg": "#1c1917", "color": "#ffffff"}
row_style = {"bold": False, "bg": "#ffffff", "color": "#1c1917"}
alt_style = {"bold": False, "bg": "#f5f0e8", "color": "#1c1917"}

cells = {
    "0-0": {"text": "Region", **header_style},
    "0-1": {"text": "Approach", **header_style},
    "0-2": {"text": "Key Rule", **header_style},
    "0-3": {"text": "Penalty Cap", **header_style},

    "1-0": {"text": "European Union", **row_style},
    "1-1": {"text": "Risk-tiered", **row_style},
    "1-2": {"text": "Mandatory model audits", **row_style},
    "1-3": {"text": "7% global revenue", **row_style},

    "2-0": {"text": "United States", **alt_style},
    "2-1": {"text": "Sector-specific", **alt_style},
    "2-2": {"text": "Disclosure + red team", **alt_style},
    "2-3": {"text": "$50M per violation", **alt_style},

    "3-0": {"text": "China", **row_style},
    "3-1": {"text": "State-aligned", **row_style},
    "3-2": {"text": "Content + model registry", **row_style},
    "3-3": {"text": "License revocation", **row_style},

    "4-0": {"text": "United Kingdom", **alt_style},
    "4-1": {"text": "Principles-based", **alt_style},
    "4-2": {"text": "Regulator-led guidance", **alt_style},
    "4-3": {"text": "Discretionary", **alt_style},
}
add_table(sid, 48, 336,
          col_widths=[256, 256, 416, 256],
          row_heights=[64, 56, 56, 56, 56],
          cells=cells, font_size=18)

add_text(sid, "Source: Stanford AI Index 2026 · OECD Policy Observatory",
         "caption", 48, 656, 1184, 24, color="#666666", font_size=14)

# =====================================================
# SLIDE 9 — Sustainable AI
# =====================================================
sid = "slide-9"
init_slide(sid, 3, "#c8f5e4")

add_text(sid, "TREND 09 — SUSTAINABILITY", "caption", 48, 56, 400, 24, color="#1c1917",
         font_weight=700)
add_text(sid, "Inference now costs 1/40th the energy of 2023", "title",
         48, 96, 1184, 140, font_size=48, line_height=1.1)
add_text(sid,
         "Sparse mixture-of-experts, 4-bit quantization, and analog accelerators have collapsed the energy curve — making AI cheaper per token than search.",
         "paragraph", 48, 248, 1184, 80, font_size=20, font_weight=500, line_height=1.5)

# Line chart - watts per inference
chart_config = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": ["2023", "2024 H1", "2024 H2", "2025 H1", "2025 H2", "2026 Q1", "2026 Q2"],
        "axisLabel": {"color": "#1c1917", "fontSize": 14}
    },
    "yAxis": {
        "type": "value",
        "axisLabel": {"color": "#1c1917", "fontSize": 14}
    },
    "series": [{
        "type": "line",
        "name": "Joules per 1K tokens",
        "data": [40.0, 28.5, 18.2, 9.4, 4.8, 2.1, 1.0],
        "smooth": True,
        "lineStyle": {"width": 4, "color": "#1c1917"},
        "itemStyle": {"color": "#1c1917"},
        "areaStyle": {"color": "#1c1917", "opacity": 0.15}
    }],
    "backgroundColor": "transparent",
    "color": ["#1c1917"],
    "animation": False,
    "textStyle": {"color": "#1c1917", "fontSize": 14, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["2023","2024 H1","2024 H2","2025 H1","2025 H2","2026 Q1","2026 Q2"],
        "series": [{"name": "Joules per 1K tokens", "data": [40.0, 28.5, 18.2, 9.4, 4.8, 2.1, 1.0]}]
    },
    "properties": {"showXAxis": True, "showYAxis": True, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 14, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": False,
    "customSeriesColors": {"0": "#1c1917"},
    "textColor": "#1c1917", "isMonochrome": False
}
add_chart(sid, "line", 48, 360, 720, 312, chart_config)

# Right side metrics
add_shape(sid, "rectangle", 800, 360, 432, 312, fill="#ffffff", opacity=1)
add_icon(sid, "Leaf", 824, 384, size=56, color="#1c9961")
add_text(sid, "−97.5%", "title", 824, 456, 384, 80, font_size=60, color="#1c1917")
add_text(sid, "Joules per token vs. 2023 baseline", "subheading",
         824, 532, 384, 32, font_weight=500)
add_text(sid, "Carbon-neutral training is now the industry default for frontier labs.",
         "paragraph", 824, 580, 384, 80, font_size=18, font_weight=500, line_height=1.45)

# =====================================================
# SLIDE 10 — The Road Ahead
# =====================================================
sid = "slide-10"
init_slide(sid, 4, "#14204e")

# Big accent block
add_shape(sid, "rectangle", 0, 0, 480, 720, fill="#c67c3a")
add_text(sid, "10", "title", 96, 80, 384, 240, font_size=240, color="#ffffff",
         font_weight=700, line_height=1)
add_text(sid, "THE ROAD AHEAD", "caption", 96, 336, 384, 24, color="#1c1917",
         font_weight=700)
add_text(sid, "What comes next in 2027", "heading", 96, 376, 384, 80,
         color="#ffffff", font_size=28, line_height=1.2)
add_text(sid, "Bildory · AI Trends Report", "caption", 96, 640, 384, 24,
         color="#1c1917", font_weight=700)

# Right column predictions
add_text(sid, "Three things to watch", "subtitle", 528, 80, 704, 56,
         color="#ffffff", font_size=36)

predictions = [
    ("Globe", "Sovereign AI",
     "By Q3 2027, 14+ nations will operate state-funded foundation models trained on local data."),
    ("Brain", "Agent-to-agent economies",
     "Autonomous agents transacting with each other will represent 18% of B2B software spending."),
    ("ShieldCheck", "Verified provenance",
     "C2PA-style content credentials will be required on all public media in the EU and Japan."),
]

y0 = 168
for i, (icon, title, body) in enumerate(predictions):
    y = y0 + i * 156
    add_icon(sid, icon, 528, y, size=56, color="#c67c3a")
    add_text(sid, title, "heading", 608, y + 4, 624, 40,
             color="#ffffff", font_size=26)
    add_text(sid, body, "paragraph", 608, y + 48, 624, 100,
             color="#e9defc", font_size=18, font_weight=500, line_height=1.5)

# Closing line
add_shape(sid, "rectangle", 528, 640, 704, 2, fill="#c67c3a")
add_text(sid, "The hardest problems are still ahead — and the next year decides who solves them.",
         "caption", 528, 656, 704, 40, color="#f5f0e8", font_size=15, font_weight=500)

# =====================================================
# Assemble final deck
# =====================================================
# Insert textElements into slide objects
for s in content_slides:
    s["textElements"] = text_by_slide[s["id"]]

# Build baseLayout
base_slides = []
for s in content_slides:
    base_slides.append({
        "id": s["id"], "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })

# Element count
elem_count = sum(len(s["textElements"]) for s in content_slides)
elem_count += len(shape_content) + len(image_content) + len(icon_content)
elem_count += len(chart_content) + len(table_content)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "AI Trends 2026 — Slides 6-10",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": elem_count,
        "createdAt": "2026-06-02T00:00:00.000Z",
        "updatedAt": "2026-06-02T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": {
            "slides": content_slides,
            "imageElements": image_content,
            "shapeElements": shape_content,
            "chartElements": chart_content,
            "tableElements": table_content,
            "iconElements": icon_content,
            "embedElements": [],
            "smartDiagramElements": [],
            "groupElements": []
        },
        "baseLayout": {
            "version": "v1",
            "slides": base_slides,
            "imageElements": [],
            "shapeElements": [],
            "chartElements": [],
            "iconElements": [],
            "embedElements": []
        },
        "changelog": {
            "version": "2.0",
            "slides": changelog_slides
        }
    }
}

out_file = "deck.json"
with open(out_file, "w") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {out_file}")
print(f"slideCount: {deck['presentation']['slideCount']}")
print(f"elementCount: {elem_count}")
