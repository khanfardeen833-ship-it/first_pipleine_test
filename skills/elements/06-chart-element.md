# Skill 06 — Chart Elements

## What this is
Charts are ECharts-powered visualizations. The content record is minimal;
the full chart configuration lives in `content.chartElements[i].chartConfig`.
The changelog entry is also minimal — just position, size, zIndex, and chartType.

## content record (inside `content.chartElements` array)

```json
{
  "id": "chart-32",
  "slideId": "slide-6",
  "groupId": null,
  "svgDataUrl": "",
  "chartType": "nightingale",
  "chartConfig": { }
}
```

- `svgDataUrl` is always `""`
- `chartType` must match the type used inside `chartConfig`

## changelog record (inside `changelog.slides[slideId].elements`)

```json
{
  "slideId": "slide-6",
  "position": { "x": 48, "y": 48 },
  "width": 560,
  "height": 400,
  "rotation": 0,
  "zIndex": 32,
  "updatedAt": 1778924967244,
  "chartType": "nightingale"
}
```

Note: the changelog for charts is intentionally minimal — no chartConfig here.

## chartConfig — full structure

All chart configs share these top-level fields:

```json
{
  "tooltip": { "trigger": "item" },
  "series": [ ],
  "backgroundColor": "transparent",
  "color": ["#c67c3a", "#ca8746", "#cd9352"],
  "animation": false,
  "textStyle": {
    "color": "#1c1917",
    "fontSize": 16,
    "fontWeight": "normal",
    "fontStyle": "normal"
  },
  "tableData": { },
  "properties": {
    "showXAxis": true,
    "showYAxis": true,
    "showDataLabels": false,
    "showLegend": false,
    "showLabelName": true,
    "showLabelValue": false,
    "labelFontSize": 16,
    "labelBold": false,
    "labelItalic": false,
    "labelUnderline": false,
    "labelStrike": false
  },
  "activeColorScheme": null,
  "isDarkMode": false,
  "customSeriesColors": { "0": "#c67c3a", "1": "#ca8746" },
  "textColor": "#1c1917",
  "isMonochrome": false
}
```

## Chart types and their series config

### Bar chart (`"bar"`)
```json
{
  "xAxis": { "type": "category", "data": ["Jan", "Feb", "Mar"] },
  "yAxis": { "type": "value" },
  "series": [{ "type": "bar", "data": [120, 200, 150] }],
  "tableData": { "categories": ["Jan","Feb","Mar"], "series": [{"name":"Value","data":[120,200,150]}] }
}
```

### Line chart (`"line"`)
```json
{
  "xAxis": { "type": "category", "data": ["Q1", "Q2", "Q3", "Q4"] },
  "yAxis": { "type": "value" },
  "series": [{ "type": "line", "data": [820, 932, 901, 1290], "smooth": true }],
  "tableData": { "categories": ["Q1","Q2","Q3","Q4"], "series": [{"name":"Revenue","data":[820,932,901,1290]}] }
}
```

### Pie chart (`"pie"`)
```json
{
  "tooltip": { "trigger": "item", "formatter": "{b}: {c} ({d}%)" },
  "series": [{
    "type": "pie", "radius": ["0%", "70%"],
    "data": [{"value": 1048, "name": "A"}, {"value": 735, "name": "B"}],
    "label": { "show": true, "color": "#1c1917", "fontSize": 16 }
  }],
  "tableData": { "data": [{"value": 1048, "name": "A"}, {"value": 735, "name": "B"}] }
}
```

### Nightingale / rose chart (`"nightingale"`)
Same as pie but add `"roseType": "area"` to the series.

### Doughnut chart (`"doughnut"`)
Same as pie but set `"radius": ["40%", "70%"]`.

## Data integrity (READ THIS — bad data ruins the slide)

A chart compares values **on one shared axis**, so every number in a cartesian
(bar/line/area) chart MUST share the same unit and a comparable scale.

- **One unit per chart.** Never mix percentages, dollars, counts, and durations in
  the same bar/line series. `["34% labor cut", "2.1 yr payback", "87% fewer
  mis-picks", "210 throughput"]` is FOUR different units — that is not a chart, it
  is four unrelated stats. Render those as stat cards (number + label), not a chart.
- **No negative values to mean "a reduction."** "34% lower cost" is the value `34`
  (a magnitude), not `-34`. Only use negatives for genuine below-zero data
  (e.g. net change, temperature).
- **Comparable scale.** If one value is `2.1` and another is `210` in the same
  series, the small bars vanish. Split into separate charts, use a second yAxis,
  or switch to stat cards.
- **A chart needs ≥3 comparable data points** that tell a trend or comparison
  story. For 1–3 unrelated KPIs, use stat cards instead — they read better.
- `xAxis.data` length MUST equal each `series[i].data` length.

## Rules & gotchas

- `tableData` must be kept in sync with `series.data` — they represent the same data in two formats
- `backgroundColor` must be `"transparent"` — never a solid color
- `animation` must be `false`
- `isDarkMode`: set to `true` only if the slide background is dark (e.g. `#1c1917`)
- `customSeriesColors` keys are zero-indexed strings: `"0"`, `"1"`, `"2"` — not integers
- Recommended chart size: minimum `400×300`, ideal `560×400`

## Helper function

```python
def make_chart(chart_id, slide_id, chart_type, x, y, w, h, zidx, now, chart_config):
    content_record = {
        "id": chart_id, "slideId": slide_id, "groupId": None,
        "svgDataUrl": "", "chartType": chart_type,
        "chartConfig": chart_config
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "updatedAt": now,
        "chartType": chart_type
    }
    return content_record, changelog_record
```
