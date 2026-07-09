# Shared deck_builder API

Use the provided `deck_builder.py` instead of recreating schema helpers.
The builder handles IDs, globally unique zIndex values, envelope structure,
content/changelog synchronization, slide counts, and element counts.
It does not choose layouts or styles. You retain full creative control.

```python
from deck_builder import Deck

deck = Deck("Deck title", id_offset=ID_OFFSET)
slide = deck.add_slide(slide_id="slide-1", background="#14204e")

slide.add_shape("rectangle", x=0, y=0, width=1280, height=720, fill="#14204e")
slide.add_title("A custom title", x=64, y=96, width=900, height=144,
                color="#ffffff", font_size=64)
slide.add_text("Supporting copy", type="paragraph", x=64, y=280,
               width=560, height=96, color="#ffffff", font_size=22)
slide.add_icon("Cpu", x=1040, y=80, size=96, color="#c67c3a")
slide.add_image(URL, x=672, y=240, width=560, height=360, border_radius=16)
chart_config = {
    "title": "Revenue Trend",
    "showTitle": True,
    "data": [
        {
            "name": "2024",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [45, 52, 38, 61]
        }
    ]
}
slide.add_chart("line", chart_config, x=672, y=240, width=560, height=360)

cells = {"0-0": "Header 1", "0-1": "Header 2", "1-0": "Data A", "1-1": "Data B"}
slide.add_table(cells, x=64, y=240, col_widths=[280, 280],
                row_heights=[64, 56, 56])

deck.save("deck.json")
```

Every primitive accepts explicit coordinates and visual properties. For unusual
properties, use `style={...}` on text or `changelog={...}` on any primitive.
Use `content={...}` on tables for additional content fields.

Important:
- Set `id_offset` to the batch offset from the batch constraint.
- Use the exact assigned slide IDs.
- Design every slide for its topic; do not rely on repetitive fixed templates.
- Do not copy builder internals into `build.py`.

## OMIT DEFAULTS — exact reference

The builder fills every default automatically. Passing a default value wastes
output tokens and slows generation. Only pass arguments that DIFFER from:

```
add_text:   color="#1c1917", font_family="Trebuchet MS", text_align="left",
            rotation=0, style=None, animation=None
            per-type (font_size / font_weight / line_height):
              title 60/700/1.05   subtitle 40/600/1.35   heading 32/600/1.30
              subheading 26/600/1.30   paragraph 22/700/1.50   caption 18/600/1.30
add_shape:  fill="#c67c3a", stroke=<same as fill>, stroke_width=0, opacity=1, rotation=0
add_icon:   size=64, color="#c67c3a", opacity=1, rotation=0
add_image:  is_background=False, border_radius=0, opacity=1, rotation=0,
            object_fit="cover", filter="none", blur=0, scale_x=1, scale_y=1,
            crop_ratio="free",
            crop_rect={"left": 0, "top": 0, "right": 0, "bottom": 0},
            focus_point={"x": 50, "y": 50},
            shadow={"enabled": False, "angle": 135, "color": "#000000",
                    "opacity": 40, "distance": 8, "blur": 12, "size": 0, "spread": 0},
            border={"type": "none", "width": 4, "color": "#000000", "specialStyle": None},
            overlay={"color": None, "opacity": 0, "blendMode": "normal"}
add_chart:  rotation=0
add_table:  font_size=20, table_color="#1c1917", table_bg="#ffffff",
            table_bold=False, table_italic=False, table_align="left"
```

Merge semantics when you DO change something:
- `style=`, `animation=`, `shadow=`, `border=`, `overlay=` are PARTIAL dicts —
  they merge over the defaults. Pass only the keys you change,
  e.g. `shadow={"enabled": True, "distance": 12}`.
- `crop_rect=` and `focus_point=` are NOT merged — if passed, pass the complete dict.
