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

## No-overlap rules (hard — the #1 source of broken slides)

Every element is absolutely positioned; nothing reflows. Two element boxes must
**never overlap** unless the overlap is deliberate design (text on a full-bleed
background image, a "VS" badge sitting on a divider). Before you place an
element, compute its box `[x, y, x+width, y+height]` and check it against every
box already on the slide.

- **Kicker/eyebrow above title.** A small caption above a title (e.g. a section
  label like "DEMOCRATS") must sit *fully above* the title: `caption.y +
  caption.height + 8 ≤ title.y`. Never give the caption and the title the same
  `y` — that stacks them on top of each other.
- **Image + text in a column.** Body text must go **beside or below** its image,
  never on top of it. If the image is `128×128` at `x=88, y=272` (bottom 400),
  the paragraph starts at `y ≥ 408` (below) or `x ≥ image.x + image.width + 24`
  (beside) — its box must not intersect the image box. This does **not** apply to
  a full-bleed background image (`isBackground: true`), where text over the image
  is intended.
- **Titles stay in their column.** A title/heading in a two-column layout must
  not extend past the column divider into the other column. Full-width titles are
  fine only when the row below them is also full-width (no second-column content
  at the same `y`).
- **Minimum gaps between boxes:** ≥ 24px vertical between stacked text blocks,
  ≥ 16px around an icon/badge, ≥ 24px between a text box and an image. If content
  doesn't fit with these gaps, cut copy or split the slide — do not overlap.
- **Align two columns.** Left and right columns should share top anchors: the
  two headings at the same `y`, the two portraits at the same `y`, the two body
  paragraphs at the same `y`. Mismatched column baselines read as broken.

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
