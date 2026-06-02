import json
import time

NOW = int(time.time() * 1000)

COUNTER = 2100
def next_n():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------- helpers ----------

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
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
            "fontSize": fs, "fontFamily": "Space Grotesk", "color": color,
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


# ---------- registries ----------

SLIDE_ID = "slide-15"
text_elements_in_slide = []
shape_elements_file = []
icon_elements_file = []
changelog_elements = {}

def reg_shape(c, cl):
    shape_elements_file.append(c)
    changelog_elements[c["id"]] = cl

def reg_text(c, cl):
    text_elements_in_slide.append(c)
    changelog_elements[c["id"]] = cl

def reg_icon(c, cl):
    icon_elements_file.append(c)
    changelog_elements[c["id"]] = cl


# ---------- 1. Top accent tick ----------
n = next_n()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   96, 36, 48, 2, n, NOW,
                   fill="#22D3EE", stroke="#22D3EE", stroke_width=0, opacity=0.9)
reg_shape(c, cl)

# ---------- 2. Caption left (chapter metadata) ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "ENGINEERING EXCELLENCE  ·  CHAPTER VI  ·  CLOSING",
                  "caption",
                  x=160, y=32, w=720, h=20, zidx=n, now=NOW,
                  color="#22D3EE", font_size=11, font_weight=600,
                  letter_spacing=2.5)
reg_text(c, cl)

# ---------- 3. Page indicator right ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID, "15 / 15", "caption",
                  x=1080, y=32, w=104, h=20, zidx=n, now=NOW,
                  color="#94A3B8", font_size=11, font_weight=600,
                  text_align="right", letter_spacing=2.5)
reg_text(c, cl)

# ---------- 4. Hero title ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "Engineering Excellence Is a System", "title",
                  x=96, y=64, w=1088, h=56, zidx=n, now=NOW,
                  color="#F8FAFC", font_size=42, font_weight=700,
                  line_height=1.1, text_align="center")
reg_text(c, cl)

# ---------- 5. Subtitle ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "Six pillars. One feedback loop.",
                  "subheading",
                  x=96, y=124, w=1088, h=24, zidx=n, now=NOW,
                  color="#94A3B8", font_size=16, font_weight=500,
                  line_height=1.4, text_align="center", letter_spacing=0.5)
reg_text(c, cl)

# ---------- 6. Outer cyan halo (subtle glow behind compass) ----------
n = next_n()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "circle",
                   380, 150, 520, 440, n, NOW,
                   fill="#22D3EE", stroke="#22D3EE", stroke_width=0, opacity=0.06)
reg_shape(c, cl)

# ---------- 7-24. Six pillars (each = circle + icon + label) ----------
PILLARS = [
    # (cx, cy, icon_name, label, accent_color)
    (640, 200, "GitBranch",     "VERSION CONTROL", "#22D3EE"),
    (813, 285, "CheckCircle",   "TESTING",         "#22C55E"),
    (813, 455, "MessageSquare", "CODE REVIEW",     "#F8FAFC"),
    (640, 540, "Zap",           "CI / CD",         "#F59E0B"),
    (467, 455, "Cloud",         "DEPLOYMENT",      "#A78BFA"),
    (467, 285, "Activity",      "OBSERVABILITY",   "#22D3EE"),
]

for cx, cy, icon_name, label, accent in PILLARS:
    # pillar circle (graphite filled, accent stroke)
    n = next_n()
    c, cl = make_shape(f"shape-{n}", SLIDE_ID, "circle",
                       cx - 40, cy - 40, 80, 80, n, NOW,
                       fill="#171C2E", stroke=accent, stroke_width=2)
    reg_shape(c, cl)

    # pillar icon
    n = next_n()
    c, cl = make_icon(f"icon-{n}", SLIDE_ID, icon_name,
                      cx - 20, cy - 20, n, NOW,
                      size=40, color=accent)
    reg_icon(c, cl)

    # pillar label below circle
    n = next_n()
    c, cl = make_text(f"text-{n}", SLIDE_ID, label, "caption",
                      x=cx - 90, y=cy + 46, w=180, h=20, zidx=n, now=NOW,
                      color="#F8FAFC", font_size=12, font_weight=600,
                      text_align="center", letter_spacing=2)
    reg_text(c, cl)

# ---------- 25. Core circle ----------
n = next_n()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "circle",
                   568, 298, 144, 144, n, NOW,
                   fill="#1E3A5F", stroke="#22D3EE", stroke_width=2)
reg_shape(c, cl)

# ---------- 26. Core small label (top) ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID, "RELIABLE SOFTWARE", "caption",
                  x=568, y=336, w=144, h=16, zidx=n, now=NOW,
                  color="#22D3EE", font_size=10, font_weight=600,
                  text_align="center", letter_spacing=2)
reg_text(c, cl)

# ---------- 27. Core mid line ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID, "CONTINUOUSLY", "caption",
                  x=568, y=356, w=144, h=20, zidx=n, now=NOW,
                  color="#F8FAFC", font_size=15, font_weight=700,
                  text_align="center", letter_spacing=1)
reg_text(c, cl)

# ---------- 28. Core bottom line ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID, "IMPROVED", "caption",
                  x=568, y=380, w=144, h=20, zidx=n, now=NOW,
                  color="#F8FAFC", font_size=15, font_weight=700,
                  text_align="center", letter_spacing=1)
reg_text(c, cl)

# ---------- 29. Closing editorial statement ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "Best practices are not ceremonies — they are feedback loops that protect speed, quality, and trust.",
                  "paragraph",
                  x=128, y=624, w=1024, h=56, zidx=n, now=NOW,
                  color="#F8FAFC", font_size=18, font_weight=500,
                  line_height=1.5, text_align="center")
reg_text(c, cl)

# ---------- 30. Footer caption ----------
n = next_n()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "RELIABLE SOFTWARE  ·  CONTINUOUSLY IMPROVED",
                  "caption",
                  x=96, y=688, w=1088, h=18, zidx=n, now=NOW,
                  color="#94A3B8", font_size=10, font_weight=600,
                  text_align="center", letter_spacing=4)
reg_text(c, cl)


# ---------- assemble the deck ----------

content = {
    "slides": [
        {
            "id": SLIDE_ID,
            "order": 0,
            "layoutId": "blank-canvas",
            "backgroundColor": "#0B1020",
            "textElements": text_elements_in_slide
        }
    ],
    "imageElements": [],
    "shapeElements": shape_elements_file,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements_file,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

baseLayout = {
    "version": "v1",
    "slides": [
        {
            "id": SLIDE_ID,
            "layoutId": "blank-canvas",
            "imageElements": [],
            "shapeElements": [],
            "chartElements": [],
            "iconElements": [],
            "embedElements": []
        }
    ],
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
    len(text_elements_in_slide)
    + len(shape_elements_file)
    + len(icon_elements_file)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-15-{NOW}",
        "title": "Engineering Excellence: From Commit to Production — Slide 15",
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
        "baseLayout": baseLayout,
        "changelog": changelog
    }
}

OUT = "deck.json"
with open(OUT, "w") as f:
    json.dump(deck, f, indent=2)

print(f"Wrote {OUT}")
print(f"slideCount   = {deck['presentation']['slideCount']}")
print(f"elementCount = {element_count}")
print(f"  texts  = {len(text_elements_in_slide)}")
print(f"  shapes = {len(shape_elements_file)}")
print(f"  icons  = {len(icon_elements_file)}")
print(f"changelog elements = {len(changelog_elements)}")
print(f"id range: 2101..{COUNTER}")
