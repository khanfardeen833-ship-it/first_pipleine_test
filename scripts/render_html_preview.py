"""
Render a merged_deck.json into a single standalone preview.html that mimics
the bildory editor's rendering — including image features the PPTX exporter
doesn't map yet (ellipse crop, CSS filters, blend-mode overlays, focusPoint,
flips, special frames).

Usage:
    python scripts/render_html_preview.py workspace/<run>/merged_deck.json
    -> writes preview.html next to the JSON
"""

import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUCIDE_DIR = ROOT / "node_modules" / "lucide-static" / "icons"

# CSS approximations of the editor's 16 named filters
FILTER_CSS = {
    "none": "none",
    "noir": "grayscale(1) contrast(1.3) brightness(0.9)",
    "gray": "grayscale(1)",
    "sepia": "sepia(0.8)",
    "vintage": "sepia(0.4) saturate(0.8) contrast(0.9) brightness(1.05)",
    "warm": "sepia(0.25) saturate(1.25) brightness(1.05) hue-rotate(-10deg)",
    "cool": "saturate(1.1) brightness(1.02) hue-rotate(12deg)",
    "crossprocess": "saturate(1.4) contrast(1.2) hue-rotate(-15deg)",
    "bright": "brightness(1.25) saturate(1.05)",
    "dark": "brightness(0.7) contrast(1.05)",
    "faded": "saturate(0.65) brightness(1.1) contrast(0.85)",
    "matte": "contrast(0.9) brightness(1.05) saturate(0.9)",
    "dynamic": "contrast(1.25) saturate(1.2)",
    "vibrant": "saturate(1.5) contrast(1.1)",
    "dramatic": "contrast(1.4) brightness(0.85) saturate(1.1)",
    "soft": "contrast(0.85) brightness(1.08) saturate(0.95)",
}

SPECIAL_FRAME_CSS = {
    "thin-frame": "border:1px solid rgba(255,255,255,.9); outline:1px solid rgba(0,0,0,.25);",
    "double-frame": "border:6px double #ffffff;",
    "polaroid": "border:12px solid #fff; border-bottom-width:44px; box-shadow:0 8px 24px rgba(0,0,0,.35);",
    "film": "border:14px solid #111; box-shadow:0 6px 20px rgba(0,0,0,.4);",
    "rounded-white": "border:10px solid #fff; border-radius:18px;",
    "inner-shadow": "",  # handled via ::after inset shadow class
}


def esc(s):
    return html.escape(str(s if s is not None else ""))


def kebab(name):
    s = re.sub(r"(?<!^)(?=[A-Z0-9])", "-", name).lower()
    return re.sub(r"-+", "-", s)


def lucide_svg(name, color, size):
    for cand in (kebab(name), name.lower()):
        p = LUCIDE_DIR / f"{cand}.svg"
        if p.exists():
            svg = p.read_text(encoding="utf-8")
            svg = re.sub(r'width="\d+"', f'width="{size}"', svg, count=1)
            svg = re.sub(r'height="\d+"', f'height="{size}"', svg, count=1)
            return svg.replace('stroke="currentColor"', f'stroke="{color}"')
    return (f'<div style="width:{size}px;height:{size}px;border:2px solid {color};'
            f'border-radius:6px"></div>')


def shadow_css(sh):
    if not sh or not sh.get("enabled"):
        return ""
    ang = math.radians(sh.get("angle", 135))
    dist = sh.get("distance", 8)
    dx, dy = round(math.cos(ang) * dist, 1), round(math.sin(ang) * dist, 1)
    color = sh.get("color", "#000000")
    op = sh.get("opacity", 40) / 100
    r = int(color[1:3], 16) if color.startswith("#") else 0
    g = int(color[3:5], 16) if color.startswith("#") else 0
    b = int(color[5:7], 16) if color.startswith("#") else 0
    return (f"box-shadow:{dx}px {dy}px {sh.get('blur', 12)}px "
            f"{sh.get('size', 0)}px rgba({r},{g},{b},{op:.2f});")


def render_image(el, src):
    x, y = el["position"]["x"], el["position"]["y"]
    w, h = el["width"], el["height"]
    radius = "50%" if el.get("cropRatio") == "ellipse" else f"{el.get('borderRadius', 0)}px"
    fp = el.get("focusPoint") or {"x": 50, "y": 50}
    filt = FILTER_CSS.get(el.get("filter", "none"), "none")
    if el.get("blur", 0):
        filt = (filt if filt != "none" else "") + f" blur({el['blur']}px)"
    sx, sy = el.get("scaleX", 1), el.get("scaleY", 1)
    flip = f"transform:scale({sx},{sy});" if (sx, sy) != (1, 1) else ""

    border = el.get("border") or {}
    bcss = ""
    if border.get("type") == "standard":
        bcss = f"border:{border.get('width', 4)}px solid {border.get('color', '#000')};"
    elif border.get("type") == "special":
        bcss = SPECIAL_FRAME_CSS.get(border.get("specialStyle") or "", "")

    overlay_html = ""
    ov = el.get("overlay") or {}
    if ov.get("color") and ov.get("opacity", 0) > 0:
        overlay_html = (
            f'<div style="position:absolute;inset:0;background:{ov["color"]};'
            f'opacity:{ov["opacity"] / 100:.2f};mix-blend-mode:{ov.get("blendMode", "normal")};'
            f'border-radius:{radius}"></div>'
        )

    inset = ('<div style="position:absolute;inset:0;box-shadow:inset 0 0 24px rgba(0,0,0,.55);'
             f'border-radius:{radius}"></div>'
             if border.get("specialStyle") == "inner-shadow" else "")

    rot = f"rotate({el.get('rotation', 0)}deg)" if el.get("rotation") else ""
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'z-index:{el.get("zIndex", 0)};opacity:{el.get("opacity", 1)};border-radius:{radius};'
        f'overflow:hidden;{bcss}{shadow_css(el.get("shadow"))}'
        f'{f"transform:{rot};" if rot else ""}">'
        f'<img src="{esc(src)}" style="width:100%;height:100%;'
        f'object-fit:{el.get("objectFit", "cover")};'
        f'object-position:{fp.get("x", 50)}% {fp.get("y", 50)}%;'
        f'filter:{filt};{flip}">'
        f"{overlay_html}{inset}</div>"
    )


def render_text(el, content):
    st = el.get("style") or {}
    x, y = el["position"]["x"], el["position"]["y"]
    rot = f"transform:rotate({el.get('rotation', 0)}deg);" if el.get("rotation") else ""
    css = (
        f"font-size:{st.get('fontSize', 22)}px;"
        f"font-family:'{st.get('fontFamily', 'Trebuchet MS')}',sans-serif;"
        f"color:{st.get('color', '#000')};text-align:{st.get('textAlign', 'left')};"
        f"line-height:{st.get('lineHeight', 1.3)};"
        f"letter-spacing:{st.get('letterSpacing', 0)}px;"
        f"font-weight:{st.get('fontWeight', 400)};font-style:{st.get('fontStyle', 'normal')};"
        f"text-decoration:{st.get('textDecoration', 'none')};"
        f"text-transform:{st.get('textTransform', 'none')};"
    )
    if st.get("backgroundColor") not in (None, "", "transparent"):
        css += f"background:{st['backgroundColor']};"
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{el["width"]}px;'
        f'min-height:{el["height"]}px;z-index:{el.get("zIndex", 0)};white-space:pre-wrap;'
        f"{rot}{css}\">{esc(content)}</div>"
    )


def render_shape(el):
    x, y = el["position"]["x"], el["position"]["y"]
    w, h = el["width"], el["height"]
    kind = el.get("shapeType", "rectangle")
    radius = "50%" if kind in ("circle", "ellipse") else "0"
    fill = el.get("fill", "#000")
    stroke = f"border:{el['strokeWidth']}px solid {el.get('stroke', fill)};" \
        if el.get("strokeWidth") else ""
    rot = f"transform:rotate({el.get('rotation', 0)}deg);" if el.get("rotation") else ""
    if kind == "line":
        h = max(h, el.get("strokeWidth", 2))
        return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'background:{el.get("stroke", fill)};z-index:{el.get("zIndex", 0)};'
                f'opacity:{el.get("opacity", 1)};{rot}"></div>')
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'background:{fill};{stroke}border-radius:{radius};z-index:{el.get("zIndex", 0)};'
        f'opacity:{el.get("opacity", 1)};{rot}"></div>'
    )


def render_icon(el, name):
    x, y = el["position"]["x"], el["position"]["y"]
    size = el.get("width", 24)
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;z-index:{el.get("zIndex", 0)};'
        f'opacity:{el.get("opacity", 1)}">'
        f'{lucide_svg(name, el.get("color", "#000"), size)}</div>'
    )


def render_chart(el, rec, idx):
    x, y = el["position"]["x"], el["position"]["y"]
    if rec.get("svgDataUrl"):
        return (f'<img src="{esc(rec["svgDataUrl"])}" style="position:absolute;left:{x}px;'
                f'top:{y}px;width:{el["width"]}px;height:{el["height"]}px;'
                f'z-index:{el.get("zIndex", 0)}">')
    cfg = rec.get("chartConfig", {})
    ctype = el.get("chartType") or rec.get("chartType", "bar")
    div_id = f"chart-{idx}"
    payload = json.dumps({"type": ctype, "config": cfg})
    return (
        f'<div id="{div_id}" data-chart=\'{payload.replace("&", "&amp;").replace(chr(39), "&#39;")}\' '
        f'style="position:absolute;left:{x}px;top:{y}px;width:{el["width"]}px;'
        f'height:{el["height"]}px;z-index:{el.get("zIndex", 0)}"></div>'
    )


def render_table(el, rec):
    x, y = el["position"]["x"], el["position"]["y"]
    cells = rec.get("cells", {})
    if not cells:
        return ""
    rows = max(int(k.split("-")[0]) for k in cells) + 1
    cols = max(int(k.split("-")[1]) for k in cells) + 1
    trs = []
    for r in range(rows):
        tds = "".join(
            f'<td style="border:1px solid #ccc;padding:6px 10px">'
            f'{esc(cells.get(f"{r}-{c}", ""))}</td>'
            for c in range(cols)
        )
        trs.append(f"<tr>{tds}</tr>")
    width = el.get("width") or sum(rec.get("colWidths") or []) or 600
    return (
        f'<table style="position:absolute;left:{x}px;top:{y}px;width:{width}px;'
        f'z-index:{el.get("zIndex", 0)};border-collapse:collapse;'
        f'font:14px Trebuchet MS">{"".join(trs)}</table>'
    )


def main(json_path):
    deck = json.loads(Path(json_path).read_text(encoding="utf-8"))
    files = deck["files"]
    content, changelog = files["content"], files["changelog"]

    by_id = {}  # element id -> content record
    for coll in ("imageElements", "shapeElements", "chartElements",
                 "tableElements", "iconElements"):
        for rec in content.get(coll) or []:
            by_id[rec["id"]] = rec
    for s in content["slides"]:
        for rec in s.get("textElements") or []:
            by_id[rec["id"]] = rec

    slides_html, chart_idx = [], 0
    for s in sorted(content["slides"], key=lambda x: x.get("order", 0)):
        sid = s["id"]
        els = changelog["slides"].get(sid, {}).get("elements", {})
        parts = []
        for eid, el in sorted(els.items(), key=lambda kv: kv[1].get("zIndex", 0)):
            rec = by_id.get(eid, {})
            if eid.startswith("image"):
                parts.append(render_image(el, rec.get("src", "")))
            elif eid.startswith("text"):
                parts.append(render_text(el, rec.get("content", "")))
            elif eid.startswith("shape"):
                parts.append(render_shape(el))
            elif eid.startswith("icon"):
                parts.append(render_icon(el, rec.get("iconName", "Circle")))
            elif eid.startswith("chart"):
                chart_idx += 1
                parts.append(render_chart(el, rec, chart_idx))
            elif eid.startswith("table"):
                parts.append(render_table(el, {**rec, **el}))
        bg = s.get("backgroundColor", "#ffffff")
        slides_html.append(
            f'<div class="slide-label">{sid}</div>'
            f'<div class="slide" style="background:{bg}">{"".join(parts)}</div>'
        )

    title = deck.get("presentation", {}).get("title", "Deck Preview")
    out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{esc(title)} — preview</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  body {{ background:#0e0f12; margin:0; padding:32px 0; font-family:Trebuchet MS; }}
  h1 {{ color:#e7e9ee; text-align:center; font-size:20px; }}
  .scaler {{ width:1280px; margin:0 auto; transform-origin:top center; }}
  .slide {{ position:relative; width:1280px; height:720px; overflow:hidden;
           margin:0 auto 12px; box-shadow:0 12px 40px rgba(0,0,0,.5); }}
  .slide-label {{ color:#9aa3b2; font-size:13px; margin:28px auto 6px; width:1280px; }}
</style></head><body>
<h1>{esc(title)} — HTML render (editor-faithful: filters, overlays, ellipse crops)</h1>
<div class="scaler" id="scaler">{"".join(slides_html)}</div>
<script>
  function fit() {{
    var s = Math.min(1, (window.innerWidth - 48) / 1280);
    var el = document.getElementById('scaler');
    el.style.transform = 'scale(' + s + ')';
    document.body.style.height = el.getBoundingClientRect().height + 64 + 'px';
  }}
  window.addEventListener('resize', fit); fit();

  document.querySelectorAll('[data-chart]').forEach(function (div) {{
    var spec = JSON.parse(div.getAttribute('data-chart'));
    var cfg = spec.config, series = [], labels = [];
    (cfg.data || []).forEach(function (d) {{
      labels = d.labels || labels;
      var color = (cfg.customSeriesColors && cfg.customSeriesColors[String(series.length)])
                  || (cfg.color && cfg.color[series.length]);
      if (spec.type === 'pie' || spec.type === 'doughnut') {{
        series.push({{ type:'pie',
          radius: spec.type === 'doughnut' ? ['45%','70%'] : '70%',
          data: d.labels.map(function (l, i) {{ return {{ name:l, value:d.values[i] }}; }}) }});
      }} else {{
        series.push({{ name:d.name, type: spec.type === 'line' ? 'line' : 'bar',
          data:d.values, smooth:true,
          itemStyle: color ? {{ color: color }} : undefined,
          lineStyle: color ? {{ color: color }} : undefined }});
      }}
    }});
    var opt = {{ animation:false,
      title: cfg.showTitle ? {{ text:cfg.title, left:'center',
        textStyle:{{ fontSize:16, fontFamily:'Trebuchet MS' }} }} : undefined,
      grid: {{ left:50, right:20, top:cfg.showTitle ? 48 : 20, bottom:30 }},
      series: series }};
    if (spec.type !== 'pie' && spec.type !== 'doughnut') {{
      opt.xAxis = {{ type:'category', data:labels }};
      opt.yAxis = {{ type:'value' }};
    }}
    echarts.init(div).setOption(opt);
  }});
</script></body></html>"""

    out_path = Path(json_path).parent / "preview.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"wrote {out_path}  ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         "workspace/run-premium-1781181578872/merged_deck.json")
