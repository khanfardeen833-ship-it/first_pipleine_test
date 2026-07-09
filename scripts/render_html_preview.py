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
# Vendored ECharts — inlined into the preview so charts paint offline (headless
# QA screenshots have no reliable network for a CDN). Falls back to the CDN if
# the package isn't installed (`npm install echarts`).
ECHARTS_MIN_JS = ROOT / "node_modules" / "echarts" / "dist" / "echarts.min.js"

# The editor's 16 named filters. Kept byte-for-byte in sync with the editor's
# frontend/src/elements/image/configs/imagePresets.js (IMAGE_FILTERS) so this
# preview renders images exactly as the editor will after Import JSON.
FILTER_CSS = {
    "none": "none",
    "noir": "grayscale(1) contrast(1.4) brightness(0.85)",
    "gray": "grayscale(1)",
    "sepia": "sepia(1)",
    "vintage": "sepia(0.5) contrast(0.85) brightness(1.1) saturate(0.8)",
    "warm": "sepia(0.25) saturate(1.3) brightness(1.05) hue-rotate(-10deg)",
    "cool": "saturate(0.85) hue-rotate(195deg) brightness(1.08)",
    # editor key is "cross"; keep the legacy "crossprocess" alias pointing at it
    "cross": "saturate(1.6) hue-rotate(15deg) contrast(1.15) brightness(1.05)",
    "crossprocess": "saturate(1.6) hue-rotate(15deg) contrast(1.15) brightness(1.05)",
    "bright": "brightness(1.3) contrast(1.05) saturate(1.1)",
    "dark": "brightness(0.65) contrast(1.15)",
    "faded": "brightness(1.1) saturate(0.65) contrast(0.82)",
    "matte": "contrast(0.88) brightness(1.12) saturate(0.75)",
    "dynamic": "contrast(1.3) saturate(1.4) brightness(1.05)",
    "vibrant": "saturate(1.9) contrast(1.12) brightness(1.05)",
    "dramatic": "contrast(1.55) brightness(0.88) saturate(1.25)",
    "soft": "brightness(1.15) contrast(0.88) saturate(0.9)",
}

# Decorative frames — kept in sync with the editor's buildSpecialBorderStyle()
# in frontend/src/elements/image/configs/imagePresets.js.
SPECIAL_FRAME_CSS = {
    "thin-frame": "border:3px solid #fff; outline:1.5px solid #ccc;",
    "double-frame": "border:4px double #999;",
    "polaroid": ("border-top:8px solid #fff; border-left:8px solid #fff; "
                 "border-right:8px solid #fff; border-bottom:28px solid #fff; "
                 "box-shadow:0 2px 8px rgba(0,0,0,.18);"),
    "film": "border:6px solid #111; border-radius:0;",
    "rounded-white": "border:10px solid #fff; border-radius:16px; box-shadow:0 0 0 1.5px #ddd;",
    "inner-shadow": "",  # handled via inset shadow class
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
    """filter:drop-shadow(...) — a byte-for-byte port of the editor's
    buildShadowCSS() (imagePresets.js: offX=sin·dist, offY=-cos·dist, and a
    second soft drop-shadow when size>0), so previewed image shadows land in the
    same place and shape as the editor renders after Import JSON. Returns a
    full `filter:...;` declaration (applied on the outer wrapper), or ""."""
    if not sh or not sh.get("enabled"):
        return ""
    ang = math.radians(sh.get("angle", 135))
    dist = sh.get("distance", 8)
    off_x = round(math.sin(ang) * dist)
    off_y = round(-math.cos(ang) * dist)
    color = sh.get("color", "#000000")
    r = int(color[1:3], 16) if color.startswith("#") else 0
    g = int(color[3:5], 16) if color.startswith("#") else 0
    b = int(color[5:7], 16) if color.startswith("#") else 0
    al = sh.get("opacity", 40) / 100
    blur = sh.get("blur", 12)
    main = f"drop-shadow({off_x}px {off_y}px {blur}px rgba({r},{g},{b},{al:.2f}))"
    size = sh.get("size", 0) or 0
    if size > 0:
        size_blur = round(size * 0.8)
        size_al = min(1.0, al * 0.6)
        return f"filter:{main} drop-shadow(0px 0px {size_blur}px rgba({r},{g},{b},{size_al:.2f}));"
    return f"filter:{main};"


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

    inset = ('<div style="position:absolute;inset:0;box-shadow:inset 0 0 20px rgba(0,0,0,0.45);'
             f'border-radius:{radius}"></div>'
             if border.get("specialStyle") == "inner-shadow" else "")

    # Two-div layout mirrors the editor's ImageElement: the OUTER div carries
    # the drop-shadow filter (so it follows the clipped shape and isn't clipped
    # away), the INNER div does overflow-clip + border/frame + flip. The colour
    # filter + blur stay on the <img>.
    rot = f"transform:rotate({el.get('rotation', 0)}deg);" if el.get("rotation") else ""
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'z-index:{el.get("zIndex", 0)};opacity:{el.get("opacity", 1)};'
        f'{rot}{shadow_css(el.get("shadow"))}">'
        f'<div style="position:relative;width:100%;height:100%;overflow:hidden;'
        f'border-radius:{radius};{bcss}{flip}">'
        f'<img src="{esc(src)}" style="width:100%;height:100%;'
        f'object-fit:{el.get("objectFit", "cover")};'
        f'object-position:{fp.get("x", 50)}% {fp.get("y", 50)}%;'
        f'filter:{filt};">'
        f"{overlay_html}{inset}</div></div>"
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
    # Element-level opacity — the editor applies it on the element wrapper for
    # every type (CanvasElement), so read it off the element, not the style.
    opacity = el.get("opacity", st.get("opacity", 1))
    op_css = f"opacity:{opacity};" if opacity != 1 else ""
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{el["width"]}px;'
        f'min-height:{el["height"]}px;z-index:{el.get("zIndex", 0)};white-space:pre-wrap;'
        f"{op_css}{rot}{css}\">{esc(content)}</div>"
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


def render_chart(el, rec, idx, slide_bg="#ffffff"):
    x, y = el["position"]["x"], el["position"]["y"]
    if rec.get("svgDataUrl"):
        return (f'<img src="{esc(rec["svgDataUrl"])}" style="position:absolute;left:{x}px;'
                f'top:{y}px;width:{el["width"]}px;height:{el["height"]}px;'
                f'z-index:{el.get("zIndex", 0)}">')
    cfg = rec.get("chartConfig", {})
    ctype = el.get("chartType") or rec.get("chartType", "bar")
    div_id = f"chart-{idx}"
    # Dark mode if the config says so, or if the chart sits on a dark slide. When
    # dark, the JS forces a light text/axis color so titles & labels stay legible
    # (the model often omits axis/title colors, leaving ECharts' near-black default).
    cfg_bg = cfg.get("backgroundColor")
    panel = cfg_bg if (cfg_bg and cfg_bg != "transparent") else slide_bg
    is_dark = bool(cfg.get("isDarkMode")) or not _is_light_hex(panel)
    text_color = cfg.get("textColor") or ("#F5F7FA" if is_dark else "#1c1917")
    payload = json.dumps({"type": ctype, "config": cfg,
                          "dark": is_dark, "textColor": text_color})
    return (
        f'<div id="{div_id}" data-chart=\'{payload.replace("&", "&amp;").replace(chr(39), "&#39;")}\' '
        f'style="position:absolute;left:{x}px;top:{y}px;width:{el["width"]}px;'
        f'height:{el["height"]}px;z-index:{el.get("zIndex", 0)}"></div>'
    )


def _is_light_hex(h):
    """Perceived-luminance test — pick dark/light table chrome for legibility."""
    h = (h or "").lstrip("#")
    if len(h) != 6:
        return True
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) > 140


def render_table(el, rec):
    x, y = el["position"]["x"], el["position"]["y"]
    cells = rec.get("cells", {})
    if not cells:
        return ""
    rows = max(int(k.split("-")[0]) for k in cells) + 1
    cols = max(int(k.split("-")[1]) for k in cells) + 1

    # Honor the deck's table styling (it carries dark-mode colors). Defaulting to
    # black-on-white made light-on-dark tables render as invisible black text.
    text_color = rec.get("tableColor") or "#1c1917"
    bg_color = rec.get("tableBg") or "#ffffff"
    font_size = rec.get("tableFontSize") or 18
    col_widths = rec.get("colWidths") or []
    row_heights = rec.get("rowHeights") or []
    light_bg = _is_light_hex(bg_color)
    border = "#d9dde3" if light_bg else "#3a3f4a"
    header_fill = "#1c1917" if light_bg else "#3E7BFA"

    def cell_text(v):
        return v.get("text", "") if isinstance(v, dict) else (v or "")

    trs = []
    for r in range(rows):
        is_header = r == 0
        rh = f"height:{row_heights[r]}px;" if r < len(row_heights) else ""
        fill = header_fill if is_header else bg_color
        color = "#ffffff" if is_header else text_color
        weight = "700" if is_header else "400"
        tds = "".join(
            f'<td style="border:1px solid {border};padding:0 14px;{rh}'
            f'background:{fill};color:{color};font-weight:{weight};'
            f'vertical-align:middle">{esc(cell_text(cells.get(f"{r}-{c}", "")).strip())}</td>'
            for c in range(cols)
        )
        trs.append(f'<tr>{tds}</tr>')

    col_group = "".join(f'<col style="width:{w}px">' for w in col_widths)
    width = el.get("width") or sum(col_widths) or 600
    return (
        f'<table style="position:absolute;left:{x}px;top:{y}px;width:{width}px;'
        f'z-index:{el.get("zIndex", 0)};border-collapse:collapse;table-layout:fixed;'
        f'background:{bg_color};font-family:Trebuchet MS;font-size:{font_size}px">'
        f'{col_group}{"".join(trs)}</table>'
    )


def main(json_path):
    deck = json.loads(Path(json_path).read_text(encoding="utf-8"))
    files = deck["files"]
    content, changelog = files["content"], files["changelog"]

    # Local image cache (core/image_cache.py): rewrite remote srcs to the
    # cached copies in images/ so previews/screenshots skip the network.
    manifest_path = Path(json_path).parent / "images" / "manifest.json"
    img_manifest = (json.loads(manifest_path.read_text(encoding="utf-8"))
                    if manifest_path.exists() else {})

    def local_src(src):
        return f"images/{img_manifest[src]}" if src in img_manifest else src

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
        bg = s.get("backgroundColor", "#ffffff")
        for eid, el in sorted(els.items(), key=lambda kv: kv[1].get("zIndex", 0)):
            rec = by_id.get(eid, {})
            if eid.startswith("image"):
                parts.append(render_image(el, local_src(rec.get("src", ""))))
            elif eid.startswith("text"):
                parts.append(render_text(el, rec.get("content", "")))
            elif eid.startswith("shape"):
                parts.append(render_shape(el))
            elif eid.startswith("icon"):
                parts.append(render_icon(el, rec.get("iconName", "Circle")))
            elif eid.startswith("chart"):
                chart_idx += 1
                parts.append(render_chart(el, rec, chart_idx, slide_bg=bg))
            elif eid.startswith("table"):
                parts.append(render_table(el, {**rec, **el}))
        slides_html.append(
            f'<div class="slide-label">{sid}</div>'
            f'<div class="slide" style="background:{bg}">{"".join(parts)}</div>'
        )

    title = deck.get("presentation", {}).get("title", "Deck Preview")
    if ECHARTS_MIN_JS.exists():
        echarts_tag = "<script>" + ECHARTS_MIN_JS.read_text(encoding="utf-8") + "</script>"
    else:
        echarts_tag = ('<script src="https://cdn.jsdelivr.net/npm/'
                       'echarts@5/dist/echarts.min.js"></script>')
    out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{esc(title)} — preview</title>
{echarts_tag}
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
    if (typeof echarts === 'undefined' || !div.clientWidth) return;
    var spec = JSON.parse(div.getAttribute('data-chart'));
    var cfg = spec.config || {{}}, opt;
    if (cfg.series) {{
      // Native ECharts option (current generator output: series + xAxis/yAxis).
      // Use it directly — the legacy cfg.data transform below never populated
      // it, which is why these charts rendered blank.
      opt = cfg;
      opt.animation = false;
      if (!opt.grid) opt.grid = {{ left:50, right:20, top:20, bottom:30, containLabel:true }};
    }} else {{
      // Legacy simplified shape: {{ data:[{{name,values,labels}}], ... }}
      var series = [], labels = [];
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
      opt = {{ animation:false,
        title: cfg.showTitle ? {{ text:cfg.title, left:'center',
          textStyle:{{ fontSize:16, fontFamily:'Trebuchet MS' }} }} : undefined,
        grid: {{ left:50, right:20, top:cfg.showTitle ? 48 : 20, bottom:30, containLabel:true }},
        series: series }};
      if (spec.type !== 'pie' && spec.type !== 'doughnut') {{
        opt.xAxis = {{ type:'category', data:labels }};
        opt.yAxis = {{ type:'value' }};
      }}
    }}
    // Force legible text on dark backgrounds — the model often omits axis/title
    // colors, so ECharts falls back to near-black, invisible on a dark slide.
    if (spec.dark) {{
      var tc = spec.textColor || '#F5F7FA';
      var line = 'rgba(245,247,250,0.25)';
      opt.textStyle = Object.assign({{ color: tc }}, opt.textStyle || {{}});
      if (opt.title) {{
        opt.title.textStyle = Object.assign({{ color: tc }}, opt.title.textStyle || {{}});
      }}
      if (opt.legend) {{
        opt.legend.textStyle = Object.assign({{ color: tc }}, opt.legend.textStyle || {{}});
      }}
      ['xAxis', 'yAxis'].forEach(function (ax) {{
        var arr = Array.isArray(opt[ax]) ? opt[ax] : (opt[ax] ? [opt[ax]] : []);
        arr.forEach(function (a) {{
          a.axisLabel = Object.assign({{ color: tc }}, a.axisLabel || {{}});
          a.axisLine = a.axisLine || {{}};
          a.axisLine.lineStyle = Object.assign({{ color: line }}, a.axisLine.lineStyle || {{}});
          a.splitLine = a.splitLine || {{}};
          a.splitLine.lineStyle = Object.assign({{ color: line }}, a.splitLine.lineStyle || {{}});
        }});
      }});
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
