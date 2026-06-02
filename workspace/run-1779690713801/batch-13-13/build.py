import json
import time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-13"

# Counter starts at 1800; first element is 1801
COUNTER = 1800

def next_n():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- builders ----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F8FAFC", font_size=None, font_weight=None, line_height=None,
              align="left", letter_spacing=0, font_family="Space Grotesk"):
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
            "textAlign": align, "lineHeight": lh, "letterSpacing": letter_spacing,
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
               fill="#22D3EE", stroke=None, stroke_width=0, opacity=1):
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
              size=80, color="#22D3EE", opacity=1):
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


# ---------- registries ----------

text_elements_for_slide = []
shape_elements = []
icon_elements = []
image_elements = []
chart_elements = []
table_elements = []

changelog_elements = {}  # keyed by element id

def add_text(*args, **kwargs):
    c, cl = make_text(*args, **kwargs)
    text_elements_for_slide.append(c)
    changelog_elements[c["id"]] = cl

def add_shape(*args, **kwargs):
    c, cl = make_shape(*args, **kwargs)
    shape_elements.append(c)
    changelog_elements[c["id"]] = cl

def add_icon(*args, **kwargs):
    c, cl = make_icon(*args, **kwargs)
    icon_elements.append(c)
    changelog_elements[c["id"]] = cl


# ---------- COLOR PALETTE ----------
OBSIDIAN   = "#0B1020"
GRAPHITE   = "#171C2E"
BLUEPRINT  = "#1E3A5F"
CYAN       = "#22D3EE"
GREEN      = "#22C55E"
AMBER      = "#F59E0B"
RED        = "#EF4444"
LAVENDER   = "#A78BFA"
WHITE      = "#F8FAFC"
STEEL      = "#94A3B8"


# ====================== BUILD SLIDE 13 ======================

# 1. Background full-bleed
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=0, y=0, w=1280, h=720, zidx=n, now=NOW,
          fill=OBSIDIAN, stroke=OBSIDIAN, stroke_width=0)

# 2. Subtle blueprint accent — thin top divider line
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=48, y=40, w=120, h=2, zidx=n, now=NOW,
          fill=CYAN, stroke=CYAN, stroke_width=0, opacity=0.7)

# 3. Caption (chapter label) — top-left
n = next_n()
add_text(f"text-{n}", SLIDE_ID,
         "CHAPTER 13  /  DEPLOYMENT DISCIPLINE",
         "caption",
         x=48, y=56, w=520, h=20, zidx=n, now=NOW,
         color=CYAN, font_size=12, font_weight=600,
         letter_spacing=4, font_family="JetBrains Mono")

# 4. Title — large editorial display
n = next_n()
add_text(f"text-{n}", SLIDE_ID,
         "Deploy Small, Recover Fast",
         "title",
         x=48, y=88, w=900, h=78, zidx=n, now=NOW,
         color=WHITE, font_size=64, font_weight=700,
         line_height=1.05, letter_spacing=-1)

# 5. Subtitle / quote
n = next_n()
add_text(f"text-{n}", SLIDE_ID,
         "Shipping is safest when every move is reversible.",
         "subtitle",
         x=48, y=174, w=900, h=32, zidx=n, now=NOW,
         color=STEEL, font_size=22, font_weight=500,
         line_height=1.3, font_family="Inter")

# ---------------- LEFT COLUMN: Three Strategy Cards ----------------
# left column: x=48, w=560
# right column: x=672, w=560
# cards y range: 232 .. 632  (400px) -> 3 cards 124h with 14px gaps

CARD_X = 48
CARD_W = 560
CARD_H = 124
CARD_GAP = 14
CARD_Y_START = 232

cards = [
    {
        "num": "01",
        "name": "BLUE-GREEN DEPLOYMENT",
        "desc": "Two parallel environments. Switch traffic instantly. Roll back without redeploying.",
        "icon": "Layers",
        "accent": CYAN,
    },
    {
        "num": "02",
        "name": "CANARY RELEASE",
        "desc": "Route 5% → 25% → 100%. Measure health at each step. Promote only when stable.",
        "icon": "Bird",
        "accent": GREEN,
    },
    {
        "num": "03",
        "name": "FEATURE FLAGS",
        "desc": "Decouple deploy from release. Toggle behavior per cohort. Reverse risk in one click.",
        "icon": "ToggleRight",
        "accent": AMBER,
    },
]

for i, card in enumerate(cards):
    cy = CARD_Y_START + i * (CARD_H + CARD_GAP)

    # card background panel
    n = next_n()
    add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
              x=CARD_X, y=cy, w=CARD_W, h=CARD_H, zidx=n, now=NOW,
              fill=GRAPHITE, stroke=GRAPHITE, stroke_width=0, opacity=1)

    # left accent stripe
    n = next_n()
    add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
              x=CARD_X, y=cy, w=4, h=CARD_H, zidx=n, now=NOW,
              fill=card["accent"], stroke=card["accent"], stroke_width=0)

    # card number (mono)
    n = next_n()
    add_text(f"text-{n}", SLIDE_ID, card["num"], "caption",
             x=CARD_X + 24, y=cy + 18, w=60, h=20, zidx=n, now=NOW,
             color=card["accent"], font_size=12, font_weight=600,
             letter_spacing=3, font_family="JetBrains Mono")

    # card name (uppercase strong)
    n = next_n()
    add_text(f"text-{n}", SLIDE_ID, card["name"], "heading",
             x=CARD_X + 24, y=cy + 38, w=420, h=30, zidx=n, now=NOW,
             color=WHITE, font_size=22, font_weight=700,
             letter_spacing=0.5, font_family="Space Grotesk")

    # card description
    n = next_n()
    add_text(f"text-{n}", SLIDE_ID, card["desc"], "paragraph",
             x=CARD_X + 24, y=cy + 72, w=420, h=44, zidx=n, now=NOW,
             color=STEEL, font_size=14, font_weight=400,
             line_height=1.5, font_family="Inter")

    # icon in top-right corner of card
    n = next_n()
    add_icon(f"icon-{n}", SLIDE_ID, card["icon"],
             x=CARD_X + CARD_W - 64, y=cy + 30, zidx=n, now=NOW,
             size=40, color=card["accent"], opacity=0.95)


# ---------------- RIGHT COLUMN: Release Control Panel ----------------
PANEL_X = 672
PANEL_W = 560
PANEL_Y = 232
PANEL_H = 400

# panel background
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=PANEL_X, y=PANEL_Y, w=PANEL_W, h=PANEL_H, zidx=n, now=NOW,
          fill=GRAPHITE, stroke=GRAPHITE, stroke_width=0)

# panel inner accent — thin top header bar
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=PANEL_X, y=PANEL_Y, w=PANEL_W, h=44, zidx=n, now=NOW,
          fill=BLUEPRINT, stroke=BLUEPRINT, stroke_width=0)

# header label
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "RELEASE CONTROL", "caption",
         x=PANEL_X + 20, y=PANEL_Y + 14, w=240, h=18, zidx=n, now=NOW,
         color=CYAN, font_size=12, font_weight=600,
         letter_spacing=4, font_family="JetBrains Mono")

# header status pill — small green dot
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "circle",
          x=PANEL_X + PANEL_W - 120, y=PANEL_Y + 16, w=10, h=10, zidx=n, now=NOW,
          fill=GREEN, stroke=GREEN, stroke_width=0)

n = next_n()
add_text(f"text-{n}", SLIDE_ID, "LIVE", "caption",
         x=PANEL_X + PANEL_W - 100, y=PANEL_Y + 14, w=80, h=18, zidx=n, now=NOW,
         color=GREEN, font_size=11, font_weight=600,
         letter_spacing=3, font_family="JetBrains Mono")

# --- Section 1: Health Checks ---
SEC1_Y = PANEL_Y + 64

n = next_n()
add_text(f"text-{n}", SLIDE_ID, "HEALTH CHECKS", "caption",
         x=PANEL_X + 20, y=SEC1_Y, w=240, h=16, zidx=n, now=NOW,
         color=STEEL, font_size=10, font_weight=600,
         letter_spacing=2, font_family="JetBrains Mono")

# four service status rows
services = [
    ("api-gateway",      "200 OK",   GREEN, "CheckCircle"),
    ("auth-service",     "200 OK",   GREEN, "CheckCircle"),
    ("payments-service", "PROBE",    AMBER, "AlertTriangle"),
    ("orders-service",   "200 OK",   GREEN, "CheckCircle"),
]

for idx, (svc, status, col, icn) in enumerate(services):
    ry = SEC1_Y + 22 + idx * 22

    # tiny status icon
    n = next_n()
    add_icon(f"icon-{n}", SLIDE_ID, icn,
             x=PANEL_X + 20, y=ry, zidx=n, now=NOW,
             size=14, color=col)

    # service name
    n = next_n()
    add_text(f"text-{n}", SLIDE_ID, svc, "caption",
             x=PANEL_X + 42, y=ry, w=240, h=16, zidx=n, now=NOW,
             color=WHITE, font_size=12, font_weight=500,
             font_family="JetBrains Mono")

    # status value
    n = next_n()
    add_text(f"text-{n}", SLIDE_ID, status, "caption",
             x=PANEL_X + PANEL_W - 100, y=ry, w=80, h=16, zidx=n, now=NOW,
             color=col, font_size=11, font_weight=600,
             letter_spacing=1, font_family="JetBrains Mono", align="right")

# divider
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=PANEL_X + 20, y=SEC1_Y + 130, w=PANEL_W - 40, h=1, zidx=n, now=NOW,
          fill=BLUEPRINT, stroke=BLUEPRINT, stroke_width=0, opacity=0.8)

# --- Section 2: Traffic Routing ---
SEC2_Y = SEC1_Y + 144

n = next_n()
add_text(f"text-{n}", SLIDE_ID, "TRAFFIC ROUTING", "caption",
         x=PANEL_X + 20, y=SEC2_Y, w=240, h=16, zidx=n, now=NOW,
         color=STEEL, font_size=10, font_weight=600,
         letter_spacing=2, font_family="JetBrains Mono")

# routing visualization: three segments (blue env, green env, canary)
ROUTE_Y = SEC2_Y + 24
ROUTE_H = 14
ROUTE_X = PANEL_X + 20
ROUTE_W = PANEL_W - 40

# blue segment 75%
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=ROUTE_X, y=ROUTE_Y, w=int(ROUTE_W * 0.75), h=ROUTE_H, zidx=n, now=NOW,
          fill=CYAN, stroke=CYAN, stroke_width=0)
# canary green segment 20%
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=ROUTE_X + int(ROUTE_W * 0.75), y=ROUTE_Y, w=int(ROUTE_W * 0.20), h=ROUTE_H, zidx=n, now=NOW,
          fill=GREEN, stroke=GREEN, stroke_width=0)
# holdout 5% amber
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=ROUTE_X + int(ROUTE_W * 0.95), y=ROUTE_Y, w=int(ROUTE_W * 0.05), h=ROUTE_H, zidx=n, now=NOW,
          fill=AMBER, stroke=AMBER, stroke_width=0)

# routing labels (3 columns under bar)
LB_Y = ROUTE_Y + 22
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "STABLE  75%", "caption",
         x=ROUTE_X, y=LB_Y, w=160, h=16, zidx=n, now=NOW,
         color=CYAN, font_size=11, font_weight=600,
         letter_spacing=1.5, font_family="JetBrains Mono")
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "CANARY  20%", "caption",
         x=ROUTE_X + 180, y=LB_Y, w=160, h=16, zidx=n, now=NOW,
         color=GREEN, font_size=11, font_weight=600,
         letter_spacing=1.5, font_family="JetBrains Mono")
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "HOLDOUT  5%", "caption",
         x=ROUTE_X + 360, y=LB_Y, w=160, h=16, zidx=n, now=NOW,
         color=AMBER, font_size=11, font_weight=600,
         letter_spacing=1.5, font_family="JetBrains Mono")

# divider 2
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=PANEL_X + 20, y=SEC2_Y + 76, w=PANEL_W - 40, h=1, zidx=n, now=NOW,
          fill=BLUEPRINT, stroke=BLUEPRINT, stroke_width=0, opacity=0.8)

# --- Section 3: Error Budget + Rollback Action ---
SEC3_Y = SEC2_Y + 92

# Error budget label
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "ERROR BUDGET", "caption",
         x=PANEL_X + 20, y=SEC3_Y, w=180, h=16, zidx=n, now=NOW,
         color=STEEL, font_size=10, font_weight=600,
         letter_spacing=2, font_family="JetBrains Mono")

# Error budget value
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "92.4%", "heading",
         x=PANEL_X + 20, y=SEC3_Y + 18, w=140, h=34, zidx=n, now=NOW,
         color=WHITE, font_size=28, font_weight=700,
         font_family="JetBrains Mono")

# Error budget bar (background)
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=PANEL_X + 20, y=SEC3_Y + 56, w=240, h=6, zidx=n, now=NOW,
          fill=BLUEPRINT, stroke=BLUEPRINT, stroke_width=0)
# Error budget bar fill 92.4%
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=PANEL_X + 20, y=SEC3_Y + 56, w=int(240 * 0.924), h=6, zidx=n, now=NOW,
          fill=GREEN, stroke=GREEN, stroke_width=0)

# Rollback button
ROLL_X = PANEL_X + PANEL_W - 180
ROLL_Y = SEC3_Y + 14
n = next_n()
add_shape(f"shape-{n}", SLIDE_ID, "rectangle",
          x=ROLL_X, y=ROLL_Y, w=160, h=44, zidx=n, now=NOW,
          fill=AMBER, stroke=AMBER, stroke_width=0)
n = next_n()
add_icon(f"icon-{n}", SLIDE_ID, "RotateCcw",
         x=ROLL_X + 16, y=ROLL_Y + 14, zidx=n, now=NOW,
         size=16, color=OBSIDIAN)
n = next_n()
add_text(f"text-{n}", SLIDE_ID, "ROLLBACK", "caption",
         x=ROLL_X + 38, y=ROLL_Y + 16, w=120, h=18, zidx=n, now=NOW,
         color=OBSIDIAN, font_size=12, font_weight=700,
         letter_spacing=3, font_family="JetBrains Mono")


# ---------------- BOTTOM PRINCIPLES ROW ----------------
PR_Y = 656

n = next_n()
add_text(f"text-{n}", SLIDE_ID, "PRINCIPLES", "caption",
         x=48, y=PR_Y, w=120, h=16, zidx=n, now=NOW,
         color=CYAN, font_size=10, font_weight=600,
         letter_spacing=3, font_family="JetBrains Mono")

# three principle items separated by dots
n = next_n()
add_text(f"text-{n}", SLIDE_ID,
         "Reversible by default   •   Decouple deploy from release   •   Trust signals over assumptions",
         "caption",
         x=170, y=PR_Y, w=1062, h=16, zidx=n, now=NOW,
         color=STEEL, font_size=11, font_weight=500,
         letter_spacing=1.5, font_family="JetBrains Mono")


# ====================== ASSEMBLE FILES ======================

# content
content = {
    "slides": [
        {
            "id": SLIDE_ID,
            "order": 0,
            "layoutId": "blank-canvas",
            "backgroundColor": OBSIDIAN,
            "textElements": text_elements_for_slide
        }
    ],
    "imageElements": image_elements,
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": table_elements,
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

# baseLayout
base_layout = {
    "version": "v1",
    "slides": [
        {
            "id": SLIDE_ID,
            "layoutId": "blank-canvas",
            "imageElements": [],
            "shapeElements": [],
            "chartElements": [],
            "iconElements": [],
            "embedElements": []
        }
    ],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

# changelog
changelog = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {
            "elements": changelog_elements
        }
    }
}

# total element count
total_elements = (
    len(text_elements_for_slide)
    + len(shape_elements)
    + len(icon_elements)
    + len(image_elements)
    + len(chart_elements)
    + len(table_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch13-{NOW}",
        "title": "Engineering Excellence — Slide 13",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
        "elementCount": total_elements,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": base_layout,
        "changelog": changelog
    }
}

OUT = "slide-13.json"
with open(OUT, "w") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {OUT}")
print(f"slideCount: 1")
print(f"elementCount: {total_elements}")
print(f"  text: {len(text_elements_for_slide)}")
print(f"  shape: {len(shape_elements)}")
print(f"  icon: {len(icon_elements)}")
print(f"  image: {len(image_elements)}")
print(f"  chart: {len(chart_elements)}")
print(f"  table: {len(table_elements)}")
print(f"changelog entries: {len(changelog_elements)}")
print(f"final counter: {COUNTER}")
