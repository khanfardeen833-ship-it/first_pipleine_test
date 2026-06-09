# Visual Design Guide

Read this file along with 10-design-rules.md before designing any slide.
This guide covers creative direction — color philosophy, layout patterns, and
a required avoid-list. The technical constraints (canvas size, safe zones,
element sizing) are in 10-design-rules.md.

---

## Design Philosophy

**Pick a bold, topic-specific palette.** If you could swap your colors into a
completely different presentation and they'd still "work," the choices aren't
specific enough. Every deck should feel designed for its subject.

**Dominance over equality.** One color must carry 60–70% of the visual weight.
Support it with 1–2 complementary tones and one sharp accent. Never give all
colors equal weight — that produces visual mush.

**Sandwich structure.** Dark-background slides for the title and conclusion;
light-background slides for content. Or commit to dark throughout for a premium
feel. Do not mix arbitrarily.

**Commit to a visual motif.** Pick ONE distinctive element and repeat it on
every slide — rounded image frames, icons inside colored circles, a thick
left-edge accent bar. Consistency creates a designed look; variety creates noise.

---

## Color Palettes

Choose the palette that fits the topic. Do not default to the warm/navy palette
on every deck — match the mood and subject.

| Name | Primary | Secondary | Accent |
|------|---------|-----------|--------|
| Midnight Executive | `#1E2761` | `#CADCFC` | `#FFFFFF` |
| Forest & Moss | `#2C5F2D` | `#97BC62` | `#F5F5F5` |
| Coral Energy | `#F96167` | `#F9E795` | `#2F3C7E` |
| Warm Terracotta | `#B85042` | `#E7E8D1` | `#A7BEAE` |
| Ocean Gradient | `#065A82` | `#1C7293` | `#21295C` |
| Charcoal Minimal | `#36454F` | `#F2F2F2` | `#212121` |
| Teal Trust | `#028090` | `#00A896` | `#02C39A` |
| Berry & Cream | `#6D2E46` | `#A26769` | `#ECE2D0` |
| Sage Calm | `#84B59F` | `#69A297` | `#50808E` |
| Cherry Bold | `#990011` | `#FCF6F5` | `#2F3C7E` |

---

## Per-Slide Visual Element Rule

**Every slide must have at least one non-text element.**
Add a shape, image, icon, or chart to every slide without exception.
Text-only slides are never acceptable — a single accent shape still counts.

---

## Layout Patterns

Vary the layout across slides. Do not repeat the same pattern more than twice
in a row.

**Two-column** — text content left, visual right:
```
text:   x=64,  y=variable, w=560
visual: x=672, y=variable, w=544
```

**Icon + text rows** — icon in a colored circle, bold heading beside it, body below:
```
circle: x=64,  y=row_y, w=64, h=64  (add_shape ellipse, palette accent color)
icon:   x=64,  y=row_y, size=48     (centered inside circle)
heading: x=148, y=row_y+8, w=500
body:   x=148, y=row_y+52, w=500
```

**2×2 or 2×3 card grid** — full image on one half, content blocks on other:
```
image:   x=0, y=0, w=640, h=720, is_background=False
cards:   x=672, y=48, w=544  (split vertically for 2–3 rows)
```

**Half-bleed** — full-height shape or image covers one entire half:
```
background shape: x=0, y=0, w=640, h=720   (left bleed)
content: x=672, y=48  ...
```
or
```
background shape: x=640, y=0, w=640, h=720  (right bleed)
content: x=64, y=48  ...
```

---

## Data Display Patterns

**Large stat callouts** — one big number, label beneath:
```
number: font_size=72, font_weight=700, y=240
label:  font_size=18, font_weight=400, y=340
```

**Comparison columns** — before/after, pros/cons, option A vs B:
Three columns at x=64, x=464, x=864 (each w=320) or two at x=64, x=672.

**Timeline / process flow** — numbered steps connected by shapes:
Step circles at equal horizontal intervals; connector lines between them.

---

## Visual Polish

**Icons always inside circles.** When placing a Lucide icon for decoration,
add a small ellipse shape behind it first:
```python
slide.add_shape("ellipse", x=icon_x-8, y=icon_y-8,
                width=icon_size+16, height=icon_size+16,
                fill=accent_color)
slide.add_icon(name, x=icon_x, y=icon_y, size=icon_size, color="#ffffff")
```

**Italic accent text.** Use `style={"fontStyle": "italic"}` for key stats,
taglines, or pull-quotes. Use sparingly — one italic element per slide maximum.

---

## Typography Pairings

**Only use fonts from this list** — they are built into PowerPoint and Windows and will
render correctly in the final PPTX. Never use Space Grotesk, Inter, Roboto, or any
Google/web font — they are not available in PowerPoint and will silently fall back to
a generic system font.

The default font is `Trebuchet MS`. Change it to match the mood of the deck.

| Theme | Heading font | Body font | Best for |
|-------|-------------|-----------|---------|
| Modern / Clean (default) | `Trebuchet MS` | `Calibri Light` | Tech, startup, corporate |
| Editorial / Premium | `Georgia` | `Calibri` | Reports, strategy, finance |
| Bold / Impactful | `Arial Black` | `Arial` | Marketing, sales, sports |
| Geometric / Design | `Century Gothic` | `Calibri Light` | Creative, agency, luxury |
| Elegant / Luxury | `Palatino Linotype` | `Garamond` | Fashion, hospitality, high-end |
| Sharp / Executive | `Cambria` | `Calibri` | Legal, consulting, banking |
| Tech / Digital | `Segoe UI` | `Segoe UI Light` | SaaS, data, engineering |
| High Contrast | `Impact` | `Trebuchet MS` | Events, campaigns, bold CTAs |

**Rules:**
- Use the heading font for: title, subtitle, heading, subheading elements
- Use the body font for: paragraph, caption elements
- Be consistent — pick one pairing and use it on every slide
- Vary font SIZE and WEIGHT for hierarchy, not font family

---

## Spacing

- Minimum 48px margin from all slide edges (matches the safe zone in 10-design-rules.md)
- 29–48px gap between distinct content blocks
- Leave breathing room — do not fill every pixel

---

## Chart Data Patterns

Charts must include actual data series. Structure charts with this format:

**Bar Chart (side-by-side or stacked):**
```python
chart_config = {
    "title": "Revenue by Region",
    "showTitle": True,
    "data": [
        {
            "name": "2023",
            "labels": ["North", "South", "East", "West"],
            "values": [45, 52, 38, 61]
        },
        {
            "name": "2024",
            "labels": ["North", "South", "East", "West"],
            "values": [52, 61, 44, 73]
        }
    ]
}
```

**Line Chart (trends):**
```python
chart_config = {
    "title": "Market Growth Trend",
    "showTitle": True,
    "data": [
        {
            "name": "Ultra-luxury",
            "labels": ["2019", "2020", "2021", "2022", "2023", "2024"],
            "values": [100, 102, 108, 115, 124, 137]
        }
    ]
}
```

**Pie Chart (composition):**
```python
chart_config = {
    "title": "Market Share",
    "showTitle": True,
    "data": [
        {
            "name": "Composition",
            "labels": ["Primary", "Secondary", "Tertiary"],
            "values": [45, 35, 20]
        }
    ]
}
```

**Key rules:**
- `labels` and `values` arrays must be same length
- Use 3–6 data points per series (more gets crowded)
- Series names should be short (year, region, category)
- Prefer bar/line for comparisons; pie for part-to-whole; area for stacked trends
- Never pass empty data — always populate with real numbers

---

## Avoid List

These are hard rules, not suggestions.

- **Do not repeat the same layout** across consecutive slides — vary columns, cards, and callouts
- **Do not center body text** — left-align paragraphs and bullet lists; center only slide titles
- **Do not use accent lines or underlines under titles** — use whitespace or a background color change instead; underlines are a hallmark of AI-generated slides
- **Do not add full-width colored bars, header ribbons, or footer stripes** — decorative horizontal bands read as AI slop unless the user explicitly requested them
- **Do not default to cream/beige backgrounds** — use `#ffffff` or a palette color; never use `#F5F5DC`, `#FAF0E6`, `#FAEBD7`, or similar warm-neutral defaults
- **Do not make text-only slides** — every slide needs at least one shape, icon, image, or chart
- **Do not let text overflow its container** — if content is too long, reduce font size, split across two slides, or enlarge the text box; never leave text cut off
- **Do not use low-contrast elements** — all text and icons must have strong contrast against their background; avoid light gray text on off-white backgrounds or dark icons on dark shapes
- **Do not use the same palette as the previous deck** — if context suggests multiple decks are being made, actively vary the palette choice
