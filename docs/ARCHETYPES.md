# ARCHETYPES.md — Layout Archetype Knowledge

> How reference-derived knowledge maps to slide archetypes, and where new archetypes
> are needed. **Learn, never copy** — an archetype is a *composition recipe* (which
> components + principles), never a reproduction of any reference's layout.
>
> This document does NOT define engine archetypes or code. It is the design-analysis
> layer feeding the pipeline: References → Design System → Component Library → **Archetypes** → Generator.
> Built on [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md), [`COMPONENT_LIBRARY.md`](./COMPONENT_LIBRARY.md),
> and v1 §10 (the six-decision authoring method).

## Merge convention
- Each archetype lists supporting references `[R#]`, its component recipe, and the
  principles it must obey. New references extend recipes; disagreements become variants.
- Reference IDs: see `DESIGN_SYSTEM.md` Reference Log.

## The six-decision authoring method (from v1 §10 — every archetype follows it)
1. Choose the focal highlight. 2. Pick the grid split. 3. Assign type roles.
4. Assemble from the Component Library. 5. Apply color + image rules. 6. Apply
decorative + layout discipline. Then pass the authoring checklist (v1 §10).

---

## A. Reference → archetype mapping

| Ref | Nearest engine archetype | Verdict | Action |
|-----|--------------------------|---------|--------|
| R1  | `title_only` → "split hero" | **Matches** | Reinforce with the blend/bleed + gradient-wordmark recipe |
| R2  | `title_only` → "editorial masthead" | **Partial** | **New variant: "Editorial Neon Cover"** |
| R3  | `bullets` → "numbered editorial" | **Gap** | **New archetype: "Agenda / Table of Contents"** |
| R4  | `three_column` → "three cards" | **Partial** | **New archetype: "Feature / Process Cards (N-up + highlight)"** |
| R5  | `two_column` → "dual panel" | **Matches** | Enshrine recipe as **"Dual-Panel Comparison"** |

---

## B. Existing archetypes — recipe reinforcement

### Cover · Split Hero `[R1]`
- **Focal:** gradient wordmark (or hero subject). **Split:** 55/45, subject bleeds far edge.
- **Components:** Title Block (gradient wordmark) + Logo Block + Icon+Caption Chips + Hero Image (blended).
- **Principles:** title opposite the subject; two type sizes; one dominant dark void.

### Comparison · Dual-Panel Comparison `[R5]`
- **Focal:** the contrast between two panels. **Split:** 50/50, dark vs light.
- **Components:** Title Block (two-tone) + 2× Comparison Panel (Pill Label header + Number
  Badge rows). **Principles:** mirror rows across the seam; add a winner chip if asymmetric.

---

## C. Recommended NEW archetypes (design rationale)

### 1. Agenda / Table of Contents `[R3]` — **highest-value gap**
- **Why new:** agenda/TOC is a high-frequency deck genre with no first-class home;
  `bullets`→"numbered editorial" approximates it but lacks the rail + badge system and the
  optional hero-image pairing that make it read premium.
- **Focal:** the numbered rail. **Split:** 60/40 (rail left, optional bleed image right).
- **Components:** Title Block (two-tone + muted sub) + Connector Rail + Number Badge
  (accent-cycle) + row (heading + caption) + optional Hero Image (blend/bleed).
- **Principles:** even vertical rhythm; captions muted; image is optional and must not
  claim to relate to specific items.
- **Variations:** with image (R3) · text-only rail · two-column agenda (long decks).

### 2. Feature / Process Cards (N-up + highlight) `[R4]`
- **Why new:** covers both the "feature grid" and the missing **Process** genre; the
  "one featured card" device is a distinct, repeatable premium pattern not captured by
  generic three_column cards.
- **Focal:** the Highlight/Featured Card. **Split:** N equal columns (3–4) + 1 featured.
- **Components:** Title Block + N× Feature Card (Icon Circle + Number Badge + heading +
  caption) + 1× Highlight Card. **Principles:** equal footprints; elevate exactly one;
  fill short cards with a stat/icon; left-to-right reading.
- **Variations:** feature grid · sequential process (rail through badges) · benefits.

### 3. Editorial Neon Cover `[R2]` — mode variant of Cover
- **Why new:** the neon-editorial cover is a coherent *mode variant*, not the corporate
  split-hero; it needs sharp/tilted photos, pills, and extreme scale — different rules.
- **Focal:** extreme-scale two-tone headline. **Split:** asymmetric editorial.
- **Components:** Pill Label tags + year marker + Title Block (condensed two-tone) +
  Editorial Photo Block(s) + small justified body. **Principles:** vast negative space;
  single neon; sharp corners; one tilted block max.
- **Variations:** single big photo · overlapping pair · no-photo statement.

---

## D. Cross-archetype consistency rules
- All archetypes in one deck share: the component kit, radius system, spacing rhythm
  (8px), palette roles, and mode. Archetypes vary **composition**, never **language**.
- Anti-repeat must extend to *visual motif* (card-grid vs list vs band), not just layout
  name, so consecutive slides never feel same-y. `[audit finding, reinforced by R3/R4]`
- Every archetype must resolve the density↔whitespace tension: hit richness with
  purposeful layers, but protect one dominant negative-space zone. `[R1,R2 vs element floor]`

## E. Genres still lacking references (from the engine audit — watch for them)
Statistics / Dashboard, Timeline, Section Divider, Closing/Conclusion, Quote (have engine
support but no premium reference yet). When references arrive, map them here and write recipes.

*Append new references to the mapping table, then extend recipes or add archetypes.
Never delete a recipe; disagreements become variations with trade-off notes.*
