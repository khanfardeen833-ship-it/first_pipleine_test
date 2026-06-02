import json
import time

NOW = int(time.time() * 1000)

# ID + zIndex counter starts at 600, so first element = 601
COUNTER = 600

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ----------- Helper Functions -----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#D8DEE9", font_size=None, font_weight=None, line_height=None,
              font_family="Inter", text_align="left", letter_spacing=0):
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
               fill="#2F80FF", stroke=None, stroke_width=0, opacity=1):
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
              size=80, color="#21D4FD", opacity=1):
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


def make_table(table_id, slide_id, x, y, zidx, now,
               col_widths, row_heights, cells,
               font_size=20, table_color="#D8DEE9", table_bg="#0B1020"):
    content_record = {
        "id": table_id, "slideId": slide_id, "groupId": None,
        "type": "table",
        "position": {"x": x, "y": y},
        "zIndex": zidx,
        "cells": cells,
        "colWidths": col_widths,
        "rowHeights": row_heights,
        "tableFontSize": font_size,
        "tableBold": False, "tableItalic": False,
        "tableAlign": "left",
        "tableColor": table_color, "tableBg": table_bg
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "zIndex": zidx,
        "updatedAt": now,
        "style": {"colWidths": col_widths, "rowHeights": row_heights}
    }
    return content_record, changelog_record


# ----------- State -----------
text_elements_by_slide = {f"slide-{i}": [] for i in range(11, 16)}
shape_elements = []
image_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {f"slide-{i}": {"elements": {}} for i in range(11, 16)}

# Color palette
OBSIDIAN = "#0B1020"
NAVY = "#111A33"
AZURE = "#2F80FF"
CYAN = "#21D4FD"
VIOLET = "#8B5CF6"
GREEN = "#22C55E"
AMBER = "#F59E0B"
MINT = "#7DD3FC"
SILVER = "#D8DEE9"
WHITE = "#F8FAFC"
RED = "#EF4444"
GRAPHITE = "#1A2236"


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid

def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid

def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid

def add_image(slide_id, src, x, y, w, h, **kwargs):
    n = next_id()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, src, x, y, w, h, n, NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid

def add_table(slide_id, x, y, col_widths, row_heights, cells, **kwargs):
    n = next_id()
    tid = f"table-{n}"
    c, cl = make_table(tid, slide_id, x, y, n, NOW, col_widths, row_heights, cells, **kwargs)
    table_elements.append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


# ============================================================
# SLIDE 11 — Deployment as a Cinematic Release
# ============================================================
sid = "slide-11"

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN)
# Decorative grid stripes
add_shape(sid, "rectangle", 0, 0, 1280, 1, fill=NAVY, opacity=0.5)
add_shape(sid, "rectangle", 0, 719, 1280, 1, fill=NAVY, opacity=0.5)

# Top metadata strip
add_text(sid, "RELEASE / / PIPELINE  ·  CHAPTER 11", "caption", 48, 32, 600, 24,
         color=CYAN, font_family="JetBrains Mono", font_size=12, letter_spacing=2)
add_text(sid, "v1.4.2 → prod", "caption", 1080, 32, 152, 24,
         color=AMBER, font_family="JetBrains Mono", font_size=12, text_align="right", letter_spacing=1)

# Hero title
add_text(sid, "Deployment as a", "title", 48, 72, 1184, 72,
         color=WHITE, font_size=64, font_weight=600, line_height=1.0)
add_text(sid, "Cinematic Release", "title", 48, 144, 1184, 72,
         color=CYAN, font_size=64, font_weight=600, line_height=1.0)

# Subtitle
add_text(sid, "Six stages, one continuous heartbeat — from commit to observability.", "paragraph",
         48, 224, 1100, 32, color=SILVER, font_size=20, font_weight=400)

# ----- Pipeline horizontal track -----
TRACK_Y = 296
TRACK_H = 88
add_shape(sid, "rectangle", 48, TRACK_Y, 1184, TRACK_H, fill=NAVY, opacity=0.65)
# Connecting line
add_shape(sid, "rectangle", 80, TRACK_Y + TRACK_H/2 - 1, 1120, 2, fill=CYAN, opacity=0.4)

stages = [
    ("GitBranch", "COMMIT", AZURE),
    ("Hammer",   "BUILD",  AZURE),
    ("FlaskConical", "TEST", VIOLET),
    ("ShieldCheck", "SCAN", AMBER),
    ("Rocket",   "DEPLOY", GREEN),
    ("Activity", "OBSERVE", CYAN),
]
stage_w = 1120 / 6
for i, (icon_name, label, col) in enumerate(stages):
    cx = 80 + int(i * stage_w + stage_w/2)
    # node circle
    add_shape(sid, "circle", cx - 24, TRACK_Y + TRACK_H/2 - 24, 48, 48, fill=col, opacity=0.95)
    add_icon(sid, icon_name, cx - 14, TRACK_Y + TRACK_H/2 - 14, size=28, color=WHITE)
    add_text(sid, label, "caption", cx - 60, TRACK_Y + TRACK_H + 10, 120, 20,
             color=SILVER, font_family="JetBrains Mono", font_size=12,
             font_weight=600, text_align="center", letter_spacing=2)

# ----- Three deployment strategy panels -----
PANEL_Y = 448
PANEL_H = 224
panels = [
    ("BLUE / GREEN", "Two identical environments. Switch traffic atomically. Rollback in seconds.",
     AZURE, "0% → 100% switch", "Zero downtime swap"),
    ("CANARY", "Promote to a small slice first. Watch SLOs. Expand confidently.",
     VIOLET, "5% → 25% → 100%", "Risk-aware rollout"),
    ("ROLLING", "Replace pods in waves. maxSurge & maxUnavailable govern velocity.",
     GREEN, "maxSurge: 25%", "Continuous reconciliation"),
]
panel_w = (1184 - 32) / 3  # 384
for i, (title, desc, col, code, sub) in enumerate(panels):
    px = 48 + int(i * (panel_w + 16))
    # Panel background
    add_shape(sid, "rectangle", px, PANEL_Y, int(panel_w), PANEL_H, fill=NAVY, opacity=0.8)
    # Top accent bar
    add_shape(sid, "rectangle", px, PANEL_Y, int(panel_w), 4, fill=col)
    # Title
    add_text(sid, title, "caption", px + 20, PANEL_Y + 20, int(panel_w) - 40, 22,
             color=col, font_family="JetBrains Mono", font_size=13, letter_spacing=3)
    # Strategy heading
    add_text(sid, sub, "subheading", px + 20, PANEL_Y + 48, int(panel_w) - 40, 32,
             color=WHITE, font_size=22, font_weight=600)
    # Description
    add_text(sid, desc, "paragraph", px + 20, PANEL_Y + 96, int(panel_w) - 40, 72,
             color=SILVER, font_size=15, font_weight=400, line_height=1.5)
    # Code chip
    add_shape(sid, "rectangle", px + 20, PANEL_Y + 172, int(panel_w) - 40, 32, fill=OBSIDIAN, opacity=0.9)
    add_text(sid, code, "caption", px + 32, PANEL_Y + 178, int(panel_w) - 60, 20,
             color=col, font_family="JetBrains Mono", font_size=12)


# ============================================================
# SLIDE 12 — The Release Constellation
# ============================================================
sid = "slide-12"

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN)
# Side gradient panels
add_shape(sid, "rectangle", 0, 0, 6, 720, fill=CYAN, opacity=0.6)
add_shape(sid, "rectangle", 1274, 0, 6, 720, fill=VIOLET, opacity=0.5)

# Top meta strip
add_text(sid, "12  ·  THE RELEASE CONSTELLATION", "caption", 48, 32, 600, 22,
         color=CYAN, font_family="JetBrains Mono", font_size=12, letter_spacing=3)
add_text(sid, "kubectl rollout status deployment/api", "caption", 760, 32, 472, 22,
         color=AMBER, font_family="JetBrains Mono", font_size=12, text_align="right")

# Cinematic title
add_text(sid, "Every deployment is", "subtitle", 48, 72, 800, 40,
         color=SILVER, font_size=22, font_weight=400)
add_text(sid, "an intentional path.", "title", 48, 112, 1100, 80,
         color=WHITE, font_size=58, font_weight=700, line_height=1.05)

# ----- Three lanes: Build → Validate → Release -----
LANE_Y = 232
LANE_H = 56
lane_labels = [("BUILD", AZURE, 0), ("VALIDATE", AMBER, 1), ("RELEASE", GREEN, 2)]
for label, col, i in lane_labels:
    ly = LANE_Y + i * (LANE_H + 12)
    add_shape(sid, "rectangle", 48, ly, 280, LANE_H, fill=NAVY, opacity=0.85)
    add_shape(sid, "rectangle", 48, ly, 4, LANE_H, fill=col)
    add_text(sid, label, "caption", 70, ly + 12, 200, 20,
             color=col, font_family="JetBrains Mono", font_size=13, letter_spacing=3)
    add_text(sid, ["Compile · Containerize · Sign", "Test · Scan · Approve", "Canary · Promote · Observe"][i],
             "caption", 70, ly + 32, 220, 18, color=SILVER, font_size=11, font_weight=400)

# Connector line from lanes
add_shape(sid, "rectangle", 328, LANE_Y + 28, 96, 2, fill=CYAN, opacity=0.6)
add_shape(sid, "rectangle", 328, LANE_Y + LANE_H + 12 + 28, 96, 2, fill=AMBER, opacity=0.6)
add_shape(sid, "rectangle", 328, LANE_Y + 2*(LANE_H + 12) + 28, 96, 2, fill=GREEN, opacity=0.6)

# ----- Production environments (right side) -----
ENV_X = 440
env_titles = [
    ("PROD-EU-WEST", "Pods 12 / 12", GREEN),
    ("PROD-US-EAST", "Pods 18 / 18", GREEN),
    ("CANARY-NA", "Traffic 25%", AMBER),
]
for i, (n, sub, col) in enumerate(env_titles):
    ex = ENV_X
    ey = LANE_Y + i * (LANE_H + 12)
    add_shape(sid, "rectangle", ex, ey, 240, LANE_H, fill=GRAPHITE, opacity=0.9)
    add_shape(sid, "circle", ex + 16, ey + LANE_H/2 - 6, 12, 12, fill=col)
    add_text(sid, n, "caption", ex + 36, ey + 10, 200, 20,
             color=WHITE, font_family="JetBrains Mono", font_size=13, font_weight=600)
    add_text(sid, sub, "caption", ex + 36, ey + 30, 200, 18,
             color=SILVER, font_size=12, font_weight=400)

# ----- Right side: traffic split visualization -----
TS_X = 720
TS_Y = 232
add_text(sid, "TRAFFIC SHIFT", "caption", TS_X, TS_Y - 20, 200, 18,
         color=CYAN, font_family="JetBrains Mono", font_size=11, letter_spacing=3)
# Bars representing 5% → 25% → 100%
bar_specs = [("5%", 24, VIOLET), ("25%", 120, AMBER), ("100%", 480, GREEN)]
bar_y = TS_Y
for label, w, col in bar_specs:
    add_shape(sid, "rectangle", TS_X, bar_y, 480, 28, fill=NAVY, opacity=0.7)
    add_shape(sid, "rectangle", TS_X, bar_y, w, 28, fill=col, opacity=0.95)
    add_text(sid, label, "caption", TS_X + 488, bar_y + 4, 60, 22,
             color=WHITE, font_family="JetBrains Mono", font_size=14, font_weight=600)
    bar_y += 40

# ----- Bottom code card -----
CC_X, CC_Y, CC_W, CC_H = 48, 460, 600, 196
add_shape(sid, "rectangle", CC_X, CC_Y, CC_W, CC_H, fill="#070B18")
add_shape(sid, "rectangle", CC_X, CC_Y, CC_W, 28, fill=NAVY)
# Window dots
add_shape(sid, "circle", CC_X + 12, CC_Y + 10, 8, 8, fill="#FF5F56")
add_shape(sid, "circle", CC_X + 28, CC_Y + 10, 8, 8, fill="#FFBD2E")
add_shape(sid, "circle", CC_X + 44, CC_Y + 10, 8, 8, fill=GREEN)
add_text(sid, "rollout.yaml", "caption", CC_X + 64, CC_Y + 6, 300, 18,
         color=SILVER, font_family="JetBrains Mono", font_size=12)

code_lines = [
    ("strategy:", CYAN),
    ("  type: canary", WHITE),
    ("  steps:", WHITE),
    ("    - setWeight: 25", AMBER),
    ("    - pause: { duration: 5m }", VIOLET),
    ("    - setWeight: 100", GREEN),
    ("metrics:", CYAN),
    ("  successCondition: result[0] >= 0.995", MINT),
]
for i, (line, col) in enumerate(code_lines):
    add_text(sid, line, "caption", CC_X + 24, CC_Y + 40 + i * 18, CC_W - 40, 18,
             color=col, font_family="JetBrains Mono", font_size=13, font_weight=400)

# Bottom-right callout
CO_X, CO_Y = 680, 460
add_shape(sid, "rectangle", CO_X, CO_Y, 552, 196, fill=NAVY, opacity=0.85)
add_shape(sid, "rectangle", CO_X, CO_Y, 4, 196, fill=VIOLET)
add_text(sid, "DEPLOYMENT METHOD", "caption", CO_X + 24, CO_Y + 20, 400, 18,
         color=VIOLET, font_family="JetBrains Mono", font_size=12, letter_spacing=3)
add_text(sid, "Canary release", "subtitle", CO_X + 24, CO_Y + 46, 500, 36,
         color=WHITE, font_size=28, font_weight=600)
add_text(sid,
         "Promote to a thin slice. Hold. Measure SLOs. Expand only when error budget remains intact.",
         "paragraph", CO_X + 24, CO_Y + 88, 504, 80,
         color=SILVER, font_size=14, font_weight=400, line_height=1.55)
add_text(sid, "→ blue/green   → canary   → rolling", "caption", CO_X + 24, CO_Y + 168, 504, 20,
         color=CYAN, font_family="JetBrains Mono", font_size=12, letter_spacing=2)


# ============================================================
# SLIDE 13 — Infrastructure as Living Blueprint
# ============================================================
sid = "slide-13"

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=NAVY)
# Blueprint grid (decorative thin lines)
for gx in range(80, 1280, 80):
    add_shape(sid, "rectangle", gx, 0, 1, 720, fill=CYAN, opacity=0.05)
for gy in range(80, 720, 80):
    add_shape(sid, "rectangle", 0, gy, 1280, 1, fill=CYAN, opacity=0.05)

# Top meta
add_text(sid, "13  ·  INFRASTRUCTURE AS CODE", "caption", 48, 32, 600, 22,
         color=MINT, font_family="JetBrains Mono", font_size=12, letter_spacing=3)
add_text(sid, "terraform plan → apply", "caption", 880, 32, 352, 22,
         color=SILVER, font_family="JetBrains Mono", font_size=12, text_align="right")

# Title
add_text(sid, "Infrastructure as", "title", 48, 72, 1184, 64,
         color=WHITE, font_size=52, font_weight=600, line_height=1.0)
add_text(sid, "a living blueprint.", "title", 48, 132, 1184, 64,
         color=MINT, font_size=52, font_weight=600, line_height=1.0)
add_text(sid,
         "Declared, versioned, reviewed. The diagram is generated — not drawn.",
         "paragraph", 48, 200, 1100, 28, color=SILVER, font_size=18, font_weight=400)

# ===== LEFT: Code panel (frosted glass) =====
CP_X, CP_Y, CP_W, CP_H = 48, 256, 568, 416
add_shape(sid, "rectangle", CP_X, CP_Y, CP_W, CP_H, fill="#0A1228", opacity=0.95)
add_shape(sid, "rectangle", CP_X, CP_Y, 4, CP_H, fill=MINT)
# header
add_shape(sid, "rectangle", CP_X, CP_Y, CP_W, 32, fill=OBSIDIAN, opacity=0.95)
add_icon(sid, "FileCode", CP_X + 16, CP_Y + 7, size=18, color=MINT)
add_text(sid, "main.tf", "caption", CP_X + 44, CP_Y + 8, 300, 18,
         color=SILVER, font_family="JetBrains Mono", font_size=12)
add_text(sid, "● aws  · us-east-1", "caption", CP_X + CP_W - 180, CP_Y + 8, 160, 18,
         color=GREEN, font_family="JetBrains Mono", font_size=11, text_align="right")

# code block
tf_lines = [
    ('resource "aws_vpc" "main" {',                       CYAN, "1"),
    ('  cidr_block = "10.0.0.0/16"',                       WHITE, "2"),
    ('  tags = { Name = "prod-vpc" }',                     MINT, "3"),
    ('}',                                                  CYAN, "4"),
    ('',                                                   WHITE, "5"),
    ('resource "aws_ecs_service" "api" {',                 CYAN, "6"),
    ('  name             = "api"',                         WHITE, "7"),
    ('  cluster          = aws_ecs_cluster.prod.id',       VIOLET, "8"),
    ('  desired_count    = 3',                             AMBER, "9"),
    ('  launch_type      = "FARGATE"',                     WHITE, "10"),
    ('  deployment_controller {',                          CYAN, "11"),
    ('    type = "CODE_DEPLOY"',                           GREEN, "12"),
    ('  }',                                                CYAN, "13"),
    ('}',                                                  CYAN, "14"),
    ('',                                                   WHITE, "15"),
    ('# policy guardrails enforced via OPA',               "#6B7280", "16"),
]
for i, (line, col, ln) in enumerate(tf_lines):
    ly = CP_Y + 48 + i * 22
    # line number
    add_text(sid, ln, "caption", CP_X + 18, ly, 28, 20,
             color="#475569", font_family="JetBrains Mono", font_size=11, text_align="right")
    add_text(sid, line, "caption", CP_X + 56, ly, CP_W - 72, 20,
             color=col, font_family="JetBrains Mono", font_size=12, font_weight=400)

# ===== RIGHT: Generated architecture diagram =====
DG_X, DG_Y, DG_W, DG_H = 648, 256, 584, 416
add_shape(sid, "rectangle", DG_X, DG_Y, DG_W, DG_H, fill=OBSIDIAN, opacity=0.85)
add_text(sid, "GENERATED ARCHITECTURE", "caption", DG_X + 20, DG_Y + 16, 400, 18,
         color=MINT, font_family="JetBrains Mono", font_size=11, letter_spacing=3)
add_text(sid, "▲ apply complete · 14 resources", "caption", DG_X + DG_W - 280, DG_Y + 16, 260, 18,
         color=GREEN, font_family="JetBrains Mono", font_size=11, text_align="right")

# Outer VPC frame
VPC_X, VPC_Y, VPC_W, VPC_H = DG_X + 24, DG_Y + 56, DG_W - 48, DG_H - 80
add_shape(sid, "rectangle", VPC_X, VPC_Y, VPC_W, VPC_H, fill=NAVY, opacity=0.6,
          stroke=MINT, stroke_width=1)
add_text(sid, "VPC  10.0.0.0/16", "caption", VPC_X + 12, VPC_Y + 8, 200, 16,
         color=MINT, font_family="JetBrains Mono", font_size=10, letter_spacing=2)

# Public subnet
PS_X, PS_Y, PS_W, PS_H = VPC_X + 16, VPC_Y + 32, VPC_W - 32, 96
add_shape(sid, "rectangle", PS_X, PS_Y, PS_W, PS_H, fill=GRAPHITE, opacity=0.7)
add_text(sid, "PUBLIC  · IGW · ALB", "caption", PS_X + 10, PS_Y + 6, 200, 16,
         color=CYAN, font_family="JetBrains Mono", font_size=10, letter_spacing=2)
# IGW + ALB nodes
add_shape(sid, "circle", PS_X + 32, PS_Y + 36, 36, 36, fill=AZURE, opacity=0.95)
add_icon(sid, "Globe", PS_X + 41, PS_Y + 45, size=18, color=WHITE)
add_text(sid, "IGW", "caption", PS_X + 22, PS_Y + 74, 56, 14,
         color=SILVER, font_family="JetBrains Mono", font_size=10, text_align="center")

add_shape(sid, "rectangle", PS_X + 132, PS_Y + 32, 96, 44, fill=AZURE, opacity=0.95)
add_text(sid, "ALB", "caption", PS_X + 132, PS_Y + 46, 96, 18,
         color=WHITE, font_family="JetBrains Mono", font_size=14, text_align="center", font_weight=600)
# Connector
add_shape(sid, "rectangle", PS_X + 68, PS_Y + 52, 64, 2, fill=CYAN, opacity=0.7)

# Private subnet (ECS + RDS)
PR_X, PR_Y, PR_W, PR_H = VPC_X + 16, VPC_Y + 144, VPC_W - 32, 184
add_shape(sid, "rectangle", PR_X, PR_Y, PR_W, PR_H, fill=GRAPHITE, opacity=0.7)
add_text(sid, "PRIVATE  · ECS · RDS · CACHE", "caption", PR_X + 10, PR_Y + 6, 300, 16,
         color=VIOLET, font_family="JetBrains Mono", font_size=10, letter_spacing=2)

# 3 ECS task pods
pod_labels = ["task-1", "task-2", "task-3"]
for i, lbl in enumerate(pod_labels):
    px = PR_X + 24 + i * 92
    add_shape(sid, "rectangle", px, PR_Y + 36, 76, 56, fill=VIOLET, opacity=0.9)
    add_icon(sid, "Container", px + 24, PR_Y + 44, size=24, color=WHITE)
    add_text(sid, lbl, "caption", px, PR_Y + 74, 76, 16,
             color=WHITE, font_family="JetBrains Mono", font_size=11, text_align="center")

# RDS + Cache
add_shape(sid, "rectangle", PR_X + 320, PR_Y + 36, 96, 56, fill=GREEN, opacity=0.9)
add_icon(sid, "Database", PR_X + 354, PR_Y + 44, size=24, color=WHITE)
add_text(sid, "RDS", "caption", PR_X + 320, PR_Y + 74, 96, 16,
         color=WHITE, font_family="JetBrains Mono", font_size=11, text_align="center", font_weight=600)

add_shape(sid, "rectangle", PR_X + 432, PR_Y + 36, 96, 56, fill=AMBER, opacity=0.9)
add_icon(sid, "Zap", PR_X + 466, PR_Y + 44, size=24, color=OBSIDIAN)
add_text(sid, "CACHE", "caption", PR_X + 432, PR_Y + 74, 96, 16,
         color=OBSIDIAN, font_family="JetBrains Mono", font_size=11, text_align="center", font_weight=600)

# Connectors private
add_shape(sid, "rectangle", PR_X + 100, PR_Y + 60, 220, 2, fill=MINT, opacity=0.5)
add_shape(sid, "rectangle", PR_X + 416, PR_Y + 60, 16, 2, fill=MINT, opacity=0.5)

# ALB → ECS connector
add_shape(sid, "rectangle", PS_X + 178, PS_Y + 76, 2, 68, fill=CYAN, opacity=0.5)

# Bottom guardrail strip
GR_Y = PR_Y + PR_H + 12
add_shape(sid, "rectangle", VPC_X + 16, GR_Y, VPC_W - 32, 28, fill=OBSIDIAN, opacity=0.9)
add_icon(sid, "ShieldCheck", VPC_X + 28, GR_Y + 5, size=18, color=GREEN)
add_text(sid, "OPA POLICY · ENCRYPTED · COMPLIANT · IMMUTABLE", "caption",
         VPC_X + 56, GR_Y + 7, VPC_W - 80, 16,
         color=GREEN, font_family="JetBrains Mono", font_size=10, letter_spacing=3)


# ============================================================
# SLIDE 14 — Observability: Seeing the Invisible
# ============================================================
sid = "slide-14"

# Background
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#070B18")

# Top meta strip
add_text(sid, "14  ·  OBSERVABILITY", "caption", 48, 32, 600, 22,
         color=CYAN, font_family="JetBrains Mono", font_size=12, letter_spacing=3)
add_text(sid, "● live  · 4 regions · 1.2M req/min", "caption", 880, 32, 352, 22,
         color=GREEN, font_family="JetBrains Mono", font_size=12, text_align="right")

# Title
add_text(sid, "Seeing the invisible.", "title", 48, 72, 1184, 72,
         color=WHITE, font_size=58, font_weight=700, line_height=1.0)
add_text(sid,
         "Logs, metrics, traces — three signals, one truth.",
         "paragraph", 48, 152, 1100, 28, color=SILVER, font_size=18, font_weight=400)

# ===== Hero metrics row =====
HR_Y = 200
metrics = [
    ("99.95%", "AVAILABILITY", GREEN),
    ("p95 180ms", "LATENCY", CYAN),
    ("0.3%", "ERROR RATE", AMBER),
    ("47%", "ERROR BUDGET", VIOLET),
]
mw = (1184 - 48) / 4  # 284
for i, (val, lbl, col) in enumerate(metrics):
    mx = 48 + int(i * (mw + 16))
    add_shape(sid, "rectangle", mx, HR_Y, int(mw), 88, fill=NAVY, opacity=0.9)
    add_shape(sid, "rectangle", mx, HR_Y, 3, 88, fill=col)
    add_text(sid, val, "title", mx + 16, HR_Y + 12, int(mw) - 32, 44,
             color=WHITE, font_size=32, font_weight=700, font_family="JetBrains Mono")
    add_text(sid, lbl, "caption", mx + 16, HR_Y + 60, int(mw) - 32, 18,
             color=col, font_family="JetBrains Mono", font_size=11, letter_spacing=3)

# ===== Service map (left, large) =====
SM_X, SM_Y, SM_W, SM_H = 48, 312, 720, 312
add_shape(sid, "rectangle", SM_X, SM_Y, SM_W, SM_H, fill=NAVY, opacity=0.85)
add_text(sid, "SERVICE DEPENDENCY MAP", "caption", SM_X + 20, SM_Y + 16, 400, 18,
         color=CYAN, font_family="JetBrains Mono", font_size=11, letter_spacing=3)

# Service nodes
nodes = [
    ("gateway",   SM_X + 80,  SM_Y + 80, AZURE, "12ms"),
    ("auth",      SM_X + 240, SM_Y + 56, VIOLET, "8ms"),
    ("catalog",   SM_X + 240, SM_Y + 152, CYAN, "22ms"),
    ("orders",    SM_X + 420, SM_Y + 56, GREEN, "34ms"),
    ("payments",  SM_X + 420, SM_Y + 152, AMBER, "180ms"),
    ("notify",    SM_X + 600, SM_Y + 80, VIOLET, "9ms"),
    ("postgres",  SM_X + 240, SM_Y + 240, "#3FB950", "5ms"),
    ("redis",     SM_X + 420, SM_Y + 240, "#FF7B72", "1ms"),
]
# connectors
connections = [
    (0,1),(0,2),(1,3),(1,4),(2,3),(3,5),(4,5),(2,6),(3,7),(4,7)
]
for a, b in connections:
    ax = nodes[a][1] + 32; ay = nodes[a][2] + 16
    bx = nodes[b][1] + 32; by = nodes[b][2] + 16
    # simple horizontal+vertical L line via two rectangles
    if abs(ax - bx) > 2:
        x1 = min(ax, bx); w = abs(ax - bx)
        add_shape(sid, "rectangle", x1, ay, w, 1, fill=CYAN, opacity=0.4)
    if abs(ay - by) > 2:
        y1 = min(ay, by); h = abs(ay - by)
        add_shape(sid, "rectangle", bx, y1, 1, h, fill=CYAN, opacity=0.4)

# render nodes
for name, nx, ny, col, lat in nodes:
    add_shape(sid, "rectangle", nx, ny, 64, 32, fill=col, opacity=0.95)
    add_text(sid, name, "caption", nx, ny + 6, 64, 20,
             color=WHITE, font_family="JetBrains Mono", font_size=10, text_align="center", font_weight=600)
    add_text(sid, lat, "caption", nx, ny + 36, 64, 14,
             color=SILVER, font_family="JetBrains Mono", font_size=9, text_align="center")

# legend
add_text(sid, "● healthy   ◐ degraded   ✕ failing", "caption",
         SM_X + 20, SM_Y + SM_H - 28, 400, 18,
         color=SILVER, font_family="JetBrains Mono", font_size=11)

# ===== Right: 4 telemetry panels =====
PX = 784
PY = 312
PW = 448
panel_h = 72
panel_data = [
    ("LOGS",    "FileText",  "1.2M / min · 0 errors",   GREEN),
    ("METRICS", "Activity",  "p95 180ms · 99.95% up",   CYAN),
    ("TRACES",  "GitCommitHorizontal", "spans avg 12 hops",       VIOLET),
    ("ALERTS",  "Bell",      "2 active · 1 acked",      AMBER),
]
for i, (n, ic, sub, col) in enumerate(panel_data):
    py = PY + i * (panel_h + 8)
    add_shape(sid, "rectangle", PX, py, PW, panel_h, fill=NAVY, opacity=0.9)
    add_shape(sid, "rectangle", PX, py, 3, panel_h, fill=col)
    add_icon(sid, ic, PX + 18, py + 18, size=36, color=col)
    add_text(sid, n, "caption", PX + 70, py + 14, 200, 18,
             color=col, font_family="JetBrains Mono", font_size=11, letter_spacing=3)
    add_text(sid, sub, "subheading", PX + 70, py + 36, 360, 24,
             color=WHITE, font_size=18, font_weight=500)

# ===== Bottom: SLO burn-rate timeline =====
BT_X, BT_Y, BT_W, BT_H = 48, 638, 1184, 50
add_shape(sid, "rectangle", BT_X, BT_Y, BT_W, BT_H, fill=NAVY, opacity=0.85)
add_text(sid, "SLO BURN RATE  · 24H", "caption", BT_X + 16, BT_Y + 6, 250, 16,
         color=AMBER, font_family="JetBrains Mono", font_size=10, letter_spacing=3)
# Draw 48 bars (every 30 min)
import math
random_seed_vals = [
    8,7,6,7,8,9,10,9,8,7,8,9,11,12,10,9,
    8,7,8,9,10,12,18,22,16,11,9,8,7,8,9,10,
    11,10,9,8,7,7,8,9,10,11,10,9,8,7,7,6
]
bar_w = (BT_W - 32) / 48
for i, v in enumerate(random_seed_vals):
    bx = BT_X + 16 + i * bar_w
    bh = max(2, v)
    by = BT_Y + BT_H - 8 - bh
    if v >= 16:
        col = AMBER
    elif v >= 12:
        col = MINT
    else:
        col = GREEN
    add_shape(sid, "rectangle", int(bx), int(by), max(2, int(bar_w - 2)), int(bh), fill=col, opacity=0.95)
add_text(sid, "0.3% errors · within budget", "caption", BT_X + BT_W - 320, BT_Y + 6, 300, 16,
         color=GREEN, font_family="JetBrains Mono", font_size=10, text_align="right", letter_spacing=2)


# ============================================================
# SLIDE 15 — Cloud Architecture North Star
# ============================================================
sid = "slide-15"

# Cosmic gradient background (layered)
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill="#05070F")
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=VIOLET, opacity=0.08)
# subtle vignette accents
add_shape(sid, "circle", -120, -120, 480, 480, fill=AZURE, opacity=0.08)
add_shape(sid, "circle", 920, 480, 520, 520, fill=VIOLET, opacity=0.10)

# Decorative star points
for sx, sy, ssz in [(120, 120, 3),(220, 80, 2),(1100, 90, 3),(1180, 200, 2),
                     (90, 600, 2),(1220, 620, 3),(640, 60, 2),(720, 660, 2)]:
    add_shape(sid, "circle", sx, sy, ssz, ssz, fill=WHITE, opacity=0.7)

# Top meta
add_text(sid, "15  ·  NORTH STAR", "caption", 48, 32, 400, 22,
         color=CYAN, font_family="JetBrains Mono", font_size=12, letter_spacing=4)
add_text(sid, "Cloud Architecture Best Practices", "caption", 800, 32, 432, 22,
         color=SILVER, font_family="JetBrains Mono", font_size=12, text_align="right", letter_spacing=2)

# Hero title
add_text(sid, "The architecture", "subtitle", 48, 80, 1184, 36,
         color=SILVER, font_size=24, font_weight=400, text_align="center")
add_text(sid, "we choose to build.", "title", 48, 116, 1184, 88,
         color=WHITE, font_size=68, font_weight=700, text_align="center", line_height=1.0,
         font_family="Inter")

# ----- Central mandala -----
CX, CY = 640, 408
# Outer orbit ring
add_shape(sid, "circle", CX - 220, CY - 220, 440, 440, fill=AZURE, opacity=0.04,
          stroke=CYAN, stroke_width=1)
# Mid ring
add_shape(sid, "circle", CX - 150, CY - 150, 300, 300, fill=VIOLET, opacity=0.06,
          stroke=VIOLET, stroke_width=1)
# Inner core
add_shape(sid, "circle", CX - 70, CY - 70, 140, 140, fill=NAVY, opacity=0.95)
add_shape(sid, "circle", CX - 50, CY - 50, 100, 100, fill=AZURE, opacity=0.25)
add_shape(sid, "circle", CX - 28, CY - 28, 56, 56, fill=WHITE, opacity=0.95)
add_icon(sid, "Cloud", CX - 18, CY - 18, size=36, color=OBSIDIAN)

# 5 orbiting principle cards
import math as _m
principles = [
    ("Modular",            "Box",           AZURE),
    ("Resilient",          "ShieldCheck",   GREEN),
    ("Automated",          "Workflow",      CYAN),
    ("Observable",         "Activity",      VIOLET),
    ("Secure by Default",  "Lock",          AMBER),
]
ORBIT_R = 220
CARD_W, CARD_H = 168, 72
for i, (name, ic, col) in enumerate(principles):
    angle = -90 + i * (360 / 5)  # start at top
    rad = _m.radians(angle)
    px_ = CX + int(ORBIT_R * _m.cos(rad)) - CARD_W // 2
    py_ = CY + int(ORBIT_R * _m.sin(rad)) - CARD_H // 2
    # card
    add_shape(sid, "rectangle", px_, py_, CARD_W, CARD_H, fill=NAVY, opacity=0.95)
    add_shape(sid, "rectangle", px_, py_, 3, CARD_H, fill=col)
    add_icon(sid, ic, px_ + 14, py_ + 20, size=32, color=col)
    add_text(sid, name, "caption", px_ + 56, py_ + 14, CARD_W - 64, 22,
             color=WHITE, font_size=14, font_weight=600)
    add_text(sid, ["small surface","fail safely","no toil","know everything","zero trust"][i],
             "caption", px_ + 56, py_ + 38, CARD_W - 64, 18,
             color=SILVER, font_family="JetBrains Mono", font_size=10, letter_spacing=1)

# Closing code accent at bottom
CL_X, CL_Y, CL_W, CL_H = 320, 648, 640, 44
add_shape(sid, "rectangle", CL_X, CL_Y, CL_W, CL_H, fill=OBSIDIAN, opacity=0.95)
add_shape(sid, "rectangle", CL_X, CL_Y, 4, CL_H, fill=CYAN)
add_text(sid, "$ deploy with confidence", "caption", CL_X + 20, CL_Y + 6, 320, 18,
         color=CYAN, font_family="JetBrains Mono", font_size=13)
add_text(sid, "build small  ·  deploy safely  ·  observe everything", "caption",
         CL_X + 20, CL_Y + 24, 600, 16,
         color=SILVER, font_family="JetBrains Mono", font_size=11, letter_spacing=2)


# ============================================================
# Build envelope
# ============================================================

slides_content = []
slides_baselayout = []
for i in range(11, 16):
    sid_ = f"slide-{i}"
    slides_content.append({
        "id": sid_,
        "order": i - 11,
        "layoutId": "blank-canvas",
        "backgroundColor": OBSIDIAN if i != 13 else NAVY,
        "textElements": text_elements_by_slide[sid_]
    })
    slides_baselayout.append({
        "id": sid_,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    })

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

# element count
elem_count = (
    sum(len(s["textElements"]) for s in slides_content)
    + len(image_elements) + len(shape_elements) + len(chart_elements)
    + len(table_elements) + len(icon_elements)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-11-15-{NOW}",
        "title": "Cloud Architecture Best Practices",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": elem_count,
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

out = "deck.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(envelope, f, ensure_ascii=False, indent=2)

print(f"Wrote {out}  slides=5  elements={elem_count}")
