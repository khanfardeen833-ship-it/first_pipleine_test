import json
import time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-9"

# Colors
BG_OBSIDIAN = "#0B1020"
GRAPHITE    = "#171C2E"
BLUEPRINT   = "#1E3A5F"
CYAN        = "#22D3EE"
GREEN       = "#22C55E"
AMBER       = "#F59E0B"
LAVENDER    = "#A78BFA"
WHITE       = "#F8FAFC"
STEEL       = "#94A3B8"

# Pyramid tier fills (subtle hierarchy — lightest on top)
TIER_UNIT_FILL  = "#0E1A33"
TIER_INT_FILL   = "#13234A"
TIER_E2E_FILL   = "#1A2E5C"

COUNTER = 1200

def next_n():
    global COUNTER
    COUNTER += 1
    return COUNTER


def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color=WHITE, font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk",
              font_style="normal"):
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
               fill="#000000", stroke=None, stroke_width=0, opacity=1):
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


# Storage
text_elements_per_slide = []     # per-slide list (we have one slide here)
shape_elements_file = []
icon_elements_file = []
changelog_elements = {}          # for slide-9


def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_n()
    text_id = f"text-{n}"
    c, cl = make_text(text_id, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_elements_per_slide.append(c)
    changelog_elements[text_id] = cl
    return text_id


def add_shape(shape_type, x, y, w, h, **kwargs):
    n = next_n()
    shape_id = f"shape-{n}"
    c, cl = make_shape(shape_id, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements_file.append(c)
    changelog_elements[shape_id] = cl
    return shape_id


def add_icon(icon_name, x, y, **kwargs):
    n = next_n()
    icon_id = f"icon-{n}"
    c, cl = make_icon(icon_id, SLIDE_ID, icon_name, x, y, n, NOW, **kwargs)
    icon_elements_file.append(c)
    changelog_elements[icon_id] = cl
    return icon_id


# ============================================================================
# SLIDE 9 — Tests That Guard the Future
# ============================================================================

# 1201 — Background full slide
add_shape("rectangle", 0, 0, 1280, 720,
          fill=BG_OBSIDIAN, stroke=BG_OBSIDIAN, stroke_width=0)

# 1202 — Top accent cyan line (editorial mark)
add_shape("rectangle", 80, 80, 64, 2,
          fill=CYAN, stroke=CYAN, stroke_width=0)

# 1203 — Eyebrow caption
add_text("TESTING  —  CHAPTER 09 / 15", "caption",
         80, 92, 600, 20,
         color=CYAN, font_size=12, font_weight=600,
         letter_spacing=4, font_family="JetBrains Mono")

# 1204 — Title
add_text("Tests That Guard the Future", "title",
         80, 120, 1120, 84,
         color=WHITE, font_size=64, font_weight=700,
         line_height=1.05, letter_spacing=-1)

# 1205 — Subtitle paragraph
add_text(
    "Layered automation that protects velocity and the invariants of every release.",
    "paragraph",
    80, 220, 820, 56,
    color=STEEL, font_size=20, font_weight=400, line_height=1.45)

# 1206 — Pyramid section label (left)
add_text("// THE TESTING PYRAMID", "caption",
         80, 296, 400, 20,
         color=CYAN, font_size=12, font_weight=600,
         letter_spacing=2, font_family="JetBrains Mono")

# 1207 — Unit pyramid tier (BASE — drawn first, lowest z within pyramid)
add_shape("rectangle", 100, 472, 400, 88,
          fill=TIER_UNIT_FILL, stroke=CYAN, stroke_width=2, opacity=1)

# 1208 — Integration pyramid tier (MIDDLE)
add_shape("rectangle", 160, 388, 280, 68,
          fill=TIER_INT_FILL, stroke=CYAN, stroke_width=2, opacity=1)

# 1209 — E2E pyramid tier (TOP)
add_shape("rectangle", 200, 320, 200, 56,
          fill=TIER_E2E_FILL, stroke=CYAN, stroke_width=2, opacity=1)

# 1210 — E2E label heading
add_text("E2E TESTS", "subheading",
         200, 328, 200, 24,
         color=WHITE, font_size=18, font_weight=700,
         text_align="center", letter_spacing=2)

# 1211 — E2E sub-caption
add_text("SLOW · FEW · USER FLOWS", "caption",
         200, 354, 200, 18,
         color=CYAN, font_size=10, font_weight=500,
         text_align="center", letter_spacing=2,
         font_family="JetBrains Mono")

# 1212 — Integration label heading
add_text("INTEGRATION TESTS", "subheading",
         160, 398, 280, 28,
         color=WHITE, font_size=22, font_weight=700,
         text_align="center", letter_spacing=2)

# 1213 — Integration sub-caption
add_text("MEDIUM · SELECTIVE · BOUNDARIES", "caption",
         160, 428, 280, 18,
         color=CYAN, font_size=11, font_weight=500,
         text_align="center", letter_spacing=2,
         font_family="JetBrains Mono")

# 1214 — Unit label heading
add_text("UNIT TESTS", "subheading",
         100, 488, 400, 32,
         color=WHITE, font_size=26, font_weight=700,
         text_align="center", letter_spacing=2)

# 1215 — Unit sub-caption
add_text("FAST · MANY · PURE LOGIC", "caption",
         100, 524, 400, 20,
         color=CYAN, font_size=12, font_weight=500,
         text_align="center", letter_spacing=2,
         font_family="JetBrains Mono")

# 1216 — Unit % share
add_text("70%", "heading",
         512, 500, 80, 36,
         color=GREEN, font_size=28, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=-1)

# 1217 — Integration % share
add_text("20%", "heading",
         452, 404, 80, 32,
         color=AMBER, font_size=22, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=-1)

# 1218 — E2E % share
add_text("10%", "heading",
         412, 332, 80, 24,
         color=LAVENDER, font_size=18, font_weight=700,
         font_family="JetBrains Mono", letter_spacing=-1)

# 1219 — Defense layers section label (right)
add_text("// DEFENSE LAYERS", "caption",
         664, 296, 400, 20,
         color=CYAN, font_size=12, font_weight=600,
         letter_spacing=2, font_family="JetBrains Mono")

# 1220 — Divider 1 (between card 1 & 2)
add_shape("rectangle", 664, 412, 552, 1,
          fill=BLUEPRINT, stroke=BLUEPRINT, stroke_width=0, opacity=1)

# 1221 — Divider 2 (between card 2 & 3)
add_shape("rectangle", 664, 496, 552, 1,
          fill=BLUEPRINT, stroke=BLUEPRINT, stroke_width=0, opacity=1)

# 1222 — Icon: Zap (Fast Feedback)
add_icon("Zap", 664, 340, size=44, color=CYAN)

# 1223 — Card 1 heading
add_text("Fast Feedback", "subheading",
         720, 340, 480, 28,
         color=WHITE, font_size=22, font_weight=600)

# 1224 — Card 1 body
add_text(
    "Failures surface in seconds, not days — engineers fix while context is still warm.",
    "paragraph",
    720, 372, 480, 36,
    color=STEEL, font_size=14, font_weight=400, line_height=1.45)

# 1225 — Icon: ShieldCheck (Confidence)
add_icon("ShieldCheck", 664, 424, size=44, color=GREEN)

# 1226 — Card 2 heading
add_text("Confidence to Refactor", "subheading",
         720, 424, 480, 28,
         color=WHITE, font_size=22, font_weight=600)

# 1227 — Card 2 body
add_text(
    "Reshape architecture freely when every behavior is encoded in deterministic checks.",
    "paragraph",
    720, 456, 480, 36,
    color=STEEL, font_size=14, font_weight=400, line_height=1.45)

# 1228 — Icon: Target (Risk Reduction)
add_icon("Target", 664, 508, size=44, color=LAVENDER)

# 1229 — Card 3 heading
add_text("Risk Reduction", "subheading",
         720, 508, 480, 28,
         color=WHITE, font_size=22, font_weight=600)

# 1230 — Card 3 body
add_text(
    "Catch regressions before users do; guard the invariants that matter most in production.",
    "paragraph",
    720, 540, 480, 36,
    color=STEEL, font_size=14, font_weight=400, line_height=1.45)

# 1231 — Footer mono caption
add_text("// fast  ·  deterministic  ·  isolated  ·  meaningful", "caption",
         80, 648, 800, 20,
         color=STEEL, font_size=12, font_weight=500,
         letter_spacing=2, font_family="JetBrains Mono")

# 1232 — Slide indicator
add_text("09 / 15", "caption",
         1120, 648, 100, 20,
         color=STEEL, font_size=12, font_weight=600,
         text_align="right", letter_spacing=2,
         font_family="JetBrains Mono")


# ============================================================================
# Build envelope
# ============================================================================

slide_obj = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": BG_OBSIDIAN,
    "textElements": text_elements_per_slide,
}

baseLayout_slide = {
    "id": SLIDE_ID,
    "layoutId": "blank-canvas",
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": [],
}

content_file = {
    "slides": [slide_obj],
    "imageElements": [],
    "shapeElements": shape_elements_file,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements_file,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": [],
}

baseLayout_file = {
    "version": "v1",
    "slides": [baseLayout_slide],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": [],
}

changelog_file = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {
            "elements": changelog_elements
        }
    }
}

element_count = (
    len(text_elements_per_slide) +
    len(shape_elements_file) +
    len(icon_elements_file)
)
slide_count = 1

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch9-{NOW}",
        "title": "Engineering Excellence: From Commit to Production",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": slide_count,
        "elementCount": element_count,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None,
    },
    "files": {
        "content": content_file,
        "baseLayout": baseLayout_file,
        "changelog": changelog_file,
    }
}

OUT = "deck.json"
with open(OUT, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {OUT}")
print(f"slideCount = {slide_count}")
print(f"elementCount = {element_count}")
print(f"  text:  {len(text_elements_per_slide)}")
print(f"  shape: {len(shape_elements_file)}")
print(f"  icon:  {len(icon_elements_file)}")
print(f"  changelog entries: {len(changelog_elements)}")
