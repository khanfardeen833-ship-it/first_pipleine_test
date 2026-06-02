import json
import time

NOW = int(time.time() * 1000)

# Color palette
OBSIDIAN = "#080A0F"
GRAPHITE = "#161A22"
NEURAL_BLUE = "#2F6BFF"
QUANTUM_CYAN = "#4DEBFF"
SYNTHETIC_VIOLET = "#7B5CFF"
PLATINUM = "#E8ECF2"
MIST = "#AAB2C0"
SIGNAL_GREEN = "#38F2A0"
WARM_GOLD = "#F4B860"
EDITORIAL_WHITE = "#FAFAF7"
CHARCOAL = "#1c1917"

# Counter starting at 300 (so first element is 301)
COUNTER = 300

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- HELPERS ----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color=PLATINUM, font_size=None, font_weight=None, line_height=None,
              text_align="left", font_family="Space Grotesk", letter_spacing=0,
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
               fill=NEURAL_BLUE, stroke=None, stroke_width=0, opacity=1, rotation=0):
    if stroke is None:
        stroke = fill
    content_record = {
        "id": shape_id, "slideId": slide_id, "groupId": None
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": rotation,
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
              size=80, color=NEURAL_BLUE, opacity=1):
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


# ---------- DECK STATE ----------

slides_content = []
slides_baselayout = []
text_by_slide = {}  # slide_id -> list
image_elements = []
shape_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}  # slide_id -> {"elements": {}}

def init_slide(slide_id, order, bg_color):
    slides_content.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg_color, "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [],
        "chartElements": [], "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid


def add_image(slide_id, src, x, y, w, h, **kwargs):
    n = next_id()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, src, x, y, w, h, n, NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


# ============================================================
# SLIDE 6 — INSIDE THE BLACK BOX
# ============================================================
sid = "slide-6"
init_slide(sid, 0, OBSIDIAN)

# Full-bleed obsidian background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN)

# Subtle vignette panels
add_shape(sid, "rectangle", 0, 0, 1280, 80, fill=GRAPHITE, opacity=0.5)
add_shape(sid, "rectangle", 0, 640, 1280, 80, fill=GRAPHITE, opacity=0.5)

# Top mono caption
add_text(sid, "06  /  ARCHITECTURE", "caption", 96, 32, 400, 24,
         color=MIST, font_size=11, font_family="IBM Plex Mono",
         letter_spacing=4, text_transform="uppercase")

add_text(sid, "MODEL  INTERIOR", "caption", 1080, 32, 200, 24,
         color=MIST, font_size=11, font_family="IBM Plex Mono",
         letter_spacing=4, text_transform="uppercase", text_align="right")

# Section title - top left
add_text(sid, "Inside the", "title", 96, 96, 700, 80,
         color=PLATINUM, font_size=64, font_weight=300,
         font_family="Space Grotesk", line_height=1.0)
add_text(sid, "black box.", "title", 96, 168, 700, 80,
         color=PLATINUM, font_size=64, font_weight=400,
         font_family="Space Grotesk", line_height=1.0,
         font_style="italic")

# Right margin caption
add_text(sid,
         "An architecture rendered\nin five quiet chambers.",
         "caption", 980, 168, 220, 60,
         color=MIST, font_size=12, font_weight=400,
         font_family="IBM Plex Mono", line_height=1.6,
         text_align="right")

# --- The five chambers (horizontal layered diagram) ---
# Center diagram zone: y = 280 to y = 540, x = 96 to 1184
# 5 chambers, each ~200px wide with 16px gaps
chamber_y = 320
chamber_h = 180
chamber_w = 200
gap = 18
start_x = 96 + (1280 - 96 - 96 - (chamber_w*5 + gap*4)) // 2

chambers = [
    ("01", "DATA", "raw signal", QUANTUM_CYAN),
    ("02", "EMBED", "vector form", NEURAL_BLUE),
    ("03", "ATTENTION", "weighted focus", SYNTHETIC_VIOLET),
    ("04", "REASON", "inferred path", SIGNAL_GREEN),
    ("05", "OUTPUT", "expressed meaning", WARM_GOLD),
]

# Connecting line behind chambers
add_shape(sid, "line", start_x + 20, chamber_y + chamber_h//2,
          chamber_w*5 + gap*4 - 40, 1, fill=GRAPHITE, stroke=MIST,
          stroke_width=1, opacity=0.3)

for i, (num, label, sub, accent) in enumerate(chambers):
    cx = start_x + i * (chamber_w + gap)
    # Glass panel
    add_shape(sid, "rectangle", cx, chamber_y, chamber_w, chamber_h,
              fill=GRAPHITE, opacity=0.8)
    # Top accent bar
    add_shape(sid, "rectangle", cx, chamber_y, chamber_w, 2,
              fill=accent, opacity=1)
    # Bottom node dot
    add_shape(sid, "circle", cx + chamber_w//2 - 6, chamber_y + chamber_h - 14, 12, 12,
              fill=accent, opacity=0.9)
    # Inner subtle layer line
    add_shape(sid, "rectangle", cx + 16, chamber_y + 80, chamber_w - 32, 1,
              fill=accent, opacity=0.25)

    # Number
    add_text(sid, num, "caption", cx + 16, chamber_y + 16, 60, 20,
             color=accent, font_size=11, font_family="IBM Plex Mono",
             letter_spacing=2, font_weight=500)
    # Label
    add_text(sid, label, "heading", cx + 16, chamber_y + 44, chamber_w - 32, 32,
             color=PLATINUM, font_size=20, font_weight=500,
             font_family="Space Grotesk", letter_spacing=1)
    # Sub
    add_text(sid, sub, "caption", cx + 16, chamber_y + 110, chamber_w - 32, 20,
             color=MIST, font_size=11, font_family="IBM Plex Mono",
             letter_spacing=1, font_style="italic")

# Pull quote bottom
add_text(sid,
         "“Intelligence is not a single act —\nit is a sequence of quiet decisions.”",
         "subtitle", 96, 580, 880, 80,
         color=PLATINUM, font_size=22, font_weight=300,
         font_family="Space Grotesk", line_height=1.5,
         font_style="italic")

# Footer
add_text(sid, "—  CHAPTER 06", "caption", 1100, 668, 100, 20,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, text_align="right")


# ============================================================
# SLIDE 7 — FROM PREDICTION TO POSSIBILITY
# ============================================================
sid = "slide-7"
init_slide(sid, 1, EDITORIAL_WHITE)

# Background panels
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=EDITORIAL_WHITE)

# Top mono caption
add_text(sid, "07  /  APPLICATION", "caption", 96, 36, 400, 24,
         color="#5a6170", font_size=11, font_family="IBM Plex Mono",
         letter_spacing=4, text_transform="uppercase")

add_text(sid, "FOUR DOMAINS", "caption", 1080, 36, 200, 24,
         color="#5a6170", font_size=11, font_family="IBM Plex Mono",
         letter_spacing=4, text_transform="uppercase", text_align="right")

# Thin divider
add_shape(sid, "rectangle", 96, 76, 1088, 1, fill="#5a6170", opacity=0.25)

# Oversized title
add_text(sid, "From prediction", "title", 96, 110, 1100, 80,
         color="#0c1322", font_size=68, font_weight=300,
         font_family="Space Grotesk", line_height=1.0)
add_text(sid, "to possibility.", "title", 96, 184, 1100, 80,
         color="#0c1322", font_size=68, font_weight=400,
         font_family="Space Grotesk", line_height=1.0,
         font_style="italic")

# Subtitle
add_text(sid,
         "Where intelligence stops describing the world—and begins to shape it.",
         "subtitle", 96, 286, 900, 32,
         color="#5a6170", font_size=18, font_weight=400,
         font_family="Space Grotesk", line_height=1.5)

# Four panels
panel_y = 360
panel_h = 240
panel_w = 248
panel_gap = 24
start_x = 96 + (1088 - (panel_w*4 + panel_gap*3)) // 2

panels = [
    ("Health", "Diagnostic clarity\nfrom millions of scans.", "Heart", NEURAL_BLUE, "01"),
    ("Creativity", "Expression amplified\nbeyond the page.", "Sparkles", SYNTHETIC_VIOLET, "02"),
    ("Climate", "Forecasting Earth\nat planetary scale.", "Globe", SIGNAL_GREEN, "03"),
    ("Productivity", "Quiet leverage in\nevery working hour.", "Zap", WARM_GOLD, "04"),
]

for i, (label, desc, icon, accent, num) in enumerate(panels):
    px = start_x + i * (panel_w + panel_gap)
    # Card background
    add_shape(sid, "rectangle", px, panel_y, panel_w, panel_h,
              fill="#ffffff", opacity=1)
    # Subtle border
    add_shape(sid, "rectangle", px, panel_y, panel_w, 1,
              fill="#0c1322", opacity=0.1)
    add_shape(sid, "rectangle", px, panel_y + panel_h - 1, panel_w, 1,
              fill="#0c1322", opacity=0.1)
    # Top accent dot
    add_shape(sid, "circle", px + 24, panel_y + 24, 8, 8, fill=accent)
    # Number
    add_text(sid, num, "caption", px + 40, panel_y + 22, 60, 16,
             color="#5a6170", font_size=10, font_family="IBM Plex Mono",
             letter_spacing=2)
    # Icon
    add_icon(sid, icon, px + 24, panel_y + 60, size=44, color=accent)
    # Label
    add_text(sid, label, "heading", px + 24, panel_y + 124, panel_w - 48, 36,
             color="#0c1322", font_size=24, font_weight=500,
             font_family="Space Grotesk", letter_spacing=0)
    # Desc
    add_text(sid, desc, "paragraph", px + 24, panel_y + 168, panel_w - 48, 56,
             color="#5a6170", font_size=13, font_weight=400,
             font_family="Space Grotesk", line_height=1.5)

# Bottom closing line
add_text(sid,
         "Intelligence becomes useful only when it gives something back.",
         "caption", 96, 644, 1088, 24,
         color="#0c1322", font_size=14, font_weight=400,
         font_family="Space Grotesk", letter_spacing=1,
         text_align="center", font_style="italic")


# ============================================================
# SLIDE 8 — THE MACHINE BEGINS TO SEE
# ============================================================
sid = "slide-8"
init_slide(sid, 2, OBSIDIAN)

# Full-bleed background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN)

# Cinematic city image — bleed right side
add_image(sid,
          "https://images.pexels.com/photos/2362029/pexels-photo-2362029.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          320, 0, 960, 720,
          opacity=0.85)

# Dark gradient overlay on left for readability
add_shape(sid, "rectangle", 0, 0, 540, 720, fill=OBSIDIAN, opacity=0.85)
add_shape(sid, "rectangle", 540, 0, 200, 720, fill=OBSIDIAN, opacity=0.4)

# Subtle scan lines (decorative)
add_shape(sid, "rectangle", 320, 180, 960, 1, fill=QUANTUM_CYAN, opacity=0.18)
add_shape(sid, "rectangle", 320, 380, 960, 1, fill=QUANTUM_CYAN, opacity=0.12)
add_shape(sid, "rectangle", 320, 560, 960, 1, fill=QUANTUM_CYAN, opacity=0.18)

# AI vision bounding boxes (decorative thin frames)
add_shape(sid, "rectangle", 700, 220, 140, 100, fill=OBSIDIAN, stroke=QUANTUM_CYAN, stroke_width=1, opacity=0.0)
add_shape(sid, "rectangle", 700, 220, 140, 1, fill=QUANTUM_CYAN, opacity=0.7)
add_shape(sid, "rectangle", 700, 320, 140, 1, fill=QUANTUM_CYAN, opacity=0.7)
add_shape(sid, "rectangle", 700, 220, 1, 100, fill=QUANTUM_CYAN, opacity=0.7)
add_shape(sid, "rectangle", 840, 220, 1, 100, fill=QUANTUM_CYAN, opacity=0.7)
# corner ticks
add_shape(sid, "rectangle", 700, 218, 12, 2, fill=QUANTUM_CYAN)
add_shape(sid, "rectangle", 828, 218, 12, 2, fill=QUANTUM_CYAN)

add_shape(sid, "rectangle", 920, 380, 200, 140, fill=OBSIDIAN, stroke=NEURAL_BLUE, stroke_width=1, opacity=0.0)
add_shape(sid, "rectangle", 920, 380, 200, 1, fill=NEURAL_BLUE, opacity=0.6)
add_shape(sid, "rectangle", 920, 520, 200, 1, fill=NEURAL_BLUE, opacity=0.6)
add_shape(sid, "rectangle", 920, 380, 1, 140, fill=NEURAL_BLUE, opacity=0.6)
add_shape(sid, "rectangle", 1120, 380, 1, 140, fill=NEURAL_BLUE, opacity=0.6)

# Tiny labels next to boxes (mono)
add_text(sid, "OBJ • 0.94", "caption", 700, 200, 100, 14,
         color=QUANTUM_CYAN, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=2, font_weight=500)
add_text(sid, "DEPTH • 22m", "caption", 920, 360, 120, 14,
         color=NEURAL_BLUE, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=2, font_weight=500)

# LEFT EDITORIAL CAPTION RAIL
# Vertical thin line
add_shape(sid, "rectangle", 96, 96, 1, 528, fill=PLATINUM, opacity=0.25)

add_text(sid, "08", "caption", 116, 96, 60, 20,
         color=QUANTUM_CYAN, font_size=11, font_family="IBM Plex Mono",
         letter_spacing=3, font_weight=500)

add_text(sid, "FIELD", "caption", 116, 124, 80, 16,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, text_transform="uppercase")
add_text(sid, "Urban / Night", "paragraph", 116, 144, 200, 22,
         color=PLATINUM, font_size=14, font_weight=400,
         font_family="Space Grotesk", line_height=1.4)

add_text(sid, "MODE", "caption", 116, 196, 80, 16,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, text_transform="uppercase")
add_text(sid, "Vision • Active", "paragraph", 116, 216, 200, 22,
         color=PLATINUM, font_size=14, font_weight=400,
         font_family="Space Grotesk", line_height=1.4)

add_text(sid, "SIGNAL", "caption", 116, 268, 80, 16,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, text_transform="uppercase")
add_text(sid, "1,284 objects/s", "paragraph", 116, 288, 200, 22,
         color=PLATINUM, font_size=14, font_weight=400,
         font_family="Space Grotesk", line_height=1.4)

# Editorial body line
add_text(sid,
         "It does not look\nthe way we look.\nIt sees the world\nas geometry.",
         "paragraph", 116, 360, 200, 130,
         color=MIST, font_size=14, font_weight=400,
         font_family="Space Grotesk", line_height=1.6,
         font_style="italic")

# OVERSIZED TITLE — bottom right
add_text(sid, "The machine", "title", 540, 480, 720, 70,
         color=PLATINUM, font_size=56, font_weight=300,
         font_family="Space Grotesk", line_height=1.0,
         text_align="right")
add_text(sid, "begins to see.", "title", 540, 548, 720, 70,
         color=PLATINUM, font_size=56, font_weight=400,
         font_family="Space Grotesk", line_height=1.0,
         font_style="italic", text_align="right")

# Footer
add_text(sid, "VISION  —  CH. 08", "caption", 96, 668, 200, 20,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3)
add_text(sid, "AI, DISTILLED", "caption", 1080, 668, 200, 20,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, text_align="right")


# ============================================================
# SLIDE 9 — LANGUAGE AS ARCHITECTURE
# ============================================================
sid = "slide-9"
init_slide(sid, 3, EDITORIAL_WHITE)

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=EDITORIAL_WHITE)

# RIGHT SIDE — dark architectural panel
add_shape(sid, "rectangle", 640, 0, 640, 720, fill=OBSIDIAN)

# LEFT SIDE — ivory editorial space
# Top label
add_text(sid, "09  /  LANGUAGE", "caption", 96, 36, 300, 24,
         color="#5a6170", font_size=11, font_family="IBM Plex Mono",
         letter_spacing=4, text_transform="uppercase")

# Thin divider
add_shape(sid, "rectangle", 96, 76, 480, 1, fill="#0c1322", opacity=0.2)

# Tiny intro
add_text(sid, "An essay in three sentences.", "caption", 96, 92, 480, 18,
         color="#5a6170", font_size=11, font_family="IBM Plex Mono",
         letter_spacing=2, font_style="italic")

# HERO ITALIC QUOTE
add_text(sid, "“Words",
         "title", 96, 180, 480, 80,
         color="#0c1322", font_size=58, font_weight=300,
         font_family="Space Grotesk", line_height=1.0,
         font_style="italic")

add_text(sid, "are no longer",
         "title", 96, 256, 480, 80,
         color="#0c1322", font_size=42, font_weight=300,
         font_family="Space Grotesk", line_height=1.1)

add_text(sid, "decoration —",
         "title", 96, 308, 480, 80,
         color="#5a6170", font_size=42, font_weight=300,
         font_family="Space Grotesk", line_height=1.1,
         font_style="italic")

add_text(sid, "they are",
         "title", 96, 380, 480, 80,
         color="#0c1322", font_size=42, font_weight=300,
         font_family="Space Grotesk", line_height=1.1)

add_text(sid, "the structure",
         "title", 96, 432, 480, 80,
         color="#0c1322", font_size=58, font_weight=500,
         font_family="Space Grotesk", line_height=1.0)

add_text(sid, "itself.”",
         "title", 96, 506, 480, 80,
         color="#0c1322", font_size=58, font_weight=400,
         font_family="Space Grotesk", line_height=1.0,
         font_style="italic")

# Attribution
add_shape(sid, "rectangle", 96, 612, 24, 1, fill="#0c1322", opacity=0.6)
add_text(sid, "ON LANGUAGE MODELS", "caption", 132, 604, 300, 18,
         color="#5a6170", font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, font_weight=500)
add_text(sid, "Field notes • 2026", "caption", 132, 624, 300, 18,
         color="#5a6170", font_size=10, font_family="IBM Plex Mono",
         letter_spacing=2)

# RIGHT SIDE — luminous lattice (cathedral of language)
# Top mono label
add_text(sid, "—  LATTICE  /  EN  /  v.1", "caption", 680, 36, 400, 24,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, font_weight=400)
add_text(sid, "TOKENS  •  4096", "caption", 1080, 36, 200, 24,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3, text_align="right")

# Build cathedral-like lattice with floating nodes & beams
# Central column
center_x = 960
# Beam structure — vertical beams
for i, ox in enumerate([-180, -90, 0, 90, 180]):
    bx = center_x + ox
    opacity = 0.3 if abs(ox) > 100 else (0.5 if abs(ox) > 0 else 0.7)
    add_shape(sid, "rectangle", bx, 140, 1, 480, fill=NEURAL_BLUE, opacity=opacity)

# Horizontal arches / connectors
for y in [180, 260, 340, 420, 500, 580]:
    add_shape(sid, "rectangle", 760, y, 400, 1, fill=QUANTUM_CYAN, opacity=0.18)

# Diagonal beams (rotated lines as thin rectangles)
add_shape(sid, "rectangle", 780, 145, 360, 1, fill=SYNTHETIC_VIOLET, opacity=0.4, rotation=8)
add_shape(sid, "rectangle", 780, 600, 360, 1, fill=SYNTHETIC_VIOLET, opacity=0.4, rotation=-8)

# Glowing nodes at intersections
node_positions = [
    (780, 180, QUANTUM_CYAN, 8),
    (870, 260, NEURAL_BLUE, 10),
    (960, 180, PLATINUM, 6),
    (1050, 340, SYNTHETIC_VIOLET, 10),
    (1140, 260, QUANTUM_CYAN, 8),
    (780, 420, NEURAL_BLUE, 8),
    (960, 500, WARM_GOLD, 12),
    (1140, 500, NEURAL_BLUE, 8),
    (870, 580, QUANTUM_CYAN, 6),
    (1050, 580, SYNTHETIC_VIOLET, 6),
    (960, 340, PLATINUM, 14),
]
for nx, ny, col, sz in node_positions:
    # outer glow
    add_shape(sid, "circle", nx - sz, ny - sz, sz*2, sz*2, fill=col, opacity=0.25)
    # core
    add_shape(sid, "circle", nx - sz//2, ny - sz//2, sz, sz, fill=col, opacity=1)

# Token labels floating around lattice
add_text(sid, "the", "caption", 760, 154, 60, 14,
         color=MIST, font_size=10, font_family="IBM Plex Mono", letter_spacing=1)
add_text(sid, "machine", "caption", 920, 154, 80, 14,
         color=PLATINUM, font_size=10, font_family="IBM Plex Mono", letter_spacing=1)
add_text(sid, "thinks", "caption", 1100, 234, 80, 14,
         color=QUANTUM_CYAN, font_size=10, font_family="IBM Plex Mono", letter_spacing=1)
add_text(sid, "in", "caption", 740, 394, 40, 14,
         color=MIST, font_size=10, font_family="IBM Plex Mono", letter_spacing=1)
add_text(sid, "structure", "caption", 920, 478, 100, 14,
         color=WARM_GOLD, font_size=10, font_family="IBM Plex Mono", letter_spacing=1)
add_text(sid, "not in", "caption", 800, 558, 80, 14,
         color=MIST, font_size=10, font_family="IBM Plex Mono", letter_spacing=1, font_style="italic")
add_text(sid, "sentences.", "caption", 1040, 558, 120, 14,
         color=PLATINUM, font_size=10, font_family="IBM Plex Mono", letter_spacing=1)

# Bottom mono caption (right)
add_text(sid, "FIG. 09  —  language as architecture", "caption", 680, 668, 600, 18,
         color=MIST, font_size=10, font_family="IBM Plex Mono",
         letter_spacing=3)


# ============================================================
# SLIDE 10 — THE NEW CREATIVE PARTNER
# ============================================================
sid = "slide-10"
init_slide(sid, 4, GRAPHITE)

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=GRAPHITE)

# Top mono caption
add_text(sid, "10  /  COLLABORATION", "caption", 96, 36, 400, 24,
         color=MIST, font_size=11, font_family="IBM Plex Mono",
         letter_spacing=4, text_transform="uppercase")

add_text(sid, "STUDIO  •  HUMAN  ×  AI", "caption", 1080, 36, 200, 24,
         color=MIST, font_size=11, font_family="IBM Plex Mono",
         letter_spacing=3, text_transform="uppercase", text_align="right")

# Editorial divider
add_shape(sid, "rectangle", 96, 76, 1088, 1, fill=PLATINUM, opacity=0.2)

# BOLD EDITORIAL HEADLINE
add_text(sid, "The new creative", "title", 96, 112, 1100, 80,
         color=PLATINUM, font_size=68, font_weight=300,
         font_family="Space Grotesk", line_height=1.0)
add_text(sid, "partner.", "title", 96, 184, 1100, 80,
         color=PLATINUM, font_size=68, font_weight=400,
         font_family="Space Grotesk", line_height=1.0,
         font_style="italic")

# Subtitle
add_text(sid,
         "Three studios, three disciplines, one quiet collaborator at every desk.",
         "subtitle", 96, 286, 900, 32,
         color=MIST, font_size=18, font_weight=400,
         font_family="Space Grotesk", line_height=1.5,
         font_style="italic")

# THREE PANELS — Magazine-style
panel_y = 354
panel_h = 280
panel_w = 352
panel_gap = 16
total_w = panel_w*3 + panel_gap*2
start_x = 96 + (1088 - total_w) // 2

panels_10 = [
    ("01", "Artist", "Brushstroke meets\nlatent space.",
     "Sketches, color tests, mood frames—\nconjured at the speed of thought.",
     "https://images.pexels.com/photos/8761744/pexels-photo-8761744.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
     SYNTHETIC_VIOLET, "Palette"),
    ("02", "Engineer", "Code as\nco-authorship.",
     "Functions drafted, edge cases revealed,\nrefactors completed in silence.",
     "https://images.pexels.com/photos/4974915/pexels-photo-4974915.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
     QUANTUM_CYAN, "Code"),
    ("03", "Strategist", "A quiet voice\nin the room.",
     "Frameworks tested, narratives shaped,\ndecisions sharpened at every turn.",
     "https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
     WARM_GOLD, "Compass"),
]

for i, (num, role, head, desc, img, accent, icon) in enumerate(panels_10):
    px = start_x + i * (panel_w + panel_gap)
    # Image (top portion)
    add_image(sid, img, px, panel_y, panel_w, 160, opacity=0.7)
    # Dark overlay on image bottom for accent strip
    add_shape(sid, "rectangle", px, panel_y + 158, panel_w, 2, fill=accent, opacity=1)
    # Content card below image
    add_shape(sid, "rectangle", px, panel_y + 160, panel_w, 120,
              fill=OBSIDIAN, opacity=1)
    # Inner subtle border
    add_shape(sid, "rectangle", px, panel_y + 160, 1, 120, fill=accent, opacity=0.4)

    # Number on image (top-left)
    add_shape(sid, "rectangle", px + 16, panel_y + 16, 40, 22, fill=OBSIDIAN, opacity=0.85)
    add_text(sid, num, "caption", px + 22, panel_y + 19, 30, 18,
             color=accent, font_size=11, font_family="IBM Plex Mono",
             letter_spacing=2, font_weight=500)

    # Role label
    add_text(sid, role.upper(), "caption", px + 24, panel_y + 178, 200, 18,
             color=accent, font_size=11, font_family="IBM Plex Mono",
             letter_spacing=3, font_weight=500)

    # Headline
    add_text(sid, head, "heading", px + 24, panel_y + 200, panel_w - 48, 50,
             color=PLATINUM, font_size=20, font_weight=400,
             font_family="Space Grotesk", line_height=1.2)

    # Description
    add_text(sid, desc, "paragraph", px + 24, panel_y + 250, panel_w - 48, 28,
             color=MIST, font_size=11, font_weight=400,
             font_family="IBM Plex Mono", line_height=1.6)

# Closing line at bottom
add_text(sid,
         "—  The hand and the model, both holding the pencil.",
         "caption", 96, 668, 1088, 24,
         color=PLATINUM, font_size=13, font_weight=400,
         font_family="Space Grotesk", letter_spacing=1,
         text_align="center", font_style="italic")


# ============================================================
# ASSEMBLE FINAL JSON
# ============================================================

# Attach text elements to their slides
for slide in slides_content:
    slide["textElements"] = text_by_slide[slide["id"]]

# Count elements
total_text = sum(len(text_by_slide[s["id"]]) for s in slides_content)
total_elements = (total_text + len(image_elements) + len(shape_elements) +
                  len(icon_elements) + len(chart_elements) + len(table_elements))

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
        "_id": f"deck-batch-6-10-{NOW}",
        "title": "AI, Distilled — Slides 6-10",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": total_elements,
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

OUT = "ai_distilled_slides_6_10.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deck, f, indent=2, ensure_ascii=False)

print(f"Wrote {OUT}")
print(f"Slides: {len(slides_content)}")
print(f"Total elements: {total_elements}")
print(f"  text:   {total_text}")
print(f"  shape:  {len(shape_elements)}")
print(f"  image:  {len(image_elements)}")
print(f"  icon:   {len(icon_elements)}")
print(f"Final element ID counter: {COUNTER}")
