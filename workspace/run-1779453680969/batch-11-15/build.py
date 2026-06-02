import json
import time

NOW = int(time.time() * 1000)

# Counter — IDs and zIndex must start at 600/601 for this batch
COUNTER = 600
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- HELPERS ----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", text_align="left", font_style="normal",
              letter_spacing=0, text_transform="none"):
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
        "shadow": {
            "enabled": False, "angle": 135, "color": "#000000",
            "opacity": 40, "distance": 8, "blur": 12, "size": 0, "spread": 0
        },
        "border": {"type": "none", "width": 4, "color": "#000000", "specialStyle": None},
        "cropRatio": "free",
        "cropRect": {"left": 0, "top": 0, "right": 0, "bottom": 0},
        "focusPoint": {"x": 50, "y": 50},
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


# ---------- COLOR PALETTE ----------
HIGHLAND_ESPRESSO = "#2A170F"
ROASTED_CACAO    = "#4A2C1A"
CEREMONY_CLAY    = "#8B4A2F"
CHERRY_RED       = "#A83228"
GOLDEN_CREMA     = "#D6A15D"
PARCHMENT_CREAM  = "#F2E7D5"
HIGHLAND_MIST    = "#D9D3C4"
YIRGACHEFFE_GREEN= "#4F6F45"
JASMINE_WHITE    = "#FFF8EA"
BLUE_HOUR_SLATE  = "#26313A"

SERIF = "Cormorant Garamond"     # editorial cinematic serif feel
SANS  = "Inter"                  # clean editorial sans
MONO  = "JetBrains Mono"         # mono caption stand-in
SCRIPT= "Caveat"                 # hand-script accent

# ---------- SLIDES ----------
slides_content = []
slides_baselayout = []
text_elements_by_slide = {}
shape_elements = []
image_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}

def init_slide(slide_id, bg):
    slides_content.append({
        "id": slide_id, "order": int(slide_id.split("-")[1]) - 11,
        "layoutId": "blank-canvas",
        "backgroundColor": bg,
        "textElements": []
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
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

def add_image(slide_id, src, x, y, w, h, **kwargs):
    n = next_id()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, src, x, y, w, h, n, NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl


# ============================================================
# SLIDE 11 — HANDS THAT CARRY THE HARVEST
# ============================================================
SLIDE = "slide-11"
init_slide(SLIDE, HIGHLAND_ESPRESSO)

# Hero portrait — left 2/3
add_image(SLIDE,
    "https://images.pexels.com/photos/4913436/pexels-photo-4913436.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 800, 720, is_background=True)

# Dark gradient veil over portrait base for type contrast
add_shape(SLIDE, "rectangle", 0, 480, 800, 240, fill=HIGHLAND_ESPRESSO, opacity=0.55)

# Right column dark panel
add_shape(SLIDE, "rectangle", 800, 0, 480, 720, fill=HIGHLAND_ESPRESSO)

# Three stacked detail frames on right
add_image(SLIDE,
    "https://images.pexels.com/photos/4820818/pexels-photo-4820818.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    832, 32, 416, 200)
add_image(SLIDE,
    "https://images.pexels.com/photos/4820816/pexels-photo-4820816.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    832, 248, 416, 200)
add_image(SLIDE,
    "https://images.pexels.com/photos/2387873/pexels-photo-2387873.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    832, 464, 416, 224)

# Tiny mono caption under each frame (overlaid on its bottom edge)
add_text(SLIDE, "01 — SORTING THE CHERRIES", "caption", 832, 208, 416, 20,
         color=PARCHMENT_CREAM, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "02 — WOVEN BASKETS, HIGHLAND HANDS", "caption", 832, 424, 416, 20,
         color=PARCHMENT_CREAM, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "03 — THE DRYING BEDS AT NOON", "caption", 832, 664, 416, 20,
         color=PARCHMENT_CREAM, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")

# Top-left chapter label
add_text(SLIDE, "CHAPTER 11 — THE PEOPLE", "caption", 48, 48, 320, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase")

# Thin golden rule
add_shape(SLIDE, "rectangle", 48, 80, 56, 1, fill=GOLDEN_CREMA, opacity=0.9)

# Oversized italic pull quote anchored low-left
add_text(SLIDE,
    "“Coffee is not only what we grow.\nIt is how we welcome the world.”",
    "title", 48, 504, 720, 160,
    color=JASMINE_WHITE, font_size=44, font_weight=400, line_height=1.18,
    font_family=SERIF, font_style="italic")

# Subject name + region in mono
add_text(SLIDE, "ALEMITU B. — SIDAMA COOPERATIVE / 1,950 M",
         "caption", 48, 672, 600, 18,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Small frame markers (corner ticks) around hero
add_shape(SLIDE, "rectangle", 48, 96, 24, 1, fill=PARCHMENT_CREAM, opacity=0.6)
add_shape(SLIDE, "rectangle", 48, 96, 1, 24, fill=PARCHMENT_CREAM, opacity=0.6)


# ============================================================
# SLIDE 12 — THE MARKET BEFORE SUNRISE
# ============================================================
SLIDE = "slide-12"
init_slide(SLIDE, BLUE_HOUR_SLATE)

# Full-bleed dawn marketplace
add_image(SLIDE,
    "https://images.pexels.com/photos/2252584/pexels-photo-2252584.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 1280, 720, is_background=True)

# Left dawn-blue gradient veil for atmosphere
add_shape(SLIDE, "rectangle", 0, 0, 760, 720, fill=BLUE_HOUR_SLATE, opacity=0.35)

# Right narrow editorial column — dark scrim
add_shape(SLIDE, "rectangle", 928, 0, 352, 720, fill=HIGHLAND_ESPRESSO, opacity=0.78)

# Top folio
add_text(SLIDE, "12 / 15", "caption", 48, 48, 80, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3)
add_text(SLIDE, "ADDIS — 04:42 AM", "caption", 1088, 48, 192, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3, text_align="right", text_transform="uppercase")

# Lower-left elegant serif title (uppercase)
add_text(SLIDE, "THE MARKET", "title", 48, 432, 720, 96,
         color=JASMINE_WHITE, font_size=88, font_weight=400, line_height=1.0,
         font_family=SERIF, letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "BEFORE", "title", 48, 524, 720, 90,
         color=JASMINE_WHITE, font_size=88, font_weight=400, line_height=1.0,
         font_family=SERIF, font_style="italic", text_transform="uppercase")
add_text(SLIDE, "SUNRISE", "title", 248, 524, 520, 90,
         color=GOLDEN_CREMA, font_size=88, font_weight=400, line_height=1.0,
         font_family=SERIF, letter_spacing=2, text_transform="uppercase")

# Thin ornament rule under title
add_shape(SLIDE, "rectangle", 48, 648, 80, 1, fill=GOLDEN_CREMA)
add_text(SLIDE, "FIELD NOTES — MERCATO DISTRICT", "caption", 144, 642, 360, 16,
         color=PARCHMENT_CREAM, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Right column — section label
add_text(SLIDE, "DAYBREAK ECONOMY", "caption", 960, 80, 280, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase")

add_shape(SLIDE, "rectangle", 960, 108, 40, 1, fill=GOLDEN_CREMA)

add_text(SLIDE,
    "Before the city stirs, the coffee already moves.",
    "subtitle", 960, 132, 280, 84,
    color=JASMINE_WHITE, font_size=22, font_weight=400, line_height=1.35,
    font_family=SERIF, font_style="italic")

add_text(SLIDE,
    "Burlap sacks pass between hands marked by harvest. Chalk numbers ghost across wooden boards. Steam from morning tea threads through the lamp-lit aisles.",
    "paragraph", 960, 232, 280, 220,
    color=HIGHLAND_MIST, font_size=14, font_weight=400, line_height=1.65,
    font_family=SANS)

# Floating data labels on left over imagery (documentary lower-thirds)
# Label 1 — sack weight
add_shape(SLIDE, "rectangle", 80, 200, 220, 56, fill=HIGHLAND_ESPRESSO, opacity=0.82)
add_shape(SLIDE, "rectangle", 80, 200, 4, 56, fill=CHERRY_RED)
add_text(SLIDE, "60 KG", "heading", 96, 208, 200, 28,
         color=JASMINE_WHITE, font_size=22, font_weight=500, font_family=MONO,
         letter_spacing=2)
add_text(SLIDE, "STANDARD COFFEE SACK", "caption", 96, 236, 200, 14,
         color=GOLDEN_CREMA, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Label 2 — ECX
add_shape(SLIDE, "rectangle", 80, 296, 220, 56, fill=HIGHLAND_ESPRESSO, opacity=0.82)
add_shape(SLIDE, "rectangle", 80, 296, 4, 56, fill=CHERRY_RED)
add_text(SLIDE, "ECX FLOOR", "heading", 96, 304, 200, 28,
         color=JASMINE_WHITE, font_size=18, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "ETHIOPIA COMMODITY EXCHANGE", "caption", 96, 332, 200, 14,
         color=GOLDEN_CREMA, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Bottom-right small caption
add_text(SLIDE, "PHOTO — MERCATO, ADDIS ABABA",
         "caption", 928, 696, 336, 16,
         color=HIGHLAND_MIST, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_align="right", text_transform="uppercase")


# ============================================================
# SLIDE 13 — FROM ADDIS TO THE WORLD
# ============================================================
SLIDE = "slide-13"
init_slide(SLIDE, PARCHMENT_CREAM)

# Background subtle parchment tone (already set). Add roasted cacao right panel.
add_shape(SLIDE, "rectangle", 720, 0, 560, 720, fill=ROASTED_CACAO)

# Right side cinematic export image
add_image(SLIDE,
    "https://images.pexels.com/photos/4040646/pexels-photo-4040646.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    720, 0, 560, 720, opacity=0.55)

# Right-side dark veil for legibility
add_shape(SLIDE, "rectangle", 720, 0, 560, 720, fill=ROASTED_CACAO, opacity=0.55)

# Top folio + chapter
add_text(SLIDE, "CHAPTER 13 — EXPORT", "caption", 48, 48, 320, 16,
         color=ROASTED_CACAO, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase")
add_text(SLIDE, "13 / 15", "caption", 1208, 48, 56, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3, text_align="right")

# Left section — map title
add_text(SLIDE, "From Addis", "title", 48, 96, 640, 80,
         color=HIGHLAND_ESPRESSO, font_size=68, font_weight=400, line_height=1.0,
         font_family=SERIF)
add_text(SLIDE, "to the world.", "title", 48, 168, 640, 80,
         color=CHERRY_RED, font_size=68, font_weight=400, line_height=1.0,
         font_family=SERIF, font_style="italic")

# Origin point — Addis Ababa (centered-left)
ADDIS_X, ADDIS_Y = 188, 480
add_shape(SLIDE, "circle", ADDIS_X-8, ADDIS_Y-8, 16, 16, fill=CHERRY_RED)
add_shape(SLIDE, "circle", ADDIS_X-16, ADDIS_Y-16, 32, 32, fill=CHERRY_RED, opacity=0.25)
add_text(SLIDE, "ADDIS ABABA", "caption", ADDIS_X+16, ADDIS_Y-8, 160, 14,
         color=HIGHLAND_ESPRESSO, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "9.03°N · 38.74°E", "caption", ADDIS_X+16, ADDIS_Y+8, 160, 14,
         color=ROASTED_CACAO, font_size=9, font_weight=500, font_family=MONO,
         letter_spacing=1)

# Five destination markers with arc lines (use thin lines)
# We'll simulate arcs with diagonal thin rectangles — destinations placed around addis
destinations = [
    ("LONDON",     "51.50°N · 0.13°W",  120, 312),
    ("NEW YORK",   "40.71°N · 74.01°W",  56, 408),
    ("TOKYO",      "35.68°N · 139.69°E", 612, 304),
    ("DUBAI",      "25.20°N · 55.27°E",  584, 472),
    ("MELBOURNE",  "37.81°S · 144.96°E", 600, 596),
]

import math
for name, coords, dx, dy in destinations:
    # Endpoint marker
    add_shape(SLIDE, "circle", dx-6, dy-6, 12, 12, fill=GOLDEN_CREMA)
    add_shape(SLIDE, "circle", dx-10, dy-10, 20, 20, fill=GOLDEN_CREMA, opacity=0.3)
    # Compute thin connecting line as a rotated narrow rectangle is complex; use a 'line' shape
    # Use shapeType "line" — but bbox geometry is needed. We'll fall back to rectangle along a chord.
    # Instead, draw a series of small dots along path? Simpler: thin rectangle from addis to dest.
    length = math.hypot(dx-ADDIS_X, dy-ADDIS_Y)
    angle = math.degrees(math.atan2(dy-ADDIS_Y, dx-ADDIS_X))
    # We'll position a thin rectangle and use rotation via the shape changelog. Need to update geometry manually.
    # Use the helper but post-mutate rotation in changelog.
    n = next_id()
    sid = f"shape-{n}"
    c = {"id": sid, "slideId": SLIDE, "groupId": None}
    cl = {
        "slideId": SLIDE,
        "position": {"x": ADDIS_X, "y": ADDIS_Y - 1},
        "width": int(length), "height": 1, "rotation": angle,
        "zIndex": n, "opacity": 0.65,
        "shapeType": "rectangle",
        "fill": GOLDEN_CREMA, "stroke": GOLDEN_CREMA, "strokeWidth": 0,
        "updatedAt": NOW
    }
    shape_elements.append(c)
    changelog_slides[SLIDE]["elements"][sid] = cl

    # Destination label
    add_text(SLIDE, name, "caption", dx+12, dy-6, 140, 14,
             color=HIGHLAND_ESPRESSO, font_size=11, font_weight=500, font_family=MONO,
             letter_spacing=2, text_transform="uppercase")
    add_text(SLIDE, coords, "caption", dx+12, dy+10, 160, 12,
             color=ROASTED_CACAO, font_size=9, font_weight=500, font_family=MONO,
             letter_spacing=1)

# Left-bottom thin rule + caption
add_shape(SLIDE, "rectangle", 48, 660, 80, 1, fill=ROASTED_CACAO)
add_text(SLIDE, "ROUTES OF THE 2024 EXPORT SEASON",
         "caption", 144, 654, 540, 16,
         color=ROASTED_CACAO, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Right column — pull quote + stamps
add_text(SLIDE, "EXPORT LEDGER", "caption", 752, 80, 280, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase")
add_shape(SLIDE, "rectangle", 752, 108, 40, 1, fill=GOLDEN_CREMA)

add_text(SLIDE,
    "“The origin travels —\nbut the terroir remains.”",
    "title", 752, 148, 480, 160,
    color=JASMINE_WHITE, font_size=34, font_weight=400, line_height=1.25,
    font_family=SERIF, font_style="italic")

# Stamp-style data cards
add_shape(SLIDE, "rectangle", 752, 360, 220, 56, fill=PARCHMENT_CREAM, opacity=0.92)
add_shape(SLIDE, "rectangle", 752, 360, 4, 56, fill=CHERRY_RED)
add_text(SLIDE, "84+", "heading", 768, 368, 200, 28,
         color=HIGHLAND_ESPRESSO, font_size=22, font_weight=500, font_family=MONO,
         letter_spacing=1)
add_text(SLIDE, "AVG. CUPPING SCORE", "caption", 768, 396, 200, 14,
         color=ROASTED_CACAO, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

add_shape(SLIDE, "rectangle", 992, 360, 240, 56, fill=PARCHMENT_CREAM, opacity=0.92)
add_shape(SLIDE, "rectangle", 992, 360, 4, 56, fill=GOLDEN_CREMA)
add_text(SLIDE, "120+", "heading", 1008, 368, 220, 28,
         color=HIGHLAND_ESPRESSO, font_size=22, font_weight=500, font_family=MONO,
         letter_spacing=1)
add_text(SLIDE, "DESTINATION COUNTRIES", "caption", 1008, 396, 220, 14,
         color=ROASTED_CACAO, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Lucide icon: globe
add_icon(SLIDE, "Globe", 752, 440, size=40, color=GOLDEN_CREMA)
add_text(SLIDE,
    "Ethiopia's coffee crosses oceans, languages, and rituals — every roaster a translator of place.",
    "paragraph", 800, 448, 432, 64,
    color=HIGHLAND_MIST, font_size=14, font_weight=400, line_height=1.55,
    font_family=SANS)

# Lucide icon: stamp/shield-check
add_icon(SLIDE, "BadgeCheck", 752, 540, size=40, color=GOLDEN_CREMA)
add_text(SLIDE,
    "Single-origin lots traceable to washing station, farmer, and altitude.",
    "paragraph", 800, 548, 432, 64,
    color=HIGHLAND_MIST, font_size=14, font_weight=400, line_height=1.55,
    font_family=SANS)

# Bottom credit
add_text(SLIDE, "MAP — HAND-DRAWN STUDY, FIELD JOURNAL VOL. III",
         "caption", 752, 680, 480, 16,
         color=HIGHLAND_MIST, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")


# ============================================================
# SLIDE 14 — THE NEW GUARDIANS OF ORIGIN
# ============================================================
SLIDE = "slide-14"
init_slide(SLIDE, HIGHLAND_ESPRESSO)

# Top chapter rail
add_text(SLIDE, "CHAPTER 14 — THE NEW GUARDIANS",
         "caption", 48, 40, 480, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase")
add_text(SLIDE, "14 / 15", "caption", 1208, 40, 56, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3, text_align="right")

# Section title
add_text(SLIDE, "Keepers of the next harvest.", "title", 48, 72, 1080, 56,
         color=JASMINE_WHITE, font_size=44, font_weight=400, line_height=1.05,
         font_family=SERIF, font_style="italic")

# Thin gold rule under title
add_shape(SLIDE, "rectangle", 48, 144, 60, 1, fill=GOLDEN_CREMA)

# Hero portrait — left
add_image(SLIDE,
    "https://images.pexels.com/photos/4820816/pexels-photo-4820816.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    48, 168, 600, 400)

# Soft frame border for hero (thin gold rule top)
add_shape(SLIDE, "rectangle", 48, 168, 600, 2, fill=GOLDEN_CREMA, opacity=0.7)

# Hero name + role label
add_text(SLIDE, "MERON H.", "subheading", 48, 580, 600, 28,
         color=JASMINE_WHITE, font_size=22, font_weight=500, font_family=SERIF,
         letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "FOUNDER · GUJI WOMEN'S COOPERATIVE",
         "caption", 48, 612, 600, 14,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")
add_text(SLIDE,
    "“We do not export beans. We export the patience of three generations.”",
    "paragraph", 48, 636, 600, 60,
    color=HIGHLAND_MIST, font_size=15, font_weight=400, line_height=1.55,
    font_family=SERIF, font_style="italic")

# Three smaller stacked portraits on the right
add_image(SLIDE,
    "https://images.pexels.com/photos/4820770/pexels-photo-4820770.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    680, 168, 280, 168)
add_image(SLIDE,
    "https://images.pexels.com/photos/4820817/pexels-photo-4820817.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    984, 168, 248, 168)
add_image(SLIDE,
    "https://images.pexels.com/photos/2074130/pexels-photo-2074130.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    680, 360, 552, 168)

# Right portrait labels
add_text(SLIDE, "DAWIT T.", "subheading", 680, 344, 280, 18,
         color=JASMINE_WHITE, font_size=14, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")
add_text(SLIDE, "DAWIT T.", "caption", 680, 344, 280, 16,
         color=JASMINE_WHITE, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=2, text_transform="uppercase")

# (Replacing the duplicate above — keep the cleaner versions)
# Region tags row at bottom
TAG_Y = 644
add_text(SLIDE, "ROAST MASTER · ADDIS",
         "caption", 984, 344, 248, 14,
         color=GOLDEN_CREMA, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")
add_text(SLIDE, "FAMILY FARM · YIRGACHEFFE",
         "caption", 680, 536, 552, 14,
         color=GOLDEN_CREMA, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

# Bottom band — three quote cards
add_shape(SLIDE, "rectangle", 680, 568, 552, 124, fill=ROASTED_CACAO, opacity=0.85)
add_shape(SLIDE, "rectangle", 680, 568, 4, 124, fill=GOLDEN_CREMA)

add_text(SLIDE, "VOICES FROM THE COOPERATIVE",
         "caption", 700, 580, 400, 14,
         color=GOLDEN_CREMA, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=3, text_transform="uppercase")

add_text(SLIDE,
    "“We sort, we taste, we name our coffee — so the world hears Ethiopia, not just the price.”",
    "paragraph", 700, 604, 520, 80,
    color=JASMINE_WHITE, font_size=15, font_weight=400, line_height=1.5,
    font_family=SERIF, font_style="italic")

# Small number badges on left hero (subtle frame number)
add_text(SLIDE, "01", "caption", 48, 168, 40, 14,
         color=GOLDEN_CREMA, font_size=10, font_weight=500, font_family=MONO,
         letter_spacing=2)


# ============================================================
# SLIDE 15 — THE CUP REMEMBERS
# ============================================================
SLIDE = "slide-15"
init_slide(SLIDE, HIGHLAND_ESPRESSO)

# Full-bleed cinematic jebena pour
add_image(SLIDE,
    "https://images.pexels.com/photos/4820817/pexels-photo-4820817.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 1280, 720, is_background=True)

# Deep ceremonial darkening veil — top and bottom
add_shape(SLIDE, "rectangle", 0, 0, 1280, 720, fill=HIGHLAND_ESPRESSO, opacity=0.55)
add_shape(SLIDE, "rectangle", 0, 0, 1280, 200, fill=HIGHLAND_ESPRESSO, opacity=0.45)
add_shape(SLIDE, "rectangle", 0, 520, 1280, 200, fill=HIGHLAND_ESPRESSO, opacity=0.55)

# Top folio
add_text(SLIDE, "FINAL CHAPTER", "caption", 48, 48, 240, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase")
add_text(SLIDE, "15 / 15", "caption", 1208, 48, 56, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=3, text_align="right")

# Centered ornamental rule
add_shape(SLIDE, "rectangle", 600, 248, 80, 1, fill=GOLDEN_CREMA, opacity=0.85)
add_text(SLIDE, "·", "caption", 632, 240, 16, 16,
         color=GOLDEN_CREMA, font_size=14, font_weight=500, font_family=SERIF,
         text_align="center")

# Small label above title
add_text(SLIDE, "ORIGIN — ETHIOPIA", "caption", 48, 272, 1184, 16,
         color=GOLDEN_CREMA, font_size=11, font_weight=500, font_family=MONO,
         letter_spacing=6, text_transform="uppercase", text_align="center")

# Centered cinematic italic serif final line
add_text(SLIDE, "Every cup", "title", 48, 304, 1184, 88,
         color=JASMINE_WHITE, font_size=80, font_weight=400, line_height=1.05,
         font_family=SERIF, font_style="italic", text_align="center")
add_text(SLIDE, "begins in a place.", "title", 48, 392, 1184, 88,
         color=GOLDEN_CREMA, font_size=80, font_weight=400, line_height=1.05,
         font_family=SERIF, font_style="italic", text_align="center")

# Centered closing rule
add_shape(SLIDE, "rectangle", 600, 504, 80, 1, fill=GOLDEN_CREMA, opacity=0.85)

# Footer — small mono
add_text(SLIDE,
    "ETHIOPIA — THE BIRTHPLACE, THE CEREMONY, THE MEMORY.",
    "caption", 48, 656, 1184, 16,
    color=PARCHMENT_CREAM, font_size=11, font_weight=500, font_family=MONO,
    letter_spacing=6, text_transform="uppercase", text_align="center")

# Tiny credit mark
add_text(SLIDE, "ORIGIN · A CINEMATIC FIELD STUDY · MMXXVI",
         "caption", 48, 684, 1184, 14,
         color=HIGHLAND_MIST, font_size=9, font_weight=500, font_family=MONO,
         letter_spacing=4, text_transform="uppercase", text_align="center")


# ============================================================
# WRITE OUTPUT
# ============================================================
# Inject text elements back into slides
for s in slides_content:
    s["textElements"] = text_elements_by_slide[s["id"]]

content = {
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

baselayout = {
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

# count elements
total_elems = (
    sum(len(s["textElements"]) for s in slides_content)
    + len(image_elements) + len(shape_elements) + len(chart_elements)
    + len(table_elements) + len(icon_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-11-15-{NOW}",
        "title": "ORIGIN: Ethiopia's Living Coffee Legacy — Batch 11–15",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": total_elems,
        "createdAt": "2026-01-01T00:00:00.000Z",
        "updatedAt": "2026-01-01T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": baselayout,
        "changelog": changelog
    }
}

out_path = "ethiopia_coffee_batch_11_15.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(deck, f, indent=2, ensure_ascii=False)

print(f"Wrote {out_path}")
print(f"Slides: {len(slides_content)}")
print(f"Elements: {total_elems}")
print(f"  text:   {sum(len(s['textElements']) for s in slides_content)}")
print(f"  shapes: {len(shape_elements)}")
print(f"  images: {len(image_elements)}")
print(f"  icons:  {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
print(f"  tables: {len(table_elements)}")
