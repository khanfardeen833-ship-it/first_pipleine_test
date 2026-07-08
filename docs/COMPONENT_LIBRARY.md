# COMPONENT_LIBRARY.md — Reusable Design Components

> The reusable building blocks extracted from professional references.
> **Learn, never copy** — these are abstract, parameterized components, not any
> reference's exact element. Every future archetype composes only from this library;
> a new primitive is added here *before* it is used.
>
> Companion to [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) (principles) and
> [`ARCHETYPES.md`](./ARCHETYPES.md) (composition). Full token tables in
> [`Presentation-Design-System-v1.md`](./Presentation-Design-System-v1.md) §4.

## Merge convention
- Each component tags the references that evidence it, e.g. `[R3,R4]`.
- New references may add **variations** or **relationships** — append, don't replace.
- Conflicting guidance becomes a **Variation** or a note, never a deletion.
- Reference IDs: see `DESIGN_SYSTEM.md` Reference Log.

Every entry: **Purpose · Structure · Padding · Spacing · Hierarchy · Variations ·
When to use · When NOT to use · Relationships.**

---

### Title Block (two-tone) `[R3,R4,R5]`
- **Purpose:** the slide's headline unit. **Structure:** optional kicker/pill →
  title (base ink + one accent word) → muted subheading → optional short accent rule.
- **Padding/Spacing:** 8–16px between lines; sits in the top band.
- **Hierarchy:** highest on content slides. **Variations:** two-tone (default) ·
  gradient wordmark (cover) · centered (luxury/minimal) · with eyebrow pill.
- **Use:** every content slide. **Don't:** two title blocks; skip the subheading slot.
- **Relationships:** kicker color echoes a Section Ribbon/Pill; accent word echoes the accent rule.

### Number Badge `[R3,R4,R5]`
- **Purpose:** ordinal marker (01–0N) that ties list/card items together — the deck's
  connective tissue. **Structure:** filled circle + white numeral; optional connector rail.
- **Padding:** numeral optically centered. **Spacing:** even vertical/horizontal intervals.
- **Hierarchy:** secondary but unifying. **Variations:** gradient fill · outlined ·
  solid · **accent-cycle** (rotate through an ordered hue set) · overlapping an Icon Circle.
- **Use:** agendas, process, comparison rows, feature cards. **Don't:** mix badge styles
  on one slide; exceed ~6.
- **Relationships:** pairs with Connector Rail and Icon Circle; cycles with accent set.

### Icon Circle `[R1,R4]`
- **Purpose:** a soft-tinted disc holding one line icon; humanizes cards.
- **Structure:** disc + centered icon (~50% of disc). **Padding:** ≥25% breathing room.
- **Hierarchy:** supporting. **Variations:** soft tint (default) · solid accent ·
  gradient (featured only) · with overlapping Number Badge.
- **Use:** feature/stat cards, agendas. **Don't:** >1 icon per card; multi-color icons.
- **Relationships:** frequently hosts a Number Badge; one accent family per deck.

### Pill Label `[R2,R5]`
- **Purpose:** rounded-full tag for sections, categories, eyebrows, cover tags.
- **Structure:** rounded-full container + uppercase Section-Label text; optional leading icon (↗).
- **Padding:** 16–24px horizontal; height ~32–44px. **Hierarchy:** low but eye-catching.
- **Variations:** gradient fill · solid · outlined · with icon.
- **Use:** comparison headers, section labels, cover tag rows. **Don't:** long text
  (1–3 words); stacking many into clutter; using a full-width bar instead.
- **Relationships:** color aligns with the panel/section it labels; echoes Section Ribbon.

### Feature Card `[R4]`
- **Purpose:** one idea = icon + heading + short caption, in a repeatable grid.
- **Structure:** rounded soft-fill card → Icon Circle (+ badge) → bold heading → muted
  caption → optional footer accent bar. **Padding:** ≥28px. **Spacing:** 24px inter-card.
- **Hierarchy:** heading leads within the card. **Variations:** default · with stat ·
  numbered · featured (see Highlight Card).
- **Use:** feature sets, process steps, benefits. **Don't:** long paragraphs; unequal
  card footprints; leaving dead bottom space (fill with a stat/icon).
- **Relationships:** shares radius with all cards; one Highlight Card per grid.

### Metric Card `[R4-adjacent; statistics genre]`
- **Purpose:** one number + label + optional delta/context. **Structure:** oversized
  KPI Number → label → optional delta chip / sparkline; optional Icon Circle.
- **Padding:** ≥28px. **Hierarchy:** the number dominates.
- **Variations:** default · with sparkline · with delta chip · featured (gradient).
- **Use:** statistics/dashboard slides. **Don't:** bury the number in a sentence; >6 per slide.
- **Relationships:** hosts delta (positive/negative); may embed a Chart Container (sparkline).

### Highlight / Featured Card `[R4]`
- **Purpose:** the one emphasized card that breaks a uniform grid = the focal highlight.
- **Structure:** same footprint as siblings + gradient fill / elevation + inverted (on-accent) text.
- **Hierarchy:** the focal element. **Variations:** gradient fill · elevated · accent border.
- **Use:** to signal the recommended/featured item. **Don't:** more than one per slide.
- **Relationships:** uses the gradient-accent token; sits within a Feature/Metric grid.

### Comparison Panel `[R5]`
- **Purpose:** one side of an A/B comparison. **Structure:** large rounded panel →
  Section Ribbon/Pill header → numbered rows (heading + caption). **Padding:** panel ≥28px.
- **Hierarchy:** mirrored with its counterpart; rows aligned across the seam.
- **Variations:** dark vs light · filled vs outlined · with center "VS" badge · with
  a "winner" accent chip.
- **Use:** vs., before/after, us/them. **Don't:** unequal weights unless one is the
  deliberate winner; symmetric panels with no emphasis.
- **Relationships:** hosts Pill Label + Number Badges; winner uses positive chip.

### Hero Image (blend/bleed) `[R1,R3]`
- **Purpose:** dominant visual; often the focal highlight. **Structure:** large subject
  bleeding off ≥1 edge, blended into a same-hue field or full-bleed. **Padding:** none on
  bleed side; ≥32px from text on content side.
- **Variations:** blended side subject · full-bleed background · (see Editorial Photo Block).
- **Use:** covers, section dividers, image-heavy slides. **Don't:** small centered
  thumbnail; text on it without a scrim.
- **Relationships:** requires Overlay/Scrim when text overlaps; may pair with a floating card.

### Editorial Photo Block `[R2]`
- **Purpose:** sharp-cornered photo used as an energetic block. **Structure:** rectangular
  photo, sharp corners, optional tilt ±3–8°, may overlap another block.
- **Hierarchy:** supporting-to-focal. **Variations:** straight · tilted · overlapping pair.
- **Use:** Editorial/Startup mode. **Don't:** in rounded/corporate decks (radius clash);
  tilting more than one block into chaos.
- **Relationships:** consistent treatment across the deck; pairs with Pill tags.

### Connector Rail `[R3]`
- **Purpose:** a vertical/horizontal line linking sequential Number Badges/nodes.
- **Structure:** 1–2px muted line threading badge centers. **Hierarchy:** minimal.
- **Variations:** vertical (agenda) · horizontal/diagonal (timeline) · dotted.
- **Use:** agendas, timelines, processes. **Don't:** decorative rails with nothing on them.
- **Relationships:** binds Number Badges / Timeline Nodes.

### Icon + Caption Chip `[R1]`
- **Purpose:** a compact icon + 1–2 line label, for cover feature call-outs.
- **Structure:** small icon (accent) + 2-line caption beside it. **Hierarchy:** low.
- **Variations:** icon-left · stacked. **Use:** cover feature hints, footnote facts.
- **Don't:** carry primary content; crowd many chips.
- **Relationships:** lives in the cover's lower band, aligned to the title's left edge.

### Logo Block `[R1]`
- **Purpose:** brand mark placement. **Structure:** mark (+ optional wordmark) with clear
  space ≥ its own height. **Hierarchy:** low, persistent. **Placement:** top-left cover or footer.
- **Variations:** mark only · mark + wordmark. **Use:** cover, closing, optional footer.
- **Don't:** scale up to fill space; place over busy imagery without clear space.
- **Relationships:** respects margins; never inside the focal zone.

### Footer `[general]`
- **Purpose:** page number + optional deck/section marker. **Structure:** Footnote type,
  bottom band (bottom-right). **Hierarchy:** lowest. **Variations:** page only · title+page · with hairline.
- **Use:** content slides. **Don't:** compete with content; center placement.
- **Relationships:** muted color; aligns to outer margin.

### Chart Container / Table Container / Quote Block `[carried from v1 §4]`
- Carried forward unchanged from the design system; no new reference evidence yet.
  Chart = framed tinted plot + callout; Table = accent header + one highlighted row/col;
  Quote = oversized statement + attribution + optional ghost quote-mark.

---

## Components still unseen in references (defined in v1, awaiting evidence)
Progress Bar / Meter · Timeline Node · Section Ribbon (full-width variant) · Navigation
Element · Divider (standalone). Keep v1 specs; upgrade confidence when a reference appears.

*Append variations/relationships from new references; never delete a component.*
