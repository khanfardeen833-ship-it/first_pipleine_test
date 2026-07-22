# Skill 04 — Image Elements

## ⚠️ Choosing the photo: use `query`, never a guessed URL

You do NOT know which Pexels photo ID maps to which picture. If you fabricate a
URL like `.../photos/37290569/...` you get a RANDOM photo (a dog, a cliff) —
this is the #1 cause of irrelevant images.

**Instead, give every image element a `query`** — 2-5 concrete subject words
describing the photo you want. The pipeline runs a real Pexels search and fills
in a relevant `src` for you. Examples:

```
{ "kind": "image", "query": "bubble tea pastel cups", "x": 720, "y": 0, "width": 560, "height": 720, ... }
{ "kind": "image", "query": "warehouse robots automation", "is_background": true, ... }
```

- `query` should name the **literal subject** ("matcha latte top view", "city
  skyline night"), not abstract themes ("success", "innovation").
- Omit `src` when you provide `query` — the search supplies it. Only hard-code a
  `src` if you were given a specific verified URL.
- Orientation is inferred from width/height (tall element → portrait photo).

## What this is
Images (photos, GIFs) live at the file level in `content.imageElements`.
The changelog entry carries position, size, and several required blocks
(shadow, border, cropRect, focusPoint). `deck_builder.py` emits all required
blocks automatically — you only set values you want to change.

## content record (inside `content.imageElements` array)

```json
{
  "id": "image-26",
  "slideId": "slide-3",
  "groupId": null,
  "src": "https://images.pexels.com/photos/37290569/pexels-photo-37290569.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
  "s3Key": null,
  "isBackground": false,
  "_smartDiagram": false
}
```

- `src` is the image URL — use Pexels URLs for stock photos
- `s3Key` is `null` for external URLs
- `isBackground`: set to `true` if the image covers the full slide as background
- `_smartDiagram`: always `false` for regular images

## changelog record (inside `changelog.slides[slideId].elements`)

```json
{
  "slideId": "slide-3",
  "position": { "x": 48, "y": 48 },
  "width": 382,
  "height": 254,
  "rotation": 0,
  "zIndex": 26,
  "opacity": 1,
  "objectFit": "cover",
  "borderRadius": 0,
  "filter": "none",
  "blur": 0,
  "scaleX": 1,
  "scaleY": 1,
  "shadow": {
    "enabled": false,
    "angle": 135,
    "color": "#000000",
    "opacity": 40,
    "distance": 8,
    "blur": 12,
    "size": 0,
    "spread": 0
  },
  "border": {
    "type": "none",
    "width": 4,
    "color": "#000000",
    "specialStyle": null
  },
  "overlay": {
    "color": null,
    "opacity": 0,
    "blendMode": "normal"
  },
  "cropRatio": "free",
  "cropRect": {
    "left": 0,
    "top": 0,
    "right": 0,
    "bottom": 0
  },
  "focusPoint": {
    "x": 50,
    "y": 50
  },
  "cropScale": 1,
  "cropAppliedCount": 0,
  "updatedAt": 1778668347757
}
```

## Rules & gotchas

- `shadow`, `border`, `overlay`, `cropRect`, `focusPoint` blocks are required in the JSON — `deck_builder.py` emits them automatically. **Never pass them to `add_image()` unless you change a value**; `shadow`/`border`/`overlay` accept partial dicts (merged over defaults), `crop_rect`/`focus_point` must be complete dicts if passed
- `borderRadius`: `0` = sharp corners; `8` = slightly rounded; `360` = circle crop
- `cropRatio`: use `"free"` for no forced ratio, or `"16:9"`, `"4:3"`, `"1:1"`, `"3:2"`
- `focusPoint` x and y are percentages (0–100), default `50, 50` = center
- Full-slide background image: `x: 0, y: 0, width: 1280, height: 720`, set `isBackground: true` in content record, and put it at a low `zIndex` (e.g. 1) so other elements render on top
- `filter`: choose from `none | noir | gray | sepia | vintage | warm | cool | crossprocess | bright | dark | faded | matte | dynamic | vibrant | dramatic | soft` — pick one that suits the slide mood
- `blur`: `0` = sharp; use `4–8` for subtle background blur effect
- `objectFit`: `"cover"` fills the box (recommended); `"contain"` letterboxes
- `scaleX/scaleY`: `1` = normal, `-1` = flip; default both to `1`
- `overlay`: set `color` + `opacity > 0` to tint the image (e.g. dark overlay for text readability). `blendMode` options: `normal | multiply | screen | overlay | darken | lighten | color | soft-light | hard-light`
- `border.specialStyle`: only used when `border.type = "special"` — options: `inner-shadow | thin-frame | double-frame | film | polaroid | rounded-white`

---

## IMPORTANT — Use these properties, don't leave them at defaults

`filter`, `shadow`, `border`, and `overlay` exist to make slides look premium.
**Always choose intentional values — never leave every property at its default.**

---

## filter — pick one per image (never always "none")

| filter | when to use |
|--------|------------|
| `"dramatic"` | Hero/title slides, dark moody backgrounds |
| `"warm"` | Real estate, food, lifestyle, travel |
| `"cool"` | Tech, finance, corporate, medical |
| `"noir"` | Fashion, luxury, black-and-white editorial |
| `"dark"` | Full-bleed backgrounds where text sits on top |
| `"vibrant"` | Consumer apps, playful/youthful decks |
| `"faded"` | Minimal/editorial decks, muted aesthetic |
| `"sepia"` | Historical, vintage, heritage topics |
| `"matte"` | Premium lifestyle, neutral editorial |

```python
# Hero background — dark filter so white text is readable
slide.add_image(src, x=0, y=0, width=1280, height=720,
    is_background=True, filter="dramatic",
    overlay={"color": "#000000", "opacity": 40, "blendMode": "multiply"})

# Side panel — warm filter for lifestyle topic
slide.add_image(src, x=720, y=0, width=560, height=720, filter="warm")
```

---

## shadow — enable for floating/card images (not full-bleed)

Enable shadow when the image sits on a light background as a card/panel.
**Never enable shadow on full-bleed background images.**

```python
# Card image with shadow — floats on light slide background
# (partial shadow dict merges over defaults; unchanged keys omitted)
slide.add_image(src, x=720, y=80, width=480, height=360,
    border_radius=12,
    shadow={"enabled": True, "angle": 145, "distance": 12,
            "blur": 24, "size": 4, "opacity": 35})
```

---

## border — use "standard" to frame card images

```python
# Image with gold border frame
slide.add_image(src, x=720, y=80, width=480, height=360,
    border_radius=8, filter="warm",
    border={"type": "standard", "width": 3, "color": "#c9a14a"},
    shadow={"enabled": True, "blur": 16, "size": 2, "opacity": 30})
```

## border — "special" preset frames (instant premium looks)

`border={"type": "special", "specialStyle": ...}` applies a designed frame —
width/color are ignored. One per slide max; match the deck's mood:

| specialStyle | look | best for |
|---|---|---|
| `"polaroid"` | white frame, thick bottom | team photos, galleries, casual/retro decks (pair with slight `rotation` ±2–4) |
| `"film"` | black frame with sprocket strips | media, photography, storytelling decks |
| `"thin-frame"` | hairline gallery frame | minimal/editorial, luxury |
| `"double-frame"` | double-line classic frame | heritage, formal, awards |
| `"rounded-white"` | thick white rounded frame | light backgrounds, product shots |
| `"inner-shadow"` | inset depth, no visible frame | subtle polish on full-width panels |

```python
# Polaroid trio — stagger y and rotation for a pinned-photos look
slide.add_image(src, x=90,  y=160, width=300, height=260, rotation=-3,
    filter="warm", border={"type": "special", "specialStyle": "polaroid"},
    shadow={"enabled": True, "blur": 20, "distance": 10, "opacity": 35})
```

---

## Premium image recipes — composition treatments

### Circular portrait / avatar (ellipse crop)
`crop_ratio="ellipse"` clips the image to an ellipse (make width == height for
a circle). Use for speaker headshots, testimonial avatars, team grids.

```python
slide.add_image(src, x=88, y=200, width=220, height=220,
    crop_ratio="ellipse", filter="matte",
    focus_point={"x": 50, "y": 35},   # anchor on the face
    border={"type": "standard", "width": 4, "color": "#c9a14a"},
    shadow={"enabled": True, "blur": 22, "distance": 8, "opacity": 30})
```

### focus_point — art-direct every cover crop
With `object_fit="cover"` the box crops the source; `focus_point` (x/y in %)
chooses what survives the crop. **Set it intentionally on heroes and tall
panels**: faces ≈ `{"x": 50, "y": 30}`, skylines/horizons ≈ `{"x": 50, "y": 60}`,
subject right-of-frame ≈ `{"x": 70, "y": 45}`. Default 50/50 beheads portraits.

### crop_ratio + crop_rect — disciplined framing
- `crop_ratio`: force `"1:1"` for grid tiles, `"16:9"` for wide banners,
  `"3:2"` for editorial cards — keeps multi-image grids perfectly uniform.
- `crop_rect` trims % off each edge of the source before fitting, e.g.
  `{"left": 10, "top": 0, "right": 10, "bottom": 20}` to cut a watermark or
  tighten on the subject.

### scale_x=-1 — flip toward the content
Flip an image horizontally so its subject *faces into* the slide's text
(people/objects looking off-canvas leak attention). Costs nothing, reads pro.

```python
slide.add_image(src, x=760, y=0, width=520, height=720,
    scale_x=-1, filter="cool", focus_point={"x": 40, "y": 45})
```

### Blurred backdrop + sharp card (depth stack)
Same or related image twice: full-bleed blurred + darkened behind, sharp
framed card on top. Instant depth for section dividers.

```python
slide.add_image(src, x=0, y=0, width=1280, height=720, is_background=True,
    blur=8, filter="dark",
    overlay={"color": "#0a0d12", "opacity": 50, "blendMode": "multiply"})
slide.add_image(src, x=420, y=140, width=440, height=440,
    border_radius=16, border={"type": "special", "specialStyle": "thin-frame"},
    shadow={"enabled": True, "blur": 36, "distance": 16, "opacity": 50})
```

### overlay blend modes — palette-tinted photography
Tinting every photo with the deck's palette color is the single biggest
"designed, not assembled" signal. Recipes (overlay only renders when `color`
is set and `opacity > 0`):

| goal | recipe |
|---|---|
| text-safe dark hero | dark hex (e.g. `#0a0d12`), opacity 45–65, `multiply` |
| brand duotone wash | palette accent hex, opacity 30–45, `color` or `soft-light` |
| moody color grade | deep palette hex, opacity 25–40, `overlay` or `hard-light` |
| lift a dark photo | light hex (e.g. `#f4ecdf`), opacity 15–25, `screen` |

```python
# Brand-tinted side panel — overlay color comes from the deck palette
slide.add_image(src, x=768, y=0, width=512, height=720,
    filter="noir", scale_x=-1,
    overlay={"color": "#6D2E46", "opacity": 38, "blendMode": "soft-light"},
    focus_point={"x": 55, "y": 35})
```

### Hero background — the full treatment
Full-bleed background = filter + overlay + focus_point together, always:

```python
slide.add_image(src, x=0, y=0, width=1280, height=720,
    is_background=True, filter="dramatic",
    overlay={"color": "#0a0d12", "opacity": 55, "blendMode": "multiply"},
    focus_point={"x": 50, "y": 40})
```

### Per-slide image styling checklist
Every `add_image()` call should set, deliberately:
1. `filter` matched to deck mood (never leave all images `"none"`)
2. `overlay` tinted with a palette hex on heroes/panels (text safety + cohesion)
3. `focus_point` on any cover-cropped hero, portrait, or tall panel
4. shadow + radius (or a `special` frame) on card images; **neither** on full-bleed
5. `scale_x=-1` when the subject faces away from the content

Use the SAME filter family + overlay hex across a deck's images — mixed
gradings (one warm, one cool, one vibrant) read as clip-art, not design.

---

## Pexels URL format

Prefer `query` (see the top of this file) — the search returns a real, relevant
URL. Do NOT invent photo IDs; a guessed ID resolves to an unrelated photo.
The resolved URLs look like this (you don't write them by hand):
```
https://images.pexels.com/photos/{PHOTO_ID}/pexels-photo-{PHOTO_ID}.jpeg?auto=compress&cs=tinysrgb&h=650&w=940
```
