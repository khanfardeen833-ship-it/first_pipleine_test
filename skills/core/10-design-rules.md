# Skill 10 — Design Rules

## Canvas

- Size: **1280 × 720** pixels (16:9)
- Safe zone: **48px** on all sides — keep all text inside x: 48–1232, y: 48–672
- Snap all coordinates to **multiples of 8**

## Typography

Default font: **Trebuchet MS** — see 11-visual-design-guide.md for the full font pairing table. Only use fonts listed there (all are built-in Windows/PowerPoint fonts). Never use Space Grotesk, Inter, Roboto, or any Google font.
Default text color: **#1c1917** (near-black warm tone)

| Type        | Size | Weight | Use for                          |
|-------------|------|--------|----------------------------------|
| title       | 60   | 700    | Slide headline — the insight     |
| subtitle    | 40   | 600    | Supporting statement             |
| heading     | 32   | 600    | Section label or key stat        |
| subheading  | 26   | 600    | Supporting label                 |
| paragraph   | 22   | 700    | Body copy — keep under 3 lines   |
| caption     | 18   | 600    | Source, footnote, label          |

**Title rule:** The title should be the *insight*, not the topic.
- ✓ "Revenue grew 34% in Q3"
- ✗ "Q3 Revenue Overview"

## Color palette

Default palette (warm/navy):
```
#1c1917   near-black (text, dark backgrounds)
#ffffff   white
#c67c3a   warm amber (accent)
#f5f0e8   warm cream (light backgrounds)
#14204e   deep navy (alternative dark)
```

Palette rules:
- Use one primary accent color per deck
- Max 3 distinct colors per slide (background + text + accent)
- Dark slides: use `#1c1917` or `#14204e` as background, `#ffffff` for text
- Light slides: use `#ffffff` or `#f5f0e8` as background, `#1c1917` for text

## Layout principles

One focal idea per slide — if you need to say two things, use two slides.

**Comfortable text widths:**
- Full-width text block: x=48, width=1184
- Left column (two-column): x=48, width=560
- Right column (two-column): x=672, width=560
- Centered narrow: x=240, width=800

**Vertical rhythm (common starting y positions):**
- Hero title: y=240 (vertically centered on slide)
- Top section title: y=48
- Content below a title: title_y + title_height + 24

## Element sizing guidelines

| Element  | Typical size        |
|----------|---------------------|
| Icon     | 64×64 or 80×80      |
| Image    | min 300×200         |
| Chart    | 560×400             |
| Table    | colWidth 160–220px  |

## Background colors — pre-calculated safe pairs

```python
SLIDE_BACKGROUNDS = [
    "#ffffff",   # pure white
    "#f5f0e8",   # warm cream
    "#ffe9d6",   # soft peach
    "#e9defc",   # soft lavender
    "#c8f5e4",   # soft mint
    "#fff3c2",   # soft yellow
    "#ffe0eb",   # soft rose
    "#d6f1fb",   # soft sky
    "#1c1917",   # dark (use white text)
    "#14204e",   # navy (use white text)
]
```

For dark backgrounds (#1c1917, #14204e), set all text color to `#ffffff`.

## Table sizing

Max safe table width = 1184px (from x=48 to x=1232).

Common column width splits:
- 3 equal columns: `colWidths=[394, 394, 396]`
- 4 equal columns: `colWidths=[296, 296, 296, 296]`
- 5 equal columns: `colWidths=[236, 236, 236, 236, 240]`

Standard row height: `53px`. Header row can be `64px` for emphasis.
