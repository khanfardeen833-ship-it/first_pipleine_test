# Skill 03 — Shape Elements

## What this is
Shapes are rectangles, circles, lines, and other geometric elements.
They live at the **file level** in `content.shapeElements` (not inside slides).
Each shape carries a `slideId` to associate it with a slide.

## content record (inside `content.shapeElements` array)

```json
{
  "id": "shape-7",
  "slideId": "slide-2",
  "groupId": null
}
```

- Only 3 fields in the content record — do not add more here
- `slideId` must match a valid slide ID in `content.slides`

## changelog record (inside `changelog.slides[slideId].elements`)

```json
{
  "slideId": "slide-2",
  "position": { "x": 440, "y": 56 },
  "width": 150,
  "height": 100,
  "rotation": 0,
  "zIndex": 7,
  "opacity": 1,
  "shapeType": "rectangle",
  "fill": "#c67c3a",
  "stroke": "#c67c3a",
  "strokeWidth": 2,
  "updatedAt": 1778668169445
}
```

## Valid shapeType values

- `rectangle`
- `circle` (renders as ellipse — width/height control the ratio)
- `triangle`
- `line`
- `arrow`
- `star`
- `hexagon`

## Rules & gotchas

- The `slideId` in the changelog record must match the `slideId` in the content record AND be the key under `changelog.slides` where this element lives
- `fill` and `stroke` are hex colors — they can differ (e.g. filled shape with no border: set `stroke` same as `fill` and `strokeWidth: 0`)
- **Outline / frame shapes: set `fill: "transparent"`** (plus `stroke` + `strokeWidth`). A frame, ring, or picture-border is a stroke-only shape — its interior stays see-through so whatever is behind it (an image, text, another panel) remains visible.
- **NEVER draw a frame with an opaque fill on TOP of an image.** A rectangle filled with a solid color (even the background color) at a higher `zIndex` than a photo will completely HIDE that photo — the #1 cause of "empty framed box" slides. To frame a photo, either (a) give the image element its own `border` (see `04-image-element.md`), or (b) overlay a `fill: "transparent"` stroke-only shape. If you truly want a solid panel, place it BEHIND the image (lower `zIndex`), never over it.
- `opacity` is `0.0` to `1.0` — use `1` for fully opaque
- `zIndex` must be globally unique — see `09-zindex-rules.md`
- Shapes are commonly used as background color blocks — for a full-slide background, use `x: 0, y: 0, width: 1280, height: 720`

## Helper function

```python
def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx, now,
               fill="#c67c3a", stroke=None, stroke_width=0, opacity=1):
    if stroke is None:
        stroke = fill
    content_record = {
        "id": shape_id, "slideId": slide_id, "groupId": None
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "opacity": opacity,
        "shapeType": shape_type,
        "fill": fill, "stroke": stroke, "strokeWidth": stroke_width,
        "updatedAt": now
    }
    return content_record, changelog_record
```
