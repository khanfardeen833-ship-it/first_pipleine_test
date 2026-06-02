import json, time

NOW = int(time.time() * 1000)

# ID / zIndex counter starting at 300 per batch instruction
COUNTER = 300

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# --- Helpers --------------------------------------------------------------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx,
              color="#D8DEE9", font_size=None, font_weight=None,
              line_height=None, font_family="Space Grotesk",
              text_align="left", letter_spacing=0):
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
        "animationTypewriterMode": "character", "updatedAt": NOW
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx,
               fill="#151B2E", stroke=None, stroke_width=0, opacity=1, rotation=0):
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
              size=64, color="#00D4FF", opacity=1):
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


# --- Containers -----------------------------------------------------------

slides_content = []
slides_baselayout = []
shape_elements = []
icon_elements = []
image_elements = []
chart_elements = []
table_elements = []

changelog_slides = {}

def add_text(slide_id, text, type_, x, y, w, h, **kw):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, **kw)
    # Find the slide in slides_content
    for s in slides_content:
        if s["id"] == slide_id:
            s["textElements"].append(c)
            break
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid

def add_shape(slide_id, shape_type, x, y, w, h, **kw):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, **kw)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid

def add_icon(slide_id, icon_name, x, y, **kw):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, **kw)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


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
    changelog_slides[slide_id] = {"elements": {}}


# --- Palette --------------------------------------------------------------
OBSIDIAN = "#090A0F"
GRAPHITE = "#151B2E"
SILVER   = "#D8DEE9"
WHITE    = "#F7F8FA"
CYAN     = "#00D4FF"
ACCEL    = "#2563FF"
VIOLET   = "#7C3AED"
AMBER    = "#FFB020"
GREEN    = "#22C55E"
WARM     = "#A6A29A"
RED      = "#EF4444"

# =========================================================================
# SLIDE 6 — The Optimization Sprint
# =========================================================================
SID = "slide-6"
init_slide(SID, 0, OBSIDIAN)

# Subtle grid divider lines
add_shape(SID, "rectangle", 96, 96, 1088, 1, fill="#1E2436", stroke="#1E2436")

# Caption / chapter label
add_text(SID, "CHAPTER 06  /  EXECUTION", "caption", 96, 56, 600, 24,
         color=WARM, font_family="JetBrains Mono",
         font_size=12, font_weight=500, letter_spacing=2.4)

# Title
add_text(SID, "The Optimization Sprint", "title", 96, 112, 1088, 80,
         color=WHITE, font_size=72, font_weight=600, line_height=1.05,
         font_family="Space Grotesk", letter_spacing=-1)

# Subtitle / lede
add_text(SID, "Three intervention lanes. Surgical refactors at clock speed.",
         "subheading", 96, 200, 900, 36, color=SILVER, font_size=22,
         font_weight=400, font_family="Inter")

# Lane 1 — CODE PATH
lane_y = 272
# Lane container
add_shape(SID, "rectangle", 96, lane_y, 1088, 112, fill=GRAPHITE, stroke=GRAPHITE)
# Cyan vertical accent
add_shape(SID, "rectangle", 96, lane_y, 4, 112, fill=CYAN, stroke=CYAN)
# Lane label
add_text(SID, "01  CODE PATH", "caption", 120, lane_y + 18, 240, 20,
         color=CYAN, font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2)
add_text(SID, "Refactor hot loops · inline critical functions", "paragraph",
         120, lane_y + 42, 540, 30, color=WHITE, font_size=20,
         font_weight=500, font_family="Inter")
# Before metric
add_text(SID, "412ms", "heading", 720, lane_y + 28, 100, 36, color=WARM,
         font_size=28, font_weight=400, font_family="JetBrains Mono")
add_text(SID, "BEFORE", "caption", 720, lane_y + 68, 100, 16, color=WARM,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)
# Arrow
add_icon(SID, "ArrowRight", 836, lane_y + 32, size=40, color=SILVER)
# After metric
add_text(SID, "088ms", "heading", 900, lane_y + 28, 160, 36, color=GREEN,
         font_size=28, font_weight=600, font_family="JetBrains Mono")
add_text(SID, "AFTER", "caption", 900, lane_y + 68, 160, 16, color=GREEN,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)

# Lane 2 — DATA PATH
lane_y = 400
add_shape(SID, "rectangle", 96, lane_y, 1088, 112, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", 96, lane_y, 4, 112, fill=ACCEL, stroke=ACCEL)
add_text(SID, "02  DATA PATH", "caption", 120, lane_y + 18, 240, 20,
         color=ACCEL, font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2)
add_text(SID, "Index tuning · query batching · column pruning",
         "paragraph", 120, lane_y + 42, 580, 30, color=WHITE, font_size=20,
         font_weight=500, font_family="Inter")
add_text(SID, "1.8s", "heading", 720, lane_y + 28, 100, 36, color=WARM,
         font_size=28, font_weight=400, font_family="JetBrains Mono")
add_text(SID, "BEFORE", "caption", 720, lane_y + 68, 100, 16, color=WARM,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)
add_icon(SID, "ArrowRight", 836, lane_y + 32, size=40, color=SILVER)
add_text(SID, "240ms", "heading", 900, lane_y + 28, 160, 36, color=GREEN,
         font_size=28, font_weight=600, font_family="JetBrains Mono")
add_text(SID, "AFTER", "caption", 900, lane_y + 68, 160, 16, color=GREEN,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)

# Lane 3 — RUNTIME PATH
lane_y = 528
add_shape(SID, "rectangle", 96, lane_y, 1088, 112, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", 96, lane_y, 4, 112, fill=VIOLET, stroke=VIOLET)
add_text(SID, "03  RUNTIME PATH", "caption", 120, lane_y + 18, 240, 20,
         color=VIOLET, font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2)
add_text(SID, "Parallel exec · cache layer · async I/O", "paragraph",
         120, lane_y + 42, 540, 30, color=WHITE, font_size=20,
         font_weight=500, font_family="Inter")
add_text(SID, "920ms", "heading", 720, lane_y + 28, 100, 36, color=WARM,
         font_size=28, font_weight=400, font_family="JetBrains Mono")
add_text(SID, "BEFORE", "caption", 720, lane_y + 68, 100, 16, color=WARM,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)
add_icon(SID, "ArrowRight", 836, lane_y + 32, size=40, color=SILVER)
add_text(SID, "104ms", "heading", 900, lane_y + 28, 160, 36, color=GREEN,
         font_size=28, font_weight=600, font_family="JetBrains Mono")
add_text(SID, "AFTER", "caption", 900, lane_y + 68, 160, 16, color=GREEN,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)

# Footer mono caption
add_text(SID, "RUN 0427 · ENV: ml-bench-prod · ITER 12 / 12",
         "caption", 96, 672, 800, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5)


# =========================================================================
# SLIDE 7 — Velocity Proven
# =========================================================================
SID = "slide-7"
init_slide(SID, 1, GRAPHITE)

# Background subtle accent corner shapes
add_shape(SID, "circle", -200, -200, 600, 600, fill=ACCEL, stroke=ACCEL,
          opacity=0.08)
add_shape(SID, "circle", 880, 480, 500, 500, fill=CYAN, stroke=CYAN,
          opacity=0.06)

# Top caption
add_text(SID, "RESULT  /  POST-OPTIMIZATION BENCHMARK", "caption",
         96, 64, 800, 20, color=CYAN,
         font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2.4)

# Hero title
add_text(SID, "Velocity, Proven.", "title", 96, 104, 900, 80,
         color=WHITE, font_size=64, font_weight=600, line_height=1,
         font_family="Space Grotesk", letter_spacing=-1)

# Massive hero metric — center stage
add_shape(SID, "rectangle", 96, 224, 600, 280, fill=OBSIDIAN, stroke=OBSIDIAN)
# Cyan top accent bar
add_shape(SID, "rectangle", 96, 224, 600, 4, fill=CYAN, stroke=CYAN)

add_text(SID, "AGGREGATE GAIN", "caption", 128, 248, 400, 20, color=WARM,
         font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2.4)

add_text(SID, "9.4×", "title", 128, 280, 540, 180, color=WHITE,
         font_size=180, font_weight=700, line_height=1,
         font_family="Space Grotesk", letter_spacing=-4)

add_text(SID, "faster end-to-end vs. baseline run", "subheading",
         128, 460, 540, 32, color=SILVER, font_size=20,
         font_weight=400, font_family="Inter")

# Right column KPI cards
# KPI 1
kx, ky = 736, 224
add_shape(SID, "rectangle", kx, ky, 448, 88, fill=OBSIDIAN, stroke=OBSIDIAN)
add_shape(SID, "rectangle", kx, ky, 4, 88, fill=GREEN, stroke=GREEN)
add_text(SID, "LATENCY", "caption", kx + 24, ky + 16, 200, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=2)
add_text(SID, "−78%", "heading", kx + 24, ky + 36, 220, 40, color=GREEN,
         font_size=36, font_weight=700, font_family="Space Grotesk")
add_text(SID, "412ms → 88ms", "caption", kx + 260, ky + 48, 180, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=14,
         font_weight=400)

# KPI 2
ky = 320
add_shape(SID, "rectangle", kx, ky, 448, 88, fill=OBSIDIAN, stroke=OBSIDIAN)
add_shape(SID, "rectangle", kx, ky, 4, 88, fill=CYAN, stroke=CYAN)
add_text(SID, "THROUGHPUT", "caption", kx + 24, ky + 16, 240, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=2)
add_text(SID, "+612%", "heading", kx + 24, ky + 36, 220, 40, color=CYAN,
         font_size=36, font_weight=700, font_family="Space Grotesk")
add_text(SID, "1.2k → 8.6k req/s", "caption", kx + 260, ky + 48, 200, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=14,
         font_weight=400)

# KPI 3
ky = 416
add_shape(SID, "rectangle", kx, ky, 448, 88, fill=OBSIDIAN, stroke=OBSIDIAN)
add_shape(SID, "rectangle", kx, ky, 4, 88, fill=AMBER, stroke=AMBER)
add_text(SID, "ERROR RATE", "caption", kx + 24, ky + 16, 240, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=2)
add_text(SID, "−94%", "heading", kx + 24, ky + 36, 220, 40, color=AMBER,
         font_size=36, font_weight=700, font_family="Space Grotesk")
add_text(SID, "1.4% → 0.08%", "caption", kx + 260, ky + 48, 200, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=14,
         font_weight=400)

# KPI 4 (full width below hero)
add_shape(SID, "rectangle", 96, 528, 1088, 96, fill=OBSIDIAN, stroke=OBSIDIAN)
add_shape(SID, "rectangle", 96, 528, 4, 96, fill=VIOLET, stroke=VIOLET)
add_text(SID, "COST PER 1M REQUESTS", "caption", 128, 552, 320, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=2)
add_text(SID, "$184  →  $19", "heading", 128, 576, 360, 36, color=WHITE,
         font_size=30, font_weight=600, font_family="JetBrains Mono")
add_text(SID, "−89.7% compute spend, identical SLA envelope.",
         "subheading", 560, 576, 600, 32, color=SILVER, font_size=18,
         font_weight=400, font_family="Inter")

# Footer
add_text(SID, "BENCHMARK ID #VR-7841  ·  CONFIDENCE 99.2%  ·  N = 4,200 RUNS",
         "caption", 96, 672, 1088, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5)


# =========================================================================
# SLIDE 8 — The Speed Trial Begins
# =========================================================================
SID = "slide-8"
init_slide(SID, 2, OBSIDIAN)

# Diagonal accent line (rotated rectangle)
add_shape(SID, "rectangle", 200, 360, 1000, 2, fill=CYAN, stroke=CYAN,
          rotation=-12, opacity=0.4)
add_shape(SID, "rectangle", 240, 380, 900, 1, fill=ACCEL, stroke=ACCEL,
          rotation=-8, opacity=0.3)

# Top label
add_text(SID, "T −00:00  /  TRIAL ACTIVE", "caption", 96, 56, 600, 20,
         color=AMBER, font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2.4)

# Editorial headline upper-left
add_text(SID, "The Speed Trial", "title", 96, 100, 700, 80,
         color=WHITE, font_size=72, font_weight=600, line_height=1,
         font_family="Space Grotesk", letter_spacing=-1)
add_text(SID, "Begins.", "title", 96, 180, 700, 80,
         color=CYAN, font_size=72, font_weight=600, line_height=1,
         font_family="Space Grotesk", letter_spacing=-1)

# Tagline
add_text(SID, "Cold start. Real load. No safety net.", "subheading",
         96, 280, 700, 32, color=SILVER, font_size=20,
         font_weight=400, font_family="Inter")

# CENTRAL BENCHMARK TIMER
# Frame
add_shape(SID, "rectangle", 96, 376, 720, 200, fill=GRAPHITE, stroke=GRAPHITE)
# Corner accents
add_shape(SID, "rectangle", 96, 376, 60, 2, fill=CYAN, stroke=CYAN)
add_shape(SID, "rectangle", 96, 376, 2, 60, fill=CYAN, stroke=CYAN)
add_shape(SID, "rectangle", 754, 574, 62, 2, fill=CYAN, stroke=CYAN)
add_shape(SID, "rectangle", 814, 514, 2, 62, fill=CYAN, stroke=CYAN)

add_text(SID, "ELAPSED", "caption", 128, 400, 200, 16, color=WARM,
         font_family="JetBrains Mono", font_size=12, letter_spacing=2.4)

# Massive timer
add_text(SID, "00:00:42", "title", 128, 424, 660, 140, color=WHITE,
         font_size=140, font_weight=700, line_height=1,
         font_family="JetBrains Mono", letter_spacing=-2)

# Right side floating KPI mini-cards (top-right region)
# Card 1
kx, ky = 856, 376
add_shape(SID, "rectangle", kx, ky, 328, 60, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", kx, ky, 2, 60, fill=GREEN, stroke=GREEN)
add_text(SID, "THROUGHPUT", "caption", kx + 16, ky + 10, 180, 14, color=WARM,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)
add_text(SID, "8,612 r/s", "heading", kx + 16, ky + 28, 240, 28, color=GREEN,
         font_size=24, font_weight=700, font_family="JetBrains Mono")

# Card 2
ky = 444
add_shape(SID, "rectangle", kx, ky, 328, 60, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", kx, ky, 2, 60, fill=CYAN, stroke=CYAN)
add_text(SID, "P99 LATENCY", "caption", kx + 16, ky + 10, 180, 14, color=WARM,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)
add_text(SID, "94 ms", "heading", kx + 16, ky + 28, 240, 28, color=CYAN,
         font_size=24, font_weight=700, font_family="JetBrains Mono")

# Card 3
ky = 512
add_shape(SID, "rectangle", kx, ky, 328, 60, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", kx, ky, 2, 60, fill=AMBER, stroke=AMBER)
add_text(SID, "CPU UTIL", "caption", kx + 16, ky + 10, 180, 14, color=WARM,
         font_family="JetBrains Mono", font_size=10, letter_spacing=1.8)
add_text(SID, "62.4%", "heading", kx + 16, ky + 28, 240, 28, color=AMBER,
         font_size=24, font_weight=700, font_family="JetBrains Mono")

# Footer mono telemetry
add_text(SID, "▶ STREAM ACTIVE   ·   NODE: ml-bench-12   ·   REGION: us-east-1   ·   SAMPLE 0427",
         "caption", 96, 672, 1100, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.4)

# Tiny accent dot
add_shape(SID, "circle", 80, 672, 8, 8, fill=GREEN, stroke=GREEN)


# =========================================================================
# SLIDE 9 — Bottlenecks Under Glass
# =========================================================================
SID = "slide-9"
init_slide(SID, 3, OBSIDIAN)

# Top caption
add_text(SID, "DIAGNOSTIC  /  SYSTEM ANATOMY", "caption", 96, 56, 600, 20,
         color=RED, font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2.4)

# Editorial title
add_text(SID, "Bottlenecks Under Glass", "title", 96, 100, 1100, 80,
         color=WHITE, font_size=64, font_weight=500, line_height=1,
         font_family="Space Grotesk", letter_spacing=-1)

add_text(SID, "Where the machine slows — and why.", "subheading",
         96, 184, 900, 32, color=SILVER, font_size=20,
         font_weight=400, font_family="Inter")

# === LEFT HALF — System Anatomy Diagram ===
# Panel background
add_shape(SID, "rectangle", 96, 248, 560, 400, fill=GRAPHITE, stroke=GRAPHITE)
# Panel header bar
add_shape(SID, "rectangle", 96, 248, 560, 2, fill=CYAN, stroke=CYAN)

add_text(SID, "ARCHITECTURE TRACE", "caption", 116, 268, 400, 16, color=CYAN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=2)

# Diagram nodes — pipeline flow
# Node 1: INGEST
add_shape(SID, "rectangle", 124, 320, 100, 60, fill=OBSIDIAN, stroke=CYAN, stroke_width=1)
add_text(SID, "INGEST", "caption", 124, 340, 100, 18, color=CYAN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5,
         text_align="center")
add_text(SID, "12ms", "caption", 124, 358, 100, 14, color=WARM,
         font_family="JetBrains Mono", font_size=10, text_align="center")

# Connector line
add_shape(SID, "line", 224, 350, 60, 1, fill=SILVER, stroke=SILVER, stroke_width=1)

# Node 2: QUEUE — BOTTLENECK (red)
add_shape(SID, "rectangle", 284, 320, 100, 60, fill=OBSIDIAN, stroke=RED, stroke_width=2)
add_text(SID, "QUEUE", "caption", 284, 340, 100, 18, color=RED,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5,
         text_align="center")
add_text(SID, "612ms", "caption", 284, 358, 100, 14, color=RED,
         font_family="JetBrains Mono", font_size=10, font_weight=700,
         text_align="center")

# Connector
add_shape(SID, "line", 384, 350, 60, 1, fill=SILVER, stroke=SILVER, stroke_width=1)

# Node 3: COMPUTE
add_shape(SID, "rectangle", 444, 320, 100, 60, fill=OBSIDIAN, stroke=CYAN, stroke_width=1)
add_text(SID, "COMPUTE", "caption", 444, 340, 100, 18, color=CYAN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5,
         text_align="center")
add_text(SID, "84ms", "caption", 444, 358, 100, 14, color=WARM,
         font_family="JetBrains Mono", font_size=10, text_align="center")

# Lower row — DB and CACHE
# Connector down
add_shape(SID, "line", 334, 380, 1, 50, fill=SILVER, stroke=SILVER, stroke_width=1)

# Node 4: DB — secondary bottleneck (amber)
add_shape(SID, "rectangle", 184, 440, 100, 60, fill=OBSIDIAN, stroke=AMBER, stroke_width=2)
add_text(SID, "DATABASE", "caption", 184, 460, 100, 18, color=AMBER,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5,
         text_align="center")
add_text(SID, "248ms", "caption", 184, 478, 100, 14, color=AMBER,
         font_family="JetBrains Mono", font_size=10, font_weight=700,
         text_align="center")

# Node 5: CACHE
add_shape(SID, "rectangle", 384, 440, 100, 60, fill=OBSIDIAN, stroke=GREEN, stroke_width=1)
add_text(SID, "CACHE", "caption", 384, 460, 100, 18, color=GREEN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5,
         text_align="center")
add_text(SID, "4ms", "caption", 384, 478, 100, 14, color=WARM,
         font_family="JetBrains Mono", font_size=10, text_align="center")

# Legend at bottom of panel
add_text(SID, "● HEALTHY   ● FRICTION   ● CRITICAL", "caption", 124, 596, 500, 16,
         color=SILVER, font_family="JetBrains Mono", font_size=10,
         letter_spacing=1.5)

# === RIGHT HALF — Diagnostic Panels ===
panel_x = 688
# Panel header
add_text(SID, "HOTSPOT REPORT", "caption", panel_x, 268, 400, 16, color=AMBER,
         font_family="JetBrains Mono", font_size=11, letter_spacing=2)

# Panel 1 — CRITICAL
py = 296
add_shape(SID, "rectangle", panel_x, py, 496, 108, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", panel_x, py, 4, 108, fill=RED, stroke=RED)
add_text(SID, "CRITICAL", "caption", panel_x + 20, py + 16, 120, 16,
         color=RED, font_family="JetBrains Mono",
         font_size=11, font_weight=700, letter_spacing=1.8)
add_text(SID, "Queue saturation @ 92%", "paragraph", panel_x + 20, py + 36, 460, 28,
         color=WHITE, font_size=20, font_weight=600, font_family="Inter")
add_text(SID, "Single-threaded dispatcher under contention. Fix: parallel workers + async drain.",
         "caption", panel_x + 20, py + 68, 460, 32, color=SILVER,
         font_family="Inter", font_size=13, font_weight=400, line_height=1.4)

# Panel 2 — DEGRADED
py = 420
add_shape(SID, "rectangle", panel_x, py, 496, 108, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", panel_x, py, 4, 108, fill=AMBER, stroke=AMBER)
add_text(SID, "DEGRADED", "caption", panel_x + 20, py + 16, 120, 16,
         color=AMBER, font_family="JetBrains Mono",
         font_size=11, font_weight=700, letter_spacing=1.8)
add_text(SID, "DB lock contention", "paragraph", panel_x + 20, py + 36, 460, 28,
         color=WHITE, font_size=20, font_weight=600, font_family="Inter")
add_text(SID, "Row-level locks held during analytical scans. Fix: read replica + index hint.",
         "caption", panel_x + 20, py + 68, 460, 32, color=SILVER,
         font_family="Inter", font_size=13, font_weight=400, line_height=1.4)

# Panel 3 — WATCH
py = 544
add_shape(SID, "rectangle", panel_x, py, 496, 104, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", panel_x, py, 4, 104, fill=CYAN, stroke=CYAN)
add_text(SID, "WATCH", "caption", panel_x + 20, py + 16, 120, 16,
         color=CYAN, font_family="JetBrains Mono",
         font_size=11, font_weight=700, letter_spacing=1.8)
add_text(SID, "Memory pressure — heap @ 71%", "paragraph", panel_x + 20, py + 36, 460, 28,
         color=WHITE, font_size=20, font_weight=600, font_family="Inter")
add_text(SID, "Trending upward across last 6 cycles. No action yet — flag for next pass.",
         "caption", panel_x + 20, py + 68, 460, 28, color=SILVER,
         font_family="Inter", font_size=13, font_weight=400, line_height=1.4)

# Footer
add_text(SID, "TRACE 0427-Δ  ·  3 ANOMALIES DETECTED  ·  ROOT-CAUSE CONFIDENCE 96.4%",
         "caption", 96, 672, 1100, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.4)


# =========================================================================
# SLIDE 10 — The Optimization Pass
# =========================================================================
SID = "slide-10"
init_slide(SID, 4, OBSIDIAN)

# Top caption
add_text(SID, "TRANSFORMATION  /  PASS 02", "caption", 96, 56, 600, 20,
         color=CYAN, font_family="JetBrains Mono", font_size=12,
         font_weight=600, letter_spacing=2.4)

# Editorial title
add_text(SID, "The Optimization Pass", "title", 96, 100, 1100, 80,
         color=WHITE, font_size=64, font_weight=500, line_height=1,
         font_family="Space Grotesk", letter_spacing=-1)

add_text(SID, "Chaos becomes engineered flow.", "subheading",
         96, 184, 800, 32, color=SILVER, font_size=20,
         font_weight=400, font_family="Inter")

# === LEFT — BEFORE panel ===
bx, by = 96, 256
add_shape(SID, "rectangle", bx, by, 320, 392, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", bx, by, 320, 2, fill=RED, stroke=RED)

add_text(SID, "BEFORE", "caption", bx + 24, by + 24, 200, 16, color=RED,
         font_family="JetBrains Mono", font_size=12,
         font_weight=700, letter_spacing=2.4)

add_text(SID, "Congested.", "heading", bx + 24, by + 50, 280, 36, color=WHITE,
         font_size=30, font_weight=600, font_family="Space Grotesk")

# Mini bar chart — congested (red bars of varying heights)
# Bar visualization: 6 bars
chart_y = by + 120
chart_x = bx + 24
bar_w = 36
gap = 8
heights = [180, 220, 160, 240, 200, 230]
for i, h in enumerate(heights):
    bx_pos = chart_x + i * (bar_w + gap)
    bx_top = chart_y + (240 - h)
    add_shape(SID, "rectangle", bx_pos, bx_top, bar_w, h,
              fill=RED, stroke=RED, opacity=0.85)

# Baseline reading
add_text(SID, "P99  812ms", "caption", bx + 24, by + 372, 280, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5)

# === CENTER — Optimization Engine ===
ex, ey = 448, 256
add_shape(SID, "rectangle", ex, ey, 384, 392, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", ex, ey, 384, 2, fill=CYAN, stroke=CYAN)
add_shape(SID, "rectangle", ex, ey + 390, 384, 2, fill=CYAN, stroke=CYAN)

add_text(SID, "OPTIMIZATION ENGINE", "caption", ex + 24, ey + 24, 340, 16,
         color=CYAN, font_family="JetBrains Mono", font_size=11,
         font_weight=600, letter_spacing=2)

# Central glowing ring
add_shape(SID, "circle", ex + 112, ey + 80, 160, 160, fill=OBSIDIAN, stroke=CYAN,
          stroke_width=2, opacity=0.95)
add_shape(SID, "circle", ex + 132, ey + 100, 120, 120, fill=GRAPHITE, stroke=ACCEL,
          stroke_width=1)

# Center icon
add_icon(SID, "Zap", ex + 160, ey + 128, size=64, color=CYAN)

# Modules around the ring (4 module tags)
# Top
add_shape(SID, "rectangle", ex + 132, ey + 254, 120, 28, fill=OBSIDIAN, stroke=CYAN,
          stroke_width=1)
add_text(SID, "CACHE", "caption", ex + 132, ey + 261, 120, 16, color=CYAN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.8,
         text_align="center")

add_shape(SID, "rectangle", ex + 132, ey + 290, 120, 28, fill=OBSIDIAN, stroke=ACCEL,
          stroke_width=1)
add_text(SID, "BATCH", "caption", ex + 132, ey + 297, 120, 16, color=ACCEL,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.8,
         text_align="center")

add_shape(SID, "rectangle", ex + 132, ey + 326, 120, 28, fill=OBSIDIAN, stroke=VIOLET,
          stroke_width=1)
add_text(SID, "PARALLEL", "caption", ex + 132, ey + 333, 120, 16, color=VIOLET,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.8,
         text_align="center")

# Side modules
add_shape(SID, "rectangle", ex + 16, ey + 290, 96, 28, fill=OBSIDIAN, stroke=GREEN,
          stroke_width=1)
add_text(SID, "PRUNE", "caption", ex + 16, ey + 297, 96, 16, color=GREEN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.8,
         text_align="center")

add_shape(SID, "rectangle", ex + 272, ey + 290, 96, 28, fill=OBSIDIAN, stroke=AMBER,
          stroke_width=1)
add_text(SID, "ASYNC", "caption", ex + 272, ey + 297, 96, 16, color=AMBER,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.8,
         text_align="center")

# === RIGHT — AFTER panel ===
ax, ay = 864, 256
add_shape(SID, "rectangle", ax, ay, 320, 392, fill=GRAPHITE, stroke=GRAPHITE)
add_shape(SID, "rectangle", ax, ay, 320, 2, fill=GREEN, stroke=GREEN)

add_text(SID, "AFTER", "caption", ax + 24, ay + 24, 200, 16, color=GREEN,
         font_family="JetBrains Mono", font_size=12,
         font_weight=700, letter_spacing=2.4)

add_text(SID, "Engineered.", "heading", ax + 24, ay + 50, 280, 36, color=WHITE,
         font_size=30, font_weight=600, font_family="Space Grotesk")

# Mini bar chart — optimized (cyan-green bars, low and uniform)
chart_y = ay + 120
chart_x = ax + 24
heights = [60, 72, 58, 80, 64, 70]
for i, h in enumerate(heights):
    bx_pos = chart_x + i * (bar_w + gap)
    bx_top = chart_y + (240 - h)
    add_shape(SID, "rectangle", bx_pos, bx_top, bar_w, h,
              fill=CYAN, stroke=CYAN, opacity=0.95)

# Optimized reading
add_text(SID, "P99  142ms", "caption", ax + 24, ay + 372, 280, 16, color=GREEN,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.5,
         font_weight=600)

# Connecting arrows between panels
add_icon(SID, "ArrowRight", 416, 432, size=32, color=SILVER)
add_icon(SID, "ArrowRight", 832, 432, size=32, color=SILVER)

# Footer
add_text(SID, "5 INTERVENTIONS APPLIED  ·  ROLLOUT GREEN  ·  REGRESSION DELTA 0.0%",
         "caption", 96, 672, 1100, 16, color=WARM,
         font_family="JetBrains Mono", font_size=11, letter_spacing=1.4)


# =========================================================================
# Final assembly
# =========================================================================

# Count text elements across slides
text_count = sum(len(s["textElements"]) for s in slides_content)
total_elements = (text_count + len(shape_elements) + len(image_elements)
                  + len(chart_elements) + len(table_elements)
                  + len(icon_elements))

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

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-2-{NOW}",
        "title": "Fast Optimization Test (slides 6-10)",
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
        "baseLayout": baselayout_file,
        "changelog": changelog_file
    }
}

with open("deck.json", "w") as f:
    json.dump(envelope, f, indent=2)

print(f"deck.json | slides=5 | elements={total_elements}")
