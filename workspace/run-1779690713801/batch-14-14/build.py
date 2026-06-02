import json
import time

NOW = int(time.time() * 1000)

COUNTER = 1950

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              text_align="left", font_family="Inter", letter_spacing=0):
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


def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=80, color="#c67c3a", opacity=1):
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


SLIDE_ID = "slide-14"

text_elements_by_slide = {SLIDE_ID: []}
shape_elements = []
icon_elements = []
changelog_elements = {}


def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_id()
    text_id = f"text-{n}"
    c, cl = make_text(text_id, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements_by_slide[SLIDE_ID].append(c)
    changelog_elements[text_id] = cl
    return text_id


def add_shape(shape_type, x, y, w, h, **kwargs):
    n = next_id()
    shape_id = f"shape-{n}"
    c, cl = make_shape(shape_id, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_elements[shape_id] = cl
    return shape_id


def add_icon(icon_name, x, y, **kwargs):
    n = next_id()
    icon_id = f"icon-{n}"
    c, cl = make_icon(icon_id, SLIDE_ID, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_elements[icon_id] = cl
    return icon_id


# ---------- Color palette ----------
OBSIDIAN  = "#0B1020"
GRAPHITE  = "#171C2E"
BLUEPRINT = "#1E3A5F"
CYAN      = "#22D3EE"
GREEN     = "#22C55E"
AMBER     = "#F59E0B"
RED       = "#EF4444"
LAVENDER  = "#A78BFA"
WHITE     = "#F8FAFC"
STEEL     = "#94A3B8"


# ============== BUILD SLIDE 14 ==============

# --- Background canvas ---
add_shape("rectangle", 0, 0, 1280, 720, fill=OBSIDIAN)

# Subtle horizontal blueprint guides
add_shape("rectangle", 48, 192, 1184, 1, fill=BLUEPRINT, opacity=0.55)
add_shape("rectangle", 48, 588, 1184, 1, fill=BLUEPRINT, opacity=0.35)

# --- Top tag chip ---
add_shape("circle", 48, 64, 8, 8, fill=CYAN)
add_text("OBSERVABILITY  ·  CHAPTER 14", "caption",
         64, 60, 360, 16,
         color=CYAN, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2.5)

# Top-right live indicator
add_shape("circle", 1136, 66, 8, 8, fill=GREEN)
add_text("LIVE  ·  TELEMETRY ONLINE", "caption",
         1152, 62, 200, 14,
         color=GREEN, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1.8)

# --- Title (single line) ---
add_text("Observability is the nervous system.", "title",
         48, 84, 1184, 60,
         color=WHITE, font_size=46, font_weight=700, line_height=1.1,
         font_family="Inter")

# --- Subtitle ---
add_text("Three telemetry signals — logs, metrics, traces — woven into one continuous truth.",
         "paragraph",
         48, 152, 1184, 28,
         color=STEEL, font_size=18, font_weight=400, line_height=1.4,
         font_family="Inter")

# ============== Three telemetry panels ==============

PANEL_Y = 208
PANEL_H = 372
PANEL_W = 384

panels = [
    {
        "x": 48,
        "accent": CYAN,
        "num": "01",
        "label": "STREAM",
        "icon": "ScrollText",
        "heading": "Logs",
        "desc": "Structured contextual events — the narrative of every request, retry, queue, and worker as it actually happened.",
        "footer_color": GREEN,
        "footer_text": "STREAM HEALTHY  ·  3.2K LOGS / SEC",
    },
    {
        "x": 448,
        "accent": GREEN,
        "num": "02",
        "label": "MEASURE",
        "icon": "Activity",
        "heading": "Metrics",
        "desc": "Time-series signals — latency, throughput, errors, saturation — measured continuously against SLOs.",
        "footer_color": GREEN,
        "footer_text": "SLO MET  ·  99.94% AVAILABILITY",
    },
    {
        "x": 848,
        "accent": LAVENDER,
        "num": "03",
        "label": "CONNECT",
        "icon": "Network",
        "heading": "Traces",
        "desc": "End-to-end spans across services — the map of where time and failure actually live in your system.",
        "footer_color": AMBER,
        "footer_text": "ANOMALY  ·  payments p95 spike",
    },
]

for p in panels:
    px = p["x"]
    accent = p["accent"]

    # Card background
    add_shape("rectangle", px, PANEL_Y, PANEL_W, PANEL_H, fill=GRAPHITE)
    # Top accent stripe
    add_shape("rectangle", px, PANEL_Y, PANEL_W, 3, fill=accent)
    # Vertical edge marker (left side)
    add_shape("rectangle", px, PANEL_Y, 2, 32, fill=accent, opacity=0.85)

    # Numbered caption
    add_text(f"{p['num']}  ·  {p['label']}", "caption",
             px + 24, PANEL_Y + 24, 240, 14,
             color=accent, font_size=11, font_weight=600,
             font_family="JetBrains Mono", letter_spacing=2)

    # Icon top-right
    add_icon(p["icon"], px + PANEL_W - 56, PANEL_Y + 20,
             size=32, color=accent, opacity=0.85)

    # Heading
    add_text(p["heading"], "heading",
             px + 24, PANEL_Y + 52, PANEL_W - 48, 44,
             color=WHITE, font_size=34, font_weight=700, line_height=1.1,
             font_family="Inter")

    # Description
    add_text(p["desc"], "paragraph",
             px + 24, PANEL_Y + 108, PANEL_W - 48, 76,
             color=STEEL, font_size=14, font_weight=400, line_height=1.55,
             font_family="Inter")

    # Status footer dot + text
    add_shape("circle", px + 24, PANEL_Y + PANEL_H - 28, 6, 6, fill=p["footer_color"])
    add_text(p["footer_text"], "caption",
             px + 38, PANEL_Y + PANEL_H - 30, PANEL_W - 64, 14,
             color=STEEL, font_size=10, font_weight=600,
             font_family="JetBrains Mono", letter_spacing=1.5)


# ============== Mini visualizations ==============

VIZ_Y = PANEL_Y + 196     # 404
VIZ_H = 132
VIZ_INNER_PAD = 16

# ----- Panel 1: Log stream -----
p1x = 48
viz1_x = p1x + 24
viz1_w = PANEL_W - 48
add_shape("rectangle", viz1_x, VIZ_Y, viz1_w, VIZ_H, fill=OBSIDIAN)
# Tiny header chip
add_text("> tail -f /var/log/app", "caption",
         viz1_x + 12, VIZ_Y + 8, viz1_w - 24, 12,
         color=CYAN, font_size=9, font_weight=500,
         font_family="JetBrains Mono", letter_spacing=0.5)
add_shape("rectangle", viz1_x + 12, VIZ_Y + 24, viz1_w - 24, 1, fill=BLUEPRINT, opacity=0.6)

log_lines = [
    ("12:04:21", "INFO ", "POST /orders 201 84ms",       STEEL),
    ("12:04:22", "WARN ", "queue depth=12 svc=payments", AMBER),
    ("12:04:22", "INFO ", "GET /users/me 200 11ms",      CYAN),
    ("12:04:23", "ERROR", "db.timeout host=primary",     RED),
    ("12:04:23", "INFO ", "trace=abc92f span ok",        STEEL),
]
ly = VIZ_Y + 32
for ts, lvl, msg, col in log_lines:
    add_text(f"{ts}  {lvl}  {msg}", "caption",
             viz1_x + 12, ly, viz1_w - 24, 14,
             color=col, font_size=10, font_weight=500,
             font_family="JetBrains Mono", letter_spacing=0.2)
    ly += 18

# ----- Panel 2: Metrics bars -----
p2x = 448
viz2_x = p2x + 24
viz2_w = PANEL_W - 48
add_shape("rectangle", viz2_x, VIZ_Y, viz2_w, VIZ_H, fill=OBSIDIAN)

# Header label
add_text("p99 LATENCY · ms", "caption",
         viz2_x + 12, VIZ_Y + 8, 200, 12,
         color=STEEL, font_size=9, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1.5)

# Big metric value
add_text("142", "heading",
         viz2_x + viz2_w - 80, VIZ_Y + 4, 68, 24,
         color=WHITE, font_size=20, font_weight=700,
         font_family="JetBrains Mono", text_align="right")
add_text("ms", "caption",
         viz2_x + viz2_w - 14, VIZ_Y + 14, 16, 12,
         color=GREEN, font_size=10, font_weight=600,
         font_family="JetBrains Mono", text_align="right")

# Bars baseline
baseline_y = VIZ_Y + VIZ_H - 14
bar_heights = [14, 22, 18, 30, 24, 38, 32, 46, 38, 54, 44, 60]
bar_w = 16
bar_gap = 7
total_w = len(bar_heights) * bar_w + (len(bar_heights) - 1) * bar_gap
start_x = viz2_x + (viz2_w - total_w) // 2
for i, h in enumerate(bar_heights):
    bx = start_x + i * (bar_w + bar_gap)
    by = baseline_y - h
    col = GREEN if h >= 40 else CYAN
    op = 0.95 if h >= 40 else 0.7
    add_shape("rectangle", bx, by, bar_w, h, fill=col, opacity=op)

# Baseline guide line
add_shape("rectangle", viz2_x + 12, baseline_y + 1, viz2_w - 24, 1,
          fill=BLUEPRINT, opacity=0.6)

# Tiny axis caption
add_text("LAST 12 MIN", "caption",
         viz2_x + 12, VIZ_Y + VIZ_H - 12, 120, 10,
         color=STEEL, font_size=8, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1.2)

# ----- Panel 3: Trace waterfall -----
p3x = 848
viz3_x = p3x + 24
viz3_w = PANEL_W - 48
add_shape("rectangle", viz3_x, VIZ_Y, viz3_w, VIZ_H, fill=OBSIDIAN)

# Header
add_text("trace abc92f  ·  4 spans", "caption",
         viz3_x + 12, VIZ_Y + 8, 240, 12,
         color=LAVENDER, font_size=9, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=1)

# Span rows
span_track_left = viz3_x + 84
span_track_right = viz3_x + viz3_w - 16
span_track_w = span_track_right - span_track_left

trace_spans = [
    ("gateway",  0.00, 0.95, CYAN,     "312ms"),
    ("auth",     0.06, 0.18, GREEN,    "62ms"),
    ("orders",   0.28, 0.45, LAVENDER, "148ms"),
    ("payments", 0.62, 0.30, AMBER,    "98ms"),
]
ty = VIZ_Y + 30
for label, off_pct, w_pct, col, dur in trace_spans:
    bar_x = span_track_left + int(span_track_w * off_pct)
    bar_w_px = max(8, int(span_track_w * w_pct))
    # span bar
    add_shape("rectangle", bar_x, ty + 4, bar_w_px, 6, fill=col, opacity=0.9)
    # service label
    add_text(label, "caption",
             viz3_x + 12, ty + 1, 70, 12,
             color=STEEL, font_size=10, font_weight=500,
             font_family="JetBrains Mono")
    # duration
    add_text(dur, "caption",
             viz3_x + viz3_w - 50, ty + 1, 38, 12,
             color=col, font_size=9, font_weight=600,
             font_family="JetBrains Mono", text_align="right")
    ty += 18

# Anomaly callout below traces
add_shape("rectangle", viz3_x + 12, VIZ_Y + VIZ_H - 22, viz3_w - 24, 1,
          fill=BLUEPRINT, opacity=0.5)
add_text("⌁ payments span 2.4× baseline", "caption",
         viz3_x + 12, VIZ_Y + VIZ_H - 14, 240, 10,
         color=AMBER, font_size=9, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=0.8)


# ============== Bottom insight band ==============

# Amber accent bar
add_shape("rectangle", 48, 612, 28, 2, fill=AMBER)
add_text("THE GOLDEN THREAD", "caption",
         84, 608, 220, 12,
         color=AMBER, font_size=11, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2.4)

add_text("“You can’t fix what you can’t see — observability turns silent failure into a story you can read.”",
         "paragraph",
         48, 632, 1184, 30,
         color=WHITE, font_size=18, font_weight=500, line_height=1.4,
         font_family="Inter")

# --- Footer line ---
add_text("14 / 15  ·  ENGINEERING EXCELLENCE", "caption",
         48, 686, 400, 14,
         color=STEEL, font_size=10, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2)

add_text("LOGS  ·  METRICS  ·  TRACES", "caption",
         832, 686, 400, 14,
         color=STEEL, font_size=10, font_weight=600,
         font_family="JetBrains Mono", letter_spacing=2.4, text_align="right")


# ============== ASSEMBLE FILES ==============

slide = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": OBSIDIAN,
    "textElements": text_elements_by_slide[SLIDE_ID]
}

content = {
    "slides": [slide],
    "imageElements": [],
    "shapeElements": shape_elements,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

base_layout = {
    "version": "v1",
    "slides": [{
        "id": SLIDE_ID,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    }],
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
    len(text_elements_by_slide[SLIDE_ID])
    + len(shape_elements)
    + len(icon_elements)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}",
        "title": "Engineering Excellence — Slide 14: Observability Is the Nervous System",
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

with open("slide-14.json", "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote slide-14.json")
print(f"Slide count: 1")
print(f"Text elements:  {len(text_elements_by_slide[SLIDE_ID])}")
print(f"Shape elements: {len(shape_elements)}")
print(f"Icon elements:  {len(icon_elements)}")
print(f"Total element count: {element_count}")
print(f"Final ID counter: {COUNTER}")
print(f"First ID = text-1951, Last ID = element-{COUNTER}")
