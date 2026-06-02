import json
import time

# Timestamp in milliseconds
NOW = int(time.time() * 1000)

# Global counters for unique IDs and zIndex
COUNTER = 0
ZIDX = 0

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX

# Helper functions
def make_text(slide_id, text, type_, x, y, w, h, color="#1c1917", font_size=None, font_weight=None, line_height=None):
    n = next_id()
    text_id = f"text-{n}"
    zidx = nextz()

    DEFAULTS = {
        "title": (60, 700, 1.05),
        "subtitle": (40, 600, 1.35),
        "heading": (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph": (22, 700, 1.50),
        "caption": (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None:
        fs = font_size
    if font_weight is not None:
        fw = font_weight
    if line_height is not None:
        lh = line_height

    content_record = {
        "id": text_id,
        "content": text,
        "type": type_,
        "originalType": type_,
        "groupId": None,
        "formattedContent": text
    }

    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w,
        "height": h,
        "rotation": 0,
        "zIndex": zidx,
        "style": {
            "fontSize": fs,
            "fontFamily": "Space Grotesk",
            "color": color,
            "textAlign": "left",
            "lineHeight": lh,
            "letterSpacing": 0,
            "fontWeight": fw,
            "fontStyle": "normal",
            "textDecoration": "none",
            "textTransform": "none",
            "isCode": False,
            "listStyle": "none",
            "link": "",
            "backgroundColor": "transparent",
            "background": "none",
            "WebkitBackgroundClip": "unset",
            "WebkitTextFillColor": "unset",
            "backgroundClip": "unset",
            "listLevel": 1,
            "paragraphSpacingBefore": 0,
            "paragraphSpacingAfter": 0,
            "textOutlineColor": "#000000",
            "textOutlineWidth": 0,
            "textTransformEffect": "none",
            "textTransformRadius": 220,
            "textVerticalAlign": "baseline",
            "curveEnabled": False,
            "curveValue": 26,
            "shadowType": "none",
            "shadowOffset": 22,
            "shadowDirection": -45,
            "shadowBlur": 0,
            "shadowTransparency": 40,
            "shadowColor": "#000000"
        },
        "formattedContent": text,
        "animation": {
            "enter": "none",
            "exit": "fade",
            "duration": 550,
            "delay": 0,
            "trigger": "both",
            "typewriterMode": "character"
        },
        "enterAnimation": "none",
        "exitAnimation": "fade",
        "animationEffect": "none",
        "animationDurationMs": 550,
        "animationDelayMs": 0,
        "animationTrigger": "both",
        "animationTypewriterMode": "character",
        "updatedAt": NOW
    }
    return text_id, content_record, changelog_record

def make_icon(slide_id, icon_name, x, y, size=80, color="#c67c3a", opacity=1):
    n = next_id()
    icon_id = f"icon-{n}"
    zidx = nextz()

    content_record = {
        "id": icon_id,
        "slideId": slide_id,
        "groupId": None,
        "iconName": icon_name,
        "iconSource": "lucide"
    }

    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": size,
        "height": size,
        "rotation": 0,
        "zIndex": zidx,
        "color": color,
        "opacity": opacity,
        "updatedAt": NOW
    }
    return icon_id, content_record, changelog_record

# Initialize structures
content_slides = []
content_text_by_slide = {}
content_icons = []
changelog_slides = {}

# Build each slide
for i in range(1, 11):
    slide_id = f"slide-{i}"
    content_slides.append({
        "id": slide_id,
        "order": i - 1,
        "layoutId": "blank-canvas",
        "backgroundColor": "#ffffff",
        "textElements": []
    })
    content_text_by_slide[slide_id] = []
    changelog_slides[slide_id] = {"elements": {}}

# Slide 1: Title Slide
slide_id = "slide-1"
t1, c1, cl1 = make_text(slide_id, "AI Trends 2026", "title", 48, 240, 1184, 100, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

t2, c2, cl2 = make_text(slide_id, "The Acceleration Era", "subtitle", 48, 380, 1184, 80, color="#c67c3a")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

# Slide 2: Multimodal AI
slide_id = "slide-2"
content_slides[1]["backgroundColor"] = "#f5f0e8"

t1, c1, cl1 = make_text(slide_id, "Multimodal AI", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Image", 100, 180, size=64, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

i2, ci2, cli2 = make_icon(slide_id, "Music", 340, 180, size=64, color="#c67c3a")
content_icons.append(ci2)
changelog_slides[slide_id]["elements"][i2] = cli2

i3, ci3, cli3 = make_icon(slide_id, "MessageCircle", 580, 180, size=64, color="#c67c3a")
content_icons.append(ci3)
changelog_slides[slide_id]["elements"][i3] = cli3

i4, ci4, cli4 = make_icon(slide_id, "Video", 820, 180, size=64, color="#c67c3a")
content_icons.append(ci4)
changelog_slides[slide_id]["elements"][i4] = cli4

t2, c2, cl2 = make_text(slide_id, "AI systems seamlessly process text, images, audio, and video in integrated workflows.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=24)
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "Real-time translation across formats | Context-aware processing | Unified model architectures", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

# Slide 3: Agentic Systems
slide_id = "slide-3"

t1, c1, cl1 = make_text(slide_id, "Agentic AI Systems", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Zap", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Autonomous Task Execution", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "AI agents plan, execute, and refine complex multi-step workflows without human intervention.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "End-to-end task automation | Dynamic decision-making | Error recovery & adaptation", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 4: Reasoning & Verification
slide_id = "slide-4"
content_slides[3]["backgroundColor"] = "#f5f0e8"

t1, c1, cl1 = make_text(slide_id, "Reasoning & Verification", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Brain", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Extended Thinking Becomes Standard", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "Models use chain-of-thought reasoning and self-verification to improve accuracy and trustworthiness.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "Transparent reasoning processes | Built-in output validation | Improved reliability in critical domains", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 5: Enterprise AI
slide_id = "slide-5"

t1, c1, cl1 = make_text(slide_id, "Enterprise AI Adoption", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Briefcase", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Mainstream Business Integration", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "AI moves from pilot projects to core business operations across finance, HR, customer service, and more.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "Productivity gains of 20-40% | Custom model fine-tuning | Seamless legacy system integration", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 6: AI Safety & Alignment
slide_id = "slide-6"
content_slides[5]["backgroundColor"] = "#e9defc"

t1, c1, cl1 = make_text(slide_id, "AI Safety & Alignment", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Lock", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Responsible AI Development", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "Guardrails, interpretability, and bias mitigation become non-negotiable in production systems.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "Constitutional AI principles | Explainability frameworks | Responsible deployment standards", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 7: Edge & Distributed AI
slide_id = "slide-7"

t1, c1, cl1 = make_text(slide_id, "Edge & Distributed AI", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Cpu", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Computing at the Edges", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "Smaller, efficient models run locally on devices, reducing latency and cloud dependency while improving privacy.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "Sub-second inference on mobile | Privacy-first processing | Reduced bandwidth requirements", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 8: Retrieval-Augmented Generation
slide_id = "slide-8"
content_slides[7]["backgroundColor"] = "#fff3c2"

t1, c1, cl1 = make_text(slide_id, "Retrieval-Augmented Generation", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "Search", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Knowledge-Grounded AI", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "RAG systems combine retrieval engines with generation, enabling accurate, fact-based responses from private data.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "Reduced hallucinations | Current information integration | Corporate knowledge leverage", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 9: AI Regulation & Ethics
slide_id = "slide-9"

t1, c1, cl1 = make_text(slide_id, "Regulation & Governance", "title", 48, 48, 1184, 80, color="#14204e")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

i1, ci1, cli1 = make_icon(slide_id, "FileText", 100, 180, size=80, color="#c67c3a")
content_icons.append(ci1)
changelog_slides[slide_id]["elements"][i1] = cli1

t2, c2, cl2 = make_text(slide_id, "Compliance Becomes Essential", "subheading", 220, 190, 1000, 60, color="#1c1917")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

t3, c3, cl3 = make_text(slide_id, "Global AI frameworks, including EU AI Act and similar regulations, create compliance requirements and standardized practices.", "paragraph", 48, 300, 1184, 120, color="#1c1917", font_size=22)
content_text_by_slide[slide_id].append(c3)
changelog_slides[slide_id]["elements"][t3] = cl3

t4, c4, cl4 = make_text(slide_id, "Risk assessment frameworks | Audit trails & transparency | Ethical AI guidelines", "paragraph", 48, 450, 1184, 100, color="#1c1917", font_size=18)
content_text_by_slide[slide_id].append(c4)
changelog_slides[slide_id]["elements"][t4] = cl4

# Slide 10: Future Outlook
slide_id = "slide-10"
content_slides[9]["backgroundColor"] = "#14204e"

t1, c1, cl1 = make_text(slide_id, "Looking Ahead to 2027", "title", 48, 200, 1184, 100, color="#ffffff")
content_text_by_slide[slide_id].append(c1)
changelog_slides[slide_id]["elements"][t1] = cl1

t2, c2, cl2 = make_text(slide_id, "AI will become even more integrated, reliable, and responsible—reshaping how we work and solve problems.", "subtitle", 48, 340, 1184, 120, color="#c67c3a")
content_text_by_slide[slide_id].append(c2)
changelog_slides[slide_id]["elements"][t2] = cl2

# Build content structure
for slide in content_slides:
    slide_id = slide["id"]
    slide["textElements"] = content_text_by_slide[slide_id]

content = {
    "slides": content_slides,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "tableElements": [],
    "iconElements": content_icons,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": []
}

# Build baseLayout
base_layout_slides = []
for slide in content_slides:
    base_layout_slides.append({
        "id": slide["id"],
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": []
    })

base_layout = {
    "version": "v1",
    "slides": base_layout_slides,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": []
}

# Build changelog
changelog = {
    "version": "2.0",
    "slides": changelog_slides
}

# Calculate element count
text_count = sum(len(slide["textElements"]) for slide in content_slides)
icon_count = len(content_icons)
element_count = text_count + icon_count

# Build envelope
envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"ai-trends-2026-{NOW}",
        "title": "AI Trends 2026: The Acceleration Era",
        "description": "A comprehensive look at the major AI trends shaping 2026 and beyond",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 10,
        "elementCount": element_count,
        "createdAt": "2026-06-02T00:00:00.000Z",
        "updatedAt": "2026-06-02T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None
    },
    "files": {
        "content": content,
        "baseLayout": base_layout,
        "changelog": changelog
    }
}

# Write to file
with open("ai_trends_2026.json", "w") as f:
    json.dump(envelope, f, indent=2)

print(f"[OK] Deck generated: ai_trends_2026.json")
print(f"[OK] Slides: {len(content_slides)}")
print(f"[OK] Total elements: {element_count}")
print(f"     - Text: {text_count}")
print(f"     - Icons: {icon_count}")
