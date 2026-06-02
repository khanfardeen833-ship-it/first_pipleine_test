import json, time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-7"

COUNTER = 900
def nxt():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F8FAFC", font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", text_align="left", letter_spacing=0):
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


# ---------- Element collectors ----------
text_elements = []           # for content.slides[0].textElements
shape_elements_content = []  # for content.shapeElements
icon_elements_content = []   # for content.iconElements

changelog_elements = {}      # for changelog.slides[SLIDE_ID].elements

def add_text(text, type_, x, y, w, h, **kwargs):
    n = nxt()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements.append(c)
    changelog_elements[tid] = cl

def add_shape(shape_type, x, y, w, h, **kwargs):
    n = nxt()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements_content.append(c)
    changelog_elements[sid] = cl

def add_icon(icon_name, x, y, **kwargs):
    n = nxt()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, icon_name, x, y, n, NOW, **kwargs)
    icon_elements_content.append(c)
    changelog_elements[iid] = cl


# ============================================================
# SLIDE 7 — The Pipeline That Never Sleeps
# ============================================================
# Background: Obsidian Console base
add_shape("rectangle", 0, 0, 1280, 720, fill="#0B1020", stroke="#0B1020", stroke_width=0)

# Subtle blueprint grid bands (faint horizontal lines using thin rectangles)
add_shape("rectangle", 0, 180, 1280, 1, fill="#1E3A5F", stroke="#1E3A5F", stroke_width=0, opacity=0.35)
add_shape("rectangle", 0, 540, 1280, 1, fill="#1E3A5F", stroke="#1E3A5F", stroke_width=0, opacity=0.35)

# Top accent strip (chapter)
add_shape("rectangle", 96, 64, 40, 2, fill="#22D3EE", stroke="#22D3EE", stroke_width=0)

# Chapter caption
add_text("CHAPTER 04  /  CONTINUOUS DELIVERY",
         "caption", 144, 56, 600, 24,
         color="#22D3EE", font_size=12, font_weight=500, letter_spacing=2.4,
         font_family="JetBrains Mono")

# Top-right status badge background
add_shape("rectangle", 1040, 56, 144, 28, fill="#171C2E", stroke="#22C55E", stroke_width=1, opacity=1)
# Live dot
add_shape("circle", 1056, 66, 8, 8, fill="#22C55E", stroke="#22C55E", stroke_width=0)
add_text("PIPELINE  /  LIVE", "caption", 1072, 60, 112, 20,
         color="#22C55E", font_size=11, font_weight=600, letter_spacing=1.6,
         font_family="JetBrains Mono")

# ---- HERO TITLE ----
add_text("The Pipeline That Never Sleeps",
         "title", 96, 104, 960, 80,
         color="#F8FAFC", font_size=56, font_weight=700, line_height=1.05)

# Subtitle
add_text("Every commit travels a guarded path — built, tested, scanned, packaged, and delivered to production with calm, repeatable precision.",
         "paragraph", 96, 192, 800, 56,
         color="#94A3B8", font_size=18, font_weight=400, line_height=1.45)

# ============================================================
# CI/CD PIPELINE — 6 stages, horizontal
# ============================================================
# Pipeline rail (single thin glowing line connecting stage centers)
# Stages laid out across slide; centers at y=380
STAGES = [
    {"label": "COMMIT",  "desc": "Source of truth",  "icon": "GitCommit",  "color": "#22D3EE", "num": "01"},
    {"label": "BUILD",   "desc": "Compile & assemble","icon": "Hammer",     "color": "#22D3EE", "num": "02"},
    {"label": "TEST",    "desc": "Verify behavior",  "icon": "FlaskConical","color": "#22C55E", "num": "03"},
    {"label": "SCAN",    "desc": "Security gate",    "icon": "ShieldCheck","color": "#F59E0B", "num": "04"},
    {"label": "PACKAGE", "desc": "Versioned artifact","icon": "Package",   "color": "#A78BFA", "num": "05"},
    {"label": "DEPLOY",  "desc": "Production release","icon": "Rocket",    "color": "#22C55E", "num": "06"},
]

# Layout math
NUM_STAGES = 6
PIPELINE_LEFT = 112
PIPELINE_RIGHT = 1168
PIPELINE_W = PIPELINE_RIGHT - PIPELINE_LEFT  # 1056
GAP = PIPELINE_W // (NUM_STAGES - 1)  # ~211
NODE_OUTER = 88   # outer halo diameter
NODE_INNER = 64   # inner filled diameter
PIPELINE_Y = 388  # vertical center of stages

# Connecting rail (under nodes) — thin cyan line
# Draw as a thin rectangle from first to last node center
rail_y = PIPELINE_Y + NODE_OUTER // 2 - 1
add_shape("rectangle",
          PIPELINE_LEFT + NODE_OUTER // 2,
          rail_y,
          PIPELINE_W - NODE_OUTER + 1,
          2,
          fill="#1E3A5F", stroke="#1E3A5F", stroke_width=0, opacity=1)

# A second, brighter pulse rail overlay (shorter, signals direction)
add_shape("rectangle",
          PIPELINE_LEFT + NODE_OUTER // 2,
          rail_y,
          (PIPELINE_W - NODE_OUTER + 1),
          1,
          fill="#22D3EE", stroke="#22D3EE", stroke_width=0, opacity=0.55)

# Place each stage
for i, st in enumerate(STAGES):
    cx = PIPELINE_LEFT + i * GAP + NODE_OUTER // 2  # node center x
    node_x = cx - NODE_OUTER // 2
    node_y = PIPELINE_Y

    # Outer glow ring (ellipse)
    add_shape("circle", node_x, node_y, NODE_OUTER, NODE_OUTER,
              fill=st["color"], stroke=st["color"], stroke_width=0, opacity=0.18)

    # Inner filled circle (graphite panel)
    inner_x = cx - NODE_INNER // 2
    inner_y = node_y + (NODE_OUTER - NODE_INNER) // 2
    add_shape("circle", inner_x, inner_y, NODE_INNER, NODE_INNER,
              fill="#171C2E", stroke=st["color"], stroke_width=2, opacity=1)

    # Icon centered inside inner circle
    icon_size = 32
    add_icon(st["icon"],
             cx - icon_size // 2,
             inner_y + (NODE_INNER - icon_size) // 2,
             size=icon_size, color=st["color"])

    # Stage ordinal number above node (mono, faint)
    add_text(st["num"], "caption",
             cx - 30, node_y - 36, 60, 18,
             color=st["color"], font_size=11, font_weight=600,
             letter_spacing=1.6, font_family="JetBrains Mono",
             text_align="center")

    # Label below node (uppercase mono)
    add_text(st["label"], "caption",
             cx - 80, node_y + NODE_OUTER + 16, 160, 22,
             color="#F8FAFC", font_size=14, font_weight=600,
             letter_spacing=1.8, font_family="JetBrains Mono",
             text_align="center")

    # Description below label (muted steel)
    add_text(st["desc"], "caption",
             cx - 90, node_y + NODE_OUTER + 42, 180, 20,
             color="#94A3B8", font_size=12, font_weight=400,
             letter_spacing=0.2, font_family="Inter",
             text_align="center")

# ============================================================
# Bottom: 3 principles
# ============================================================
PRINCIPLE_Y = 600
PRINCIPLES = [
    {"label": "AUTOMATION",     "desc": "Humans approve. Machines execute.",       "color": "#22D3EE"},
    {"label": "REPEATABILITY",  "desc": "Same inputs, same outputs — every run.",   "color": "#A78BFA"},
    {"label": "FAST FEEDBACK",  "desc": "Failures surface in minutes, not days.",   "color": "#22C55E"},
]
COL_W = 360
COL_GAP = 32
TOTAL_W = COL_W * 3 + COL_GAP * 2
START_X = (1280 - TOTAL_W) // 2  # centered
for i, p in enumerate(PRINCIPLES):
    x = START_X + i * (COL_W + COL_GAP)
    # accent dot
    add_shape("circle", x, PRINCIPLE_Y + 6, 8, 8,
              fill=p["color"], stroke=p["color"], stroke_width=0)
    # label
    add_text(p["label"], "caption",
             x + 20, PRINCIPLE_Y, 200, 20,
             color=p["color"], font_size=12, font_weight=600,
             letter_spacing=2.0, font_family="JetBrains Mono")
    # description
    add_text(p["desc"], "paragraph",
             x, PRINCIPLE_Y + 26, COL_W, 24,
             color="#F8FAFC", font_size=15, font_weight=400, line_height=1.4,
             font_family="Inter")

# Bottom-right slide marker
add_text("07 / 15", "caption",
         1120, 676, 64, 16,
         color="#94A3B8", font_size=11, font_weight=500, letter_spacing=1.6,
         font_family="JetBrains Mono", text_align="right")

# ============================================================
# Assemble JSON
# ============================================================
total_elements = (
    len(text_elements)
    + len(shape_elements_content)
    + len(icon_elements_content)
)

content_file = {
    "slides": [
        {
            "id": SLIDE_ID,
            "order": 0,
            "layoutId": "blank-canvas",
            "backgroundColor": "#0B1020",
            "textElements": text_elements,
        }
    ],
    "imageElements": [],
    "shapeElements": shape_elements_content,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements_content,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": [],
}

base_layout_file = {
    "version": "v1",
    "slides": [
        {
            "id": SLIDE_ID,
            "layoutId": "blank-canvas",
            "imageElements": [],
            "shapeElements": [],
            "chartElements": [],
            "iconElements": [],
            "embedElements": [],
        }
    ],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": [],
}

changelog_file = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {
            "elements": changelog_elements
        }
    }
}

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Engineering Excellence: From Commit to Production",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
        "elementCount": total_elements,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None,
    },
    "files": {
        "content": content_file,
        "baseLayout": base_layout_file,
        "changelog": changelog_file,
    }
}

with open("deck.json", "w") as f:
    json.dump(envelope, f, indent=2)

print(f"OK  slides=1  elements={total_elements}  texts={len(text_elements)}  shapes={len(shape_elements_content)}  icons={len(icon_elements_content)}")
