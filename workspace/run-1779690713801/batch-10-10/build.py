import json, time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-10"

# ID + zIndex counter — starts at 1350 so first call returns 1351
COUNTER = 1350
def nx():
    global COUNTER
    COUNTER += 1
    return COUNTER

# --------------- builders ---------------

TEXT_DEFAULTS = {
    "title":      (60, 700, 1.05),
    "subtitle":   (40, 600, 1.35),
    "heading":    (32, 600, 1.30),
    "subheading": (26, 600, 1.30),
    "paragraph":  (22, 700, 1.50),
    "caption":    (18, 600, 1.30),
}

def make_text(tid, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#F8FAFC", font_size=None, font_weight=None,
              line_height=None, font_family="Space Grotesk",
              text_align="left", letter_spacing=0, font_style="normal",
              text_transform="none"):
    fs, fw, lh = TEXT_DEFAULTS[type_]
    if font_size is not None: fs = font_size
    if font_weight is not None: fw = font_weight
    if line_height is not None: lh = line_height
    c = {"id": tid, "content": text, "type": type_,
         "originalType": type_, "groupId": None, "formattedContent": text}
    cl = {
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
            "shadowTransparency": 40, "shadowColor": "#000000",
        },
        "formattedContent": text,
        "animation": {"enter": "none", "exit": "fade", "duration": 550,
                      "delay": 0, "trigger": "both", "typewriterMode": "character"},
        "enterAnimation": "none", "exitAnimation": "fade",
        "animationEffect": "none", "animationDurationMs": 550,
        "animationDelayMs": 0, "animationTrigger": "both",
        "animationTypewriterMode": "character", "updatedAt": now,
    }
    return c, cl

def make_shape(sid, slide_id, shape_type, x, y, w, h, zidx, now,
               fill="#171C2E", stroke=None, stroke_width=0, opacity=1):
    if stroke is None: stroke = fill
    c = {"id": sid, "slideId": slide_id, "groupId": None}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "width": w, "height": h, "rotation": 0, "zIndex": zidx,
          "opacity": opacity, "shapeType": shape_type,
          "fill": fill, "stroke": stroke, "strokeWidth": stroke_width,
          "updatedAt": now}
    return c, cl

def make_icon(iid, slide_id, name, x, y, zidx, now,
              size=64, color="#22D3EE", opacity=1):
    c = {"id": iid, "slideId": slide_id, "groupId": None,
         "iconName": name, "iconSource": "lucide"}
    cl = {"slideId": slide_id, "position": {"x": x, "y": y},
          "width": size, "height": size, "rotation": 0,
          "zIndex": zidx, "color": color, "opacity": opacity,
          "updatedAt": now}
    return c, cl

# --------------- slide build ---------------

text_content = []  # textElements inside the slide
shape_content = []
icon_content = []
changelog_elements = {}

def add_text(*args, **kwargs):
    n = nx()
    tid = f"text-{n}"
    c, cl = make_text(tid, SLIDE_ID, args[0], args[1], *args[2:],
                       zidx=n, now=NOW, **kwargs)
    text_content.append(c)
    changelog_elements[tid] = cl
    return tid

def add_shape(shape_type, x, y, w, h, **kwargs):
    n = nx()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, SLIDE_ID, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_content.append(c)
    changelog_elements[sid] = cl
    return sid

def add_icon(name, x, y, **kwargs):
    n = nx()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, SLIDE_ID, name, x, y, n, NOW, **kwargs)
    icon_content.append(c)
    changelog_elements[iid] = cl
    return iid

# ---------- background ----------
# A very faint accent bar on the left edge for editorial signature
add_shape("rectangle", 0, 0, 1280, 720, fill="#0B1020", opacity=1)  # full bg
add_shape("rectangle", 48, 48, 4, 624, fill="#22D3EE", opacity=0.85)  # left accent rail

# ---------- top band ----------
add_text("10 · CODE REVIEW", "caption", 72, 56, 320, 20,
         color="#22D3EE", font_size=13, letter_spacing=4,
         font_family="JetBrains Mono", text_transform="uppercase")

add_text("The Human Firewall", "title", 72, 84, 1100, 72,
         color="#F8FAFC", font_size=64, font_weight=700,
         line_height=1.05)

add_text("“Review the idea, not the person.”  The discipline that catches what tests cannot.",
         "paragraph", 72, 168, 1100, 28,
         color="#94A3B8", font_size=18, font_weight=400,
         line_height=1.40, font_style="italic")

# ---------- LEFT: PR mockup ----------
# outer card
add_shape("rectangle", 72, 220, 552, 452,
          fill="#171C2E", stroke="#1E3A5F", stroke_width=1)

# small status bar at top of card
add_shape("rectangle", 72, 220, 552, 36, fill="#1E3A5F", opacity=0.55)
add_shape("circle", 88, 234, 8, 8, fill="#22C55E")  # status dot
add_text("PULL REQUEST · #1247", "caption", 108, 230, 240, 16,
         color="#94A3B8", font_size=11, letter_spacing=2,
         font_family="JetBrains Mono", text_transform="uppercase")
add_text("OPEN · 3 commits", "caption", 460, 230, 160, 16,
         color="#22C55E", font_size=11, letter_spacing=2,
         font_family="JetBrains Mono", text_transform="uppercase",
         text_align="right")

# PR title + meta
add_text("feat(api): add retry logic to client", "subheading", 96, 268, 504, 30,
         color="#F8FAFC", font_size=22, font_weight=600, line_height=1.25)
add_text("feature/retry-logic → main   ·   +24  −7   ·   2 reviewers",
         "caption", 96, 302, 504, 18,
         color="#94A3B8", font_size=12, font_family="JetBrains Mono")

# divider
add_shape("rectangle", 96, 332, 504, 1, fill="#1E3A5F")

# diff block — code lines
DIFF_X = 96
DIFF_W = 504
add_text("  async function fetchUser(id) {", "caption", DIFF_X, 348, DIFF_W, 22,
         color="#94A3B8", font_size=14, font_family="JetBrains Mono",
         font_weight=400, line_height=1.5)

# minus line — red wash
add_shape("rectangle", DIFF_X-4, 374, DIFF_W+8, 24, fill="#EF4444", opacity=0.10)
add_text("-   return api.get(`/users/${id}`);", "caption", DIFF_X, 376, DIFF_W, 22,
         color="#FCA5A5", font_size=14, font_family="JetBrains Mono",
         font_weight=500, line_height=1.5)

# plus lines — green wash
add_shape("rectangle", DIFF_X-4, 402, DIFF_W+8, 24, fill="#22C55E", opacity=0.12)
add_text("+   return retry(", "caption", DIFF_X, 404, DIFF_W, 22,
         color="#86EFAC", font_size=14, font_family="JetBrains Mono",
         font_weight=500, line_height=1.5)

add_shape("rectangle", DIFF_X-4, 426, DIFF_W+8, 24, fill="#22C55E", opacity=0.12)
add_text("+     () => api.get(`/users/${id}`), { max: 3 });",
         "caption", DIFF_X, 428, DIFF_W, 22,
         color="#86EFAC", font_size=14, font_family="JetBrains Mono",
         font_weight=500, line_height=1.5)

add_text("  }", "caption", DIFF_X, 454, DIFF_W, 22,
         color="#94A3B8", font_size=14, font_family="JetBrains Mono",
         font_weight=400, line_height=1.5)

# inline comment block
add_shape("rectangle", 96, 488, 504, 96, fill="#1E3A5F", opacity=0.55,
          stroke="#22D3EE", stroke_width=0)
add_shape("rectangle", 96, 488, 3, 96, fill="#22D3EE")  # left rail
add_text("@alex.chen   ·   senior reviewer", "caption", 112, 500, 480, 16,
         color="#22D3EE", font_size=11, letter_spacing=1.5,
         font_family="JetBrains Mono", text_transform="uppercase")
add_text("Nice. Add a max-backoff cap so retries can't compound under load — and a test for the timeout path.",
         "paragraph", 112, 522, 472, 50,
         color="#F8FAFC", font_size=14, font_weight=400, line_height=1.45)

# approval badge bottom
add_shape("rectangle", 96, 604, 220, 40, fill="#22C55E", opacity=0.18,
          stroke="#22C55E", stroke_width=1)
add_icon("CheckCircle", 108, 612, size=24, color="#22C55E")
add_text("APPROVED · READY TO MERGE", "caption", 142, 615, 170, 18,
         color="#22C55E", font_size=11, letter_spacing=2,
         font_family="JetBrains Mono", text_transform="uppercase",
         font_weight=600)

# small commit hash on the right of the badge
add_text("a3f9e1c", "caption", 540, 615, 80, 18,
         color="#94A3B8", font_size=12, font_family="JetBrains Mono",
         text_align="right")

# ---------- RIGHT: Three pillars ----------
add_text("THE THREE LENSES", "caption", 664, 230, 280, 16,
         color="#A78BFA", font_size=11, letter_spacing=3,
         font_family="JetBrains Mono", text_transform="uppercase")

add_text("Three lenses for every diff", "subheading", 664, 252, 568, 30,
         color="#F8FAFC", font_size=20, font_weight=600, line_height=1.25)

# pillar card geometry
PX = 664
PW = 568
PH = 110
GAP = 14

# Card 1 — Clarity (cyan)
y1 = 296
add_shape("rectangle", PX, y1, PW, PH, fill="#171C2E",
          stroke="#1E3A5F", stroke_width=1)
add_shape("rectangle", PX, y1, 3, PH, fill="#22D3EE")
add_icon("Eye", PX+24, y1+24, size=44, color="#22D3EE")
add_text("Clarity", "subheading", PX+92, y1+22, 440, 28,
         color="#F8FAFC", font_size=22, font_weight=600)
add_text("Code should explain itself. Names, structure, and intent legible at a glance — no archaeology required.",
         "paragraph", PX+92, y1+54, 452, 44,
         color="#94A3B8", font_size=14, font_weight=400, line_height=1.45)

# Card 2 — Correctness (green)
y2 = y1 + PH + GAP
add_shape("rectangle", PX, y2, PW, PH, fill="#171C2E",
          stroke="#1E3A5F", stroke_width=1)
add_shape("rectangle", PX, y2, 3, PH, fill="#22C55E")
add_icon("ShieldCheck", PX+24, y2+24, size=44, color="#22C55E")
add_text("Correctness", "subheading", PX+92, y2+22, 440, 28,
         color="#F8FAFC", font_size=22, font_weight=600)
add_text("Trust is verified, not assumed. Edge cases surfaced, invariants protected, failure modes named before production.",
         "paragraph", PX+92, y2+54, 452, 44,
         color="#94A3B8", font_size=14, font_weight=400, line_height=1.45)

# Card 3 — Maintainability (lavender)
y3 = y2 + PH + GAP
add_shape("rectangle", PX, y3, PW, PH, fill="#171C2E",
          stroke="#1E3A5F", stroke_width=1)
add_shape("rectangle", PX, y3, 3, PH, fill="#A78BFA")
add_icon("Wrench", PX+24, y3+24, size=44, color="#A78BFA")
add_text("Maintainability", "subheading", PX+92, y3+22, 440, 28,
         color="#F8FAFC", font_size=22, font_weight=600)
add_text("Choices that age well. Small interfaces, low coupling, and obvious extension points — future engineers will thank this PR.",
         "paragraph", PX+92, y3+54, 452, 44,
         color="#94A3B8", font_size=14, font_weight=400, line_height=1.45)

# bottom-right footer caption
add_text("REVIEW THE IDEA · DEFEND THE USER · TEACH THE NEXT ENGINEER",
         "caption", 72, 686, 1136, 16,
         color="#475569", font_size=10, letter_spacing=4,
         font_family="JetBrains Mono", text_transform="uppercase",
         text_align="center")

# --------------- assemble files ---------------

slide_obj = {
    "id": SLIDE_ID,
    "order": 9,           # slide-10 → index 9
    "layoutId": "blank-canvas",
    "backgroundColor": "#0B1020",
    "textElements": text_content,
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
    "shapeElements": shape_content,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_content,
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
        SLIDE_ID: {"elements": changelog_elements}
    }
}

element_count = (
    len(text_content) + len(shape_content) + len(icon_content)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-slide10-{NOW}",
        "title": "Engineering Excellence — Slide 10 (Code Review: The Human Firewall)",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 1,
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

OUT = "slide-10.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deck, f, indent=2, ensure_ascii=False)

# integrity report
text_ids = {t["id"] for t in text_content}
shape_ids = {s["id"] for s in shape_content}
icon_ids = {i["id"] for i in icon_content}
cl_ids = set(changelog_elements.keys())
missing = (text_ids | shape_ids | icon_ids) - cl_ids
extra = cl_ids - (text_ids | shape_ids | icon_ids)
zs = [v["zIndex"] for v in changelog_elements.values()]

print(f"file: {OUT}")
print(f"slides: 1   elements: {element_count}")
print(f"text: {len(text_content)}  shapes: {len(shape_content)}  icons: {len(icon_content)}")
print(f"changelog entries: {len(changelog_elements)}")
print(f"missing in changelog: {missing or 'none'}")
print(f"orphan in changelog : {extra or 'none'}")
print(f"zIndex range: {min(zs)}..{max(zs)}  unique: {len(set(zs)) == len(zs)}")
print(f"counter end: {COUNTER}")
