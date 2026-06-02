import json
import time

NOW = int(time.time() * 1000)

# Palette
OBSIDIAN = "#080A0F"
GRAPHITE = "#161A22"
NEURAL_BLUE = "#2F6BFF"
QUANTUM_CYAN = "#4DEBFF"
SYNTH_VIOLET = "#7B5CFF"
PLATINUM = "#E8ECF2"
MIST = "#AAB2C0"
SIGNAL_GREEN = "#38F2A0"
WARM_GOLD = "#F4B860"
IVORY = "#FAFAF7"

COUNTER = 600
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- Helpers ----------
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
               fill=NEURAL_BLUE, stroke=None, stroke_width=0, opacity=1):
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
              size=48, color=NEURAL_BLUE, opacity=1):
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


# ---------- Containers ----------
SLIDES = []
TEXT_BY_SLIDE = {}
SHAPE_CONTENT, IMAGE_CONTENT, ICON_CONTENT, CHART_CONTENT, TABLE_CONTENT = [], [], [], [], []
CHANGELOG_SLIDES = {}

def new_slide(slide_id, bg_color=OBSIDIAN):
    order = int(slide_id.split("-")[1]) - 11
    SLIDES.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg_color, "textElements": []
    })
    TEXT_BY_SLIDE[slide_id] = []
    CHANGELOG_SLIDES[slide_id] = {"elements": {}}

def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    TEXT_BY_SLIDE[slide_id].append(c)
    CHANGELOG_SLIDES[slide_id]["elements"][tid] = cl

def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    SHAPE_CONTENT.append(c)
    CHANGELOG_SLIDES[slide_id]["elements"][sid] = cl

def add_image(slide_id, src, x, y, w, h, **kwargs):
    n = next_id()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, src, x, y, w, h, n, NOW, **kwargs)
    IMAGE_CONTENT.append(c)
    CHANGELOG_SLIDES[slide_id]["elements"][iid] = cl

def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kwargs)
    ICON_CONTENT.append(c)
    CHANGELOG_SLIDES[slide_id]["elements"][iid] = cl


# =====================================================================
# SLIDE 11 — Trust Is the Interface
# =====================================================================
sid = "slide-11"
new_slide(sid, OBSIDIAN)

# Faint ambient panel - very subtle horizontal divider band
add_shape(sid, "rectangle", 0, 358, 1280, 1, fill="#1A1F2A", opacity=0.6)

# Section eyebrow (top center)
add_text(sid, "CHAPTER 11  ·  ETHICS", "caption", 48, 56, 600, 22,
         color=MIST, font_size=12, letter_spacing=4, text_transform="uppercase",
         font_weight=500)

# Title — centered serif feel via large weight
add_text(sid, "Trust is the interface.", "title", 48, 96, 1184, 90,
         color=PLATINUM, font_size=64, font_weight=600, text_align="center",
         letter_spacing=-1, line_height=1.05)

# Subtitle
add_text(sid, "What we cannot inspect, we cannot trust.", "subtitle", 48, 196, 1184, 36,
         color=MIST, font_size=20, font_weight=400, text_align="center",
         font_style="italic", line_height=1.3)

# Central balance diagram — a glass card panel
# Card background
add_shape(sid, "rectangle", 480, 264, 320, 76, fill=GRAPHITE, opacity=0.9)
# Thin border accent at top of card
add_shape(sid, "rectangle", 480, 264, 320, 1, fill=NEURAL_BLUE, opacity=0.7)

# Glow circle at center (decision node)
add_shape(sid, "circle", 624, 282, 32, 32, fill=NEURAL_BLUE, opacity=0.25)
add_shape(sid, "circle", 632, 290, 16, 16, fill=QUANTUM_CYAN, opacity=0.9)

# Decision path label
add_text(sid, "AI DECISION PATH", "caption", 480, 280, 320, 16,
         color=MIST, font_size=10, letter_spacing=3, text_transform="uppercase",
         font_weight=500, text_align="center")
add_text(sid, "model → reasoning → output", "caption", 480, 312, 320, 18,
         color=PLATINUM, font_size=13, font_weight=400, text_align="center",
         font_family="IBM Plex Mono")

# Golden oversight thread (horizontal line through the center)
add_shape(sid, "line", 96, 302, 384, 1, fill=WARM_GOLD, stroke=WARM_GOLD,
          stroke_width=1, opacity=0.55)
add_shape(sid, "line", 800, 302, 384, 1, fill=WARM_GOLD, stroke=WARM_GOLD,
          stroke_width=1, opacity=0.55)
# Tiny gold endpoints
add_shape(sid, "circle", 92, 298, 8, 8, fill=WARM_GOLD, opacity=0.9)
add_shape(sid, "circle", 1180, 298, 8, 8, fill=WARM_GOLD, opacity=0.9)

# Gold thread label
add_text(sid, "HUMAN OVERSIGHT", "caption", 540, 240, 200, 14,
         color=WARM_GOLD, font_size=10, letter_spacing=4, text_transform="uppercase",
         font_weight=500, text_align="center")

# Four editorial cards along the bottom
card_y = 408
card_h = 232
card_w = 264
gap = 24
start_x = (1280 - (4 * card_w + 3 * gap)) // 2  # = 64

cards = [
    ("01", "Transparency", "Models that explain themselves before they decide.", "Eye"),
    ("02", "Safety", "Boundaries built in, not bolted on after release.", "Shield"),
    ("03", "Bias", "Continuous audit of who the system serves — and who it doesn't.", "Scale"),
    ("04", "Control", "A steady human hand on every consequential output.", "Hand"),
]

for i, (num, title, body, icon_name) in enumerate(cards):
    cx = start_x + i * (card_w + gap)
    # card panel
    add_shape(sid, "rectangle", cx, card_y, card_w, card_h, fill=GRAPHITE, opacity=0.85)
    # top accent bar
    add_shape(sid, "rectangle", cx, card_y, card_w, 2, fill=NEURAL_BLUE, opacity=0.9)
    # number
    add_text(sid, num, "caption", cx + 24, card_y + 24, 60, 16,
             color=NEURAL_BLUE, font_size=11, letter_spacing=3,
             text_transform="uppercase", font_weight=600,
             font_family="IBM Plex Mono")
    # icon
    add_icon(sid, icon_name, cx + 24, card_y + 56, size=28, color=PLATINUM, opacity=0.9)
    # heading
    add_text(sid, title, "heading", cx + 24, card_y + 100, card_w - 48, 32,
             color=PLATINUM, font_size=22, font_weight=600, line_height=1.2)
    # body
    add_text(sid, body, "paragraph", cx + 24, card_y + 140, card_w - 48, 80,
             color=MIST, font_size=13, font_weight=400, line_height=1.55)


# =====================================================================
# SLIDE 12 — The Machine Learns in Silence
# =====================================================================
sid = "slide-12"
new_slide(sid, OBSIDIAN)

# Faint vertical rule for editorial structure
add_shape(sid, "rectangle", 96, 96, 1, 528, fill="#1F2530", opacity=0.7)

# Eyebrow
add_text(sid, "CHAPTER 12  ·  LEARNING", "caption", 128, 96, 400, 18,
         color=MIST, font_size=12, letter_spacing=4, text_transform="uppercase",
         font_weight=500)

# Oversized title (top-left, two lines)
add_text(sid, "The machine learns", "title", 128, 136, 720, 80,
         color=PLATINUM, font_size=68, font_weight=600, letter_spacing=-1.5,
         line_height=1.05)
add_text(sid, "in silence.", "title", 128, 216, 720, 80,
         color=PLATINUM, font_size=68, font_weight=400, letter_spacing=-1.5,
         line_height=1.05, font_style="italic")

# Neural network diagram — center-left/center area
# Three layers of nodes, thin connecting lines
# Layer x positions
layer_x = [200, 380, 560, 740]
nodes_per_layer = [3, 5, 5, 3]
node_radius = 7
layer_y_offsets = {3: [180, 240, 300], 5: [120, 180, 240, 300, 360]}

# Compute node centers
node_centers = []
center_y = 380
for i, nx in enumerate(layer_x):
    n = nodes_per_layer[i]
    if n == 3:
        ys = [center_y - 80, center_y, center_y + 80]
    else:
        ys = [center_y - 160, center_y - 80, center_y, center_y + 80, center_y + 160]
    layer_pts = [(nx, y) for y in ys]
    node_centers.append(layer_pts)

# Draw connections (lines) between adjacent layers
for li in range(len(node_centers) - 1):
    for (x1, y1) in node_centers[li]:
        for (x2, y2) in node_centers[li + 1]:
            # Draw a thin line as a rectangle (very thin) — but use 'line' shapeType
            add_shape(sid, "line", x1, y1, x2 - x1, y2 - y1,
                      fill=NEURAL_BLUE, stroke=NEURAL_BLUE,
                      stroke_width=1, opacity=0.18)

# Draw nodes on top — outer glow + inner dot
for li, layer in enumerate(node_centers):
    for (x, y) in layer:
        # outer glow
        add_shape(sid, "circle", x - 14, y - 14, 28, 28,
                  fill=NEURAL_BLUE, opacity=0.15)
        # core
        color = QUANTUM_CYAN if li in (1, 2) else PLATINUM
        add_shape(sid, "circle", x - node_radius, y - node_radius,
                  node_radius * 2, node_radius * 2,
                  fill=color, opacity=0.95)

# Layer labels (mono, beneath the diagram)
layer_labels = ["INPUT", "HIDDEN", "HIDDEN", "OUTPUT"]
for i, lbl in enumerate(layer_labels):
    add_text(sid, lbl, "caption", layer_x[i] - 50, 568, 100, 14,
             color=MIST, font_size=10, letter_spacing=3,
             text_transform="uppercase", font_weight=500, text_align="center",
             font_family="IBM Plex Mono")

# Insight block bottom-right
add_shape(sid, "rectangle", 880, 432, 304, 1, fill=QUANTUM_CYAN, opacity=0.5)
add_text(sid, "OBSERVATION", "caption", 880, 448, 304, 14,
         color=QUANTUM_CYAN, font_size=10, letter_spacing=4,
         text_transform="uppercase", font_weight=500,
         font_family="IBM Plex Mono")
add_text(sid,
         "Billions of weights settle into pattern — a quiet calibration that human eyes will never see.",
         "paragraph", 880, 472, 304, 120,
         color=PLATINUM, font_size=15, font_weight=400, line_height=1.55)
add_text(sid, "— architecture, in motion", "caption", 880, 600, 304, 16,
         color=MIST, font_size=11, font_style="italic", font_weight=400)

# Footer mono caption
add_text(sid, "fig.12  ·  feed-forward neural model", "caption", 128, 656, 400, 14,
         color=MIST, font_size=10, letter_spacing=2,
         font_weight=400, font_family="IBM Plex Mono")


# =====================================================================
# SLIDE 13 — Signals Become Meaning
# =====================================================================
sid = "slide-13"
new_slide(sid, OBSIDIAN)

# Eyebrow
add_text(sid, "CHAPTER 13  ·  TRANSFORMATION", "caption", 48, 64, 1184, 18,
         color=MIST, font_size=12, letter_spacing=4, text_transform="uppercase",
         font_weight=500, text_align="center")

# Title centered
add_text(sid, "Signals become meaning.", "title", 48, 104, 1184, 80,
         color=PLATINUM, font_size=56, font_weight=600, text_align="center",
         letter_spacing=-1)

# Subtitle
add_text(sid, "Three stages from noise to insight.", "subtitle", 48, 188, 1184, 32,
         color=MIST, font_size=18, font_weight=400, text_align="center",
         font_style="italic")

# Three glass panels
panel_y = 264
panel_h = 320
panel_w = 360
gap = 32
start_x = (1280 - (3 * panel_w + 2 * gap)) // 2  # = 64

stages = [
    ("01", "DATA", "Raw signal", "Numbers without form, scattered across the dark.", "raw"),
    ("02", "PATTERN", "Constellation", "Clusters emerge — relationships find each other.", "cluster"),
    ("03", "PREDICTION", "Insight", "A clean waveform draws itself out of the noise.", "wave"),
]

for i, (num, label, title, body, kind) in enumerate(stages):
    px = start_x + i * (panel_w + gap)
    # Panel
    add_shape(sid, "rectangle", px, panel_y, panel_w, panel_h, fill=GRAPHITE, opacity=0.85)
    # Top accent
    accent = [NEURAL_BLUE, SYNTH_VIOLET, QUANTUM_CYAN][i]
    add_shape(sid, "rectangle", px, panel_y, panel_w, 2, fill=accent, opacity=0.95)
    # Stage number
    add_text(sid, num, "caption", px + 28, panel_y + 24, 60, 16,
             color=accent, font_size=11, letter_spacing=3,
             text_transform="uppercase", font_weight=600,
             font_family="IBM Plex Mono")
    # Mono label
    add_text(sid, label, "caption", px + 28, panel_y + 48, 200, 14,
             color=MIST, font_size=10, letter_spacing=4,
             text_transform="uppercase", font_weight=500,
             font_family="IBM Plex Mono")
    # Visual zone (height 120) — different per stage
    vy = panel_y + 88
    if kind == "raw":
        # scattered dots
        positions = [(20, 30), (60, 70), (110, 20), (150, 80), (190, 40),
                     (230, 60), (270, 30), (300, 75), (45, 90), (130, 100),
                     (180, 15), (250, 95), (90, 50), (215, 110), (145, 55)]
        for (dx, dy) in positions:
            add_shape(sid, "circle", px + 28 + dx, vy + dy, 4, 4,
                      fill=accent, opacity=0.65)
    elif kind == "cluster":
        # three clustered groups
        clusters = [(60, 40), (200, 30), (140, 90)]
        offsets = [(0,0),(8,4),(-6,8),(4,-6),(10,10),(-8,-2),(2,12)]
        for (cx, cy) in clusters:
            for (ox, oy) in offsets:
                add_shape(sid, "circle", px + 28 + cx + ox, vy + cy + oy, 4, 4,
                          fill=accent, opacity=0.75)
        # connector lines
        add_shape(sid, "line", px + 28 + 60, vy + 40, 140, -10,
                  fill=accent, stroke=accent, stroke_width=1, opacity=0.4)
        add_shape(sid, "line", px + 28 + 200, vy + 30, -60, 60,
                  fill=accent, stroke=accent, stroke_width=1, opacity=0.4)
        add_shape(sid, "line", px + 28 + 60, vy + 40, 80, 50,
                  fill=accent, stroke=accent, stroke_width=1, opacity=0.4)
    else:  # wave
        # smooth waveform via segmented lines
        wave_pts = [(0, 80), (40, 60), (80, 40), (120, 50), (160, 30),
                    (200, 50), (240, 70), (280, 50), (304, 40)]
        for j in range(len(wave_pts) - 1):
            x1, y1 = wave_pts[j]
            x2, y2 = wave_pts[j + 1]
            add_shape(sid, "line", px + 28 + x1, vy + y1, x2 - x1, y2 - y1,
                      fill=accent, stroke=accent, stroke_width=2, opacity=0.95)
        # endpoint dot
        add_shape(sid, "circle", px + 28 + 300, vy + 36, 8, 8,
                  fill=accent, opacity=1)

    # Title
    add_text(sid, title, "heading", px + 28, panel_y + 220, panel_w - 56, 32,
             color=PLATINUM, font_size=22, font_weight=600)
    # Body
    add_text(sid, body, "paragraph", px + 28, panel_y + 256, panel_w - 56, 60,
             color=MIST, font_size=13, font_weight=400, line_height=1.55)

# Connector arrows between panels
for i in range(2):
    cx_start = start_x + (i + 1) * panel_w + i * gap
    arrow_y = panel_y + panel_h // 2 - 6
    add_text(sid, "→", "heading", cx_start, arrow_y, gap, 24,
             color=MIST, font_size=20, font_weight=400, text_align="center")

# Footer
add_text(sid, "fig.13  ·  data → pattern → prediction", "caption", 48, 656, 1184, 14,
         color=MIST, font_size=10, letter_spacing=3,
         font_weight=400, font_family="IBM Plex Mono", text_align="center")


# =====================================================================
# SLIDE 14 — The Human Question
# =====================================================================
sid = "slide-14"
new_slide(sid, OBSIDIAN)

# Right-side image — silhouette / human in dark room
add_image(sid,
          "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          720, 0, 560, 720, opacity=0.85)

# Soft dark overlay on image to deepen the cinematic feel
add_shape(sid, "rectangle", 720, 0, 560, 720, fill=OBSIDIAN, opacity=0.35)

# Vertical accent rule on the left
add_shape(sid, "rectangle", 96, 96, 1, 528, fill="#2A3040", opacity=0.7)

# Eyebrow
add_text(sid, "CHAPTER 14  ·  RESPONSIBILITY", "caption", 128, 96, 480, 18,
         color=MIST, font_size=12, letter_spacing=4, text_transform="uppercase",
         font_weight=500)

# Tiny attribution top-right (over image)
add_text(sid, "ESSAY  ·  04", "caption", 1080, 96, 152, 14,
         color=MIST, font_size=10, letter_spacing=4, text_transform="uppercase",
         font_weight=500, text_align="right", font_family="IBM Plex Mono")

# Quote mark
add_text(sid, "“", "title", 128, 200, 80, 100,
         color=WARM_GOLD, font_size=120, font_weight=400, line_height=1)

# Pull quote — italic, oversized
add_text(sid,
         "The hardest question is not",
         "title", 128, 296, 600, 60,
         color=PLATINUM, font_size=42, font_weight=400, font_style="italic",
         letter_spacing=-0.5, line_height=1.15)
add_text(sid,
         "what the machine can do —",
         "title", 128, 348, 600, 60,
         color=PLATINUM, font_size=42, font_weight=400, font_style="italic",
         letter_spacing=-0.5, line_height=1.15)
add_text(sid,
         "but what we should ask of it.",
         "title", 128, 400, 600, 60,
         color=WARM_GOLD, font_size=42, font_weight=500, font_style="italic",
         letter_spacing=-0.5, line_height=1.15)

# Attribution
add_text(sid, "—  ON THE HUMAN QUESTION", "caption", 128, 488, 480, 16,
         color=MIST, font_size=11, letter_spacing=4, text_transform="uppercase",
         font_weight=500, font_family="IBM Plex Mono")

# Small editorial body line
add_text(sid,
         "Judgment, dignity, and consequence remain ours to carry.",
         "paragraph", 128, 544, 528, 28,
         color=MIST, font_size=15, font_weight=400, line_height=1.5,
         font_style="italic")

# Tiny mono footer left
add_text(sid, "fig.14  ·  the human question", "caption", 128, 656, 400, 14,
         color=MIST, font_size=10, letter_spacing=2,
         font_weight=400, font_family="IBM Plex Mono")


# =====================================================================
# SLIDE 15 — Intelligence, Designed Carefully
# =====================================================================
sid = "slide-15"
new_slide(sid, OBSIDIAN)

# Horizon line
add_shape(sid, "rectangle", 0, 432, 1280, 1, fill="#1F2530", opacity=0.9)

# Subtle reflective gradient under horizon (a faint band)
add_shape(sid, "rectangle", 0, 432, 1280, 80, fill=NEURAL_BLUE, opacity=0.06)
add_shape(sid, "rectangle", 0, 512, 1280, 80, fill=NEURAL_BLUE, opacity=0.03)

# Sunrise glow — three stacked translucent rings (concentric circles centered at horizon)
core_cx, core_cy = 640, 432
ring_specs = [
    (220, WARM_GOLD, 0.08),
    (180, WARM_GOLD, 0.12),
    (140, NEURAL_BLUE, 0.22),
    (100, QUANTUM_CYAN, 0.35),
    (64,  QUANTUM_CYAN, 0.6),
    (32,  PLATINUM, 0.95),
]
for r, color, op in ring_specs:
    add_shape(sid, "circle", core_cx - r, core_cy - r, r * 2, r * 2,
              fill=color, opacity=op)

# Tiny orbiting nodes (data threads) — pure decoration
orbit = [(-220, -40), (-120, -150), (140, -130), (240, -30),
         (-260, 20), (260, 20), (-90, 100), (110, 100)]
for (dx, dy) in orbit:
    add_shape(sid, "circle", core_cx + dx, core_cy + dy, 4, 4,
              fill=QUANTUM_CYAN, opacity=0.7)

# Faint radial line accents (two diagonal lines crossing through the core)
add_shape(sid, "line", 320, 432, 640, 0,
          fill=PLATINUM, stroke=PLATINUM, stroke_width=1, opacity=0.08)

# Eyebrow at top
add_text(sid, "CHAPTER 15  ·  CLOSING", "caption", 48, 56, 1184, 18,
         color=MIST, font_size=12, letter_spacing=4, text_transform="uppercase",
         font_weight=500, text_align="center")

# Final title (below horizon)
add_text(sid, "Intelligence, designed carefully.", "title", 48, 504, 1184, 64,
         color=PLATINUM, font_size=52, font_weight=600, text_align="center",
         letter_spacing=-1, line_height=1.1)

# Subtitle / closing line
add_text(sid, "The future is not automated. It is authored.", "subtitle", 48, 572, 1184, 28,
         color=MIST, font_size=18, font_weight=400, text_align="center",
         font_style="italic")

# Three principles at bottom
principles = ["CLARITY", "TRUST", "HUMAN DIRECTION"]
total_w = 720
start_x = (1280 - total_w) // 2
slot_w = total_w // 3
for i, p in enumerate(principles):
    x = start_x + i * slot_w
    add_text(sid, p, "caption", x, 632, slot_w, 18,
             color=PLATINUM, font_size=12, letter_spacing=5, text_transform="uppercase",
             font_weight=600, text_align="center", font_family="IBM Plex Mono")

# Tiny dot separators between principles
for i in range(2):
    dot_x = start_x + (i + 1) * slot_w - 4
    add_shape(sid, "circle", dot_x, 638, 4, 4, fill=WARM_GOLD, opacity=0.9)

# Bottom mono signature
add_text(sid, "AI, DISTILLED  ·  END", "caption", 48, 676, 1184, 14,
         color=MIST, font_size=10, letter_spacing=5, text_transform="uppercase",
         font_weight=500, text_align="center", font_family="IBM Plex Mono")


# =====================================================================
# Assemble files
# =====================================================================
# Inject text elements into their slides
for s in SLIDES:
    s["textElements"] = TEXT_BY_SLIDE[s["id"]]

content = {
    "slides": SLIDES,
    "imageElements": IMAGE_CONTENT,
    "shapeElements": SHAPE_CONTENT,
    "chartElements": CHART_CONTENT,
    "tableElements": TABLE_CONTENT,
    "iconElements": ICON_CONTENT,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

base_layout_slides = []
for s in SLIDES:
    base_layout_slides.append({
        "id": s["id"],
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    })

base_layout = {
    "version": "v1",
    "slides": base_layout_slides,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

changelog = {"version": "2.0", "slides": CHANGELOG_SLIDES}

# Count elements
element_count = (
    sum(len(s["textElements"]) for s in SLIDES)
    + len(IMAGE_CONTENT) + len(SHAPE_CONTENT) + len(CHART_CONTENT)
    + len(TABLE_CONTENT) + len(ICON_CONTENT)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-ai-distilled-batch-11-15-{NOW}",
        "title": "AI, Distilled — Slides 11–15",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(SLIDES),
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

out_name = "ai_distilled_batch_11_15.json"
with open(out_name, "w", encoding="utf-8") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {out_name}")
print(f"Slides: {len(SLIDES)}")
print(f"Elements: {element_count}")
