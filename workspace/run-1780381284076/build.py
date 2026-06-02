import json, time

NOW = int(time.time() * 1000)
COUNTER = 0

def next_n():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              text_align="left"):
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

# ---------- registries ----------
slides_content = []
slides_baselayout = []
slides_bg = {}
text_by_slide = {}
shape_elements = []
icon_elements = []
image_elements = []
chart_elements = []
table_elements = []

changelog_slides = {}

def reg_slide(slide_id, bg):
    slides_content.append({
        "id": slide_id, "order": len(slides_content),
        "layoutId": "blank-canvas", "backgroundColor": bg,
        "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    slides_bg[slide_id] = bg
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

def add_text(slide_id, text, type_, x, y, w, h, **kw):
    n = next_n()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kw)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

def add_shape(slide_id, shape_type, x, y, w, h, **kw):
    n = next_n()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kw)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

def add_icon(slide_id, icon_name, x, y, **kw):
    n = next_n()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kw)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = next_n()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, NOW, chart_config)
    chart_elements.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl

def add_table(slide_id, x, y, col_widths, row_heights, cells, **kw):
    n = next_n()
    tid = f"table-{n}"
    c, cl = make_table(tid, slide_id, x, y, n, NOW, col_widths, row_heights, cells, **kw)
    table_elements.append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

# ============================================================
# SLIDE 1 — TITLE
# ============================================================
s = "slide-1"
reg_slide(s, "#1c1917")
add_shape(s, "circle", 880, 80, 360, 360, fill="#c67c3a", opacity=1)
add_shape(s, "rectangle", 48, 600, 80, 8, fill="#c67c3a")
add_icon(s, "Cat", 920, 160, size=240, color="#1c1917")
add_text(s, "Why Cats Think", "title", 48, 200, 800, 80, color="#ffffff", font_size=72)
add_text(s, "They Rule the World", "title", 48, 290, 900, 80, color="#c67c3a", font_size=72)
add_text(s, "A scientifically questionable investigation", "subheading", 48, 400, 800, 40, color="#ffffff")
add_text(s, "FELINE STUDIES DEPT.  /  2026", "caption", 48, 620, 600, 30, color="#c67c3a", font_size=14, line_height=1.4)

# ============================================================
# SLIDE 2 — THE THRONE (couch claim)
# ============================================================
s = "slide-2"
reg_slide(s, "#f5f0e8")
add_shape(s, "rectangle", 48, 48, 8, 80, fill="#c67c3a")
add_text(s, "CHAPTER ONE", "caption", 72, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "The Throne is Mine", "title", 72, 96, 1100, 80, font_size=68)

add_shape(s, "rectangle", 48, 240, 560, 380, fill="#ffffff")
add_icon(s, "Sofa", 220, 320, size=220, color="#1c1917")
add_text(s, "the couch", "caption", 48, 588, 560, 30, color="#c67c3a", font_size=14, text_align="left")

add_text(s, "Any horizontal surface you", "subtitle", 672, 264, 560, 60, font_size=36)
add_text(s, "claim as yours is, in fact,", "subtitle", 672, 312, 560, 60, font_size=36)
add_text(s, "theirs.", "subtitle", 672, 360, 560, 60, font_size=36, color="#c67c3a")
add_text(s, "The warmest cushion. The fresh laundry. Your laptop keyboard at 11:42pm. By feline law, occupation equals ownership.", "paragraph", 672, 448, 560, 140, font_weight=500)

# ============================================================
# SLIDE 3 — THE STARE
# ============================================================
s = "slide-3"
reg_slide(s, "#ffe9d6")
add_text(s, "Exhibit A", "caption", 48, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "The Unblinking Stare", "title", 48, 96, 1184, 80, font_size=68)

# Three big stat blocks
add_shape(s, "rectangle", 48, 240, 376, 360, fill="#ffffff")
add_text(s, "14 sec", "title", 72, 280, 340, 80, color="#c67c3a", font_size=84)
add_text(s, "average duration of an unprovoked stare from across the room", "paragraph", 72, 408, 330, 160, font_weight=500)

add_shape(s, "rectangle", 452, 240, 376, 360, fill="#ffffff")
add_text(s, "0", "title", 476, 280, 340, 80, color="#c67c3a", font_size=84)
add_text(s, "blinks required to make you question every decision you've ever made", "paragraph", 476, 408, 330, 160, font_weight=500)

add_shape(s, "rectangle", 856, 240, 376, 360, fill="#1c1917")
add_text(s, "100%", "title", 880, 280, 340, 80, color="#c67c3a", font_size=84)
add_text(s, "of human responses are exactly what the cat expected", "paragraph", 880, 408, 330, 160, color="#ffffff", font_weight=500)

add_text(s, "Eye contact is leverage. They invented it.", "caption", 48, 632, 800, 30, color="#1c1917", font_size=16)

# ============================================================
# SLIDE 4 — 3AM ZOOMIES
# ============================================================
s = "slide-4"
reg_slide(s, "#14204e")
add_shape(s, "circle", 920, 60, 360, 360, fill="#c67c3a", opacity=0.15)
add_text(s, "03:00", "title", 48, 80, 800, 80, color="#c67c3a", font_size=120, font_weight=700)
add_text(s, "AM", "subtitle", 380, 96, 200, 60, color="#c67c3a", font_size=48)

add_text(s, "The Zoomies Hour", "subtitle", 48, 230, 800, 60, color="#ffffff", font_size=44)
add_text(s, "Sleep is a privilege the cat grants you,", "paragraph", 48, 308, 700, 40, color="#ffffff", font_weight=500)
add_text(s, "and grants it can revoke without notice.", "paragraph", 48, 348, 700, 40, color="#ffffff", font_weight=500)

# the schedule
add_icon(s, "Moon", 48, 440, size=48, color="#c67c3a")
add_text(s, "11:00 PM  —  You go to bed", "subheading", 112, 448, 700, 36, color="#ffffff", font_size=22)

add_icon(s, "Footprints", 48, 504, size=48, color="#c67c3a")
add_text(s, "02:47 AM  —  A 4kg shape lands on your chest", "subheading", 112, 512, 800, 36, color="#ffffff", font_size=22)

add_icon(s, "Zap", 48, 568, size=48, color="#c67c3a")
add_text(s, "03:00 AM  —  Indoor 0–60 mph in 1.2 seconds", "subheading", 112, 576, 800, 36, color="#ffffff", font_size=22)

add_icon(s, "Cat", 950, 440, size=180, color="#c67c3a")

# ============================================================
# SLIDE 5 — FOOD DEMANDS CHART
# ============================================================
s = "slide-5"
reg_slide(s, "#fff3c2")
add_text(s, "Daily Schedule", "caption", 48, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "Meal Requests vs Actual Meals", "title", 48, 96, 1184, 80, font_size=52)
add_text(s, "The bowl is empty (it is not).", "subheading", 48, 184, 800, 40)

chart_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {"type": "category", "data": ["6 AM", "9 AM", "12 PM", "3 PM", "6 PM", "9 PM", "12 AM"],
              "axisLine": {"lineStyle": {"color": "#1c1917"}},
              "axisLabel": {"color": "#1c1917", "fontSize": 14}},
    "yAxis": {"type": "value",
              "axisLine": {"lineStyle": {"color": "#1c1917"}},
              "axisLabel": {"color": "#1c1917", "fontSize": 14},
              "splitLine": {"lineStyle": {"color": "#1c191722"}}},
    "series": [
        {"type": "bar", "name": "Requests", "data": [8, 6, 7, 9, 12, 10, 11], "itemStyle": {"color": "#c67c3a"}},
        {"type": "bar", "name": "Actual meals", "data": [1, 0, 1, 0, 1, 0, 0], "itemStyle": {"color": "#1c1917"}}
    ],
    "backgroundColor": "transparent",
    "color": ["#c67c3a", "#1c1917"],
    "animation": False,
    "textStyle": {"color": "#1c1917", "fontSize": 14, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["6 AM", "9 AM", "12 PM", "3 PM", "6 PM", "9 PM", "12 AM"],
        "series": [
            {"name": "Requests", "data": [8, 6, 7, 9, 12, 10, 11]},
            {"name": "Actual meals", "data": [1, 0, 1, 0, 1, 0, 0]}
        ]
    },
    "properties": {
        "showXAxis": True, "showYAxis": True, "showDataLabels": False,
        "showLegend": True, "showLabelName": True, "showLabelValue": False,
        "labelFontSize": 14, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None, "isDarkMode": False,
    "customSeriesColors": {"0": "#c67c3a", "1": "#1c1917"},
    "textColor": "#1c1917", "isMonochrome": False
}
add_chart(s, "bar", 48, 240, 760, 420, chart_cfg)

# legend explanation card
add_shape(s, "rectangle", 840, 240, 392, 200, fill="#ffffff")
add_shape(s, "rectangle", 864, 268, 24, 24, fill="#c67c3a")
add_text(s, "Requests", "subheading", 904, 264, 280, 32, font_size=22)
add_text(s, "shrill, urgent, ankle-adjacent", "paragraph", 864, 304, 320, 60, font_size=16, font_weight=500)

add_shape(s, "rectangle", 864, 380, 24, 24, fill="#1c1917")
add_text(s, "Actual meals", "subheading", 904, 376, 280, 32, font_size=22)

add_shape(s, "rectangle", 840, 460, 392, 200, fill="#1c1917")
add_text(s, "Ratio:", "caption", 864, 484, 200, 24, color="#c67c3a", font_size=14)
add_text(s, "63 : 3", "title", 864, 512, 360, 80, color="#ffffff", font_size=72)
add_text(s, "requests per meal served", "caption", 864, 612, 360, 30, color="#ffffff", font_size=16)

# ============================================================
# SLIDE 6 — BOX EMPIRE
# ============================================================
s = "slide-6"
reg_slide(s, "#c8f5e4")
add_text(s, "Territorial Expansion", "caption", 48, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "If It Fits,", "title", 48, 96, 800, 80, font_size=84)
add_text(s, "I Sits.", "title", 48, 188, 800, 80, font_size=84, color="#c67c3a")

# four boxes grid
positions = [(48, 320), (344, 320), (640, 320), (936, 320)]
labels = ["Amazon box", "Shoe box", "Sink", "8.5 x 11 paper"]
sizes = ["L", "M", "S", "XS"]
for (x, y), label, size in zip(positions, labels, sizes):
    add_shape(s, "rectangle", x, y, 248, 248, fill="#ffffff")
    add_text(s, size, "title", x+24, y+24, 200, 80, color="#c67c3a", font_size=72)
    add_text(s, label, "subheading", x+24, y+150, 200, 32, font_size=20)
    add_text(s, "claimed", "caption", x+24, y+186, 200, 30, font_size=14, color="#c67c3a")

add_text(s, "Conquest does not require permission. It requires a flat surface and approximately one (1) cat.", "paragraph", 48, 612, 1184, 60, font_weight=500, font_size=20)

# ============================================================
# SLIDE 7 — SILENT JUDGMENT (table)
# ============================================================
s = "slide-7"
reg_slide(s, "#ffffff")
add_shape(s, "rectangle", 48, 48, 8, 80, fill="#c67c3a")
add_text(s, "Crimes Catalogue", "caption", 72, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "Offenses Against the Cat", "title", 72, 96, 1184, 80, font_size=58)
add_text(s, "Logged by the cat. Sentencing: a slow blink in your general direction.", "subheading", 72, 184, 1100, 40, font_size=22)

header_bg = "#1c1917"
header_fg = "#ffffff"
body_bg = "#ffffff"
body_fg = "#1c1917"
alt_bg = "#f5f0e8"

cells = {
    "0-0": {"text": "Offense", "bold": True, "bg": header_bg, "color": header_fg},
    "0-1": {"text": "Severity", "bold": True, "bg": header_bg, "color": header_fg},
    "0-2": {"text": "Punishment", "bold": True, "bg": header_bg, "color": header_fg},

    "1-0": {"text": "Closing a door", "bold": False, "bg": body_bg, "color": body_fg},
    "1-1": {"text": "Severe", "bold": True, "bg": body_bg, "color": "#c67c3a"},
    "1-2": {"text": "Continuous meowing for 47 minutes", "bold": False, "bg": body_bg, "color": body_fg},

    "2-0": {"text": "Late dinner (>5 min)", "bold": False, "bg": alt_bg, "color": body_fg},
    "2-1": {"text": "Critical", "bold": True, "bg": alt_bg, "color": "#c67c3a"},
    "2-2": {"text": "Knock vase off shelf", "bold": False, "bg": alt_bg, "color": body_fg},

    "3-0": {"text": "Wrong flavor of pâté", "bold": False, "bg": body_bg, "color": body_fg},
    "3-1": {"text": "Capital", "bold": True, "bg": body_bg, "color": "#c67c3a"},
    "3-2": {"text": "Bury it like litter, glare", "bold": False, "bg": body_bg, "color": body_fg},

    "4-0": {"text": "Petting the belly (a trap)", "bold": False, "bg": alt_bg, "color": body_fg},
    "4-1": {"text": "Self-inflicted", "bold": True, "bg": alt_bg, "color": "#c67c3a"},
    "4-2": {"text": "Eighteen paws, all claws", "bold": False, "bg": alt_bg, "color": body_fg},
}
add_table(s, 72, 264, [380, 220, 584], [56, 64, 64, 64, 64], cells, font_size=18)

# ============================================================
# SLIDE 8 — KNOCKING THINGS OFF TABLES
# ============================================================
s = "slide-8"
reg_slide(s, "#ffe0eb")
add_text(s, "Field Research", "caption", 48, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "Gravity: An Experiment", "title", 48, 96, 1184, 80, font_size=60)
add_text(s, "Repeated daily, for science.", "subheading", 48, 184, 800, 40)

# steps
add_shape(s, "circle", 48, 280, 80, 80, fill="#c67c3a")
add_text(s, "1", "title", 48, 290, 80, 80, color="#ffffff", text_align="center", font_size=44)
add_text(s, "Approach object on table edge", "subheading", 152, 296, 700, 40, font_size=24)
add_text(s, "A mug. A pen. Your grandmother's heirloom.", "paragraph", 152, 332, 700, 40, font_size=18, font_weight=500)

add_shape(s, "circle", 48, 396, 80, 80, fill="#c67c3a")
add_text(s, "2", "title", 48, 406, 80, 80, color="#ffffff", text_align="center", font_size=44)
add_text(s, "Make eye contact with human", "subheading", 152, 412, 700, 40, font_size=24)
add_text(s, "This is the critical step. Hold for full effect.", "paragraph", 152, 448, 700, 40, font_size=18, font_weight=500)

add_shape(s, "circle", 48, 512, 80, 80, fill="#c67c3a")
add_text(s, "3", "title", 48, 522, 80, 80, color="#ffffff", text_align="center", font_size=44)
add_text(s, "Paw. Push. Observe descent.", "subheading", 152, 528, 700, 40, font_size=24)
add_text(s, "Gravity confirmed. Again. Document with sustained stare.", "paragraph", 152, 564, 800, 40, font_size=18, font_weight=500)

# big finding card
add_shape(s, "rectangle", 896, 280, 336, 312, fill="#1c1917")
add_text(s, "FINDING", "caption", 920, 304, 280, 30, color="#c67c3a", font_size=14)
add_text(s, "9.8", "title", 920, 340, 300, 100, color="#ffffff", font_size=104)
add_text(s, "m/s² — still works.", "subheading", 920, 460, 300, 36, color="#ffffff", font_size=22)
add_text(s, "We must verify tomorrow.", "paragraph", 920, 510, 300, 60, color="#c67c3a", font_size=18, font_weight=500)

# ============================================================
# SLIDE 9 — PURR MANIPULATION (pie chart)
# ============================================================
s = "slide-9"
reg_slide(s, "#e9defc")
add_text(s, "Acoustic Warfare", "caption", 48, 56, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "What a Purr Actually Means", "title", 48, 96, 1184, 80, font_size=56)
add_text(s, "Spoiler: rarely \"I love you.\"", "subheading", 48, 184, 800, 40)

pie_cfg = {
    "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
    "series": [{
        "type": "pie", "radius": ["35%", "75%"],
        "data": [
            {"value": 38, "name": "Feed me immediately"},
            {"value": 24, "name": "Pet me (correctly)"},
            {"value": 18, "name": "Open this door"},
            {"value": 12, "name": "I am plotting"},
            {"value": 8,  "name": "Affection (rare)"}
        ],
        "label": {"show": True, "color": "#1c1917", "fontSize": 14}
    }],
    "backgroundColor": "transparent",
    "color": ["#c67c3a", "#1c1917", "#14204e", "#9b6332", "#d6b89c"],
    "animation": False,
    "textStyle": {"color": "#1c1917", "fontSize": 14, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "data": [
            {"value": 38, "name": "Feed me immediately"},
            {"value": 24, "name": "Pet me (correctly)"},
            {"value": 18, "name": "Open this door"},
            {"value": 12, "name": "I am plotting"},
            {"value": 8,  "name": "Affection (rare)"}
        ]
    },
    "properties": {
        "showXAxis": False, "showYAxis": False, "showDataLabels": True,
        "showLegend": False, "showLabelName": True, "showLabelValue": True,
        "labelFontSize": 14, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None, "isDarkMode": False,
    "customSeriesColors": {"0": "#c67c3a", "1": "#1c1917", "2": "#14204e", "3": "#9b6332", "4": "#d6b89c"},
    "textColor": "#1c1917", "isMonochrome": False
}
add_chart(s, "doughnut", 48, 240, 560, 420, pie_cfg)

# right column commentary
add_shape(s, "rectangle", 648, 240, 584, 200, fill="#ffffff")
add_text(s, "The purr is a control signal", "subheading", 672, 264, 540, 36, font_size=24)
add_text(s, "25–150 Hz. Travels through walls. Bypasses your rational brain and lands directly in the part that opens cans.", "paragraph", 672, 308, 540, 120, font_size=17, font_weight=500)

add_shape(s, "rectangle", 648, 460, 584, 200, fill="#1c1917")
add_text(s, "Your compliance rate:", "caption", 672, 484, 360, 30, color="#c67c3a", font_size=14)
add_text(s, "92%", "title", 672, 516, 360, 100, color="#ffffff", font_size=88)
add_text(s, "(within 4.2 seconds of purr onset)", "caption", 672, 624, 540, 30, color="#ffffff", font_size=14)

# ============================================================
# SLIDE 10 — CONCLUSION
# ============================================================
s = "slide-10"
reg_slide(s, "#1c1917")
add_shape(s, "rectangle", 0, 0, 1280, 8, fill="#c67c3a")
add_shape(s, "circle", 960, 360, 280, 280, fill="#c67c3a", opacity=0.25)
add_icon(s, "Crown", 1020, 360, size=160, color="#c67c3a")

add_text(s, "CONCLUSION", "caption", 48, 80, 400, 30, color="#c67c3a", font_size=14)
add_text(s, "You don't own a cat.", "title", 48, 140, 900, 80, color="#ffffff", font_size=64)
add_text(s, "You staff one.", "title", 48, 220, 900, 80, color="#c67c3a", font_size=64)

# three takeaway bullets
add_icon(s, "Check", 48, 360, size=36, color="#c67c3a")
add_text(s, "They claim the territory. You pay the rent.", "subheading", 100, 364, 800, 36, color="#ffffff", font_size=22)

add_icon(s, "Check", 48, 416, size=36, color="#c67c3a")
add_text(s, "They set the schedule. You set the alarm.", "subheading", 100, 420, 800, 36, color="#ffffff", font_size=22)

add_icon(s, "Check", 48, 472, size=36, color="#c67c3a")
add_text(s, "They issue the purr. You serve the snack.", "subheading", 100, 476, 800, 36, color="#ffffff", font_size=22)

add_shape(s, "rectangle", 48, 580, 800, 2, fill="#c67c3a")
add_text(s, "Long live the cats.", "subtitle", 48, 600, 800, 50, color="#c67c3a", font_size=32)
add_text(s, "thank you for attending today's briefing", "caption", 48, 660, 800, 30, color="#ffffff", font_size=14)

# ---------- attach text elements to slides ----------
for sc in slides_content:
    sc["textElements"] = text_by_slide[sc["id"]]

# ---------- count elements ----------
total_text = sum(len(text_by_slide[s["id"]]) for s in slides_content)
total_elements = (total_text + len(shape_elements) + len(icon_elements)
                  + len(image_elements) + len(chart_elements) + len(table_elements))

# ---------- envelope ----------
deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Why Cats Think They Rule the World",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": total_elements,
        "createdAt": "2026-06-02T00:00:00.000Z",
        "updatedAt": "2026-06-02T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": {
            "slides": slides_content,
            "imageElements": image_elements,
            "shapeElements": shape_elements,
            "chartElements": chart_elements,
            "tableElements": table_elements,
            "iconElements": icon_elements,
            "embedElements": [],
            "smartDiagramElements": [],
            "groupElements": []
        },
        "baseLayout": {
            "version": "v1",
            "slides": slides_baselayout,
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

out = "cats_rule_the_world.json"
with open(out, "w") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {out}")
print(f"Slides: {len(slides_content)}")
print(f"Elements: {total_elements}")
print(f"  text: {total_text}")
print(f"  shapes: {len(shape_elements)}")
print(f"  icons: {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
print(f"  tables: {len(table_elements)}")
