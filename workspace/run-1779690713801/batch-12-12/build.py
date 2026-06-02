import json
import time

NOW = int(time.time() * 1000)
COUNTER = 1650
SLIDE_ID = "slide-12"

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F8FAFC", font_size=None, font_weight=None, line_height=None,
              text_align="left", font_family="Space Grotesk", letter_spacing=0):
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
               fill="#22D3EE", stroke=None, stroke_width=0, opacity=1):
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
              size=80, color="#22D3EE", opacity=1):
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


# Containers
text_elements = []
shape_elements_content = []
icon_elements_content = []
changelog_elements = {}


def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, zidx=n, now=NOW, **kwargs)
    text_elements.append(c)
    changelog_elements[tid] = cl


def add_shape(shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, zidx=n, now=NOW, **kwargs)
    shape_elements_content.append(c)
    changelog_elements[sid] = cl


def add_icon(icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, icon_name, x, y, zidx=n, now=NOW, **kwargs)
    icon_elements_content.append(c)
    changelog_elements[iid] = cl


# ============ BUILD SLIDE 12 — "The Release Gate" ============

# 1. Dark cinematic background — Obsidian Console
add_shape("rectangle", 0, 0, 1280, 720, fill="#0B1020")

# 2. Eyebrow — chapter label in mono cyan
add_text("RELEASE  /  CHAPTER 12", "caption", 64, 56, 400, 20,
         color="#22D3EE", font_size=12, font_weight=600, letter_spacing=3,
         font_family="JetBrains Mono")

# 3. Hero title
add_text("The Release Gate", "title", 64, 88, 900, 96,
         color="#F8FAFC", font_size=72, font_weight=700, line_height=1.05,
         font_family="Space Grotesk")

# 4. Editorial lede beneath title
add_text("A staged path from merged code to production — controlled, measured, reversible.",
         "paragraph", 64, 196, 880, 64,
         color="#94A3B8", font_size=22, font_weight=400, line_height=1.5,
         font_family="Inter")

# 5. Pipeline runway (dim Blueprint Navy line behind circles)
add_shape("rectangle", 148, 347, 984, 2, fill="#1E3A5F")

# 6-25. Four pipeline stages
stages = [
    {"x": 100, "name": "DEV", "desc": "Code merged to main",
     "version": "feat/auth-v2", "icon": "GitMerge",
     "stroke": "#22D3EE", "accent": "#22D3EE"},
    {"x": 428, "name": "STAGING", "desc": "Integration suite",
     "version": "build #4821", "icon": "FlaskConical",
     "stroke": "#22D3EE", "accent": "#22D3EE"},
    {"x": 756, "name": "CANARY", "desc": "5% live traffic",
     "version": "v2.4.1-rc", "icon": "Activity",
     "stroke": "#F59E0B", "accent": "#F59E0B"},
    {"x": 1084, "name": "PRODUCTION", "desc": "Full rollout",
     "version": "v2.4.1", "icon": "CheckCircle",
     "stroke": "#22C55E", "accent": "#22C55E"},
]

for s in stages:
    cx = s["x"] + 48  # circle center x
    # Glowing stage node — graphite fill, colored stroke ring
    add_shape("circle", s["x"], 300, 96, 96,
              fill="#171C2E", stroke=s["stroke"], stroke_width=3)
    # Lucide icon centered inside circle
    add_icon(s["icon"], cx - 20, 328, size=40, color=s["accent"])
    # Stage name — mono uppercase
    add_text(s["name"], "caption", cx - 110, 416, 220, 22,
             color="#F8FAFC", font_size=15, font_weight=700, letter_spacing=2,
             font_family="JetBrains Mono", text_align="center")
    # Stage description — muted steel
    add_text(s["desc"], "paragraph", cx - 110, 442, 220, 22,
             color="#94A3B8", font_size=14, font_weight=400, line_height=1.4,
             font_family="Inter", text_align="center")
    # Version / artifact label — mono accent
    add_text(s["version"], "caption", cx - 110, 470, 220, 18,
             color=s["accent"], font_size=12, font_weight=500,
             font_family="JetBrains Mono", text_align="center")

# 26-41. Four release-discipline principle cards
cards = [
    {"x": 64,  "num": "01", "title": "Automated Gates",
     "desc": "Tests, scans, and approvals must pass."},
    {"x": 368, "num": "02", "title": "Reversible by Design",
     "desc": "One-click rollback to last good version."},
    {"x": 672, "num": "03", "title": "Versioned Artifacts",
     "desc": "Immutable, signed, traceable builds."},
    {"x": 976, "num": "04", "title": "Progressive Rollout",
     "desc": "Canary first; expand on green signals."},
]

for c in cards:
    # Graphite card panel
    add_shape("rectangle", c["x"], 540, 240, 108, fill="#171C2E")
    # Mono number — cyan accent
    add_text(c["num"], "caption", c["x"] + 20, 556, 60, 18,
             color="#22D3EE", font_size=12, font_weight=700, letter_spacing=2,
             font_family="JetBrains Mono")
    # Card title — paper white
    add_text(c["title"], "heading", c["x"] + 20, 580, 200, 22,
             color="#F8FAFC", font_size=16, font_weight=600,
             font_family="Inter")
    # Card desc — muted steel
    add_text(c["desc"], "paragraph", c["x"] + 20, 608, 200, 32,
             color="#94A3B8", font_size=12, font_weight=400, line_height=1.5,
             font_family="Inter")

# 42. Editorial footer
add_text("ENGINEERING EXCELLENCE  ·  FROM COMMIT TO PRODUCTION  ·  12 / 15",
         "caption", 64, 684, 1152, 16,
         color="#475569", font_size=11, font_weight=500, letter_spacing=3,
         font_family="JetBrains Mono")


# ============ ASSEMBLE ENVELOPE ============

slide_data = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": "#0B1020",
    "textElements": text_elements
}

content_file = {
    "slides": [slide_data],
    "imageElements": [],
    "shapeElements": shape_elements_content,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements_content,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baselayout_slide = {
    "id": SLIDE_ID,
    "layoutId": "blank-canvas",
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

baselayout_file = {
    "version": "v1",
    "slides": [baselayout_slide],
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

changelog_file = {
    "version": "2.0",
    "slides": {
        SLIDE_ID: {
            "elements": changelog_elements
        }
    }
}

element_count = (len(text_elements) + len(shape_elements_content) +
                 len(icon_elements_content))

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-12-{NOW}",
        "title": "Engineering Excellence: From Commit to Production — Slide 12",
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
        "content": content_file,
        "baseLayout": baselayout_file,
        "changelog": changelog_file
    }
}

OUT = "slide_12.json"
with open(OUT, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {OUT}")
print(f"Slide count: 1")
print(f"Element count: {element_count}")
print(f"  Texts:  {len(text_elements)}")
print(f"  Shapes: {len(shape_elements_content)}")
print(f"  Icons:  {len(icon_elements_content)}")
print(f"Final counter: {COUNTER} (started at 1650)")
print(f"Changelog entries: {len(changelog_elements)}")
