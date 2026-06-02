import json, time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-8"
COUNTER = 1050

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------------- helpers ----------------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk"):
    DEFAULTS = {
        "title":      (60, 700, 1.05),
        "subtitle":   (40, 600, 1.35),
        "heading":    (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph":  (22, 700, 1.50),
        "caption":    (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None: fs = font_size
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


# ---------------- registries ----------------
text_elements = []
shape_elements = []
icon_elements = []
chart_elements = []
table_elements = []
image_elements = []
changelog_elements = {}


def add_text(text, type_, x, y, w, h, **kw):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kw)
    text_elements.append(c)
    changelog_elements[tid] = cl


def add_shape(shape_type, x, y, w, h, **kw):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kw)
    shape_elements.append(c)
    changelog_elements[sid] = cl


def add_icon(icon_name, x, y, **kw):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, icon_name, x, y, n, NOW, **kw)
    icon_elements.append(c)
    changelog_elements[iid] = cl


# ---------------- palette ----------------
OBSIDIAN  = "#0B1020"
GRAPHITE  = "#171C2E"
NAVY      = "#1E3A5F"
CYAN      = "#22D3EE"
GREEN     = "#22C55E"
AMBER     = "#F59E0B"
RED       = "#EF4444"
LAVENDER  = "#A78BFA"
PAPER     = "#F8FAFC"
STEEL     = "#94A3B8"

MONO = "JetBrains Mono"
SANS = "Space Grotesk"


# ---------------- 1. background ----------------
add_shape("rectangle", 0, 0, 1280, 720, fill=OBSIDIAN)

# subtle blueprint horizon line near the pipeline
add_shape("rectangle", 0, 280, 1280, 1, fill=NAVY, opacity=0.55)
add_shape("rectangle", 0, 472, 1280, 1, fill=NAVY, opacity=0.55)


# ---------------- 2. header block ----------------
# kicker
add_text("CI/CD  ·  OPERATIONAL FLOW", "caption",
         x=64, y=72, w=600, h=20,
         color=CYAN, font_size=12, font_weight=600,
         letter_spacing=4, font_family=MONO)

# title
add_text("The Pipeline as a Living System", "title",
         x=64, y=104, w=1152, h=72,
         color=PAPER, font_size=54, font_weight=700, line_height=1.1,
         font_family=SANS)

# thin accent rule under title
add_shape("rectangle", 64, 188, 56, 3, fill=CYAN)

# lead paragraph
add_text(
    "Every commit travels the same illuminated path — built, tested, scanned, packaged, deployed, verified.",
    "paragraph",
    x=64, y=204, w=1100, h=28,
    color=STEEL, font_size=18, font_weight=400, line_height=1.4,
    font_family=SANS
)


# ---------------- 3. pipeline track ----------------
TRACK_Y = 326
NODE_CY = 328
NODE_R = 96  # diameter
HALF = NODE_R // 2

# stage center x positions
centers = [144, 352, 560, 768, 976, 1184]

# track base (navy)
add_shape("rectangle", centers[0], TRACK_Y, centers[-1] - centers[0], 4,
          fill=NAVY, opacity=0.9)
# cyan accent track (slightly thinner, on top)
add_shape("rectangle", centers[0], TRACK_Y + 1, centers[-1] - centers[0], 2,
          fill=CYAN, opacity=0.55)


# ---------------- 4. stage nodes ----------------
stages = [
    ("01", "Hammer",       "BUILD",    "compile  ·  lint"),
    ("02", "FlaskConical", "TEST",     "unit  ·  integration"),
    ("03", "ShieldCheck",  "SCAN",     "sca  ·  sast"),
    ("04", "Package",      "PACKAGE",  "image  ·  sbom"),
    ("05", "Rocket",       "DEPLOY",   "canary  ·  prod"),
    ("06", "Activity",     "VERIFY",   "metrics  ·  slo"),
]

for i, (num, icon_name, name, desc) in enumerate(stages):
    cx = centers[i]
    node_x = cx - HALF
    node_y = NODE_CY - HALF

    # outer ring (cyan glow)
    add_shape("circle", node_x - 6, node_y - 6, NODE_R + 12, NODE_R + 12,
              fill=CYAN, opacity=0.10)

    # node face
    add_shape("circle", node_x, node_y, NODE_R, NODE_R,
              fill=GRAPHITE, stroke=CYAN, stroke_width=2)

    # icon centered (48x48)
    add_icon(icon_name, cx - 24, NODE_CY - 24, size=48, color=CYAN)

    # number above
    add_text(num, "caption",
             x=cx - 40, y=246, w=80, h=18,
             color=STEEL, font_size=12, font_weight=500,
             letter_spacing=3, font_family=MONO, text_align="center")

    # name below node
    add_text(name, "subheading",
             x=cx - 100, y=440, w=200, h=28,
             color=PAPER, font_size=18, font_weight=600,
             letter_spacing=4, font_family=MONO, text_align="center")

    # description under name
    add_text(desc, "caption",
             x=cx - 110, y=470, w=220, h=18,
             color=STEEL, font_size=12, font_weight=400,
             letter_spacing=2, font_family=MONO, text_align="center")


# ---------------- 5. dashboard cards ----------------
CARD_Y = 510
CARD_H = 140
CARD_W = 352
card_x_positions = [64, 464, 864]

cards = [
    ("BUILD TIME",        "4m 12s",   "v 22% vs last week",     GREEN),
    ("FAILURE RATE",      "2.1%",     "18 of 842 builds",       AMBER),
    ("DEPLOY FREQUENCY",  "38 / day", "12 services tracked",    CYAN),
]

for (label, value, note, note_color), x in zip(cards, card_x_positions):
    # card background
    add_shape("rectangle", x, CARD_Y, CARD_W, CARD_H, fill=GRAPHITE)
    # left accent strip
    add_shape("rectangle", x, CARD_Y, 3, CARD_H, fill=note_color, opacity=0.85)

    # label
    add_text(label, "caption",
             x=x + 24, y=CARD_Y + 20, w=CARD_W - 48, h=16,
             color=STEEL, font_size=11, font_weight=600,
             letter_spacing=3, font_family=MONO)

    # value
    add_text(value, "heading",
             x=x + 24, y=CARD_Y + 44, w=CARD_W - 48, h=60,
             color=PAPER, font_size=44, font_weight=700, line_height=1.05,
             font_family=SANS)

    # note
    add_text(note, "caption",
             x=x + 24, y=CARD_Y + 108, w=CARD_W - 48, h=18,
             color=note_color, font_size=12, font_weight=500,
             letter_spacing=1, font_family=MONO)


# ---------------- 6. footer ----------------
add_text(
    "PIPELINES ARE NOT JUST AUTOMATION — THEY ARE THE HEARTBEAT OF ENGINEERING QUALITY.",
    "caption",
    x=64, y=676, w=1152, h=18,
    color=STEEL, font_size=11, font_weight=500,
    letter_spacing=3, font_family=MONO, text_align="center"
)


# ---------------- assemble files ----------------
slide = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": OBSIDIAN,
    "textElements": text_elements
}

content = {
    "slides": [slide],
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

changelog = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {"elements": changelog_elements}
    }
}

element_count = (
    len(text_elements) + len(shape_elements) + len(icon_elements)
    + len(image_elements) + len(chart_elements) + len(table_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Engineering Excellence: From Commit to Production",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
        "elementCount": element_count,
        "createdAt": "2026-01-01T00:00:00.000Z",
        "updatedAt": "2026-01-01T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": base_layout,
        "changelog": changelog
    }
}

OUT = "slide_8.json"
with open(OUT, "w") as f:
    json.dump(deck, f, indent=2)

print(f"wrote {OUT}")
print(f"slides: 1 (slide-8)")
print(f"elements: {element_count}")
print(f"  text:  {len(text_elements)}")
print(f"  shape: {len(shape_elements)}")
print(f"  icon:  {len(icon_elements)}")
print(f"final counter: {COUNTER}")
