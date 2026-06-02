import json
import time

NOW = int(time.time() * 1000)

# ----- ID + zIndex counter (batch starts at 600) -----
COUNTER = 600
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ============== HELPERS ==============

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F4F7FB", font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk",
              text_transform="none"):
    DEFAULTS = {
        "title": (60, 700, 1.05),
        "subtitle": (40, 600, 1.35),
        "heading": (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph": (22, 700, 1.50),
        "caption": (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None: fs = font_size
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
              size=80, color="#00D8FF", opacity=1):
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


def make_table(table_id, slide_id, x, y, zidx, now,
               col_widths, row_heights, cells,
               font_size=18, table_color="#F4F7FB", table_bg="#0B0E1A"):
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


# ============== STATE ==============
text_by_slide = {f"slide-{i}": [] for i in range(11, 16)}
shape_elements = []
image_elements = []
icon_elements = []
table_elements = []
chart_elements = []
changelog_slides = {f"slide-{i}": {"elements": {}} for i in range(11, 16)}
slide_bgs = {}


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


def add_table(slide_id, x, y, col_widths, row_heights, cells, **kwargs):
    n = next_id()
    tid = f"table-{n}"
    c, cl = make_table(tid, slide_id, x, y, n, NOW, col_widths, row_heights, cells, **kwargs)
    table_elements.append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


# ============== PALETTE ==============
SIGNAL_BLACK = "#05060A"
NEURAL_WHITE = "#F4F7FB"
SAFETY_RED = "#FF335C"
ALIGN_VIOLET = "#7C3CFF"
ROBUST_CYAN = "#00D8FF"
INTERP_GOLD = "#FFC857"
OVERSIGHT_BLUE = "#2D6BFF"
LATENT_GREEN = "#19E68C"
UNCERT_MAGENTA = "#D946EF"
GRAPHITE = "#2A2E3A"
DEEP_PANEL = "#0B0E1A"


# ============== SLIDE 11 — From Explanation to Control ==============
sid = "slide-11"
slide_bgs[sid] = SIGNAL_BLACK

# Top bar / section index
add_shape(sid, "rectangle", 96, 56, 80, 4, fill=ROBUST_CYAN)
add_text(sid, "11 / INTERPRETABILITY", "caption",
         184, 48, 400, 24, font_family="IBM Plex Mono",
         color=ROBUST_CYAN, font_size=14, letter_spacing=4, text_transform="uppercase")

# Subtle vignette panels (left/right columns and central map)
add_shape(sid, "rectangle", 0, 0, 1280, 720, fill=SIGNAL_BLACK, opacity=1)

# Central topographic behavior map background
add_shape(sid, "rectangle", 312, 168, 656, 360, fill=DEEP_PANEL, opacity=1)
# topographic contour rings (concentric ellipses)
add_shape(sid, "circle", 472, 248, 336, 200, fill=DEEP_PANEL, stroke=ROBUST_CYAN, stroke_width=1, opacity=0.35)
add_shape(sid, "circle", 512, 272, 256, 152, fill=DEEP_PANEL, stroke=ROBUST_CYAN, stroke_width=1, opacity=0.5)
add_shape(sid, "circle", 552, 296, 176, 104, fill=DEEP_PANEL, stroke=LATENT_GREEN, stroke_width=2, opacity=0.7)
add_shape(sid, "circle", 592, 320, 96, 56, fill=LATENT_GREEN, opacity=0.18)

# Risk zones (red pulses)
add_shape(sid, "circle", 360, 200, 56, 56, fill=SAFETY_RED, opacity=0.85)
add_shape(sid, "circle", 880, 440, 40, 40, fill=SAFETY_RED, opacity=0.8)
add_shape(sid, "circle", 800, 200, 32, 32, fill=UNCERT_MAGENTA, opacity=0.85)

# Safe corridor line
add_shape(sid, "line", 360, 480, 600, 2, fill=LATENT_GREEN, opacity=0.95)

# Hero headline (lower-left editorial title)
add_text(sid, "FROM EXPLANATION", "title", 96, 552, 760, 60,
         font_size=56, font_weight=800, color=NEURAL_WHITE, letter_spacing=-1)
add_text(sid, "TO CONTROL.", "title", 96, 612, 760, 60,
         font_size=56, font_weight=800, color=ROBUST_CYAN, letter_spacing=-1)

# Big editorial topline
add_text(sid, "Interpretability becomes an active safety instrument —",
         "paragraph", 96, 96, 600, 32,
         font_size=22, font_weight=500, color=NEURAL_WHITE, line_height=1.4)
add_text(sid, "not a microscope, but a steering wheel.",
         "paragraph", 96, 128, 600, 32,
         font_size=22, font_weight=500, color="#A8B0C2", line_height=1.4)

# Key phrase
add_text(sid, "Understand  →  Intervene  →  Verify", "heading",
         312, 540, 656, 36, font_size=22, font_weight=700,
         color=INTERP_GOLD, letter_spacing=2,
         text_transform="uppercase", font_family="IBM Plex Mono", text_align="center")

# Map labels (mono)
add_text(sid, "RISK ZONE", "caption", 320, 248, 120, 16,
         font_family="IBM Plex Mono", font_size=11, color=SAFETY_RED, letter_spacing=2)
add_text(sid, "SAFE CORRIDOR", "caption", 380, 460, 160, 16,
         font_family="IBM Plex Mono", font_size=11, color=LATENT_GREEN, letter_spacing=2)
add_text(sid, "EMERGENT", "caption", 760, 176, 120, 16,
         font_family="IBM Plex Mono", font_size=11, color=UNCERT_MAGENTA, letter_spacing=2)

# Right column: three panels (Inspection, Intervention, Verification)
def panel(slide_id, x, y, label, num, title, body, color, icon_name):
    add_shape(slide_id, "rectangle", x, y, 224, 96, fill=DEEP_PANEL)
    add_shape(slide_id, "rectangle", x, y, 4, 96, fill=color)
    add_text(slide_id, num, "caption", x + 16, y + 12, 60, 16,
             font_family="IBM Plex Mono", font_size=11, color=color, letter_spacing=3)
    add_text(slide_id, label, "caption", x + 60, y + 12, 160, 16,
             font_family="IBM Plex Mono", font_size=11, color="#A8B0C2", letter_spacing=2)
    add_text(slide_id, title, "heading", x + 16, y + 32, 200, 26,
             font_size=18, font_weight=700, color=NEURAL_WHITE)
    add_text(slide_id, body, "caption", x + 16, y + 60, 200, 32,
             font_size=12, font_weight=400, color="#A8B0C2", line_height=1.4)

panel(sid, 1024, 168, "PANEL", "01", "Inspection",
      "Trace activations to features and circuits.",
      ROBUST_CYAN, "Eye")
panel(sid, 1024, 280, "PANEL", "02", "Intervention",
      "Edit weights, ablate features, steer behavior.",
      INTERP_GOLD, "SlidersHorizontal")
panel(sid, 1024, 392, "PANEL", "03", "Verification",
      "Prove the change holds across distributions.",
      LATENT_GREEN, "ShieldCheck")

# Footer
add_text(sid, "MECHANISTIC INTERPRETABILITY · ACTIVATION STEERING · CAUSAL TRACING",
         "caption", 96, 680, 1088, 16,
         font_family="IBM Plex Mono", font_size=11, color="#5C6478",
         letter_spacing=4, text_align="center")


# ============== SLIDE 12 — Human-in-the-Loop Control Room ==============
sid = "slide-12"
slide_bgs[sid] = SIGNAL_BLACK

# Hero photo: control room, full-bleed
add_image(sid,
          "https://images.pexels.com/photos/16129703/pexels-photo-16129703.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          0, 0, 1280, 720, is_background=True, opacity=0.55)

# Dark gradient overlay panels for legibility
add_shape(sid, "rectangle", 0, 0, 1280, 200, fill=SIGNAL_BLACK, opacity=0.85)
add_shape(sid, "rectangle", 0, 480, 1280, 240, fill=SIGNAL_BLACK, opacity=0.88)

# Top: section chip
add_shape(sid, "rectangle", 96, 56, 80, 4, fill=OVERSIGHT_BLUE)
add_text(sid, "12 / DEPLOYMENT OVERSIGHT", "caption",
         184, 48, 400, 24, font_family="IBM Plex Mono",
         color=OVERSIGHT_BLUE, font_size=14, letter_spacing=4, text_transform="uppercase")

# Headline
add_text(sid, "THE HUMAN-IN-THE-LOOP", "title",
         96, 88, 1088, 60, font_size=52, font_weight=800,
         color=NEURAL_WHITE, letter_spacing=-1)
add_text(sid, "CONTROL ROOM.", "title",
         96, 144, 1088, 60, font_size=52, font_weight=800,
         color=OVERSIGHT_BLUE, letter_spacing=-1)

# Three column dashboards (mid-band, semi-transparent glass)
# Column 1: Live Model Status
add_shape(sid, "rectangle", 96, 240, 336, 220, fill=DEEP_PANEL, opacity=0.92)
add_shape(sid, "rectangle", 96, 240, 336, 4, fill=LATENT_GREEN)
add_text(sid, "LIVE MODEL STATUS", "caption", 112, 256, 300, 16,
         font_family="IBM Plex Mono", font_size=11, color=LATENT_GREEN, letter_spacing=3)
add_text(sid, "Operational", "heading", 112, 280, 300, 32,
         font_size=26, font_weight=700, color=NEURAL_WHITE)

add_text(sid, "Latency", "caption", 112, 324, 100, 14,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B")
add_text(sid, "84 ms", "subheading", 112, 340, 120, 24,
         font_size=18, font_weight=600, color=NEURAL_WHITE, font_family="IBM Plex Mono")

add_text(sid, "Refusal rate", "caption", 232, 324, 120, 14,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B")
add_text(sid, "2.1%", "subheading", 232, 340, 120, 24,
         font_size=18, font_weight=600, color=NEURAL_WHITE, font_family="IBM Plex Mono")

add_text(sid, "Eval pass", "caption", 112, 384, 120, 14,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B")
add_text(sid, "98.4%", "subheading", 112, 400, 120, 24,
         font_size=18, font_weight=600, color=LATENT_GREEN, font_family="IBM Plex Mono")

add_text(sid, "Drift index", "caption", 232, 384, 120, 14,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B")
add_text(sid, "0.12", "subheading", 232, 400, 120, 24,
         font_size=18, font_weight=600, color=NEURAL_WHITE, font_family="IBM Plex Mono")

add_icon(sid, "Activity", 376, 256, size=24, color=LATENT_GREEN)

# Column 2: Risk Alerts
add_shape(sid, "rectangle", 472, 240, 336, 220, fill=DEEP_PANEL, opacity=0.92)
add_shape(sid, "rectangle", 472, 240, 336, 4, fill=SAFETY_RED)
add_text(sid, "RISK ALERTS", "caption", 488, 256, 300, 16,
         font_family="IBM Plex Mono", font_size=11, color=SAFETY_RED, letter_spacing=3)
add_text(sid, "3 active", "heading", 488, 280, 300, 32,
         font_size=26, font_weight=700, color=NEURAL_WHITE)

# Alert rows
alerts = [
    ("HIGH", "Jailbreak pattern detected", SAFETY_RED, 332),
    ("MED", "Unusual tool-use loop", INTERP_GOLD, 372),
    ("MED", "Drift on safety eval #14", INTERP_GOLD, 412),
]
for tag, msg, col, y in alerts:
    add_shape(sid, "rectangle", 488, y, 56, 18, fill=col, opacity=0.95)
    add_text(sid, tag, "caption", 488, y + 2, 56, 14,
             font_family="IBM Plex Mono", font_size=10, color=SIGNAL_BLACK,
             letter_spacing=2, text_align="center")
    add_text(sid, msg, "caption", 552, y + 2, 240, 14,
             font_family="IBM Plex Mono", font_size=12, color=NEURAL_WHITE)

add_icon(sid, "AlertTriangle", 752, 256, size=24, color=SAFETY_RED)

# Column 3: Human Approval Checkpoints
add_shape(sid, "rectangle", 848, 240, 336, 220, fill=DEEP_PANEL, opacity=0.92)
add_shape(sid, "rectangle", 848, 240, 336, 4, fill=OVERSIGHT_BLUE)
add_text(sid, "HUMAN CHECKPOINTS", "caption", 864, 256, 320, 16,
         font_family="IBM Plex Mono", font_size=11, color=OVERSIGHT_BLUE, letter_spacing=3)
add_text(sid, "12 pending", "heading", 864, 280, 320, 32,
         font_size=26, font_weight=700, color=NEURAL_WHITE)

checks = [
    ("Capability tier upgrade", "L4 reviewer", LATENT_GREEN, 332),
    ("New tool registration", "Policy team", INTERP_GOLD, 372),
    ("Public deployment gate", "Safety council", OVERSIGHT_BLUE, 412),
]
for label, who, col, y in checks:
    add_shape(sid, "circle", 864, y + 2, 12, 12, fill=col)
    add_text(sid, label, "caption", 884, y, 220, 14,
             font_size=12, font_weight=600, color=NEURAL_WHITE)
    add_text(sid, who, "caption", 884, y + 16, 220, 12,
             font_family="IBM Plex Mono", font_size=10, color="#7E879B")

add_icon(sid, "ShieldCheck", 1128, 256, size=24, color=OVERSIGHT_BLUE)

# Bottom strip: governance pipeline
add_text(sid, "GOVERNANCE PIPELINE", "caption", 96, 504, 400, 16,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B", letter_spacing=3)
stages = ["Submit", "Triage", "Eval", "Review", "Approve", "Deploy"]
sx = 96
sw = 176
sgap = 8
for i, s in enumerate(stages):
    bx = sx + i * (sw + sgap)
    bcol = OVERSIGHT_BLUE if i < 4 else LATENT_GREEN
    add_shape(sid, "rectangle", bx, 532, sw, 48, fill=DEEP_PANEL, opacity=0.92)
    add_shape(sid, "rectangle", bx, 532, 4, 48, fill=bcol)
    add_text(sid, f"0{i+1}", "caption", bx + 16, 542, 40, 14,
             font_family="IBM Plex Mono", font_size=10, color=bcol, letter_spacing=2)
    add_text(sid, s, "subheading", bx + 16, 558, 140, 18,
             font_size=14, font_weight=700, color=NEURAL_WHITE)

# Footer
add_text(sid, "Every consequential decision passes through a human reviewer with audit trail and rollback authority.",
         "caption", 96, 624, 1088, 20,
         font_size=14, font_weight=500, color="#A8B0C2", text_align="center", line_height=1.4)
add_text(sid, "BILDORY · CONTROL ROOM FOR INTELLIGENCE",
         "caption", 96, 680, 1088, 16,
         font_family="IBM Plex Mono", font_size=10, color="#5C6478",
         letter_spacing=4, text_align="center")


# ============== SLIDE 13 — Guardrails Before Scale ==============
sid = "slide-13"
slide_bgs[sid] = "#070A18"  # midnight navy base

# Subtle grid lines
for gx in range(96, 1185, 96):
    add_shape(sid, "line", gx, 0, 1, 720, fill=GRAPHITE, opacity=0.18)

# Section
add_shape(sid, "rectangle", 96, 56, 80, 4, fill=ALIGN_VIOLET)
add_text(sid, "13 / DEPLOYMENT OVERSIGHT", "caption",
         184, 48, 400, 24, font_family="IBM Plex Mono",
         color=ALIGN_VIOLET, font_size=14, letter_spacing=4, text_transform="uppercase")

# Headline + pull quote
add_text(sid, "GUARDRAILS BEFORE SCALE.", "title",
         96, 96, 1088, 60, font_size=48, font_weight=800,
         color=NEURAL_WHITE, letter_spacing=-1)
add_text(sid, "Every powerful model deploys behind a hardened stack.",
         "paragraph", 96, 156, 720, 28,
         font_size=20, font_weight=500, color="#A8B0C2", line_height=1.4)

# Pull quote (right side)
add_shape(sid, "rectangle", 880, 96, 304, 88, fill=ALIGN_VIOLET, opacity=0.12)
add_shape(sid, "rectangle", 880, 96, 4, 88, fill=ALIGN_VIOLET)
add_text(sid, "SAFETY", "caption", 896, 108, 280, 16,
         font_family="IBM Plex Mono", font_size=11, color=ALIGN_VIOLET, letter_spacing=4)
add_text(sid, "IS INFRASTRUCTURE.", "heading",
         896, 128, 280, 36, font_size=22, font_weight=800, color=NEURAL_WHITE,
         letter_spacing=-0.5)
add_text(sid, "— Engineering principle", "caption",
         896, 162, 280, 14, font_size=11, font_weight=500, color="#A8B0C2",
         font_family="IBM Plex Mono")

# Layered glass slabs (deployment stack)
layers = [
    ("06", "ROLLBACK SYSTEM", "Instant revert to last safe checkpoint", SAFETY_RED, "RotateCcw"),
    ("05", "HUMAN REVIEW", "L1–L4 escalation; council approval at frontier", OVERSIGHT_BLUE, "Users"),
    ("04", "MONITORING", "Drift, anomalies, refusal rate, jailbreak telemetry", ROBUST_CYAN, "Activity"),
    ("03", "SAFETY FILTERS", "Output classifiers, refusal policies, redaction", LATENT_GREEN, "Filter"),
    ("02", "POLICY LAYER", "Rate limits, allowed tools, scoped permissions", INTERP_GOLD, "ShieldCheck"),
    ("01", "BASE MODEL", "Trained, red-teamed, capability-evaluated", ALIGN_VIOLET, "Cpu"),
]

slab_x = 240
slab_w = 800
slab_h = 56
gap = 6
top_y = 220

for i, (num, title, body, col, icon) in enumerate(layers):
    y = top_y + i * (slab_h + gap)
    # slab background
    add_shape(sid, "rectangle", slab_x, y, slab_w, slab_h, fill=DEEP_PANEL, opacity=0.96)
    # left accent
    add_shape(sid, "rectangle", slab_x, y, 6, slab_h, fill=col)
    # icon
    add_icon(sid, icon, slab_x + 24, y + 16, size=24, color=col)
    # number
    add_text(sid, num, "caption", slab_x + 64, y + 12, 40, 14,
             font_family="IBM Plex Mono", font_size=11, color=col, letter_spacing=3)
    # title
    add_text(sid, title, "subheading", slab_x + 64, y + 28, 240, 22,
             font_size=16, font_weight=700, color=NEURAL_WHITE, letter_spacing=2)
    # body
    add_text(sid, body, "caption", slab_x + 320, y + 18, 460, 22,
             font_size=13, font_weight=500, color="#A8B0C2")
    # status pill
    add_shape(sid, "circle", slab_x + slab_w - 32, y + 22, 12, 12, fill=col, opacity=0.9)

# Left side: data flow arrow
add_text(sid, "DATA FLOW", "caption", 120, 240, 96, 14,
         font_family="IBM Plex Mono", font_size=10, color="#7E879B", letter_spacing=3)
add_shape(sid, "line", 168, 260, 2, 360, fill=ROBUST_CYAN, opacity=0.5)
add_icon(sid, "ArrowDown", 152, 600, size=32, color=ROBUST_CYAN)

# Right side: blocked output indicator
add_text(sid, "UNSAFE → BLOCKED", "caption", 1064, 300, 160, 14,
         font_family="IBM Plex Mono", font_size=10, color=SAFETY_RED, letter_spacing=2)
add_text(sid, "SAFE → DELIVERED", "caption", 1064, 472, 160, 14,
         font_family="IBM Plex Mono", font_size=10, color=LATENT_GREEN, letter_spacing=2)

# Footer
add_text(sid, "DEFENSE IN DEPTH · LAYERED MITIGATIONS · CONTINUOUS EVALUATION",
         "caption", 96, 680, 1088, 16,
         font_family="IBM Plex Mono", font_size=11, color="#5C6478",
         letter_spacing=4, text_align="center")


# ============== SLIDE 14 — From Incident to Learning Loop ==============
sid = "slide-14"
slide_bgs[sid] = SIGNAL_BLACK

# Section
add_shape(sid, "rectangle", 96, 56, 80, 4, fill=SAFETY_RED)
add_text(sid, "14 / DEPLOYMENT OVERSIGHT", "caption",
         184, 48, 400, 24, font_family="IBM Plex Mono",
         color=SAFETY_RED, font_size=14, letter_spacing=4, text_transform="uppercase")

# Headline
add_text(sid, "FROM INCIDENT", "title",
         96, 96, 1088, 60, font_size=52, font_weight=800,
         color=NEURAL_WHITE, letter_spacing=-1)
add_text(sid, "TO LEARNING LOOP.", "title",
         96, 152, 1088, 60, font_size=52, font_weight=800,
         color=ROBUST_CYAN, letter_spacing=-1)

add_text(sid, "Every failure is a feedback signal. Forensic, fast, and folded back into training.",
         "paragraph", 96, 216, 920, 28,
         font_size=20, font_weight=500, color="#A8B0C2", line_height=1.4)

# Timeline strip
add_text(sid, "INCIDENT RESPONSE TIMELINE", "caption", 96, 272, 400, 16,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B", letter_spacing=3)

steps = [
    ("01", "DETECT", "Anomaly flagged", SAFETY_RED),
    ("02", "TRIAGE", "Severity classified", INTERP_GOLD),
    ("03", "CONTAIN", "Traffic gated", INTERP_GOLD),
    ("04", "INVESTIGATE", "Root cause traced", ROBUST_CYAN),
    ("05", "PATCH", "Model updated", OVERSIGHT_BLUE),
    ("06", "PUBLISH", "Learnings shared", LATENT_GREEN),
]

step_x = 96
step_w = 176
step_gap = 8
step_top = 304

for i, (num, label, body, col) in enumerate(steps):
    bx = step_x + i * (step_w + step_gap)
    add_shape(sid, "rectangle", bx, step_top, step_w, 96, fill=DEEP_PANEL)
    add_shape(sid, "rectangle", bx, step_top, step_w, 4, fill=col)
    add_text(sid, num, "caption", bx + 16, step_top + 16, 40, 14,
             font_family="IBM Plex Mono", font_size=11, color=col, letter_spacing=3)
    add_text(sid, label, "subheading", bx + 16, step_top + 36, 144, 22,
             font_size=15, font_weight=800, color=NEURAL_WHITE, letter_spacing=1)
    add_text(sid, body, "caption", bx + 16, step_top + 64, 144, 18,
             font_size=11, font_weight=500, color="#A8B0C2")

# Connecting tracer line under steps
add_shape(sid, "line", 112, 408, 1056, 2, fill=ROBUST_CYAN, opacity=0.4)

# Bottom feedback loop band
add_shape(sid, "rectangle", 96, 432, 1088, 200, fill=DEEP_PANEL, opacity=0.95)
add_shape(sid, "rectangle", 96, 432, 4, 200, fill=LATENT_GREEN)

# Left half: anomaly waveform / incident card
add_text(sid, "INCIDENT — 2026-04-14", "caption", 120, 452, 300, 16,
         font_family="IBM Plex Mono", font_size=11, color=SAFETY_RED, letter_spacing=3)
add_text(sid, "Tool-use loop in agent v3.2", "subheading",
         120, 472, 480, 24, font_size=18, font_weight=700, color=NEURAL_WHITE)

# Mini waveform (red bars)
bar_x = 120
bar_y_base = 580
heights = [24, 36, 18, 56, 72, 48, 28, 64, 40, 20, 32, 50, 22, 14]
for i, h in enumerate(heights):
    add_shape(sid, "rectangle", bar_x + i * 24, bar_y_base - h, 14, h,
              fill=SAFETY_RED, opacity=0.85)
add_text(sid, "ERROR SIGNAL", "caption", 120, 596, 200, 14,
         font_family="IBM Plex Mono", font_size=10, color=SAFETY_RED, letter_spacing=2)

# Right half: resolution / learning loop
add_text(sid, "RESOLUTION", "caption", 680, 452, 200, 16,
         font_family="IBM Plex Mono", font_size=11, color=LATENT_GREEN, letter_spacing=3)
add_text(sid, "Folded back into training & evals", "subheading",
         680, 472, 480, 24, font_size=18, font_weight=700, color=NEURAL_WHITE)

# Forensic incident metrics table
cells = {
    "0-0": {"text": "METRIC", "bold": True, "bg": "#0B0E1A", "color": "#7E879B"},
    "0-1": {"text": "BEFORE", "bold": True, "bg": "#0B0E1A", "color": "#7E879B"},
    "0-2": {"text": "AFTER", "bold": True, "bg": "#0B0E1A", "color": "#7E879B"},
    "0-3": {"text": "DELTA", "bold": True, "bg": "#0B0E1A", "color": "#7E879B"},
    "1-0": {"text": "Loop incidents / day", "bold": False, "bg": "#0B0E1A", "color": NEURAL_WHITE},
    "1-1": {"text": "47", "bold": True, "bg": "#0B0E1A", "color": SAFETY_RED},
    "1-2": {"text": "1", "bold": True, "bg": "#0B0E1A", "color": LATENT_GREEN},
    "1-3": {"text": "−97.8%", "bold": True, "bg": "#0B0E1A", "color": LATENT_GREEN},
    "2-0": {"text": "Time to detect", "bold": False, "bg": "#0B0E1A", "color": NEURAL_WHITE},
    "2-1": {"text": "42 min", "bold": True, "bg": "#0B0E1A", "color": SAFETY_RED},
    "2-2": {"text": "38 sec", "bold": True, "bg": "#0B0E1A", "color": LATENT_GREEN},
    "2-3": {"text": "−98.5%", "bold": True, "bg": "#0B0E1A", "color": LATENT_GREEN},
}
add_table(sid, 680, 504, [200, 90, 90, 100], [32, 32, 32], cells,
          font_size=12, table_color=NEURAL_WHITE, table_bg="#0B0E1A")

# Loop arrow icon
add_icon(sid, "RefreshCcw", 1112, 460, size=32, color=LATENT_GREEN)

# Footer
add_text(sid, "AUDIT · POSTMORTEM · CONTINUOUS LEARNING",
         "caption", 96, 680, 1088, 16,
         font_family="IBM Plex Mono", font_size=11, color="#5C6478",
         letter_spacing=4, text_align="center")


# ============== SLIDE 15 — Safe Intelligence, Shared Future ==============
sid = "slide-15"
slide_bgs[sid] = SIGNAL_BLACK

# Hero dawn-over-city background
add_image(sid,
          "https://images.pexels.com/photos/2086125/pexels-photo-2086125.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
          0, 0, 1280, 720, is_background=True, opacity=0.55)

# Top dark gradient overlay for type legibility
add_shape(sid, "rectangle", 0, 0, 1280, 200, fill=SIGNAL_BLACK, opacity=0.65)
# Bottom dark band for pillars
add_shape(sid, "rectangle", 0, 480, 1280, 240, fill=SIGNAL_BLACK, opacity=0.85)

# Section chip
add_shape(sid, "rectangle", 96, 56, 80, 4, fill=INTERP_GOLD)
add_text(sid, "15 / FINALE", "caption",
         184, 48, 400, 24, font_family="IBM Plex Mono",
         color=INTERP_GOLD, font_size=14, letter_spacing=4, text_transform="uppercase")

# Subtle orbital rings (governance halo)
add_shape(sid, "circle", 440, 200, 400, 240, fill=DEEP_PANEL,
          stroke=INTERP_GOLD, stroke_width=1, opacity=0.18)
add_shape(sid, "circle", 480, 220, 320, 200, fill=DEEP_PANEL,
          stroke=ROBUST_CYAN, stroke_width=1, opacity=0.22)
add_shape(sid, "circle", 520, 240, 240, 160, fill=DEEP_PANEL,
          stroke=ALIGN_VIOLET, stroke_width=1, opacity=0.28)

# Constellation nodes
nodes = [
    (480, 220, INTERP_GOLD),
    (640, 180, NEURAL_WHITE),
    (800, 240, ROBUST_CYAN),
    (560, 320, LATENT_GREEN),
    (740, 360, ALIGN_VIOLET),
    (860, 200, INTERP_GOLD),
    (520, 260, OVERSIGHT_BLUE),
]
for nx, ny, c in nodes:
    add_shape(sid, "circle", nx, ny, 8, 8, fill=c, opacity=0.95)

# Constellation connecting lines (subtle)
add_shape(sid, "line", 484, 224, 320, 1, fill=NEURAL_WHITE, opacity=0.25, rotation=-15)
add_shape(sid, "line", 524, 264, 240, 1, fill=NEURAL_WHITE, opacity=0.18, rotation=20)

# Hero headline (centered)
add_text(sid, "SAFE INTELLIGENCE,", "title",
         96, 240, 1088, 80, font_size=72, font_weight=800,
         color=NEURAL_WHITE, letter_spacing=-2, text_align="center")
add_text(sid, "SHARED FUTURE.", "title",
         96, 320, 1088, 80, font_size=72, font_weight=800,
         color=INTERP_GOLD, letter_spacing=-2, text_align="center")

# Subtitle / closing line
add_text(sid, "Build systems worthy of trust.",
         "subtitle", 96, 416, 1088, 36,
         font_size=24, font_weight=500, color="#D8DEEC",
         letter_spacing=4, text_align="center", text_transform="uppercase",
         font_family="IBM Plex Mono")

# Four pillars
pillars = [
    ("ALIGNMENT", "Match human values", ALIGN_VIOLET, "Compass"),
    ("ROBUSTNESS", "Hold under stress", ROBUST_CYAN, "Shield"),
    ("INTERPRETABILITY", "See inside the model", INTERP_GOLD, "Eye"),
    ("OVERSIGHT", "Humans in command", OVERSIGHT_BLUE, "Users"),
]

p_x = 112
p_w = 248
p_gap = 16
p_top = 504

for i, (label, body, col, icon) in enumerate(pillars):
    bx = p_x + i * (p_w + p_gap)
    add_shape(sid, "rectangle", bx, p_top, p_w, 144, fill=DEEP_PANEL, opacity=0.88)
    add_shape(sid, "rectangle", bx, p_top, p_w, 4, fill=col)
    add_icon(sid, icon, bx + 24, p_top + 24, size=32, color=col)
    add_text(sid, f"0{i+1}", "caption", bx + p_w - 56, p_top + 28, 40, 16,
             font_family="IBM Plex Mono", font_size=12, color=col,
             letter_spacing=3, text_align="right")
    add_text(sid, label, "subheading", bx + 24, p_top + 72, p_w - 48, 24,
             font_size=18, font_weight=800, color=NEURAL_WHITE, letter_spacing=2)
    add_text(sid, body, "caption", bx + 24, p_top + 100, p_w - 48, 20,
             font_size=13, font_weight=500, color="#A8B0C2")

# Footer
add_text(sid, "CONTROL ROOM FOR INTELLIGENCE · 2026",
         "caption", 96, 684, 1088, 16,
         font_family="IBM Plex Mono", font_size=11, color="#7E879B",
         letter_spacing=6, text_align="center")


# ============== ASSEMBLE ==============
slide_ids = [f"slide-{i}" for i in range(11, 16)]

content_slides = []
baselayout_slides = []
for idx, sid in enumerate(slide_ids):
    content_slides.append({
        "id": sid,
        "order": idx,
        "layoutId": "blank-canvas",
        "backgroundColor": slide_bgs[sid],
        "textElements": text_by_slide[sid],
    })
    baselayout_slides.append({
        "id": sid,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": [],
    })

content_file = {
    "slides": content_slides,
    "imageElements": image_elements,
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": table_elements,
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": [],
}

baselayout_file = {
    "version": "v1",
    "slides": baselayout_slides,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": [],
}

changelog_file = {
    "version": "2.0",
    "slides": changelog_slides,
}

# Element count
elem_count = (
    sum(len(s["textElements"]) for s in content_slides)
    + len(image_elements)
    + len(shape_elements)
    + len(chart_elements)
    + len(table_elements)
    + len(icon_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch3-{NOW}",
        "title": "Control Room for Intelligence — Slides 11-15",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": elem_count,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None,
    },
    "files": {
        "content": content_file,
        "baseLayout": baselayout_file,
        "changelog": changelog_file,
    },
}

with open("deck.json", "w") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote deck.json — {len(content_slides)} slides, {elem_count} elements")
