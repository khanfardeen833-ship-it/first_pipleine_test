import json, time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-5"

# Palette
BG       = "#0B1020"  # Obsidian Console
PANEL    = "#171C2E"  # Graphite Panel
NAVY     = "#1E3A5F"  # Blueprint Navy
CYAN     = "#22D3EE"  # Signal Cyan
GREEN    = "#22C55E"  # Merge Green
AMBER    = "#F59E0B"  # Alert Amber
RED      = "#EF4444"  # Incident Red
LAVENDER = "#A78BFA"  # Cloud Lavender
WHITE    = "#F8FAFC"  # Paper White
STEEL    = "#94A3B8"  # Muted Steel

COUNTER = 600
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

text_by_slide = {SLIDE_ID: []}
shape_elements = []
icon_elements = []
image_elements = []
chart_elements = []
table_elements = []
changelog_elements = {}

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx,
              color=WHITE, font_size=None, font_weight=None, line_height=None,
              text_align="left", font_family="Space Grotesk", letter_spacing=0):
    DEFAULTS = {
        "title": (60, 700, 1.05),
        "subtitle": (40, 600, 1.35),
        "heading": (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph": (22, 700, 1.50),
        "caption": (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None: fs = font_size
    if font_weight is not None: fw = font_weight
    if line_height is not None: lh = line_height

    content = {
        "id": text_id, "content": text, "type": type_,
        "originalType": type_, "groupId": None, "formattedContent": text
    }
    cl = {
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
        "animationTypewriterMode": "character", "updatedAt": NOW
    }
    return content, cl

def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx,
               fill, stroke=None, stroke_width=0, opacity=1):
    if stroke is None:
        stroke = fill
    content = {"id": shape_id, "slideId": slide_id, "groupId": None}
    cl = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "opacity": opacity,
        "shapeType": shape_type,
        "fill": fill, "stroke": stroke, "strokeWidth": stroke_width,
        "updatedAt": NOW
    }
    return content, cl

def make_icon(icon_id, slide_id, icon_name, x, y, zidx, size=64, color=CYAN, opacity=1):
    content = {
        "id": icon_id, "slideId": slide_id, "groupId": None,
        "iconName": icon_name, "iconSource": "lucide"
    }
    cl = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": size, "height": size, "rotation": 0,
        "zIndex": zidx, "color": color, "opacity": opacity,
        "updatedAt": NOW
    }
    return content, cl

def add_shape(shape_type, x, y, w, h, fill, stroke=None, stroke_width=0, opacity=1):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n,
                       fill=fill, stroke=stroke, stroke_width=stroke_width, opacity=opacity)
    shape_elements.append(c)
    changelog_elements[sid] = cl

def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, n, **kwargs)
    text_by_slide[SLIDE_ID].append(c)
    changelog_elements[tid] = cl

def add_icon(icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, icon_name, x, y, n, **kwargs)
    icon_elements.append(c)
    changelog_elements[iid] = cl

# ---- Build slide ----

# 1. Full-bleed background
add_shape("rectangle", 0, 0, 1280, 720, BG)

# 2. Subtle blueprint grid bands (very faint horizontal accent strips)
add_shape("rectangle", 0, 240, 1280, 1, NAVY, opacity=0.45)
add_shape("rectangle", 0, 600, 1280, 1, NAVY, opacity=0.35)

# 3. Top-left signal accent bar (cyan tick)
add_shape("rectangle", 48, 56, 72, 2, CYAN)

# 4. Eyebrow label (mono caption)
add_text("PRINCIPLE  02   //   TESTING DISCIPLINE", "caption",
         48, 72, 600, 18,
         color=CYAN, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=3)

# 5. Hero title
add_text("Tests as Safety Nets", "title",
         48, 104, 920, 80,
         color=WHITE, font_size=68, font_weight=700, line_height=1.05)

# 6. Subtitle / lead
add_text("Layered confidence — every commit travels through invisible nets that catch regressions before users do.",
         "paragraph", 48, 192, 800, 56,
         color=STEEL, font_size=20, font_weight=400, line_height=1.45)

# ---- Pyramid (left half) ----

# Section eyebrow above pyramid
add_text("THE TEST PYRAMID", "caption",
         80, 280, 320, 16,
         color=STEEL, font_size=11, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=2)

# Pyramid container subtle backplate
add_shape("rectangle", 64, 308, 552, 232, PANEL, opacity=0.55)
add_shape("rectangle", 64, 308, 2, 232, NAVY, opacity=1)

# --- Pyramid top tier (E2E) ---
add_shape("rectangle", 264, 320, 152, 52, LAVENDER, opacity=0.18)
add_shape("rectangle", 264, 320, 3, 52, LAVENDER, opacity=1)
add_text("E2E   ·   10%", "subheading",
         276, 334, 140, 24,
         color=WHITE, font_size=15, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1)

# --- Pyramid middle tier (Integration) ---
add_shape("rectangle", 200, 384, 280, 52, CYAN, opacity=0.16)
add_shape("rectangle", 200, 384, 3, 52, CYAN, opacity=1)
add_text("INTEGRATION   ·   30%", "subheading",
         212, 398, 268, 24,
         color=WHITE, font_size=15, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1)

# --- Pyramid base tier (Unit) ---
add_shape("rectangle", 96, 448, 488, 52, GREEN, opacity=0.18)
add_shape("rectangle", 96, 448, 3, 52, GREEN, opacity=1)
add_text("UNIT TESTS   ·   60%", "subheading",
         108, 462, 472, 24,
         color=WHITE, font_size=15, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1)

# Pyramid principles strip (amber accent)
add_text("Fast   ·   Deterministic   ·   Isolated   ·   Meaningful", "caption",
         80, 560, 540, 18,
         color=AMBER, font_size=12, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=2)

# Tiny pyramid annotations to right of base tier (counts in mono)
add_text("4,231 tests", "caption",
         96, 512, 200, 14,
         color=STEEL, font_size=10, font_weight=400,
         font_family="JetBrains Mono", letter_spacing=1)

# ---- KPI dashboard (right half) ----

# Section eyebrow
add_text("PIPELINE METRICS   ·   LAST 7 DAYS", "caption",
         672, 280, 400, 16,
         color=STEEL, font_size=11, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=2)

def kpi_card(x, y, label, value, sub, accent):
    # card
    add_shape("rectangle", x, y, 270, 110, PANEL, opacity=1)
    # accent rail
    add_shape("rectangle", x, y, 3, 110, accent, opacity=1)
    # label
    add_text(label, "caption",
             x + 18, y + 16, 240, 14,
             color=STEEL, font_size=10, font_weight=600,
             font_family="JetBrains Mono", letter_spacing=2)
    # value
    add_text(value, "heading",
             x + 18, y + 38, 240, 50,
             color=WHITE, font_size=36, font_weight=700,
             font_family="JetBrains Mono", line_height=1.1)
    # sub-caption
    add_text(sub, "caption",
             x + 18, y + 86, 240, 14,
             color=accent, font_size=10, font_weight=500,
             font_family="JetBrains Mono", letter_spacing=1)

kpi_card(672, 312, "COVERAGE",     "92.4%", "+1.8 vs prior week",  GREEN)
kpi_card(962, 312, "FLAKINESS",    "0.4%",  "-0.2 trending down",  AMBER)
kpi_card(672, 442, "AVG RUNTIME",  "3:42",  "p95 within budget",   CYAN)
kpi_card(962, 442, "PASS RATE",    "99.7%", "4,812 / 4,827 green", GREEN)

# ---- Bottom: terminal echo line ----
add_shape("rectangle", 672, 568, 560, 1, NAVY, opacity=0.7)

# tiny green status dot
add_shape("circle", 676, 588, 8, 8, GREEN, opacity=1)

add_text("$ pytest --cov  →  4,812 passed   ·   15 skipped   ·   0 failed   ·   3m 42s",
         "caption", 696, 584, 560, 16,
         color=STEEL, font_size=11, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=1)

# ---- Footer pagination ----
add_text("ENGINEERING EXCELLENCE   ·   05 / 15", "caption",
         48, 678, 600, 14,
         color=STEEL, font_size=10, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=2)

add_text("tests/safety-nets.md", "caption",
         1000, 678, 232, 14,
         color=STEEL, font_size=10, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=1, text_align="right")

# ---- Assemble envelope ----

slide_obj = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": BG,
    "textElements": text_by_slide[SLIDE_ID]
}

content_file = {
    "slides": [slide_obj],
    "imageElements": image_elements,
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": table_elements,
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

base_layout = {
    "version": "v1",
    "slides": [{
        "id": SLIDE_ID,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    }],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

changelog_file = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {"elements": changelog_elements}
    }
}

elem_count = (
    len(text_by_slide[SLIDE_ID]) +
    len(shape_elements) +
    len(image_elements) +
    len(chart_elements) +
    len(table_elements) +
    len(icon_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}-slide5",
        "title": "Engineering Excellence — Slide 5: Tests as Safety Nets",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
        "elementCount": elem_count,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": base_layout,
        "changelog": changelog_file
    }
}

OUT = "deck_slide_5.json"
with open(OUT, "w") as f:
    json.dump(deck, f, indent=2)

# Sanity: confirm changelog/content sync
content_ids = set()
for t in text_by_slide[SLIDE_ID]:
    content_ids.add(t["id"])
for s in shape_elements:
    content_ids.add(s["id"])
for i in icon_elements:
    content_ids.add(i["id"])
cl_ids = set(changelog_elements.keys())
missing_in_cl = content_ids - cl_ids
orphan_in_cl  = cl_ids - content_ids

print(f"Wrote {OUT}")
print(f"slideCount: 1")
print(f"elementCount: {elem_count}")
print(f"  text:   {len(text_by_slide[SLIDE_ID])}")
print(f"  shape:  {len(shape_elements)}")
print(f"  icon:   {len(icon_elements)}")
print(f"id range: 601..{COUNTER}")
print(f"missing in changelog: {missing_in_cl}")
print(f"orphan in changelog:  {orphan_in_cl}")
