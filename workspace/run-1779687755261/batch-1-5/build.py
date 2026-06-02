import json
import time

NOW = int(time.time() * 1000)

# Palette
OBSIDIAN     = "#080A0F"
GRAPHITE     = "#161A22"
NEURAL_BLUE  = "#2F6BFF"
QUANTUM_CYAN = "#4DEBFF"
VIOLET       = "#7B5CFF"
PLATINUM     = "#E8ECF2"
MIST         = "#AAB2C0"
SIGNAL_GREEN = "#38F2A0"
WARM_AMBER   = "#F4B860"
EDITORIAL    = "#FAFAF7"
INK          = "#1c1917"

# Counters
COUNTER = 0
def next_n():
    global COUNTER
    COUNTER += 1
    return COUNTER

ZIDX = 0
def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX


# --------- Helpers ---------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color=PLATINUM, font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", text_align="left",
              letter_spacing=0, font_style="normal", text_transform="none"):
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
    content_record = {"id": shape_id, "slideId": slide_id, "groupId": None}
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


def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=64, color=QUANTUM_CYAN, opacity=1):
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


# ---------- Storage ----------
slides = []
baseLayout_slides = []
text_by_slide = {}  # slide_id -> list of content records
shape_elements = []
image_elements = []
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
        "imageElements": [], "shapeElements": [],
        "chartElements": [], "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_n()
    tid = f"text-{n}"
    z = nextz()
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, z, NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_n()
    sid = f"shape-{n}"
    z = nextz()
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, z, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_n()
    iid = f"icon-{n}"
    z = nextz()
    c, cl = make_icon(iid, slide_id, icon_name, x, y, z, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl


# =============================================================================
# SLIDE 1 — The Quiet Arrival
# =============================================================================
S1 = "slide-1"
init_slide(S1, 0, OBSIDIAN)

# Diagonal neural thread (a thin rotated line/rectangle)
add_shape(S1, "rectangle", 120, 360, 1100, 1, fill=NEURAL_BLUE, opacity=0.55, rotation=-22)

# Subtle accent glow (soft circle behind title area)
add_shape(S1, "circle", -120, 380, 520, 520, fill=VIOLET, opacity=0.08)
add_shape(S1, "circle", 880, 80, 360, 360, fill=NEURAL_BLUE, opacity=0.10)

# Particle dots scattered along the thread (cinematic dust)
particles = [
    (200, 470, 6), (320, 432, 4), (430, 392, 8),
    (560, 348, 5), (680, 308, 6), (800, 264, 4),
    (910, 224, 7), (1040, 180, 5), (1140, 140, 4),
    (260, 500, 3), (490, 420, 3), (760, 290, 3),
]
for (px, py, ps) in particles:
    add_shape(S1, "circle", px, py, ps, ps, fill=QUANTUM_CYAN, opacity=0.85)

# A tiny accent dot in champagne (warm intelligence) — mid-thread
add_shape(S1, "circle", 600, 332, 10, 10, fill=WARM_AMBER, opacity=0.95)

# Top-left tiny brand mark
add_shape(S1, "rectangle", 96, 64, 28, 2, fill=PLATINUM, opacity=0.85)
add_text(S1, "AI · DISTILLED", "caption",
         x=132, y=56, w=300, h=22,
         color=MIST, font_size=11, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Top-right slide indicator
add_text(S1, "01 / 15", "caption",
         x=1080, y=56, w=120, h=22,
         color=MIST, font_size=11, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_align="right", text_transform="uppercase")

# Eyebrow above hero title
add_text(S1, "A MINIMAL TEST PRESENTATION ABOUT AI", "caption",
         x=96, y=470, w=600, h=20,
         color=QUANTUM_CYAN, font_size=12, font_weight=500, letter_spacing=6,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Hero title — bottom-left
add_text(S1, "The Quiet Arrival.", "title",
         x=96, y=500, w=1000, h=110,
         color=PLATINUM, font_size=96, font_weight=400, line_height=1.0,
         letter_spacing=-2)

# Subtitle / supporting italic line
add_text(S1, "Intelligence, settling into the room.", "subtitle",
         x=96, y=620, w=900, h=40,
         color=MIST, font_size=24, font_weight=400, font_style="italic",
         line_height=1.3)

# Bottom-right meta
add_text(S1, "VOL. I  ·  ACT ONE", "caption",
         x=1000, y=668, w=200, h=18,
         color=MIST, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_align="right", text_transform="uppercase")


# =============================================================================
# SLIDE 2 — Intelligence Becomes Interface
# =============================================================================
S2 = "slide-2"
init_slide(S2, 1, EDITORIAL)

# Right 60% dark graphite panel (cinematic visual side)
add_shape(S2, "rectangle", 560, 0, 720, 720, fill=GRAPHITE, opacity=1)

# Soft violet/blue glow behind the UI
add_shape(S2, "circle", 660, 120, 440, 440, fill=VIOLET, opacity=0.18)
add_shape(S2, "circle", 880, 360, 320, 320, fill=NEURAL_BLUE, opacity=0.16)

# Glassmorphism UI panel (prompt window)
add_shape(S2, "rectangle", 660, 200, 540, 320, fill=PLATINUM, opacity=0.06,
          stroke=PLATINUM, stroke_width=1)

# UI top bar
add_shape(S2, "rectangle", 660, 200, 540, 36, fill=PLATINUM, opacity=0.04)
# UI dot indicators
add_shape(S2, "circle", 678, 214, 8, 8, fill=WARM_AMBER, opacity=0.9)
add_shape(S2, "circle", 696, 214, 8, 8, fill=SIGNAL_GREEN, opacity=0.9)
add_shape(S2, "circle", 714, 214, 8, 8, fill=NEURAL_BLUE, opacity=0.9)

# Prompt label
add_text(S2, "PROMPT", "caption",
         x=680, y=256, w=120, h=14,
         color=QUANTUM_CYAN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")
add_text(S2, "What does intelligence feel like\nwhen it answers back?", "paragraph",
         x=680, y=276, w=500, h=70,
         color=PLATINUM, font_size=20, font_weight=400, line_height=1.4,
         font_family="Space Grotesk")

# Divider line in panel
add_shape(S2, "rectangle", 680, 372, 500, 1, fill=PLATINUM, opacity=0.18)

# Output label + cursor
add_text(S2, "OUTPUT", "caption",
         x=680, y=388, w=120, h=14,
         color=SIGNAL_GREEN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Waveform-like bars (response visualization)
bar_y = 412
bar_x = 680
bar_heights = [22, 38, 14, 50, 30, 44, 18, 56, 26, 40, 16, 48, 22, 34]
for i, bh in enumerate(bar_heights):
    add_shape(S2, "rectangle", bar_x + i*16, bar_y + (60 - bh)//2, 6, bh,
              fill=QUANTUM_CYAN, opacity=0.85)

# Faint neural network nodes/connectors floating behind UI
nodes = [(620, 80, 8), (840, 60, 6), (1080, 120, 7),
         (600, 600, 6), (820, 640, 8), (1100, 580, 6)]
for (nx, ny, ns) in nodes:
    add_shape(S2, "circle", nx, ny, ns, ns, fill=QUANTUM_CYAN, opacity=0.5)

# Thin connector lines (very thin rectangles)
add_shape(S2, "rectangle", 624, 92, 220, 1, fill=NEURAL_BLUE, opacity=0.45, rotation=-6)
add_shape(S2, "rectangle", 848, 80, 240, 1, fill=NEURAL_BLUE, opacity=0.45, rotation=8)
add_shape(S2, "rectangle", 608, 612, 220, 1, fill=NEURAL_BLUE, opacity=0.4, rotation=6)
add_shape(S2, "rectangle", 828, 624, 280, 1, fill=NEURAL_BLUE, opacity=0.4, rotation=-6)

# Mono UI micro-label top of panel (filename style)
add_text(S2, "session_03 · ai.distilled", "caption",
         x=820, y=212, w=360, h=14,
         color=MIST, font_size=10, font_weight=400, letter_spacing=2,
         font_family="IBM Plex Mono", text_align="center")

# ---- Left 40% editorial text column on warm ivory ----
# Tiny rule
add_shape(S2, "rectangle", 96, 96, 36, 2, fill=INK, opacity=0.9)

# Eyebrow
add_text(S2, "CHAPTER 02 · INTERFACE", "caption",
         x=144, y=88, w=320, h=18,
         color=INK, font_size=11, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Headline
add_text(S2, "Intelligence becomes interface.", "title",
         x=96, y=200, w=460, h=240,
         color=INK, font_size=54, font_weight=400, line_height=1.05,
         letter_spacing=-1)

# Body
add_text(S2, "Computation, once invisible, takes a shape we can speak to. The model does not arrive as a machine — it arrives as conversation.", "paragraph",
         x=96, y=470, w=420, h=120,
         color="#3a3733", font_size=18, font_weight=400, line_height=1.55,
         font_family="Space Grotesk")

# Small mono caption at bottom-left
add_text(S2, "FIG. 02 — HUMAN ↔ MODEL", "caption",
         x=96, y=668, w=320, h=14,
         color=MIST, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")


# =============================================================================
# SLIDE 3 — From Model to Meaning
# =============================================================================
S3 = "slide-3"
init_slide(S3, 2, OBSIDIAN)

# Background gradient suggestions: large soft circles for atmosphere
add_shape(S3, "circle", -200, -120, 700, 700, fill=NEURAL_BLUE, opacity=0.10)
add_shape(S3, "circle", 880, 480, 600, 600, fill=VIOLET, opacity=0.10)

# Top eyebrow
add_text(S3, "ACT I  ·  03", "caption",
         x=96, y=72, w=200, h=14,
         color=MIST, font_size=11, font_weight=500, letter_spacing=6,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Hero title centered top
add_text(S3, "From model to meaning.", "title",
         x=96, y=120, w=1088, h=80,
         color=PLATINUM, font_size=64, font_weight=400, line_height=1.05,
         letter_spacing=-1, text_align="center")

# Sub-line
add_text(S3, "How signal becomes structure becomes sense.", "subtitle",
         x=96, y=210, w=1088, h=36,
         color=MIST, font_size=22, font_weight=400, font_style="italic",
         text_align="center")

# Three editorial cards — Signal · Model · Meaning
# Card width 320, height 280, gaps 40
card_w, card_h, card_y = 320, 280, 320
positions = [96, 480, 864]  # x for each
labels   = ["SIGNAL", "MODEL", "MEANING"]
titles   = ["Raw input", "Reasoning", "Insight"]
bodies   = [
    "Text, image, sound — the world arrives as fragments.",
    "Patterns, weights, attention — fragments find structure.",
    "Code, decision, image — structure becomes useful.",
]
accents  = [QUANTUM_CYAN, NEURAL_BLUE, SIGNAL_GREEN]
icons    = ["Waves", "Cpu", "Sparkles"]

for i, x in enumerate(positions):
    # Card body (translucent panel)
    add_shape(S3, "rectangle", x, card_y, card_w, card_h, fill=GRAPHITE, opacity=0.85,
              stroke=PLATINUM, stroke_width=1)
    # Top accent bar
    add_shape(S3, "rectangle", x, card_y, card_w, 2, fill=accents[i], opacity=1)
    # Stage number / label
    add_text(S3, f"0{i+1}", "caption",
             x=x+24, y=card_y+22, w=80, h=16,
             color=accents[i], font_size=11, font_weight=500, letter_spacing=4,
             font_family="IBM Plex Mono")
    add_text(S3, labels[i], "caption",
             x=x+24, y=card_y+44, w=200, h=14,
             color=MIST, font_size=11, font_weight=500, letter_spacing=4,
             font_family="IBM Plex Mono", text_transform="uppercase")
    # Icon
    add_icon(S3, icons[i], x+24, card_y+76, size=44, color=accents[i], opacity=0.95)
    # Card title
    add_text(S3, titles[i], "heading",
             x=x+24, y=card_y+136, w=272, h=40,
             color=PLATINUM, font_size=28, font_weight=500, line_height=1.1)
    # Card body
    add_text(S3, bodies[i], "paragraph",
             x=x+24, y=card_y+184, w=272, h=80,
             color=MIST, font_size=15, font_weight=400, line_height=1.5,
             font_family="Space Grotesk")

# Connector lines between the 3 cards (thin glowing rectangles)
# Card 1 right edge x = 96+320=416, card 2 left edge x=480 → gap 64
add_shape(S3, "rectangle", 416, card_y + card_h//2, 64, 1, fill=NEURAL_BLUE, opacity=0.85)
# Card 2 right edge x = 480+320=800, card 3 left x=864 → gap 64
add_shape(S3, "rectangle", 800, card_y + card_h//2, 64, 1, fill=NEURAL_BLUE, opacity=0.85)
# Small connector dots
add_shape(S3, "circle", 444, card_y + card_h//2 - 3, 6, 6, fill=QUANTUM_CYAN, opacity=1)
add_shape(S3, "circle", 828, card_y + card_h//2 - 3, 6, 6, fill=QUANTUM_CYAN, opacity=1)

# Bottom mono caption
add_text(S3, "FIG. 03 — SIGNAL → MODEL → MEANING", "caption",
         x=96, y=648, w=600, h=14,
         color=MIST, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")
add_text(S3, "AI · DISTILLED  ·  03 / 15", "caption",
         x=900, y=648, w=300, h=14,
         color=MIST, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase", text_align="right")


# =============================================================================
# SLIDE 4 — The Machine Begins to See
# =============================================================================
S4 = "slide-4"
init_slide(S4, 3, OBSIDIAN)

# Atmospheric glow
add_shape(S4, "circle", 360, 80, 560, 560, fill=NEURAL_BLUE, opacity=0.10)
add_shape(S4, "circle", 520, 200, 320, 320, fill=VIOLET, opacity=0.14)

# Top-right slide meta
add_text(S4, "ACT II  ·  04", "caption",
         x=1040, y=64, w=160, h=14,
         color=MIST, font_size=11, font_weight=500, letter_spacing=6,
         font_family="IBM Plex Mono", text_align="right", text_transform="uppercase")

# Top-left brand
add_shape(S4, "rectangle", 96, 72, 28, 2, fill=PLATINUM, opacity=0.85)
add_text(S4, "AI · DISTILLED", "caption",
         x=132, y=64, w=300, h=18,
         color=MIST, font_size=11, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Center "lens" — concentric rings (use circles with stroke / no fill via opacity trick)
# Bildory shapes use fill — to make a ring, layer outer (accent) with inner (background) circle.
cx, cy = 640, 320
ring_specs = [
    (340, NEURAL_BLUE, 0.55),
    (260, NEURAL_BLUE, 0.38),
    (190, QUANTUM_CYAN, 0.30),
    (130, QUANTUM_CYAN, 0.45),
    (80,  PLATINUM,    0.18),
]
for (d, color, op) in ring_specs:
    add_shape(S4, "circle", cx - d, cy - d, d*2, d*2, fill=color, opacity=op)
    # mask with background colored circle slightly smaller
    inner = d - 6
    add_shape(S4, "circle", cx - inner, cy - inner, inner*2, inner*2, fill=OBSIDIAN, opacity=1)

# Inner core — solid luminous dot
add_shape(S4, "circle", cx - 16, cy - 16, 32, 32, fill=QUANTUM_CYAN, opacity=1)
add_shape(S4, "circle", cx - 6, cy - 6, 12, 12, fill=PLATINUM, opacity=1)

# Crosshair lines (very thin)
add_shape(S4, "rectangle", cx - 360, cy, 720, 1, fill=PLATINUM, opacity=0.12)
add_shape(S4, "rectangle", cx, cy - 280, 1, 560, fill=PLATINUM, opacity=0.12)

# Four orbiting annotation dots + labels (museum-label style)
# Top
add_shape(S4, "circle", cx - 4, cy - 340 - 4, 8, 8, fill=WARM_AMBER, opacity=1)
add_text(S4, "01 · APERTURE", "caption",
         x=560, y=cy - 372, w=240, h=14,
         color=WARM_AMBER, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_align="center", text_transform="uppercase")

# Right
add_shape(S4, "circle", cx + 340 - 4, cy - 4, 8, 8, fill=QUANTUM_CYAN, opacity=1)
add_text(S4, "02 · DEPTH", "caption",
         x=cx + 354, y=cy - 8, w=180, h=14,
         color=QUANTUM_CYAN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Bottom
add_shape(S4, "circle", cx - 4, cy + 340 - 4, 8, 8, fill=SIGNAL_GREEN, opacity=1)
add_text(S4, "03 · CONTEXT", "caption",
         x=560, y=cy + 352, w=240, h=14,
         color=SIGNAL_GREEN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_align="center", text_transform="uppercase")

# Left
add_shape(S4, "circle", cx - 340 - 4, cy - 4, 8, 8, fill=VIOLET, opacity=1)
add_text(S4, "04 · INFERENCE", "caption",
         x=cx - 540, y=cy - 8, w=180, h=14,
         color=VIOLET, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_align="right", text_transform="uppercase")

# Bottom-left hero title + supporting line
add_text(S4, "The machine\nbegins to see.", "title",
         x=96, y=540, w=720, h=120,
         color=PLATINUM, font_size=58, font_weight=400, line_height=1.0,
         letter_spacing=-1)

# Bottom-right supporting paragraph
add_text(S4, "Vision is not a camera. It is a model learning what to keep, and what to ignore.", "paragraph",
         x=820, y=560, w=380, h=80,
         color=MIST, font_size=15, font_weight=400, line_height=1.55,
         font_family="Space Grotesk", font_style="italic")

# Bottom mono fig caption
add_text(S4, "FIG. 04 — RECOGNITION FIELD", "caption",
         x=96, y=672, w=300, h=14,
         color=MIST, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")


# =============================================================================
# SLIDE 5 — Language Becomes Interface
# =============================================================================
S5 = "slide-5"
init_slide(S5, 4, EDITORIAL)

# Top-left brand mark + meta
add_shape(S5, "rectangle", 96, 72, 28, 2, fill=INK, opacity=0.9)
add_text(S5, "AI · DISTILLED", "caption",
         x=132, y=64, w=300, h=18,
         color=INK, font_size=11, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")
add_text(S5, "ACT II  ·  05", "caption",
         x=1040, y=64, w=160, h=14,
         color="#3a3733", font_size=11, font_weight=500, letter_spacing=6,
         font_family="IBM Plex Mono", text_align="right", text_transform="uppercase")

# Editorial headline top-left
add_text(S5, "Language becomes\ninterface.", "title",
         x=96, y=140, w=600, h=140,
         color=INK, font_size=58, font_weight=400, line_height=1.0,
         letter_spacing=-1)

# Italic supporting line
add_text(S5, "A sentence is now a control panel.", "subtitle",
         x=96, y=296, w=560, h=36,
         color="#3a3733", font_size=22, font_weight=400, font_style="italic")

# Vertical thin divider down the middle
add_shape(S5, "rectangle", 620, 120, 1, 480, fill=INK, opacity=0.15)

# ---- Left side: PROMPT block ----
add_text(S5, "PROMPT", "caption",
         x=96, y=380, w=120, h=14,
         color=NEURAL_BLUE, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Prompt card
add_shape(S5, "rectangle", 96, 404, 500, 160, fill=PLATINUM, opacity=0.55,
          stroke=INK, stroke_width=1)
# Vertical accent bar inside prompt card
add_shape(S5, "rectangle", 96, 404, 4, 160, fill=NEURAL_BLUE, opacity=1)
add_text(S5, "Design a calm dashboard\nthat explains my data.", "paragraph",
         x=128, y=420, w=440, h=80,
         color=INK, font_size=22, font_weight=400, line_height=1.4,
         font_family="Space Grotesk", font_style="italic")
add_text(S5, "user · 22:14", "caption",
         x=128, y=520, w=300, h=14,
         color="#6b6863", font_size=11, font_weight=400, letter_spacing=2,
         font_family="IBM Plex Mono")

# Bottom-left mono caption
add_text(S5, "FIG. 05 — TEXT → STRUCTURE", "caption",
         x=96, y=672, w=320, h=14,
         color="#6b6863", font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# ---- Right side: blooming response cards ----
# Output label
add_text(S5, "OUTPUT", "caption",
         x=672, y=140, w=120, h=14,
         color=SIGNAL_GREEN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_transform="uppercase")

# Card 1 — UI mock
card1_x, card1_y = 672, 168
add_shape(S5, "rectangle", card1_x, card1_y, 520, 140, fill=GRAPHITE, opacity=1)
add_shape(S5, "rectangle", card1_x, card1_y, 520, 2, fill=NEURAL_BLUE, opacity=1)
add_text(S5, "01 · UI", "caption",
         x=card1_x+20, y=card1_y+18, w=120, h=12,
         color=QUANTUM_CYAN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono")
# Mini bars (mock chart)
mini_bars = [40, 64, 28, 78, 50, 90, 36, 60]
for i, h in enumerate(mini_bars):
    add_shape(S5, "rectangle", card1_x + 20 + i*16, card1_y + 110 - h, 8, h,
              fill=QUANTUM_CYAN, opacity=0.85)
add_text(S5, "Calm dashboard · v1", "caption",
         x=card1_x+170, y=card1_y+44, w=320, h=14,
         color=PLATINUM, font_size=14, font_weight=500, letter_spacing=1,
         font_family="Space Grotesk")
add_text(S5, "Tone: minimal · cinematic · monochrome", "caption",
         x=card1_x+170, y=card1_y+68, w=340, h=14,
         color=MIST, font_size=11, font_weight=400, letter_spacing=2,
         font_family="IBM Plex Mono")

# Card 2 — Diagram
card2_x, card2_y = 672, 324
add_shape(S5, "rectangle", card2_x, card2_y, 520, 130, fill=GRAPHITE, opacity=1)
add_shape(S5, "rectangle", card2_x, card2_y, 520, 2, fill=VIOLET, opacity=1)
add_text(S5, "02 · DIAGRAM", "caption",
         x=card2_x+20, y=card2_y+18, w=160, h=12,
         color=VIOLET, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono")
# small node diagram
n1 = (card2_x+220, card2_y+72)
n2 = (card2_x+340, card2_y+50)
n3 = (card2_x+340, card2_y+96)
n4 = (card2_x+460, card2_y+72)
# connector lines (thin rectangles)
add_shape(S5, "rectangle", n1[0], n1[1], 122, 1, fill=PLATINUM, opacity=0.4, rotation=-10)
add_shape(S5, "rectangle", n1[0], n1[1], 122, 1, fill=PLATINUM, opacity=0.4, rotation=12)
add_shape(S5, "rectangle", n2[0], n2[1], 122, 1, fill=PLATINUM, opacity=0.4, rotation=10)
add_shape(S5, "rectangle", n3[0], n3[1], 122, 1, fill=PLATINUM, opacity=0.4, rotation=-12)
# nodes
for (nx, ny, c) in [(n1[0]-6, n1[1]-6, QUANTUM_CYAN),
                    (n2[0]-6, n2[1]-6, VIOLET),
                    (n3[0]-6, n3[1]-6, VIOLET),
                    (n4[0]-6, n4[1]-6, SIGNAL_GREEN)]:
    add_shape(S5, "circle", nx, ny, 12, 12, fill=c, opacity=1)
add_text(S5, "Information architecture", "caption",
         x=card2_x+20, y=card2_y+96, w=200, h=14,
         color=PLATINUM, font_size=12, font_weight=500, letter_spacing=1,
         font_family="Space Grotesk")

# Card 3 — Code / voice waveform (mini)
card3_x, card3_y = 672, 470
add_shape(S5, "rectangle", card3_x, card3_y, 520, 120, fill=GRAPHITE, opacity=1)
add_shape(S5, "rectangle", card3_x, card3_y, 520, 2, fill=SIGNAL_GREEN, opacity=1)
add_text(S5, "03 · CODE / VOICE", "caption",
         x=card3_x+20, y=card3_y+18, w=180, h=12,
         color=SIGNAL_GREEN, font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono")
# fake code lines
add_text(S5, "render(dashboard, theme=\"obsidian\")", "caption",
         x=card3_x+20, y=card3_y+44, w=440, h=14,
         color=PLATINUM, font_size=13, font_weight=400, letter_spacing=1,
         font_family="IBM Plex Mono")
add_text(S5, "→ minimal · calm · luminous", "caption",
         x=card3_x+20, y=card3_y+64, w=440, h=14,
         color=MIST, font_size=12, font_weight=400, letter_spacing=1,
         font_family="IBM Plex Mono")
# tiny waveform
wave = [10, 18, 6, 22, 12, 26, 8, 18, 14, 22, 10, 28, 12, 16]
for i, h in enumerate(wave):
    add_shape(S5, "rectangle", card3_x + 20 + i*14, card3_y + 96 - h//2, 4, h,
              fill=SIGNAL_GREEN, opacity=0.85)

# Right-bottom mono meta
add_text(S5, "AI · DISTILLED  ·  05 / 15", "caption",
         x=900, y=672, w=300, h=14,
         color="#6b6863", font_size=10, font_weight=500, letter_spacing=4,
         font_family="IBM Plex Mono", text_align="right", text_transform="uppercase")


# =============================================================================
# Assemble files
# =============================================================================
# Inject text elements into slides
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

# Element count
total_elements = (
    sum(len(s["textElements"]) for s in slides)
    + len(image_elements) + len(shape_elements) + len(chart_elements)
    + len(table_elements) + len(icon_elements)
)

presentation = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "AI, Distilled",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides),
        "elementCount": total_elements,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": baseLayout,
        "changelog": changelog
    }
}

OUT = "ai_distilled_slides_1_5.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(presentation, f, indent=2, ensure_ascii=False)

print(f"Wrote {OUT}")
print(f"slides: {len(slides)}")
print(f"elements: {total_elements}")
print(f"  text: {sum(len(s['textElements']) for s in slides)}")
print(f"  shapes: {len(shape_elements)}")
print(f"  icons: {len(icon_elements)}")
print(f"max zIndex: {ZIDX}")
