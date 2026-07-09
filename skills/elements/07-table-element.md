# Skill 07 — Table Elements

## What this is
Tables are grid elements with keyed cells.
Unlike other elements, tables carry their position and zIndex in the **content** record,
not just in the changelog. They also appear in `content.tableElements` only —
there is no `tableElements` array in `baseLayout`.

## content record (inside `content.tableElements` array)

```json
{
  "id": "table-27",
  "slideId": "slide-4",
  "groupId": null,
  "type": "table",
  "position": {
    "x": 80,
    "y": 200
  },
  "zIndex": 27,
  "cells": {
    "0-0": { "text": "Header 1", "bold": true, "bg": "#1c1917", "color": "#ffffff" },
    "0-1": { "text": "Header 2", "bold": true, "bg": "#1c1917", "color": "#ffffff" },
    "1-0": { "text": "Row 1 Col 1", "bold": false, "bg": "#ffffff", "color": "#1c1917" },
    "1-1": { "text": "Row 1 Col 2", "bold": false, "bg": "#ffffff", "color": "#1c1917" }
  },
  "colWidths": [200, 200, 200],
  "rowHeights": [53, 53, 53],
  "tableFontSize": 20,
  "tableBold": false,
  "tableItalic": false,
  "tableAlign": "left",
  "tableColor": "#1c1917",
  "tableBg": "#ffffff"
}
```

## changelog record (inside `changelog.slides[slideId].elements`)

```json
{
  "slideId": "slide-4",
  "position": { "x": 80, "y": 200 },
  "zIndex": 27,
  "updatedAt": 1778924967244,
  "style": {
    "colWidths": [200, 200, 200],
    "rowHeights": [53, 53, 53]
  }
}
```

Note: the changelog for tables is minimal — position, zIndex, and the style sizing only.

## Cell key format

Cells are keyed as `"row-col"` (zero-indexed strings):
- `"0-0"` = row 0, col 0 (top-left)
- `"0-1"` = row 0, col 1
- `"1-0"` = row 1, col 0

Each cell object:
```json
{
  "text": "Cell content",
  "bold": false,
  "bg": "#ffffff",
  "color": "#1c1917"
}
```

## Rules & gotchas

- `position` and `zIndex` appear in BOTH the content record and the changelog — they must match
- `colWidths` length = number of columns; `rowHeights` length = number of rows
- Total table width = sum of `colWidths`. Keep it within the safe zone (max 1184px from x=48)
- Row 0 is conventionally the header row — style it with a dark background and light text
- `tableFontSize`: use `20` for standard, `16` for dense data, `24` for large display tables
- `cells` only needs entries for cells that have content or custom styling — empty cells can be omitted
- Tables do NOT appear in `baseLayout` — this is intentional

## Helper function

```python
def make_table(table_id, slide_id, x, y, zidx, now,
               col_widths, row_heights, cells,
               font_size=20, table_color="#1c1917", table_bg="#ffffff"):
    content_record = {
        "id": table_id, "slideId": slide_id, "groupId": None,
        "type": "table",
        "position": {"x": x, "y": y},
        "zIndex": zidx,
        "cells": cells,
        "colWidths": col_widths,
        "rowHeights": row_heights,
        "tableFontSize": font_size,
        "tableBold": False, "tableItalic": False,
        "tableAlign": "left",
        "tableColor": table_color, "tableBg": table_bg
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "zIndex": zidx,
        "updatedAt": now,
        "style": {"colWidths": col_widths, "rowHeights": row_heights}
    }
    return content_record, changelog_record
```
