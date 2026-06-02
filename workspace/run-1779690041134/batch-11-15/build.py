import json, time, os

NOW = int(time.time() * 1000)
COUNTER = 600

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ----- Helpers -----

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              font_family="Inter Tight", text_align="left", letter_spacing=0,
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
              size=80, color="#06B6D4", opacity=1, w=None, h=None):
    if w is None: w = size
    if h is None: h = size
    content_record = {
        "id": icon_id, "slideId": slide_id, "groupId": None,
        "iconName": icon_name, "iconSource": "lucide"
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
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


# ----- Containers -----
SLIDE_IDS = [f"slide-{i}" for i in range(11, 16)]

content = {
    "slides": [],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "tableElements": [],
    "iconElements": [],
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baseLayout = {
    "version": "v1",
    "slides": [],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

changelog = {"version": "2.0", "slides": {}}

# Slide backgrounds (per slide narrative mood)
SLIDE_BG = {
    "slide-11": "#0B1020",
    "slide-12": "#0B1020",
    "slide-13": "#0B1020",
    "slide-14": "#0B1020",
    "slide-15": "#0B1020",
}

for sid in SLIDE_IDS:
    content["slides"].append({
        "id": sid,
        "order": SLIDE_IDS.index(sid),
        "layoutId": "blank-canvas",
        "backgroundColor": SLIDE_BG[sid],
        "textElements": []
    })
    baseLayout["slides"].append({
        "id": sid, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [],
        "chartElements": [], "iconElements": [], "embedElements": []
    })
    changelog["slides"][sid] = {"elements": {}}


def add_text(slide_id, *args, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, *args, zidx=n, now=NOW, **kwargs)
    for s in content["slides"]:
        if s["id"] == slide_id:
            s["textElements"].append(c)
            break
    changelog["slides"][slide_id]["elements"][tid] = cl
    return tid

def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid_el = f"shape-{n}"
    c, cl = make_shape(sid_el, slide_id, shape_type, x, y, w, h, zidx=n, now=NOW, **kwargs)
    content["shapeElements"].append(c)
    changelog["slides"][slide_id]["elements"][sid_el] = cl
    return sid_el

def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, zidx=n, now=NOW, **kwargs)
    content["iconElements"].append(c)
    changelog["slides"][slide_id]["elements"][iid] = cl
    return iid

def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = next_id()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, zidx=n, now=NOW, chart_config=chart_config)
    content["chartElements"].append(c)
    changelog["slides"][slide_id]["elements"][cid] = cl
    return cid


# ============================================================
# SLIDE 11 — The Scoreboard of Truth (metrics dashboard)
# ============================================================
sid = "slide-11"

# Top thin rule + chapter tab
add_shape(sid, "rectangle", 64, 56, 32, 2, fill="#06B6D4")
add_text(sid, "11 / 15  ·  EVALUATION", "caption",
         104, 48, 320, 20, color="#CBD5E1", font_size=11,
         font_family="JetBrains Mono", letter_spacing=2, text_transform="uppercase")

# Hero title
add_text(sid, "The Scoreboard of Truth", "title",
         64, 88, 900, 80, color="#F8FAFC",
         font_size=64, font_weight=600, font_family="Playfair Display",
         line_height=1.05)
add_text(sid, "Every model is judged. The numbers decide.", "subtitle",
         64, 168, 900, 36, color="#CBD5E1",
         font_size=22, font_weight=400, font_family="Inter Tight",
         font_style="italic", line_height=1.3)

# Left: Confusion Matrix glassmorphic card (x=64..544, y=232..632)
add_shape(sid, "rectangle", 64, 224, 480, 416, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 64, 224, 480, 2, fill="#2563EB", opacity=0.6)

add_text(sid, "CONFUSION MATRIX", "caption",
         88, 244, 320, 16, color="#06B6D4", font_size=11,
         font_family="JetBrains Mono", letter_spacing=2)

# Axis labels
add_text(sid, "PREDICTED →", "caption", 232, 272, 200, 14,
         color="#CBD5E1", font_size=10, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "ACTUAL ↓", "caption", 88, 392, 80, 14,
         color="#CBD5E1", font_size=10, font_family="JetBrains Mono", letter_spacing=2)

# Matrix cells (2x2). Cells region: x=176..520, y=296..544
# col headers
add_text(sid, "POSITIVE", "caption", 200, 296, 144, 16,
         color="#F8FAFC", font_size=11, font_family="JetBrains Mono",
         text_align="center", letter_spacing=1.5)
add_text(sid, "NEGATIVE", "caption", 360, 296, 144, 16,
         color="#F8FAFC", font_size=11, font_family="JetBrains Mono",
         text_align="center", letter_spacing=1.5)

# row headers
add_text(sid, "POS", "caption", 176, 360, 24, 14,
         color="#F8FAFC", font_size=10, font_family="JetBrains Mono", letter_spacing=1.5)
add_text(sid, "NEG", "caption", 176, 488, 24, 14,
         color="#F8FAFC", font_size=10, font_family="JetBrains Mono", letter_spacing=1.5)

# TP cell
add_shape(sid, "rectangle", 208, 320, 144, 112, fill="#22C55E", opacity=0.22)
add_shape(sid, "rectangle", 208, 320, 144, 2, fill="#22C55E", opacity=0.9)
add_text(sid, "TP", "caption", 216, 328, 60, 14,
         color="#22C55E", font_size=10, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "842", "heading", 216, 348, 128, 56,
         color="#F8FAFC", font_size=44, font_weight=600,
         font_family="Inter Tight", text_align="left")

# FP cell
add_shape(sid, "rectangle", 360, 320, 144, 112, fill="#EF4444", opacity=0.22)
add_shape(sid, "rectangle", 360, 320, 144, 2, fill="#EF4444", opacity=0.9)
add_text(sid, "FP", "caption", 368, 328, 60, 14,
         color="#EF4444", font_size=10, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "47", "heading", 368, 348, 128, 56,
         color="#F8FAFC", font_size=44, font_weight=600,
         font_family="Inter Tight", text_align="left")

# FN cell
add_shape(sid, "rectangle", 208, 448, 144, 112, fill="#F59E0B", opacity=0.22)
add_shape(sid, "rectangle", 208, 448, 144, 2, fill="#F59E0B", opacity=0.9)
add_text(sid, "FN", "caption", 216, 456, 60, 14,
         color="#F59E0B", font_size=10, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "63", "heading", 216, 476, 128, 56,
         color="#F8FAFC", font_size=44, font_weight=600,
         font_family="Inter Tight", text_align="left")

# TN cell
add_shape(sid, "rectangle", 360, 448, 144, 112, fill="#06B6D4", opacity=0.22)
add_shape(sid, "rectangle", 360, 448, 144, 2, fill="#06B6D4", opacity=0.9)
add_text(sid, "TN", "caption", 368, 456, 60, 14,
         color="#06B6D4", font_size=10, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "1,248", "heading", 368, 476, 128, 56,
         color="#F8FAFC", font_size=44, font_weight=600,
         font_family="Inter Tight", text_align="left")

# Insight ribbon under matrix
add_text(sid, "Medical screening: prioritize recall — false negatives are costly.", "caption",
         88, 588, 432, 36, color="#F59E0B", font_size=13,
         font_family="Inter Tight", font_style="italic", line_height=1.4)

# Right column: metric tiles (x=576..1216, y=232..632)
# Tile 1 — Accuracy
add_shape(sid, "rectangle", 576, 224, 304, 124, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 576, 224, 2, 124, fill="#06B6D4")
add_text(sid, "ACCURACY", "caption", 600, 240, 200, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "0.95", "heading", 600, 260, 200, 56,
         color="#F8FAFC", font_size=48, font_weight=600, font_family="Inter Tight")
add_text(sid, "(TP+TN) / total", "caption", 600, 320, 200, 16,
         color="#94A3B8", font_size=11, font_family="JetBrains Mono")

# Tile 2 — Precision
add_shape(sid, "rectangle", 912, 224, 304, 124, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 912, 224, 2, 124, fill="#7C3AED")
add_text(sid, "PRECISION", "caption", 936, 240, 200, 14,
         color="#7C3AED", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "0.947", "heading", 936, 260, 200, 56,
         color="#F8FAFC", font_size=48, font_weight=600, font_family="Inter Tight")
add_text(sid, "TP / (TP+FP)", "caption", 936, 320, 200, 16,
         color="#94A3B8", font_size=11, font_family="JetBrains Mono")

# Tile 3 — Recall
add_shape(sid, "rectangle", 576, 364, 304, 124, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 576, 364, 2, 124, fill="#22C55E")
add_text(sid, "RECALL", "caption", 600, 380, 200, 14,
         color="#22C55E", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "0.930", "heading", 600, 400, 200, 56,
         color="#F8FAFC", font_size=48, font_weight=600, font_family="Inter Tight")
add_text(sid, "TP / (TP+FN)", "caption", 600, 460, 200, 16,
         color="#94A3B8", font_size=11, font_family="JetBrains Mono")

# Tile 4 — F1
add_shape(sid, "rectangle", 912, 364, 304, 124, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 912, 364, 2, 124, fill="#F59E0B")
add_text(sid, "F1 SCORE", "caption", 936, 380, 200, 14,
         color="#F59E0B", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "0.938", "heading", 936, 400, 200, 56,
         color="#F8FAFC", font_size=48, font_weight=600, font_family="Inter Tight")
add_text(sid, "harmonic mean(P,R)", "caption", 936, 460, 200, 16,
         color="#94A3B8", font_size=11, font_family="JetBrains Mono")

# Tile 5 — ROC-AUC large wide
add_shape(sid, "rectangle", 576, 504, 640, 128, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 576, 504, 2, 128, fill="#2563EB")
add_text(sid, "ROC – AUC", "caption", 600, 520, 240, 14,
         color="#2563EB", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "0.973", "heading", 600, 540, 200, 60,
         color="#F8FAFC", font_size=52, font_weight=600, font_family="Inter Tight")

# Mini ROC sparkline using a chart
roc_mini = {
    "tooltip": {"trigger": "item"},
    "xAxis": {"type": "value", "min": 0, "max": 1, "show": False},
    "yAxis": {"type": "value", "min": 0, "max": 1, "show": False},
    "grid": {"left": 0, "right": 0, "top": 4, "bottom": 4, "containLabel": False},
    "series": [
        {"type": "line", "data": [[0,0],[0.05,0.55],[0.15,0.82],[0.3,0.93],[0.6,0.98],[1,1]],
         "smooth": True, "showSymbol": False,
         "lineStyle": {"color": "#06B6D4", "width": 3},
         "areaStyle": {"color": "rgba(6,182,212,0.18)"}},
        {"type": "line", "data": [[0,0],[1,1]], "showSymbol": False,
         "lineStyle": {"color": "#475569", "width": 1, "type": "dashed"}}
    ],
    "backgroundColor": "transparent",
    "color": ["#06B6D4"], "animation": False,
    "textStyle": {"color": "#F8FAFC", "fontSize": 10, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": ["0","1"], "series": [{"name":"ROC","data":[0,1]}]},
    "properties": {"showXAxis": False, "showYAxis": False, "showDataLabels": False,
                   "showLegend": False, "showLabelName": False, "showLabelValue": False,
                   "labelFontSize": 10, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#06B6D4", "1": "#475569"},
    "textColor": "#F8FAFC", "isMonochrome": False
}
add_chart(sid, "line", 880, 516, 320, 104, roc_mini)

add_text(sid, "AUC ≈ 1.0  →  near-perfect class separation", "caption",
         600, 600, 280, 18, color="#CBD5E1", font_size=12,
         font_family="JetBrains Mono", letter_spacing=1)

# Bottom rule + footer
add_shape(sid, "rectangle", 64, 668, 1152, 1, fill="#1E293B")
add_text(sid, "DATA SCIENCE FUNDAMENTALS", "caption",
         64, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "MODEL EVALUATION · BENCHMARK", "caption",
         896, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2, text_align="right")


# ============================================================
# SLIDE 12 — The Confusion Matrix: Where Predictions Meet Reality
# ============================================================
sid = "slide-12"

add_shape(sid, "rectangle", 64, 56, 32, 2, fill="#06B6D4")
add_text(sid, "12 / 15  ·  CLASSIFICATION OUTCOMES", "caption",
         104, 48, 360, 20, color="#CBD5E1", font_size=11,
         font_family="JetBrains Mono", letter_spacing=2, text_transform="uppercase")

add_text(sid, "Where Predictions Meet Reality", "title",
         64, 88, 900, 80, color="#F8FAFC",
         font_size=58, font_weight=600, font_family="Playfair Display",
         line_height=1.05)
add_text(sid, "A 2×2 grid that exposes every model's truth — and its failures.", "subtitle",
         64, 168, 900, 32, color="#CBD5E1",
         font_size=20, font_weight=400, font_family="Inter Tight",
         font_style="italic", line_height=1.3)

# LEFT: large 2x2 matrix command table (x=64..720, y=240..640)
# Outer frame
add_shape(sid, "rectangle", 64, 240, 656, 400, fill="#111A33", opacity=0.85)

# Axis labels
add_text(sid, "PREDICTED", "caption", 240, 256, 480, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono",
         letter_spacing=3, text_align="center")
add_text(sid, "POSITIVE", "caption", 240, 280, 240, 14,
         color="#F8FAFC", font_size=11, font_family="JetBrains Mono",
         letter_spacing=2, text_align="center")
add_text(sid, "NEGATIVE", "caption", 480, 280, 240, 14,
         color="#F8FAFC", font_size=11, font_family="JetBrains Mono",
         letter_spacing=2, text_align="center")

# vertical actual axis — rotated text not supported, so vertical labels stacked
add_text(sid, "A", "caption", 80, 360, 24, 16, color="#06B6D4",
         font_size=12, font_family="JetBrains Mono", text_align="center")
add_text(sid, "C", "caption", 80, 380, 24, 16, color="#06B6D4",
         font_size=12, font_family="JetBrains Mono", text_align="center")
add_text(sid, "T", "caption", 80, 400, 24, 16, color="#06B6D4",
         font_size=12, font_family="JetBrains Mono", text_align="center")
add_text(sid, "U", "caption", 80, 420, 24, 16, color="#06B6D4",
         font_size=12, font_family="JetBrains Mono", text_align="center")
add_text(sid, "A", "caption", 80, 440, 24, 16, color="#06B6D4",
         font_size=12, font_family="JetBrains Mono", text_align="center")
add_text(sid, "L", "caption", 80, 460, 24, 16, color="#06B6D4",
         font_size=12, font_family="JetBrains Mono", text_align="center")

# row labels
add_text(sid, "POS", "caption", 112, 364, 80, 14,
         color="#F8FAFC", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "NEG", "caption", 112, 524, 80, 14,
         color="#F8FAFC", font_size=11, font_family="JetBrains Mono", letter_spacing=2)

# Cells: each cell ~232 wide, 156 tall
# TP (top-left)
add_shape(sid, "rectangle", 240, 308, 232, 156, fill="#06B6D4", opacity=0.18)
add_shape(sid, "rectangle", 240, 308, 232, 2, fill="#06B6D4")
add_text(sid, "TRUE POSITIVE", "caption", 256, 320, 200, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Fraud detected", "subheading", 256, 340, 200, 28,
         color="#F8FAFC", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "Correctly flagged a real fraudulent transaction.", "caption",
         256, 372, 200, 60, color="#CBD5E1", font_size=12,
         font_family="Inter Tight", font_style="italic", line_height=1.4)

# FP (top-right)
add_shape(sid, "rectangle", 480, 308, 232, 156, fill="#EF4444", opacity=0.18)
add_shape(sid, "rectangle", 480, 308, 232, 2, fill="#EF4444")
add_text(sid, "FALSE POSITIVE", "caption", 496, 320, 200, 14,
         color="#EF4444", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Healthy txn flagged", "subheading", 496, 340, 200, 28,
         color="#F8FAFC", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "A safe transaction wrongly marked as fraud.", "caption",
         496, 372, 200, 60, color="#CBD5E1", font_size=12,
         font_family="Inter Tight", font_style="italic", line_height=1.4)

# FN (bottom-left)
add_shape(sid, "rectangle", 240, 472, 232, 156, fill="#F59E0B", opacity=0.20)
add_shape(sid, "rectangle", 240, 472, 232, 2, fill="#F59E0B")
add_text(sid, "FALSE NEGATIVE", "caption", 256, 484, 200, 14,
         color="#F59E0B", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Fraud missed", "subheading", 256, 504, 200, 28,
         color="#F8FAFC", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "A real fraud slipped through undetected.", "caption",
         256, 536, 200, 60, color="#CBD5E1", font_size=12,
         font_family="Inter Tight", font_style="italic", line_height=1.4)

# TN (bottom-right)
add_shape(sid, "rectangle", 480, 472, 232, 156, fill="#22C55E", opacity=0.18)
add_shape(sid, "rectangle", 480, 472, 232, 2, fill="#22C55E")
add_text(sid, "TRUE NEGATIVE", "caption", 496, 484, 200, 14,
         color="#22C55E", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Normal txn cleared", "subheading", 496, 504, 200, 28,
         color="#F8FAFC", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "A clean transaction correctly let through.", "caption",
         496, 536, 200, 60, color="#CBD5E1", font_size=12,
         font_family="Inter Tight", font_style="italic", line_height=1.4)

# RIGHT annotation column (x=752..1216)
add_shape(sid, "rectangle", 752, 240, 2, 400, fill="#1E293B")

add_text(sid, "READING THE GRID", "caption", 776, 244, 320, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)

add_text(sid, "Diagonal", "subheading", 776, 268, 440, 26,
         color="#F8FAFC", font_size=20, font_weight=600, font_family="Inter Tight")
add_text(sid, "TP and TN — where the model's prediction agrees with reality.", "caption",
         776, 296, 440, 36, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", line_height=1.5)

add_text(sid, "Off-Diagonal", "subheading", 776, 348, 440, 26,
         color="#F8FAFC", font_size=20, font_weight=600, font_family="Inter Tight")
add_text(sid, "FP and FN — every error has a different cost depending on context.", "caption",
         776, 376, 440, 50, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", line_height=1.5)

add_text(sid, "Why It Matters", "subheading", 776, 440, 440, 26,
         color="#F8FAFC", font_size=20, font_weight=600, font_family="Inter Tight")
add_text(sid, "Every metric you'll meet next — precision, recall, F1, ROC — is a different way of squeezing meaning from these four numbers.", "caption",
         776, 468, 440, 110, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", line_height=1.55)

# Pull-quote
add_shape(sid, "rectangle", 776, 596, 2, 32, fill="#F59E0B")
add_text(sid, "Behind every accuracy score lies a hidden topology of errors.", "caption",
         792, 596, 424, 36, color="#F59E0B", font_size=13,
         font_family="Inter Tight", font_style="italic", line_height=1.5)

# footer
add_shape(sid, "rectangle", 64, 668, 1152, 1, fill="#1E293B")
add_text(sid, "DATA SCIENCE FUNDAMENTALS", "caption",
         64, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "CLASSIFICATION · OUTCOMES", "caption",
         896, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2, text_align="right")


# ============================================================
# SLIDE 13 — Precision, Recall & F1: The Balance of Consequences
# ============================================================
sid = "slide-13"

add_shape(sid, "rectangle", 64, 56, 32, 2, fill="#7C3AED")
add_text(sid, "13 / 15  ·  METRIC TRADE-OFFS", "caption",
         104, 48, 360, 20, color="#CBD5E1", font_size=11,
         font_family="JetBrains Mono", letter_spacing=2, text_transform="uppercase")

add_text(sid, "Precision, Recall & F1", "title",
         64, 88, 900, 72, color="#F8FAFC",
         font_size=58, font_weight=600, font_family="Playfair Display",
         line_height=1.05)
add_text(sid, "The balance of consequences — every metric carries a cost.", "subtitle",
         64, 160, 900, 32, color="#CBD5E1",
         font_size=20, font_weight=400, font_family="Inter Tight",
         font_style="italic", line_height=1.3)

# LEFT: 3 stacked metric cards (x=64..640, y=216..648)
# Card 1: Precision
add_shape(sid, "rectangle", 64, 216, 576, 132, fill="#111A33", opacity=0.9)
add_shape(sid, "rectangle", 64, 216, 4, 132, fill="#06B6D4")
add_text(sid, "01", "caption", 88, 232, 40, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "PRECISION", "caption", 128, 232, 200, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Precision = TP / (TP + FP)", "heading", 88, 252, 480, 36,
         color="#F8FAFC", font_size=26, font_weight=500,
         font_family="STIX Two Math", font_style="italic")
add_text(sid, "Of all the items the model flagged — how many were actually correct?", "caption",
         88, 296, 460, 18, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", line_height=1.4)
add_text(sid, "Use when false positives are costly  ·  e.g. spam detection", "caption",
         88, 318, 460, 16, color="#06B6D4", font_size=11,
         font_family="JetBrains Mono", letter_spacing=1)

# Card 2: Recall
add_shape(sid, "rectangle", 64, 364, 576, 132, fill="#111A33", opacity=0.9)
add_shape(sid, "rectangle", 64, 364, 4, 132, fill="#7C3AED")
add_text(sid, "02", "caption", 88, 380, 40, 14,
         color="#7C3AED", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "RECALL", "caption", 128, 380, 200, 14,
         color="#7C3AED", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Recall = TP / (TP + FN)", "heading", 88, 400, 480, 36,
         color="#F8FAFC", font_size=26, font_weight=500,
         font_family="STIX Two Math", font_style="italic")
add_text(sid, "Of all the truly positive cases — how many did the model catch?", "caption",
         88, 444, 460, 18, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", line_height=1.4)
add_text(sid, "Use when false negatives are costly  ·  e.g. medical screening", "caption",
         88, 466, 460, 16, color="#7C3AED", font_size=11,
         font_family="JetBrains Mono", letter_spacing=1)

# Card 3: F1
add_shape(sid, "rectangle", 64, 512, 576, 132, fill="#111A33", opacity=0.9)
add_shape(sid, "rectangle", 64, 512, 4, 132, fill="#F59E0B")
add_text(sid, "03", "caption", 88, 528, 40, 14,
         color="#F59E0B", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "F1  ·  HARMONIC BALANCE", "caption", 128, 528, 280, 14,
         color="#F59E0B", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "F1 = 2 · (P · R) / (P + R)", "heading", 88, 548, 480, 36,
         color="#F8FAFC", font_size=26, font_weight=500,
         font_family="STIX Two Math", font_style="italic")
add_text(sid, "Harmonic mean of precision and recall — penalizes extreme imbalance.", "caption",
         88, 592, 460, 18, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", line_height=1.4)
add_text(sid, "Use when classes are imbalanced  ·  e.g. fraud monitoring", "caption",
         88, 614, 460, 16, color="#F59E0B", font_size=11,
         font_family="JetBrains Mono", letter_spacing=1)

# RIGHT: cinematic seesaw / balance diagram (x=672..1216, y=216..648)
add_shape(sid, "rectangle", 672, 216, 544, 432, fill="#111A33", opacity=0.85)
add_shape(sid, "rectangle", 672, 216, 544, 2, fill="#7C3AED", opacity=0.6)
add_text(sid, "THE BALANCE OF CONSEQUENCES", "caption",
         696, 232, 480, 14, color="#7C3AED", font_size=11,
         font_family="JetBrains Mono", letter_spacing=2)

# Fulcrum triangle (use triangle shape) at center (x=920, y=480-520)
add_shape(sid, "triangle", 904, 480, 32, 32, fill="#F59E0B", opacity=0.9)
# Beam (rectangle representing the balance bar) tilted slightly via two segments
# Use a single rectangle horizontal as the seesaw bar
add_shape(sid, "rectangle", 712, 458, 416, 6, fill="#F8FAFC", opacity=0.85)

# Left pan (False Positives) - heavier left
add_shape(sid, "rectangle", 712, 380, 144, 76, fill="#EF4444", opacity=0.20)
add_shape(sid, "rectangle", 712, 380, 144, 2, fill="#EF4444")
add_text(sid, "FALSE POSITIVES", "caption", 720, 392, 128, 14,
         color="#EF4444", font_size=11, font_family="JetBrains Mono",
         letter_spacing=1.5, text_align="center")
add_text(sid, "↑ Precision pays", "caption", 720, 414, 128, 16,
         color="#F8FAFC", font_size=12, font_family="Inter Tight",
         text_align="center", font_style="italic")
add_text(sid, "annoyance · noise · trust", "caption", 720, 432, 128, 14,
         color="#CBD5E1", font_size=10, font_family="JetBrains Mono",
         text_align="center")

# Right pan (False Negatives)
add_shape(sid, "rectangle", 984, 380, 144, 76, fill="#F59E0B", opacity=0.20)
add_shape(sid, "rectangle", 984, 380, 144, 2, fill="#F59E0B")
add_text(sid, "FALSE NEGATIVES", "caption", 992, 392, 128, 14,
         color="#F59E0B", font_size=11, font_family="JetBrains Mono",
         letter_spacing=1.5, text_align="center")
add_text(sid, "↑ Recall pays", "caption", 992, 414, 128, 16,
         color="#F8FAFC", font_size=12, font_family="Inter Tight",
         text_align="center", font_style="italic")
add_text(sid, "missed cases · risk · loss", "caption", 992, 432, 128, 14,
         color="#CBD5E1", font_size=10, font_family="JetBrains Mono",
         text_align="center")

# pillar / base under fulcrum
add_shape(sid, "rectangle", 880, 512, 80, 4, fill="#F8FAFC", opacity=0.6)
add_shape(sid, "rectangle", 856, 516, 128, 2, fill="#1E293B")

# Top-of-card heading
add_text(sid, "Every choice of threshold tilts the scale.", "subheading",
         696, 256, 496, 32, color="#F8FAFC",
         font_size=22, font_weight=600, font_family="Inter Tight")
add_text(sid, "Precision and recall are the two ends of every model's moral economy. F1 is the equilibrium between them.", "caption",
         696, 296, 496, 60, color="#CBD5E1", font_size=13,
         font_family="Inter Tight", font_style="italic", line_height=1.5)

# Bottom note
add_text(sid, "F1 = harmonic mean — punishes imbalance, rewards equilibrium.", "caption",
         696, 568, 496, 18, color="#F59E0B", font_size=12,
         font_family="JetBrains Mono", letter_spacing=1)
add_text(sid, "When precision and recall diverge, F1 collapses faster than the average.", "caption",
         696, 596, 496, 36, color="#CBD5E1", font_size=12,
         font_family="Inter Tight", line_height=1.5)

# footer
add_shape(sid, "rectangle", 64, 668, 1152, 1, fill="#1E293B")
add_text(sid, "DATA SCIENCE FUNDAMENTALS", "caption",
         64, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "PRECISION · RECALL · F1", "caption",
         896, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2, text_align="right")


# ============================================================
# SLIDE 14 — ROC & AUC: Reading the Curve of Confidence
# ============================================================
sid = "slide-14"

add_shape(sid, "rectangle", 64, 56, 32, 2, fill="#2563EB")
add_text(sid, "14 / 15  ·  RECEIVER OPERATING CHARACTERISTIC", "caption",
         104, 48, 480, 20, color="#CBD5E1", font_size=11,
         font_family="JetBrains Mono", letter_spacing=2, text_transform="uppercase")

add_text(sid, "ROC & AUC", "title",
         64, 88, 900, 72, color="#F8FAFC",
         font_size=64, font_weight=600, font_family="Playfair Display",
         line_height=1.05)
add_text(sid, "Reading the curve of confidence — every threshold tells a story.", "subtitle",
         64, 160, 900, 32, color="#CBD5E1",
         font_size=20, font_weight=400, font_family="Inter Tight",
         font_style="italic", line_height=1.3)

# AUC badge — top-right
add_shape(sid, "rectangle", 1008, 224, 208, 88, fill="#111A33", opacity=0.95)
add_shape(sid, "rectangle", 1008, 224, 208, 2, fill="#F59E0B")
add_text(sid, "AUC", "caption", 1024, 240, 80, 14,
         color="#F59E0B", font_size=11, font_family="JetBrains Mono", letter_spacing=3)
add_text(sid, "0.91", "heading", 1024, 256, 180, 48,
         color="#F8FAFC", font_size=44, font_weight=600, font_family="Inter Tight")

# Big ROC chart (x=64..960, y=224..568)
roc_full = {
    "tooltip": {"trigger": "axis"},
    "grid": {"left": 56, "right": 24, "top": 24, "bottom": 56, "containLabel": False},
    "xAxis": {
        "type": "value", "min": 0, "max": 1,
        "name": "False Positive Rate", "nameLocation": "middle", "nameGap": 32,
        "nameTextStyle": {"color": "#94A3B8", "fontSize": 12, "fontFamily": "JetBrains Mono"},
        "axisLine": {"lineStyle": {"color": "#475569"}},
        "axisLabel": {"color": "#94A3B8", "fontSize": 11, "fontFamily": "JetBrains Mono"},
        "splitLine": {"lineStyle": {"color": "#1E293B", "type": "dashed"}}
    },
    "yAxis": {
        "type": "value", "min": 0, "max": 1,
        "name": "True Positive Rate", "nameLocation": "middle", "nameGap": 40,
        "nameTextStyle": {"color": "#94A3B8", "fontSize": 12, "fontFamily": "JetBrains Mono"},
        "axisLine": {"lineStyle": {"color": "#475569"}},
        "axisLabel": {"color": "#94A3B8", "fontSize": 11, "fontFamily": "JetBrains Mono"},
        "splitLine": {"lineStyle": {"color": "#1E293B", "type": "dashed"}}
    },
    "series": [
        {"name": "Random Guess", "type": "line",
         "data": [[0,0],[1,1]], "showSymbol": False,
         "lineStyle": {"color": "#64748B", "width": 1.5, "type": "dashed"}},
        {"name": "Model ROC", "type": "line",
         "data": [[0,0],[0.04,0.32],[0.08,0.55],[0.14,0.72],[0.22,0.83],
                  [0.34,0.90],[0.5,0.94],[0.7,0.97],[0.85,0.99],[1,1]],
         "smooth": True, "showSymbol": True,
         "symbolSize": 8,
         "lineStyle": {"color": "#2563EB", "width": 4},
         "itemStyle": {"color": "#06B6D4", "borderColor": "#F8FAFC", "borderWidth": 2},
         "areaStyle": {"color": "rgba(37,99,235,0.22)"}}
    ],
    "backgroundColor": "transparent",
    "color": ["#64748B", "#2563EB"], "animation": False,
    "textStyle": {"color": "#F8FAFC", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {"categories": ["0","0.25","0.5","0.75","1"],
                  "series": [{"name":"Model","data":[0,0.85,0.94,0.98,1]}]},
    "properties": {"showXAxis": True, "showYAxis": True, "showDataLabels": False,
                   "showLegend": False, "showLabelName": True, "showLabelValue": False,
                   "labelFontSize": 12, "labelBold": False, "labelItalic": False,
                   "labelUnderline": False, "labelStrike": False},
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#64748B", "1": "#2563EB"},
    "textColor": "#F8FAFC", "isMonochrome": False
}
add_chart(sid, "line", 64, 216, 928, 360, roc_full)

# Annotation labels floating over chart
add_text(sid, "RANDOM GUESS", "caption", 720, 528, 200, 14,
         color="#64748B", font_size=10, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "MODEL ROC", "caption", 200, 280, 200, 14,
         color="#2563EB", font_size=10, font_family="JetBrains Mono", letter_spacing=2)

# Threshold snapshot strip (bottom)
add_text(sid, "THRESHOLD SNAPSHOTS", "caption", 64, 588, 320, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)

# Four mini threshold cards
def threshold_card(x, label, p, r, color):
    add_shape(sid, "rectangle", x, 608, 220, 48, fill="#111A33", opacity=0.9)
    add_shape(sid, "rectangle", x, 608, 2, 48, fill=color)
    add_text(sid, label, "caption", x+12, 614, 100, 14,
             color=color, font_size=10, font_family="JetBrains Mono", letter_spacing=2)
    add_text(sid, p, "caption", x+12, 632, 100, 16,
             color="#F8FAFC", font_size=12, font_family="Inter Tight", font_weight=500)
    add_text(sid, r, "caption", x+116, 632, 96, 16,
             color="#CBD5E1", font_size=12, font_family="Inter Tight")

threshold_card(64,  "τ = 0.10", "P 0.62", "R 0.98", "#F59E0B")
threshold_card(304, "τ = 0.30", "P 0.81", "R 0.93", "#22C55E")
threshold_card(544, "τ = 0.50", "P 0.91", "R 0.85", "#06B6D4")
threshold_card(784, "τ = 0.80", "P 0.97", "R 0.62", "#7C3AED")

# Right side annotation panel
add_shape(sid, "rectangle", 1008, 332, 208, 240, fill="#111A33", opacity=0.9)
add_shape(sid, "rectangle", 1008, 332, 2, 240, fill="#06B6D4")
add_text(sid, "READING THE CURVE", "caption", 1024, 348, 184, 14,
         color="#06B6D4", font_size=11, font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "Higher area =", "subheading", 1024, 372, 184, 26,
         color="#F8FAFC", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "stronger separability between the two classes.", "caption",
         1024, 400, 184, 50, color="#CBD5E1", font_size=12,
         font_family="Inter Tight", line_height=1.5)
add_text(sid, "0.5", "subheading", 1024, 460, 60, 26,
         color="#64748B", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "= random", "caption", 1080, 466, 130, 18,
         color="#64748B", font_size=12, font_family="Inter Tight")
add_text(sid, "1.0", "subheading", 1024, 488, 60, 26,
         color="#22C55E", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "= perfect", "caption", 1080, 494, 130, 18,
         color="#22C55E", font_size=12, font_family="Inter Tight")
add_text(sid, "0.91", "subheading", 1024, 516, 70, 26,
         color="#F59E0B", font_size=18, font_weight=600, font_family="Inter Tight")
add_text(sid, "= excellent", "caption", 1090, 522, 120, 18,
         color="#F59E0B", font_size=12, font_family="Inter Tight")

# footer
add_shape(sid, "rectangle", 64, 668, 1152, 1, fill="#1E293B")
add_text(sid, "DATA SCIENCE FUNDAMENTALS", "caption",
         64, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "ROC · AUC · THRESHOLDS", "caption",
         896, 680, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2, text_align="right")


# ============================================================
# SLIDE 15 — The Data Science Compass: From Question to Decision
# ============================================================
sid = "slide-15"

add_shape(sid, "rectangle", 64, 56, 32, 2, fill="#F59E0B")
add_text(sid, "15 / 15  ·  FINALE", "caption",
         104, 48, 280, 20, color="#CBD5E1", font_size=11,
         font_family="JetBrains Mono", letter_spacing=3, text_transform="uppercase")

add_text(sid, "The Data Science Compass", "title",
         64, 88, 1152, 80, color="#F8FAFC",
         font_size=58, font_weight=600, font_family="Playfair Display",
         line_height=1.05, text_align="center")
add_text(sid, "From question to decision — the six fundamentals in orbit.", "subtitle",
         64, 168, 1152, 32, color="#CBD5E1",
         font_size=20, font_weight=400, font_family="Inter Tight",
         font_style="italic", line_height=1.3, text_align="center")

# Compass center — circle at canvas center (640, 432)
# Outer rings
add_shape(sid, "circle", 320, 224, 640, 320, fill="#0B1020",
          stroke="#1E293B", stroke_width=1, opacity=0.7)
add_shape(sid, "circle", 400, 264, 480, 240, fill="#0B1020",
          stroke="#1E293B", stroke_width=1, opacity=0.7)
add_shape(sid, "circle", 480, 304, 320, 160, fill="#0B1020",
          stroke="#2563EB", stroke_width=1, opacity=0.5)

# Center node — DECISION
add_shape(sid, "circle", 568, 352, 144, 72, fill="#F59E0B", opacity=0.18)
add_shape(sid, "circle", 584, 360, 112, 56, fill="#F59E0B", opacity=0.95)
add_text(sid, "DECISION", "caption", 584, 376, 112, 18,
         color="#0B1020", font_size=14, font_weight=600,
         font_family="Inter Tight", letter_spacing=3, text_align="center")
add_text(sid, "the destination", "caption", 568, 400, 144, 16,
         color="#F8FAFC", font_size=10, font_family="JetBrains Mono",
         font_style="italic", text_align="center")

# Six orbiting nodes positioned around the center (640, 388 vertical center)
# Center of compass: (640, 388). Use radius ~220.
# Hex positions (angles 0°, 60°, 120°, 180°, 240°, 300°)
import math
cx, cy = 640, 388
R = 232
nodes = [
    ("STATISTICS",         0,   "#06B6D4", "Center · Spread · Shape"),
    ("PROBABILITY",       60,   "#7C3AED", "Likelihood · Conditioning"),
    ("HYPOTHESIS TESTING",120,  "#EF4444", "H₀ vs H₁ · p-value"),
    ("REGRESSION",       180,   "#2563EB", "ŷ = β₀ + β₁x"),
    ("CLASSIFICATION",   240,   "#22C55E", "Decision boundary"),
    ("EVALUATION",       300,   "#F59E0B", "Precision · Recall · AUC"),
]

for label, deg, color, sub in nodes:
    rad = math.radians(deg - 90)  # start at top
    nx = cx + R * math.cos(rad)
    ny = cy + R * math.sin(rad) * 0.55  # squish vertically to fit canvas
    nx = int(nx)
    ny = int(ny)
    # connecting line — represented as a thin rectangle from center toward node (approx)
    # We'll draw a thin radial line as a small rectangle near the node base
    # Skip exact rotation; use small node circles + label cards
    # Node circle
    add_shape(sid, "circle", nx-28, ny-28, 56, 56, fill=color, opacity=0.22,
              stroke=color, stroke_width=2)
    add_shape(sid, "circle", nx-8, ny-8, 16, 16, fill=color, opacity=1)
    # Label card placement based on quadrant
    label_w = 200
    label_h = 48
    # decide label offset
    if deg == 0:        # top
        lx, ly = nx - label_w//2, ny - 86
    elif deg == 60:     # upper-right
        lx, ly = nx + 36, ny - 32
    elif deg == 120:    # lower-right
        lx, ly = nx + 36, ny - 8
    elif deg == 180:    # bottom
        lx, ly = nx - label_w//2, ny + 40
    elif deg == 240:    # lower-left
        lx, ly = nx - label_w - 36, ny - 8
    else:               # upper-left (300)
        lx, ly = nx - label_w - 36, ny - 32

    add_text(sid, label, "caption", lx, ly, label_w, 16,
             color=color, font_size=11, font_family="JetBrains Mono",
             letter_spacing=2,
             text_align="center" if deg in (0,180) else ("left" if deg in (60,120) else "right"))
    add_text(sid, sub, "caption", lx, ly+20, label_w, 18,
             color="#CBD5E1", font_size=11, font_family="Inter Tight",
             font_style="italic",
             text_align="center" if deg in (0,180) else ("left" if deg in (60,120) else "right"))

# Closing statement near bottom
add_shape(sid, "rectangle", 320, 612, 640, 1, fill="#F59E0B", opacity=0.4)
add_text(sid, "Data science is the craft of turning uncertainty into action.", "subtitle",
         64, 624, 1152, 36, color="#F8FAFC",
         font_size=24, font_weight=500, font_family="Playfair Display",
         font_style="italic", line_height=1.3, text_align="center")

# footer
add_shape(sid, "rectangle", 64, 692, 1152, 1, fill="#1E293B")
add_text(sid, "DATA SCIENCE FUNDAMENTALS", "caption",
         64, 700, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=2)
add_text(sid, "FIN  ·  THANK YOU", "caption",
         896, 700, 320, 16, color="#475569", font_size=10,
         font_family="JetBrains Mono", letter_spacing=3, text_align="right")


# ============================================================
# Build envelope
# ============================================================
total_elements = (
    sum(len(s["textElements"]) for s in content["slides"])
    + len(content["imageElements"])
    + len(content["shapeElements"])
    + len(content["chartElements"])
    + len(content["tableElements"])
    + len(content["iconElements"])
    + len(content["embedElements"])
    + len(content["smartDiagramElements"])
    + len(content["groupElements"])
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-11-15-{NOW}",
        "title": "Data Science Fundamentals (Slides 11-15)",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(content["slides"]),
        "elementCount": total_elements,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": baseLayout,
        "changelog": changelog
    }
}

out = "deck.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(envelope, f, ensure_ascii=False, indent=2)

print(f"WROTE {out}")
print(f"slides={len(content['slides'])} elements={total_elements}")
