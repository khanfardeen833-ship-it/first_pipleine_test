# Skill 05 — Icon Elements

## What this is
Icons are vector symbols from the Lucide icon library.
They live at the file level in `content.iconElements`.
The changelog entry is simple — just position, size, color, opacity.

## content record (inside `content.iconElements` array)

```json
{
  "id": "icon-28",
  "slideId": "slide-5",
  "groupId": null,
  "iconName": "AArrowDown",
  "iconSource": "lucide"
}
```

- `iconSource` is always `"lucide"`
- `iconName` must be a valid Lucide icon name in PascalCase

## changelog record (inside `changelog.slides[slideId].elements`)

```json
{
  "slideId": "slide-5",
  "position": { "x": 48, "y": 48 },
  "width": 80,
  "height": 80,
  "rotation": 0,
  "zIndex": 28,
  "color": "#c67c3a",
  "opacity": 1,
  "updatedAt": 1778668320399
}
```

## Commonly used Lucide icon names

Arrows & navigation: `ArrowRight`, `ArrowLeft`, `ArrowUp`, `ArrowDown`, `ChevronRight`, `ExternalLink`
Charts & data: `BarChart`, `BarChart2`, `LineChart`, `PieChart`, `TrendingUp`, `TrendingDown`
People & org: `User`, `Users`, `UserCheck`, `Building`, `Briefcase`
Communication: `Mail`, `MessageCircle`, `Phone`, `Bell`, `Send`
Files & content: `FileText`, `Folder`, `BookOpen`, `Clipboard`, `Download`
Status & feedback: `Check`, `CheckCircle`, `XCircle`, `AlertTriangle`, `Info`, `Star`
Tech: `Globe`, `Cpu`, `Database`, `Cloud`, `Lock`, `Settings`, `Zap`
Misc: `Heart`, `Lightbulb`, `Target`, `Award`, `Clock`, `Calendar`, `Search`

## Rules & gotchas

- `width` and `height` should be equal (icons are square) — typical sizes: `48`, `64`, `80`, `96`
- `color` is a hex string — icons render as a single flat color
- Keep `opacity` at `1` unless you want a ghost/watermark effect
- Icons work great in rows — space them evenly across a slide for a feature list layout
- `zIndex` must be globally unique — see `09-zindex-rules.md`

## Helper function

```python
def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=80, color="#c67c3a", opacity=1):
    content_record = {
        "id": icon_id, "slideId": slide_id, "groupId": None,
        "iconName": icon_name, "iconSource": "lucide"
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": size, "height": size, "rotation": 0,
        "zIndex": zidx, "color": color, "opacity": opacity,
        "updatedAt": now
    }
    return content_record, changelog_record
```
