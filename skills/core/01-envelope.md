# Skill 01 — Presentation Envelope

## What this is
The top-level wrapper for every Bildory export. Every generated JSON must start here.
Read this file first before building any deck.

## Schema

```json
{
  "exportedAt": 1778924967244,
  "presentation": {
    "_id": "generated-id",
    "title": "Your Deck Title",
    "description": "",
    "thumbnailUrl": null,
    "isPublic": false,
    "slideCount": 6,
    "elementCount": 35,
    "createdAt": "2026-01-01T00:00:00.000Z",
    "updatedAt": "2026-01-01T00:00:00.000Z",
    "s3Key": null,
    "s3Url": null
  },
  "files": {
    "content": { },
    "baseLayout": { },
    "changelog": { }
  }
}
```

## Rules & gotchas

- `exportedAt` is a Unix timestamp in **milliseconds** — use `int(time.time() * 1000)`
- `slideCount` must exactly equal `len(files.content.slides)` — validate this before saving
- `elementCount` must equal the **total** of all elements across all types:
  - text elements (sum across all slides)
  - imageElements, shapeElements, chartElements, tableElements, iconElements, embedElements, smartDiagramElements, groupElements
  - Getting this wrong will fail validation
- `_id` can be any unique string — use a timestamp-based slug like `"deck-1778924967244"`
- `s3Key` and `s3Url` should be `null` for generated decks

## baseLayout structure

```json
{
  "version": "v1",
  "slides": [
    {
      "id": "slide-1",
      "layoutId": "blank-canvas",
      "imageElements": [],
      "shapeElements": [],
      "chartElements": [],
      "iconElements": [],
      "embedElements": []
    }
  ],
  "imageElements": [],
  "shapeElements": [],
  "chartElements": [],
  "iconElements": [],
  "embedElements": []
}
```

- `version` must be exactly `"v1"` — not `"1"`, not `1`
- Every slide in `content.slides` must have a matching entry in `baseLayout.slides` with the same `id`, in the same order
- All array fields in each baseLayout slide must exist and be empty `[]`
- The file-level arrays (`imageElements`, `shapeElements`, etc.) must also exist and be empty

## content structure

```json
{
  "slides": [
    {
      "id": "slide-1",
      "order": 0,
      "layoutId": "blank-canvas",
      "backgroundColor": "#ffffff",
      "textElements": []
    }
  ],
  "imageElements": [],
  "shapeElements": [],
  "chartElements": [],
  "tableElements": [],
  "iconElements": [],
  "embedElements": [],
  "smartDiagramElements": [],
  "groupElements": []
}
```

- `order` is zero-indexed and must match the array index exactly
- `textElements` live **inside** each slide object
- All other element types live at the **file level** (not inside slides) — they carry a `slideId` field instead
- `tableElements` exists in `content` but NOT in `baseLayout` — that's intentional

## changelog structure

```json
{
  "version": "2.0",
  "slides": {
    "slide-1": {
      "elements": {
        "text-1": { },
        "shape-7": { }
      }
    }
  }
}
```

- `version` must be exactly `"2.0"` — not `2`, not `"2"`
- `slides` is an **object** (keyed by slide ID), not an array
- Every slide that exists in `content` must have an entry here
- See `08-changelog-sync.md` for the full sync rules
