import json, time

NOW = int(time.time() * 1000)

# ---- counters ----
COUNTER = 300  # element IDs start so first text = text-301
ZIDX = 300     # zIndex starts at 301

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX

# ---- helpers ----
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              font_family="Space Grotesk", text_align="left", letter_spacing=0,
              font_style="normal", text_transform="none"):
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


# ---- palette ----
HIGHLAND_ESPRESSO = "#2A170F"
ROASTED_CACAO = "#4A2C1A"
CEREMONY_CLAY = "#8B4A2F"
COFFEE_CHERRY = "#A83228"
GOLDEN_CREMA = "#D6A15D"
PARCHMENT = "#F2E7D5"
HIGHLAND_MIST = "#D9D3C4"
YIRGACHEFFE_GREEN = "#4F6F45"
JASMINE_WHITE = "#FFF8EA"
BLUE_HOUR = "#26313A"

SERIF = "Georgia"
SANS = "Space Grotesk"
MONO = "Courier New"

# ---- containers ----
slides_content = []
slides_baselayout = []
text_elements_by_slide = {}
image_elements = []
shape_elements = []
icon_elements = []
chart_elements = []
table_elements = []
changelog_slides = {}

slide_ids = ["slide-6", "slide-7", "slide-8", "slide-9", "slide-10"]
for sid in slide_ids:
    text_elements_by_slide[sid] = []
    changelog_slides[sid] = {"elements": {}}


def register_text(slide_id, c, cl):
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][c["id"]] = cl

def register_shape(slide_id, c, cl):
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][c["id"]] = cl

def register_image(slide_id, c, cl):
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][c["id"]] = cl

def register_icon(slide_id, c, cl):
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][c["id"]] = cl


# ============================================================================
# SLIDE 6 — The Washing Stations
# ============================================================================
sid = "slide-6"
slides_content.append({
    "id": sid, "order": 5, "layoutId": "blank-canvas",
    "backgroundColor": PARCHMENT, "textElements": []
})
slides_baselayout.append({
    "id": sid, "layoutId": "blank-canvas",
    "imageElements": [], "shapeElements": [],
    "chartElements": [], "iconElements": [], "embedElements": []
})

# Left full-height image of washing station / drying beds
n = next_id(); z = nextz()
c, cl = make_image(f"image-{n}", sid,
    "https://images.pexels.com/photos/4820807/pexels-photo-4820807.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 640, 720, z, NOW)
register_image(sid, c, cl)

# Dark scrim shape across image bottom for caption
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 600, 640, 120, z, NOW,
                   fill=HIGHLAND_ESPRESSO, opacity=0.55)
register_shape(sid, c, cl)

# Right panel - parchment background (already slide bg, add subtle accent rect)
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 640, 0, 640, 720, z, NOW,
                   fill=PARCHMENT, opacity=1)
register_shape(sid, c, cl)

# Vertical golden rule between halves
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 640, 80, 1, 560, z, NOW,
                   fill=GOLDEN_CREMA, opacity=0.6)
register_shape(sid, c, cl)

# Mono caption top-right
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "CHAPTER  /  06", "caption",
                  680, 64, 200, 24, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=11,
                  letter_spacing=4, text_transform="uppercase")
register_text(sid, c, cl)

# Mono caption on image
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "WASHING STATION  /  YIRGACHEFFE", "caption",
                  32, 632, 500, 24, z, NOW,
                  color=JASMINE_WHITE, font_family=MONO, font_size=11,
                  letter_spacing=4, text_transform="uppercase")
register_text(sid, c, cl)

# Title - editorial serif
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "Where Fruit\nBecomes Origin", "title",
                  680, 110, 560, 160, z, NOW,
                  color=HIGHLAND_ESPRESSO, font_family=SERIF, font_size=58,
                  font_weight=400, line_height=1.05, font_style="italic")
register_text(sid, c, cl)

# Body paragraph
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "At the washing stations of Sidama and Yirgacheffe, water, wood, and patient hands begin the slow alchemy that turns ripe cherries into the parchment beans the world will one day taste.",
                  "paragraph", 680, 290, 500, 130, z, NOW,
                  color=ROASTED_CACAO, font_family=SANS, font_size=17,
                  font_weight=400, line_height=1.55)
register_text(sid, c, cl)

# Process diagram - 4 stages with circles + labels
process_y = 460
stages = [
    ("Pick",    "Hand-sorted ripe cherries", "Hand"),
    ("Depulp",  "Skin & pulp removed",        "Droplet"),
    ("Ferment", "12–48 hours in fresh water", "Waves"),
    ("Dry",     "Sun-cured on raised beds",   "Sun"),
]

# Horizontal connector line behind stages
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 700, process_y + 35, 480, 1, z, NOW,
                   fill=GOLDEN_CREMA, opacity=0.7)
register_shape(sid, c, cl)

# Stage circles + numbers + labels
for i, (label, desc, icon_name) in enumerate(stages):
    cx = 700 + i * 130
    # Circle
    n = next_id(); z = nextz()
    c, cl = make_shape(f"shape-{n}", sid, "circle", cx, process_y, 70, 70, z, NOW,
                       fill=PARCHMENT, stroke=CEREMONY_CLAY, stroke_width=2)
    register_shape(sid, c, cl)
    # Stage number in mono
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, f"0{i+1}", "caption",
                      cx, process_y + 22, 70, 28, z, NOW,
                      color=COFFEE_CHERRY, font_family=MONO, font_size=14,
                      font_weight=700, text_align="center", letter_spacing=2)
    register_text(sid, c, cl)
    # Stage label
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, label, "subheading",
                      cx - 20, process_y + 86, 110, 26, z, NOW,
                      color=HIGHLAND_ESPRESSO, font_family=SERIF, font_size=20,
                      font_weight=600, text_align="center")
    register_text(sid, c, cl)
    # Stage description in mono
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, desc, "caption",
                      cx - 35, process_y + 116, 140, 36, z, NOW,
                      color=ROASTED_CACAO, font_family=MONO, font_size=10,
                      font_weight=500, text_align="center", line_height=1.4)
    register_text(sid, c, cl)

# Footer rule + caption
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "PROCESS  ·  WASHED METHOD  ·  ETHIOPIA", "caption",
                  680, 660, 500, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=10,
                  letter_spacing=4, text_transform="uppercase")
register_text(sid, c, cl)


# ============================================================================
# SLIDE 7 — The Jebena Breathes
# ============================================================================
sid = "slide-7"
slides_content.append({
    "id": sid, "order": 6, "layoutId": "blank-canvas",
    "backgroundColor": HIGHLAND_ESPRESSO, "textElements": []
})
slides_baselayout.append({
    "id": sid, "layoutId": "blank-canvas",
    "imageElements": [], "shapeElements": [],
    "chartElements": [], "iconElements": [], "embedElements": []
})

# Full-bleed dark cinematic image of jebena / coffee pouring
n = next_id(); z = nextz()
c, cl = make_image(f"image-{n}", sid,
    "https://images.pexels.com/photos/3026808/pexels-photo-3026808.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 1280, 720, z, NOW, is_background=True, opacity=0.85)
register_image(sid, c, cl)

# Dark left-side gradient veil - heavy left, fading right
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 0, 560, 720, z, NOW,
                   fill=HIGHLAND_ESPRESSO, opacity=0.78)
register_shape(sid, c, cl)

# Soft transition strip
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 560, 0, 200, 720, z, NOW,
                   fill=HIGHLAND_ESPRESSO, opacity=0.4)
register_shape(sid, c, cl)

# Top mono folio
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "ORIGIN  /  CHAPTER  07", "caption",
                  64, 48, 300, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

# Thin gold rule
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 64, 86, 56, 1, z, NOW,
                   fill=GOLDEN_CREMA, opacity=0.9)
register_shape(sid, c, cl)

# Vertical text stack on left - large serif title
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "The Jebena\nBreathes", "title",
                  64, 250, 480, 200, z, NOW,
                  color=JASMINE_WHITE, font_family=SERIF, font_size=78,
                  font_weight=400, line_height=1.0, font_style="italic")
register_text(sid, c, cl)

# Subtitle line
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "Clay, fire, and patience —\nthe oldest coffee vessel still in daily use.",
                  "subtitle", 64, 460, 480, 80, z, NOW,
                  color=HIGHLAND_MIST, font_family=SANS, font_size=20,
                  font_weight=400, line_height=1.5)
register_text(sid, c, cl)

# Small ember ornament
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "circle", 64, 568, 8, 8, z, NOW,
                   fill=COFFEE_CHERRY, opacity=1)
register_shape(sid, c, cl)

# Mono caption bottom-left
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "BUNNA CEREMONY  /  ETHIOPIA", "caption",
                  88, 568, 400, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

# Bottom poetic line
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "“To pour bunna is to slow the world.”",
                  "caption", 64, 624, 480, 30, z, NOW,
                  color=GOLDEN_CREMA, font_family=SERIF, font_size=18,
                  font_weight=400, font_style="italic")
register_text(sid, c, cl)

# Right edge thin folio
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "07  /  15", "caption",
                  1170, 670, 80, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=4, text_align="right")
register_text(sid, c, cl)


# ============================================================================
# SLIDE 8 — The Ceremony of Smoke & Welcome
# ============================================================================
sid = "slide-8"
slides_content.append({
    "id": sid, "order": 7, "layoutId": "blank-canvas",
    "backgroundColor": HIGHLAND_ESPRESSO, "textElements": []
})
slides_baselayout.append({
    "id": sid, "layoutId": "blank-canvas",
    "imageElements": [], "shapeElements": [],
    "chartElements": [], "iconElements": [], "embedElements": []
})

# Full bleed candlelit ceremony scene
n = next_id(); z = nextz()
c, cl = make_image(f"image-{n}", sid,
    "https://images.pexels.com/photos/4820817/pexels-photo-4820817.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 1280, 720, z, NOW, is_background=True, opacity=0.92)
register_image(sid, c, cl)

# Dark left gradient veil
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 0, 640, 720, z, NOW,
                   fill=HIGHLAND_ESPRESSO, opacity=0.55)
register_shape(sid, c, cl)

# Top folio
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "RITUAL  /  CHAPTER  08", "caption",
                  64, 48, 300, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

# Thin top rule
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 64, 86, 56, 1, z, NOW,
                   fill=GOLDEN_CREMA, opacity=0.9)
register_shape(sid, c, cl)

# Large ivory serif title - upper left
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "Smoke,\nWelcome,\n& Time.", "title",
                  64, 150, 560, 320, z, NOW,
                  color=JASMINE_WHITE, font_family=SERIF, font_size=92,
                  font_weight=400, line_height=1.02, font_style="italic")
register_text(sid, c, cl)

# Body text - restrained editorial
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "Frankincense rises with the first roast. Beans crack over charcoal. A small grass mat is laid, and the ceremony begins — not as performance, but as the quiet language of hospitality.",
                  "paragraph", 64, 470, 520, 130, z, NOW,
                  color=HIGHLAND_MIST, font_family=SANS, font_size=18,
                  font_weight=400, line_height=1.6)
register_text(sid, c, cl)

# Bottom caption strip - thin gold rule
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 64, 658, 1152, 1, z, NOW,
                   fill=GOLDEN_CREMA, opacity=0.4)
register_shape(sid, c, cl)

# Bottom mono caption
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "BUNNA CEREMONY  /  ETHIOPIA", "caption",
                  64, 676, 400, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

# Right edge accent caption
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "Charcoal · Incense · Grass · Cup", "caption",
                  760, 676, 460, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=3, text_align="right")
register_text(sid, c, cl)

# Folio number
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "08  /  15", "caption",
                  1170, 48, 80, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=4, text_align="right")
register_text(sid, c, cl)


# ============================================================================
# SLIDE 9 — Three Cups, Three Blessings
# ============================================================================
sid = "slide-9"
slides_content.append({
    "id": sid, "order": 8, "layoutId": "blank-canvas",
    "backgroundColor": PARCHMENT, "textElements": []
})
slides_baselayout.append({
    "id": sid, "layoutId": "blank-canvas",
    "imageElements": [], "shapeElements": [],
    "chartElements": [], "iconElements": [], "embedElements": []
})

# Top mono folio
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "CHAPTER  /  09", "caption",
                  64, 56, 200, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

# Right folio
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "ETHIOPIA  /  BUNNA", "caption",
                  1016, 56, 200, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase", text_align="right")
register_text(sid, c, cl)

# Top thin rule
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 64, 88, 1152, 1, z, NOW,
                   fill=CEREMONY_CLAY, opacity=0.4)
register_shape(sid, c, cl)

# Headline at top - centered
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "Three Cups, Three Blessings", "title",
                  64, 112, 1152, 70, z, NOW,
                  color=HIGHLAND_ESPRESSO, font_family=SERIF, font_size=52,
                  font_weight=400, line_height=1.1, font_style="italic",
                  text_align="center")
register_text(sid, c, cl)

# Subhead
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "A ceremony measured not in minutes, but in pours.",
                  "subtitle", 64, 184, 1152, 30, z, NOW,
                  color=ROASTED_CACAO, font_family=SANS, font_size=18,
                  font_weight=400, text_align="center", letter_spacing=1)
register_text(sid, c, cl)

# Triptych — three vertical panels
panels = [
    ("Abol",   "First",  "The strongest pour. A blessing of welcome and beginning.",
     "https://images.pexels.com/photos/162947/coffee-pour-arabica-cup-162947.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
    ("Tona",   "Second", "Lighter, sweeter — the blessing of friendship taking root.",
     "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
    ("Baraka", "Third",  "The softest cup. A blessing carried into the day ahead.",
     "https://images.pexels.com/photos/585750/pexels-photo-585750.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"),
]

panel_w = 350
panel_gap = 44
total_w = panel_w * 3 + panel_gap * 2
start_x = (1280 - total_w) // 2  # centered

for i, (name, order_label, desc, src) in enumerate(panels):
    px = start_x + i * (panel_w + panel_gap)
    py = 240

    # Panel image
    n = next_id(); z = nextz()
    c, cl = make_image(f"image-{n}", sid, src,
                       px, py, panel_w, 280, z, NOW)
    register_image(sid, c, cl)

    # Subtle dark scrim under image
    n = next_id(); z = nextz()
    c, cl = make_shape(f"shape-{n}", sid, "rectangle", px, py + 220, panel_w, 60, z, NOW,
                       fill=HIGHLAND_ESPRESSO, opacity=0.35)
    register_shape(sid, c, cl)

    # Order label (mono) on image
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, f"POUR  ·  {order_label.upper()}", "caption",
                      px + 16, py + 240, 200, 20, z, NOW,
                      color=JASMINE_WHITE, font_family=MONO, font_size=10,
                      letter_spacing=4, text_transform="uppercase")
    register_text(sid, c, cl)

    # Blessing name (large serif)
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, name, "title",
                      px, py + 296, panel_w, 70, z, NOW,
                      color=HIGHLAND_ESPRESSO, font_family=SERIF, font_size=46,
                      font_weight=400, line_height=1.05, font_style="italic",
                      text_align="center")
    register_text(sid, c, cl)

    # Thin clay rule under name
    n = next_id(); z = nextz()
    c, cl = make_shape(f"shape-{n}", sid, "rectangle",
                       px + panel_w//2 - 20, py + 376, 40, 1, z, NOW,
                       fill=COFFEE_CHERRY, opacity=0.9)
    register_shape(sid, c, cl)

    # Description sans
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, desc, "paragraph",
                      px + 18, py + 396, panel_w - 36, 80, z, NOW,
                      color=ROASTED_CACAO, font_family=SANS, font_size=15,
                      font_weight=400, line_height=1.55, text_align="center")
    register_text(sid, c, cl)

# Bottom rule
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 64, 670, 1152, 1, z, NOW,
                   fill=CEREMONY_CLAY, opacity=0.3)
register_shape(sid, c, cl)

# Bottom caption
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "ABOL  ·  TONA  ·  BARAKA", "caption",
                  64, 688, 1152, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=10,
                  letter_spacing=8, text_transform="uppercase", text_align="center")
register_text(sid, c, cl)


# ============================================================================
# SLIDE 10 — The Flavor of Altitude
# ============================================================================
sid = "slide-10"
slides_content.append({
    "id": sid, "order": 9, "layoutId": "blank-canvas",
    "backgroundColor": PARCHMENT, "textElements": []
})
slides_baselayout.append({
    "id": sid, "layoutId": "blank-canvas",
    "imageElements": [], "shapeElements": [],
    "chartElements": [], "iconElements": [], "embedElements": []
})

# Left - misty highland landscape full height
n = next_id(); z = nextz()
c, cl = make_image(f"image-{n}", sid,
    "https://images.pexels.com/photos/281260/pexels-photo-281260.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    0, 0, 560, 720, z, NOW)
register_image(sid, c, cl)

# Subtle dark gradient overlay on lower image for caption
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 0, 540, 560, 180, z, NOW,
                   fill=BLUE_HOUR, opacity=0.55)
register_shape(sid, c, cl)

# Mono caption on image
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "ELEVATION  /  1,500 — 2,200 M", "caption",
                  32, 588, 500, 20, z, NOW,
                  color=GOLDEN_CREMA, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

# Image title overlay
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "The Highland\nGrows the Cup", "subtitle",
                  32, 620, 500, 80, z, NOW,
                  color=JASMINE_WHITE, font_family=SERIF, font_size=28,
                  font_weight=400, line_height=1.15, font_style="italic")
register_text(sid, c, cl)

# Right side - parchment background with flavor diagram (slide bg already)
# Right top folio
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "CHAPTER  /  10", "caption",
                  608, 56, 200, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase")
register_text(sid, c, cl)

n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "TASTING  /  ETHIOPIA", "caption",
                  1000, 56, 220, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=11,
                  letter_spacing=5, text_transform="uppercase", text_align="right")
register_text(sid, c, cl)

# Top thin rule on right side
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 608, 88, 608, 1, z, NOW,
                   fill=CEREMONY_CLAY, opacity=0.4)
register_shape(sid, c, cl)

# Right side title
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid, "The Flavor\nof Altitude", "title",
                  608, 116, 608, 140, z, NOW,
                  color=HIGHLAND_ESPRESSO, font_family=SERIF, font_size=54,
                  font_weight=400, line_height=1.05, font_style="italic")
register_text(sid, c, cl)

# Body intro
n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "Each elevation band whispers a different note —\nfrom citrus brightness above the clouds to cocoa weight in lower forests.",
                  "paragraph", 608, 268, 600, 60, z, NOW,
                  color=ROASTED_CACAO, font_family=SANS, font_size=16,
                  font_weight=400, line_height=1.55)
register_text(sid, c, cl)

# Altitude diagram - 4 bands (top = highest altitude = brightest)
# Each row: altitude label (mono), bar (filled), flavor notes
diagram_x = 608
diagram_y = 360
band_h = 56
band_gap = 8

bands = [
    ("2,200 M", "Jasmine · Bergamot · Lemon Zest", 1.00, YIRGACHEFFE_GREEN),
    ("2,000 M", "Floral · Black Tea · Citrus",      0.78, CEREMONY_CLAY),
    ("1,800 M", "Berry · Wine-like · Stone Fruit",  0.58, COFFEE_CHERRY),
    ("1,500 M", "Cocoa · Brown Sugar · Spice",      0.38, ROASTED_CACAO),
]

# Vertical scale axis line on left of bars
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle",
                   diagram_x + 80, diagram_y - 8, 1, len(bands) * (band_h + band_gap), z, NOW,
                   fill=CEREMONY_CLAY, opacity=0.4)
register_shape(sid, c, cl)

bar_max_w = 460
for i, (alt, notes, frac, color) in enumerate(bands):
    by = diagram_y + i * (band_h + band_gap)
    # Altitude label mono
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, alt, "caption",
                      diagram_x, by + 18, 76, 20, z, NOW,
                      color=ROASTED_CACAO, font_family=MONO, font_size=11,
                      font_weight=700, letter_spacing=2, text_align="right")
    register_text(sid, c, cl)
    # tick mark
    n = next_id(); z = nextz()
    c, cl = make_shape(f"shape-{n}", sid, "rectangle",
                       diagram_x + 78, by + 26, 6, 1, z, NOW,
                       fill=CEREMONY_CLAY, opacity=0.7)
    register_shape(sid, c, cl)
    # Bar - background track
    n = next_id(); z = nextz()
    c, cl = make_shape(f"shape-{n}", sid, "rectangle",
                       diagram_x + 92, by + 22, bar_max_w, 12, z, NOW,
                       fill=HIGHLAND_MIST, opacity=0.6)
    register_shape(sid, c, cl)
    # Bar - filled portion
    n = next_id(); z = nextz()
    c, cl = make_shape(f"shape-{n}", sid, "rectangle",
                       diagram_x + 92, by + 22, int(bar_max_w * frac), 12, z, NOW,
                       fill=color, opacity=1)
    register_shape(sid, c, cl)
    # Flavor notes - sans
    n = next_id(); z = nextz()
    c, cl = make_text(f"text-{n}", sid, notes, "caption",
                      diagram_x + 92, by, bar_max_w, 20, z, NOW,
                      color=HIGHLAND_ESPRESSO, font_family=SERIF, font_size=15,
                      font_weight=400, font_style="italic")
    register_text(sid, c, cl)

# Bottom legend / source line
n = next_id(); z = nextz()
c, cl = make_shape(f"shape-{n}", sid, "rectangle", 608, 658, 608, 1, z, NOW,
                   fill=CEREMONY_CLAY, opacity=0.3)
register_shape(sid, c, cl)

n = next_id(); z = nextz()
c, cl = make_text(f"text-{n}", sid,
                  "TASTING NOTES — TYPICAL ETHIOPIAN ARABICA, WASHED PROCESS",
                  "caption", 608, 676, 608, 20, z, NOW,
                  color=CEREMONY_CLAY, font_family=MONO, font_size=10,
                  letter_spacing=4, text_transform="uppercase")
register_text(sid, c, cl)


# ============================================================================
# Assemble final JSON
# ============================================================================

# Place text elements into their slides
for s in slides_content:
    s["textElements"] = text_elements_by_slide[s["id"]]

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

baseLayout_file = {
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

# Compute element count
element_count = (
    sum(len(s["textElements"]) for s in slides_content)
    + len(image_elements) + len(shape_elements) + len(chart_elements)
    + len(table_elements) + len(icon_elements)
)

deck = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-batch-6-10-{NOW}",
        "title": "ORIGIN: Ethiopia's Living Coffee Legacy (Slides 6-10)",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": len(slides_content),
        "elementCount": element_count,
        "createdAt": "2026-05-22T00:00:00.000Z",
        "updatedAt": "2026-05-22T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content_file,
        "baseLayout": baseLayout_file,
        "changelog": changelog_file
    }
}

OUT = "ethiopia_coffee_batch_6_10.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(deck, f, indent=2, ensure_ascii=False)

print(f"Wrote {OUT}")
print(f"Slides: {len(slides_content)}")
print(f"Elements: {element_count}")
print(f"  text: {sum(len(s['textElements']) for s in slides_content)}")
print(f"  images: {len(image_elements)}")
print(f"  shapes: {len(shape_elements)}")
print(f"  icons: {len(icon_elements)}")
print(f"  charts: {len(chart_elements)}")
print(f"  tables: {len(table_elements)}")
