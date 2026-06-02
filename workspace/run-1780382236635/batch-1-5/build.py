#!/usr/bin/env python3
"""
Bildory Presentation Generator: AI Trends in 2026 (Slides 1-5)
Generates a complete presentation JSON structure following all schema rules.
"""

import json
import time
from uuid import uuid4

# ============================================================================
# CONSTANTS & HELPERS
# ============================================================================

NOW = int(time.time() * 1000)
ZIDX = 0
ELEMENT_ID = 0

def nextz():
    """Get the next globally unique zIndex value."""
    global ZIDX
    ZIDX += 1
    return ZIDX

def next_id():
    """Get the next element ID number."""
    global ELEMENT_ID
    ELEMENT_ID += 1
    return ELEMENT_ID

# ============================================================================
# BUILDER FUNCTIONS - Text, Shape, Icon, etc.
# ============================================================================

def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx,
              color="#1c1917", font_size=None, font_weight=None, line_height=None):
    """Build both content and changelog records for a text element."""
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
            "textAlign": "left", "lineHeight": lh, "letterSpacing": 0,
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
        "animationTypewriterMode": "character", "updatedAt": NOW
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx,
               fill="#c67c3a", stroke=None, stroke_width=0, opacity=1):
    """Build both content and changelog records for a shape element."""
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
        "updatedAt": NOW
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx,
              size=80, color="#c67c3a", opacity=1):
    """Build both content and changelog records for an icon element."""
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


# ============================================================================
# SLIDE BUILDERS
# ============================================================================

def build_slide_1(text_elements_by_slide, changelog_slides, content_shapes, content_icons):
    """Slide 1: Title Slide"""
    slide_id = "slide-1"

    # Background shape
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 0, 0, 1280, 720, nextz(),
                       fill="#1c1917", stroke="#1c1917")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Title
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "AI Trends in 2026", "title", 48, 240, 1184, 80, nextz(),
                      color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Subtitle
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "The Year of Agentic Intelligence", "subtitle", 48, 360, 1184, 60, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Small tagline
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "How AI is transforming business in 2026", "caption", 48, 450, 1184, 40, nextz(),
                      color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


def build_slide_2(text_elements_by_slide, changelog_slides, content_shapes, content_icons):
    """Slide 2: Agentic AI Revolution"""
    slide_id = "slide-2"

    # Background
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 0, 0, 1280, 720, nextz(),
                       fill="#ffffff", stroke="#ffffff")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Accent bar
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 0, 0, 8, 720, nextz(),
                       fill="#c67c3a", stroke="#c67c3a")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Title
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Agentic AI is Becoming Reality", "title", 48, 48, 1184, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Content bullets as text
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "• AI systems that autonomously plan, execute, and refine their own work",
                      "paragraph", 80, 160, 1104, 60, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "• Multi-step reasoning replacing single-prompt responses",
                      "paragraph", 80, 240, 1104, 60, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "• From assistants to autonomous agents handling complex workflows",
                      "paragraph", 80, 320, 1104, 60, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Icon
    iid = f"icon-{next_id()}"
    c, cl = make_icon(iid, slide_id, "Zap", 80, 420, nextz(), size=96, color="#c67c3a")
    content_icons.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Expected to drive 40% productivity gains in knowledge work",
                      "paragraph", 200, 445, 984, 50, nextz(), color="#c67c3a", font_weight=700)
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


def build_slide_3(text_elements_by_slide, changelog_slides, content_shapes, content_icons):
    """Slide 3: Multimodal Intelligence"""
    slide_id = "slide-3"

    # Background
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 0, 0, 1280, 720, nextz(),
                       fill="#f5f0e8", stroke="#f5f0e8")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Title
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Multimodal Intelligence Takes Center Stage", "title", 48, 48, 1184, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Three columns with icons
    # Column 1
    iid = f"icon-{next_id()}"
    c, cl = make_icon(iid, slide_id, "FileText", 80, 160, nextz(), size=64, color="#c67c3a")
    content_icons.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Text Understanding", "subheading", 48, 240, 344, 50, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Parse documents, understand context, generate insights",
                      "caption", 48, 300, 344, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Column 2
    iid = f"icon-{next_id()}"
    c, cl = make_icon(iid, slide_id, "Image", 468, 160, nextz(), size=64, color="#ca8746")
    content_icons.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Image & Video Analysis", "subheading", 436, 240, 344, 50, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Detect objects, read charts, understand scenes in video",
                      "caption", 436, 300, 344, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Column 3
    iid = f"icon-{next_id()}"
    c, cl = make_icon(iid, slide_id, "Music", 856, 160, nextz(), size=64, color="#cd9352")
    content_icons.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Audio & Voice AI", "subheading", 824, 240, 344, 50, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Speech recognition, audio generation, sound understanding",
                      "caption", 824, 300, 344, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Bottom insight
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "2026 reality: AI understands and reasons across all data types simultaneously",
                      "paragraph", 48, 570, 1184, 70, nextz(), color="#14204e")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


def build_slide_4(text_elements_by_slide, changelog_slides, content_shapes, content_icons):
    """Slide 4: Enterprise Adoption Boom"""
    slide_id = "slide-4"

    # Background
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 0, 0, 1280, 720, nextz(),
                       fill="#14204e", stroke="#14204e")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Title
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "AI Goes Mainstream in Business", "title", 48, 48, 1184, 80, nextz(),
                      color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Three key stats
    # Stat 1
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "87%", "heading", 80, 160, 280, 60, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "of enterprises now have AI projects in production",
                      "caption", 80, 240, 280, 80, nextz(), color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Stat 2
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "5.2x", "heading", 500, 160, 280, 60, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "faster time to completion for routine tasks",
                      "caption", 500, 240, 280, 80, nextz(), color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Stat 3
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "$1.2T", "heading", 920, 160, 280, 60, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "estimated global AI enterprise market value",
                      "caption", 920, 240, 280, 80, nextz(), color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Integration points
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Integration into CRM, ERP, productivity tools, and custom workflows",
                      "paragraph", 48, 420, 1184, 60, nextz(), color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Moving from pilot phase → scaled adoption across departments",
                      "paragraph", 48, 510, 1184, 60, nextz(), color="#ffffff")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


def build_slide_5(text_elements_by_slide, changelog_slides, content_shapes, content_icons):
    """Slide 5: Open Source Dominance"""
    slide_id = "slide-5"

    # Background
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 0, 0, 1280, 720, nextz(),
                       fill="#ffffff", stroke="#ffffff")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Accent shape on right
    sid = f"shape-{next_id()}"
    c, cl = make_shape(sid, slide_id, "rectangle", 1000, 0, 280, 720, nextz(),
                       fill="#ffe9d6", stroke="#ffe9d6")
    content_shapes.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl

    # Title
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Open Source Models Challenge Incumbents", "title", 48, 48, 952, 100, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    # Key points
    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Democratization of AI", "subheading", 48, 180, 900, 40, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Models like Llama, Mistral, and others achieve parity with commercial APIs at a fraction of the cost",
                      "paragraph", 48, 230, 900, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Cost Reduction", "subheading", 48, 340, 900, 40, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "On-premise and edge deployment options eliminate API dependency and reduce operational costs",
                      "paragraph", 48, 390, 900, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Competitive Pressure", "subheading", 48, 500, 900, 40, nextz(),
                      color="#c67c3a")
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl

    tid = f"text-{next_id()}"
    c, cl = make_text(tid, slide_id, "Closed API providers must now justify premium pricing with clearly superior performance",
                      "paragraph", 48, 550, 900, 80, nextz())
    text_elements_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl


# ============================================================================
# MAIN BUILD
# ============================================================================

def main():
    # Initialize structures
    text_elements_by_slide = {f"slide-{i}": [] for i in range(1, 6)}
    changelog_slides = {f"slide-{i}": {"elements": {}} for i in range(1, 6)}
    content_slides = []
    content_shapes = []
    content_icons = []

    # Build each slide
    print("Building slide 1 (Title)...")
    build_slide_1(text_elements_by_slide, changelog_slides, content_shapes, content_icons)

    print("Building slide 2 (Agentic AI)...")
    build_slide_2(text_elements_by_slide, changelog_slides, content_shapes, content_icons)

    print("Building slide 3 (Multimodal)...")
    build_slide_3(text_elements_by_slide, changelog_slides, content_shapes, content_icons)

    print("Building slide 4 (Enterprise)...")
    build_slide_4(text_elements_by_slide, changelog_slides, content_shapes, content_icons)

    print("Building slide 5 (Open Source)...")
    build_slide_5(text_elements_by_slide, changelog_slides, content_shapes, content_icons)

    # Assemble content.slides with text elements
    for i in range(1, 6):
        slide_id = f"slide-1" if i == 1 else f"slide-{i}"
        slide_id = f"slide-{i}"
        bg_color = "#1c1917" if i == 1 else "#ffffff" if i in [2, 5] else ("#f5f0e8" if i == 3 else "#14204e")
        content_slides.append({
            "id": slide_id,
            "order": i - 1,
            "layoutId": "blank-canvas",
            "backgroundColor": bg_color,
            "textElements": text_elements_by_slide[slide_id]
        })

    # Count total elements
    total_text = sum(len(text_elements_by_slide[f"slide-{i}"]) for i in range(1, 6))
    total_shapes = len(content_shapes)
    total_icons = len(content_icons)
    total_elements = total_text + total_shapes + total_icons

    # Build files object
    files = {
        "content": {
            "slides": content_slides,
            "imageElements": [],
            "shapeElements": content_shapes,
            "chartElements": [],
            "tableElements": [],
            "iconElements": content_icons,
            "embedElements": [],
            "smartDiagramElements": [],
            "groupElements": []
        },
        "baseLayout": {
            "version": "v1",
            "slides": [
                {
                    "id": f"slide-{i}",
                    "layoutId": "blank-canvas",
                    "imageElements": [],
                    "shapeElements": [],
                    "chartElements": [],
                    "iconElements": [],
                    "embedElements": []
                }
                for i in range(1, 6)
            ],
            "imageElements": [],
            "shapeElements": [],
            "chartElements": [],
            "iconElements": [],
            "embedElements": []
        },
        "changelog": {
            "version": "2.0",
            "slides": changelog_slides
        }
    }

    # Build presentation envelope
    presentation = {
        "exportedAt": NOW,
        "presentation": {
            "_id": f"ai-trends-2026-{NOW}",
            "title": "AI Trends in 2026",
            "description": "A comprehensive overview of the major AI trends reshaping business and technology in 2026.",
            "thumbnailUrl": None,
            "isPublic": False,
            "slideCount": 5,
            "elementCount": total_elements,
            "createdAt": "2026-01-01T00:00:00.000Z",
            "updatedAt": "2026-01-01T00:00:00.000Z",
            "s3Key": None,
            "s3Url": None
        },
        "files": files
    }

    # Write to file
    output_file = "ai-trends-2026.json"
    with open(output_file, "w") as f:
        json.dump(presentation, f, indent=2)

    print(f"\n[OK] Presentation generated: {output_file}")
    print(f"  Slides: 5 (batch 1 of 2)")
    print(f"  Elements: {total_elements}")
    print(f"    - Text: {total_text}")
    print(f"    - Shapes: {total_shapes}")
    print(f"    - Icons: {total_icons}")
    print(f"  zIndex range: 1-{ZIDX}")


if __name__ == "__main__":
    main()
