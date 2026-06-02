import json, time

NOW = int(time.time() * 1000)
SLIDE_ID = "slide-4"

# Counter starts at 450 so first next_id() returns 451
COUNTER = 450
def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# Color palette
BG_OBSIDIAN = "#0B1020"
GRAPHITE   = "#171C2E"
NAVY       = "#1E3A5F"
CYAN       = "#22D3EE"
GREEN      = "#22C55E"
AMBER      = "#F59E0B"
RED        = "#EF4444"
LAVENDER   = "#A78BFA"
PAPER      = "#F8FAFC"
STEEL      = "#94A3B8"


# ---------- helpers ----------
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None,
              line_height=None, font_family="Space Grotesk",
              text_align="left", letter_spacing=0,
              text_transform="none"):
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


# ---------- registries ----------
text_elements_per_slide = {SLIDE_ID: []}
content_shape_elements = []
changelog_elements = {}  # keyed by element id


def reg_text(c, cl):
    text_elements_per_slide[c["id"].split("__")[0] and SLIDE_ID].append(c)
    changelog_elements[c["id"]] = cl


def reg_shape(c, cl):
    content_shape_elements.append(c)
    changelog_elements[c["id"]] = cl


# ---------- build slide-4 ----------

# 1. Full background
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   0, 0, 1280, 720, n, NOW, fill=BG_OBSIDIAN)
reg_shape(c, cl)

# 2. Top-left cyan accent bar (vertical)
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   48, 56, 4, 22, n, NOW, fill=CYAN)
reg_shape(c, cl)

# 3. Caption
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID, "04  /  VERSION CONTROL",
                  "caption", 64, 58, 360, 20, n, NOW,
                  color=CYAN, font_size=13, font_weight=600,
                  font_family="JetBrains Mono",
                  letter_spacing=2, text_transform="uppercase")
reg_text(c, cl)

# 4. Title
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID, "The Living Repository",
                  "title", 48, 96, 960, 80, n, NOW,
                  color=PAPER, font_size=64, font_weight=700,
                  letter_spacing=-1)
reg_text(c, cl)

# 5. Subtitle / tagline
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "Code is memory. Every commit, a decision. Every merge, a contract.",
                  "subheading", 48, 188, 880, 40, n, NOW,
                  color=STEEL, font_size=22, font_weight=400, line_height=1.4,
                  font_family="Inter")
reg_text(c, cl)

# 6. Section label for branch timeline
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "BRANCH TIMELINE   ·   git log --graph --decorate",
                  "caption", 48, 290, 600, 18, n, NOW,
                  color=STEEL, font_size=12, font_weight=500,
                  font_family="JetBrains Mono",
                  letter_spacing=2, text_transform="uppercase")
reg_text(c, cl)

# ---------- Git branch diagram ----------
# Coordinates:
#   main branch line at y=470, x from 80 to 680
#   feature branch line at y=400, x from 280 to 400
#   Main commit centers (y=470): 120, 200, 280, 400, 520, 620
#   Feature commit centers (y=400): 320, 360
#   Branch out: vertical line at x=280 from y=400 to y=470
#   Merge in: vertical line at x=400 from y=400 to y=470

# 7. Main branch horizontal line
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   80, 469, 600, 2, n, NOW, fill=CYAN, opacity=0.85)
reg_shape(c, cl)

# 8. Feature branch horizontal line
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   280, 399, 120, 2, n, NOW, fill=LAVENDER, opacity=0.85)
reg_shape(c, cl)

# 9. Vertical connector — branch out at x=280
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   279, 400, 2, 70, n, NOW, fill=LAVENDER, opacity=0.7)
reg_shape(c, cl)

# 10. Vertical connector — merge in at x=400
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   399, 400, 2, 70, n, NOW, fill=LAVENDER, opacity=0.7)
reg_shape(c, cl)

# 11-16. Six commit dots on main (circles, 14x14, centered at y=470)
main_centers = [120, 200, 280, 400, 520, 620]
for cx in main_centers:
    n = next_id()
    c, cl = make_shape(f"shape-{n}", SLIDE_ID, "circle",
                       cx - 7, 463, 14, 14, n, NOW,
                       fill=CYAN, stroke=PAPER, stroke_width=2)
    reg_shape(c, cl)

# 17-18. Two commit dots on feature branch
feature_centers = [320, 360]
for cx in feature_centers:
    n = next_id()
    c, cl = make_shape(f"shape-{n}", SLIDE_ID, "circle",
                       cx - 6, 394, 12, 12, n, NOW,
                       fill=LAVENDER, stroke=PAPER, stroke_width=1)
    reg_shape(c, cl)

# 19. Release tag indicator (amber rectangle above last main commit)
n = next_id()
c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                   600, 440, 44, 4, n, NOW, fill=AMBER)
reg_shape(c, cl)

# 20. "main" branch label (right of main line)
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID, "main",
                  "caption", 692, 462, 80, 18, n, NOW,
                  color=CYAN, font_size=13, font_weight=600,
                  font_family="JetBrains Mono", letter_spacing=1)
reg_text(c, cl)

# 21. "feature/auth-flow" branch label
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID, "feature/auth-flow",
                  "caption", 280, 372, 220, 18, n, NOW,
                  color=LAVENDER, font_size=12, font_weight=500,
                  font_family="JetBrains Mono", letter_spacing=1)
reg_text(c, cl)

# 22. Latest commit hash + message under main
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "a3f9c2b   ·   feat: rotate refresh tokens on session resume",
                  "caption", 96, 494, 560, 18, n, NOW,
                  color=STEEL, font_size=12, font_weight=400,
                  font_family="JetBrains Mono", letter_spacing=0.5)
reg_text(c, cl)

# 23. Release tag label
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID, "v2.4.0  ·  release",
                  "caption", 580, 418, 140, 18, n, NOW,
                  color=AMBER, font_size=12, font_weight=600,
                  font_family="JetBrains Mono", letter_spacing=1)
reg_text(c, cl)

# 24. Diagram footnote — small directional caption
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "Linear history.  Reversible state.  Reviewable diffs.",
                  "caption", 48, 540, 640, 18, n, NOW,
                  color=STEEL, font_size=14, font_weight=500,
                  font_family="Inter", letter_spacing=0.5)
reg_text(c, cl)

# ---------- Right column: Operating Principles ----------

# 25. Section label
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID, "OPERATING PRINCIPLES",
                  "caption", 760, 290, 300, 18, n, NOW,
                  color=CYAN, font_size=12, font_weight=600,
                  font_family="JetBrains Mono",
                  letter_spacing=2, text_transform="uppercase")
reg_text(c, cl)

# 4 cards
principles = [
    ("01", "Small Commits",
     "Each commit tells one story — easy to read, easy to revert."),
    ("02", "Meaningful Messages",
     "Imperative mood. The why before the what. Zero noise."),
    ("03", "Protected Branches",
     "Main is sacred. Required reviews, status checks, signed merges."),
    ("04", "Trunk-Based Flow",
     "Short-lived branches. Frequent integration. Fewer conflicts."),
]

card_x = 760
card_w = 472
card_h = 76
card_gap = 8
card_y_start = 320

for i, (num, title_, desc) in enumerate(principles):
    cy = card_y_start + i * (card_h + card_gap)

    # card background
    n = next_id()
    c, cl = make_shape(f"shape-{n}", SLIDE_ID, "rectangle",
                       card_x, cy, card_w, card_h, n, NOW,
                       fill=GRAPHITE, stroke=NAVY, stroke_width=1)
    reg_shape(c, cl)

    # number (mono cyan)
    n = next_id()
    c, cl = make_text(f"text-{n}", SLIDE_ID, num,
                      "caption", card_x + 20, cy + 14, 40, 20, n, NOW,
                      color=CYAN, font_size=14, font_weight=600,
                      font_family="JetBrains Mono", letter_spacing=1)
    reg_text(c, cl)

    # title
    n = next_id()
    c, cl = make_text(f"text-{n}", SLIDE_ID, title_,
                      "paragraph", card_x + 70, cy + 10, 380, 28, n, NOW,
                      color=PAPER, font_size=20, font_weight=600,
                      line_height=1.2, font_family="IBM Plex Sans")
    reg_text(c, cl)

    # description
    n = next_id()
    c, cl = make_text(f"text-{n}", SLIDE_ID, desc,
                      "caption", card_x + 70, cy + 42, 380, 22, n, NOW,
                      color=STEEL, font_size=13, font_weight=400,
                      line_height=1.4, font_family="Inter")
    reg_text(c, cl)

# Bottom footer line
n = next_id()
c, cl = make_text(f"text-{n}", SLIDE_ID,
                  "$ git log --oneline --graph --decorate --all   "
                  "·   protected: main   ·   policy: signed-commits",
                  "caption", 48, 678, 1100, 18, n, NOW,
                  color=STEEL, font_size=11, font_weight=400,
                  font_family="JetBrains Mono", letter_spacing=1)
reg_text(c, cl)

# ---------- assemble JSON ----------

slide_obj_content = {
    "id": SLIDE_ID,
    "order": 0,
    "layoutId": "blank-canvas",
    "backgroundColor": BG_OBSIDIAN,
    "textElements": text_elements_per_slide[SLIDE_ID],
}

slide_obj_baselayout = {
    "id": SLIDE_ID,
    "layoutId": "blank-canvas",
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": [],
}

content_file = {
    "slides": [slide_obj_content],
    "imageElements": [],
    "shapeElements": content_shape_elements,
    "chartElements": [],
    "tableElements": [],
    "iconElements": [],
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": [],
}

baseLayout_file = {
    "version": "v1",
    "slides": [slide_obj_baselayout],
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
    len(text_elements_per_slide[SLIDE_ID])
    + len(content_shape_elements)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-eng-excellence-slide4-{NOW}",
        "title": "Engineering Excellence — Slide 4: The Living Repository",
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

OUTFILE = "slide-4.json"
with open(OUTFILE, "w") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {OUTFILE}")
print(f"slideCount: 1")
print(f"elementCount: {element_count}")
print(f"  text:   {len(text_elements_per_slide[SLIDE_ID])}")
print(f"  shapes: {len(content_shape_elements)}")
print(f"  changelog entries: {len(changelog_elements)}")
print(f"final COUNTER: {COUNTER}")
