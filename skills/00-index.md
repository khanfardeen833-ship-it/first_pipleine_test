# Skills Index

Read this file first on every run. Use it to decide which `elements/` skills you need.
Always read all files in `core/` before doing anything else — no exceptions.

---

## core/ — always read these first

**01-envelope.md** — The top-level JSON wrapper every deck must start with. Covers the three required files (`content`, `baseLayout`, `changelog`), their version strings (`"v1"` and `"2.0"`), and how `slideCount` and `elementCount` must be kept accurate. Read this before writing any deck structure.

**08-changelog-sync.md** — The most critical structural rule: every element has two records — a minimal content record and a full geometry record in the changelog. Covers the sync checklist, the slideId rule, and the builder pattern that keeps them in sync. Read this before creating any element.

**09-zindex-rules.md** — zIndex must be globally unique across the entire deck, not just per slide. Covers the counter pattern (`nextz()`), stacking order conventions, and how element IDs and zIndex values should match. Read this before creating any element.

**10-design-rules.md** — Canvas (1280×720), safe zone (48px), typography defaults, color palette, comfortable text widths, element sizing guidelines, background color options, and table column width formulas. Read this before positioning anything.

**11-visual-design-guide.md** — Creative direction: 10 color palettes to choose from, per-slide visual element rules, layout patterns (two-column, icon rows, card grid, half-bleed), data display patterns, typography pairings, and a hard avoid-list. Read this before designing any slide.

---

## elements/ — read only what your deck needs

**02-text-element.md** — Read this if your deck has any text. Covers the 6 text types (title, subtitle, heading, subheading, paragraph, caption), all 27 required style fields, and the split between content and changelog records. Almost every deck needs this.

**03-shape-element.md** — Read this if your deck uses rectangles, circles, lines, or other geometric shapes. Covers valid shape types, fill/stroke rules, and the 3-field content record. Use shapes for backgrounds, accent bars, overlays, and card containers.

**04-image-element.md** — Read this if your deck uses photos or images. Covers the Pexels URL format, required shadow/border/crop blocks that must always be present, and the `isBackground` flag for full-slide images.

**05-icon-element.md** — Read this if your deck uses icons. Covers Lucide icon names, sizing conventions, and color rules. Use icons for feature lists, benefit summaries, and visual emphasis.

**06-chart-element.md** — Read this if your deck uses charts. Covers bar, line, pie, doughnut, and nightingale chart types, the full `chartConfig` structure, and the `tableData` sync requirement. Also covers missing axis label options (`xAxis.axisLabel`, `yAxis.axisLabel`).

**07-table-element.md** — Read this if your deck uses data tables. Covers cell key format (`"row-col"`), `colWidths`, `rowHeights`, and the fact that tables carry position and zIndex in both content and changelog records. Note: tables do not appear in `baseLayout`.
