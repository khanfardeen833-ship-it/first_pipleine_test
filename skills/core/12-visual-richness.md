# Skill 12 — Visual Richness & Data Integration

Every slide must combine **text + data visualization + background imagery**. This skill
ensures decks look premium and tell stories through visuals, not just words.

---

## HARD RULE — Images Are Not Optional

**You MUST call `slide.add_image(src=..., ...)` at least once every 2 slides.**
- Use real Pexels JPEG URLs (format: `https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg`)
- Add images as hero photos, side panels, or background half-bleed — NOT decorative filler
- Slides with ONLY shapes and icons are **rejected** — add a photo

**Minimum image quota: at least 1 `add_image()` call per deck batch.**

---

## Mandatory Visual Elements Per Slide

**RULE: Every slide must have AT LEAST ONE of these:**
1. Background image (using `slide.add_image()` with a Pexels URL)
2. Data visualization chart (bar, line, pie)
3. Large hero graphic or infographic
4. Grid of image cards or visual blocks

Text-only or icon-only slides are **forbidden**.

---

## Background Images (via Pexels)

Use high-quality Pexels images as slide backgrounds or visual anchors.

### Pattern 1: Full Bleed Image + Text Overlay

```python
# Add a full-width background image on the left
slide.add_image(
    src="https://images.pexels.com/photos/3182812/pexels-photo-3182812.jpeg",
    x=0, y=0, width=640, height=720,
    is_background=False,
    border_radius=0
)

# Add semi-transparent shape overlay for text readability
slide.add_shape(
    "rectangle",
    x=0, y=0, width=640, height=720,
    fill="#000000",
    opacity=0.3
)

# Text on top of image
slide.add_title(
    "Your Headline",
    x=32, y=300, width=576, height=200,
    color="#ffffff"
)
```

### Pattern 2: Image Card (Right Side Content)

```python
# Large image as visual anchor (right side)
slide.add_image(
    src="https://images.pexels.com/photos/3962286/pexels-photo-3962286.jpeg",
    x=672, y=48, width=560, height=360,
    border_radius=12
)

# Text content on left (x=48-560)
slide.add_title("AI Adoption Trends", x=48, y=48, width=560, height=80)
slide.add_text("Enterprise leaders prioritize...", x=48, y=150, width=560, height=200, type="paragraph")
```

### Pexels Query Examples:

```
# For corporate/business topics:
https://images.pexels.com/photos/3182812/pexels-photo-3182812.jpeg  (office/teamwork)
https://images.pexels.com/photos/3962286/pexels-photo-3962286.jpeg  (data/analytics)
https://images.pexels.com/photos/4195325/pexels-photo-4195325.jpeg  (technology/code)
https://images.pexels.com/photos/3775517/pexels-photo-3775517.jpeg  (business meeting)

# For finance/investor presentations:
https://images.pexels.com/photos/3184423/pexels-photo-3184423.jpeg  (financial charts)
https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg  (growth/upward)
https://images.pexels.com/photos/3532557/pexels-photo-3532557.jpeg  (innovation)
```

---

## Data Visualization Charts

Every slide with statistics **MUST have a chart**, not just bullet text.

### Pattern 1: Key Stat with Bar Chart

For slide showing: "Revenue increased 34% YoY in Q3"

```python
# Add the chart
slide.add_chart(
    "bar",
    chart_config={
        "title": "Revenue Growth by Quarter (2024)",
        "showTitle": True,
        "data": [
            {
                "name": "2023",
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "values": [2.1, 2.3, 2.5, 2.8]  # $B
            },
            {
                "name": "2024",
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "values": [2.5, 2.7, 3.0, 3.2]
            }
        ]
    },
    x=48, y=240, width=560, height=360
)

# Add interpretation text below
slide.add_text(
    "Q3 2024 showed 34% YoY growth, driven by enterprise expansion",
    x=672, y=240, width=560, height=100,
    type="paragraph"
)
```

### Pattern 2: Market Share Pie Chart

```python
slide.add_chart(
    "pie",
    chart_config={
        "title": "Market Share Distribution",
        "showTitle": True,
        "data": [
            {
                "name": "Market Share",
                "labels": ["Our Company", "Competitor A", "Competitor B", "Others"],
                "values": [32, 28, 25, 15]  # percentages
            }
        ]
    },
    x=48, y=240, width=560, height=360
)
```

### Pattern 3: Trend Line Chart

```python
slide.add_chart(
    "line",
    chart_config={
        "title": "AI Adoption Trend (2020-2025)",
        "showTitle": True,
        "data": [
            {
                "name": "Enterprise Adoption Rate (%)",
                "labels": ["2020", "2021", "2022", "2023", "2024", "2025E"],
                "values": [5, 12, 24, 41, 58, 72]
            }
        ]
    },
    x=48, y=240, width=560, height=360
)
```

### Pattern 4: Comparison Bar Chart

For: "Cloud spend vs On-premise spend"

```python
slide.add_chart(
    "bar",
    chart_config={
        "title": "Infrastructure Investment Allocation",
        "showTitle": True,
        "data": [
            {
                "name": "Cloud",
                "labels": ["2023", "2024", "2025E"],
                "values": [38, 52, 65]  # % of IT budget
            },
            {
                "name": "On-Premise",
                "labels": ["2023", "2024", "2025E"],
                "values": [62, 48, 35]
            }
        ]
    },
    x=48, y=240, width=560, height=360
)
```

---

## Visual Richness Checklist

For **every slide**, verify:

- [ ] Has at least one image OR chart (not optional)
- [ ] If stat-heavy: has corresponding chart (bar, line, or pie)
- [ ] If process/workflow: has visual diagram or numbered steps with icons
- [ ] If conceptual: has hero image or background
- [ ] Images have proper aspect ratios (not squished/stretched)
- [ ] Chart data has 3-6 data points per series (not too crowded)
- [ ] Text has breathing room around images (min 24px padding)
- [ ] Color contrast between text and background is strong

---

## Icon + Chart Combination Pattern

Pair small icon elements with data to create visual interest:

```python
# Chart on left
slide.add_chart("bar", {...}, x=48, y=100, width=560, height=400)

# Icon on right with key takeaway
slide.add_shape(
    "circle",
    x=700, y=120, width=80, height=80,
    fill="#c67c3a"  # accent color
)
slide.add_icon(
    "TrendingUp",
    x=715, y=135, size=48,
    color="#ffffff"
)

slide.add_text(
    "34% Growth",
    x=672, y=220, width=560, height=60,
    type="heading"
)
```

---

## Image Best Practices

1. **Size matters**: Use min 300×200px for visible detail
2. **Aspect ratio**: Prefer 16:9 or 4:3 (matches slide proportions)
3. **Border radius**: 8-16px for softer, premium look
4. **Overlays**: If text on image, add 0.2-0.4 opacity dark overlay
5. **Relevance**: Images must relate to slide topic, not decorative filler

---

## Common Patterns to AVOID

- Text-only bullet lists (must pair with icon, chart, or image)
- Tiny charts (min 560×360 for readability)
- Low-resolution or pixelated images
- Charts with 10+ data points (use summary instead)
- Images with no breathing room from text
- Misaligned elements (snap to 8px grid)

---

## Summary

**High-quality decks require:**
1. Strategic image placement (background or card)
2. Data visualization for every statistic
3. Consistent visual hierarchy
4. Professional polish (spacing, alignment, colors)

A premium deck tells stories through **visuals first, text second**.
