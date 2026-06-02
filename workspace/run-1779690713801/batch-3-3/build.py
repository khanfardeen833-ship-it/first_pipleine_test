import json
import time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-3"
COUNTER = 300


def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


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
    if font_size is not None:
        fs = font_size
    if font_weight is not None:
        fw = font_weight
    if line_height is not None:
        lh = line_height

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


# Collectors
content_text_elements = []
content_shape_elements = []
content_icon_elements = []
changelog_elements = {}


def add_text(text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, text, type_, x, y, w, h, n, NOW, **kwargs)
    content_text_elements.append(c)
    changelog_elements[tid] = cl
    return tid


def add_shape(shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    content_shape_elements.append(c)
    changelog_elements[sid] = cl
    return sid


def add_icon(icon_name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, icon_name, x, y, n, NOW, **kwargs)
    content_icon_elements.append(c)
    changelog_elements[iid] = cl
    return iid


# ========================================================
# SLIDE 3 — Testing: Confidence Before Velocity
# Background: #0B1020 (Obsidian Console)
# ========================================================

# --- Decorative shapes (low z, behind content) ---

# Cyan accent stripe under chapter caption
add_shape("rectangle", 64, 84, 40, 2, fill="#22D3EE")

# Vertical divider between pyramid section and principle sidebar
add_shape("rectangle", 696, 216, 1, 444, fill="#1E3A5F")

# Pyramid layers (stacked, narrowing toward the top)
# Bottom — Unit Tests (broad foundation, merge green)
add_shape("rectangle", 160, 376, 480, 96, fill="#22C55E")
# Middle — Integration Tests (signal cyan)
add_shape("rectangle", 240, 300, 320, 72, fill="#22D3EE")
# Top — End-to-End Tests (cloud lavender)
add_shape("rectangle", 300, 232, 200, 64, fill="#A78BFA")

# KPI metric cards (4 across, beneath pyramid)
add_shape("rectangle", 160, 508, 108, 84, fill="#171C2E")
add_shape("rectangle", 284, 508, 108, 84, fill="#171C2E")
add_shape("rectangle", 408, 508, 108, 84, fill="#171C2E")
add_shape("rectangle", 532, 508, 108, 84, fill="#171C2E")

# Rule card backgrounds (right sidebar, 4 stacked)
add_shape("rectangle", 720, 308, 496, 72, fill="#171C2E")
add_shape("rectangle", 720, 398, 496, 72, fill="#171C2E")
add_shape("rectangle", 720, 488, 496, 72, fill="#171C2E")
add_shape("rectangle", 720, 578, 496, 72, fill="#171C2E")

# --- Icons inside rule cards (one per rule) ---
add_icon("Zap", 740, 326, size=36, color="#22D3EE")
add_icon("Target", 740, 416, size=36, color="#22C55E")
add_icon("Lock", 740, 506, size=36, color="#A78BFA")
add_icon("CheckCircle", 740, 596, size=36, color="#F59E0B")

# --- Editorial header (left zone) ---
add_text("03 — QUALITY ENGINEERING", "caption", 64, 56, 400, 20,
         color="#22D3EE", font_size=14, font_weight=600, letter_spacing=2)

add_text("Confidence Before Velocity", "title", 64, 96, 900, 72,
         color="#F8FAFC", font_size=56, font_weight=700, line_height=1.1)

add_text("Test what matters. Automate what repeats.", "subheading", 64, 174, 900, 32,
         color="#94A3B8", font_size=22, font_weight=500)

# --- Pyramid layer labels (centered inside each layer) ---
add_text("END-TO-END", "paragraph", 300, 253, 200, 22,
         color="#0B1020", font_size=18, font_weight=700,
         text_align="center", letter_spacing=2)

add_text("INTEGRATION TESTS", "paragraph", 240, 325, 320, 22,
         color="#0B1020", font_size=18, font_weight=700,
         text_align="center", letter_spacing=2)

add_text("UNIT TESTS", "paragraph", 160, 413, 480, 22,
         color="#0B1020", font_size=18, font_weight=700,
         text_align="center", letter_spacing=2)

# --- KPI numbers + labels (4 cards) ---
# Card 1 — Coverage
add_text("92%", "heading", 160, 522, 108, 36,
         color="#22C55E", font_size=30, font_weight=700, text_align="center")
add_text("COVERAGE", "caption", 160, 562, 108, 18,
         color="#94A3B8", font_size=11, font_weight=600,
         text_align="center", letter_spacing=1.5)

# Card 2 — Flakiness
add_text("1.4%", "heading", 284, 522, 108, 36,
         color="#F59E0B", font_size=30, font_weight=700, text_align="center")
add_text("FLAKINESS", "caption", 284, 562, 108, 18,
         color="#94A3B8", font_size=11, font_weight=600,
         text_align="center", letter_spacing=1.5)

# Card 3 — Runtime
add_text("4m12s", "heading", 408, 522, 108, 36,
         color="#22D3EE", font_size=30, font_weight=700, text_align="center")
add_text("RUNTIME", "caption", 408, 562, 108, 18,
         color="#94A3B8", font_size=11, font_weight=600,
         text_align="center", letter_spacing=1.5)

# Card 4 — Escape rate
add_text("0.3%", "heading", 532, 522, 108, 36,
         color="#EF4444", font_size=30, font_weight=700, text_align="center")
add_text("ESCAPE RATE", "caption", 532, 562, 108, 18,
         color="#94A3B8", font_size=11, font_weight=600,
         text_align="center", letter_spacing=1.5)

# --- Sidebar header (right zone) ---
add_text("PRINCIPLES OF TESTING", "caption", 720, 224, 480, 18,
         color="#22D3EE", font_size=12, font_weight=600, letter_spacing=2.5)

add_text("Engineering Discipline", "subheading", 720, 250, 480, 36,
         color="#F8FAFC", font_size=28, font_weight=600)

# --- Rule cards (title + body for each) ---
# Rule 1 — Fast
add_text("Fast", "subheading", 776, 320, 380, 28,
         color="#F8FAFC", font_size=22, font_weight=700)
add_text("Sub-10-minute feedback loops keep developers in flow.",
         "caption", 776, 350, 420, 20,
         color="#94A3B8", font_size=14, font_weight=500)

# Rule 2 — Deterministic
add_text("Deterministic", "subheading", 776, 410, 380, 28,
         color="#F8FAFC", font_size=22, font_weight=700)
add_text("No flakes, no random failures, no retries-as-fixes.",
         "caption", 776, 440, 420, 20,
         color="#94A3B8", font_size=14, font_weight=500)

# Rule 3 — Isolated
add_text("Isolated", "subheading", 776, 500, 380, 28,
         color="#F8FAFC", font_size=22, font_weight=700)
add_text("Tests own their state. Never share, never leak.",
         "caption", 776, 530, 420, 20,
         color="#94A3B8", font_size=14, font_weight=500)

# Rule 4 — Meaningful
add_text("Meaningful", "subheading", 776, 590, 380, 28,
         color="#F8FAFC", font_size=22, font_weight=700)
add_text("Assert on behavior, not implementation details.",
         "caption", 776, 620, 420, 20,
         color="#94A3B8", font_size=14, font_weight=500)

# --- Footer attribution ---
add_text("TEST PYRAMID / ADAPTED FROM MIKE COHN, 2009",
         "caption", 64, 662, 600, 18,
         color="#94A3B8", font_size=11, font_weight=500, letter_spacing=2)


# ========================================================
# Assemble final JSON envelope
# ========================================================

total_elements = (
    len(content_text_elements)
    + len(content_shape_elements)
    + len(content_icon_elements)
)

content = {
    "slides": [{
        "id": SLIDE_ID,
        "order": 0,
        "layoutId": "blank-canvas",
        "backgroundColor": "#0B1020",
        "textElements": content_text_elements
    }],
    "imageElements": [],
    "shapeElements": content_shape_elements,
    "chartElements": [],
    "tableElements": [],
    "iconElements": content_icon_elements,
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

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}-batch-slide3",
        "title": "Engineering Excellence: From Commit to Production",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
        "elementCount": total_elements,
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

with open("slide-3.json", "w") as f:
    json.dump(deck, f, indent=2)

print("Wrote slide-3.json")
print(f"slideCount: 1")
print(f"elementCount: {total_elements}")
print(f"  texts:  {len(content_text_elements)}")
print(f"  shapes: {len(content_shape_elements)}")
print(f"  icons:  {len(content_icon_elements)}")
print(f"  zIndex range: 301..{COUNTER}")
