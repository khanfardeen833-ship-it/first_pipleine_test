import json
import time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-2"

# ID/zIndex counter — first new element is 151 per batch constraint
COUNTER = 150
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


# ---------- Helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", text_align="left", letter_spacing=0):
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
    content_record = {"id": shape_id, "slideId": slide_id, "groupId": None}
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


# ---------- Registries ----------
text_elements = []
shape_elements = []
icon_elements = []
changelog_elements = {}

def reg_text(content, changelog):
    text_elements.append(content)
    changelog_elements[content["id"]] = changelog

def reg_shape(content, changelog):
    shape_elements.append(content)
    changelog_elements[content["id"]] = changelog

def reg_icon(content, changelog):
    icon_elements.append(content)
    changelog_elements[content["id"]] = changelog


# ---------- BUILD SLIDE 2 ----------

# 1. Background full slide — Obsidian Console
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 0, 0, 1280, 720, n, NOW,
                      fill="#0B1020"))

# 2. Cyan accent bar under title
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 48, 184, 72, 3, n, NOW,
                      fill="#22D3EE"))

# 3. Chapter caption
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "CHAPTER 02   /   VERSION CONTROL", "caption",
                    48, 56, 600, 18, n, NOW,
                    color="#22D3EE", font_size=12, font_weight=600,
                    font_family="JetBrains Mono", letter_spacing=2))

# 4. Title
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "Version Control Is Memory", "title",
                    48, 96, 1100, 80, n, NOW,
                    color="#F8FAFC", font_size=64, font_weight=700, line_height=1.1))

# 5. Subtitle paragraph
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "Every commit is a decision. Every branch a hypothesis. "
                    "Every merge a conversation — captured forever in the team's shared memory.",
                    "paragraph",
                    48, 200, 600, 72, n, NOW,
                    color="#94A3B8", font_size=18, font_weight=400, line_height=1.55,
                    font_family="Inter"))

# 6. Git history caption (left section label)
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "GIT HISTORY   ·   main  ←  feature/checkout", "caption",
                    48, 296, 480, 16, n, NOW,
                    color="#94A3B8", font_size=11, font_weight=500,
                    font_family="IBM Plex Mono", letter_spacing=1.5))

# ---------- Git Graph (left) ----------
# 7. Main branch vertical line (cyan)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 124, 330, 2, 320, n, NOW,
                      fill="#22D3EE"))

# 8. Feature branch vertical line (green)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 264, 458, 2, 60, n, NOW,
                      fill="#22C55E"))

# 9. Connector branch-off (M4 → feature start)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 125, 516, 140, 2, n, NOW,
                      fill="#22C55E"))

# 10. Connector merge (feature top → M3)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 125, 458, 140, 2, n, NOW,
                      fill="#22C55E"))

# 11–16. Commit dots on main (cyan, 14×14) — except M3 amber merge (18×18)
# M1 (HEAD)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 118, 330, 14, 14, n, NOW,
                      fill="#22D3EE"))
# M2
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 118, 390, 14, 14, n, NOW,
                      fill="#22D3EE"))
# M3 — merge commit (amber, slightly larger)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 116, 450, 18, 18, n, NOW,
                      fill="#F59E0B"))
# M4 — branch-off point
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 118, 510, 14, 14, n, NOW,
                      fill="#22D3EE"))
# M5
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 118, 570, 14, 14, n, NOW,
                      fill="#22D3EE"))
# M6 — initial commit
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 118, 630, 14, 14, n, NOW,
                      fill="#22D3EE"))

# 17–18. Feature commits (green)
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 258, 470, 14, 14, n, NOW,
                      fill="#22C55E"))
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "circle", 258, 498, 14, 14, n, NOW,
                      fill="#22C55E"))

# 19–24. Mono commit labels next to dots
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "a3f8c21   release: v1.4.2", "caption",
                    152, 332, 380, 20, n, NOW,
                    color="#F8FAFC", font_size=13, font_weight=500,
                    font_family="JetBrains Mono"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "9d4b6e7   fix: race condition in queue", "caption",
                    152, 392, 420, 20, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=500,
                    font_family="JetBrains Mono"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "5c1a9f2   merge: feature/checkout → main", "caption",
                    152, 452, 460, 20, n, NOW,
                    color="#F59E0B", font_size=13, font_weight=600,
                    font_family="JetBrains Mono"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "2e7c3b8   refactor: simplify auth flow", "caption",
                    152, 512, 420, 20, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=500,
                    font_family="JetBrains Mono"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "f0a5d29   feat: add pricing page", "caption",
                    152, 572, 380, 20, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=500,
                    font_family="JetBrains Mono"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "1b8e4c0   initial commit", "caption",
                    152, 632, 380, 20, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=500,
                    font_family="JetBrains Mono"))

# 25–26. Feature commit labels (green)
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "8a2f1d3   feat: cart UI", "caption",
                    292, 472, 280, 18, n, NOW,
                    color="#22C55E", font_size=12, font_weight=500,
                    font_family="JetBrains Mono"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "c4e9b7a   test: cart edge cases", "caption",
                    292, 500, 280, 18, n, NOW,
                    color="#22C55E", font_size=12, font_weight=500,
                    font_family="JetBrains Mono"))

# 27. Branch tag — main
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "main", "caption",
                    108, 312, 60, 16, n, NOW,
                    color="#22D3EE", font_size=11, font_weight=600,
                    font_family="JetBrains Mono", letter_spacing=1))

# 28. Branch tag — feature/checkout
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "feature/checkout", "caption",
                    244, 440, 180, 14, n, NOW,
                    color="#22C55E", font_size=10, font_weight=600,
                    font_family="JetBrains Mono", letter_spacing=0.5))

# 29. Right column section caption — PRACTICES
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "PRACTICES   ·   THREE PRINCIPLES", "caption",
                    672, 260, 480, 16, n, NOW,
                    color="#94A3B8", font_size=11, font_weight=500,
                    font_family="IBM Plex Mono", letter_spacing=1.5))

# ---------- Card 1: Small Commits (y=288) ----------
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 672, 288, 560, 124, n, NOW,
                      fill="#171C2E", stroke="#1E3A5F", stroke_width=1))
n = next_id()
reg_icon(*make_icon(f"icon-{n}", SLIDE_ID, "GitCommit", 692, 308, n, NOW,
                    size=24, color="#22D3EE"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID, "01", "caption",
                    724, 312, 40, 18, n, NOW,
                    color="#22D3EE", font_size=14, font_weight=600,
                    font_family="JetBrains Mono", letter_spacing=1))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID, "Small Commits", "subheading",
                    692, 338, 540, 26, n, NOW,
                    color="#F8FAFC", font_size=22, font_weight=600,
                    font_family="IBM Plex Sans"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "One change per commit. Make rollback, review, and bisect feel effortless instead of forensic.",
                    "paragraph",
                    692, 370, 540, 40, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=400, line_height=1.5,
                    font_family="Inter"))

# ---------- Card 2: Clear Branching (y=418) ----------
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 672, 418, 560, 124, n, NOW,
                      fill="#171C2E", stroke="#1E3A5F", stroke_width=1))
n = next_id()
reg_icon(*make_icon(f"icon-{n}", SLIDE_ID, "GitBranch", 692, 438, n, NOW,
                    size=24, color="#22C55E"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID, "02", "caption",
                    724, 442, 40, 18, n, NOW,
                    color="#22C55E", font_size=14, font_weight=600,
                    font_family="JetBrains Mono", letter_spacing=1))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID, "Clear Branching", "subheading",
                    692, 468, 540, 26, n, NOW,
                    color="#F8FAFC", font_size=22, font_weight=600,
                    font_family="IBM Plex Sans"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "Trunk-based flow with short-lived feature branches. Long-running branches quietly become technical debt.",
                    "paragraph",
                    692, 500, 540, 40, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=400, line_height=1.5,
                    font_family="Inter"))

# ---------- Card 3: Readable History (y=548) ----------
n = next_id()
reg_shape(*make_shape(f"shape-{n}", SLIDE_ID, "rectangle", 672, 548, 560, 124, n, NOW,
                      fill="#171C2E", stroke="#1E3A5F", stroke_width=1))
n = next_id()
reg_icon(*make_icon(f"icon-{n}", SLIDE_ID, "History", 692, 568, n, NOW,
                    size=24, color="#A78BFA"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID, "03", "caption",
                    724, 572, 40, 18, n, NOW,
                    color="#A78BFA", font_size=14, font_weight=600,
                    font_family="JetBrains Mono", letter_spacing=1))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID, "Readable History", "subheading",
                    692, 598, 540, 26, n, NOW,
                    color="#F8FAFC", font_size=22, font_weight=600,
                    font_family="IBM Plex Sans"))
n = next_id()
reg_text(*make_text(f"text-{n}", SLIDE_ID,
                    "Write commits the next engineer (and future you) will thank you for. Messages explain why, not what.",
                    "paragraph",
                    692, 630, 540, 40, n, NOW,
                    color="#94A3B8", font_size=13, font_weight=400, line_height=1.5,
                    font_family="Inter"))


# ---------- Assemble files ----------
content_slide = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": "#0B1020",
    "textElements": text_elements,
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
    "slides": [content_slide],
    "imageElements": [],
    "shapeElements": shape_elements,
    "chartElements": [],
    "tableElements": [],
    "iconElements": icon_elements,
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
    },
}

element_count = (
    len(text_elements)
    + len(shape_elements)
    + len(icon_elements)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-{NOW}-batch-slide2",
        "title": "Engineering Excellence: From Commit to Production",
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
    },
}

OUT = "deck.json"
with open(OUT, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {OUT}")
print(f"slideCount = {envelope['presentation']['slideCount']}")
print(f"elementCount = {element_count}")
print(f"  text:  {len(text_elements)}")
print(f"  shape: {len(shape_elements)}")
print(f"  icon:  {len(icon_elements)}")
print(f"changelog entries on {SLIDE_ID}: {len(changelog_elements)}")
