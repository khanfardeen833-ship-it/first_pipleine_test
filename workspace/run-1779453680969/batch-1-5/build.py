#!/usr/bin/env python3
"""Build slides 1-5 for ORIGIN: Ethiopia's Living Coffee Legacy."""
import json
import time

NOW = int(time.time() * 1000)

# Color palette
HIGHLAND_ESPRESSO = "#2A170F"
ROASTED_CACAO = "#4A2C1A"
CEREMONY_CLAY = "#8B4A2F"
CHERRY_RED = "#A83228"
GOLDEN_CREMA = "#D6A15D"
PARCHMENT = "#F2E7D5"
HIGHLAND_MIST = "#D9D3C4"
YIRGACHEFFE_GREEN = "#4F6F45"
JASMINE_WHITE = "#FFF8EA"
BLUE_HOUR = "#26313A"

# Counter for IDs and zIndex (unified)
COUNTER = 0
def nxt():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None,
              line_height=None, font_family="Space Grotesk",
              text_align="left", letter_spacing=0, font_style="normal",
              text_transform="none"):
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
               fill=CEREMONY_CLAY, stroke=None, stroke_width=0, opacity=1):
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


def pexels(photo_id):
    return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"


# ---------- Containers ----------
slides_content = []
slides_baselayout = []
text_by_slide = {}
image_elements = []
shape_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}


def init_slide(slide_id, order, bg_color="#ffffff"):
    slides_content.append({
        "id": slide_id, "order": order,
        "layoutId": "blank-canvas",
        "backgroundColor": bg_color,
        "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [],
        "chartElements": [], "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = nxt()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = nxt()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl


def add_image(slide_id, src, x, y, w, h, **kwargs):
    n = nxt()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, src, x, y, w, h, n, NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl


# ============================================================
# SLIDE 1 — Birthplace in the Mist
# ============================================================
init_slide("slide-1", 0, bg_color=HIGHLAND_ESPRESSO)

# Full-bleed misty highlands hero photograph
add_image("slide-1",
          pexels(1366630),  # misty mountain landscape
          0, 0, 1280, 720, is_background=True)

# Dark gradient overlay (bottom-left scrim for title legibility)
add_shape("slide-1", "rectangle",
          0, 360, 720, 360,
          fill=HIGHLAND_ESPRESSO, opacity=0.55)

# Subtle full-slide vignette base for cinematic feel
add_shape("slide-1", "rectangle",
          0, 0, 1280, 80,
          fill=HIGHLAND_ESPRESSO, opacity=0.35)

# Mono folio caption upper-right
add_text("slide-1",
         "ORIGIN  /  EAST AFRICAN HIGHLANDS",
         "caption", 880, 56, 360, 24,
         color=JASMINE_WHITE, font_size=12, font_weight=500,
         font_family="Space Grotesk",
         letter_spacing=4, text_transform="uppercase",
         text_align="right")

# Small ornamental rule above title
add_shape("slide-1", "rectangle",
          88, 432, 56, 2,
          fill=GOLDEN_CREMA, opacity=1)

# Section label / kicker above hero title
add_text("slide-1",
         "CHAPTER  I",
         "caption", 160, 424, 280, 20,
         color=GOLDEN_CREMA, font_size=12, font_weight=600,
         letter_spacing=6, text_transform="uppercase")

# Hero serif title
add_text("slide-1",
         "Coffee Began Here.",
         "title", 88, 464, 920, 110,
         color=JASMINE_WHITE, font_size=92, font_weight=400,
         line_height=1.0, letter_spacing=-1)

# Refined sans subtitle below
add_text("slide-1",
         "Ethiopia, the living origin of the world's most beloved ritual.",
         "subtitle", 88, 588, 880, 40,
         color=HIGHLAND_MIST, font_size=22, font_weight=400,
         line_height=1.4, letter_spacing=0.5)

# Bottom-left location coordinate caption
add_text("slide-1",
         "9.1450° N   /   40.4897° E",
         "caption", 88, 660, 320, 20,
         color=GOLDEN_CREMA, font_size=11, font_weight=500,
         letter_spacing=3, text_transform="uppercase")


# ============================================================
# SLIDE 2 — Legend of Kaldi
# ============================================================
init_slide("slide-2", 1, bg_color=PARCHMENT)

# Left 60% cinematic image — herder & cherries scene (using a goat / pastoral photo)
add_image("slide-2",
          pexels(2295744),  # rural pastoral landscape with goats / golden light
          0, 0, 768, 720)

# Dark scrim on lower portion of image for caption legibility
add_shape("slide-2", "rectangle",
          0, 600, 768, 120,
          fill=HIGHLAND_ESPRESSO, opacity=0.55)

# Right parchment panel (full-height)
add_shape("slide-2", "rectangle",
          768, 0, 512, 720,
          fill=PARCHMENT, opacity=1)

# Thin vertical golden rule separating image and panel
add_shape("slide-2", "rectangle",
          768, 0, 1, 720,
          fill=ROASTED_CACAO, opacity=0.35)

# Image caption (bottom-left of photo, mono)
add_text("slide-2",
         "ETHIOPIAN HIGHLANDS  /  IX CENTURY",
         "caption", 48, 656, 480, 20,
         color=JASMINE_WHITE, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase")

# Right panel: kicker
add_text("slide-2",
         "FOLKLORE  /  CHAPTER II",
         "caption", 808, 88, 432, 20,
         color=CHERRY_RED, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase")

# Right panel: small ornamental rule
add_shape("slide-2", "rectangle",
          808, 124, 40, 2,
          fill=CHERRY_RED, opacity=1)

# Right panel: editorial serif headline (two lines)
add_text("slide-2",
         "The Goat Herder's Discovery.",
         "title", 808, 152, 432, 180,
         color=HIGHLAND_ESPRESSO, font_size=46, font_weight=500,
         line_height=1.08, letter_spacing=-0.5)

# Right panel: poetic body paragraph
add_text("slide-2",
         "Long before the first roast, before the first port shipment, a young herder named Kaldi noticed his goats dancing beneath an unfamiliar tree, restless from its bright red fruit.",
         "paragraph", 808, 348, 432, 140,
         color=ROASTED_CACAO, font_size=16, font_weight=400,
         line_height=1.65, letter_spacing=0.2)

# Right panel: oversized italic pull quote
add_text("slide-2",
         "“A restless flock. A red fruit. A world awakened.”",
         "subtitle", 808, 504, 432, 140,
         color=HIGHLAND_ESPRESSO, font_size=24, font_weight=500,
         line_height=1.35, font_style="italic", letter_spacing=0)

# Right panel: attribution caption
add_text("slide-2",
         "ORAL TRADITION  —  KAFFA REGION",
         "caption", 808, 656, 432, 20,
         color=CEREMONY_CLAY, font_size=10, font_weight=500,
         letter_spacing=4, text_transform="uppercase")


# ============================================================
# SLIDE 3 — The Map of Living Origins
# ============================================================
init_slide("slide-3", 2, bg_color=PARCHMENT)

# Map area — dark roasted cacao backdrop suggesting topographic ink map
add_shape("slide-3", "rectangle",
          48, 168, 760, 480,
          fill=ROASTED_CACAO, opacity=1)

# Subtle inner shape suggesting the Ethiopian coffee belt (large oval)
add_shape("slide-3", "circle",
          200, 240, 440, 360,
          fill=YIRGACHEFFE_GREEN, opacity=0.22)

# Smaller central elevation circle
add_shape("slide-3", "circle",
          300, 320, 240, 200,
          fill=GOLDEN_CREMA, opacity=0.12)

# Top-left mono kicker
add_text("slide-3",
         "TERROIR  /  CHAPTER III",
         "caption", 48, 80, 400, 20,
         color=CHERRY_RED, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase")

# Editorial serif title (top-left)
add_text("slide-3",
         "A Country of Microclimates.",
         "title", 48, 108, 1184, 60,
         color=HIGHLAND_ESPRESSO, font_size=48, font_weight=500,
         line_height=1.05, letter_spacing=-0.5)

# 5 origin pin markers (cherry red small circles on the map)
# Sidama
add_shape("slide-3", "circle", 360, 392, 14, 14, fill=CHERRY_RED)
# Yirgacheffe
add_shape("slide-3", "circle", 312, 472, 14, 14, fill=CHERRY_RED)
# Guji
add_shape("slide-3", "circle", 432, 504, 14, 14, fill=CHERRY_RED)
# Harrar
add_shape("slide-3", "circle", 600, 360, 14, 14, fill=CHERRY_RED)
# Limu
add_shape("slide-3", "circle", 240, 360, 14, 14, fill=CHERRY_RED)

# Region cards on the right — five elegant editorial cards
CARD_X = 840
CARD_W = 392
CARDS = [
    ("SIDAMA",        "floral · citrus · bright",        212),
    ("YIRGACHEFFE",   "jasmine · bergamot · tea-like",   268),
    ("GUJI",          "berry · winey · juicy",           324),
    ("HARRAR",        "blueberry · spice · earthy",      380),
    ("LIMU",          "chocolate · soft · balanced",     436),
]
for region, notes, y in CARDS:
    # Thin gold rule on the left edge of each card
    add_shape("slide-3", "rectangle", CARD_X, y + 4, 2, 36, fill=GOLDEN_CREMA)
    # Region name — mono uppercase
    add_text("slide-3", region, "caption",
             CARD_X + 16, y, CARD_W - 16, 20,
             color=HIGHLAND_ESPRESSO, font_size=13, font_weight=700,
             letter_spacing=4, text_transform="uppercase")
    # Flavor notes — refined sans
    add_text("slide-3", notes, "paragraph",
             CARD_X + 16, y + 22, CARD_W - 16, 22,
             color=ROASTED_CACAO, font_size=14, font_weight=400,
             line_height=1.4, letter_spacing=0.3, font_style="italic")

# Right column kicker above cards
add_text("slide-3",
         "FIVE LIVING ORIGINS",
         "caption", CARD_X, 168, CARD_W, 20,
         color=CEREMONY_CLAY, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase")

# Bottom caption strip
add_text("slide-3",
         "Ethiopia's altitude, soil, and ancestral tradition compose one of coffee's most complex terroirs.",
         "paragraph", 48, 668, 1184, 24,
         color=ROASTED_CACAO, font_size=13, font_weight=400,
         line_height=1.4, letter_spacing=0.4, font_style="italic",
         text_align="center")


# ============================================================
# SLIDE 4 — The Highland Hands
# ============================================================
init_slide("slide-4", 3, bg_color=PARCHMENT)

# Left 65% cinematic portrait — hands & coffee cherries
add_image("slide-4",
          pexels(4109743),  # coffee cherries / hands close-up
          0, 0, 832, 720)

# Right cream column background (ensures crisp text area)
add_shape("slide-4", "rectangle",
          832, 0, 448, 720,
          fill=PARCHMENT, opacity=1)

# Thin gold vertical rule at column edge
add_shape("slide-4", "rectangle",
          832, 0, 1, 720,
          fill=GOLDEN_CREMA, opacity=0.4)

# Mono caption beneath image (lower-left over photo)
add_shape("slide-4", "rectangle",
          0, 656, 832, 64,
          fill=HIGHLAND_ESPRESSO, opacity=0.6)

add_text("slide-4",
         "SIDAMA  /  HARVEST SEASON",
         "caption", 48, 676, 480, 20,
         color=JASMINE_WHITE, font_size=11, font_weight=500,
         letter_spacing=4, text_transform="uppercase")

# Right column kicker
add_text("slide-4",
         "PORTRAIT  /  CHAPTER IV",
         "caption", 872, 88, 360, 20,
         color=CHERRY_RED, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase")

# Small ornamental rule
add_shape("slide-4", "rectangle",
          872, 124, 40, 2,
          fill=CHERRY_RED, opacity=1)

# Editorial serif headline (right column)
add_text("slide-4",
         "The Highland Hands.",
         "title", 872, 152, 360, 180,
         color=HIGHLAND_ESPRESSO, font_size=44, font_weight=500,
         line_height=1.08, letter_spacing=-0.5)

# Italic pull quote
add_text("slide-4",
         "“Each cherry is chosen by hand, one at a time, season after season — a quiet inheritance passed between fingers.”",
         "subtitle", 872, 360, 360, 220,
         color=ROASTED_CACAO, font_size=20, font_weight=500,
         line_height=1.45, font_style="italic", letter_spacing=0.2)

# Attribution
add_text("slide-4",
         "—  ALMAZ T., COOPERATIVE MEMBER",
         "caption", 872, 596, 360, 20,
         color=CEREMONY_CLAY, font_size=11, font_weight=600,
         letter_spacing=4, text_transform="uppercase")

# Bottom row: small mono data labels (region · altitude · varietal)
add_text("slide-4",
         "1,900–2,200 M  ·  HEIRLOOM  ·  SHADE-GROWN",
         "caption", 872, 664, 360, 20,
         color=YIRGACHEFFE_GREEN, font_size=10, font_weight=600,
         letter_spacing=3, text_transform="uppercase")


# ============================================================
# SLIDE 5 — Red Cherries, White Mist
# ============================================================
init_slide("slide-5", 4, bg_color=JASMINE_WHITE)

# Three vertical image panels with thin ivory gutters
PANEL_Y = 144
PANEL_H = 440
GUTTER = 16
PANEL_W = (1184 - GUTTER * 2) // 3  # ~ 384

# Panel 1 — cherries on branch
add_image("slide-5",
          pexels(2074122),  # coffee cherries / coffee plant
          48, PANEL_Y, PANEL_W, PANEL_H)

# Panel 2 — basket / harvest
add_image("slide-5",
          pexels(4109945),  # coffee cherries close-up
          48 + PANEL_W + GUTTER, PANEL_Y, PANEL_W, PANEL_H)

# Panel 3 — workers in mist / processing
add_image("slide-5",
          pexels(4109744),  # coffee farm scene
          48 + (PANEL_W + GUTTER) * 2, PANEL_Y, PANEL_W, PANEL_H)

# Top kicker
add_text("slide-5",
         "HARVEST  /  CHAPTER V",
         "caption", 48, 64, 600, 20,
         color=CHERRY_RED, font_size=11, font_weight=600,
         letter_spacing=5, text_transform="uppercase")

# Large serif headline spanning across the top
add_text("slide-5",
         "Red Cherries, White Mist.",
         "title", 48, 88, 1184, 60,
         color=HIGHLAND_ESPRESSO, font_size=52, font_weight=500,
         line_height=1.0, letter_spacing=-0.5)

# Captions under each panel — mono labels
CAP_Y = PANEL_Y + PANEL_H + 16
add_text("slide-5",
         "I.  THE BRANCH",
         "caption", 48, CAP_Y, PANEL_W, 18,
         color=HIGHLAND_ESPRESSO, font_size=11, font_weight=700,
         letter_spacing=4, text_transform="uppercase")
add_text("slide-5",
         "Ripe cherries gathered selectively under the morning sun.",
         "paragraph", 48, CAP_Y + 22, PANEL_W, 40,
         color=ROASTED_CACAO, font_size=13, font_weight=400,
         line_height=1.4, font_style="italic")

add_text("slide-5",
         "II.  THE BASKET",
         "caption", 48 + PANEL_W + GUTTER, CAP_Y, PANEL_W, 18,
         color=HIGHLAND_ESPRESSO, font_size=11, font_weight=700,
         letter_spacing=4, text_transform="uppercase")
add_text("slide-5",
         "Hands move between branches, weighed only by patience.",
         "paragraph", 48 + PANEL_W + GUTTER, CAP_Y + 22, PANEL_W, 40,
         color=ROASTED_CACAO, font_size=13, font_weight=400,
         line_height=1.4, font_style="italic")

add_text("slide-5",
         "III.  THE TERRACE",
         "caption", 48 + (PANEL_W + GUTTER) * 2, CAP_Y, PANEL_W, 18,
         color=HIGHLAND_ESPRESSO, font_size=11, font_weight=700,
         letter_spacing=4, text_transform="uppercase")
add_text("slide-5",
         "Workers ascend through cool mist toward the highland forests.",
         "paragraph", 48 + (PANEL_W + GUTTER) * 2, CAP_Y + 22, PANEL_W, 40,
         color=ROASTED_CACAO, font_size=13, font_weight=400,
         line_height=1.4, font_style="italic")

# Bottom mono footer
add_text("slide-5",
         "BUNA HARVEST  ·  OCTOBER — JANUARY",
         "caption", 48, 692, 1184, 18,
         color=CEREMONY_CLAY, font_size=10, font_weight=600,
         letter_spacing=4, text_transform="uppercase",
         text_align="center")


# ============================================================
# Assemble final JSON
# ============================================================

# Inject text elements into slides
for slide in slides_content:
    sid = slide["id"]
    slide["textElements"] = text_by_slide.get(sid, [])

# Compute element count
element_count = (
    sum(len(s["textElements"]) for s in slides_content)
    + len(image_elements)
    + len(shape_elements)
    + len(icon_elements)
    + len(chart_elements)
    + len(table_elements)
)

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

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-origin-ethiopia-batch1-{NOW}",
        "title": "ORIGIN: Ethiopia's Living Coffee Legacy",
        "description": "From highland forest to ceremonial cup",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": element_count,
        "createdAt": "2026-05-22T00:00:00.000Z",
        "updatedAt": "2026-05-22T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baseLayout_file,
        "changelog": changelog_file
    }
}

OUT = "coffee_ethiopia_batch1.json"
with open(OUT, "w") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {OUT}")
print(f"Slides: {len(slides_content)}")
print(f"Total elements: {element_count}")
print(f"  text: {sum(len(s['textElements']) for s in slides_content)}")
print(f"  images: {len(image_elements)}")
print(f"  shapes: {len(shape_elements)}")
print(f"  icons: {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
print(f"  tables: {len(table_elements)}")
print(f"Last counter (= last zIndex): {COUNTER}")
