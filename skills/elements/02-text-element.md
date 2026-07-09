# Skill 02 — Text Elements

## What this is
Text is the most common element. There are 6 types with distinct font sizes and weights.
Text elements are split across TWO places: a minimal record in `content.slides[i].textElements`
and the full styled record in `changelog.slides[slideId].elements`.

## The 6 text types — font defaults

| type        | fontSize | fontWeight | lineHeight |
|-------------|----------|------------|------------|
| title       | 60       | 700        | 1.05       |
| subtitle    | 40       | 600        | 1.35       |
| heading     | 32       | 600        | 1.30       |
| subheading  | 26       | 600        | 1.30       |
| paragraph   | 22       | 700        | 1.50       |
| caption     | 18       | 600        | 1.30       |

## content record (inside `content.slides[i].textElements`)

```json
{
  "id": "text-1",
  "content": "Your text here",
  "type": "title",
  "originalType": "title",
  "groupId": null,
  "formattedContent": "Your text here"
}
```

- `content` and `formattedContent` must be **identical strings**
- `type` and `originalType` must be **identical**
- Valid types: `title`, `subtitle`, `heading`, `subheading`, `paragraph`, `caption`
- `groupId` is `null` unless the element is in a group

## changelog record (inside `changelog.slides[slideId].elements`)

```json
{
  "slideId": "slide-1",
  "position": { "x": 48, "y": 48 },
  "width": 800,
  "height": 80,
  "rotation": 0,
  "zIndex": 1,
  "style": {
    "fontSize": 60,
    "fontFamily": "Space Grotesk",
    "color": "#1c1917",
    "textAlign": "left",
    "lineHeight": 1.05,
    "letterSpacing": 0,
    "fontWeight": 700,
    "fontStyle": "normal",
    "textDecoration": "none",
    "textTransform": "none",
    "isCode": false,
    "listStyle": "none",
    "link": "",
    "backgroundColor": "transparent",
    "background": "none",
    "WebkitBackgroundClip": "unset",
    "WebkitTextFillColor": "unset",
    "backgroundClip": "unset",
    "listLevel": 1,
    "paragraphSpacingBefore": 0,
    "paragraphSpacingAfter": 0,
    "textOutlineColor": "#000000",
    "textOutlineWidth": 0,
    "textTransformEffect": "none",
    "textTransformRadius": 220,
    "textVerticalAlign": "baseline",
    "curveEnabled": false,
    "curveValue": 26,
    "shadowType": "none",
    "shadowOffset": 22,
    "shadowDirection": -45,
    "shadowBlur": 0,
    "shadowTransparency": 40,
    "shadowColor": "#000000"
  },
  "formattedContent": "Your text here",
  "animation": {
    "enter": "none",
    "exit": "fade",
    "duration": 550,
    "delay": 0,
    "trigger": "both",
    "typewriterMode": "character"
  },
  "enterAnimation": "none",
  "exitAnimation": "fade",
  "animationEffect": "none",
  "animationDurationMs": 550,
  "animationDelayMs": 0,
  "animationTrigger": "both",
  "animationTypewriterMode": "character",
  "updatedAt": 1778924967244
}
```

## Rules & gotchas

- DO NOT omit any style field — all 27 style fields are required even if default
- `formattedContent` in the changelog entry must match the `content` field in the content record
- `zIndex` must be globally unique across the entire deck — see `09-zindex-rules.md`
- `updatedAt` — use the same millisecond timestamp as `exportedAt`
- Animation fields are duplicated at two levels (inside `animation` object AND as flat fields) — include both
- `position.x` minimum is 48 (safe zone), `position.y` minimum is 48

## Helper function for building text elements

```python
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None):
    DEFAULTS = {
        "title":      (60, 700, 1.05),
        "subtitle":   (40, 600, 1.35),
        "heading":    (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph":  (22, 700, 1.50),
        "caption":    (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None:   fs = font_size
    if font_weight is not None: fw = font_weight
    if line_height is not None: lh = line_height

    content_record = {
        "id": text_id, "content": text, "type": type_,
        "originalType": type_, "groupId": None, "formattedContent": text
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0, "zIndex": zidx,
        "style": {
            "fontSize": fs, "fontFamily": "Space Grotesk", "color": color,
            "textAlign": "left", "lineHeight": lh, "letterSpacing": 0,
            "fontWeight": fw, "fontStyle": "normal", "textDecoration": "none",
            "textTransform": "none", "isCode": False, "listStyle": "none",
            "link": "", "backgroundColor": "transparent", "background": "none",
            "WebkitBackgroundClip": "unset", "WebkitTextFillColor": "unset",
            "backgroundClip": "unset", "listLevel": 1,
            "paragraphSpacingBefore": 0, "paragraphSpacingAfter": 0,
            "textOutlineColor": "#000000", "textOutlineWidth": 0,
            "textTransformEffect": "none", "textTransformRadius": 220,
            "textVerticalAlign": "baseline", "curveEnabled": False,
            "curveValue": 26, "shadowType": "none", "shadowOffset": 22,
            "shadowDirection": -45, "shadowBlur": 0,
            "shadowTransparency": 40, "shadowColor": "#000000"
        },
        "formattedContent": text,
        "animation": {"enter": "none", "exit": "fade", "duration": 550,
                      "delay": 0, "trigger": "both", "typewriterMode": "character"},
        "enterAnimation": "none", "exitAnimation": "fade",
        "animationEffect": "none", "animationDurationMs": 550,
        "animationDelayMs": 0, "animationTrigger": "both",
        "animationTypewriterMode": "character", "updatedAt": now
    }
    return content_record, changelog_record
```
