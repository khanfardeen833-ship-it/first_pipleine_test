import json
import math
import time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-1"

COUNTER = 0
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------- helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None,
              line_height=None, text_align="left",
              font_family="Space Grotesk", letter_spacing=0):
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
            "textAlign": text_align, "lineHeight": lh,
            "letterSpacing": letter_spacing,
            "fontWeight": fw, "fontStyle": "normal",
            "textDecoration": "none", "textTransform": "none",
            "isCode": False, "listStyle": "none", "link": "",
            "backgroundColor": "transparent", "background": "none",
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
                      "delay": 0, "trigger": "both",
                      "typewriterMode": "character"},
        "enterAnimation": "none", "exitAnimation": "fade",
        "animationEffect": "none", "animationDurationMs": 550,
        "animationDelayMs": 0, "animationTrigger": "both",
        "animationTypewriterMode": "character", "updatedAt": now
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx, now,
               fill="#22D3EE", stroke=None, stroke_width=0,
               opacity=1, rotation=0):
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


# ---------- storage ----------
text_elements_by_slide = {SLIDE_ID: []}
shape_elements = []
icon_elements = []
changelog_slides = {SLIDE_ID: {"elements": {}}}


def add_text(text, type_, x, y, w, h, color="#F8FAFC",
             font_size=None, font_weight=None, line_height=None,
             text_align="left", font_family="Space Grotesk",
             letter_spacing=0):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, n, NOW,
                      color=color, font_size=font_size,
                      font_weight=font_weight, line_height=line_height,
                      text_align=text_align, font_family=font_family,
                      letter_spacing=letter_spacing)
    text_elements_by_slide[SLIDE_ID].append(c)
    changelog_slides[SLIDE_ID]["elements"][tid] = cl


def add_shape(shape_type, x, y, w, h, fill="#22D3EE", stroke=None,
              stroke_width=0, opacity=1, rotation=0):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n, NOW,
                       fill=fill, stroke=stroke,
                       stroke_width=stroke_width,
                       opacity=opacity, rotation=rotation)
    shape_elements.append(c)
    changelog_slides[SLIDE_ID]["elements"][sid] = cl


def add_icon(icon_name, x, y, size=80, color="#22D3EE", opacity=1):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, icon_name, x, y, n, NOW,
                      size=size, color=color, opacity=opacity)
    icon_elements.append(c)
    changelog_slides[SLIDE_ID]["elements"][iid] = cl


# =================================================================
# SLIDE 1 — THE ENGINEERING SYSTEM
# =================================================================

# 1. Full-bleed obsidian background
add_shape("rectangle", 0, 0, 1280, 720, fill="#0B1020", opacity=1)

# 2-4. Subtle vertical blueprint grid lines
for x_pos in [320, 640, 960]:
    add_shape("rectangle", x_pos, 0, 1, 720,
              fill="#1E3A5F", opacity=0.25)

# 5. Subtle horizontal grid line under top metadata
add_shape("rectangle", 0, 96, 1280, 1, fill="#1E3A5F", opacity=0.2)

# Diagram geometry
CX, CY = 640, 270
RADIUS = 150

# 6. Outer orbital ring (faint blueprint outline)
add_shape("circle", CX - RADIUS, CY - RADIUS, RADIUS * 2, RADIUS * 2,
          fill="#0B1020", stroke="#1E3A5F", stroke_width=1, opacity=0.85)

# Six orbital nodes — (label, lucide icon, accent color, angle)
nodes = [
    ("VERSION CONTROL", "GitBranch",     "#22D3EE",  -90),
    ("TESTING",         "ShieldCheck",   "#22C55E",  -30),
    ("CODE REVIEW",     "MessageSquare", "#A78BFA",   30),
    ("CI / CD",         "Workflow",      "#22D3EE",   90),
    ("DEPLOYMENT",      "Rocket",        "#F59E0B",  150),
    ("OBSERVABILITY",   "Activity",      "#A78BFA", -150),
]

# Compute node centers
node_data = []
for label, icon_name, color, angle in nodes:
    rad = math.radians(angle)
    nx = CX + RADIUS * math.cos(rad)
    ny = CY + RADIUS * math.sin(rad)
    node_data.append((label, icon_name, color, nx, ny))

# 7-12. Connector lines (thin rotated rectangles, center -> node)
for label, icon_name, color, nx, ny in node_data:
    dx, dy = nx - CX, ny - CY
    length = math.hypot(dx, dy)
    angle_deg = math.degrees(math.atan2(dy, dx))
    mid_x = (CX + nx) / 2
    mid_y = (CY + ny) / 2
    thickness = 2
    pos_x = round(mid_x - length / 2, 2)
    pos_y = round(mid_y - thickness / 2, 2)
    add_shape("rectangle", pos_x, pos_y,
              round(length, 2), thickness,
              fill="#22D3EE", opacity=0.4,
              rotation=round(angle_deg, 2))

# 13-18. Node circles (graphite background with colored stroke)
NODE_SIZE = 80
for label, icon_name, color, nx, ny in node_data:
    px = round(nx - NODE_SIZE / 2)
    py = round(ny - NODE_SIZE / 2)
    add_shape("circle", px, py, NODE_SIZE, NODE_SIZE,
              fill="#171C2E", stroke=color,
              stroke_width=2, opacity=1)

# 19-24. Node icons (centered inside each node)
ICON_SIZE = 36
for label, icon_name, color, nx, ny in node_data:
    ix = round(nx - ICON_SIZE / 2)
    iy = round(ny - ICON_SIZE / 2)
    add_icon(icon_name, ix, iy, size=ICON_SIZE,
             color=color, opacity=1)

# 25-30. Mono labels below each node
for label, icon_name, color, nx, ny in node_data:
    px = round(nx - 100)
    py = round(ny + 50)
    add_text(label, "caption", px, py, 200, 20,
             color="#F8FAFC", font_size=11, font_weight=600,
             text_align="center",
             font_family="JetBrains Mono",
             letter_spacing=2)

# 31. Core outer circle
CORE_R = 70
add_shape("circle", CX - CORE_R, CY - CORE_R,
          CORE_R * 2, CORE_R * 2,
          fill="#171C2E", stroke="#22D3EE",
          stroke_width=2, opacity=1)

# 32. Core inner highlight
INNER_R = 40
add_shape("circle", CX - INNER_R, CY - INNER_R,
          INNER_R * 2, INNER_R * 2,
          fill="#1E3A5F", stroke="#1E3A5F",
          stroke_width=0, opacity=0.55)

# 33. Core text line 1
add_text("ENGINEERING", "caption",
         CX - 90, CY - 16, 180, 16,
         color="#F8FAFC", font_size=12, font_weight=700,
         text_align="center",
         font_family="JetBrains Mono",
         letter_spacing=2)

# 34. Core text line 2
add_text("EXCELLENCE", "caption",
         CX - 90, CY + 4, 180, 16,
         color="#22D3EE", font_size=12, font_weight=700,
         text_align="center",
         font_family="JetBrains Mono",
         letter_spacing=2)

# 35. Top section label
add_text("ENGINEERING EXCELLENCE  ·  CHAPTER ONE", "caption",
         48, 56, 700, 20,
         color="#22D3EE", font_size=12, font_weight=600,
         text_align="left",
         font_family="JetBrains Mono",
         letter_spacing=3)

# 36. Top-right metadata
add_text("01 / 15", "caption",
         1100, 56, 132, 20,
         color="#94A3B8", font_size=12, font_weight=600,
         text_align="right",
         font_family="JetBrains Mono",
         letter_spacing=2)

# 37. Cyan accent bar above hero title
add_shape("rectangle", 48, 540, 64, 2,
          fill="#22D3EE", opacity=1)

# 38. Hero title
add_text("The Engineering System", "title",
         48, 552, 1100, 80,
         color="#F8FAFC", font_size=68, font_weight=700,
         line_height=1.05, text_align="left",
         font_family="Space Grotesk")

# 39. Editorial caption
add_text("FROM CODE TO PRODUCTION, QUALITY IS A SYSTEM — NOT A PHASE.",
         "caption", 48, 640, 1184, 24,
         color="#94A3B8", font_size=13, font_weight=500,
         text_align="left",
         font_family="IBM Plex Mono",
         letter_spacing=3)


# =================================================================
# Assemble JSON
# =================================================================

slide_obj = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": "#0B1020",
    "textElements": text_elements_by_slide[SLIDE_ID]
}

content = {
    "slides": [slide_obj],
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
    "slides": changelog_slides
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
        "title": "Engineering Excellence: From Commit to Production",
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

OUT = "deck.json"
with open(OUT, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {OUT}")
print(f"slideCount = 1")
print(f"elementCount = {element_count}")
print(f"  texts  = {len(text_elements_by_slide[SLIDE_ID])}")
print(f"  shapes = {len(shape_elements)}")
print(f"  icons  = {len(icon_elements)}")
