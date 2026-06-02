import json, time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-6"

COUNTER = 750
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F8FAFC", font_size=None, font_weight=None, line_height=None,
              text_align="left", font_family="Space Grotesk", letter_spacing=0,
              font_style="normal"):
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
               fill="#171C2E", stroke=None, stroke_width=0, opacity=1):
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
              size=80, color="#22D3EE", opacity=1, w=None, h=None):
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


# Storage
text_elements = []
shape_elements = []
icon_elements = []
changelog_elements = {}


def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_id()
    text_id = f"text-{n}"
    c, cl = make_text(text_id, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements.append(c)
    changelog_elements[text_id] = cl
    return text_id


def add_shape(shape_type, x, y, w, h, **kwargs):
    n = next_id()
    shape_id = f"shape-{n}"
    c, cl = make_shape(shape_id, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_elements[shape_id] = cl
    return shape_id


def add_icon(icon_name, x, y, **kwargs):
    n = next_id()
    icon_id = f"icon-{n}"
    c, cl = make_icon(icon_id, SLIDE_ID, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_elements[icon_id] = cl
    return icon_id


# === BACKGROUND ===
add_shape("rectangle", 0, 0, 1280, 720, fill="#0B1020")  # 751

# === TOP HEADER ===
add_text("BEST PRACTICE 06   /   CODE REVIEW", "caption",
         48, 48, 600, 18,
         font_size=12, color="#22D3EE", font_weight=700, letter_spacing=3.5)  # 752

add_text("The Review Ritual", "title",
         48, 70, 1000, 80,
         font_size=64, color="#F8FAFC", font_weight=700, line_height=1.05)  # 753

# Thin accent rule below title
add_shape("rectangle", 48, 150, 96, 2, fill="#22D3EE")  # 754

# === LEFT: PR CARD MOCKUP ===
PR_X, PR_Y, PR_W, PR_H = 48, 168, 664, 416

# Card body
add_shape("rectangle", PR_X, PR_Y, PR_W, PR_H, fill="#171C2E")  # 755
# Header bar
add_shape("rectangle", PR_X, PR_Y, PR_W, 60, fill="#1E2138")  # 756

# PR title
add_text("feat: enable canary guard for prod rollout", "paragraph",
         PR_X + 24, PR_Y + 14, 500, 22,
         font_size=15, color="#F8FAFC", font_weight=600, line_height=1.3)  # 757

# PR meta with arrow
add_text("main ← release/canary-guard   ·   4 files changed   ·   #2841", "caption",
         PR_X + 24, PR_Y + 38, 500, 16,
         font_size=11, color="#94A3B8", font_weight=500, letter_spacing=0.4)  # 758

# Approved badge
add_shape("rectangle", PR_X + 552, PR_Y + 16, 96, 28, fill="#22C55E")  # 759
add_text("APPROVED", "caption",
         PR_X + 552, PR_Y + 22, 96, 18,
         font_size=11, color="#0B1020", font_weight=700,
         text_align="center", letter_spacing=2.5)  # 760

# === DIFF LINES ===
diff_x = PR_X + 16
diff_w = PR_W - 32
diff_h = 32
diff_y = PR_Y + 76  # 244

diffs = [
    ("added",   "+    if (canary.healthy()) {",     "#16331E", "#86EFAC"),
    ("removed", "-    if (deploy.ok()) {",          "#3A1B1F", "#FCA5A5"),
    ("added",   "+      advanceTraffic(0.5);",      "#16331E", "#86EFAC"),
    ("context", "       return promote();",         "#1B2038", "#94A3B8"),
    ("removed", "-      advanceTraffic(1.0);",      "#3A1B1F", "#FCA5A5"),
]

for i, (kind, code, bg, fg) in enumerate(diffs):
    y = diff_y + i * diff_h
    add_shape("rectangle", diff_x, y, diff_w, diff_h, fill=bg)
    add_text(code, "paragraph",
             diff_x + 16, y + 6, diff_w - 32, 22,
             font_size=14, color=fg, font_weight=500, line_height=1.4,
             letter_spacing=0.2)

# === COMMENT BUBBLE ===
COMMENT_Y = diff_y + 5 * diff_h + 12  # 244 + 160 + 12 = 416
COMMENT_H = 152

add_shape("rectangle", diff_x, COMMENT_Y, diff_w, COMMENT_H, fill="#0F1424")
# Lavender accent bar on left edge of comment
add_shape("rectangle", diff_x, COMMENT_Y, 4, COMMENT_H, fill="#A78BFA")

# User icon
add_icon("UserCircle", diff_x + 20, COMMENT_Y + 18, w=32, h=32, color="#A78BFA")

# Author + role
add_text("alex.chen   ·   STAFF ARCHITECT", "caption",
         diff_x + 64, COMMENT_Y + 22, 500, 20,
         font_size=12, color="#F8FAFC", font_weight=600, letter_spacing=1.8)

# Comment body
add_text("Nice safety check. Let's also log the gate decision so we can trace rollback events end-to-end and feed them into the SLO error budget.",
         "paragraph",
         diff_x + 20, COMMENT_Y + 60, 580, 80,
         font_size=14, color="#94A3B8", font_weight=500, line_height=1.55)

# === RIGHT: 3 REVIEW PILLAR CARDS ===
CARD_X, CARD_W, CARD_H = 744, 488, 130
CARD_GAP = 16
CARD_Y_START = 168

cards = [
    {"icon": "Eye",         "icon_color": "#22D3EE",
     "num": "01", "num_color": "#22D3EE",
     "title": "Clarity",
     "desc": "Names and structure should explain themselves before comments do. Read the change as a stranger would."},
    {"icon": "ShieldCheck", "icon_color": "#22C55E",
     "num": "02", "num_color": "#22C55E",
     "title": "Correctness",
     "desc": "Probe edge cases, failure modes, and concurrency. Tests prove what comments only promise."},
    {"icon": "Wrench",      "icon_color": "#A78BFA",
     "num": "03", "num_color": "#A78BFA",
     "title": "Maintainability",
     "desc": "Optimize for the next engineer. Small seams and reversible decisions outlast clever ones."},
]

for i, card in enumerate(cards):
    cy = CARD_Y_START + i * (CARD_H + CARD_GAP)

    # Card background
    add_shape("rectangle", CARD_X, cy, CARD_W, CARD_H, fill="#171C2E")

    # Icon (top-left of card)
    add_icon(card["icon"], CARD_X + 24, cy + 24, w=40, h=40, color=card["icon_color"])

    # Index number (top-right, mono caption)
    add_text(card["num"], "caption",
             CARD_X + CARD_W - 88, cy + 28, 64, 20,
             font_size=14, color=card["num_color"], font_weight=700,
             text_align="right", letter_spacing=2.5)

    # Title (heading-sized)
    add_text(card["title"], "heading",
             CARD_X + 80, cy + 24, 320, 32,
             font_size=22, color="#F8FAFC", font_weight=600, line_height=1.2)

    # Description
    add_text(card["desc"], "paragraph",
             CARD_X + 24, cy + 70, 440, 56,
             font_size=13, color="#94A3B8", font_weight=500, line_height=1.55)

# === BOTTOM: PULL QUOTE ===
add_text("ENGINEERING PRINCIPLE   /   06   /   CODE REVIEW", "caption",
         48, 600, 1184, 16,
         font_size=11, color="#22D3EE", font_weight=700,
         text_align="center", letter_spacing=4.5)

add_text("“Review the idea, not the person.”", "subtitle",
         48, 624, 1184, 44,
         font_size=28, color="#F8FAFC", font_weight=500,
         text_align="center", line_height=1.3, font_style="italic")

# === ASSEMBLE ENVELOPE ===
slide = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": "#0B1020",
    "textElements": text_elements
}

content_file = {
    "slides": [slide],
    "imageElements": [],
    "shapeElements": shape_elements,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baseLayout_file = {
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
        SLIDE_ID: {
            "elements": changelog_elements
        }
    }
}

element_count = (len(text_elements) + len(shape_elements) + len(icon_elements))

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-slide6-{NOW}",
        "title": "Engineering Excellence: From Commit to Production — Slide 6",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
        "elementCount": element_count,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baseLayout_file,
        "changelog": changelog_file
    }
}

with open("slide_6.json", "w", encoding="utf-8") as f:
    json.dump(envelope, f, indent=2, ensure_ascii=False)

print(f"slide_6.json written")
print(f"  slides: 1   elements: {element_count}")
print(f"  texts: {len(text_elements)}   shapes: {len(shape_elements)}   icons: {len(icon_elements)}")
print(f"  counter ended at: {COUNTER}")
print(f"  changelog entries: {len(changelog_elements)}")
