# Skill 08 — Changelog Sync

## What this is
The most critical structural rule in Bildory. Every element that exists in
`files.content` must have a matching entry in `files.changelog.slides`.
If they go out of sync, the deck will fail validation and may not render.

## The two-record pattern

Every element type (except tables) splits into TWO records:

```
content record     → minimal, just IDs and content/src
changelog record   → full geometry: position, size, zIndex, style
```

For TEXT:
- Content lives in `content.slides[i].textElements[]`
- Geometry lives in `changelog.slides[slideId].elements[textId]`

For SHAPES, IMAGES, ICONS, CHARTS:
- Content lives in `content.{type}Elements[]` at file level
- Geometry lives in `changelog.slides[slideId].elements[elementId]`

For TABLES:
- Content (including position + zIndex) lives in `content.tableElements[]`
- Changelog has a minimal duplicate at `changelog.slides[slideId].elements[tableId]`

## Changelog structure

```
changelog.slides = {
  "slide-1": {
    "elements": {
      "text-1":  { slideId, position, width, height, rotation, zIndex, style, ... },
      "text-2":  { slideId, position, width, height, rotation, zIndex, style, ... },
      "shape-5": { slideId, position, width, height, rotation, zIndex, shapeType, fill, ... },
      "image-3": { slideId, position, width, height, rotation, zIndex, shadow, border, ... }
    }
  },
  "slide-2": {
    "elements": { ... }
  }
}
```

## Sync checklist — run this mentally before saving

1. Every `text-N` in `content.slides[i].textElements` → has entry in `changelog.slides[slideId].elements["text-N"]`
2. Every `shape-N` in `content.shapeElements` → has entry in `changelog.slides[shape.slideId].elements["shape-N"]`
3. Every `image-N` in `content.imageElements` → has entry in `changelog.slides[image.slideId].elements["image-N"]`
4. Every `icon-N` in `content.iconElements` → has entry in `changelog.slides[icon.slideId].elements["icon-N"]`
5. Every `chart-N` in `content.chartElements` → has entry in `changelog.slides[chart.slideId].elements["chart-N"]`
6. Every `table-N` in `content.tableElements` → has entry in `changelog.slides[table.slideId].elements["table-N"]`
7. No orphan entries in changelog (entry exists but no matching content record)

## The slideId rule

The `slideId` field inside every changelog entry must equal the key it lives under:

```python
# CORRECT
changelog["slides"]["slide-2"]["elements"]["shape-7"] = {
    "slideId": "slide-2",   # matches the parent key
    ...
}

# WRONG — slideId doesn't match parent
changelog["slides"]["slide-1"]["elements"]["shape-7"] = {
    "slideId": "slide-2",   # mismatch! validator will catch this
    ...
}
```

## Builder pattern — keep content and changelog in sync

The safest pattern is to build both records together using a helper, then
immediately register both:

```python
# Build both records together
c_record, cl_record = make_text("text-1", "slide-1", "Hello", "title",
                                  x=48, y=48, w=800, h=80, zidx=nextz(), now=NOW)

# Register content record
text_elements_by_slide["slide-1"].append(c_record)

# Register changelog record — SAME LINE as content, never separated
changelog_slides["slide-1"]["elements"]["text-1"] = cl_record
```

Never add a content record and then "come back later" to add the changelog entry —
that's how they get out of sync.

## Common mistakes caught by the validator

- Text element exists in content but forgot to add to changelog → `text IDs in content but missing from changelog`
- Wrong slide key used for shape changelog entry → `shape slideId mismatch`
- Copied a shape block and forgot to update its slideId → duplicate entries under wrong slide
- Added a new element type at the end but forgot its changelog entry entirely
