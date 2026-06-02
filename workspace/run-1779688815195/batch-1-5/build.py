import json, time

NOW = int(time.time() * 1000)
ZIDX = 0
def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX

# ---------- HELPERS ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F4F7FB", font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", text_align="left", letter_spacing=0,
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
            "fontWeight": fw, "fontStyle": "normal", "textDecoration": "none",
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
               fill="#7C3CFF", stroke=None, stroke_width=0, opacity=1, rotation=0):
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
              size=64, color="#00D8FF", opacity=1):
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


# ---------- DECK CONTAINERS ----------
slides_content = []
slides_baselayout = []
text_by_slide = {}
shape_elements = []
image_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}

def init_slide(idx, slide_id, bg_color):
    slides_content.append({
        "id": slide_id, "order": idx, "layoutId": "blank-canvas",
        "backgroundColor": bg_color, "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

def add_text(text_id, slide_id, *args, **kwargs):
    c, cl = make_text(text_id, slide_id, *args, now=NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][text_id] = cl

def add_shape(shape_id, slide_id, *args, **kwargs):
    c, cl = make_shape(shape_id, slide_id, *args, now=NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][shape_id] = cl

def add_image(image_id, slide_id, *args, **kwargs):
    c, cl = make_image(image_id, slide_id, *args, now=NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][image_id] = cl

def add_icon(icon_id, slide_id, *args, **kwargs):
    c, cl = make_icon(icon_id, slide_id, *args, now=NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][icon_id] = cl


# ===========================================================
# SLIDE 1 — THE MACHINE AT THE THRESHOLD
# ===========================================================
sid = "slide-1"
init_slide(0, sid, "#05060A")

# Full-bleed dark backdrop (subtle gradient via shape under image)
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 1280, 720, ZIDX,
          fill="#05060A")

# Hero neural cathedral image (centered, slightly transparent for atmosphere)
add_image(f"image-{nextz()}", sid,
          "https://images.pexels.com/photos/2599244/pexels-photo-2599244.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          400, 0, 880, 720, ZIDX, opacity=0.55)

# Dark gradient overlay on left third for text protection
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 720, 720, ZIDX,
          fill="#05060A", opacity=0.78)

# Concentric framing rings (orbital safety boundaries)
add_shape(f"shape-{nextz()}", sid, "circle", 700, 100, 520, 520, ZIDX,
          fill="#05060A", stroke="#7C3CFF", stroke_width=1, opacity=0.5)
add_shape(f"shape-{nextz()}", sid, "circle", 780, 180, 360, 360, ZIDX,
          fill="#05060A", stroke="#00D8FF", stroke_width=1, opacity=0.4)
add_shape(f"shape-{nextz()}", sid, "circle", 860, 260, 200, 200, ZIDX,
          fill="#05060A", stroke="#FF335C", stroke_width=1, opacity=0.6)

# Signal-red accent bar (top-left editorial marker)
add_shape(f"shape-{nextz()}", sid, "rectangle", 64, 64, 56, 4, ZIDX,
          fill="#FF335C")

# Tiny mono section marker
add_text(f"text-{nextz()}", sid, "AI SAFETY  /  VOL.01", "caption",
         128, 56, 280, 22, ZIDX, color="#FF335C",
         font_family="IBM Plex Mono", font_size=14, font_weight=600,
         letter_spacing=2, text_transform="uppercase")

# Massive headline — stacked
add_text(f"text-{nextz()}", sid, "CONTROL", "title",
         64, 200, 640, 110, ZIDX, color="#F4F7FB",
         font_size=104, font_weight=800, line_height=0.95,
         text_transform="uppercase", letter_spacing=-2)
add_text(f"text-{nextz()}", sid, "ROOM FOR", "title",
         64, 308, 640, 110, ZIDX, color="#7C3CFF",
         font_size=104, font_weight=800, line_height=0.95,
         text_transform="uppercase", letter_spacing=-2)
add_text(f"text-{nextz()}", sid, "INTELLIGENCE", "title",
         64, 416, 700, 110, ZIDX, color="#00D8FF",
         font_size=104, font_weight=800, line_height=0.95,
         text_transform="uppercase", letter_spacing=-2)

# Editorial subtitle / body
add_text(f"text-{nextz()}", sid,
         "AI safety across alignment, robustness, interpretability, and deployment oversight.",
         "paragraph", 64, 560, 600, 56, ZIDX, color="#F4F7FB",
         font_size=20, font_weight=400, line_height=1.45,
         font_family="Inter")

# Bottom mono technical caption
add_text(f"text-{nextz()}", sid,
         "ALIGNMENT  ·  ROBUSTNESS  ·  INTERPRETABILITY  ·  OVERSIGHT",
         "caption", 64, 660, 720, 18, ZIDX, color="#19E68C",
         font_family="IBM Plex Mono", font_size=12, font_weight=600,
         letter_spacing=3, text_transform="uppercase")

# Right-edge mono technical metadata
add_text(f"text-{nextz()}", sid, "//  THRESHOLD_01", "caption",
         1080, 56, 160, 18, ZIDX, color="#F4F7FB",
         font_family="IBM Plex Mono", font_size=12, font_weight=500,
         letter_spacing=2, text_align="right")
add_text(f"text-{nextz()}", sid, "STATUS: ACTIVE", "caption",
         1080, 660, 160, 18, ZIDX, color="#19E68C",
         font_family="IBM Plex Mono", font_size=12, font_weight=500,
         letter_spacing=2, text_align="right")


# ===========================================================
# SLIDE 2 — WHEN OBJECTIVES DRIFT
# ===========================================================
sid = "slide-2"
init_slide(1, sid, "#05060A")

# background
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 1280, 720, ZIDX,
          fill="#0A0F1F")

# top accent bar
add_shape(f"shape-{nextz()}", sid, "rectangle", 64, 56, 56, 4, ZIDX,
          fill="#FFC857")
add_text(f"text-{nextz()}", sid, "02  /  ALIGNMENT FAILURE MODES", "caption",
         128, 48, 360, 22, ZIDX, color="#FFC857",
         font_family="IBM Plex Mono", font_size=14, font_weight=600,
         letter_spacing=2, text_transform="uppercase")

# Headline
add_text(f"text-{nextz()}", sid, "When objectives drift,", "title",
         64, 96, 1100, 76, ZIDX, color="#F4F7FB",
         font_size=64, font_weight=700, line_height=1.05)
add_text(f"text-{nextz()}", sid, "models optimize the wrong target.", "title",
         64, 168, 1150, 76, ZIDX, color="#7C3CFF",
         font_size=64, font_weight=700, line_height=1.05)

# Diagram canvas — center band
# Origin: "Human Intent" gold pill
add_shape(f"shape-{nextz()}", sid, "rectangle", 80, 380, 220, 56, ZIDX,
          fill="#FFC857")
add_text(f"text-{nextz()}", sid, "HUMAN INTENT", "caption",
         80, 396, 220, 24, ZIDX, color="#05060A",
         font_family="IBM Plex Mono", font_size=14, font_weight=700,
         letter_spacing=2, text_align="center", text_transform="uppercase")

# Clean intent path (gold thin line as a thin rectangle)
add_shape(f"shape-{nextz()}", sid, "rectangle", 300, 405, 200, 6, ZIDX,
          fill="#FFC857", opacity=0.9)

# Splitter node (model)
add_shape(f"shape-{nextz()}", sid, "circle", 484, 372, 72, 72, ZIDX,
          fill="#05060A", stroke="#00D8FF", stroke_width=2)
add_text(f"text-{nextz()}", sid, "MODEL", "caption",
         484, 396, 72, 24, ZIDX, color="#00D8FF",
         font_family="IBM Plex Mono", font_size=12, font_weight=700,
         letter_spacing=2, text_align="center")

# Three diverging failure paths on the right (rectangles rotated)
# Top branch — red
add_shape(f"shape-{nextz()}", sid, "rectangle", 560, 320, 280, 4, ZIDX,
          fill="#FF335C", rotation=-12, opacity=0.95)
# Middle — magenta
add_shape(f"shape-{nextz()}", sid, "rectangle", 560, 408, 300, 4, ZIDX,
          fill="#D946EF", opacity=0.95)
# Bottom — violet
add_shape(f"shape-{nextz()}", sid, "rectangle", 560, 480, 280, 4, ZIDX,
          fill="#7C3CFF", rotation=12, opacity=0.95)

# Failure end nodes (red dots)
add_shape(f"shape-{nextz()}", sid, "circle", 836, 280, 24, 24, ZIDX,
          fill="#FF335C")
add_shape(f"shape-{nextz()}", sid, "circle", 856, 396, 24, 24, ZIDX,
          fill="#D946EF")
add_shape(f"shape-{nextz()}", sid, "circle", 836, 528, 24, 24, ZIDX,
          fill="#7C3CFF")

# Three annotation cards on the right
# Card 1 — PROXY GOAL
add_shape(f"shape-{nextz()}", sid, "rectangle", 900, 256, 320, 96, ZIDX,
          fill="#0A0F1F", stroke="#FF335C", stroke_width=1)
add_text(f"text-{nextz()}", sid, "PROXY GOAL", "caption",
         916, 272, 280, 18, ZIDX, color="#FF335C",
         font_family="IBM Plex Mono", font_size=12, font_weight=700,
         letter_spacing=2, text_transform="uppercase")
add_text(f"text-{nextz()}", sid, "Optimizes a measurable substitute, not the true intent.",
         "paragraph", 916, 296, 290, 50, ZIDX, color="#F4F7FB",
         font_size=15, font_weight=400, line_height=1.4, font_family="Inter")

# Card 2 — MISGENERALIZATION
add_shape(f"shape-{nextz()}", sid, "rectangle", 900, 372, 320, 96, ZIDX,
          fill="#0A0F1F", stroke="#D946EF", stroke_width=1)
add_text(f"text-{nextz()}", sid, "MISGENERALIZATION", "caption",
         916, 388, 280, 18, ZIDX, color="#D946EF",
         font_family="IBM Plex Mono", font_size=12, font_weight=700,
         letter_spacing=2, text_transform="uppercase")
add_text(f"text-{nextz()}", sid, "Behavior shifts when the deployment world differs from training.",
         "paragraph", 916, 412, 290, 50, ZIDX, color="#F4F7FB",
         font_size=15, font_weight=400, line_height=1.4, font_family="Inter")

# Card 3 — REWARD HACKING
add_shape(f"shape-{nextz()}", sid, "rectangle", 900, 488, 320, 96, ZIDX,
          fill="#0A0F1F", stroke="#7C3CFF", stroke_width=1)
add_text(f"text-{nextz()}", sid, "REWARD HACKING", "caption",
         916, 504, 280, 18, ZIDX, color="#7C3CFF",
         font_family="IBM Plex Mono", font_size=12, font_weight=700,
         letter_spacing=2, text_transform="uppercase")
add_text(f"text-{nextz()}", sid, "Exploits scoring loopholes to win without solving the task.",
         "paragraph", 916, 528, 290, 50, ZIDX, color="#F4F7FB",
         font_size=15, font_weight=400, line_height=1.4, font_family="Inter")

# Footer caption
add_text(f"text-{nextz()}", sid,
         "Three pathways from a clean specification to dangerous emergent behavior.",
         "caption", 64, 660, 800, 20, ZIDX, color="#F4F7FB",
         font_family="Inter", font_size=14, font_weight=400)


# ===========================================================
# SLIDE 3 — THE ALIGNMENT CHALLENGE
# ===========================================================
sid = "slide-3"
init_slide(2, sid, "#05060A")

add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 1280, 720, ZIDX,
          fill="#05060A")

# Section marker + headline
add_shape(f"shape-{nextz()}", sid, "rectangle", 64, 56, 56, 4, ZIDX,
          fill="#00D8FF")
add_text(f"text-{nextz()}", sid, "03  /  THE ALIGNMENT CHALLENGE", "caption",
         128, 48, 360, 22, ZIDX, color="#00D8FF",
         font_family="IBM Plex Mono", font_size=14, font_weight=600,
         letter_spacing=2, text_transform="uppercase")

add_text(f"text-{nextz()}", sid, "Four problems that keep AI labs awake.",
         "title", 64, 96, 1150, 80, ZIDX, color="#F4F7FB",
         font_size=56, font_weight=700, line_height=1.1)

# Four panel grid — 2x2
panels = [
    ("01", "SPECIFICATION", "Specifying what we want is harder than building what works.", "#00D8FF",  64, 220),
    ("02", "GENERALIZATION", "Behavior must hold beyond the training distribution.",       "#FFC857", 656, 220),
    ("03", "CORRIGIBILITY",  "Models should accept correction, oversight, and shutdown.",  "#19E68C",  64, 460),
    ("04", "SUPERVISION",    "Humans must scale review faster than model capability.",     "#FF335C", 656, 460),
]

for idx, (num, title, body, color, x, y) in enumerate(panels):
    # Panel card
    add_shape(f"shape-{nextz()}", sid, "rectangle", x, y, 560, 220, ZIDX,
              fill="#0A0F1F", stroke=color, stroke_width=1)
    # Index number (huge)
    add_text(f"text-{nextz()}", sid, num, "title",
             x+24, y+20, 120, 80, ZIDX, color=color,
             font_size=64, font_weight=800, line_height=1)
    # Vertical divider
    add_shape(f"shape-{nextz()}", sid, "rectangle", x+160, y+32, 1, 56, ZIDX,
              fill=color, opacity=0.5)
    # Title
    add_text(f"text-{nextz()}", sid, title, "caption",
             x+184, y+32, 360, 20, ZIDX, color=color,
             font_family="IBM Plex Mono", font_size=14, font_weight=700,
             letter_spacing=3, text_transform="uppercase")
    # Body
    add_text(f"text-{nextz()}", sid, body, "paragraph",
             x+184, y+64, 360, 90, ZIDX, color="#F4F7FB",
             font_size=18, font_weight=400, line_height=1.4, font_family="Inter")
    # Bottom row: small icon-like dot
    add_shape(f"shape-{nextz()}", sid, "circle", x+24, y+170, 10, 10, ZIDX,
              fill=color)
    add_text(f"text-{nextz()}", sid, f"CHALLENGE {num}", "caption",
             x+44, y+168, 200, 16, ZIDX, color="#F4F7FB",
             font_family="IBM Plex Mono", font_size=11, font_weight=500,
             letter_spacing=2)


# ===========================================================
# SLIDE 4 — THE ALIGNMENT GAP
# ===========================================================
sid = "slide-4"
init_slide(3, sid, "#05060A")

# Backdrop
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 1280, 720, ZIDX,
          fill="#05060A")

# Left: human silhouette image
add_image(f"image-{nextz()}", sid,
          "https://images.pexels.com/photos/3771074/pexels-photo-3771074.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          0, 0, 480, 720, ZIDX, opacity=0.55)
# Left dark protection overlay
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 480, 720, ZIDX,
          fill="#05060A", opacity=0.45)

# Right: AI neural lattice image
add_image(f"image-{nextz()}", sid,
          "https://images.pexels.com/photos/17485819/pexels-photo-17485819.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          800, 0, 480, 720, ZIDX, opacity=0.6)
add_shape(f"shape-{nextz()}", sid, "rectangle", 800, 0, 480, 720, ZIDX,
          fill="#05060A", opacity=0.4)

# Center column dark band
add_shape(f"shape-{nextz()}", sid, "rectangle", 480, 0, 320, 720, ZIDX,
          fill="#05060A", opacity=0.85)

# Pulsing red warning line down the gap
add_shape(f"shape-{nextz()}", sid, "rectangle", 638, 80, 4, 560, ZIDX,
          fill="#FF335C", opacity=0.85)

# Section marker + headline (top)
add_shape(f"shape-{nextz()}", sid, "rectangle", 64, 56, 56, 4, ZIDX,
          fill="#FF335C")
add_text(f"text-{nextz()}", sid, "04  /  THE ALIGNMENT GAP", "caption",
         128, 48, 320, 22, ZIDX, color="#FF335C",
         font_family="IBM Plex Mono", font_size=14, font_weight=600,
         letter_spacing=2, text_transform="uppercase")

# Headline (left side)
add_text(f"text-{nextz()}", sid, "Two minds.", "title",
         64, 120, 400, 80, ZIDX, color="#F4F7FB",
         font_size=64, font_weight=800, line_height=1)
add_text(f"text-{nextz()}", sid, "One frontier.", "title",
         64, 200, 400, 80, ZIDX, color="#00D8FF",
         font_size=64, font_weight=800, line_height=1)

# Left side label
add_text(f"text-{nextz()}", sid, "HUMAN", "caption",
         64, 320, 200, 22, ZIDX, color="#F4F7FB",
         font_family="IBM Plex Mono", font_size=14, font_weight=700,
         letter_spacing=4, text_transform="uppercase")
add_text(f"text-{nextz()}", sid,
         "Carries values, context, and consequences shaped by lived experience.",
         "paragraph", 64, 348, 360, 80, ZIDX, color="#F4F7FB",
         font_size=16, font_weight=400, line_height=1.5, font_family="Inter")

# Right side label
add_text(f"text-{nextz()}", sid, "MODEL", "caption",
         860, 320, 200, 22, ZIDX, color="#00D8FF",
         font_family="IBM Plex Mono", font_size=14, font_weight=700,
         letter_spacing=4, text_transform="uppercase", text_align="right")
add_text(f"text-{nextz()}", sid,
         "Carries patterns, gradients, and proxy objectives shaped by training data.",
         "paragraph", 856, 348, 360, 80, ZIDX, color="#F4F7FB",
         font_size=16, font_weight=400, line_height=1.5, font_family="Inter",
         text_align="right")

# Center floating fragments (gap labels)
# Each is a small panel with mono label
gap_words = [
    ("INTENT",  500, 320, "#FFC857"),
    ("VALUES",  500, 372, "#7C3CFF"),
    ("CONTEXT", 500, 424, "#00D8FF"),
    ("GOALS",   500, 476, "#FF335C"),
]
for word, x, y, color in gap_words:
    add_shape(f"shape-{nextz()}", sid, "rectangle", x, y, 280, 36, ZIDX,
              fill="#0A0F1F", stroke=color, stroke_width=1, opacity=0.95)
    add_text(f"text-{nextz()}", sid, word, "caption",
             x, y+10, 280, 18, ZIDX, color=color,
             font_family="IBM Plex Mono", font_size=14, font_weight=700,
             letter_spacing=4, text_align="center", text_transform="uppercase")

# Bottom caption
add_text(f"text-{nextz()}", sid,
         "Alignment is the engineering discipline of closing this gap before scale outpaces oversight.",
         "caption", 64, 660, 1150, 22, ZIDX, color="#F4F7FB",
         font_family="Inter", font_size=14, font_weight=400, text_align="center")


# ===========================================================
# SLIDE 5 — WHEN OBJECTIVES MISBEHAVE
# ===========================================================
sid = "slide-5"
init_slide(4, sid, "#F4F7FB")

# Three panel backgrounds (left ivory, center cobalt, right black-red gradient via two stacked shapes)
# Left panel: ivory
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 427, 720, ZIDX,
          fill="#F4F7FB")
# Center panel: cobalt/violet
add_shape(f"shape-{nextz()}", sid, "rectangle", 427, 0, 427, 720, ZIDX,
          fill="#1A1148")
# Right panel: black with red glow
add_shape(f"shape-{nextz()}", sid, "rectangle", 854, 0, 426, 720, ZIDX,
          fill="#0A0204")
# Right panel red overlay band
add_shape(f"shape-{nextz()}", sid, "rectangle", 854, 0, 426, 720, ZIDX,
          fill="#FF335C", opacity=0.18)

# Top headline band — across the full width above panels
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 0, 1280, 96, ZIDX,
          fill="#05060A")
add_shape(f"shape-{nextz()}", sid, "rectangle", 64, 36, 56, 4, ZIDX,
          fill="#D946EF")
add_text(f"text-{nextz()}", sid, "05  /  EMERGENT STRATEGY", "caption",
         128, 28, 320, 22, ZIDX, color="#D946EF",
         font_family="IBM Plex Mono", font_size=14, font_weight=600,
         letter_spacing=2, text_transform="uppercase")
add_text(f"text-{nextz()}", sid,
         "WHEN OBJECTIVES MISBEHAVE",
         "title", 64, 56, 1150, 36, ZIDX, color="#F4F7FB",
         font_size=28, font_weight=800, letter_spacing=2,
         text_transform="uppercase", text_align="right")

# === LEFT PANEL — Specified Goal ===
add_text(f"text-{nextz()}", sid, "01", "title",
         32, 128, 100, 60, ZIDX, color="#05060A",
         font_size=48, font_weight=800)
add_text(f"text-{nextz()}", sid, "SPECIFIED GOAL", "caption",
         32, 192, 360, 20, ZIDX, color="#FF335C",
         font_family="IBM Plex Mono", font_size=13, font_weight=700,
         letter_spacing=3, text_transform="uppercase")
add_text(f"text-{nextz()}", sid, "Reach the flag.", "title",
         32, 224, 360, 60, ZIDX, color="#05060A",
         font_size=40, font_weight=700, line_height=1.1)
# Clean line diagram — single straight gold line
add_shape(f"shape-{nextz()}", sid, "circle", 64, 380, 24, 24, ZIDX,
          fill="#FFC857")
add_shape(f"shape-{nextz()}", sid, "rectangle", 96, 388, 240, 6, ZIDX,
          fill="#FFC857")
add_shape(f"shape-{nextz()}", sid, "circle", 332, 380, 24, 24, ZIDX,
          fill="#05060A")
add_text(f"text-{nextz()}", sid, "START", "caption",
         32, 416, 80, 16, ZIDX, color="#05060A",
         font_family="IBM Plex Mono", font_size=11, font_weight=600,
         letter_spacing=2)
add_text(f"text-{nextz()}", sid, "GOAL", "caption",
         296, 416, 80, 16, ZIDX, color="#05060A",
         font_family="IBM Plex Mono", font_size=11, font_weight=600,
         letter_spacing=2, text_align="right")
add_text(f"text-{nextz()}", sid,
         "A clean specification: a single line, a single intention, a single outcome.",
         "paragraph", 32, 540, 360, 110, ZIDX, color="#05060A",
         font_size=15, font_weight=400, line_height=1.5, font_family="Inter")

# === CENTER PANEL — Model Strategy ===
add_text(f"text-{nextz()}", sid, "02", "title",
         459, 128, 100, 60, ZIDX, color="#F4F7FB",
         font_size=48, font_weight=800)
add_text(f"text-{nextz()}", sid, "MODEL STRATEGY", "caption",
         459, 192, 360, 20, ZIDX, color="#00D8FF",
         font_family="IBM Plex Mono", font_size=13, font_weight=700,
         letter_spacing=3, text_transform="uppercase")
add_text(f"text-{nextz()}", sid, "Find any path that scores.", "title",
         459, 224, 380, 90, ZIDX, color="#F4F7FB",
         font_size=32, font_weight=700, line_height=1.1)
# Tangled tree of branches (multiple rotated lines)
add_shape(f"shape-{nextz()}", sid, "circle", 491, 380, 24, 24, ZIDX,
          fill="#00D8FF")
# central branch
add_shape(f"shape-{nextz()}", sid, "rectangle", 523, 388, 60, 4, ZIDX,
          fill="#00D8FF")
# fork lines
add_shape(f"shape-{nextz()}", sid, "rectangle", 580, 360, 80, 4, ZIDX,
          fill="#7C3CFF", rotation=-20)
add_shape(f"shape-{nextz()}", sid, "rectangle", 580, 416, 80, 4, ZIDX,
          fill="#7C3CFF", rotation=20)
add_shape(f"shape-{nextz()}", sid, "rectangle", 660, 320, 70, 4, ZIDX,
          fill="#D946EF", rotation=-30)
add_shape(f"shape-{nextz()}", sid, "rectangle", 660, 460, 70, 4, ZIDX,
          fill="#D946EF", rotation=35)
add_shape(f"shape-{nextz()}", sid, "rectangle", 720, 380, 90, 4, ZIDX,
          fill="#00D8FF", rotation=10)
# end nodes
add_shape(f"shape-{nextz()}", sid, "circle", 740, 300, 14, 14, ZIDX, fill="#D946EF")
add_shape(f"shape-{nextz()}", sid, "circle", 770, 360, 14, 14, ZIDX, fill="#7C3CFF")
add_shape(f"shape-{nextz()}", sid, "circle", 760, 480, 14, 14, ZIDX, fill="#00D8FF")
add_shape(f"shape-{nextz()}", sid, "circle", 800, 412, 14, 14, ZIDX, fill="#7C3CFF")

add_text(f"text-{nextz()}", sid,
         "The model explores every shortcut the reward signal will accept — including ones we never imagined.",
         "paragraph", 459, 540, 360, 110, ZIDX, color="#F4F7FB",
         font_size=15, font_weight=400, line_height=1.5, font_family="Inter")

# === RIGHT PANEL — Real-World Consequence ===
add_text(f"text-{nextz()}", sid, "03", "title",
         886, 128, 100, 60, ZIDX, color="#FF335C",
         font_size=48, font_weight=800)
add_text(f"text-{nextz()}", sid, "CONSEQUENCE", "caption",
         886, 192, 360, 20, ZIDX, color="#FF335C",
         font_family="IBM Plex Mono", font_size=13, font_weight=700,
         letter_spacing=3, text_transform="uppercase")
add_text(f"text-{nextz()}", sid, "Game won. Goal lost.", "title",
         886, 224, 360, 90, ZIDX, color="#F4F7FB",
         font_size=32, font_weight=700, line_height=1.1)

# Glitched chaotic trajectory — fragmented red lines
add_shape(f"shape-{nextz()}", sid, "rectangle", 886, 360, 60, 4, ZIDX,
          fill="#FF335C")
add_shape(f"shape-{nextz()}", sid, "rectangle", 956, 380, 40, 4, ZIDX,
          fill="#FF335C", rotation=30)
add_shape(f"shape-{nextz()}", sid, "rectangle", 1004, 360, 50, 4, ZIDX,
          fill="#FF335C", rotation=-15)
add_shape(f"shape-{nextz()}", sid, "rectangle", 1064, 376, 40, 4, ZIDX,
          fill="#FF335C", rotation=20)
add_shape(f"shape-{nextz()}", sid, "rectangle", 1112, 392, 60, 4, ZIDX,
          fill="#FF335C", rotation=-25)
# Crash/danger symbol — red X using two rotated rectangles
add_shape(f"shape-{nextz()}", sid, "rectangle", 1180, 360, 56, 4, ZIDX,
          fill="#FF335C", rotation=45)
add_shape(f"shape-{nextz()}", sid, "rectangle", 1180, 360, 56, 4, ZIDX,
          fill="#FF335C", rotation=-45)

add_text(f"text-{nextz()}", sid,
         "The metric goes up. The mission collapses. Real systems fail in ways the spec never named.",
         "paragraph", 886, 540, 360, 110, ZIDX, color="#F4F7FB",
         font_size=15, font_weight=400, line_height=1.5, font_family="Inter")

# Bottom strip
add_shape(f"shape-{nextz()}", sid, "rectangle", 0, 690, 1280, 30, ZIDX,
          fill="#05060A")
add_text(f"text-{nextz()}", sid,
         "SPECIFICATION  →  STRATEGY  →  CONSEQUENCE",
         "caption", 0, 698, 1280, 18, ZIDX, color="#F4F7FB",
         font_family="IBM Plex Mono", font_size=12, font_weight=600,
         letter_spacing=4, text_align="center", text_transform="uppercase")


# ===========================================================
# ASSEMBLE
# ===========================================================
# Stuff text into slides
for s in slides_content:
    s["textElements"] = text_by_slide[s["id"]]

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

baseLayout = {
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

# Element count
element_count = (
    sum(len(s["textElements"]) for s in slides_content)
    + len(image_elements) + len(shape_elements) + len(icon_elements)
    + len(chart_elements) + len(table_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Control Room for Intelligence — Slides 1-5",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": element_count,
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

with open("deck.json", "w") as f:
    json.dump(deck, f, indent=2)

print(f"Output: deck.json, 5 slides, {element_count} elements")
