import json, time

NOW = int(time.time() * 1000)

# ---------- Counters ----------
COUNTER = 0
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#D8DEE9", font_size=None, font_weight=None, line_height=None,
              font_family="Inter", text_align="left", letter_spacing=0,
              text_transform="none", font_style="normal"):
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
               fill="#151B2E", stroke=None, stroke_width=0, opacity=1):
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
              size=48, color="#00D4FF", opacity=1, width=None, height=None):
    w = width if width is not None else size
    h = height if height is not None else size
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


# ---------- Storage ----------
text_by_slide = {}
image_elements = []
shape_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}

def reg_slide(slide_id):
    text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

def add_text(sid, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, sid, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_by_slide[sid].append(c)
    changelog_slides[sid]["elements"][tid] = cl
    return tid

def add_shape(sid, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    eid = f"shape-{n}"
    c, cl = make_shape(eid, sid, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[sid]["elements"][eid] = cl
    return eid

def add_image(sid, src, x, y, w, h, **kwargs):
    n = next_id()
    eid = f"image-{n}"
    c, cl = make_image(eid, sid, src, x, y, w, h, n, NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[sid]["elements"][eid] = cl
    return eid

def add_icon(sid, icon_name, x, y, **kwargs):
    n = next_id()
    eid = f"icon-{n}"
    c, cl = make_icon(eid, sid, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[sid]["elements"][eid] = cl
    return eid


# ============================================================
# SLIDE 1 — Velocity Has a Shape (cinematic hero opening)
# ============================================================
sid = "slide-1"
reg_slide(sid)

# Full-bleed cinematic background image (light trails / data terrain)
add_image(sid,
    "https://images.pexels.com/photos/2387793/pexels-photo-2387793.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 1280, 720, is_background=True, opacity=0.55)

# Dark vignette overlay
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#090A0F", opacity=0.55)

# Bottom-left gradient panel
add_shape(sid, "rectangle", 0, 420, 760, 300, fill="#090A0F", opacity=0.6)

# Diagonal optimization light trail (thin glowing line)
add_shape(sid, "line", 120, 200, 1040, 4, fill="#00D4FF", stroke="#00D4FF",
          stroke_width=2, opacity=0.85)
# Secondary thinner trail
add_shape(sid, "line", 180, 280, 920, 2, fill="#7C3AED", stroke="#7C3AED",
          stroke_width=1, opacity=0.6)

# Convergence point (small circle)
add_shape(sid, "circle", 1124, 188, 28, 28, fill="#FFB020", opacity=0.95)
add_shape(sid, "circle", 1116, 180, 44, 44, fill="#FFB020", opacity=0.25)

# Top-left mono technical label
add_text(sid, "// FAST.OPTIMIZATION.TEST  //  v1.0", "caption",
         48, 48, 600, 22,
         font_family="JetBrains Mono", font_size=12, font_weight=500,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")

# Top-right test marker
add_text(sid, "RUN ID — 0xA1F4 · 25.05.2026", "caption",
         872, 48, 360, 22,
         font_family="JetBrains Mono", font_size=12, font_weight=500,
         color="#A6A29A", letter_spacing=2, text_align="right",
         text_transform="uppercase")

# Thin divider line
add_shape(sid, "rectangle", 48, 84, 1184, 1, fill="#D8DEE9", opacity=0.18)

# Section eyebrow
add_text(sid, "CHAPTER 01 — VELOCITY", "caption",
         48, 440, 400, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=600,
         color="#00D4FF", letter_spacing=4, text_transform="uppercase")

# Hero title (oversized, condensed editorial)
add_text(sid, "Velocity has a shape.", "title",
         48, 472, 900, 110,
         font_family="Neue Haas Grotesk Display", font_size=92, font_weight=700,
         color="#F7F8FA", line_height=1.0, letter_spacing=-2)

# Subtitle / italic editorial line
add_text(sid, "Speed, precision, and performance — measured under pressure.",
         "subtitle", 48, 590, 800, 40,
         font_family="Inter", font_size=22, font_weight=400,
         color="#D8DEE9", letter_spacing=0)

# Bottom-right mono telemetry block
add_text(sid, "LAT  04.21ms\nTHRU 982k/s\nERR  0.001%", "caption",
         1024, 600, 220, 64,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#22C55E", line_height=1.6, text_align="right")


# ============================================================
# SLIDE 2 — The Test Bench (editorial blueprint + metric cards)
# ============================================================
sid = "slide-2"
reg_slide(sid)

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#090A0F")

# Faint blueprint grid (vertical lines)
for gx in range(96, 1280, 96):
    add_shape(sid, "line", gx, 0, 1, 720, fill="#D8DEE9",
              stroke="#D8DEE9", stroke_width=1, opacity=0.04)
# horizontal grid
for gy in range(72, 720, 72):
    add_shape(sid, "line", 0, gy, 1280, 1, fill="#D8DEE9",
              stroke="#D8DEE9", stroke_width=1, opacity=0.04)

# Top eyebrow
add_text(sid, "// 02 — INSTRUMENTATION", "caption",
         48, 48, 400, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=600,
         color="#00D4FF", letter_spacing=4, text_transform="uppercase")

# Section title
add_text(sid, "The test bench.", "title",
         48, 80, 800, 80,
         font_family="Neue Haas Grotesk Display", font_size=64, font_weight=700,
         color="#F7F8FA", line_height=1.05, letter_spacing=-1.5)

# Subtitle
add_text(sid, "A controlled environment where every millisecond is observed, recorded, and challenged.",
         "paragraph", 48, 168, 700, 56,
         font_family="Inter", font_size=18, font_weight=400,
         color="#A6A29A", line_height=1.5)

# LEFT — Blueprint panel
add_shape(sid, "rectangle", 48, 248, 640, 408, fill="#151B2E", opacity=0.85)
# Inner border line
add_shape(sid, "rectangle", 48, 248, 640, 1, fill="#00D4FF", opacity=0.6)

# Blueprint panel header
add_text(sid, "TEST ENVIRONMENT — SCHEMATIC", "caption",
         72, 272, 500, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=600,
         color="#A6A29A", letter_spacing=3, text_transform="uppercase")

# Pipeline boxes: INPUT → OPTIMIZER → EVAL → RESULT
# Box 1 INPUT
add_shape(sid, "rectangle", 80, 360, 130, 80, fill="#090A0F",
          stroke="#00D4FF", stroke_width=1, opacity=0.95)
add_text(sid, "INPUT", "caption", 80, 380, 130, 20,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#00D4FF", text_align="center", letter_spacing=3,
         text_transform="uppercase")
add_text(sid, "workload\n2.4M ops", "caption", 80, 400, 130, 36,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#D8DEE9", text_align="center", line_height=1.5)

# Connector line
add_shape(sid, "line", 210, 400, 28, 2, fill="#00D4FF",
          stroke="#00D4FF", stroke_width=2, opacity=0.7)

# Box 2 OPTIMIZER
add_shape(sid, "rectangle", 238, 360, 130, 80, fill="#090A0F",
          stroke="#7C3AED", stroke_width=1, opacity=0.95)
add_text(sid, "OPTIMIZER", "caption", 238, 380, 130, 20,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#7C3AED", text_align="center", letter_spacing=3,
         text_transform="uppercase")
add_text(sid, "tuner\nv4.7", "caption", 238, 400, 130, 36,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#D8DEE9", text_align="center", line_height=1.5)

# Connector
add_shape(sid, "line", 368, 400, 28, 2, fill="#00D4FF",
          stroke="#00D4FF", stroke_width=2, opacity=0.7)

# Box 3 EVAL
add_shape(sid, "rectangle", 396, 360, 130, 80, fill="#090A0F",
          stroke="#FFB020", stroke_width=1, opacity=0.95)
add_text(sid, "EVAL", "caption", 396, 380, 130, 20,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#FFB020", text_align="center", letter_spacing=3,
         text_transform="uppercase")
add_text(sid, "harness\n12 metrics", "caption", 396, 400, 130, 36,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#D8DEE9", text_align="center", line_height=1.5)

# Connector
add_shape(sid, "line", 526, 400, 28, 2, fill="#00D4FF",
          stroke="#00D4FF", stroke_width=2, opacity=0.7)

# Box 4 RESULT
add_shape(sid, "rectangle", 554, 360, 110, 80, fill="#090A0F",
          stroke="#22C55E", stroke_width=1, opacity=0.95)
add_text(sid, "RESULT", "caption", 554, 380, 110, 20,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#22C55E", text_align="center", letter_spacing=3,
         text_transform="uppercase")
add_text(sid, "pass\nΔ +34%", "caption", 554, 400, 110, 36,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#D8DEE9", text_align="center", line_height=1.5)

# Bottom telemetry sub-line in panel
add_shape(sid, "rectangle", 80, 480, 584, 1, fill="#D8DEE9", opacity=0.15)
add_text(sid, "CPU  ████████░░  82%", "caption",
         80, 500, 280, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#22C55E")
add_text(sid, "GPU  ██████░░░░  61%", "caption",
         80, 524, 280, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#00D4FF")
add_text(sid, "MEM  ████░░░░░░  42%", "caption",
         80, 548, 280, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#FFB020")

add_text(sid, "PIPELINE LATENCY  —  4.21ms p50", "caption",
         80, 600, 584, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=600,
         color="#D8DEE9", letter_spacing=3, text_transform="uppercase")

# RIGHT — Stacked metric cards
# Card spec: 4 cards in 2x2
card_x1, card_x2 = 712, 976
card_y1, card_y2 = 248, 456
card_w, card_h = 256, 192

cards = [
    (card_x1, card_y1, "SPEED",     "4.21",  "ms p50",  "#00D4FF", "Zap"),
    (card_x2, card_y1, "ACCURACY",  "99.7",  "% pass",  "#22C55E", "Target"),
    (card_x1, card_y2, "STABILITY", "0.012", "σ jitter", "#FFB020", "Activity"),
    (card_x2, card_y2, "COST",      "−38",   "% / run", "#7C3AED", "TrendingDown"),
]

for cx, cy, label, value, unit, color, icon in cards:
    add_shape(sid, "rectangle", cx, cy, card_w, card_h, fill="#151B2E", opacity=0.9)
    add_shape(sid, "rectangle", cx, cy, 4, card_h, fill=color, opacity=1)
    add_icon(sid, icon, cx + card_w - 56, cy + 20, size=28, color=color)
    add_text(sid, label, "caption", cx + 24, cy + 24, 200, 18,
             font_family="JetBrains Mono", font_size=11, font_weight=600,
             color="#A6A29A", letter_spacing=3, text_transform="uppercase")
    add_text(sid, value, "title",
             cx + 24, cy + 56, card_w - 48, 80,
             font_family="Neue Haas Grotesk Display", font_size=64, font_weight=700,
             color="#F7F8FA", line_height=1.0, letter_spacing=-2)
    add_text(sid, unit, "caption", cx + 24, cy + 144, 200, 18,
             font_family="JetBrains Mono", font_size=12, font_weight=500,
             color=color, letter_spacing=2)

# Bottom caption
add_text(sid, "All metrics captured under sustained 30-minute load.", "caption",
         48, 672, 600, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2)


# ============================================================
# SLIDE 3 — Finding the Fastest Path
# ============================================================
sid = "slide-3"
reg_slide(sid)

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#090A0F")
# Subtle navy gradient block
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#151B2E", opacity=0.4)

# Top eyebrow
add_text(sid, "// 03 — SEARCH SPACE", "caption",
         48, 48, 400, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=600,
         color="#00D4FF", letter_spacing=4, text_transform="uppercase")

# Title
add_text(sid, "Finding the fastest path.", "title",
         48, 80, 1100, 80,
         font_family="Neue Haas Grotesk Display", font_size=64, font_weight=700,
         color="#F7F8FA", line_height=1.05, letter_spacing=-1.5)

# Subtitle
add_text(sid, "Three candidate routes. One converges. One stalls. One wins.",
         "paragraph", 48, 168, 800, 30,
         font_family="Inter", font_size=18, font_weight=400,
         color="#A6A29A", line_height=1.5)

# Race target circle on right side (the destination)
target_x, target_y = 1100, 360
add_shape(sid, "circle", target_x - 40, target_y - 40, 80, 80,
          fill="#FFB020", opacity=0.18)
add_shape(sid, "circle", target_x - 24, target_y - 24, 48, 48,
          fill="#FFB020", opacity=0.4)
add_shape(sid, "circle", target_x - 10, target_y - 10, 20, 20,
          fill="#FFB020", opacity=1)

# Three routes — represented as horizontal lines with vertical jitter shapes
# Route 1 BASELINE (red, stutters) - top
# Use multiple short lines for jitter feel
add_shape(sid, "line", 48, 248, 1052, 2, fill="#FF4D4D",
          stroke="#FF4D4D", stroke_width=2, opacity=0.4)
# Stutter dots
for sx in [180, 320, 480, 640, 800, 950]:
    add_shape(sid, "circle", sx, 244, 8, 8, fill="#FF4D4D", opacity=0.8)

add_text(sid, "ROUTE A — BASELINE", "caption",
         48, 218, 320, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#FF4D4D", letter_spacing=3, text_transform="uppercase")
add_text(sid, "12.4ms · stalls @ 6 nodes", "caption",
         800, 218, 300, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2, text_align="right")

# Route 2 ACCELERATED (cyan, smooths) - middle
add_shape(sid, "line", 48, 360, 1052, 3, fill="#00D4FF",
          stroke="#00D4FF", stroke_width=3, opacity=0.85)
# Subtle nodes
for sx in [240, 480, 720, 960]:
    add_shape(sid, "circle", sx, 356, 8, 8, fill="#00D4FF", opacity=0.9)

add_text(sid, "ROUTE B — ACCELERATED", "caption",
         48, 330, 320, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#00D4FF", letter_spacing=3, text_transform="uppercase")
add_text(sid, "6.8ms · smooths convergence", "caption",
         800, 330, 300, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2, text_align="right")

# Route 3 OPTIMIZED (green, snaps clean) - bottom
add_shape(sid, "line", 48, 472, 1052, 4, fill="#22C55E",
          stroke="#22C55E", stroke_width=4, opacity=1)
for sx in [320, 640, 960]:
    add_shape(sid, "circle", sx, 468, 10, 10, fill="#22C55E", opacity=1)

add_text(sid, "ROUTE C — OPTIMIZED", "caption",
         48, 442, 320, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#22C55E", letter_spacing=3, text_transform="uppercase")
add_text(sid, "4.21ms · clean lock to target", "caption",
         800, 442, 300, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2, text_align="right")

# Bottom strip — comparative result snapshots
# Divider line
add_shape(sid, "rectangle", 48, 540, 1184, 1, fill="#D8DEE9", opacity=0.15)

# Three snapshot cards
snap_specs = [
    (48,  "BASELINE",     "12.4 ms",  "−0%",       "#FF4D4D"),
    (464, "ACCELERATED",  "6.8 ms",   "−45%",      "#00D4FF"),
    (864, "OPTIMIZED",    "4.21 ms",  "−66%",      "#22C55E"),
]
for sx, label, value, delta, color in snap_specs:
    add_text(sid, label, "caption",
             sx, 564, 180, 18,
             font_family="JetBrains Mono", font_size=11, font_weight=600,
             color="#A6A29A", letter_spacing=3, text_transform="uppercase")
    add_text(sid, value, "title",
             sx, 588, 380, 60,
             font_family="Neue Haas Grotesk Display", font_size=48, font_weight=700,
             color="#F7F8FA", line_height=1.0, letter_spacing=-1)
    add_text(sid, delta, "caption",
             sx, 648, 200, 22,
             font_family="JetBrains Mono", font_size=14, font_weight=600,
             color=color, letter_spacing=1)

# Bottom mono caption
add_text(sid, "convergence trial · n=10,000 · 95% CI", "caption",
         48, 690, 700, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")


# ============================================================
# SLIDE 4 — The Baseline Under Glass
# ============================================================
sid = "slide-4"
reg_slide(sid)

# Background — pure obsidian
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#090A0F")

# Cinematic background image (circuit / glass surface)
add_image(sid,
    "https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 1280, 720, is_background=True, opacity=0.22)

# Dark overlay
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#090A0F", opacity=0.6)

# Top-left technical label
add_text(sid, "// 04 — BASELINE TELEMETRY", "caption",
         48, 48, 400, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=600,
         color="#FFB020", letter_spacing=4, text_transform="uppercase")

# Top-right run identifier
add_text(sid, "RUN 0xA1F4 · STATE: PRE-OPT", "caption",
         800, 48, 432, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=500,
         color="#A6A29A", letter_spacing=3, text_align="right",
         text_transform="uppercase")

# Thin divider
add_shape(sid, "rectangle", 48, 84, 1184, 1, fill="#D8DEE9", opacity=0.18)

# Slide title (small editorial serif top-left)
add_text(sid, "The baseline under glass.", "subtitle",
         48, 112, 700, 50,
         font_family="Canela", font_size=36, font_weight=400,
         color="#F7F8FA", line_height=1.1, font_style="italic", letter_spacing=-0.5)

# Center oversized benchmark number
add_text(sid, "BENCHMARK SCORE", "caption",
         320, 224, 640, 22,
         font_family="JetBrains Mono", font_size=12, font_weight=600,
         color="#A6A29A", letter_spacing=6, text_align="center",
         text_transform="uppercase")

# The huge number itself
add_text(sid, "12.4", "title",
         200, 256, 880, 220,
         font_family="Neue Haas Grotesk Display", font_size=200, font_weight=700,
         color="#F7F8FA", line_height=1.0, letter_spacing=-6, text_align="center")

# Unit beneath
add_text(sid, "ms / op  ·  p50 latency", "caption",
         320, 480, 640, 24,
         font_family="JetBrains Mono", font_size=14, font_weight=500,
         color="#FFB020", letter_spacing=4, text_align="center",
         text_transform="uppercase")

# Decorative thin lines flanking the number
add_shape(sid, "line", 80, 360, 100, 1, fill="#FFB020",
          stroke="#FFB020", stroke_width=1, opacity=0.6)
add_shape(sid, "line", 1100, 360, 100, 1, fill="#FFB020",
          stroke="#FFB020", stroke_width=1, opacity=0.6)

# Side rail of micro-metrics — left rail
left_rail_x = 48
add_shape(sid, "rectangle", left_rail_x, 552, 4, 100, fill="#00D4FF", opacity=0.7)

add_text(sid, "LATENCY", "caption",
         left_rail_x + 16, 552, 200, 16,
         font_family="JetBrains Mono", font_size=10, font_weight=600,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")
add_text(sid, "12.4ms", "heading",
         left_rail_x + 16, 568, 200, 30,
         font_family="IBM Plex Sans", font_size=24, font_weight=600,
         color="#F7F8FA")

add_text(sid, "THROUGHPUT", "caption",
         left_rail_x + 16, 604, 200, 16,
         font_family="JetBrains Mono", font_size=10, font_weight=600,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")
add_text(sid, "412k/s", "heading",
         left_rail_x + 16, 620, 200, 30,
         font_family="IBM Plex Sans", font_size=24, font_weight=600,
         color="#F7F8FA")

# Center bottom rail
mid_x = 480
add_shape(sid, "rectangle", mid_x, 552, 4, 100, fill="#FFB020", opacity=0.7)
add_text(sid, "CPU LOAD", "caption",
         mid_x + 16, 552, 200, 16,
         font_family="JetBrains Mono", font_size=10, font_weight=600,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")
add_text(sid, "82%", "heading",
         mid_x + 16, 568, 200, 30,
         font_family="IBM Plex Sans", font_size=24, font_weight=600,
         color="#F7F8FA")

add_text(sid, "MEMORY", "caption",
         mid_x + 16, 604, 200, 16,
         font_family="JetBrains Mono", font_size=10, font_weight=600,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")
add_text(sid, "6.2 GB", "heading",
         mid_x + 16, 620, 200, 30,
         font_family="IBM Plex Sans", font_size=24, font_weight=600,
         color="#F7F8FA")

# Right rail
right_x = 920
add_shape(sid, "rectangle", right_x, 552, 4, 100, fill="#FF4D4D", opacity=0.8)
add_text(sid, "ERROR RATE", "caption",
         right_x + 16, 552, 200, 16,
         font_family="JetBrains Mono", font_size=10, font_weight=600,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")
add_text(sid, "0.41%", "heading",
         right_x + 16, 568, 200, 30,
         font_family="IBM Plex Sans", font_size=24, font_weight=600,
         color="#FF4D4D")

add_text(sid, "JITTER σ", "caption",
         right_x + 16, 604, 200, 16,
         font_family="JetBrains Mono", font_size=10, font_weight=600,
         color="#A6A29A", letter_spacing=2, text_transform="uppercase")
add_text(sid, "0.084", "heading",
         right_x + 16, 620, 200, 30,
         font_family="IBM Plex Sans", font_size=24, font_weight=600,
         color="#F7F8FA")

# Bottom mono footer
add_text(sid, "calibration cycle 03 · 30-minute sustained load · validated against control set",
         "caption", 48, 690, 1184, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2)


# ============================================================
# SLIDE 5 — Bottlenecks in the Machine
# ============================================================
sid = "slide-5"
reg_slide(sid)

# Background — graphite
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#151B2E")
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#090A0F", opacity=0.55)

# Top eyebrow
add_text(sid, "// 05 — DIAGNOSTIC PASS", "caption",
         48, 48, 400, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=600,
         color="#FF4D4D", letter_spacing=4, text_transform="uppercase")

# Top-right
add_text(sid, "PROFILER · ACTIVE", "caption",
         900, 48, 332, 20,
         font_family="JetBrains Mono", font_size=12, font_weight=500,
         color="#FFB020", letter_spacing=3, text_align="right",
         text_transform="uppercase")

# Divider
add_shape(sid, "rectangle", 48, 84, 1184, 1, fill="#D8DEE9", opacity=0.18)

# Title (top across full width)
add_text(sid, "Bottlenecks in the machine.", "title",
         48, 112, 1184, 80,
         font_family="Neue Haas Grotesk Display", font_size=60, font_weight=700,
         color="#F7F8FA", line_height=1.05, letter_spacing=-1.5)

# Subtitle
add_text(sid, "Where friction hides, performance bleeds. Four hotspots — exposed.",
         "paragraph", 48, 196, 1100, 30,
         font_family="Inter", font_size=18, font_weight=400,
         color="#A6A29A", line_height=1.5)

# LEFT — Architecture map panel
add_shape(sid, "rectangle", 48, 256, 568, 408, fill="#151B2E", opacity=0.85)

# Panel header
add_text(sid, "SYSTEM ARCHITECTURE — HEATMAP", "caption",
         72, 280, 500, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=600,
         color="#A6A29A", letter_spacing=3, text_transform="uppercase")

# Architecture nodes — connected pipeline flow
# Input node
add_shape(sid, "circle", 88, 376, 56, 56, fill="#00D4FF", opacity=0.9)
add_text(sid, "API", "caption", 88, 392, 56, 24,
         font_family="JetBrains Mono", font_size=12, font_weight=700,
         color="#090A0F", text_align="center", letter_spacing=2)

# Connector line
add_shape(sid, "line", 144, 404, 64, 2, fill="#00D4FF",
          stroke="#00D4FF", stroke_width=2, opacity=0.7)

# Cache node (slightly hot)
add_shape(sid, "circle", 208, 376, 56, 56, fill="#FFB020", opacity=0.85)
add_text(sid, "CACHE", "caption", 208, 392, 56, 24,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#090A0F", text_align="center", letter_spacing=2)

# Connector
add_shape(sid, "line", 264, 404, 64, 2, fill="#FFB020",
          stroke="#FFB020", stroke_width=2, opacity=0.7)

# DB node — THE BOTTLENECK (red glow)
add_shape(sid, "circle", 312, 360, 88, 88, fill="#FF4D4D", opacity=0.25)
add_shape(sid, "circle", 320, 368, 72, 72, fill="#FF4D4D", opacity=0.5)
add_shape(sid, "circle", 328, 376, 56, 56, fill="#FF4D4D", opacity=1)
add_text(sid, "DB", "caption", 328, 392, 56, 24,
         font_family="JetBrains Mono", font_size=12, font_weight=700,
         color="#F7F8FA", text_align="center", letter_spacing=2)

# Connector (slow / red)
add_shape(sid, "line", 384, 404, 64, 2, fill="#FF4D4D",
          stroke="#FF4D4D", stroke_width=2, opacity=0.8)

# Worker node
add_shape(sid, "circle", 448, 376, 56, 56, fill="#7C3AED", opacity=0.9)
add_text(sid, "WORK", "caption", 448, 392, 56, 24,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#F7F8FA", text_align="center", letter_spacing=2)

# Connector
add_shape(sid, "line", 504, 404, 60, 2, fill="#7C3AED",
          stroke="#7C3AED", stroke_width=2, opacity=0.7)

# Output
add_shape(sid, "circle", 552, 376, 48, 48, fill="#22C55E", opacity=0.9)
add_text(sid, "OUT", "caption", 552, 388, 48, 22,
         font_family="JetBrains Mono", font_size=11, font_weight=700,
         color="#090A0F", text_align="center", letter_spacing=2)

# Heat callout pointing to DB
add_shape(sid, "line", 356, 460, 1, 56, fill="#FF4D4D",
          stroke="#FF4D4D", stroke_width=1, opacity=0.7)
add_text(sid, "↑ 78% of total latency", "caption",
         200, 524, 320, 20,
         font_family="JetBrains Mono", font_size=11, font_weight=600,
         color="#FF4D4D", letter_spacing=2, text_transform="uppercase",
         text_align="center")

# Pipeline label
add_text(sid, "INPUT → CACHE → DATABASE → WORKER → OUTPUT", "caption",
         72, 568, 520, 18,
         font_family="JetBrains Mono", font_size=10, font_weight=500,
         color="#A6A29A", letter_spacing=3, text_transform="uppercase",
         text_align="center")

# Annotation line
add_shape(sid, "rectangle", 72, 600, 520, 1, fill="#D8DEE9", opacity=0.15)
add_text(sid, "Heat signature concentrated at I/O boundary.", "caption",
         72, 616, 520, 22,
         font_family="Inter", font_size=14, font_weight=400,
         color="#D8DEE9", text_align="center", font_style="italic")

# RIGHT — Stacked profiling cards
right_card_x = 648
right_card_w = 584
card_y_positions = [256, 360, 464, 568]
card_height = 88

profiling = [
    ("Slow queries",       "+8.2ms",  "ORM N+1 on /users",     "#FF4D4D", "Database"),
    ("Render blocking",    "+2.4ms",  "Synchronous bundle",     "#FFB020", "Layers"),
    ("Cache misses",       "+1.6ms",  "TTL window too short",   "#FFB020", "Layers"),
    ("Network waits",      "+1.1ms",  "TLS handshake retries",  "#00D4FF", "Wifi"),
]

for (label, delta, note, color, icon), cy in zip(profiling, card_y_positions):
    # Card background
    add_shape(sid, "rectangle", right_card_x, cy, right_card_w, card_height,
              fill="#151B2E", opacity=0.85)
    # Color bar
    add_shape(sid, "rectangle", right_card_x, cy, 4, card_height, fill=color)
    # Icon
    add_icon(sid, icon, right_card_x + 24, cy + 28, size=32, color=color)
    # Label
    add_text(sid, label, "subheading",
             right_card_x + 76, cy + 16, 380, 28,
             font_family="IBM Plex Sans", font_size=20, font_weight=600,
             color="#F7F8FA")
    # Note
    add_text(sid, note, "caption",
             right_card_x + 76, cy + 48, 380, 22,
             font_family="JetBrains Mono", font_size=12, font_weight=400,
             color="#A6A29A", letter_spacing=1)
    # Delta — right side
    add_text(sid, delta, "heading",
             right_card_x + right_card_w - 140, cy + 24, 120, 40,
             font_family="Neue Haas Grotesk Display", font_size=28, font_weight=700,
             color=color, text_align="right", letter_spacing=-0.5)

# Bottom footer
add_text(sid, "profiler trace · 30s window · sampled @ 1ms resolution",
         "caption", 48, 690, 1184, 18,
         font_family="JetBrains Mono", font_size=11, font_weight=400,
         color="#A6A29A", letter_spacing=2)


# ============================================================
# Build the final JSON envelope
# ============================================================
slide_ids = ["slide-1", "slide-2", "slide-3", "slide-4", "slide-5"]

content_slides = []
for i, sid in enumerate(slide_ids):
    content_slides.append({
        "id": sid,
        "order": i,
        "layoutId": "blank-canvas",
        "backgroundColor": "#090A0F",
        "textElements": text_by_slide[sid]
    })

baseLayout_slides = []
for sid in slide_ids:
    baseLayout_slides.append({
        "id": sid,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    })

content = {
    "slides": content_slides,
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

# Count elements
text_count = sum(len(text_by_slide[s]) for s in slide_ids)
total_elements = (text_count + len(image_elements) + len(shape_elements) +
                  len(chart_elements) + len(table_elements) + len(icon_elements))

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Fast Optimization Test",
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
        "content": content,
        "baseLayout": baseLayout,
        "changelog": changelog
    }
}

OUTFILE = "deck.json"
with open(OUTFILE, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"WROTE {OUTFILE}")
print(f"slides: 5")
print(f"elements: {total_elements}")
print(f"  text: {text_count}")
print(f"  shapes: {len(shape_elements)}")
print(f"  images: {len(image_elements)}")
print(f"  icons: {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
print(f"  tables: {len(table_elements)}")
