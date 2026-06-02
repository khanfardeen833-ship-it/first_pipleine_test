import json, time, os

NOW = int(time.time() * 1000)

# ---------- Counter ----------
COUNTER = 0
def nid():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ---------- Palette ----------
OBSIDIAN = "#0B1020"
NAVY     = "#111A33"
AZURE    = "#2F80FF"
CYAN     = "#21D4FD"
VIOLET   = "#8B5CF6"
GREEN    = "#22C55E"
AMBER    = "#F59E0B"
MINT     = "#7DD3FC"
SILVER   = "#D8DEE9"
WHITE    = "#F8FAFC"
INK      = "#1c1917"

# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx,
              color=WHITE, font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk",
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
        "animationTypewriterMode": "character", "updatedAt": NOW
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx,
               fill=AZURE, stroke=None, stroke_width=0, opacity=1, rotation=0):
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
        "updatedAt": NOW
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx,
              size=64, color=CYAN, opacity=1):
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


# ---------- Containers ----------
slides_content = []
slides_baselayout = []
changelog_slides = {}

text_by_slide = {}    # slide_id -> list
shape_elements = []
icon_elements = []
chart_elements = []
image_elements = []
table_elements = []

def init_slide(slide_id, order, bg=OBSIDIAN):
    slides_content.append({
        "id": slide_id, "order": order,
        "layoutId": "blank-canvas",
        "backgroundColor": bg,
        "textElements": []  # populated at end
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    changelog_slides[slide_id] = {"elements": {}}
    text_by_slide[slide_id] = []


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = nid()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = nid()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid


def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = nid()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = nid()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, chart_config)
    chart_elements.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl
    return cid


# ============================================================
# SLIDE 1 — The Cloud as a Living System
# ============================================================
S1 = "slide-1"
init_slide(S1, 0, bg=OBSIDIAN)

# Subtle navy band lower-third
add_shape(S1, "rectangle", 0, 470, 1280, 250, fill=NAVY, opacity=0.7)

# Decorative architecture node grid (small dots) along bottom
node_positions = [
    (120, 560), (220, 600), (320, 540), (420, 590), (520, 555),
    (640, 600), (740, 540), (840, 595), (940, 555), (1040, 600), (1140, 545)
]
for (nx, ny) in node_positions:
    add_shape(S1, "circle", nx, ny, 10, 10, fill=CYAN, opacity=0.9)

# Connector lines along bottom (thin rectangles to evoke data flow)
add_shape(S1, "rectangle", 120, 620, 1020, 2, fill=AZURE, opacity=0.55)
add_shape(S1, "rectangle", 120, 660, 1020, 1, fill=VIOLET, opacity=0.4)

# Top-right metadata caption block
add_text(S1, "CLOUD-NATIVE  //  RESILIENT  //  SCALABLE",
         "caption", 880, 56, 360, 24,
         color=CYAN, font_family="JetBrains Mono", font_size=12,
         letter_spacing=2, text_align="right", text_transform="uppercase")

# Top-left small kicker
add_shape(S1, "rectangle", 80, 152, 56, 3, fill=CYAN)
add_text(S1, "VOL. 01  //  ARCHITECTURE FIELD GUIDE",
         "caption", 144, 144, 500, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=12,
         letter_spacing=3, text_transform="uppercase")

# Hero title (two lines)
add_text(S1, "The Cloud as a",
         "title", 80, 200, 1100, 96,
         color=WHITE, font_size=86, font_weight=700, line_height=1.0)
add_text(S1, "Living System.",
         "title", 80, 296, 1100, 110,
         color=CYAN, font_size=96, font_weight=700, line_height=1.0,
         font_style="italic")

# Subtitle / thesis line
add_text(S1, "A field guide to containerized systems, orchestrated platforms,",
         "paragraph", 80, 432, 920, 30,
         color=SILVER, font_size=22, font_weight=400, line_height=1.4)
add_text(S1, "microservices, serverless patterns, and deployment excellence.",
         "paragraph", 80, 462, 920, 30,
         color=SILVER, font_size=22, font_weight=400, line_height=1.4)

# Bottom-left deck metadata
add_text(S1, "CLOUD ARCHITECTURE  //  BEST PRACTICES  //  2026",
         "caption", 80, 670, 700, 20,
         color=MINT, font_family="JetBrains Mono", font_size=12,
         letter_spacing=2, text_transform="uppercase")

# Bottom-right page number
add_text(S1, "01",
         "caption", 1180, 660, 60, 28,
         color=AMBER, font_family="JetBrains Mono", font_size=20,
         font_weight=700, text_align="right")

# Decorative cloud icon (right side, large, low opacity)
add_icon(S1, "Cloud", 1000, 200, size=180, color=AZURE, opacity=0.18)
# Smaller satellites
add_icon(S1, "Server", 1080, 380, size=44, color=VIOLET, opacity=0.55)
add_icon(S1, "Cpu", 940, 410, size=36, color=CYAN, opacity=0.55)


# ============================================================
# SLIDE 2 — Principles Before Patterns
# ============================================================
S2 = "slide-2"
init_slide(S2, 1, bg=OBSIDIAN)

# Soft vertical divider
add_shape(S2, "rectangle", 600, 96, 1, 528, fill=SILVER, opacity=0.18)

# Top kicker
add_shape(S2, "rectangle", 80, 76, 32, 3, fill=VIOLET)
add_text(S2, "CHAPTER 01  //  FOUNDATIONS",
         "caption", 124, 68, 400, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=12,
         letter_spacing=3, text_transform="uppercase")

# Section title (left column)
add_text(S2, "Principles",
         "title", 80, 110, 520, 70,
         color=WHITE, font_size=64, font_weight=700, line_height=1.0)
add_text(S2, "before patterns.",
         "title", 80, 178, 520, 70,
         color=CYAN, font_size=64, font_weight=700, line_height=1.0,
         font_style="italic")

# Editorial pull quote
add_text(S2, "“Architecture is a set of trade-offs made visible.”",
         "paragraph", 80, 268, 500, 64,
         color=MINT, font_size=20, font_weight=400, line_height=1.4,
         font_style="italic")

# Five principles as numbered manifesto (left column)
principles = [
    ("01", "Scalability",  "Design for elastic load, not peak load."),
    ("02", "Resilience",   "Assume failure. Recover gracefully."),
    ("03", "Automation",   "If a human does it twice, automate it."),
    ("04", "Isolation",    "Bound contexts. Independent blast radius."),
    ("05", "Cost Awareness","Architecture decisions are economic decisions."),
]
py = 348
for (num, name, desc) in principles:
    add_text(S2, num, "caption", 80, py, 40, 20,
             color=AMBER, font_family="JetBrains Mono", font_size=12, font_weight=600)
    add_text(S2, name, "heading", 130, py - 6, 200, 30,
             color=WHITE, font_size=22, font_weight=600)
    add_text(S2, desc, "paragraph", 130, py + 22, 440, 24,
             color=SILVER, font_size=14, font_weight=400, line_height=1.35)
    py += 56

# Right column — layered platform stack (glassmorphism)
# Title for diagram
add_text(S2, "PLATFORM STACK",
         "caption", 640, 110, 280, 18,
         color=CYAN, font_family="JetBrains Mono", font_size=12,
         letter_spacing=3, text_transform="uppercase")

layers = [
    ("Experience Layer",    AZURE,   "UI · Mobile · APIs"),
    ("API Gateway",         CYAN,    "Routing · Auth · Rate Limits"),
    ("Services",            VIOLET,  "Microservices · Functions"),
    ("Data Platform",       MINT,    "Stores · Streams · Caches"),
    ("Observability",       AMBER,   "Logs · Metrics · Traces"),
    ("Security Foundation", GREEN,   "IAM · Secrets · Policy"),
]
ly = 148
for i, (lname, lcolor, ldesc) in enumerate(layers):
    # Glass panel
    add_shape(S2, "rectangle", 640, ly, 560, 64, fill=NAVY, opacity=0.85,
              stroke=lcolor, stroke_width=1)
    # Color edge accent (left bar)
    add_shape(S2, "rectangle", 640, ly, 4, 64, fill=lcolor)
    # Layer name
    add_text(S2, lname, "heading", 664, ly + 10, 320, 28,
             color=WHITE, font_size=20, font_weight=600)
    # Layer desc
    add_text(S2, ldesc, "caption", 664, ly + 36, 320, 22,
             color=SILVER, font_family="JetBrains Mono", font_size=12,
             letter_spacing=1)
    # Right-side small index
    add_text(S2, f"L{i+1}", "caption", 1140, ly + 22, 40, 20,
             color=lcolor, font_family="JetBrains Mono", font_size=14,
             font_weight=700, text_align="right")
    ly += 76

# Bottom-right page number
add_text(S2, "02",
         "caption", 1180, 670, 60, 24,
         color=AMBER, font_family="JetBrains Mono", font_size=16,
         font_weight=700, text_align="right")


# ============================================================
# SLIDE 3 — Containerization
# ============================================================
S3 = "slide-3"
init_slide(S3, 2, bg=OBSIDIAN)

# Top kicker
add_shape(S3, "rectangle", 80, 76, 32, 3, fill=GREEN)
add_text(S3, "CHAPTER 02  //  CONTAINERIZATION",
         "caption", 124, 68, 460, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=12,
         letter_spacing=3, text_transform="uppercase")

# Title — two lines
add_text(S3, "Package the runtime,",
         "title", 80, 108, 1120, 70,
         color=WHITE, font_size=54, font_weight=700, line_height=1.0)
add_text(S3, "not the chaos.",
         "title", 80, 170, 1120, 70,
         color=CYAN, font_size=54, font_weight=700, line_height=1.0,
         font_style="italic")

# Lifecycle diagram — horizontal across middle
# Y baseline ~310
diag_y = 310
nodes = [
    ("Code",      "FileCode",     90),
    ("Build",     "Hammer",      330),
    ("Image",     "Package",     570),
    ("Registry",  "Database",    810),
    ("Runtime",   "Play",       1050),
]
# Connector rail behind nodes
add_shape(S3, "rectangle", 150, diag_y + 56, 960, 2, fill=CYAN, opacity=0.45)

for i, (label, icon_name, nx) in enumerate(nodes):
    # Node card
    add_shape(S3, "rectangle", nx, diag_y, 130, 116, fill=NAVY,
              stroke=CYAN, stroke_width=1, opacity=0.9)
    # Icon
    add_icon(S3, icon_name, nx + 41, diag_y + 16, size=48, color=CYAN)
    # Label
    add_text(S3, label, "caption", nx, diag_y + 78, 130, 24,
             color=WHITE, font_size=14, font_weight=600,
             text_align="center", letter_spacing=1, text_transform="uppercase")
    # Step number
    add_text(S3, f"0{i+1}", "caption", nx + 8, diag_y + 4, 40, 16,
             color=AMBER, font_family="JetBrains Mono", font_size=10,
             font_weight=700)

# Diagram caption
add_text(S3, "Source → Build → Image → Registry → Container",
         "caption", 80, diag_y + 140, 1120, 22,
         color=MINT, font_family="JetBrains Mono", font_size=13,
         text_align="center", letter_spacing=2, text_transform="uppercase")

# Code card bottom — premium dark mode Dockerfile
code_x, code_y, code_w, code_h = 80, 488, 700, 184
add_shape(S3, "rectangle", code_x, code_y, code_w, code_h, fill="#06080F",
          stroke=CYAN, stroke_width=1, opacity=0.95)
# Window dots
add_shape(S3, "circle", code_x + 18, code_y + 16, 10, 10, fill="#FF5F56")
add_shape(S3, "circle", code_x + 36, code_y + 16, 10, 10, fill="#FFBD2E")
add_shape(S3, "circle", code_x + 54, code_y + 16, 10, 10, fill="#27C93F")
# Filename label
add_text(S3, "Dockerfile  ·  multi-stage", "caption",
         code_x + 80, code_y + 12, 400, 18,
         color=SILVER, font_family="JetBrains Mono", font_size=12,
         letter_spacing=1)

# Code lines
code_lines = [
    ("FROM",   " node:20-alpine AS build",     CYAN),
    ("WORKDIR", " /app",                       VIOLET),
    ("COPY",   " package*.json ./",            CYAN),
    ("RUN",    " npm ci --omit=dev",           CYAN),
    ("COPY",   " . .",                         CYAN),
    ("FROM",   " gcr.io/distroless/nodejs20",  CYAN),
    ("COPY",   " --from=build /app /app",      CYAN),
    ("CMD",    " [\"/app/server.js\"]",        CYAN),
]
ly = code_y + 44
for i, (kw, rest, kcolor) in enumerate(code_lines):
    # Line number
    add_text(S3, f"{i+1:02d}", "caption", code_x + 16, ly, 28, 18,
             color="#3a4358", font_family="JetBrains Mono",
             font_size=12, font_weight=400)
    # Keyword
    add_text(S3, kw, "caption", code_x + 52, ly, 90, 18,
             color=kcolor, font_family="JetBrains Mono",
             font_size=13, font_weight=600)
    # Rest of line
    add_text(S3, rest, "caption", code_x + 100, ly, 560, 18,
             color=WHITE, font_family="JetBrains Mono",
             font_size=13, font_weight=400)
    ly += 17

# Right side — three principle pull-cards
right_x = 808
card_w = 392
card_h = 56
labels = [
    ("Build once.",       "Reproducible images, signed and scanned.", GREEN),
    ("Promote everywhere.","Same artifact across dev → staging → prod.", CYAN),
    ("Observe always.",   "Health, metrics, and logs by default.",    AMBER),
]
cy = 488
for (lname, ldesc, lcolor) in labels:
    add_shape(S3, "rectangle", right_x, cy, card_w, card_h, fill=NAVY,
              stroke=lcolor, stroke_width=1, opacity=0.85)
    add_shape(S3, "rectangle", right_x, cy, 3, card_h, fill=lcolor)
    add_text(S3, lname, "heading", right_x + 16, cy + 8, 360, 22,
             color=WHITE, font_size=16, font_weight=700)
    add_text(S3, ldesc, "caption", right_x + 16, cy + 30, 360, 20,
             color=SILVER, font_family="JetBrains Mono", font_size=11,
             letter_spacing=1)
    cy += 64

# Page number
add_text(S3, "03",
         "caption", 1180, 670, 60, 24,
         color=AMBER, font_family="JetBrains Mono", font_size=16,
         font_weight=700, text_align="right")


# ============================================================
# SLIDE 4 — Containers, Disciplined  (rules + bar chart)
# ============================================================
S4 = "slide-4"
init_slide(S4, 3, bg=OBSIDIAN)

# Kicker
add_shape(S4, "rectangle", 80, 76, 32, 3, fill=AMBER)
add_text(S4, "CHAPTER 02 · CONT'D  //  DISCIPLINE",
         "caption", 124, 68, 460, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=12,
         letter_spacing=3, text_transform="uppercase")

# Title
add_text(S4, "Smaller. Safer.",
         "title", 80, 108, 800, 70,
         color=WHITE, font_size=58, font_weight=700, line_height=1.0)
add_text(S4, "Faster to ship.",
         "title", 80, 172, 800, 70,
         color=CYAN, font_size=58, font_weight=700, line_height=1.0,
         font_style="italic")

# Subtitle
add_text(S4, "What changes when you treat the image as a contract.",
         "paragraph", 80, 252, 800, 28,
         color=MINT, font_size=20, font_weight=400, line_height=1.35,
         font_style="italic")

# Left rules list
rules = [
    ("01", "Use minimal base images",     "Distroless or Alpine. Less surface, fewer CVEs."),
    ("02", "Pin every dependency",        "Tag versions. No 'latest' in production."),
    ("03", "Scan before promotion",       "SBOM + vulnerability scan in CI."),
    ("04", "Run as non-root",             "Drop capabilities. Read-only filesystems."),
    ("05", "Treat config as input",       "12-factor: env vars, secrets, no baked configs."),
]
ry = 322
for (num, rname, rdesc) in rules:
    add_text(S4, num, "caption", 80, ry, 40, 18,
             color=AMBER, font_family="JetBrains Mono", font_size=12, font_weight=600)
    add_text(S4, rname, "heading", 130, ry - 4, 460, 24,
             color=WHITE, font_size=18, font_weight=600)
    add_text(S4, rdesc, "caption", 130, ry + 18, 480, 20,
             color=SILVER, font_family="JetBrains Mono", font_size=11,
             letter_spacing=0.5)
    ry += 58

# Right — chart panel
# Panel
add_shape(S4, "rectangle", 660, 300, 540, 360, fill=NAVY, opacity=0.85,
          stroke=CYAN, stroke_width=1)

# Panel header
add_text(S4, "BEFORE  /  AFTER  ·  IMAGE DISCIPLINE",
         "caption", 680, 316, 500, 18,
         color=CYAN, font_family="JetBrains Mono", font_size=11,
         letter_spacing=2, text_transform="uppercase")
add_text(S4, "Same workload. New defaults.",
         "subheading", 680, 338, 500, 28,
         color=WHITE, font_size=20, font_weight=600)

# Bar chart inside panel
chart_cfg = {
    "tooltip": {"trigger": "axis"},
    "legend": {
        "show": True,
        "data": ["Before", "After"],
        "textStyle": {"color": SILVER, "fontSize": 12},
        "top": 6, "right": 10
    },
    "grid": {"left": 60, "right": 20, "top": 40, "bottom": 50, "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": ["Image MB", "Build sec", "CVEs", "Cold ms"],
        "axisLine": {"lineStyle": {"color": SILVER}},
        "axisLabel": {"color": SILVER, "fontSize": 11}
    },
    "yAxis": {
        "type": "value",
        "axisLine": {"lineStyle": {"color": SILVER}},
        "axisLabel": {"color": SILVER, "fontSize": 11},
        "splitLine": {"lineStyle": {"color": "#1f2a44"}}
    },
    "series": [
        {"name": "Before", "type": "bar", "data": [980, 240, 48, 1800],
         "itemStyle": {"color": AMBER}},
        {"name": "After",  "type": "bar", "data": [120,  60,  3,  420],
         "itemStyle": {"color": CYAN}}
    ],
    "backgroundColor": "transparent",
    "color": [AMBER, CYAN],
    "animation": False,
    "textStyle": {"color": SILVER, "fontSize": 12,
                  "fontWeight": "normal", "fontStyle": "normal"},
    "tableData": {
        "categories": ["Image MB", "Build sec", "CVEs", "Cold ms"],
        "series": [
            {"name": "Before", "data": [980, 240, 48, 1800]},
            {"name": "After",  "data": [120,  60,  3,  420]}
        ]
    },
    "properties": {
        "showXAxis": True, "showYAxis": True, "showDataLabels": False,
        "showLegend": True, "showLabelName": True, "showLabelValue": False,
        "labelFontSize": 12, "labelBold": False, "labelItalic": False,
        "labelUnderline": False, "labelStrike": False
    },
    "activeColorScheme": None, "isDarkMode": True,
    "customSeriesColors": {"0": AMBER, "1": CYAN},
    "textColor": SILVER, "isMonochrome": False
}
add_chart(S4, "bar", 680, 372, 500, 240, chart_cfg)

# Panel footer caption
add_text(S4, "Median across 12 production services migrating to distroless multi-stage builds.",
         "caption", 680, 624, 500, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=10,
         letter_spacing=0.5)

# Page number
add_text(S4, "04",
         "caption", 1180, 670, 60, 24,
         color=AMBER, font_family="JetBrains Mono", font_size=16,
         font_weight=700, text_align="right")


# ============================================================
# SLIDE 5 — From Container to Cluster (bridge slide)
# ============================================================
S5 = "slide-5"
init_slide(S5, 4, bg=OBSIDIAN)

# Kicker
add_shape(S5, "rectangle", 80, 76, 32, 3, fill=VIOLET)
add_text(S5, "CHAPTER 02 → 03  //  BRIDGE",
         "caption", 124, 68, 460, 20,
         color=SILVER, font_family="JetBrains Mono", font_size=12,
         letter_spacing=3, text_transform="uppercase")

# Title
add_text(S5, "From container",
         "title", 80, 108, 1120, 70,
         color=WHITE, font_size=64, font_weight=700, line_height=1.0)
add_text(S5, "to cluster.",
         "title", 80, 178, 1120, 80,
         color=CYAN, font_size=72, font_weight=700, line_height=1.0,
         font_style="italic")

# Subtitle
add_text(S5, "One container is a unit. A cluster is a system. The discipline shifts from packaging to scheduling.",
         "paragraph", 80, 268, 1120, 30,
         color=SILVER, font_size=20, font_weight=400, line_height=1.4)

# Three environment panels (Dev → Staging → Production)
panels = [
    ("DEV",        "Local Iteration",  "1 replica",  "fast feedback",   AZURE,  "Code"),
    ("STAGING",    "Pre-Production",   "3 replicas", "shadow traffic",  VIOLET, "TestTube"),
    ("PRODUCTION", "Live Workload",    "12 replicas","SLO-bound",       GREEN,  "Globe"),
]

panel_w = 360
gap = 32
start_x = (1280 - (panel_w * 3 + gap * 2)) // 2  # center the row
panel_y = 340
panel_h = 240

for i, (env, label, repl, mode, ecolor, ico) in enumerate(panels):
    px = start_x + i * (panel_w + gap)

    # Panel background
    add_shape(S5, "rectangle", px, panel_y, panel_w, panel_h, fill=NAVY,
              stroke=ecolor, stroke_width=1, opacity=0.9)
    # Top accent bar
    add_shape(S5, "rectangle", px, panel_y, panel_w, 4, fill=ecolor)
    # Icon
    add_icon(S5, ico, px + 24, panel_y + 24, size=44, color=ecolor)
    # Env label small mono
    add_text(S5, env, "caption", px + 24, panel_y + 88, panel_w - 48, 18,
             color=ecolor, font_family="JetBrains Mono", font_size=11,
             letter_spacing=3, font_weight=700, text_transform="uppercase")
    # Headline
    add_text(S5, label, "heading", px + 24, panel_y + 108, panel_w - 48, 32,
             color=WHITE, font_size=24, font_weight=600)
    # Divider
    add_shape(S5, "rectangle", px + 24, panel_y + 152, panel_w - 48, 1,
              fill=SILVER, opacity=0.25)
    # Replicas
    add_text(S5, "REPLICAS", "caption", px + 24, panel_y + 162, 120, 16,
             color=SILVER, font_family="JetBrains Mono", font_size=10,
             letter_spacing=2, text_transform="uppercase")
    add_text(S5, repl, "subheading", px + 24, panel_y + 178, 200, 24,
             color=WHITE, font_family="JetBrains Mono", font_size=18, font_weight=700)
    # Mode label right-aligned
    add_text(S5, "MODE", "caption", px + panel_w - 144, panel_y + 162, 120, 16,
             color=SILVER, font_family="JetBrains Mono", font_size=10,
             letter_spacing=2, text_transform="uppercase", text_align="right")
    add_text(S5, mode, "subheading", px + panel_w - 200, panel_y + 178, 176, 24,
             color=ecolor, font_family="JetBrains Mono", font_size=14,
             font_weight=600, text_align="right")

    # Chevron between panels
    if i < 2:
        cx = px + panel_w + 4
        cy_mid = panel_y + panel_h // 2 - 12
        add_icon(S5, "ChevronRight", cx, cy_mid, size=24, color=CYAN, opacity=0.85)

# Bottom caption / quote
add_shape(S5, "rectangle", 80, 612, 1120, 1, fill=SILVER, opacity=0.2)
add_text(S5, "“The cluster is the contract between your image and reality.”",
         "paragraph", 80, 626, 900, 28,
         color=MINT, font_size=18, font_weight=400, line_height=1.4,
         font_style="italic")

# Page number
add_text(S5, "05",
         "caption", 1180, 670, 60, 24,
         color=AMBER, font_family="JetBrains Mono", font_size=16,
         font_weight=700, text_align="right")


# ============================================================
# Assemble final JSON
# ============================================================

# Place text elements into slides
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

# Element count = total of all element types
total_text = sum(len(text_by_slide[sid]) for sid in text_by_slide)
total_elements = (
    total_text
    + len(image_elements)
    + len(shape_elements)
    + len(chart_elements)
    + len(table_elements)
    + len(icon_elements)
    + 0  # embeds
    + 0  # smart diagrams
    + 0  # groups
)

slide_count = len(slides_content)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Cloud Architecture Best Practices",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": slide_count,
        "elementCount": total_elements,
        "createdAt": "2026-01-01T00:00:00.000Z",
        "updatedAt": "2026-01-01T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baselayout_file,
        "changelog": changelog_file
    }
}

out_path = "deck.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {out_path}")
print(f"Slides: {slide_count}")
print(f"Total elements: {total_elements}")
print(f"  text: {total_text}")
print(f"  shapes: {len(shape_elements)}")
print(f"  icons: {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
print(f"  images: {len(image_elements)}")
print(f"  tables: {len(table_elements)}")
