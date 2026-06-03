"""
Build helpers template for Phase 2 schema compression.

This module generates the _helpers.py file that gets pre-loaded into each
batch agent's working directory. The agent then writes only slide construction
code instead of redefining all helper functions from scratch.

Savings: ~195 lines of boilerplate x 3 batches = ~585 lines ~= 2,900 tokens (~13%)
"""

# Placeholders __NOW__ and __COUNTER_START__ are replaced by write_batch_helpers().
# Using __ prefix avoids conflicts with Python format() syntax.
_HELPERS_TEMPLATE = r'''import json, time, os

NOW = __NOW__
COUNTER = __COUNTER_START__


def nid():
    global COUNTER
    COUNTER += 1
    return COUNTER


def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx,
              color="#F8FAFC", font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk",
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
        "id": text_id, "content": text, "type": type_, "groupId": None
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
        "animationTypewriterMode": "character", "updatedAt": NOW
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx,
               fill="#2F80FF", stroke=None, stroke_width=0, opacity=1, rotation=0):
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
        "updatedAt": NOW
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx,
              size=64, color="#21D4FD", opacity=1):
    content_record = {
        "id": icon_id, "slideId": slide_id, "groupId": None,
        "iconName": icon_name, "iconSource": "lucide"
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": size, "height": size, "rotation": 0,
        "zIndex": zidx, "color": color, "opacity": opacity,
        "updatedAt": NOW
    }
    return content_record, changelog_record


def make_chart(chart_id, slide_id, chart_type, x, y, w, h, zidx, chart_config):
    content_record = {
        "id": chart_id, "slideId": slide_id, "groupId": None,
        "svgDataUrl": "", "chartType": chart_type,
        "chartConfig": chart_config
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "updatedAt": NOW,
        "chartType": chart_type
    }
    return content_record, changelog_record


def make_image(image_id, slide_id, image_url, x, y, w, h, zidx,
               opacity=1, rotation=0, border_radius=0):
    content_record = {
        "id": image_id, "slideId": slide_id, "groupId": None,
        "src": image_url, "alt": ""
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": rotation,
        "zIndex": zidx, "opacity": opacity,
        "borderRadius": border_radius,
        "updatedAt": NOW
    }
    return content_record, changelog_record


# Containers
slides_content = []
slides_baselayout = []
changelog_slides = {}

text_by_slide = {}
shape_elements = []
icon_elements = []
chart_elements = []
image_elements = []
table_elements = []


def init_slide(slide_id, order, bg="#000000"):
    slides_content.append({
        "id": slide_id, "order": order,
        "layoutId": "blank-canvas",
        "backgroundColor": bg,
        "textElements": []
    })
    slides_baselayout.append({
        "id": slide_id, "layoutId": "blank-canvas",
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    })
    changelog_slides[slide_id] = {"elements": {}}
    text_by_slide[slide_id] = []


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = nid()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = nid()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid


def add_icon(slide_id, icon_name, x, y, **kwargs):
    n = nid()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, icon_name, x, y, n, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


def add_chart(slide_id, chart_type, x, y, w, h, chart_config):
    n = nid()
    cid = f"chart-{n}"
    c, cl = make_chart(cid, slide_id, chart_type, x, y, w, h, n, chart_config)
    chart_elements.append(c)
    changelog_slides[slide_id]["elements"][cid] = cl
    return cid


def add_image(slide_id, image_url, x, y, w, h, **kwargs):
    n = nid()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, image_url, x, y, w, h, n, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


# ============================================================
# PHASE 3: Layout Macro Helpers
# Collapse common multi-kwarg patterns into shorter calls.
# Each saves 10-20 tokens vs the equivalent explicit add_text/add_shape.
# ============================================================

def add_mono(slide_id, text, type_, x, y, w, h, color,
             size=12, weight=600, spacing=0, align="left",
             transform="none", style="normal"):
    """JetBrains Mono text shorthand — replaces font_family kwarg (saves ~4 tokens)."""
    return add_text(slide_id, text, type_, x, y, w, h,
                    color=color, font_size=size, font_weight=weight,
                    font_family="JetBrains Mono", letter_spacing=spacing,
                    text_align=align, text_transform=transform, font_style=style)


def add_eyebrow(slide_id, text, color, x=80, y=48, w=600, h=20, size=11, spacing=2):
    """
    Standard slide eyebrow/chapter caption.
    Preset: JetBrains Mono, uppercase, letter_spacing=2, caption type.
    Saves ~18 tokens vs explicit add_text.
    """
    return add_text(slide_id, text, "caption", x, y, w, h,
                    color=color, font_size=size, font_family="JetBrains Mono",
                    letter_spacing=spacing, text_transform="uppercase")


def add_page_num(slide_id, num, color, x=1180, y=670, w=60, h=24, size=14):
    """
    Bottom-right page number.
    Preset: JetBrains Mono, right-aligned, bold, caption type.
    Saves ~14 tokens vs explicit add_text.
    """
    return add_text(slide_id, str(num), "caption", x, y, w, h,
                    color=color, font_size=size, font_family="JetBrains Mono",
                    font_weight=700, text_align="right")


def add_bg(slide_id, fill, opacity=1):
    """Full-canvas background rectangle (1280x720). Saves ~6 tokens."""
    return add_shape(slide_id, "rectangle", 0, 0, 1280, 720, fill=fill, opacity=opacity)


def add_band(slide_id, y, h, fill, opacity=1):
    """Full-width horizontal background band. Saves ~4 tokens."""
    return add_shape(slide_id, "rectangle", 0, y, 1280, h, fill=fill, opacity=opacity)


def add_rule(slide_id, y, color, opacity=0.3, x=80, w=1120, thickness=1):
    """Thin horizontal divider line. Saves ~6 tokens."""
    return add_shape(slide_id, "rectangle", x, y, w, thickness, fill=color, opacity=opacity)


def add_slide_header(slide_id, eyebrow, page_num, eyebrow_color, num_color,
                     eyebrow_x=80, eyebrow_y=48, rule=False, rule_color=None):
    """
    Combined eyebrow + page number (+ optional rule).
    Replaces 2-3 separate calls. Saves ~25 tokens per slide.
    """
    add_eyebrow(slide_id, eyebrow, eyebrow_color, x=eyebrow_x, y=eyebrow_y)
    add_page_num(slide_id, page_num, num_color)
    if rule:
        add_rule(slide_id, eyebrow_y + 32, rule_color or eyebrow_color, opacity=0.25)


def save_deck(title="Presentation"):
    """Assemble and write deck.json. Call once after all slides are built."""
    for s in slides_content:
        s["textElements"] = text_by_slide[s["id"]]

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
    baselayout_file = {
        "version": "v1",
        "slides": slides_baselayout,
        "imageElements": [], "shapeElements": [], "chartElements": [],
        "iconElements": [], "embedElements": []
    }
    changelog_file = {"version": "2.0", "slides": changelog_slides}

    total_text = sum(len(text_by_slide[sid]) for sid in text_by_slide)
    total_elements = (
        total_text + len(image_elements) + len(shape_elements)
        + len(chart_elements) + len(table_elements) + len(icon_elements)
    )
    slide_count = len(slides_content)

    envelope = {
        "exportedAt": NOW,
        "presentation": {
            "_id": f"deck-{NOW}",
            "title": title,
            "description": "",
            "thumbnailUrl": None,
            "isPublic": False,
            "slideCount": slide_count,
            "elementCount": total_elements,
            "createdAt": "2026-01-01T00:00:00.000Z",
            "updatedAt": "2026-01-01T00:00:00.000Z",
            "s3Key": None,
            "s3Url": None
        },
        "files": {
            "content": content_file,
            "baseLayout": baselayout_file,
            "changelog": changelog_file
        }
    }

    out_path = "deck.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2)

    print(f"Wrote {out_path}")
    print(f"Slides: {slide_count}")
    print(f"Total elements: {total_elements}")
    print(f"  text: {total_text}")
    print(f"  shapes: {len(shape_elements)}")
    print(f"  icons: {len(icon_elements)}")
    print(f"  charts: {len(chart_elements)}")
    print(f"  images: {len(image_elements)}")
    print(f"  tables: {len(table_elements)}")
'''


def write_batch_helpers(batch_dir, counter_start: int = 0, now_ts: int = None) -> None:
    """
    Write a pre-parameterized _helpers.py to the batch directory.

    Args:
        batch_dir: Path to the batch working directory
        counter_start: ID counter offset for this batch (0, 300, 600, etc.)
        now_ts: Unix timestamp in milliseconds (uses current time if None)
    """
    import time
    from pathlib import Path

    if now_ts is None:
        now_ts = int(time.time() * 1000)

    helpers_content = (
        _HELPERS_TEMPLATE
        .replace("__NOW__", str(now_ts))
        .replace("__COUNTER_START__", str(counter_start))
    )

    helpers_path = Path(batch_dir) / "_helpers.py"
    helpers_path.write_text(helpers_content, encoding="utf-8")
