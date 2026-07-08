# DESIGN_SYSTEM.md — Living Design Language

> Evolving design knowledge distilled from professional reference slides.
> **Learn, never copy.** This document captures *reusable principles*, not layouts.
> The frozen token tables (type scale, semantic colors, grid units, modes) live in
> [`Presentation-Design-System-v1.md`](./Presentation-Design-System-v1.md); this
> file is the **living principles layer** that grows as new references arrive.
>
> Pairs with [`COMPONENT_LIBRARY.md`](./COMPONENT_LIBRARY.md) and
> [`ARCHETYPES.md`](./ARCHETYPES.md).

## Merge convention (how this document evolves)
- New references are appended to the **Reference Log** with an ID (R1, R2, …).
- Every principle is tagged with the references that support it, e.g. `[R1,R3]`.
- **Never delete a principle** when a new reference disagrees. Instead record a
  **Trade-off** entry documenting both positions and when each applies.
- Confidence rises with more independent references: `[R1]` = provisional,
  `[R1,R3,R5]` = strong. Prefer strong principles when they conflict with provisional.
- Copyright guardrail: store *principles and relationships*, never pixel positions,
  exact color values, or artwork from a reference.

## Reference Log
| ID | Source | Family / Mode | One-line design signature |
|----|--------|---------------|---------------------------|
| R1 | cover (dark, "AI") | Technology / Corporate Gradient (Dark) | Split hero; gradient wordmark; blended subject bleed |
| R2 | cover (black, "Studio") | Editorial / Startup (Neon) | Extreme-scale condensed headline; single neon; tilted photo blocks |
| R3 | agenda | Corporate Gradient (Light) | Numbered rail + gradient badges; two-tone title; subject bleed |
| R4 | cards | Corporate Gradient (Light) | Equal card grid + one gradient featured card |
| R5 | comparison | Corporate Gradient (Light) | Dark/light dual panels; pill labels; numbered rows |

---

## 1. Core premium invariants (multi-reference, high confidence)
1. **Reuse a small component vocabulary across slide types.** Cohesion — not
   per-slide novelty — is the #1 premium signal. `[R1,R3,R4,R5]`
2. **One focal highlight per slide;** everything else is deliberately quieter. `[R1,R2,R4]`
3. **Two-tone titles** (base ink + one accent word) with a muted subheading line. `[R3,R4,R5]`
4. **Restrained accent** — one gradient family or one neon; accent ≤10% of area. `[R1,R2,R4]`
5. **Whitespace + alignment discipline** — strong margins, shared baselines, rails. `[R1,R2,R3]`
6. **Confident imagery** — subjects bleed off an edge or sit as bold blocks; never a
   timid centered thumbnail. `[R1,R2,R3]`
7. **High figure–ground contrast** — dark panel on light, or neon on black. `[R2,R5]`

## 2. Conditional principles (the "when X, do Y" library)
### Covers & heroes
- When a hero subject occupies one side, put the title on the opposite side and bleed
  the subject off the far edge to balance weight. `[R1,R3]`
- When the headline is the focus, limit a cover to two type sizes; carry emphasis with
  one accent (gradient wordmark or neon word). `[R1,R2]`
- When placing a subject on a same-hue dark field, blend it in seamlessly (no frame). `[R1]`

### Lists, agendas, processes
- When items are sequential, attach a number-badge system on a connector rail and
  cycle badge colors through an ordered accent set. `[R3,R4,R5]`
- When rows carry a heading + supporting line, set headings bold and captions muted,
  on a shared left edge. `[R3,R5]`

### Cards & grids
- When showing peers, keep all cards on one footprint and elevate exactly one
  (gradient/elevation) as the recommended item. `[R4]`
- When a card's text is short, fill the space with a larger stat/icon or tighten the
  card height — never leave dead bottom whitespace. `[R4 weak point]`

### Comparisons
- When comparing two entities, use opposing panel tones (dark vs light) and mirror the
  row structure. If one side wins, break symmetry with an accent chip. `[R5]`

### Labels & type
- When labeling a section/column, use a rounded pill, not a full-width bar. `[R2,R5]`
- Apply letterspacing only to uppercase kicker/section labels — never to body or large
  display. `[R1,R3]`

### Imagery & readability
- When text sits on imagery, add a scrim or move text onto a solid panel. `[all]`
- Keep one filter family + one overlay hue across a deck's images. `[carried from image rules]`

## 3. Trade-offs (references that legitimately disagree — keep both)
| Dimension | Position A | Position B | When to use which |
|---|---|---|---|
| Photo treatment | **Blended, frameless bleed** `[R1,R3]` | **Sharp/tilted blocks** `[R2]` | Blend for cinematic Corporate/Tech/Dark; sharp/tilt for Editorial/Startup |
| Accent strategy | **Multi-stop gradient family** `[R1,R3,R4,R5]` | **Single flat neon** `[R2]` | Gradient for polished corporate; neon for high-energy editorial |
| Card corners | **Rounded soft-fill** `[R3,R4,R5]` | **Sharp corners** `[R2]` | Match the deck mode; never mix radii within one deck |
| Density | **Moderate, structured** `[R4,R5]` | **Extreme negative space** `[R2]` | Sparse for statement covers; structured for content slides |
| Decoration under titles | Design-system allows a short accent rule | Engine avoid-list currently forbids underlines/bars | Prefer whitespace or a two-tone accent word; use a *short* accent rule (not a full-width bar/underline) only when it echoes the accent word |

## 4. Design modes observed (see v1 §9 for the full 8-mode matrix)
- **Corporate Gradient (Light)** `[R3,R4,R5]` — light field, navy ink, violet/blue/teal/gold
  gradient badges, rounded cards, two-tone titles. The workhorse mode.
- **Technology / Corporate Gradient (Dark)** `[R1]` — deep field, gradient wordmark,
  blended tech imagery. Covers, keynotes.
- **Editorial / Startup (Neon)** `[R2]` — black field, single neon, condensed black
  display, sharp/tilted photos, pills + year markers. Brand/agency energy.

## 5. Open questions to resolve with more references
- Do light corporate decks ever use a dark *content* slide mid-deck (sandwich)? (Only
  covers/comparison panels seen dark so far.)
- Is the connector rail used outside agendas (e.g., process/timeline)? (Expected, unconfirmed.)
- Editorial mode with charts/tables — no reference yet.

*Append new references above in the Reference Log, then tag principles. Do not overwrite.*
