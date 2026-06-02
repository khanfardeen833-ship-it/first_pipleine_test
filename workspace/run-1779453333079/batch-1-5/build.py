import json, time

NOW = int(time.time() * 1000)

# ---------------- Palette ----------------
ESPRESSO = "#2A1710"
CLAY     = "#6B3F2A"
GOLD     = "#C99A55"
CREAM    = "#F6EFE4"
GREEN    = "#4F6F45"
CHERRY   = "#A53A2B"
MIST     = "#9DA9A7"
JEBENA   = "#12100E"
AMBER    = "#E0B06A"
TAUPE    = "#B8A48E"

# ---------------- Counters ----------------
ZIDX = 0
def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX

# ---------------- Helpers ----------------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color=ESPRESSO, font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", font_style="normal", text_align="left",
              letter_spacing=0, text_transform="none", text_decoration="none",
              opacity=1):
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
            "fontWeight": fw, "fontStyle": font_style, "textDecoration": text_decoration,
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
               fill=CLAY, stroke=None, stroke_width=0, opacity=1):
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


def make_image(image_id, slide_id, src, x, y, w, h, zidx, now,
               is_background=False, border_radius=0, opacity=1):
    content_record = {
        "id": image_id, "slideId": slide_id, "groupId": None,
        "src": src, "s3Key": None,
        "isBackground": is_background, "_smartDiagram": False
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "opacity": opacity,
        "borderRadius": border_radius,
        "shadow": {"enabled": False, "angle": 135, "color": "#000000",
                   "opacity": 40, "distance": 8, "blur": 12, "size": 0, "spread": 0},
        "border": {"type": "none", "width": 4, "color": "#000000", "specialStyle": None},
        "cropRatio": "free",
        "cropRect": {"left": 0, "top": 0, "right": 0, "bottom": 0},
        "focusPoint": {"x": 50, "y": 50},
        "updatedAt": now
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=64, color=GOLD, opacity=1):
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


# ---------------- Containers ----------------
slides = []
baseLayout_slides = []
text_by_slide = {}
image_elements = []
shape_elements = []
icon_elements = []
chart_elements = []
table_elements = []

changelog_slides = {}

def init_slide(slide_id, order, bg):
    slides.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg, "textElements": []
    })
    baseLayout_slides.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

def add_text(slide_id, text_id, *args, **kwargs):
    c, cl = make_text(text_id, slide_id, *args, now=NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][text_id] = cl

def add_shape(slide_id, shape_id, *args, **kwargs):
    c, cl = make_shape(shape_id, slide_id, *args, now=NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][shape_id] = cl

def add_image(slide_id, image_id, *args, **kwargs):
    c, cl = make_image(image_id, slide_id, *args, now=NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][image_id] = cl

def add_icon(slide_id, icon_id, *args, **kwargs):
    c, cl = make_icon(icon_id, slide_id, *args, now=NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][icon_id] = cl


# Pexels imagery (cinematic Ethiopia / coffee documentary)
IMG_HIGHLANDS_MIST   = "https://images.pexels.com/photos/957024/forest-trees-perspective-bright-957024.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
IMG_KALDI_GOATS      = "https://images.pexels.com/photos/2647053/pexels-photo-2647053.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
IMG_LANDSCAPE_AERIAL = "https://images.pexels.com/photos/1366919/pexels-photo-1366919.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
IMG_HIGHLAND_PAN     = "https://images.pexels.com/photos/2049422/pexels-photo-2049422.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
IMG_CHERRY_HANDS     = "https://images.pexels.com/photos/4820817/pexels-photo-4820817.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

# =====================================================================
# SLIDE 1 — Birthplace in the Mist
# =====================================================================
S1 = "slide-1"
init_slide(S1, 0, ESPRESSO)

# Full-bleed hero image
add_image(S1, "image-1", IMG_HIGHLANDS_MIST, 0, 0, 1280, 720, nextz(), is_background=True)

# Espresso gradient overlay (dark wash for text legibility)
add_shape(S1, "shape-2", "rectangle", 0, 0, 1280, 720, nextz(), fill=ESPRESSO, opacity=0.45)

# Bottom-left dark gradient block (anchors title)
add_shape(S1, "shape-3", "rectangle", 0, 420, 760, 300, nextz(), fill=ESPRESSO, opacity=0.55)

# Top thin gold accent rule
add_shape(S1, "shape-4", "rectangle", 96, 96, 80, 2, nextz(), fill=GOLD)

# Top-left chapter mono label
add_text(S1, "text-5", "CHAPTER  I  /  XV", "caption",
         x=192, y=86, w=300, h=24, zidx=nextz(),
         color=GOLD, font_size=12, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

# Top-right metadata
add_text(S1, "text-6", "ETHIOPIA  /  EAST AFRICA", "caption",
         x=920, y=86, w=280, h=20, zidx=nextz(),
         color=CREAM, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono", text_align="right")

add_text(S1, "text-7", "ORIGIN ALTITUDE  /  1,500 — 2,200 M", "caption",
         x=900, y=110, w=300, h=20, zidx=nextz(),
         color=MIST, font_size=11, font_weight=500,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono", text_align="right")

# Hero serif title — "Origin:" small line
add_text(S1, "text-8", "an editorial journey", "caption",
         x=96, y=448, w=400, h=22, zidx=nextz(),
         color=GOLD, font_size=12, font_weight=500,
         letter_spacing=5, text_transform="uppercase",
         font_family="JetBrains Mono")

# Hero serif title — main "Origin"
add_text(S1, "text-9", "Origin:", "title",
         x=96, y=480, w=900, h=110, zidx=nextz(),
         color=CREAM, font_size=104, font_weight=300,
         line_height=1.0, font_family="Playfair Display")

# Italic continuation line — Ethiopia, the First Cup
add_text(S1, "text-10", "Ethiopia, the first cup.", "title",
         x=96, y=590, w=900, h=70, zidx=nextz(),
         color=AMBER, font_size=44, font_weight=400,
         font_style="italic", line_height=1.1,
         font_family="Playfair Display")

# Bottom-right credit/coordinate strip
add_shape(S1, "shape-11", "rectangle", 968, 660, 220, 1, nextz(), fill=GOLD, opacity=0.6)

add_text(S1, "text-12", "9.1450° N   40.4897° E", "caption",
         x=968, y=672, w=220, h=18, zidx=nextz(),
         color=CREAM, font_size=11, font_weight=500,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono", text_align="right")

# Bottom-left signature
add_text(S1, "text-13", "A documentary in fifteen frames", "caption",
         x=96, y=672, w=400, h=18, zidx=nextz(),
         color=MIST, font_size=11, font_weight=400,
         letter_spacing=2, font_style="italic",
         font_family="Playfair Display")

# =====================================================================
# SLIDE 2 — The Legend of Kaldi
# =====================================================================
S2 = "slide-2"
init_slide(S2, 1, CREAM)

# Left image panel (split editorial 0..640)
add_image(S2, "image-14", IMG_KALDI_GOATS, 0, 0, 640, 720, nextz())

# Soft warm overlay on image bottom for caption strip
add_shape(S2, "shape-15", "rectangle", 0, 600, 640, 120, nextz(), fill=ESPRESSO, opacity=0.55)

# Image caption (mono) — like a museum label
add_text(S2, "text-16", "FOLKLORE  /  C. 850 CE", "caption",
         x=32, y=624, w=300, h=20, zidx=nextz(),
         color=GOLD, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

add_text(S2, "text-17", "The Goatherd of Kaffa Province", "caption",
         x=32, y=652, w=560, h=24, zidx=nextz(),
         color=CREAM, font_size=14, font_weight=400,
         font_style="italic", letter_spacing=1,
         font_family="Playfair Display")

# Right panel — cream parchment text column
# Vertical hairline divider between image and text
add_shape(S2, "shape-18", "rectangle", 640, 96, 1, 528, nextz(), fill=TAUPE, opacity=0.6)

# Chapter marker
add_text(S2, "text-19", "II.", "title",
         x=688, y=96, w=120, h=80, zidx=nextz(),
         color=CHERRY, font_size=64, font_weight=400,
         font_family="Playfair Display", font_style="italic",
         line_height=1.0)

# Small kicker
add_text(S2, "text-20", "ORIGIN MYTH", "caption",
         x=820, y=120, w=240, h=20, zidx=nextz(),
         color=CLAY, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase",
         font_family="JetBrains Mono")

# Stacked serif title
add_text(S2, "text-21", "The Legend", "title",
         x=688, y=200, w=520, h=80, zidx=nextz(),
         color=ESPRESSO, font_size=64, font_weight=400,
         line_height=1.0, font_family="Playfair Display")

add_text(S2, "text-22", "of Kaldi.", "title",
         x=688, y=270, w=520, h=80, zidx=nextz(),
         color=CHERRY, font_size=64, font_weight=400,
         font_style="italic", line_height=1.0,
         font_family="Playfair Display")

# Thin gold rule under headline
add_shape(S2, "shape-23", "rectangle", 688, 372, 60, 2, nextz(), fill=GOLD)

# Pull quote (oversized italic)
add_text(S2, "text-24",
         "“A small red fruit\nchanged the rhythm\nof the world.”",
         "subtitle",
         x=688, y=396, w=520, h=160, zidx=nextz(),
         color=CLAY, font_size=30, font_weight=400,
         font_style="italic", line_height=1.25,
         font_family="Playfair Display")

# Body narrative
add_text(S2, "text-25",
         "An Ethiopian goatherd watched his flock dance through highland scrub after tasting a curious crimson cherry. He carried a handful to a nearby monastery — and from that single observation, a global ritual was born.",
         "paragraph",
         x=688, y=572, w=520, h=80, zidx=nextz(),
         color=ESPRESSO, font_size=15, font_weight=400,
         line_height=1.65, font_family="Inter")

# Bottom mono attribution
add_text(S2, "text-26", "ETHIOPIAN ORAL TRADITION  /  KAFFA HIGHLANDS", "caption",
         x=688, y=672, w=520, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

# =====================================================================
# SLIDE 3 — The Coffee Map of Ethiopia
# =====================================================================
S3 = "slide-3"
init_slide(S3, 2, CREAM)

# Right-side atmospheric landscape image
add_image(S3, "image-27", IMG_LANDSCAPE_AERIAL, 760, 0, 520, 720, nextz())

# Espresso wash on image for tone
add_shape(S3, "shape-28", "rectangle", 760, 0, 520, 720, nextz(), fill=ESPRESSO, opacity=0.32)

# Bottom caption strip on image
add_text(S3, "text-29", "ORIGIN ATLAS  /  PLATE  03", "caption",
         x=792, y=672, w=460, h=18, zidx=nextz(),
         color=GOLD, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

# Left content area (cream)
# Top kicker + chapter
add_text(S3, "text-30", "III.  /  GEOGRAPHY OF FLAVOR", "caption",
         x=96, y=96, w=400, h=20, zidx=nextz(),
         color=CHERRY, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase",
         font_family="JetBrains Mono")

# Title (two lines)
add_text(S3, "text-31", "The Coffee Map", "title",
         x=96, y=140, w=680, h=80, zidx=nextz(),
         color=ESPRESSO, font_size=58, font_weight=400,
         line_height=1.05, font_family="Playfair Display")

add_text(S3, "text-32", "of Ethiopia.", "title",
         x=96, y=212, w=680, h=80, zidx=nextz(),
         color=CLAY, font_size=58, font_weight=400,
         font_style="italic", line_height=1.05,
         font_family="Playfair Display")

# Gold rule under title
add_shape(S3, "shape-33", "rectangle", 96, 312, 60, 2, nextz(), fill=GOLD)

# Intro paragraph
add_text(S3, "text-34",
         "Six origin regions, six distinct sensory languages — each shaped by altitude, soil, varietal, and the hand of its harvester.",
         "paragraph",
         x=96, y=336, w=620, h=60, zidx=nextz(),
         color=CLAY, font_size=15, font_weight=400,
         font_style="italic", line_height=1.6,
         font_family="Playfair Display")

# Two-column flavor index — left column
COL1_X = 96
COL2_X = 416
ROW_Y_START = 432
ROW_GAP = 92

# --- Yirgacheffe ---
add_shape(S3, "shape-35", "circle", COL1_X, ROW_Y_START + 6, 8, 8, nextz(), fill=CHERRY)
add_text(S3, "text-36", "01  YIRGACHEFFE", "caption",
         x=COL1_X + 20, y=ROW_Y_START, w=300, h=20, zidx=nextz(),
         color=ESPRESSO, font_size=11, font_weight=600,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono")
add_text(S3, "text-37", "floral  ·  bergamot  ·  lemon zest", "caption",
         x=COL1_X + 20, y=ROW_Y_START + 24, w=300, h=22, zidx=nextz(),
         color=GREEN, font_size=15, font_weight=400,
         font_style="italic", line_height=1.3,
         font_family="Playfair Display")
add_text(S3, "text-38", "1,800 — 2,200 m", "caption",
         x=COL1_X + 20, y=ROW_Y_START + 50, w=240, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# --- Sidamo ---
y2 = ROW_Y_START + ROW_GAP
add_shape(S3, "shape-39", "circle", COL1_X, y2 + 6, 8, 8, nextz(), fill=CHERRY)
add_text(S3, "text-40", "02  SIDAMO", "caption",
         x=COL1_X + 20, y=y2, w=300, h=20, zidx=nextz(),
         color=ESPRESSO, font_size=11, font_weight=600,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono")
add_text(S3, "text-41", "berry  ·  winey  ·  cocoa nib", "caption",
         x=COL1_X + 20, y=y2 + 24, w=300, h=22, zidx=nextz(),
         color=GREEN, font_size=15, font_weight=400,
         font_style="italic", line_height=1.3,
         font_family="Playfair Display")
add_text(S3, "text-42", "1,550 — 2,200 m", "caption",
         x=COL1_X + 20, y=y2 + 50, w=240, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# --- Guji ---
y3 = ROW_Y_START + 2 * ROW_GAP
add_shape(S3, "shape-43", "circle", COL1_X, y3 + 6, 8, 8, nextz(), fill=CHERRY)
add_text(S3, "text-44", "03  GUJI", "caption",
         x=COL1_X + 20, y=y3, w=300, h=20, zidx=nextz(),
         color=ESPRESSO, font_size=11, font_weight=600,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono")
add_text(S3, "text-45", "stone fruit  ·  jasmine  ·  honey", "caption",
         x=COL1_X + 20, y=y3 + 24, w=300, h=22, zidx=nextz(),
         color=GREEN, font_size=15, font_weight=400,
         font_style="italic", line_height=1.3,
         font_family="Playfair Display")
add_text(S3, "text-46", "1,700 — 2,300 m", "caption",
         x=COL1_X + 20, y=y3 + 50, w=240, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# Right column
# --- Harrar ---
add_shape(S3, "shape-47", "circle", COL2_X, ROW_Y_START + 6, 8, 8, nextz(), fill=CHERRY)
add_text(S3, "text-48", "04  HARRAR", "caption",
         x=COL2_X + 20, y=ROW_Y_START, w=300, h=20, zidx=nextz(),
         color=ESPRESSO, font_size=11, font_weight=600,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono")
add_text(S3, "text-49", "blueberry  ·  spiced  ·  red wine", "caption",
         x=COL2_X + 20, y=ROW_Y_START + 24, w=300, h=22, zidx=nextz(),
         color=GREEN, font_size=15, font_weight=400,
         font_style="italic", line_height=1.3,
         font_family="Playfair Display")
add_text(S3, "text-50", "1,500 — 2,100 m", "caption",
         x=COL2_X + 20, y=ROW_Y_START + 50, w=240, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# --- Limu ---
add_shape(S3, "shape-51", "circle", COL2_X, y2 + 6, 8, 8, nextz(), fill=CHERRY)
add_text(S3, "text-52", "05  LIMU", "caption",
         x=COL2_X + 20, y=y2, w=300, h=20, zidx=nextz(),
         color=ESPRESSO, font_size=11, font_weight=600,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono")
add_text(S3, "text-53", "citrus  ·  caramel  ·  black tea", "caption",
         x=COL2_X + 20, y=y2 + 24, w=300, h=22, zidx=nextz(),
         color=GREEN, font_size=15, font_weight=400,
         font_style="italic", line_height=1.3,
         font_family="Playfair Display")
add_text(S3, "text-54", "1,400 — 2,000 m", "caption",
         x=COL2_X + 20, y=y2 + 50, w=240, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# --- Jimma ---
add_shape(S3, "shape-55", "circle", COL2_X, y3 + 6, 8, 8, nextz(), fill=CHERRY)
add_text(S3, "text-56", "06  JIMMA", "caption",
         x=COL2_X + 20, y=y3, w=300, h=20, zidx=nextz(),
         color=ESPRESSO, font_size=11, font_weight=600,
         letter_spacing=3, text_transform="uppercase",
         font_family="JetBrains Mono")
add_text(S3, "text-57", "earthy  ·  walnut  ·  dark chocolate", "caption",
         x=COL2_X + 20, y=y3 + 24, w=300, h=22, zidx=nextz(),
         color=GREEN, font_size=15, font_weight=400,
         font_style="italic", line_height=1.3,
         font_family="Playfair Display")
add_text(S3, "text-58", "1,400 — 1,900 m", "caption",
         x=COL2_X + 20, y=y3 + 50, w=240, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# =====================================================================
# SLIDE 4 — The Highlands Remember
# =====================================================================
S4 = "slide-4"
init_slide(S4, 3, ESPRESSO)

# Full-bleed panoramic image
add_image(S4, "image-59", IMG_HIGHLAND_PAN, 0, 0, 1280, 720, nextz(), is_background=True)

# Slight overall warm wash
add_shape(S4, "shape-60", "rectangle", 0, 0, 1280, 720, nextz(), fill=ESPRESSO, opacity=0.30)

# Left espresso gradient panel (text legibility)
add_shape(S4, "shape-61", "rectangle", 0, 0, 600, 720, nextz(), fill=ESPRESSO, opacity=0.55)

# Top metadata strip
add_text(S4, "text-62", "FIELD NOTE  /  04 — XV", "caption",
         x=96, y=96, w=300, h=20, zidx=nextz(),
         color=GOLD, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase",
         font_family="JetBrains Mono")

# Vertical accent rule
add_shape(S4, "shape-63", "rectangle", 96, 132, 2, 64, nextz(), fill=GOLD)

# Chapter numeral
add_text(S4, "text-64", "IV.", "title",
         x=96, y=212, w=200, h=80, zidx=nextz(),
         color=AMBER, font_size=56, font_weight=400,
         font_style="italic", font_family="Playfair Display",
         line_height=1.0)

# Stacked serif title
add_text(S4, "text-65", "The Highlands", "title",
         x=96, y=312, w=520, h=80, zidx=nextz(),
         color=CREAM, font_size=60, font_weight=400,
         line_height=1.05, font_family="Playfair Display")

add_text(S4, "text-66", "Remember.", "title",
         x=96, y=380, w=520, h=80, zidx=nextz(),
         color=AMBER, font_size=60, font_weight=400,
         font_style="italic", line_height=1.05,
         font_family="Playfair Display")

# Thin gold rule
add_shape(S4, "shape-67", "rectangle", 96, 484, 60, 2, nextz(), fill=GOLD)

# Pull quote
add_text(S4, "text-68",
         "“Coffee is not simply grown here —\nit is remembered by the land.”",
         "subtitle",
         x=96, y=508, w=520, h=80, zidx=nextz(),
         color=CREAM, font_size=22, font_weight=400,
         font_style="italic", line_height=1.45,
         font_family="Playfair Display")

# Slim narrative
add_text(S4, "text-69",
         "Forests at 2,000 metres exhale fog at dawn. Beneath the eucalyptus, wild Arabica still grows the way it has for centuries — slow, shaded, ancestral.",
         "paragraph",
         x=96, y=600, w=520, h=64, zidx=nextz(),
         color=MIST, font_size=14, font_weight=400,
         line_height=1.65, font_family="Inter")

# Bottom-right coordinate caption
add_shape(S4, "shape-70", "rectangle", 920, 624, 240, 1, nextz(), fill=GOLD, opacity=0.7)

add_text(S4, "text-71", "KAFFA  /  6.32° N  36.18° E", "caption",
         x=920, y=636, w=240, h=18, zidx=nextz(),
         color=CREAM, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono", text_align="right")

add_text(S4, "text-72", "HARVEST  /  OCT — JAN", "caption",
         x=920, y=660, w=240, h=18, zidx=nextz(),
         color=AMBER, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono", text_align="right")

# =====================================================================
# SLIDE 5 — Hands of the Harvest
# =====================================================================
S5 = "slide-5"
init_slide(S5, 4, CREAM)

# Right image (oversized close-up)
add_image(S5, "image-73", IMG_CHERRY_HANDS, 560, 0, 720, 720, nextz())

# Soft warm wash on image for tone matching
add_shape(S5, "shape-74", "rectangle", 560, 0, 720, 720, nextz(), fill=CLAY, opacity=0.10)

# Vertical cherry-red rule between cream + image
add_shape(S5, "shape-75", "rectangle", 540, 96, 2, 528, nextz(), fill=CHERRY, opacity=0.7)

# Mono caption running along image edge (top)
add_text(S5, "text-76", "MACRO  /  PLATE V  /  HARVEST 2024", "caption",
         x=592, y=96, w=400, h=20, zidx=nextz(),
         color=CREAM, font_size=11, font_weight=600,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

# Mono caption (bottom of image edge)
add_text(S5, "text-77", "SELECT-PICKED  ·  RIPE CHERRY  ·  YIRGACHEFFE", "caption",
         x=592, y=672, w=520, h=18, zidx=nextz(),
         color=CREAM, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

# Left content (cream)
# Chapter mark
add_text(S5, "text-78", "V.  /  HUMAN GEOGRAPHY", "caption",
         x=96, y=96, w=400, h=20, zidx=nextz(),
         color=CHERRY, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase",
         font_family="JetBrains Mono")

# Stacked serif title
add_text(S5, "text-79", "Hands", "title",
         x=96, y=144, w=440, h=84, zidx=nextz(),
         color=ESPRESSO, font_size=72, font_weight=400,
         line_height=1.0, font_family="Playfair Display")

add_text(S5, "text-80", "of the", "title",
         x=96, y=224, w=440, h=84, zidx=nextz(),
         color=CLAY, font_size=72, font_weight=400,
         font_style="italic", line_height=1.0,
         font_family="Playfair Display")

add_text(S5, "text-81", "Harvest.", "title",
         x=96, y=304, w=440, h=84, zidx=nextz(),
         color=CHERRY, font_size=72, font_weight=400,
         line_height=1.0, font_family="Playfair Display")

# Pull quote
add_text(S5, "text-82",
         "“Every cherry passes through hands\nthat already know the season.”",
         "subtitle",
         x=96, y=420, w=440, h=72, zidx=nextz(),
         color=CLAY, font_size=20, font_weight=400,
         font_style="italic", line_height=1.4,
         font_family="Playfair Display")

# Three poetic fragments — Touch / Time / Trust
FRAG_X = 96
FRAG_Y = 524
FRAG_GAP = 152

# 01 Touch
add_text(S5, "text-83", "01", "caption",
         x=FRAG_X, y=FRAG_Y, w=40, h=18, zidx=nextz(),
         color=GOLD, font_size=11, font_weight=600,
         letter_spacing=3, font_family="JetBrains Mono")
add_text(S5, "text-84", "Touch.", "heading",
         x=FRAG_X, y=FRAG_Y + 22, w=140, h=36, zidx=nextz(),
         color=ESPRESSO, font_size=22, font_weight=400,
         font_family="Playfair Display")
add_text(S5, "text-85", "skin learns ripeness", "caption",
         x=FRAG_X, y=FRAG_Y + 64, w=140, h=20, zidx=nextz(),
         color=CLAY, font_size=12, font_weight=400,
         font_style="italic", font_family="Playfair Display")

# 02 Time
add_text(S5, "text-86", "02", "caption",
         x=FRAG_X + FRAG_GAP, y=FRAG_Y, w=40, h=18, zidx=nextz(),
         color=GOLD, font_size=11, font_weight=600,
         letter_spacing=3, font_family="JetBrains Mono")
add_text(S5, "text-87", "Time.", "heading",
         x=FRAG_X + FRAG_GAP, y=FRAG_Y + 22, w=140, h=36, zidx=nextz(),
         color=ESPRESSO, font_size=22, font_weight=400,
         font_family="Playfair Display")
add_text(S5, "text-88", "the harvest waits", "caption",
         x=FRAG_X + FRAG_GAP, y=FRAG_Y + 64, w=140, h=20, zidx=nextz(),
         color=CLAY, font_size=12, font_weight=400,
         font_style="italic", font_family="Playfair Display")

# 03 Trust
add_text(S5, "text-89", "03", "caption",
         x=FRAG_X + 2 * FRAG_GAP, y=FRAG_Y, w=40, h=18, zidx=nextz(),
         color=GOLD, font_size=11, font_weight=600,
         letter_spacing=3, font_family="JetBrains Mono")
add_text(S5, "text-90", "Trust.", "heading",
         x=FRAG_X + 2 * FRAG_GAP, y=FRAG_Y + 22, w=140, h=36, zidx=nextz(),
         color=ESPRESSO, font_size=22, font_weight=400,
         font_family="Playfair Display")
add_text(S5, "text-91", "inherited knowing", "caption",
         x=FRAG_X + 2 * FRAG_GAP, y=FRAG_Y + 64, w=140, h=20, zidx=nextz(),
         color=CLAY, font_size=12, font_weight=400,
         font_style="italic", font_family="Playfair Display")

# Bottom signature mono
add_text(S5, "text-92", "FIELD NOTE  /  HANDS  /  CHAPTER V", "caption",
         x=96, y=672, w=440, h=18, zidx=nextz(),
         color=TAUPE, font_size=10, font_weight=500,
         letter_spacing=4, text_transform="uppercase",
         font_family="JetBrains Mono")

# =====================================================================
# Assemble files
# =====================================================================
# Attach textElements into each slide
for s in slides:
    s["textElements"] = text_by_slide[s["id"]]

content = {
    "slides": slides,
    "imageElements": image_elements,
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": table_elements,
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baseLayout = {
    "version": "v1",
    "slides": baseLayout_slides,
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

# Compute element count
total_text = sum(len(s["textElements"]) for s in slides)
element_count = (total_text
                 + len(image_elements)
                 + len(shape_elements)
                 + len(chart_elements)
                 + len(table_elements)
                 + len(icon_elements))

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-origin-ethiopia-batch-1-5-{NOW}",
        "title": "ORIGIN: Ethiopia, the First Cup",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides),
        "elementCount": element_count,
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

OUT = "origin_ethiopia_batch_1_5.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)

print(f"Wrote {OUT}")
print(f"slideCount = {len(slides)}")
print(f"elementCount = {element_count}")
print(f"  text:   {total_text}")
print(f"  image:  {len(image_elements)}")
print(f"  shape:  {len(shape_elements)}")
print(f"  icon:   {len(icon_elements)}")
print(f"  chart:  {len(chart_elements)}")
print(f"  table:  {len(table_elements)}")
print(f"max zIndex = {ZIDX}")
