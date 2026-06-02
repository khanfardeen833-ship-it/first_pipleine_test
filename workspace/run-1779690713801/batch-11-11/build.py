import json
import time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-11"

# Counter starts at 1500, first call returns 1501
COUNTER = 1500

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------- helpers ----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk",
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


# ---------- palette ----------
BG       = "#0B1020"
PANEL    = "#171C2E"
PANEL2   = "#0F1426"
NAVY     = "#1E3A5F"
CYAN     = "#22D3EE"
GREEN    = "#22C55E"
AMBER    = "#F59E0B"
RED      = "#EF4444"
LAVENDER = "#A78BFA"
WHITE    = "#F8FAFC"
STEEL    = "#94A3B8"
DIM      = "#64748B"


# ---------- registries ----------
text_elements = []
shape_elements = []
changelog_elements = {}


def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements.append(c)
    changelog_elements[tid] = cl
    return tid


def add_shape(shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_elements[sid] = cl
    return sid


# ===================================================================
# SLIDE 11 — "Deploy Small, Recover Fast"
# ===================================================================

# --- background canvas ---
add_shape("rectangle", 0, 0, 1280, 720, fill=BG)

# --- header row ---
# small cyan accent line next to caption
add_shape("rectangle", 48, 56, 4, 20, fill=CYAN)

# eyebrow caption
add_text("11 / 15   ·   DEPLOYMENT DISCIPLINE", "caption",
         64, 56, 420, 20,
         color=STEEL, font_size=12, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)

# right-side release status pill
add_shape("rectangle", 988, 50, 244, 32, fill=PANEL)
add_text("RELEASE v2.4.2  ·  STABLE", "caption",
         1004, 56, 220, 20,
         color=GREEN, font_size=12, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)

# title line 1 (paper white)
add_text("Deploy small.", "title",
         48, 88, 900, 80,
         color=WHITE, font_size=64, font_weight=700, line_height=1.05,
         font_family="IBM Plex Sans")

# title line 2 (signal cyan)
add_text("Recover fast.", "title",
         48, 162, 900, 80,
         color=CYAN, font_size=64, font_weight=700, line_height=1.05,
         font_family="IBM Plex Sans")

# subtitle / dek
add_text("Four disciplines that turn release night into a quiet, reversible non-event.",
         "subtitle", 48, 248, 1100, 32,
         color=STEEL, font_size=20, font_weight=400, line_height=1.4,
         font_family="Inter")

# horizontal divider
add_shape("rectangle", 48, 296, 1184, 1, fill=NAVY)


# ===================================================================
# strategy cards (4 across)
# ===================================================================

CARD_Y = 320
CARD_H = 240
CARD_W = 284

def make_card(x, y, accent_color, index, title, desc, metric, metric_label):
    # card body
    add_shape("rectangle", x, y, CARD_W, CARD_H, fill=PANEL)
    # top accent bar
    add_shape("rectangle", x, y, CARD_W, 3, fill=accent_color)
    # mono index number
    add_text(index, "caption",
             x + 24, y + 24, 60, 18,
             color=accent_color, font_size=12, font_weight=600,
             font_family="JetBrains Mono", letter_spacing=2)
    # card title (heading)
    add_text(title, "heading",
             x + 24, y + 52, CARD_W - 48, 36,
             color=WHITE, font_size=24, font_weight=700, line_height=1.2,
             font_family="IBM Plex Sans")
    # description
    add_text(desc, "paragraph",
             x + 24, y + 96, CARD_W - 48, 90,
             color=STEEL, font_size=14, font_weight=400, line_height=1.5,
             font_family="Inter")
    # metric value (large mono accent)
    add_text(metric, "heading",
             x + 24, y + 188, CARD_W - 48, 28,
             color=accent_color, font_size=20, font_weight=600, line_height=1.2,
             font_family="JetBrains Mono")
    # metric label
    add_text(metric_label, "caption",
             x + 24, y + 218, CARD_W - 48, 14,
             color=DIM, font_size=10, font_weight=600,
             font_family="JetBrains Mono", letter_spacing=2)


make_card(48, CARD_Y, CYAN, "01",
          "Blue-Green",
          "Two identical environments. Switch traffic atomically — zero downtime, instant cutover.",
          "100%  →  0%",
          "INSTANT CUTOVER")

make_card(348, CARD_Y, AMBER, "02",
          "Canary Release",
          "Route traffic gradually. Watch the error budget. Promote only when health stays green.",
          "5  →  50  →  100%",
          "PROGRESSIVE SHIFT")

make_card(648, CARD_Y, LAVENDER, "03",
          "Feature Flags",
          "Decouple deploy from release. Toggle features per user, region, or cohort in real time.",
          "ON   /   OFF",
          "RUNTIME CONTROL")

make_card(948, CARD_Y, RED, "04",
          "Instant Rollback",
          "Treat reverts as a feature. One command returns to the last known-good build.",
          "<  60s",
          "RECOVERY TARGET")


# ===================================================================
# KPI strip
# ===================================================================

KPI_Y = 580
KPI_H = 84

# strip background
add_shape("rectangle", 48, KPI_Y, 1184, KPI_H, fill=PANEL2)

# vertical dividers
add_shape("rectangle", 442, KPI_Y + 22, 1, 40, fill=NAVY)
add_shape("rectangle", 836, KPI_Y + 22, 1, 40, fill=NAVY)

# --- KPI 1: Lead Time ---
add_text("LEAD TIME", "caption",
         72, KPI_Y + 14, 200, 14,
         color=DIM, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)
add_text("< 1 HR", "heading",
         72, KPI_Y + 30, 220, 32,
         color=WHITE, font_size=28, font_weight=700, line_height=1.1,
         font_family="JetBrains Mono")
add_text("commit  →  production", "caption",
         72, KPI_Y + 62, 320, 14,
         color=STEEL, font_size=11, font_weight=400,
         font_family="Inter")

# --- KPI 2: MTTR ---
add_text("MTTR", "caption",
         466, KPI_Y + 14, 200, 14,
         color=DIM, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)
add_text("12 MIN", "heading",
         466, KPI_Y + 30, 220, 32,
         color=GREEN, font_size=28, font_weight=700, line_height=1.1,
         font_family="JetBrains Mono")
add_text("mean time to recover", "caption",
         466, KPI_Y + 62, 320, 14,
         color=STEEL, font_size=11, font_weight=400,
         font_family="Inter")

# --- KPI 3: Change Failure Rate ---
add_text("CHANGE FAILURE RATE", "caption",
         860, KPI_Y + 14, 320, 14,
         color=DIM, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)
add_text("4.2%", "heading",
         860, KPI_Y + 30, 220, 32,
         color=AMBER, font_size=28, font_weight=700, line_height=1.1,
         font_family="JetBrains Mono")
add_text("industry baseline: 16%", "caption",
         860, KPI_Y + 62, 320, 14,
         color=STEEL, font_size=11, font_weight=400,
         font_family="Inter")


# ===================================================================
# footer caption
# ===================================================================

add_text("Shipping is safest when every move is reversible.",
         "caption", 48, 686, 1184, 18,
         color=DIM, font_size=13, font_weight=400, line_height=1.3,
         font_family="Inter", font_style="italic")


# ===================================================================
# build envelope
# ===================================================================

content = {
    "slides": [
        {
            "id": SLIDE_ID,
            "order": 0,
            "layoutId": "blank-canvas",
            "backgroundColor": BG,
            "textElements": text_elements
        }
    ],
    "imageElements": [],
    "shapeElements": shape_elements,
    "chartElements": [],
    "tableElements": [],
    "iconElements": [],
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

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

changelog = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {
            "elements": changelog_elements
        }
    }
}

element_count = (
    len(text_elements) + len(shape_elements)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}-slide11",
        "title": "Engineering Excellence: From Commit to Production",
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
        "content": content,
        "baseLayout": base_layout,
        "changelog": changelog
    }
}

OUTFILE = "slide-11.json"
with open(OUTFILE, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Generated {OUTFILE}")
print(f"  slides: 1 (slide-11)")
print(f"  texts:  {len(text_elements)}")
print(f"  shapes: {len(shape_elements)}")
print(f"  total elements: {element_count}")
print(f"  zIndex / id range: 1501 → {COUNTER}")
print(f"  changelog entries: {len(changelog_elements)}")
