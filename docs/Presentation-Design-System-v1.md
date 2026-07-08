# Presentation Design System v1

> The visual design language for our AI Presentation Engine. Every future
> layout, archetype, and slide is built from the tokens, components, and
> principles defined here. This is **not** a layout or an archetype — it is the
> vocabulary they compose from.
>
> Canvas of record: **1280 × 720** (16:9). Safe zone x ∈ [48, 1232], y ∈ [48, 672].
> Spacing base unit: **8px**. All sizes below are in the engine's px/pt units.

---

## 0. What we learned from the references (why they look premium)

Five premium references were studied (not copied). Two visual families emerged —
**Corporate Gradient** (AI cover, agenda, cards, comparison) and **Bold Neon
Editorial** (the black "Design Studio" cover). Across both, the same premium
mechanics recur:

1. **A small, reused component vocabulary** (number badge · icon circle · pill
   label · card · two-tone title) applied across every slide type. Cohesion —
   not per-slide novelty — is the #1 premium signal.
2. **One focal highlight per slide** (a gradient wordmark, a featured card, a
   hero image, or a dark panel). Everything else is deliberately quieter.
3. **Two-tone titles** — a base phrase in ink + one accent word — always paired
   with a muted subheading line.
4. **Restrained gradient accents** — 3–4 hues max, or a single neon. Gradients
   are *events*, not wallpaper.
5. **Whitespace and alignment discipline** — strong margins, shared baselines,
   connector rails, equal card widths.
6. **Confident imagery** — subjects bleed off an edge or sit as bold blocks;
   never a timid centered thumbnail.
7. **High figure–ground contrast** — dark panel on light, or neon on black.

**Why it works:** premium reads as *intentional*. A repeated system tells the eye
"this was designed as one thing." A single focal point removes competition for
attention. Restraint (few colors, much whitespace) signals confidence. These are
the invariants the system below encodes.

---

## 1. Typography System

**Principle:** hierarchy is created by **size + weight + color + spacing**, not by
adding typefaces. Use at most **two families per deck** — a *Display* face
(headlines) and a *Text* face (body). A deck may set Display = Text for a mono-family
minimal look.

Type scale (modular, ~1.25 ratio, tuned to the 1280×720 stage):

| Role | Size | Weight | Leading | Tracking | Case | Color role | Usage |
|---|---|---|---|---|---|---|---|
| **Hero Title** | 72–120 | 800–900 | 0.95–1.05 | tight (−1 to −2%) | UPPER or title | ink / gradient | Cover & closing only. The loudest thing in the deck. |
| **Slide Title** | 40–56 | 700 | 1.05–1.15 | 0 | title | ink (+1 accent word) | Every content slide's headline. |
| **Subtitle** | 20–28 | 500–600 | 1.3 | 0 | sentence | muted | One supporting line under the title. |
| **Section Label** (kicker/eyebrow) | 13–16 | 600–700 | 1.2 | **+8 to +12%** | UPPER | accent or muted | Category/eyebrow above a title; pill labels. |
| **KPI Number** | 56–120 | 700–800 | 1.0 | tabular, −1% | numerals | accent or ink | The hero figure on stats slides. Always oversized. |
| **Card Heading** | 18–24 | 600–700 | 1.2 | 0 | title or UPPER | ink / on-accent | Title inside a card/panel. |
| **Body Text** | 15–18 | 400–500 | 1.45–1.55 | 0 | sentence | ink | Paragraphs, descriptions. Max ~2–3 lines per block. |
| **Caption** | 13–15 | 500 | 1.3 | 0 | sentence | muted | Supporting notes under cards, stat labels. |
| **Footnote** | 11–12 | 400 | 1.3 | 0 | sentence | muted | Sources, page numbers, legal. |

**Visual hierarchy rules:**
- **One dominant type element per slide.** Hero Title or KPI Number, never both large.
- Adjacent levels must differ by **≥1.5× size or a full weight step** — no ambiguous "is this a heading or body?" moments.
- **Two-tone title pattern (signature):** Slide Title in `ink`; the final word/phrase in `accent` (or a gradient on covers). This is the cheapest, most reliable hierarchy device in the system — use it on nearly every title.
- Body blocks are **short** (2–3 lines). Long prose is a layout failure, not a type problem.
- Letterspacing is applied **only** to Section Labels/kickers (uppercase). Never letterspace body or large display.
- Numerals in KPIs and tables use **tabular/lining** figures so columns align.

---

## 2. Color System (semantic, not fixed)

Colors are **roles**, filled per-deck by a chosen palette (the engine's palette
picker maps a named palette → these tokens). Never hardcode hex in layouts;
reference the role.

| Token | Meaning | Typical use |
|---|---|---|
| `background` | The slide field | Full-canvas base (light or dark) |
| `surface` | Card/panel fill, one step off background | Cards, panels, chart plots |
| `surface-alt` | Secondary surface tint | Zebra rows, alternating cards |
| `ink` (primary-text) | Highest-contrast text | Titles, body on light |
| `muted` (secondary-text) | Lowered-emphasis text | Subtitles, captions, footnotes |
| `primary` | The deck's core brand hue | Key fills, primary buttons/badges |
| `secondary` | Supporting hue | Secondary badges, second data series |
| `accent` | The attention color | The one focal highlight, active states |
| `accent-cycle` | Ordered set of 3–4 hues | Number badges, multi-item color rotation |
| `gradient-accent` | 2–3 stop gradient | Hero wordmark, featured card, pills, blobs |
| `positive` | Up/good | ▲ deltas, gains, "winner" chips |
| `negative` | Down/bad | ▼ deltas, losses, risk flags |
| `warning` | Caution | Alerts, thresholds |
| `border` / `hairline` | 1–2px separators | Dividers, card strokes, rails |
| `scrim` | Dark/È light overlay | Text-over-image readability |

**Gradient rules — gradients are allowed ONLY on:**
- the Hero Title wordmark (cover/closing),
- number badges, icon-circle fills, and pill labels,
- exactly **one** featured card per slide,
- large low-opacity decorative blobs (≤15% opacity) behind content.

**Gradients are NEVER used on:**
- body text, captions, or any small text,
- large fills sitting **behind dense text** (kills legibility),
- more than **one** competing gradient per slide (a second gradient must be far
  quieter or a repeat of the same stops),
- data marks where a solid categorical color is needed for accuracy.

**Contrast & balance:**
- Text contrast meets **AA**: ≥4.5:1 for body, ≥3:1 for large/display.
- **60 / 30 / 10 rule:** ~60% background, ~30% surface/neutral, **≤10% accent**.
  Accent is precious; if everything is accent, nothing is.
- Every slide needs **one high-contrast anchor** (dark panel on light, accent on
  neutral, or neon on black).
- Positive/negative are **reserved** for real up/down semantics — never decorative.

---

## 3. Grid System

- **Outer margin:** 64px preferred (48px hard minimum = safe zone). Content never
  touches the edge except intentional image/shape bleeds.
- **Columns:** 12-column grid, **24px gutters**. Usable width 1152 (at 64px margin).
- **Common splits:** 60/40 and 55/45 (hero + list/image), 50/50 (comparison),
  4-up equal columns (cards), 70/30 (hero chart).
- **Vertical bands:** Title band y ≈ 48–170 (kicker + title + subtitle). Content
  band y ≈ 200–660. Footer band y ≈ 672.
- **Spacing rhythm (8px base):** allowed steps 4, 8, 16, 24, 32, 48, 64. Every gap
  is a multiple. This single rule removes "random spacing" instantly.
- **Card spacing:** inter-card gap 24px; internal padding ≥28px; equal cards share
  identical width, height, and top padding.
- **Image spacing:** ≥32px between an image edge and adjacent text (48px preferred).
  Bleeding images may exceed the safe zone on the bleed side only.
- **Alignment:** everything hangs on the grid — shared left edge for stacked text,
  shared baselines across sibling cards, badges on a common rail.

**Whitespace philosophy:** whitespace is the primary luxury signal. It is *active*,
not leftover. Each slide has **one dominant negative-space zone** (usually the left
margin or the area around the hero). Density communicates "cheap/busy"; air
communicates "premium/considered." When in doubt, remove an element and enlarge the
gaps — never fill a corner just because it's empty.

---

## 4. Component Library

The reusable building blocks. Every layout is assembled from these; no layout
invents a new primitive without adding it here first. Each component: **Purpose ·
Hierarchy · Placement · Size · Padding · Variations · Use / Don't · Relationships.**

### 4.1 Title Block
- **Purpose:** the slide's headline unit. **Hierarchy:** highest on content slides.
- **Placement:** top band, left-aligned (centered only in "monolith" modes).
- **Size/Padding:** kicker (Section Label) + Slide Title + Subtitle stacked; 8–16px between lines; ~24px accent rule optional below.
- **Variations:** two-tone title (default) · gradient wordmark (cover) · centered (luxury) · with eyebrow pill.
- **Use:** every slide. **Don't:** never two title blocks; never omit the subtitle slot on content slides.
- **Relationships:** anchors the grid; kicker often echoes a Section Ribbon color.

### 4.2 Number Badge
- **Purpose:** ordinal marker (01–0N) tying list/card items together. **Hierarchy:** secondary, but the deck's connective tissue.
- **Placement:** leading each row/card, on a connector rail or overlapping an icon circle.
- **Size:** 40–56px circle. **Padding:** numeral optically centered.
- **Variations:** gradient fill (default) · outlined · solid accent · cycles through `accent-cycle`.
- **Use:** agendas, process, comparison rows, feature cards. **Don't:** don't mix badge styles within one slide; don't exceed ~6 (cognitive load).
- **Relationships:** pairs with Icon Circle and Connector Line; color cycles with `accent-cycle`.

### 4.3 Icon Circle
- **Purpose:** a soft-tinted disc holding a single line icon; humanizes cards. **Hierarchy:** supporting.
- **Placement:** top of a card, or leading a row. **Size:** 56–72px disc, icon ~50% of disc.
- **Padding:** icon centered with ≥25% breathing room.
- **Variations:** soft tint (default) · solid accent · gradient (featured only) · with overlapping Number Badge.
- **Use:** feature cards, stat cards, agendas. **Don't:** more than one icon per card; multi-color icons; decorative-only icons that add no meaning.
- **Relationships:** commonly hosts a Number Badge; one accent family per deck.

### 4.4 Pill Label
- **Purpose:** a rounded-full tag for sections, categories, or eyebrows. **Hierarchy:** low but eye-catching.
- **Placement:** above a title, atop a comparison panel, or as a cover tag row.
- **Size:** height ~32–44px, horizontal padding 16–24px; Section Label type inside.
- **Variations:** gradient fill · solid · outlined · with leading icon (↗).
- **Use:** section headers, comparison labels, cover tags. **Don't:** long text (keep 1–3 words); stacking many pills into clutter.
- **Relationships:** color aligns with the panel/section it labels; echoes Section Ribbon.

### 4.5 Metric Card (KPI)
- **Purpose:** one number + label + optional delta/context. **Hierarchy:** the KPI Number dominates within it.
- **Placement:** in equal grids (4-up, 2×2) or a hero+satellites arrangement.
- **Size:** grid card ~278×300 (4-up) or 580×236 (2×2). **Padding:** ≥28px.
- **Variations:** default · with sparkline · with delta chip · featured (gradient).
- **Use:** statistics/dashboard content. **Don't:** cram >6 metrics; bury the number in a sentence.
- **Relationships:** hosts Icon Circle + delta (positive/negative); may embed a Chart Container (sparkline).

### 4.6 Hero Image
- **Purpose:** the dominant visual, usually a bleeding subject. **Hierarchy:** can be the focal highlight.
- **Placement:** one side (40–55%) or full-bleed background. **Size:** large; bleeds off ≥1 edge.
- **Padding:** none on the bleed side; ≥32px from text on the content side.
- **Variations:** side subject (blended) · full-bleed background · tilted block (editorial).
- **Use:** covers, section dividers, image-heavy slides. **Don't:** small centered thumbnail; text on it without a scrim.
- **Relationships:** requires a Gradient/Dark Overlay when text overlaps; may pair with a floating Metric Card.

### 4.7 Divider
- **Purpose:** separate content or mark rhythm. **Hierarchy:** minimal.
- **Placement:** under titles (short accent rule), between rows (hairline), between columns (vertical rule).
- **Size:** 2–4px accent rule ~64–120px long; 1px hairlines full-width.
- **Variations:** accent rule · hairline · vertical column divider · dotted connector.
- **Use:** everywhere sparingly. **Don't:** box everything in lines; heavy borders.
- **Relationships:** the accent rule under a title echoes the two-tone accent word.

### 4.8 Quote Block
- **Purpose:** a featured statement + attribution. **Hierarchy:** the quote is the focal element.
- **Placement:** centered-left on a layered panel, or beside a portrait.
- **Size:** quote 30–48pt; attribution Caption with accent rule + initial badge.
- **Variations:** editorial (oversized quote-mark glyph) · centered statement · portrait quote.
- **Use:** testimonials, thesis slides. **Don't:** multiple quotes; quote longer than ~2 lines at large size.
- **Relationships:** may use a Ghost quotation-mark (Decorative), a portrait Image Card, proof chips.

### 4.9 Image Card
- **Purpose:** a framed/rounded photo used as a content block (not full-bleed). **Hierarchy:** supporting-to-focal.
- **Placement:** paired with text; in galleries; overlapping panels.
- **Size:** varies; **corner radius** matches the deck's card radius (or sharp in editorial mode).
- **Padding:** internal caption bar optional; ≥24px from siblings.
- **Variations:** rounded · sharp · tilted · with caption bar · with special frame.
- **Use:** case studies, galleries, portrait quotes. **Don't:** inconsistent radii/frames within one deck.
- **Relationships:** shares radius system with Metric/Highlight cards; overlay rules from Image System.

### 4.10 Section Ribbon
- **Purpose:** a full-width or panel-top band labeling a section/column. **Hierarchy:** structural.
- **Placement:** top of a comparison panel, or spanning columns.
- **Size:** height ~44–64px; hosts a Pill Label or Section Label.
- **Variations:** gradient band · solid · outlined top-edge.
- **Use:** comparison, multi-column, section context. **Don't:** compete with the Title Block.
- **Relationships:** color-codes its column; pairs with Pill Label + Number Badges.

### 4.11 Progress Bar / Meter
- **Purpose:** show a proportion or completion. **Hierarchy:** supporting.
- **Placement:** under a KPI, inside a card, or as a comparison row.
- **Size:** height 6–12px, rounded; label + value at ends.
- **Variations:** single bar · stacked · segmented · radial (ring).
- **Use:** percentages, capacity, funnel stages. **Don't:** use where a real chart is warranted; 3D effects.
- **Relationships:** fill uses accent/positive; sits inside Metric Card.

### 4.12 Timeline Node
- **Purpose:** a point on a temporal/process connector. **Hierarchy:** the node marks a beat; its label carries content.
- **Placement:** on a horizontal/vertical/diagonal connector; alternating labels.
- **Size:** node 48–64px circle (year/step); "now"/final node enlarged.
- **Padding:** label block clear of the connector; ≥24px.
- **Variations:** year badge · numbered step · enlarged "now" node.
- **Use:** timeline, process. **Don't:** place over a busy photo (legibility) — see Image System.
- **Relationships:** connector = Divider; node = Number Badge variant; label = Card Heading + Caption.

### 4.13 Comparison Card / Panel
- **Purpose:** one side of an A/B comparison. **Hierarchy:** mirrored with its counterpart.
- **Placement:** 50/50 columns; contrasting tones (dark vs light).
- **Size:** ~50% width; equal heights; rows aligned across the seam.
- **Variations:** dark vs light · filled vs outlined · with center VS badge.
- **Use:** vs., before/after, us/them. **Don't:** unequal panel weights unless one is deliberately the "winner."
- **Relationships:** each hosts a Section Ribbon + Number Badges; winner uses positive chip.

### 4.14 Highlight Card
- **Purpose:** the one emphasized card that breaks a uniform grid. **Hierarchy:** the focal highlight.
- **Placement:** within a card row/grid (e.g., last or middle card).
- **Size:** same footprint as siblings but visually elevated (gradient fill, scale, or elevation).
- **Variations:** gradient fill · elevated shadow · accent border.
- **Use:** to signal the recommended/featured item. **Don't:** more than one per slide; highlight everything.
- **Relationships:** inverts text to on-accent; uses `gradient-accent`.

### 4.15 Chart Container
- **Purpose:** a framed plotting area for data. **Hierarchy:** co-lead on data slides.
- **Placement:** 55–80% width, on a tinted plot panel; title above.
- **Size:** generous; axis labels legible (≥13px).
- **Padding:** ≥24px inside the plot panel.
- **Variations:** hero chart · chart+callout · split data story · sparkline (mini).
- **Use:** trends, distributions, series. **Don't:** chartjunk, 3D, >5 categorical colors, gradients on marks.
- **Relationships:** callout uses Metric Card; colors follow the dataviz palette rules (accent + neutrals).

### 4.16 Table Container
- **Purpose:** structured rows/columns of values. **Hierarchy:** the header band + one highlighted row/col lead.
- **Placement:** framed panel; header band accent-filled.
- **Size:** row-label column slightly wider; generous cell padding.
- **Variations:** framed · comparison matrix (one winning column) · scorecard (icons/dots per cell).
- **Use:** matrices, specs, comparisons. **Don't:** dense grids with no zebra/scan aids; tiny text.
- **Relationships:** header uses primary/accent; winning cell uses positive; may embed dots/chips.

### 4.17 Footer
- **Purpose:** page number + optional deck/section marker. **Hierarchy:** lowest.
- **Placement:** bottom band (y ≈ 672), usually bottom-right.
- **Size:** Footnote type; "NN / NN".
- **Variations:** page only · deck title + page · with hairline.
- **Use:** every content slide (optional on cover). **Don't:** compete with content; center-stage placement.
- **Relationships:** color = muted; aligns to outer margin.

### 4.18 Logo Block
- **Purpose:** brand mark placement. **Hierarchy:** low, persistent.
- **Placement:** top-left (cover) or footer; consistent per deck.
- **Size:** small; clear space ≥ its own height around it.
- **Variations:** mark only · mark + wordmark.
- **Use:** cover, closing, optional footer. **Don't:** scale it up to fill space; place over busy imagery without clear space.
- **Relationships:** respects margins/clear-space; never inside the focal zone.

### 4.19 Navigation Element (section index / dots)
- **Purpose:** orient the viewer within the deck/section. **Hierarchy:** minimal.
- **Placement:** top rail or side; e.g., "01 · Introduction" or progress dots.
- **Size:** Section Label/Footnote type.
- **Variations:** numbered section chip · progress dots · breadcrumb rail.
- **Use:** long decks, section dividers. **Don't:** clutter every slide; duplicate the Footer's job.
- **Relationships:** echoes Section Ribbon/Pill color coding.

---

## 5. Image System

- **Hero Images:** one dominant subject, bleeding off ≥1 edge or full-bleed. Subject
  faces *into* the slide (flip if needed). This is often the focal highlight.
- **Background Images:** full-bleed, pushed back with a **filter + overlay** so it
  never competes with text. Always low-contrast behind content.
- **Bleeding Images:** may exceed the safe zone on the bleed edge only; the opposite
  edge stays ≥32px from text. Bleeds create energy and scale.
- **Editorial Images:** sharp-cornered blocks, optionally **tilted ±3–8°**, sometimes
  overlapping. Used in editorial/magazine modes for dynamism.
- **Image Overlays (general):** every image that carries text needs a readability
  layer. Choose per goal:
  - **Dark overlay / scrim:** solid dark at 45–70% opacity (or a dark gradient) for
    text-safe heroes.
  - **Gradient overlay:** palette hue at 25–45%, `multiply`/`soft-light`, for brand
    duotone cohesion. Using the deck's accent as a tint is the single biggest
    "designed, not stock" signal.
- **Cropping:** use `object_fit: cover` + an intentional **focus point** (faces
  ≈ y30%, skylines ≈ y60%). Force ratios (1:1, 16:9, 3:2) for uniform galleries.
  Ellipse crop for portraits/avatars.
- **Alignment:** images snap to the grid; multi-image sets share a ratio and radius.
- **Safe placement:** never a small centered thumbnail; never text on a raw busy
  photo; keep faces/subjects out of the area covered by text.
- **Text over images:** required order — image → filter → overlay/scrim →
  (optional) solid panel behind the text block → text. If a scrim can't reach
  contrast, put the text on a solid panel instead.
- **Consistency:** one filter family + one overlay hue across a deck's images. Mixed
  gradings read as clip-art.

---

## 6. Decorative Language

Decoration exists to **structure and accent**, never to fill. Budget: decoration
should read as ~**5–10% of visual weight**. A slide with no focal content and lots
of decoration has failed.

**Allowed (use sparingly, on the grid):**
- **Connector lines / rails** — link badges, timeline nodes, list rows.
- **Accent rules** — 2–4px short rules under titles/labels (echo the accent word).
- **Frames / corner ticks** — thin hairline frames or 4 corner ticks for editorial polish.
- **Ghost typography** — one oversized background number/letter at **4–7% opacity**,
  in genuinely empty canvas, never under/touching content, never bleeding cut-off.
- **Gradient blobs** — large soft shapes at ≤15% opacity, behind content, one per slide.
- **Tech patterns / grids** — subtle, only behind hero imagery in Technology mode.
- **Editorial accents** — pills, tags, year markers, arrows (↗) in editorial mode.

**Forbidden:**
- Drop shadows on flat UI, bevels, glows, 3D, skeuomorphism.
- Heavy borders around everything; boxing content in lines.
- More than one ghost glyph or more than one competing gradient per slide.
- Noise/grain or textures over text; busy patterns behind body copy.
- Decoration placed in safe-zone corners "to balance" — balance with whitespace instead.
- Clip-art, stickers, emoji as decoration.

---

## 7. Layout Principles (Gestalt foundations)

These govern how components are arranged — the physics every archetype obeys.

- **Balance:** distribute visual weight; asymmetry is welcome if it balances (a big
  hero left ↔ dense text right). Avoid accidental lopsidedness.
- **Hierarchy:** one dominant element, one secondary tier, supporting details. The
  eye must know where to look first.
- **Contrast:** pair opposites — big/small, dark/light, dense/airy, serif/sans — to
  create interest and legibility. Every slide has one high-contrast anchor.
- **Repetition:** reuse the component kit and spacing rhythm so the deck feels like
  one system. Repetition = cohesion = premium.
- **Rhythm:** consistent spacing steps (8px base) create a calm cadence; vary it
  intentionally for emphasis.
- **Scale:** dramatic size jumps (a 3–5× ratio between hero and body) read as
  confident. Timid, similar sizes read as cheap.
- **Negative space:** the luxury signal. Protect one dominant empty zone per slide.
- **Alignment:** everything hangs on the grid; nothing floats arbitrarily. Shared
  edges and baselines do most of the "designed" work.
- **Visual flow / eye movement:** guide the eye top-left → focal → supporting, using
  size, connectors, and reading direction. Left-to-right, big-to-small.
- **Emphasis:** exactly one focal highlight per slide (the featured card, hero, or
  gradient wordmark). Emphasize one thing by de-emphasizing the rest.
- **Consistency:** palette roles, type scale, radius, spacing, and components are
  identical across the deck. Deviations are deliberate, never accidental.

---

## 8. Animation Language (future — philosophy only, do not implement)

Motion should feel **calm, purposeful, and quick** — it clarifies structure, never
decorates. Default easing: gentle ease-out; durations 200–500ms; one idea enters at
a time.

- **Fade:** default entrance for text/blocks; low-drama, 200–300ms.
- **Reveal:** wipe/clip a panel or image edge to introduce it; directional toward
  reading flow.
- **Scale:** subtle 0.98→1.0 pop for the focal element only (never everything).
- **Slide:** short-distance (≤40px) directional entrance for list rows/cards.
- **Progressive builds:** reveal list items / cards **one at a time**, in reading
  order, so the audience follows the narrative.
- **Chart animation:** bars grow from baseline, lines draw left-to-right, values
  count up — once, on entrance.
- **Timeline animation:** nodes appear in sequence along the connector; the connector
  draws to meet each node.

Principles: **stagger** (60–120ms) rather than everything at once; **respect
hierarchy** (focal element animates last/most); **never loop** or bounce; motion is
subtractive — if it doesn't aid comprehension, cut it.

---

## 9. Design Modes

A deck picks **one mode**; the mode tunes how the *same* system is expressed. Modes
change type, color, spacing, and imagery — not the component kit.

| Mode | When to use | Typography | Color | Spacing | Imagery |
|---|---|---|---|---|---|
| **Corporate** | B2B, consulting, internal, general business | Clean sans, two-tone titles, moderate scale | Light bg, navy ink, one brand accent + gradient badges | Comfortable, balanced | Blended side subjects, muted overlays |
| **Editorial** | Brand, agency, thought leadership | Condensed heavy display, huge scale, two-tone | High contrast, 1 bold accent (often neon) | Asymmetric, big negative space | Sharp/tilted photo blocks, bleeds |
| **Minimal** | Executive summaries, luxury, restraint | Single family, generous leading, few sizes | Near-monochrome + 1 quiet accent | Very airy, lots of whitespace | Sparse; one restrained image or none |
| **Dark** | Product, keynote, dramatic reveals | Bright text on deep field, large numerals | Deep bg, luminous accent, gradient events | Cinematic, focal-light | Full-bleed with dark scrims |
| **Magazine** | Storytelling, features, culture | Serif/sans mix, pull-quotes, drop kickers | Warm neutrals + editorial accent | Grid-forward, columns, rules | Large duotone photos, captions |
| **Technology** | SaaS, data, AI, engineering | Geometric sans, mono for data/labels | Cool palette, electric accent, subtle grids | Systematic, modular | Tech-textured heroes, product UI |
| **Startup** | Pitches, launches, energetic | Bold sans, punchy scale, gradient wordmarks | Saturated gradient accents | Dynamic, slightly dense | Vibrant, lifestyle, bleeds |
| **Executive** | Board, finance, premium reporting | Refined serif/sans, restrained scale | Charcoal/ivory + champagne/gold accent | Formal, generous margins | Minimal, muted, high-craft |

Mode selection is driven by topic + audience (the director already chooses palette
by mood; mode is the same decision, one level up). A deck commits to its mode on
every slide — mode-mixing breaks cohesion.

---

## 10. Archetype Foundation (how future archetypes are built)

Archetypes are **not** defined here. This section defines the *method* every future
archetype (Cover, Process, Timeline, Statistics, Dashboard, Comparison, Section
Divider, Quote, Closing, …) must follow so they look like one family, never copied.

**Every archetype is authored by making these six decisions, in order:**

1. **Choose the focal highlight.** Decide the ONE thing the eye hits first (hero
   image, KPI number, featured card, gradient wordmark, dark panel). Everything else
   is subordinate. (§7 Emphasis)
2. **Pick the grid split.** Select a split from §3 (60/40, 50/50, 4-up, 70/30…) and
   place the title band, content band, and footer band on it.
3. **Assign type roles.** Map content to the §1 scale — one dominant role only,
   two-tone title, muted subtitle, short body. Enforce the size/weight jumps.
4. **Assemble from the Component Library (§4).** Compose only existing components;
   if a genuinely new primitive is needed, add it to §4 first. Reuse the number
   badge / icon circle / card / pill kit so the archetype matches the deck.
5. **Apply color + image rules.** Use semantic tokens (§2), obey the gradient budget
   and 60/30/10; apply §5 image + overlay rules for any imagery.
6. **Apply decorative + layout discipline.** Add only §6-allowed decoration within
   budget; verify against §7 principles (balance, alignment, negative space, one
   focal point) and the 8px spacing rhythm.

**Archetype authoring checklist (must all pass):**
- [ ] Exactly one focal highlight; one dominant type element.
- [ ] Two-tone title + muted subtitle present (content slides).
- [ ] All spacing on the 8px rhythm; components on the grid.
- [ ] Accent ≤10% of area; ≤1 gradient event; contrast AA.
- [ ] Components reused from §4 (no ad-hoc primitives).
- [ ] Images obey overlay/bleed/focus rules; text never on raw busy photo.
- [ ] One dominant negative-space zone; corners not filled "to balance".
- [ ] Reads as the same system as every other archetype in the deck.

**Consistency mandate:** the source of "premium" is not any single beautiful slide —
it is that all slides share this vocabulary. Future archetypes vary *composition*,
never the *language*. When a new layout is proposed, it is designed against this
document first; only then is it turned into an archetype, and only then into code.

---

*Presentation Design System v1 — the foundation. Layouts and archetypes are built
on top of it, not beside it.*
