# Skill 12 — Visual Richness & Data Integration

Every slide must combine **text + data visualization + background imagery**. This skill
ensures decks look premium and tell stories through visuals, not just words.

---

## HARD RULE — Images Are Not Optional

**You MUST add at least one image every 2 slides.**
- Request photos with a **`query`** (2-5 literal subject words) — a real Pexels
  search supplies the URL. NEVER hand-write a `photos/{id}` URL: a guessed id
  returns a random, irrelevant photo (a dog, a cliff). See skill 04.
- Add images as hero photos, side panels, or background half-bleed — NOT decorative filler
- Slides with ONLY shapes and icons are **rejected** — add a photo

---

## Mandatory Visual Elements Per Slide

**RULE: Every slide must have AT LEAST ONE of these:**
1. Background or anchor image (an image element with a `query`)
2. Data visualization chart (bar, line, pie)
3. Large hero graphic or infographic
4. Grid of image cards or visual blocks

Text-only or icon-only slides are **forbidden**.

---

## Background Images (via Pexels search)

Use high-quality photos as slide backgrounds or visual anchors. Always describe
the subject with a `query`; the pipeline resolves it to a real, relevant image.

### Pattern 1: Full Bleed Image + Text Overlay

```python
# Full-height image on the left — query names the literal subject
slide.add_image(
    query="modern open-plan office team",
    x=0, y=0, width=640, height=720,
    border_radius=0
)
# Semi-transparent overlay for text readability
slide.add_shape("rectangle", x=0, y=0, width=640, height=720, fill="#000000", opacity=0.3)
slide.add_title("Your Headline", x=32, y=300, width=576, height=200, color="#ffffff")
```

### Pattern 2: Image Card (Right Side Content)

```python
slide.add_image(query="data analytics dashboard screen",
                x=672, y=48, width=560, height=360, border_radius=12)
slide.add_title("AI Adoption Trends", x=48, y=48, width=560, height=80)
slide.add_text("Enterprise leaders prioritize...", x=48, y=150, width=560, height=200, type="paragraph")
```

### Writing good queries

Name the **literal subject**, not the abstract theme:

| Topic | ✅ good query | ❌ bad query |
|-------|--------------|-------------|
| Investor pitch | `warehouse robots automation` | `success` |
| Coffee deck | `pour-over coffee close up` | `quality` |
| Bubble tea | `bubble tea pastel cups` | `fun drinks` |
| Finance | `stock market trading screen` | `growth` |

Match the orientation to the element: a tall side panel → portrait subject;
a wide hero → landscape subject (orientation is inferred from width/height).

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
