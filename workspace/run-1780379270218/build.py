import json, time

NOW = int(time.time() * 1000)
ZIDX = 0
def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX

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
    c = {"id": text_id, "content": text, "type": type_,
         "originalType": type_, "groupId": None, "formattedContent": text}
    cl = {
        "slideId": slide_id, "position": {"x": x, "y": y},
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
    return c, cl

def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx, now,
               fill="#c67c3a", stroke=None, stroke_width=0, opacity=1):
    if stroke is None: stroke = fill
    c = {"id": shape_id, "slideId": slide_id, "groupId": None}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "width": w, "height": h, "rotation": 0, "zIndex": zidx,
          "opacity": opacity, "shapeType": shape_type,
          "fill": fill, "stroke": stroke, "strokeWidth": stroke_width,
          "updatedAt": now}
    return c, cl

def make_image(image_id, slide_id, src, x, y, w, h, zidx, now,
               is_background=False, border_radius=0, opacity=1):
    c = {"id": image_id, "slideId": slide_id, "groupId": None,
         "src": src, "s3Key": None,
         "isBackground": is_background, "_smartDiagram": False}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "width": w, "height": h, "rotation": 0, "zIndex": zidx,
          "opacity": opacity, "borderRadius": border_radius,
          "shadow": {"enabled": False, "angle": 135, "color": "#000000",
                     "opacity": 40, "distance": 8, "blur": 12, "size": 0, "spread": 0},
          "border": {"type": "none", "width": 4, "color": "#000000", "specialStyle": None},
          "cropRatio": "free",
          "cropRect": {"left": 0, "top": 0, "right": 0, "bottom": 0},
          "focusPoint": {"x": 50, "y": 50},
          "updatedAt": now}
    return c, cl

def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=80, color="#c67c3a", opacity=1):
    c = {"id": icon_id, "slideId": slide_id, "groupId": None,
         "iconName": icon_name, "iconSource": "lucide"}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "width": size, "height": size, "rotation": 0,
          "zIndex": zidx, "color": color, "opacity": opacity,
          "updatedAt": now}
    return c, cl

def make_chart(chart_id, slide_id, chart_type, x, y, w, h, zidx, now, chart_config):
    c = {"id": chart_id, "slideId": slide_id, "groupId": None,
         "svgDataUrl": "", "chartType": chart_type, "chartConfig": chart_config}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "width": w, "height": h, "rotation": 0,
          "zIndex": zidx, "updatedAt": now, "chartType": chart_type}
    return c, cl

def make_table(table_id, slide_id, x, y, zidx, now,
               col_widths, row_heights, cells,
               font_size=20, table_color="#1c1917", table_bg="#ffffff"):
    c = {"id": table_id, "slideId": slide_id, "groupId": None,
         "type": "table", "position": {"x": x, "y": y},
         "zIndex": zidx, "cells": cells,
         "colWidths": col_widths, "rowHeights": row_heights,
         "tableFontSize": font_size, "tableBold": False, "tableItalic": False,
         "tableAlign": "left", "tableColor": table_color, "tableBg": table_bg}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "zIndex": zidx, "updatedAt": now,
          "style": {"colWidths": col_widths, "rowHeights": row_heights}}
    return c, cl

# ---------- containers ----------
slides_content = []
slides_baselayout = []
text_by_slide = {}  # slide_id -> list of content text records
shape_list = []
image_list = []
chart_list = []
table_list = []
icon_list = []
changelog_slides = {}

# slide configs
SLIDE_BACKGROUNDS = {
    "slide-1":  "#1c1917",  # dark hero
    "slide-2":  "#f5f0e8",  # cream
    "slide-3":  "#ffffff",
    "slide-4":  "#c67c3a",  # amber stat
    "slide-5":  "#ffffff",
    "slide-6":  "#f5f0e8",
    "slide-7":  "#ffffff",
    "slide-8":  "#14204e",  # navy dark
    "slide-9":  "#ffe9d6",  # peach
    "slide-10": "#1c1917",  # dark close
}

for i in range(1, 11):
    sid = f"slide-{i}"
    slides_content.append({
        "id": sid, "order": i-1, "layoutId": "blank-canvas",
        "backgroundColor": SLIDE_BACKGROUNDS[sid], "textElements": []
    })
    slides_baselayout.append({
        "id": sid, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [],
        "chartElements": [], "iconElements": [], "embedElements": []
    })
    text_by_slide[sid] = []
    changelog_slides[sid] = {"elements": {}}

def reg_text(c, cl, sid, eid):
    text_by_slide[sid].append(c)
    changelog_slides[sid]["elements"][eid] = cl

def reg_shape(c, cl, sid, eid):
    shape_list.append(c)
    changelog_slides[sid]["elements"][eid] = cl

def reg_image(c, cl, sid, eid):
    image_list.append(c)
    changelog_slides[sid]["elements"][eid] = cl

def reg_icon(c, cl, sid, eid):
    icon_list.append(c)
    changelog_slides[sid]["elements"][eid] = cl

def reg_chart(c, cl, sid, eid):
    chart_list.append(c)
    changelog_slides[sid]["elements"][eid] = cl

def reg_table(c, cl, sid, eid):
    table_list.append(c)
    changelog_slides[sid]["elements"][eid] = cl

# =========================================================
# SLIDE 1 — TITLE HERO
# =========================================================
sid = "slide-1"
n = nextz(); eid = f"shape-{n}"
c, cl = make_shape(eid, sid, "rectangle", 48, 320, 8, 80, n, NOW, fill="#c67c3a")
reg_shape(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "ETHIOPIA", "caption", 48, 80, 400, 28, n, NOW,
                  color="#c67c3a", font_size=18)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "The Birthplace of Coffee", "title", 80, 304, 1100, 200, n, NOW,
                  color="#ffffff", font_size=84, line_height=1.05)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "How a small horn of Africa nation gave the world its favorite drink — and still leads the way in single-origin quality.",
                  "paragraph", 80, 488, 1000, 80, n, NOW,
                  color="#f5f0e8", font_size=22, font_weight=400, line_height=1.5)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "A Bildory Deck  ·  June 2026", "caption", 48, 648, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 2 — ORIGIN LEGEND (Kaldi)
# =========================================================
sid = "slide-2"
# left image
n = nextz(); eid = f"image-{n}"
c, cl = make_image(eid, sid,
    "https://images.pexels.com/photos/4820817/pexels-photo-4820817.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    48, 48, 560, 624, n, NOW, border_radius=8)
reg_image(c, cl, sid, eid)

# right column text
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "ORIGIN", "caption", 656, 80, 300, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "A legend that begins with a goat herder", "title",
                  656, 128, 576, 200, n, NOW, font_size=48, line_height=1.1)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Around the 9th century, Kaldi noticed his goats dancing after eating bright red cherries from a wild bush. He tried them himself, felt energized, and brought them to a local monk.",
                  "paragraph", 656, 360, 576, 140, n, NOW,
                  font_size=20, font_weight=400, line_height=1.55)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "The monk brewed the beans into a drink that kept him awake through long prayers. Coffee was born.",
                  "paragraph", 656, 520, 576, 100, n, NOW,
                  font_size=20, font_weight=400, line_height=1.55, color="#5a4a3a")
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 3 — THREE GROWING REGIONS
# =========================================================
sid = "slide-3"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "GROWING REGIONS", "caption", 48, 64, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Three terroirs, three flavors", "title",
                  48, 104, 1100, 80, n, NOW, font_size=48)
reg_text(c, cl, sid, eid)

# three cards
cards = [
    ("Yirgacheffe", "Floral, citrus, tea-like — the world's most prized washed coffees.", "1,750–2,200m", "#c67c3a"),
    ("Sidamo",      "Berry sweetness, wine notes — heart of southern coffee country.",    "1,500–2,200m", "#14204e"),
    ("Harrar",      "Dry-processed, blueberry-forward — bold eastern highlands.",         "1,500–2,100m", "#7a4a1a"),
]
xs = [48, 464, 880]
for (name, desc, alt, color), cx in zip(cards, xs):
    n = nextz(); eid = f"shape-{n}"
    c, cl = make_shape(eid, sid, "rectangle", cx, 232, 352, 400, n, NOW,
                       fill="#f5f0e8")
    reg_shape(c, cl, sid, eid)

    n = nextz(); eid = f"shape-{n}"
    c, cl = make_shape(eid, sid, "rectangle", cx, 232, 352, 8, n, NOW, fill=color)
    reg_shape(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, name, "subtitle", cx + 24, 272, 304, 56, n, NOW,
                      color=color, font_size=34)
    reg_text(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, desc, "paragraph", cx + 24, 344, 304, 180, n, NOW,
                      font_size=18, font_weight=400, line_height=1.55)
    reg_text(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, "ELEVATION", "caption", cx + 24, 544, 200, 20, n, NOW,
                      color="#5a4a3a", font_size=14)
    reg_text(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, alt, "paragraph", cx + 24, 568, 304, 40, n, NOW,
                      font_size=22, font_weight=700)
    reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 4 — BIG STAT (amber bg)
# =========================================================
sid = "slide-4"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "BY THE NUMBERS", "caption", 80, 96, 400, 24, n, NOW,
                  color="#ffe9d6")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "5.2M", "title", 80, 200, 1120, 240, n, NOW,
                  color="#ffffff", font_size=220, line_height=1.0)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Ethiopian households depend on coffee", "subtitle",
                  80, 480, 1120, 56, n, NOW, color="#ffffff", font_size=38)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Roughly 1 in 4 working Ethiopians — farmers, pickers, processors, exporters — earns a living from the bean.",
                  "paragraph", 80, 560, 900, 80, n, NOW,
                  color="#ffe9d6", font_size=20, font_weight=400, line_height=1.5)
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 5 — PRODUCTION BY REGION (bar chart)
# =========================================================
sid = "slide-5"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "PRODUCTION 2024/25", "caption", 48, 64, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Sidamo dominates by volume", "title",
                  48, 104, 1100, 80, n, NOW, font_size=44)
reg_text(c, cl, sid, eid)

# chart
chart_cfg = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {"type": "category", "data": ["Sidamo", "Jimma", "Yirgacheffe", "Harrar", "Limu"]},
    "yAxis": {"type": "value", "name": "Thousand 60kg bags"},
    "series": [{"type": "bar", "data": [2400, 1800, 950, 720, 510],
                "itemStyle": {"color": "#c67c3a"}}],
    "backgroundColor": "transparent",
    "color": ["#c67c3a"],
    "animation": False,
    "textStyle": {"color": "#1c1917", "fontSize": 14,
                  "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": ["Sidamo", "Jimma", "Yirgacheffe", "Harrar", "Limu"],
                  "series": [{"name": "Bags (000s)", "data": [2400, 1800, 950, 720, 510]}]},
    "properties": {"showXAxis": True, "showYAxis": True, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 14, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": False,
    "customSeriesColors": {"0": "#c67c3a"},
    "textColor": "#1c1917", "isMonochrome": True
}
n = nextz(); eid = f"chart-{n}"
c, cl = make_chart(eid, sid, "bar", 48, 216, 720, 432, n, NOW, chart_cfg)
reg_chart(c, cl, sid, eid)

# side annotation
n = nextz(); eid = f"shape-{n}"
c, cl = make_shape(eid, sid, "rectangle", 800, 240, 432, 280, n, NOW, fill="#f5f0e8")
reg_shape(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "WHY IT MATTERS", "caption", 824, 264, 400, 20, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Sidamo produces nearly 40% of national volume — but Yirgacheffe earns the highest premiums per kilogram on world markets.",
                  "paragraph", 824, 304, 384, 200, n, NOW,
                  font_size=18, font_weight=400, line_height=1.55)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Source: USDA FAS, Ethiopia Coffee Annual 2025",
                  "caption", 48, 668, 700, 20, n, NOW, color="#5a4a3a", font_size=14)
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 6 — ECONOMIC IMPACT (icons row)
# =========================================================
sid = "slide-6"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "ECONOMIC IMPACT", "caption", 48, 64, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Coffee is the economic backbone", "title",
                  48, 104, 1100, 80, n, NOW, font_size=46)
reg_text(c, cl, sid, eid)

stats = [
    ("TrendingUp", "30%", "of total export revenue",       80),
    ("Users",      "25%",  "of population involved",        448),
    ("Globe",      "120+", "countries import Ethiopian",    816),
]
for icon_name, stat, label, cx in stats:
    n = nextz(); eid = f"shape-{n}"
    c, cl = make_shape(eid, sid, "rectangle", cx, 248, 352, 320, n, NOW, fill="#ffffff")
    reg_shape(c, cl, sid, eid)

    n = nextz(); eid = f"icon-{n}"
    c, cl = make_icon(eid, sid, icon_name, cx + 32, 280, n, NOW,
                      size=64, color="#c67c3a")
    reg_icon(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, stat, "title", cx + 32, 368, 296, 80, n, NOW,
                      font_size=72, color="#1c1917", line_height=1.0)
    reg_text(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, label, "paragraph", cx + 32, 472, 296, 60, n, NOW,
                      font_size=18, font_weight=500, line_height=1.4, color="#5a4a3a")
    reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Coffee earned Ethiopia $1.4B in foreign exchange in 2024.",
                  "paragraph", 48, 612, 1184, 40, n, NOW,
                  font_size=20, font_weight=400, line_height=1.4, text_align="center")
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 7 — PROCESSING METHODS (table)
# =========================================================
sid = "slide-7"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "PROCESSING", "caption", 48, 64, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Washed vs. natural: two routes from cherry to cup", "title",
                  48, 104, 1184, 80, n, NOW, font_size=40, line_height=1.1)
reg_text(c, cl, sid, eid)

# table 3 cols x 5 rows
col_widths = [320, 432, 432]
row_heights = [64, 64, 64, 64, 64]
cells = {
    "0-0": {"text": "", "bold": True, "bg": "#1c1917", "color": "#ffffff"},
    "0-1": {"text": "Washed", "bold": True, "bg": "#1c1917", "color": "#ffffff"},
    "0-2": {"text": "Natural", "bold": True, "bg": "#1c1917", "color": "#ffffff"},

    "1-0": {"text": "Process", "bold": True, "bg": "#f5f0e8", "color": "#1c1917"},
    "1-1": {"text": "Pulped, fermented, dried", "bold": False, "bg": "#ffffff", "color": "#1c1917"},
    "1-2": {"text": "Whole cherry sun-dried", "bold": False, "bg": "#ffffff", "color": "#1c1917"},

    "2-0": {"text": "Flavor", "bold": True, "bg": "#f5f0e8", "color": "#1c1917"},
    "2-1": {"text": "Clean, floral, citrus", "bold": False, "bg": "#ffffff", "color": "#1c1917"},
    "2-2": {"text": "Heavy berry, wine-like", "bold": False, "bg": "#ffffff", "color": "#1c1917"},

    "3-0": {"text": "Water use", "bold": True, "bg": "#f5f0e8", "color": "#1c1917"},
    "3-1": {"text": "High", "bold": False, "bg": "#ffffff", "color": "#c67c3a"},
    "3-2": {"text": "Very low", "bold": False, "bg": "#ffffff", "color": "#14204e"},

    "4-0": {"text": "Common in", "bold": True, "bg": "#f5f0e8", "color": "#1c1917"},
    "4-1": {"text": "Yirgacheffe, Sidamo", "bold": False, "bg": "#ffffff", "color": "#1c1917"},
    "4-2": {"text": "Harrar, dry districts", "bold": False, "bg": "#ffffff", "color": "#1c1917"},
}
n = nextz(); eid = f"table-{n}"
c, cl = make_table(eid, sid, 48, 232, n, NOW, col_widths, row_heights, cells, font_size=19)
reg_table(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Both methods carry decades of tradition — the cup you brew is shaped before the bean leaves the farm.",
                  "paragraph", 48, 600, 1184, 60, n, NOW,
                  font_size=18, font_weight=400, line_height=1.5, color="#5a4a3a")
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 8 — EXPORT DESTINATIONS (doughnut, dark bg)
# =========================================================
sid = "slide-8"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "EXPORT MARKETS 2024", "caption", 48, 64, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Where Ethiopian coffee goes", "title",
                  48, 104, 1100, 80, n, NOW, font_size=46, color="#ffffff")
reg_text(c, cl, sid, eid)

donut_data = [
    {"value": 28, "name": "Germany"},
    {"value": 22, "name": "Saudi Arabia"},
    {"value": 15, "name": "United States"},
    {"value": 12, "name": "Japan"},
    {"value": 8,  "name": "Belgium"},
    {"value": 15, "name": "Other"},
]
donut_cfg = {
    "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
    "series": [{
        "type": "pie", "radius": ["45%", "75%"],
        "data": donut_data,
        "label": {"show": True, "color": "#ffffff", "fontSize": 14}
    }],
    "backgroundColor": "transparent",
    "color": ["#c67c3a", "#e0a268", "#f5d4a6", "#7a93c8", "#3d5aa8", "#5a4a3a"],
    "animation": False,
    "textStyle": {"color": "#ffffff", "fontSize": 14,
                  "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"data": donut_data},
    "properties": {"showXAxis": False, "showYAxis": False, "showDataLabels": True,
                   "showLegend": False, "showLabelName": True, "showLabelValue": True,
                   "labelFontSize": 14, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#c67c3a", "1": "#e0a268", "2": "#f5d4a6",
                           "3": "#7a93c8", "4": "#3d5aa8", "5": "#5a4a3a"},
    "textColor": "#ffffff", "isMonochrome": False
}
n = nextz(); eid = f"chart-{n}"
c, cl = make_chart(eid, sid, "doughnut", 48, 216, 560, 432, n, NOW, donut_cfg)
reg_chart(c, cl, sid, eid)

# right column key markets
right_x = 672
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "TOP BUYER", "caption", right_x, 240, 400, 20, n, NOW,
                  color="#c67c3a", font_size=14)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Germany", "subtitle", right_x, 264, 560, 56, n, NOW,
                  color="#ffffff", font_size=42)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "German roasters absorb roughly 28% of Ethiopia's coffee exports — funneled through Bremen and Hamburg into specialty roasters across Europe.",
                  "paragraph", right_x, 336, 560, 140, n, NOW,
                  color="#f5f0e8", font_size=18, font_weight=400, line_height=1.55)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"shape-{n}"
c, cl = make_shape(eid, sid, "rectangle", right_x, 504, 560, 1, n, NOW,
                   fill="#5a4a3a", opacity=0.5)
reg_shape(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Saudi Arabia is the fastest-growing market — up 18% YoY.",
                  "paragraph", right_x, 528, 560, 80, n, NOW,
                  color="#c67c3a", font_size=18, font_weight=600, line_height=1.5)
reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 9 — CHALLENGES
# =========================================================
sid = "slide-9"
n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "HEADWINDS", "caption", 48, 64, 400, 24, n, NOW,
                  color="#c67c3a")
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Four pressures on the bean", "title",
                  48, 104, 1100, 80, n, NOW, font_size=46)
reg_text(c, cl, sid, eid)

challenges = [
    ("Thermometer",   "Climate stress",     "Rising temperatures push arabica to higher altitudes — and there's nowhere higher to go."),
    ("TrendingDown",  "Price volatility",   "Farmgate prices swing 40% year to year, leaving smallholders exposed."),
    ("Sprout",        "Plant disease",      "Coffee leaf rust and berry disease destroyed 15% of the 2023 crop."),
    ("Truck",         "Logistics bottlenecks","Limited port access through Djibouti delays shipments by weeks."),
]
positions = [(48, 220), (656, 220), (48, 452), (656, 452)]
for (icon_name, head, body), (cx, cy) in zip(challenges, positions):
    n = nextz(); eid = f"shape-{n}"
    c, cl = make_shape(eid, sid, "rectangle", cx, cy, 576, 200, n, NOW, fill="#ffffff")
    reg_shape(c, cl, sid, eid)

    n = nextz(); eid = f"icon-{n}"
    c, cl = make_icon(eid, sid, icon_name, cx + 24, cy + 28, n, NOW,
                      size=48, color="#c67c3a")
    reg_icon(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, head, "subheading", cx + 96, cy + 32, 456, 40, n, NOW,
                      font_size=24, color="#1c1917")
    reg_text(c, cl, sid, eid)

    n = nextz(); eid = f"text-{n}"
    c, cl = make_text(eid, sid, body, "paragraph", cx + 96, cy + 80, 456, 110, n, NOW,
                      font_size=17, font_weight=400, line_height=1.5, color="#5a4a3a")
    reg_text(c, cl, sid, eid)

# =========================================================
# SLIDE 10 — CLOSING (dark)
# =========================================================
sid = "slide-10"
n = nextz(); eid = f"shape-{n}"
c, cl = make_shape(eid, sid, "rectangle", 48, 320, 8, 80, n, NOW, fill="#c67c3a")
reg_shape(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "THE ROAD AHEAD", "caption", 48, 80, 400, 28, n, NOW,
                  color="#c67c3a", font_size=18)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "The future is single-origin.", "title",
                  80, 280, 1120, 120, n, NOW,
                  color="#ffffff", font_size=72, line_height=1.05)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Traceability, fair pricing, and climate-resilient varietals are reshaping the world's oldest coffee culture — one cup at a time.",
                  "paragraph", 80, 416, 1000, 100, n, NOW,
                  color="#f5f0e8", font_size=22, font_weight=400, line_height=1.55)
reg_text(c, cl, sid, eid)

n = nextz(); eid = f"text-{n}"
c, cl = make_text(eid, sid, "Thank you  ·  buna tetu", "subheading",
                  80, 600, 600, 40, n, NOW, color="#c67c3a", font_size=24)
reg_text(c, cl, sid, eid)

# =========================================================
# WRITE TEXT ELEMENTS BACK INTO SLIDES
# =========================================================
for s in slides_content:
    s["textElements"] = text_by_slide[s["id"]]

content_file = {
    "slides": slides_content,
    "imageElements": image_list,
    "shapeElements": shape_list,
    "chartElements": chart_list,
    "tableElements": table_list,
    "iconElements": icon_list,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baseLayout_file = {
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

# element count
text_total = sum(len(text_by_slide[sid]) for sid in text_by_slide)
elem_total = (text_total + len(image_list) + len(shape_list)
              + len(chart_list) + len(table_list) + len(icon_list))

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Ethiopia: The Birthplace of Coffee",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": elem_total,
        "createdAt": "2026-06-02T00:00:00.000Z",
        "updatedAt": "2026-06-02T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baseLayout_file,
        "changelog": changelog_file
    }
}

with open("ethiopia_coffee_deck.json", "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote ethiopia_coffee_deck.json")
print(f"Slides: {len(slides_content)}  Elements: {elem_total}")
print(f"  text:   {text_total}")
print(f"  image:  {len(image_list)}")
print(f"  shape:  {len(shape_list)}")
print(f"  chart:  {len(chart_list)}")
print(f"  table:  {len(table_list)}")
print(f"  icon:   {len(icon_list)}")
