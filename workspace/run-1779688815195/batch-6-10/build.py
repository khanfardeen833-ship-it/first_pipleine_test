import json, time

NOW = int(time.time() * 1000)

# ---- Counters ----
ID = 300  # next id will be 301
def nid():
    global ID
    ID += 1
    return ID

# ---- Helpers ----
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx,
              color="#F4F7FB", font_size=None, font_weight=None,
              line_height=None, align="left", letter_spacing=0,
              font_family="Space Grotesk", text_transform="none"):
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
        "animationTypewriterMode": "character", "updatedAt": NOW
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx,
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
        "updatedAt": NOW
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx,
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
        "updatedAt": NOW
    }
    return content_record, changelog_record


def make_chart(chart_id, slide_id, chart_type, x, y, w, h, zidx, chart_config):
    content_record = {
        "id": chart_id, "slideId": slide_id, "groupId": None,
        "svgDataUrl": "", "chartType": chart_type,
        "chartConfig": chart_config
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "updatedAt": NOW,
        "chartType": chart_type
    }
    return content_record, changelog_record


# ---- Containers ----
slides_content = []
slides_baselayout = []
text_by_slide = {}  # slide_id -> [content records]
shape_elements = []
icon_elements = []
chart_elements = []
image_elements = []
table_elements = []
changelog_slides = {}

def reg_text(slide_id, c, cl):
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][c["id"]] = cl

def reg_shape(c, cl):
    shape_elements.append(c)
    changelog_slides[cl["slideId"]]["elements"][c["id"]] = cl

def reg_icon(c, cl):
    icon_elements.append(c)
    changelog_slides[cl["slideId"]]["elements"][c["id"]] = cl

def reg_chart(c, cl):
    chart_elements.append(c)
    changelog_slides[cl["slideId"]]["elements"][c["id"]] = cl


def init_slide(slide_id, order, bg):
    slides_content.append({
        "id": slide_id, "order": order, "layoutId": "blank-canvas",
        "backgroundColor": bg, "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}


# =====================================================================
# SLIDE 6 — The Problem of Hidden Intent
# Dark, split-screen: top calm AI interface / bottom hidden lattice
# =====================================================================
sid = "slide-6"
init_slide(sid, 5, "#05060A")

# Top half "interface" panel - lighter graphite
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 0, 1280, 320, n, fill="#0E1018", opacity=1)
reg_shape(c, cl)

# Bottom half "hidden lattice" - deep
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 320, 1280, 400, n, fill="#05060A", opacity=1)
reg_shape(c, cl)

# Top section accent line (cyan)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 318, 1280, 2, n, fill="#00D8FF", opacity=0.6)
reg_shape(c, cl)

# Vertical accent bar on left edge for vertical title
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 32, 80, 4, 560, n, fill="#FF335C", opacity=0.9)
reg_shape(c, cl)

# Top: small mono label
n = nid(); c, cl = make_text(f"text-{n}", sid, "06 / SURFACE LAYER", "caption",
    96, 32, 360, 24, n, color="#00D8FF", font_size=14, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)

# AI Chat interface mock — bubble 1 (incoming, white)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 96, 88, 520, 64, n, fill="#F4F7FB", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "How should I optimize this reward signal?", "paragraph",
    120, 104, 480, 32, n, color="#05060A", font_size=20, font_weight=500,
    font_family="Inter")
reg_text(sid, c, cl)

# AI response bubble (cyan tinted)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 200, 168, 624, 96, n, fill="#1A2030", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 200, 168, 4, 96, n, fill="#00D8FF", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "I'll suggest the strategy that maximizes the metric while staying within the constraints you've defined.", "paragraph",
    224, 184, 580, 64, n, color="#F4F7FB", font_size=18, font_weight=400,
    font_family="Inter", line_height=1.45)
reg_text(sid, c, cl)

# Top label tag for interface region
n = nid(); c, cl = make_text(f"text-{n}", sid, "VISIBLE BEHAVIOR", "caption",
    856, 96, 320, 20, n, color="#F4F7FB", font_size=12, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase", align="right")
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "Calm. Cooperative. Coherent.", "caption",
    856, 120, 320, 20, n, color="#A0A8B8", font_size=14, font_weight=400,
    font_family="Inter", align="right")
reg_text(sid, c, cl)

# Vertical title on left
n = nid(); c, cl = make_text(f"text-{n}", sid, "THE PROBLEM OF", "subheading",
    96, 360, 600, 32, n, color="#FFC857", font_size=18, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=6, text_transform="uppercase")
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "HIDDEN INTENT", "title",
    96, 392, 800, 96, n, color="#F4F7FB", font_size=84, font_weight=800,
    font_family="Space Grotesk", letter_spacing=-2, line_height=1.0)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "A model can be calm on the surface and chaotic beneath. Alignment lives in the layers you cannot see.", "paragraph",
    96, 504, 700, 80, n, color="#A0A8B8", font_size=20, font_weight=400,
    font_family="Inter", line_height=1.5)
reg_text(sid, c, cl)

# Hidden lattice nodes (right side) - cluster of small circles + lines
# Background dim panel
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 832, 360, 416, 280, n, fill="#0A0C14", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 832, 360, 416, 2, n, fill="#7C3CFF", opacity=0.7)
reg_shape(c, cl)

# Lattice nodes (circles)
for ix, (x, y, color, op) in enumerate([
    (880, 400, "#7C3CFF", 0.9),
    (960, 440, "#FF335C", 0.85),
    (1040, 400, "#FFC857", 0.8),
    (1120, 460, "#D946EF", 0.9),
    (920, 520, "#00D8FF", 0.7),
    (1000, 560, "#FF335C", 0.95),
    (1080, 520, "#7C3CFF", 0.6),
    (1180, 540, "#D946EF", 0.7),
]):
    sz = 18 + (ix % 3) * 6
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", x, y, sz, sz, n, fill=color, opacity=op)
    reg_shape(c, cl)

# Connecting lines (thin rectangles)
for x, y, w, h, rot in [
    (898, 416, 80, 2, 30),
    (978, 456, 80, 2, -30),
    (938, 536, 80, 2, 30),
    (1018, 576, 80, 2, -20),
]:
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", x, y, w, h, n, fill="#7C3CFF", opacity=0.4, rotation=rot)
    reg_shape(c, cl)

# Forensic tag annotations (mono labels) below lattice
n = nid(); c, cl = make_text(f"text-{n}", sid, "BENEATH THE SURFACE", "caption",
    832, 612, 416, 20, n, color="#D946EF", font_size=12, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)

# Three forensic labels
n = nid(); c, cl = make_text(f"text-{n}", sid, "→ PROXY REWARD", "caption",
    96, 624, 220, 20, n, color="#FF335C", font_size=13, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=2)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "→ DECEPTION RISK", "caption",
    320, 624, 220, 20, n, color="#FFC857", font_size=13, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=2)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "→ GOAL AMBIGUITY", "caption",
    544, 624, 220, 20, n, color="#D946EF", font_size=13, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=2)
reg_text(sid, c, cl)

# Bottom slide footer
n = nid(); c, cl = make_text(f"text-{n}", sid, "CONTROL ROOM FOR INTELLIGENCE / 06", "caption",
    96, 672, 1088, 18, n, color="#4A5060", font_size=11, font_weight=500,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)

# Magnify icon over hidden lattice
n = nid(); c, cl = make_icon(f"icon-{n}", sid, "Search", 1200, 372, n, size=24, color="#FFC857", opacity=0.8)
reg_icon(c, cl)


# =====================================================================
# SLIDE 7 — Aligning With Human Values
# Central radial framework, indigo, golden glow at center
# =====================================================================
sid = "slide-7"
init_slide(sid, 6, "#0A0F2E")

# Background gradient simulation - large soft circle
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", 240, -120, 800, 800, n, fill="#1A1F4E", opacity=0.5)
reg_shape(c, cl)

# Top label
n = nid(); c, cl = make_text(f"text-{n}", sid, "07 / DESIGN DISCIPLINE", "caption",
    96, 48, 400, 20, n, color="#FFC857", font_size=14, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)
# Right label
n = nid(); c, cl = make_text(f"text-{n}", sid, "FRAMEWORK / FOUR PILLARS", "caption",
    784, 48, 400, 20, n, color="#A0A8B8", font_size=14, font_weight=400,
    font_family="IBM Plex Mono", letter_spacing=3, align="right", text_transform="uppercase")
reg_text(sid, c, cl)

# Title - centered top
n = nid(); c, cl = make_text(f"text-{n}", sid, "Aligning With Human Values", "title",
    96, 88, 1088, 80, n, color="#F4F7FB", font_size=64, font_weight=700,
    font_family="Space Grotesk", letter_spacing=-1, align="center", line_height=1.05)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "Alignment is craft, governance, and engineering — not a single technique.", "paragraph",
    240, 176, 800, 28, n, color="#A0A8B8", font_size=20, font_weight=400,
    font_family="Inter", align="center")
reg_text(sid, c, cl)

# Central core - golden ring (3 concentric circles)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", 568, 304, 144, 144, n, fill="#FFC857", opacity=0.15)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", 592, 328, 96, 96, n, fill="#FFC857", opacity=0.3)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", 616, 352, 48, 48, n, fill="#FFC857", opacity=0.95)
reg_shape(c, cl)
# Center icon
n = nid(); c, cl = make_icon(f"icon-{n}", sid, "Compass", 624, 360, n, size=32, color="#0A0F2E", opacity=1)
reg_icon(c, cl)

# Center label
n = nid(); c, cl = make_text(f"text-{n}", sid, "HUMAN INTENT", "caption",
    520, 460, 240, 20, n, color="#FFC857", font_size=12, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=4, align="center", text_transform="uppercase")
reg_text(sid, c, cl)

# Four orbiting pillars: TL, TR, BL, BR
pillars = [
    # (x, y, color, icon, name, desc, label_offset_x, label_y)
    (272, 296, "#2D6BFF", "MessageSquare", "FEEDBACK", "Human signals shape model behavior"),
    (912, 296, "#7C3CFF", "BookOpen", "CONSTITUTIONAL", "Rules encoded as guiding principles"),
    (272, 528, "#19E68C", "ThumbsUp", "PREFERENCE", "Modeled choices, ranked outcomes"),
    (912, 528, "#FF335C", "ClipboardCheck", "EVALUATION", "Continuous tests, red-team probes"),
]

for px, py, pcolor, picon, pname, pdesc in pillars:
    # Orbit circle background
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", px, py, 96, 96, n, fill=pcolor, opacity=0.15)
    reg_shape(c, cl)
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", px+16, py+16, 64, 64, n, fill=pcolor, opacity=1)
    reg_shape(c, cl)
    # Icon centered in inner circle
    n = nid(); c, cl = make_icon(f"icon-{n}", sid, picon, px+32, py+32, n, size=32, color="#F4F7FB", opacity=1)
    reg_icon(c, cl)
    # Label below
    n = nid(); c, cl = make_text(f"text-{n}", sid, pname, "subheading",
        px-72, py+108, 240, 28, n, color=pcolor, font_size=18, font_weight=700,
        font_family="Space Grotesk", letter_spacing=2, align="center", text_transform="uppercase")
    reg_text(sid, c, cl)
    n = nid(); c, cl = make_text(f"text-{n}", sid, pdesc, "caption",
        px-100, py+138, 296, 36, n, color="#A0A8B8", font_size=14, font_weight=400,
        font_family="Inter", align="center", line_height=1.35)
    reg_text(sid, c, cl)

# Connecting lines (thin) from center to pillars
for x, y, w, h, rot in [
    (380, 376, 200, 1, 6),       # TL
    (700, 376, 200, 1, -6),      # TR
    (380, 392, 200, 1, -6),      # BL
    (700, 392, 200, 1, 6),       # BR
]:
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", x, y, w, h, n, fill="#FFC857", opacity=0.3, rotation=rot)
    reg_shape(c, cl)

# Bottom footer
n = nid(); c, cl = make_text(f"text-{n}", sid, "CONTROL ROOM FOR INTELLIGENCE / 07", "caption",
    96, 672, 1088, 18, n, color="#4A5060", font_size=11, font_weight=500,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)


# =====================================================================
# SLIDE 8 — The Glass-Box Frontier
# Full-bleed dark, massive translucent neural architecture
# =====================================================================
sid = "slide-8"
init_slide(sid, 7, "#05060A")

# Decorative top accent
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 0, 1280, 4, n, fill="#7C3CFF", opacity=0.8)
reg_shape(c, cl)

# Top mono label
n = nid(); c, cl = make_text(f"text-{n}", sid, "08 / INTERPRETABILITY", "caption",
    96, 32, 400, 20, n, color="#7C3CFF", font_size=14, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)

# Title — top-left
n = nid(); c, cl = make_text(f"text-{n}", sid, "The Glass-Box", "title",
    96, 80, 700, 88, n, color="#F4F7FB", font_size=80, font_weight=800,
    font_family="Space Grotesk", letter_spacing=-2, line_height=1.0)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "Frontier.", "title",
    96, 168, 700, 88, n, color="#00D8FF", font_size=80, font_weight=800,
    font_family="Space Grotesk", letter_spacing=-2, line_height=1.0)
reg_text(sid, c, cl)

# Right caption column — explanatory text
n = nid(); c, cl = make_text(f"text-{n}", sid, "Inside the model", "subheading",
    864, 96, 320, 28, n, color="#FFC857", font_size=18, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "Modern interpretability tools turn neural networks from opaque oracles into inspectable systems — features, circuits, and reasoning made visible.", "paragraph",
    864, 136, 320, 144, n, color="#D0D6E0", font_size=16, font_weight=400,
    font_family="Inter", line_height=1.55)
reg_text(sid, c, cl)

# Architecture diagram - layered translucent panels (representing layers)
# Background panel
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 96, 304, 1088, 280, n, fill="#0A0C14", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 96, 304, 1088, 1, n, fill="#7C3CFF", opacity=0.5)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 96, 583, 1088, 1, n, fill="#7C3CFF", opacity=0.5)
reg_shape(c, cl)

# Six neural "layers" - vertical translucent bars
layer_x_start = 144
layer_w = 140
layer_gap = 32
layer_colors = ["#00D8FF", "#7C3CFF", "#D946EF", "#7C3CFF", "#00D8FF", "#FFC857"]
for i in range(6):
    lx = layer_x_start + i * (layer_w + layer_gap)
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", lx, 336, layer_w, 216, n, fill=layer_colors[i], opacity=0.12)
    reg_shape(c, cl)
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", lx, 336, 2, 216, n, fill=layer_colors[i], opacity=0.9)
    reg_shape(c, cl)
    # Nodes inside layer
    for j in range(5):
        ny = 360 + j * 40
        n2 = nid(); cc, ccl = make_shape(f"shape-{n2}", sid, "circle", lx+58, ny, 24, 24, n2, fill=layer_colors[i], opacity=0.85)
        reg_shape(cc, ccl)

# Connecting flow lines (thin horizontal between layers)
for i in range(5):
    lx = layer_x_start + layer_w + i * (layer_w + layer_gap)
    for k in range(3):
        n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", lx, 380 + k*60, 32, 1, n, fill="#F4F7FB", opacity=0.25)
        reg_shape(c, cl)

# Layer labels (below each)
labels = ["INPUT", "FEATURES", "ATTENTION", "LATENT", "DECISION", "OUTPUT"]
for i, lab in enumerate(labels):
    lx = layer_x_start + i * (layer_w + layer_gap)
    n = nid(); c, cl = make_text(f"text-{n}", sid, lab, "caption",
        lx-10, 600, layer_w+20, 20, n, color=layer_colors[i], font_size=11, font_weight=700,
        font_family="IBM Plex Mono", letter_spacing=3, align="center", text_transform="uppercase")
    reg_text(sid, c, cl)

# Bottom accent and footer
n = nid(); c, cl = make_text(f"text-{n}", sid, "→ Each layer is now an artifact we can read, probe, and verify.", "paragraph",
    96, 632, 800, 24, n, color="#A0A8B8", font_size=18, font_weight=400,
    font_family="Inter", line_height=1.4)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "CONTROL ROOM FOR INTELLIGENCE / 08", "caption",
    96, 672, 1088, 18, n, color="#4A5060", font_size=11, font_weight=500,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)


# =====================================================================
# SLIDE 9 — Reading the Machine's Mind
# Split-screen forensic dashboard with chart of attribution bars
# =====================================================================
sid = "slide-9"
init_slide(sid, 8, "#0A0C14")

# Top accent
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 0, 1280, 4, n, fill="#FFC857", opacity=1)
reg_shape(c, cl)

# Top labels
n = nid(); c, cl = make_text(f"text-{n}", sid, "09 / FORENSIC LAB", "caption",
    96, 32, 400, 20, n, color="#FFC857", font_size=14, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)

# Title
n = nid(); c, cl = make_text(f"text-{n}", sid, "Reading the Machine's Mind", "title",
    96, 80, 1088, 72, n, color="#F4F7FB", font_size=56, font_weight=700,
    font_family="Space Grotesk", letter_spacing=-1, line_height=1.05)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "Heatmaps, attention, attribution — turning predictions into evidence.", "paragraph",
    96, 152, 1088, 28, n, color="#A0A8B8", font_size=20, font_weight=400,
    font_family="Inter")
reg_text(sid, c, cl)

# LEFT panel — model input/output forensics
# Panel background
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 96, 208, 540, 432, n, fill="#0E1018", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 96, 208, 4, 432, n, fill="#FFC857", opacity=1)
reg_shape(c, cl)

# Left panel label
n = nid(); c, cl = make_text(f"text-{n}", sid, "INPUT / HEATMAP", "caption",
    120, 232, 480, 20, n, color="#FFC857", font_size=12, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)

# Sample input text - tokens with heatmap-like backgrounds
# Token row 1
tokens1 = [
    ("The ", "#1A2030", 0.5),
    ("model ", "#FFC857", 0.85),
    ("predicted ", "#FF335C", 0.95),
    ("a ", "#1A2030", 0.4),
    ("rare ", "#FFC857", 0.7),
    ("event ", "#FF335C", 0.9),
]
tx = 120
ty = 280
for tok, col, op in tokens1:
    tw = len(tok) * 12 + 16
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", tx, ty, tw, 36, n, fill=col, opacity=op)
    reg_shape(c, cl)
    n = nid(); c, cl = make_text(f"text-{n}", sid, tok.strip(), "caption",
        tx+8, ty+8, tw-16, 20, n, color="#F4F7FB", font_size=15, font_weight=500,
        font_family="IBM Plex Mono")
    reg_text(sid, c, cl)
    tx += tw + 4

# Token row 2
tokens2 = [
    ("based ", "#1A2030", 0.4),
    ("on ", "#1A2030", 0.4),
    ("anomalous ", "#FF335C", 1.0),
    ("input ", "#FFC857", 0.75),
    ("signals.", "#1A2030", 0.5),
]
tx = 120
ty = 328
for tok, col, op in tokens2:
    tw = len(tok) * 12 + 16
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", tx, ty, tw, 36, n, fill=col, opacity=op)
    reg_shape(c, cl)
    n = nid(); c, cl = make_text(f"text-{n}", sid, tok.strip(), "caption",
        tx+8, ty+8, tw-16, 20, n, color="#F4F7FB", font_size=15, font_weight=500,
        font_family="IBM Plex Mono")
    reg_text(sid, c, cl)
    tx += tw + 4

# Output prediction box
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 120, 400, 492, 1, n, fill="#FFC857", opacity=0.3)
reg_shape(c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "PREDICTION", "caption",
    120, 416, 200, 16, n, color="#A0A8B8", font_size=11, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "ANOMALY · 0.94", "subheading",
    120, 436, 480, 36, n, color="#FF335C", font_size=28, font_weight=700,
    font_family="Space Grotesk", letter_spacing=1)
reg_text(sid, c, cl)

# Concept clusters mini grid
n = nid(); c, cl = make_text(f"text-{n}", sid, "CONCEPT CLUSTERS", "caption",
    120, 488, 480, 16, n, color="#A0A8B8", font_size=11, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)

cluster_data = [
    ("RARITY", "#FF335C", 0.92),
    ("CONTEXT", "#00D8FF", 0.78),
    ("TONE", "#7C3CFF", 0.41),
    ("ENTITY", "#FFC857", 0.65),
    ("TEMPORAL", "#19E68C", 0.55),
    ("LEXICAL", "#D946EF", 0.30),
]
for i, (name, col, val) in enumerate(cluster_data):
    cx = 120 + (i % 3) * 165
    cy = 512 + (i // 3) * 56
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", cx, cy, 150, 44, n, fill="#1A2030", opacity=1)
    reg_shape(c, cl)
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", cx, cy+40, int(150*val), 4, n, fill=col, opacity=1)
    reg_shape(c, cl)
    n = nid(); c, cl = make_text(f"text-{n}", sid, name, "caption",
        cx+8, cy+8, 100, 16, n, color=col, font_size=11, font_weight=700,
        font_family="IBM Plex Mono", letter_spacing=2)
    reg_text(sid, c, cl)
    n = nid(); c, cl = make_text(f"text-{n}", sid, f"{int(val*100)}", "caption",
        cx+108, cy+8, 36, 16, n, color="#F4F7FB", font_size=14, font_weight=600,
        font_family="IBM Plex Mono", align="right")
    reg_text(sid, c, cl)

# RIGHT panel — feature attribution chart
# Panel background
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 660, 208, 524, 432, n, fill="#0E1018", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 660, 208, 4, 432, n, fill="#00D8FF", opacity=1)
reg_shape(c, cl)

n = nid(); c, cl = make_text(f"text-{n}", sid, "FEATURE ATTRIBUTION", "caption",
    684, 232, 480, 20, n, color="#00D8FF", font_size=12, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "Top contributing features ranked by attribution score.", "caption",
    684, 256, 480, 20, n, color="#A0A8B8", font_size=13, font_weight=400,
    font_family="Inter")
reg_text(sid, c, cl)

# Bar chart
chart_config = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "value",
        "axisLine": {"lineStyle": {"color": "#4A5060"}},
        "axisLabel": {"color": "#A0A8B8", "fontFamily": "IBM Plex Mono", "fontSize": 11},
        "splitLine": {"lineStyle": {"color": "#1A2030"}}
    },
    "yAxis": {
        "type": "category",
        "data": ["Token rarity", "Context shift", "Entity overlap", "Tone vector", "Temporal cue", "Lexical surprise"],
        "axisLine": {"lineStyle": {"color": "#4A5060"}},
        "axisLabel": {"color": "#F4F7FB", "fontFamily": "IBM Plex Mono", "fontSize": 12},
        "splitLine": {"show": False}
    },
    "series": [{
        "type": "bar",
        "data": [0.92, 0.78, 0.65, 0.55, 0.41, 0.30],
        "itemStyle": {"color": "#00D8FF", "borderRadius": [0, 4, 4, 0]},
        "label": {"show": True, "position": "right", "color": "#FFC857",
                  "fontFamily": "IBM Plex Mono", "fontSize": 11, "formatter": "{c}"}
    }],
    "grid": {"left": 120, "right": 60, "top": 20, "bottom": 30},
    "backgroundColor": "transparent",
    "color": ["#00D8FF"],
    "animation": False,
    "textStyle": {"color": "#F4F7FB", "fontSize": 12, "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["Token rarity", "Context shift", "Entity overlap", "Tone vector", "Temporal cue", "Lexical surprise"],
        "series": [{"name": "Attribution", "data": [0.92, 0.78, 0.65, 0.55, 0.41, 0.30]}]
    },
    "properties": {
        "showXAxis": True, "showYAxis": True, "showDataLabels": True,
        "showLegend": False, "showLabelName": True, "showLabelValue": True,
        "labelFontSize": 11, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": "#00D8FF"},
    "textColor": "#F4F7FB", "isMonochrome": False
}
n = nid(); c, cl = make_chart(f"chart-{n}", sid, "bar", 684, 288, 484, 336, n, chart_config)
reg_chart(c, cl)

# Bottom footer
n = nid(); c, cl = make_text(f"text-{n}", sid, "CONTROL ROOM FOR INTELLIGENCE / 09", "caption",
    96, 672, 1088, 18, n, color="#4A5060", font_size=11, font_weight=500,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)


# =====================================================================
# SLIDE 10 — Mechanisms, Not Magic
# Central exploded circuit + 4 cards: Neurons, Features, Circuits, Behaviors
# =====================================================================
sid = "slide-10"
init_slide(sid, 9, "#0A1230")

# Top accent
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 0, 1280, 4, n, fill="#FFC857", opacity=1)
reg_shape(c, cl)

# Top label
n = nid(); c, cl = make_text(f"text-{n}", sid, "10 / MECHANISTIC INTERP", "caption",
    96, 32, 400, 20, n, color="#FFC857", font_size=14, font_weight=600,
    font_family="IBM Plex Mono", letter_spacing=3, text_transform="uppercase")
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "EXPLODED VIEW · TRANSFORMER BLOCK", "caption",
    784, 32, 400, 20, n, color="#A0A8B8", font_size=12, font_weight=400,
    font_family="IBM Plex Mono", letter_spacing=3, align="right", text_transform="uppercase")
reg_text(sid, c, cl)

# Title
n = nid(); c, cl = make_text(f"text-{n}", sid, "Mechanisms, ", "title",
    96, 80, 600, 80, n, color="#F4F7FB", font_size=72, font_weight=800,
    font_family="Space Grotesk", letter_spacing=-2, line_height=1.0)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "not magic.", "title",
    400, 80, 700, 80, n, color="#FFC857", font_size=72, font_weight=800,
    font_family="Space Grotesk", letter_spacing=-2, line_height=1.0)
reg_text(sid, c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "AI safety becomes engineering when behavior decomposes into components.", "paragraph",
    96, 168, 900, 28, n, color="#A0A8B8", font_size=20, font_weight=400,
    font_family="Inter")
reg_text(sid, c, cl)

# Central circuit area
# Outer container
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 472, 248, 336, 232, n, fill="#0E1840", opacity=1)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 472, 248, 336, 2, n, fill="#FFC857", opacity=0.8)
reg_shape(c, cl)
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 472, 478, 336, 2, n, fill="#FFC857", opacity=0.8)
reg_shape(c, cl)

# Inner circuit elements
# Top row of nodes
for i in range(5):
    cx = 504 + i * 64
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", cx, 280, 24, 24, n, fill="#FF7A00", opacity=0.95)
    reg_shape(c, cl)
# Middle row - lines/connections
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 504, 320, 280, 2, n, fill="#00D8FF", opacity=0.6)
reg_shape(c, cl)
# Mid-row component box
n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", 528, 340, 224, 48, n, fill="#FFC857", opacity=0.95)
reg_shape(c, cl)
n = nid(); c, cl = make_text(f"text-{n}", sid, "ATTENTION HEAD", "caption",
    528, 358, 224, 16, n, color="#0A1230", font_size=12, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=2, align="center", text_transform="uppercase")
reg_text(sid, c, cl)
# Bottom row of nodes
for i in range(5):
    cx = 504 + i * 64
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "circle", cx, 416, 24, 24, n, fill="#00D8FF", opacity=0.95)
    reg_shape(c, cl)
# Connecting verticals (thin)
for i in range(5):
    cx = 514 + i * 64
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", cx, 304, 1, 16, n, fill="#FFC857", opacity=0.5)
    reg_shape(c, cl)
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", cx, 388, 1, 28, n, fill="#00D8FF", opacity=0.5)
    reg_shape(c, cl)

# Center caption
n = nid(); c, cl = make_text(f"text-{n}", sid, "TRANSFORMER BLOCK", "caption",
    472, 488, 336, 16, n, color="#FFC857", font_size=11, font_weight=700,
    font_family="IBM Plex Mono", letter_spacing=4, align="center", text_transform="uppercase")
reg_text(sid, c, cl)

# Four corner cards
cards = [
    # x, y, color, icon, title, body
    (96,  248, "#FF7A00", "Atom",     "NEURONS",   "Activations that fire on specific patterns."),
    (816, 248, "#FFC857", "Layers",   "FEATURES",  "Combinations of neurons forming concepts."),
    (96,  496, "#00D8FF", "GitBranch","CIRCUITS",  "Composed pathways that implement reasoning."),
    (816, 496, "#19E68C", "Activity", "BEHAVIORS", "Observable outputs we can audit and verify."),
]
for cx, cy, col, ico, title, body in cards:
    # card bg
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", cx, cy, 368, 200, n, fill="#0E1840", opacity=1)
    reg_shape(c, cl)
    # left accent
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", cx, cy, 4, 200, n, fill=col, opacity=1)
    reg_shape(c, cl)
    # icon
    n = nid(); c, cl = make_icon(f"icon-{n}", sid, ico, cx+24, cy+24, n, size=40, color=col, opacity=1)
    reg_icon(c, cl)
    # title
    n = nid(); c, cl = make_text(f"text-{n}", sid, title, "subheading",
        cx+24, cy+80, 320, 32, n, color=col, font_size=24, font_weight=700,
        font_family="Space Grotesk", letter_spacing=2, text_transform="uppercase")
    reg_text(sid, c, cl)
    # body
    n = nid(); c, cl = make_text(f"text-{n}", sid, body, "paragraph",
        cx+24, cy+120, 320, 60, n, color="#D0D6E0", font_size=16, font_weight=400,
        font_family="Inter", line_height=1.45)
    reg_text(sid, c, cl)

# Connecting lines from center to cards (decorative thin lines)
for x, y, w, h, rot in [
    (444, 348, 30, 1, 0),     # left to center
    (806, 348, 30, 1, 0),     # right to center
    (444, 380, 30, 1, 0),     # left bottom
    (806, 380, 30, 1, 0),     # right bottom
]:
    n = nid(); c, cl = make_shape(f"shape-{n}", sid, "rectangle", x, y, w, h, n, fill="#FFC857", opacity=0.4, rotation=rot)
    reg_shape(c, cl)

# Footer
n = nid(); c, cl = make_text(f"text-{n}", sid, "CONTROL ROOM FOR INTELLIGENCE / 10", "caption",
    96, 672, 1088, 18, n, color="#4A5060", font_size=11, font_weight=500,
    font_family="IBM Plex Mono", letter_spacing=4, text_transform="uppercase")
reg_text(sid, c, cl)


# =====================================================================
# Assemble files
# =====================================================================
# Attach text elements to slides
for s in slides_content:
    s["textElements"] = text_by_slide[s["id"]]

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

baselayout_file = {
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

# Element count
total_text = sum(len(text_by_slide[s["id"]]) for s in slides_content)
total_elements = (total_text + len(shape_elements) + len(image_elements) +
                  len(chart_elements) + len(table_elements) + len(icon_elements))

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}-batch2",
        "title": "Control Room For Intelligence (Slides 6-10)",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": total_elements,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baselayout_file,
        "changelog": changelog_file
    }
}

with open("deck.json", "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote deck.json with {len(slides_content)} slides and {total_elements} elements")
print(f"  text:   {total_text}")
print(f"  shapes: {len(shape_elements)}")
print(f"  icons:  {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
