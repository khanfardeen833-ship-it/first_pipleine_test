import json, time, os

NOW = int(time.time() * 1000)

# ============================================================
# Counters for unique IDs and zIndex
# ============================================================
COUNTER = 0
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ============================================================
# Helpers
# ============================================================
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
        "groupId": None
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
            "backgroundClip": "unset", "listLevel": 1,
            "paragraphSpacingBefore": 0, "paragraphSpacingAfter": 0,
            "textOutlineColor": "#000000", "textOutlineWidth": 0,
            "textTransformEffect": "none", "textTransformRadius": 220,
            "textVerticalAlign": "baseline", "curveEnabled": False,
            "curveValue": 26, "shadowType": "none", "shadowOffset": 22,
            "shadowDirection": -45, "shadowBlur": 0,
            "shadowTransparency": 40, "shadowColor": "#000000"
        },
        "animation": {"enter": "none", "exit": "fade", "duration": 550,
                      "delay": 0, "trigger": "both", "typewriterMode": "character"},
        "updatedAt": now
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
        "chartType": chart_type,
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


# ============================================================
# Color palette
# ============================================================
NAVY = "#14204e"
AMBER = "#c67c3a"
DARK = "#1c1917"
WHITE = "#ffffff"
CREAM = "#f5f0e8"
PEACH = "#ffe9d6"
LAVENDER = "#e9defc"
MINT = "#c8f5e4"
SKY = "#d6f1fb"

# Chart palettes (multi-color)
CHART_PALETTE = ["#c67c3a", "#14204e", "#ca8746", "#3d4f8a", "#cd9352", "#5e6fa1"]
CHART_PALETTE_DARK = ["#c67c3a", "#ffffff", "#ca8746", "#e0e0e0", "#cd9352", "#bdbdbd"]


def base_chart_cfg(palette=None, dark=False, text_color=None):
    """Returns a base chart config dict that can be extended per chart type."""
    if palette is None:
        palette = CHART_PALETTE
    if text_color is None:
        text_color = "#ffffff" if dark else "#1c1917"
    return {
        "tooltip": {"trigger": "item"},
        "series": [],
        "backgroundColor": "transparent",
        "color": palette,
        "animation": False,
        "textStyle": {
            "color": text_color,
            "fontSize": 14,
            "fontWeight": "normal",
            "fontStyle": "normal"
        },
        "tableData": {},
        "properties": {
            "showXAxis": True,
            "showYAxis": True,
            "showDataLabels": False,
            "showLegend": False,
            "showLabelName": True,
            "showLabelValue": False,
            "labelFontSize": 14,
            "labelBold": False,
            "labelItalic": False,
            "labelUnderline": False,
            "labelStrike": False
        },
        "isDarkMode": dark,
        "textColor": text_color
    }


# ============================================================
# State
# ============================================================
slides_content = []
slides_baselayout = []
text_by_slide = {}
shape_elements = []
icon_elements = []
chart_elements = []
changelog_slides = {}


def add_slide(slide_id, bg=WHITE):
    slides_content.append({
        "id": slide_id,
        "order": len(slides_content),
        "layoutId": "blank-canvas",
        "backgroundColor": bg,
        "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
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
# SLIDE 1 — Title slide
# ============================================================
S1 = "slide-1"
add_slide(S1, bg=NAVY)

# Accent bar
add_shape(S1, "rectangle", 48, 80, 80, 8, fill=AMBER)
# Eyebrow
add_text(S1, "MARKET STUDY  ·  2026", "caption",
         48, 104, 600, 28, color=AMBER)
# Hero title
add_text(S1, "The AI Presentation Market", "title",
         48, 160, 1184, 80, color=WHITE, font_size=72)
add_text(S1, "Is Reshaping How Teams Communicate", "title",
         48, 248, 1184, 80, color=WHITE, font_size=72)
# Big stat
add_text(S1, "$8.4B", "title",
         48, 392, 480, 120, color=AMBER, font_size=104)
add_text(S1, "global market value projected by 2030, growing 27% CAGR", "subtitle",
         48, 520, 760, 80, color=WHITE, font_size=28, font_weight=500)
# Footer
add_text(S1, "Prepared by Bildory Research  ·  May 2026", "caption",
         48, 656, 600, 24, color="#a8b1d6")
# Right side icon decoration
add_icon(S1, "BarChart3", 968, 200, size=216, color=AMBER, opacity=0.18)
add_icon(S1, "TrendingUp", 904, 432, size=160, color=AMBER, opacity=0.20)


# ============================================================
# SLIDE 2 — Market Size & Growth (2 charts)
# ============================================================
S2 = "slide-2"
add_slide(S2, bg=WHITE)

# Header bar
add_shape(S2, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S2, "Market expanding 4x in five years", "title",
         72, 56, 1160, 64, font_size=44)
add_text(S2, "Global AI presentation software revenue, USD billions", "subheading",
         72, 124, 1160, 32, color="#5d564f", font_size=22, font_weight=500)

# Chart 1 — Market size bar (2020-2027)
cfg1 = base_chart_cfg()
cfg1["tooltip"] = {"trigger": "axis"}
cfg1["xAxis"] = {"type": "category",
                 "data": ["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027"],
                 "axisLabel": {"color": "#1c1917", "fontSize": 13}}
cfg1["yAxis"] = {"type": "value",
                 "axisLabel": {"color": "#1c1917", "fontSize": 13, "formatter": "${value}B"}}
cfg1["series"] = [{"type": "bar",
                   "data": [0.9, 1.3, 1.8, 2.4, 3.2, 4.4, 5.8, 7.6],
                   "itemStyle": {"color": AMBER, "borderRadius": [6, 6, 0, 0]}}]
cfg1["tableData"] = {"categories": ["2020","2021","2022","2023","2024","2025","2026","2027"],
                     "series": [{"name": "Revenue ($B)",
                                 "data": [0.9, 1.3, 1.8, 2.4, 3.2, 4.4, 5.8, 7.6]}]}
cfg1["properties"]["showDataLabels"] = True
add_chart(S2, "bar", 48, 184, 720, 432, cfg1)

# Chart 2 — CAGR doughnut (segments contribution)
cfg2 = base_chart_cfg(palette=[AMBER, NAVY, "#ca8746"])
cfg2["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg2["series"] = [{
    "type": "pie",
    "radius": ["45%", "75%"],
    "center": ["50%", "55%"],
    "data": [
        {"value": 27.1, "name": "AI features"},
        {"value": 14.5, "name": "Templates"},
        {"value": 8.4, "name": "Collaboration"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 13, "formatter": "{b}\n{c}%"}
}]
cfg2["tableData"] = {"data": [
    {"value": 27.1, "name": "AI features"},
    {"value": 14.5, "name": "Templates"},
    {"value": 8.4, "name": "Collaboration"}]}
add_chart(S2, "doughnut", 800, 184, 432, 432, cfg2)

# Captions
add_text(S2, "Source: Grand View Research, IDC", "caption",
         48, 632, 600, 24, color="#7a716a")
add_text(S2, "CAGR by feature segment", "caption",
         800, 632, 432, 24, color="#7a716a", text_align="center")


# ============================================================
# SLIDE 3 — Market Segmentation (3 charts)
# ============================================================
S3 = "slide-3"
add_slide(S3, bg=CREAM)

add_shape(S3, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S3, "Three lenses on the market today", "title",
         72, 56, 1160, 64, font_size=44)
add_text(S3, "Deployment, organization size, and geography", "subheading",
         72, 124, 1160, 32, color="#5d564f", font_size=22, font_weight=500)

# Three card backgrounds for charts
add_shape(S3, "rectangle", 48, 184, 384, 432, fill=WHITE)
add_shape(S3, "rectangle", 448, 184, 384, 432, fill=WHITE)
add_shape(S3, "rectangle", 848, 184, 384, 432, fill=WHITE)

# Card titles
add_text(S3, "By Deployment", "subheading", 64, 200, 360, 32, font_size=20)
add_text(S3, "By Org Size", "subheading", 464, 200, 360, 32, font_size=20)
add_text(S3, "By Region", "subheading", 864, 200, 360, 32, font_size=20)

# Chart 3 — Deployment Pie
cfg3 = base_chart_cfg(palette=[AMBER, NAVY, "#cd9352"])
cfg3["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg3["series"] = [{
    "type": "pie",
    "radius": ["0%", "70%"],
    "center": ["50%", "55%"],
    "data": [
        {"value": 64, "name": "Cloud / SaaS"},
        {"value": 24, "name": "Hybrid"},
        {"value": 12, "name": "On-Premise"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 12,
              "formatter": "{b}\n{d}%"}
}]
cfg3["tableData"] = {"data": [
    {"value": 64, "name": "Cloud / SaaS"},
    {"value": 24, "name": "Hybrid"},
    {"value": 12, "name": "On-Premise"}]}
add_chart(S3, "pie", 56, 240, 368, 360, cfg3)

# Chart 4 — Org Size Doughnut
cfg4 = base_chart_cfg(palette=[NAVY, AMBER, "#cd9352", "#3d4f8a"])
cfg4["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg4["series"] = [{
    "type": "pie",
    "radius": ["40%", "70%"],
    "center": ["50%", "55%"],
    "data": [
        {"value": 41, "name": "Enterprise"},
        {"value": 28, "name": "Mid-Market"},
        {"value": 19, "name": "SMB"},
        {"value": 12, "name": "Solo"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 12,
              "formatter": "{b}\n{d}%"}
}]
cfg4["tableData"] = {"data": [
    {"value": 41, "name": "Enterprise"},
    {"value": 28, "name": "Mid-Market"},
    {"value": 19, "name": "SMB"},
    {"value": 12, "name": "Solo"}]}
add_chart(S3, "doughnut", 456, 240, 368, 360, cfg4)

# Chart 5 — Region Bar
cfg5 = base_chart_cfg()
cfg5["tooltip"] = {"trigger": "axis"}
cfg5["xAxis"] = {"type": "value",
                 "axisLabel": {"color": "#1c1917", "fontSize": 11, "formatter": "{value}%"}}
cfg5["yAxis"] = {"type": "category",
                 "data": ["Africa", "LATAM", "MEA", "APAC", "EMEA", "N. America"],
                 "axisLabel": {"color": "#1c1917", "fontSize": 11}}
cfg5["series"] = [{"type": "bar",
                   "data": [3, 6, 8, 22, 26, 35],
                   "itemStyle": {"color": AMBER, "borderRadius": [0, 4, 4, 0]}}]
cfg5["tableData"] = {"categories": ["Africa","LATAM","MEA","APAC","EMEA","N. America"],
                     "series": [{"name": "Share %", "data": [3, 6, 8, 22, 26, 35]}]}
add_chart(S3, "bar", 856, 240, 368, 360, cfg5)


# ============================================================
# SLIDE 4 — Adoption by Industry & Tools (2 charts)
# ============================================================
S4 = "slide-4"
add_slide(S4, bg=WHITE)

add_shape(S4, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S4, "Sales and marketing teams lead adoption", "title",
         72, 56, 1160, 64, font_size=40)
add_text(S4, "Industry penetration vs. tool preference among 2,400 surveyed teams", "subheading",
         72, 124, 1160, 32, color="#5d564f", font_size=22, font_weight=500)

# Chart 6 — Industry adoption bar
cfg6 = base_chart_cfg()
cfg6["tooltip"] = {"trigger": "axis"}
cfg6["xAxis"] = {"type": "category",
                 "data": ["Tech", "Mktg", "Edu", "Finance", "Health", "Retail", "Mfg"],
                 "axisLabel": {"color": "#1c1917", "fontSize": 12}}
cfg6["yAxis"] = {"type": "value",
                 "axisLabel": {"color": "#1c1917", "fontSize": 12, "formatter": "{value}%"}}
cfg6["series"] = [{"type": "bar",
                   "data": [78, 71, 64, 52, 41, 38, 24],
                   "itemStyle": {"color": NAVY, "borderRadius": [6, 6, 0, 0]}}]
cfg6["tableData"] = {"categories": ["Tech","Mktg","Edu","Finance","Health","Retail","Mfg"],
                     "series": [{"name": "Adoption %",
                                 "data": [78, 71, 64, 52, 41, 38, 24]}]}
cfg6["properties"]["showDataLabels"] = True
add_chart(S4, "bar", 48, 184, 600, 432, cfg6)
add_text(S4, "% of teams using AI-assisted decks", "caption",
         48, 624, 600, 24, color="#7a716a", text_align="center")

# Chart 7 — Tools used pie
cfg7 = base_chart_cfg(palette=[AMBER, NAVY, "#ca8746", "#3d4f8a", "#cd9352"])
cfg7["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg7["series"] = [{
    "type": "pie",
    "radius": ["35%", "70%"],
    "roseType": "area",
    "center": ["50%", "55%"],
    "data": [
        {"value": 34, "name": "Bildory"},
        {"value": 22, "name": "Gamma"},
        {"value": 17, "name": "Beautiful.ai"},
        {"value": 14, "name": "Tome"},
        {"value": 13, "name": "Other"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 13,
              "formatter": "{b}\n{c}%"}
}]
cfg7["tableData"] = {"data": [
    {"value": 34, "name": "Bildory"},
    {"value": 22, "name": "Gamma"},
    {"value": 17, "name": "Beautiful.ai"},
    {"value": 14, "name": "Tome"},
    {"value": 13, "name": "Other"}]}
add_chart(S4, "nightingale", 672, 184, 560, 432, cfg7)
add_text(S4, "Tool preference share, n=2,400", "caption",
         672, 624, 560, 24, color="#7a716a", text_align="center")


# ============================================================
# SLIDE 5 — Demographics & Use Cases (4 charts in 2x2 grid)
# ============================================================
S5 = "slide-5"
add_slide(S5, bg=CREAM)

add_shape(S5, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S5, "Who uses AI decks — and why", "title",
         72, 56, 1160, 64, font_size=44)
add_text(S5, "Demographics, primary use cases, and satisfaction at a glance", "subheading",
         72, 124, 1160, 32, color="#5d564f", font_size=22, font_weight=500)

# 2x2 card backgrounds
GX1, GX2 = 48, 656
GY1, GY2 = 184, 432
GW, GH = 576, 240

add_shape(S5, "rectangle", GX1, GY1, GW, GH, fill=WHITE)
add_shape(S5, "rectangle", GX2, GY1, GW, GH, fill=WHITE)
add_shape(S5, "rectangle", GX1, GY2, GW, GH, fill=WHITE)
add_shape(S5, "rectangle", GX2, GY2, GW, GH, fill=WHITE)

# Card labels
add_text(S5, "By Role", "caption", GX1+16, GY1+12, 200, 20,
         color=AMBER, font_size=14, font_weight=700)
add_text(S5, "By Age Group", "caption", GX2+16, GY1+12, 200, 20,
         color=AMBER, font_size=14, font_weight=700)
add_text(S5, "Top Use Cases", "caption", GX1+16, GY2+12, 200, 20,
         color=AMBER, font_size=14, font_weight=700)
add_text(S5, "Satisfaction", "caption", GX2+16, GY2+12, 200, 20,
         color=AMBER, font_size=14, font_weight=700)

# Chart 8 — By Role (doughnut)
cfg8 = base_chart_cfg(palette=[AMBER, NAVY, "#ca8746", "#3d4f8a", "#cd9352"])
cfg8["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg8["series"] = [{
    "type": "pie",
    "radius": ["40%", "70%"],
    "center": ["50%", "55%"],
    "data": [
        {"value": 32, "name": "Sales"},
        {"value": 24, "name": "Marketing"},
        {"value": 18, "name": "Product"},
        {"value": 14, "name": "Exec"},
        {"value": 12, "name": "Other"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 11,
              "formatter": "{b} {d}%"}
}]
cfg8["tableData"] = {"data": [
    {"value": 32, "name": "Sales"},
    {"value": 24, "name": "Marketing"},
    {"value": 18, "name": "Product"},
    {"value": 14, "name": "Exec"},
    {"value": 12, "name": "Other"}]}
add_chart(S5, "doughnut", GX1+16, GY1+40, GW-32, GH-56, cfg8)

# Chart 9 — Age Group bar
cfg9 = base_chart_cfg()
cfg9["tooltip"] = {"trigger": "axis"}
cfg9["xAxis"] = {"type": "category",
                 "data": ["18-24", "25-34", "35-44", "45-54", "55+"],
                 "axisLabel": {"color": "#1c1917", "fontSize": 11}}
cfg9["yAxis"] = {"type": "value",
                 "axisLabel": {"color": "#1c1917", "fontSize": 10, "formatter": "{value}%"}}
cfg9["series"] = [{"type": "bar",
                   "data": [11, 38, 28, 16, 7],
                   "itemStyle": {"color": NAVY, "borderRadius": [4, 4, 0, 0]}}]
cfg9["tableData"] = {"categories": ["18-24","25-34","35-44","45-54","55+"],
                     "series": [{"name": "Users %", "data": [11, 38, 28, 16, 7]}]}
add_chart(S5, "bar", GX2+16, GY1+40, GW-32, GH-56, cfg9)

# Chart 10 — Use cases bar (horizontal)
cfg10 = base_chart_cfg()
cfg10["tooltip"] = {"trigger": "axis"}
cfg10["xAxis"] = {"type": "value",
                  "axisLabel": {"color": "#1c1917", "fontSize": 10, "formatter": "{value}%"}}
cfg10["yAxis"] = {"type": "category",
                  "data": ["Internal", "Reports", "Training", "Investor", "Sales pitch"],
                  "axisLabel": {"color": "#1c1917", "fontSize": 11}}
cfg10["series"] = [{"type": "bar",
                    "data": [22, 31, 38, 47, 62],
                    "itemStyle": {"color": AMBER, "borderRadius": [0, 4, 4, 0]}}]
cfg10["tableData"] = {"categories": ["Internal","Reports","Training","Investor","Sales pitch"],
                      "series": [{"name": "Frequency",
                                  "data": [22, 31, 38, 47, 62]}]}
add_chart(S5, "bar", GX1+16, GY2+40, GW-32, GH-56, cfg10)

# Chart 11 — Satisfaction pie
cfg11 = base_chart_cfg(palette=[AMBER, "#ca8746", "#cd9352", NAVY])
cfg11["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg11["series"] = [{
    "type": "pie",
    "radius": ["0%", "70%"],
    "center": ["50%", "55%"],
    "data": [
        {"value": 48, "name": "Very satisfied"},
        {"value": 34, "name": "Satisfied"},
        {"value": 12, "name": "Neutral"},
        {"value": 6, "name": "Dissatisfied"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 11,
              "formatter": "{d}%"}
}]
cfg11["tableData"] = {"data": [
    {"value": 48, "name": "Very satisfied"},
    {"value": 34, "name": "Satisfied"},
    {"value": 12, "name": "Neutral"},
    {"value": 6, "name": "Dissatisfied"}]}
add_chart(S5, "pie", GX2+16, GY2+40, GW-32, GH-56, cfg11)


# ============================================================
# SLIDE 6 — Competitive Landscape (2 charts)
# ============================================================
S6 = "slide-6"
add_slide(S6, bg=WHITE)

add_shape(S6, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S6, "A fragmented market — but consolidating fast", "title",
         72, 56, 1160, 64, font_size=40)
add_text(S6, "Top vendor share and quarterly revenue trajectory", "subheading",
         72, 124, 1160, 32, color="#5d564f", font_size=22, font_weight=500)

# Chart 12 — Vendor market share pie
cfg12 = base_chart_cfg(palette=[AMBER, NAVY, "#ca8746", "#3d4f8a", "#cd9352", "#5e6fa1"])
cfg12["tooltip"] = {"trigger": "item", "formatter": "{b}: {d}%"}
cfg12["series"] = [{
    "type": "pie",
    "radius": ["35%", "75%"],
    "center": ["50%", "55%"],
    "data": [
        {"value": 26, "name": "Bildory"},
        {"value": 21, "name": "Gamma"},
        {"value": 15, "name": "Beautiful.ai"},
        {"value": 12, "name": "Tome"},
        {"value": 10, "name": "Pitch"},
        {"value": 16, "name": "Long tail"}
    ],
    "label": {"show": True, "color": "#1c1917", "fontSize": 12,
              "formatter": "{b}\n{d}%"}
}]
cfg12["tableData"] = {"data": [
    {"value": 26, "name": "Bildory"},
    {"value": 21, "name": "Gamma"},
    {"value": 15, "name": "Beautiful.ai"},
    {"value": 12, "name": "Tome"},
    {"value": 10, "name": "Pitch"},
    {"value": 16, "name": "Long tail"}]}
add_chart(S6, "doughnut", 48, 184, 560, 432, cfg12)
add_text(S6, "2026 estimated market share", "caption",
         48, 624, 560, 24, color="#7a716a", text_align="center")

# Chart 13 — Quarterly revenue line (top 3 vendors)
cfg13 = base_chart_cfg(palette=[AMBER, NAVY, "#cd9352"])
cfg13["tooltip"] = {"trigger": "axis"}
cfg13["xAxis"] = {"type": "category",
                  "data": ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25"],
                  "axisLabel": {"color": "#1c1917", "fontSize": 11}}
cfg13["yAxis"] = {"type": "value",
                  "axisLabel": {"color": "#1c1917", "fontSize": 12, "formatter": "${value}M"}}
cfg13["series"] = [
    {"type": "line", "name": "Bildory", "smooth": True,
     "data": [12, 18, 26, 38, 54, 72, 96, 124],
     "lineStyle": {"color": AMBER, "width": 3},
     "itemStyle": {"color": AMBER}},
    {"type": "line", "name": "Gamma", "smooth": True,
     "data": [22, 28, 34, 41, 50, 60, 72, 86],
     "lineStyle": {"color": NAVY, "width": 3},
     "itemStyle": {"color": NAVY}},
    {"type": "line", "name": "Beautiful.ai", "smooth": True,
     "data": [18, 22, 26, 30, 35, 40, 46, 52],
     "lineStyle": {"color": "#cd9352", "width": 3},
     "itemStyle": {"color": "#cd9352"}}
]
cfg13["tableData"] = {"categories": ["Q1'24","Q2'24","Q3'24","Q4'24","Q1'25","Q2'25","Q3'25","Q4'25"],
                      "series": [
                          {"name": "Bildory", "data": [12,18,26,38,54,72,96,124]},
                          {"name": "Gamma", "data": [22,28,34,41,50,60,72,86]},
                          {"name": "Beautiful.ai", "data": [18,22,26,30,35,40,46,52]}]}
cfg13["properties"]["showLegend"] = True
cfg13["legend"] = {"show": True, "top": "bottom", "textStyle": {"color": "#1c1917", "fontSize": 12}}
add_chart(S6, "line", 632, 184, 600, 432, cfg13)
add_text(S6, "Quarterly revenue, top 3 vendors ($M)", "caption",
         632, 624, 600, 24, color="#7a716a", text_align="center")


# ============================================================
# SLIDE 7 — Future Outlook (2 charts)
# ============================================================
S7 = "slide-7"
add_slide(S7, bg=NAVY)

add_shape(S7, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S7, "Where the next $4B will come from", "title",
         72, 56, 1160, 64, font_size=44, color=WHITE)
add_text(S7, "5-year revenue projection and where venture capital is flowing", "subheading",
         72, 124, 1160, 32, color="#a8b1d6", font_size=22, font_weight=500)

# Chart 14 — 5-year projection line
cfg14 = base_chart_cfg(palette=[AMBER, "#ffffff"], dark=True)
cfg14["tooltip"] = {"trigger": "axis"}
cfg14["xAxis"] = {"type": "category",
                  "data": ["2026", "2027", "2028", "2029", "2030"],
                  "axisLabel": {"color": "#ffffff", "fontSize": 13}}
cfg14["yAxis"] = {"type": "value",
                  "axisLabel": {"color": "#ffffff", "fontSize": 12, "formatter": "${value}B"},
                  "splitLine": {"lineStyle": {"color": "#3d4f8a"}}}
cfg14["series"] = [
    {"type": "line", "name": "Conservative", "smooth": True,
     "data": [4.4, 5.1, 5.9, 6.6, 7.2],
     "lineStyle": {"color": "#ffffff", "width": 3, "type": "dashed"},
     "itemStyle": {"color": "#ffffff"}},
    {"type": "line", "name": "Base case", "smooth": True,
     "data": [4.4, 5.8, 7.6, 8.9, 8.4],
     "lineStyle": {"color": AMBER, "width": 4},
     "itemStyle": {"color": AMBER},
     "areaStyle": {"color": AMBER, "opacity": 0.25}}
]
cfg14["tableData"] = {"categories": ["2026","2027","2028","2029","2030"],
                      "series": [
                          {"name": "Conservative", "data": [4.4,5.1,5.9,6.6,7.2]},
                          {"name": "Base case", "data": [4.4,5.8,7.6,8.9,8.4]}]}
cfg14["properties"]["showLegend"] = True
cfg14["legend"] = {"show": True, "top": "bottom",
                   "textStyle": {"color": "#ffffff", "fontSize": 12}}
add_chart(S7, "line", 48, 184, 600, 432, cfg14)
add_text(S7, "Global revenue scenarios, 2026–2030", "caption",
         48, 624, 600, 24, color="#a8b1d6", text_align="center")

# Chart 15 — VC investment bar
cfg15 = base_chart_cfg(dark=True)
cfg15["tooltip"] = {"trigger": "axis"}
cfg15["xAxis"] = {"type": "category",
                  "data": ["Gen-AI\nCopilots", "Multi-modal\nDecks", "Real-time\nCollab", "Enterprise\nSecurity", "Analytics\n& Insights"],
                  "axisLabel": {"color": "#ffffff", "fontSize": 11, "interval": 0}}
cfg15["yAxis"] = {"type": "value",
                  "axisLabel": {"color": "#ffffff", "fontSize": 12, "formatter": "${value}M"},
                  "splitLine": {"lineStyle": {"color": "#3d4f8a"}}}
cfg15["series"] = [{"type": "bar",
                    "data": [840, 620, 410, 290, 180],
                    "itemStyle": {"color": AMBER, "borderRadius": [6, 6, 0, 0]}}]
cfg15["tableData"] = {"categories": ["Gen-AI Copilots","Multi-modal Decks","Real-time Collab","Enterprise Security","Analytics & Insights"],
                      "series": [{"name": "VC ($M)",
                                  "data": [840, 620, 410, 290, 180]}]}
cfg15["properties"]["showDataLabels"] = True
add_chart(S7, "bar", 672, 184, 560, 432, cfg15)
add_text(S7, "VC funding by category, trailing 18 months", "caption",
         672, 624, 560, 24, color="#a8b1d6", text_align="center")


# ============================================================
# SLIDE 8 — Key Takeaways (icons + 1 chart)
# ============================================================
S8 = "slide-8"
add_slide(S8, bg=CREAM)

add_shape(S8, "rectangle", 48, 56, 8, 56, fill=AMBER)
add_text(S8, "Three truths to build the next decade on", "title",
         72, 56, 1160, 64, font_size=40)
add_text(S8, "What every team should know about AI presentations in 2026", "subheading",
         72, 124, 1160, 32, color="#5d564f", font_size=22, font_weight=500)

# Three takeaway cards
CY = 200
CH = 200
def takeaway_card(slide, x, icon, title, body):
    add_shape(slide, "rectangle", x, CY, 384, CH, fill=WHITE)
    add_icon(slide, icon, x+24, CY+24, size=56, color=AMBER)
    add_text(slide, title, "heading", x+24, CY+96, 336, 36, font_size=22)
    add_text(slide, body, "paragraph", x+24, CY+136, 336, 56,
             font_size=14, font_weight=500, color="#5d564f", line_height=1.5)

takeaway_card(S8, 48, "Rocket",
              "Adoption is accelerating",
              "78% of tech teams already use AI-assisted decks; 5x more enterprises will follow by 2028.")
takeaway_card(S8, 448, "Users",
              "Sales drives the wedge",
              "Sales pitches and investor decks are the #1 use case — value is realized in revenue moments.")
takeaway_card(S8, 848, "Trophy",
              "Winner takes most",
              "The top 3 vendors will capture 62% of share; product depth and AI quality drive lock-in.")

# Bottom small chart — confidence levels (heading + bar)
add_text(S8, "Executive confidence in AI deck tools, 2024 vs 2026", "subheading",
         48, 432, 1184, 32, font_size=20)

cfg16 = base_chart_cfg(palette=[NAVY, AMBER])
cfg16["tooltip"] = {"trigger": "axis"}
cfg16["xAxis"] = {"type": "category",
                  "data": ["Not confident", "Somewhat", "Confident", "Very confident"],
                  "axisLabel": {"color": "#1c1917", "fontSize": 12}}
cfg16["yAxis"] = {"type": "value",
                  "axisLabel": {"color": "#1c1917", "fontSize": 12, "formatter": "{value}%"}}
cfg16["series"] = [
    {"type": "bar", "name": "2024",
     "data": [22, 38, 28, 12],
     "itemStyle": {"color": NAVY, "borderRadius": [4, 4, 0, 0]}},
    {"type": "bar", "name": "2026",
     "data": [6, 18, 42, 34],
     "itemStyle": {"color": AMBER, "borderRadius": [4, 4, 0, 0]}}
]
cfg16["tableData"] = {"categories": ["Not confident","Somewhat","Confident","Very confident"],
                      "series": [
                          {"name": "2024", "data": [22, 38, 28, 12]},
                          {"name": "2026", "data": [6, 18, 42, 34]}]}
cfg16["properties"]["showLegend"] = True
cfg16["legend"] = {"show": True, "top": "bottom",
                   "textStyle": {"color": "#1c1917", "fontSize": 12}}
add_chart(S8, "bar", 48, 472, 1184, 200, cfg16)


# ============================================================
# Assemble final JSON
# ============================================================
# Inject text elements into slides
for s in slides_content:
    s["textElements"] = text_by_slide[s["id"]]

# Count elements
text_count = sum(len(text_by_slide[s["id"]]) for s in slides_content)
total_elements = (text_count + len(shape_elements) + len(icon_elements)
                  + len(chart_elements))

content = {
    "slides": slides_content,
    "imageElements": [],
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": [],
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baseLayout = {
    "version": "v1",
    "slides": slides_baselayout,
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

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "AI Presentation Market Study 2026",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": total_elements,
        "createdAt": "2026-05-22T00:00:00.000Z",
        "updatedAt": "2026-05-22T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": baseLayout,
        "changelog": changelog
    }
}

OUT = "ai_presentation_market_study.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {OUT}")
print(f"  slides: {len(slides_content)}")
print(f"  elements: {total_elements}")
print(f"    text: {text_count}")
print(f"    shapes: {len(shape_elements)}")
print(f"    icons: {len(icon_elements)}")
print(f"    charts: {len(chart_elements)}")
