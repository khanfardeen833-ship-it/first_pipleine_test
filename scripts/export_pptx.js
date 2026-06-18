/**
 * Convert decks.slides[] JSON → .pptx using PptxGenJS.
 * Usage: node scripts/export_pptx.js <merged_deck.json> <output.pptx>
 *
 * Coordinate system: our slides are 1280×720 px; pptxgenjs WIDE layout is
 * 13.33×7.5 inches. Scale = px / 96 → exact 1:1 at 96 DPI.
 */

'use strict';

const PptxGenJS = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// ── Image fetcher: downloads URL → base64 data URI ───────────────────────────
function fetchImageAsDataUri(url) {
  return new Promise((resolve, reject) => {
    const proto = url.startsWith('https') ? https : http;
    const req = proto.get(url, { timeout: 10000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        // follow one redirect
        return fetchImageAsDataUri(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      const contentType = res.headers['content-type'] || 'image/jpeg';
      const mimeType = contentType.split(';')[0].trim();
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        const b64 = Buffer.concat(chunks).toString('base64');
        resolve(`data:${mimeType};base64,${b64}`);
      });
      res.on('error', reject);
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error(`Timeout fetching ${url}`)); });
  });
}

// ── Coordinate helpers ────────────────────────────────────────────────────────
const px2in = (px) => Number((px / 96).toFixed(4));
const px2pt = (px) => Math.round(px * 0.75);
// Normalize any CSS color the generator emits into the 6-digit RGB hex (no '#')
// pptxgenjs requires. Handles #rgb, #rrggbb, rgb()/rgba() (alpha dropped — opacity
// is carried separately via `transparency`). Anything unparseable → black.
const hex = (color) => {
  const s = String(color || '').trim();
  const m = /^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)/i.exec(s);
  if (m) {
    return [m[1], m[2], m[3]]
      .map(n => Math.max(0, Math.min(255, Math.round(parseFloat(n)))).toString(16).padStart(2, '0'))
      .join('');
  }
  const h = s.replace(/^#/, '');
  if (/^[0-9a-f]{3}$/i.test(h)) return h.split('').map(c => c + c).join('');   // #abc → aabbcc
  if (/^[0-9a-f]{6}$/i.test(h)) return h;
  return '000000';
};
// Alpha channel of an rgba()/hsla() color as 0..1 (1 if none) — folded into
// pptxgenjs `transparency` so translucent captions keep their intended opacity.
const alphaOf = (color) => {
  const m = /^(?:rgba|hsla)\([^)]*,\s*([\d.]+)\s*\)$/i.exec(String(color || '').trim());
  return m ? Math.max(0, Math.min(1, parseFloat(m[1]))) : 1;
};
// Perceived-luminance test on a 6-digit hex (no '#') — used to pick dark/light
// table chrome so text stays legible on either background.
const isLightHex = (h) => {
  const m = /^([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(String(h || '').replace(/^#/, ''));
  if (!m) return true;
  const [r, g, b] = [m[1], m[2], m[3]].map(x => parseInt(x, 16));
  return (0.299 * r + 0.587 * g + 0.114 * b) > 140;
};

// ── Icon helpers ──────────────────────────────────────────────────────────────
const LUCIDE_DIR = path.join(__dirname, '..', 'node_modules', 'lucide-static', 'icons');

// Lucide renamed many icons in v0.4xx+. Map old names → new kebab names.
const ICON_ALIASES = {
  'alert-triangle':       'triangle-alert',
  'alert-circle':         'circle-alert',
  'alert-octagon':        'octagon-alert',
  'home':                 'house',
  'trash':                'trash-2',
  'tool':                 'wrench',
  'calendar-days':        'calendar',
  'sidebar-open':         'panel-left-open',
  'sidebar-close':        'panel-left-close',
  'arrow-circle-right':   'circle-arrow-right',
  'arrow-circle-left':    'circle-arrow-left',
  'arrow-circle-up':      'circle-arrow-up',
  'arrow-circle-down':    'circle-arrow-down',
  'eye-off':              'eye-closed',
  'loader':               'loader-circle',
  'help-circle':          'circle-question-mark',
  'circle-help':          'circle-question-mark',
  'question-mark':        'circle-question-mark',
  'help':                 'circle-question-mark',
  'x-circle':             'circle-x',
  'check-circle':         'circle-check',
  'check-circle-2':       'circle-check-big',
  'more-horizontal':      'ellipsis',
  'more-vertical':        'ellipsis-vertical',
};

function toKebab(name) {
  // Strip trailing "Icon" suffix some agents add (e.g. HandshakeIcon → handshake)
  const stripped = name.replace(/Icon$/, '');
  return stripped
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/([a-zA-Z])([0-9])/g, '$1-$2')   // Building2 → building-2
    .toLowerCase();
}

function loadIconDataUri(iconName, color) {
  let kebab = toKebab(iconName);
  kebab = ICON_ALIASES[kebab] || kebab;
  const svgPath = path.join(LUCIDE_DIR, `${kebab}.svg`);
  if (!fs.existsSync(svgPath)) {
    throw new Error(`Icon not found: ${kebab}.svg`);
  }
  let svg = fs.readFileSync(svgPath, 'utf8');
  // Apply the icon color — replace stroke="currentColor" and fill="currentColor"
  const c = color || '#000000';
  svg = svg.replace(/stroke="currentColor"/g, `stroke="${c}"`);
  svg = svg.replace(/fill="currentColor"/g, `fill="${c}"`);
  const b64 = Buffer.from(svg).toString('base64');
  return `data:image/svg+xml;base64,${b64}`;
}

// ── Shape type map ────────────────────────────────────────────────────────────
function getShapeType(pptx, shapeType) {
  const map = {
    rectangle: pptx.ShapeType.rect,
    rect:      pptx.ShapeType.rect,
    circle:    pptx.ShapeType.ellipse,
    ellipse:   pptx.ShapeType.ellipse,
    oval:      pptx.ShapeType.ellipse,
    line:      pptx.ShapeType.line,
    triangle:  pptx.ShapeType.triangle,
    diamond:   pptx.ShapeType.diamond,
    pentagon:  pptx.ShapeType.pentagon,
    hexagon:   pptx.ShapeType.hexagon,
    arrow:     pptx.ShapeType.rightArrow,
    rightarrow: pptx.ShapeType.rightArrow,
  };
  return map[(shapeType || 'rectangle').toLowerCase()] || pptx.ShapeType.rect;
}

// ── Render functions ──────────────────────────────────────────────────────────

function renderText(slide, el, changelogData) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 560;
  const height = changelogData?.height || 100;
  const style = changelogData?.style || {};

  const fontSize = style.fontSize || 22;
  const fontFamily = style.fontFamily || 'Trebuchet MS';
  const color = style.color || '#1c1917';
  const textAlign = style.textAlign || 'left';
  const fontWeight = style.fontWeight || 400;
  // Combine the style opacity with any alpha baked into an rgba() color string
  // (e.g. translucent captions) so neither is silently dropped.
  const opacity = (style.opacity ?? 1) * alphaOf(color);   // ghost glyphs live at 0.03-0.08
  const letterSpacing = style.letterSpacing || 0;

  slide.addText(el.content || '', {
    x: px2in(pos.x),
    y: px2in(pos.y),
    w: px2in(width),
    h: px2in(height),
    fontSize: px2pt(fontSize),
    fontFace: fontFamily,
    color: hex(color),
    transparency: opacity < 1 ? Math.round((1 - opacity) * 100) : undefined,
    align: textAlign === 'center' ? 'center' : textAlign === 'right' ? 'right' : 'left',
    bold: fontWeight >= 700,
    italic: style.fontStyle === 'italic',
    charSpacing: letterSpacing ? px2pt(letterSpacing) : undefined,
    margin: 0,
  });
}

function renderShape(pptx, slide, el, changelogData) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 100;
  const height = changelogData?.height || 100;
  const fill = changelogData?.fill || '#cccccc';
  const stroke = changelogData?.stroke || fill;
  const opacity = changelogData?.opacity ?? 1;
  const shapeType = changelogData?.shapeType || 'rectangle';

  slide.addShape(getShapeType(pptx, shapeType), {
    x: px2in(pos.x),
    y: px2in(pos.y),
    w: px2in(width),
    h: px2in(height),
    fill: { color: hex(fill), transparency: Math.round((1 - opacity) * 100) },
    line: { color: hex(stroke), width: 0 },
  });
}

function renderIcon(pptx, slide, el, changelogData) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 48;
  const height = changelogData?.height || 48;
  const color = changelogData?.color || changelogData?.style?.color || el.color || '#000000';
  const iconName = el.iconName || 'question-mark';

  try {
    const dataUri = loadIconDataUri(iconName, color);
    slide.addImage({
      data: dataUri,
      x: px2in(pos.x),
      y: px2in(pos.y),
      w: px2in(width),
      h: px2in(height),
    });
  } catch (err) {
    throw new Error(`Icon render failed for ${iconName}: ${err.message}`);
  }
}

function renderImage(pptx, slide, el, changelogData, imageCache) {
  // Support both flat format (el has all props) and split format (props in changelogData)
  const cl = changelogData || {};
  const pos    = el.position  || cl.position  || { x: 0, y: 0 };
  const width  = el.width     ?? cl.width     ?? 560;
  const height = el.height    ?? cl.height    ?? 360;
  const src    = el.src || '';

  const dataUri = imageCache && imageCache.get(src);
  if (!dataUri) {
    throw new Error(`Image not fetched: ${src.substring(0, 60)}`);
  }

  const rotation  = el.rotation  ?? cl.rotation  ?? 0;
  const opacity   = el.opacity   ?? cl.opacity   ?? 1;
  const shadow    = el.shadow    || cl.shadow    || {};
  const border    = el.border    || cl.border    || {};
  const overlay   = el.overlay   || cl.overlay   || {};

  // ── shadow ────────────────────────────────────────────────────────────────
  const pptxShadow = shadow.enabled ? {
    type:    'outer',
    blur:    shadow.blur    || 0,
    color:   hex(shadow.color || '#000000'),
    opacity: (shadow.opacity || 0) / 100,
    offset:  shadow.distance || 0,
    angle:   shadow.angle   || 135,
  } : undefined;

  // ── border (standard only — special styles not supported in PPTX) ─────────
  const pptxLine = border.type === 'standard' ? {
    color: hex(border.color || '#000000'),
    pt:    border.width || 1,
  } : undefined;

  slide.addImage({
    data:         dataUri,
    x:            px2in(pos.x),
    y:            px2in(pos.y),
    w:            px2in(width),
    h:            px2in(height),
    rotate:       rotation || undefined,
    transparency: opacity < 1 ? Math.round((1 - opacity) * 100) : undefined,
    shadow:       pptxShadow,
    line:         pptxLine,
  });

  // ── overlay: render as semi-transparent shape on top (blend mode ignored) ─
  if (overlay.color && overlay.opacity > 0) {
    slide.addShape(pptx.ShapeType.rect, {
      x: px2in(pos.x),
      y: px2in(pos.y),
      w: px2in(width),
      h: px2in(height),
      fill: {
        color:        hex(overlay.color),
        transparency: Math.round((1 - overlay.opacity / 100) * 100),
      },
      line: { color: hex(overlay.color), width: 0 },
    });
  }
}

const CHART_TYPE_MAP = {
  bar:      'bar',
  line:     'line',
  pie:      'pie',
  doughnut: 'doughnut',
  area:     'area',
  scatter:  'scatter',
};

// Normalize a chartConfig into pptxgenjs's [{ name, labels, values }] shape.
// Handles both the NATIVE ECharts option the generator now emits
// (series[].data + xAxis/yAxis.data) and the legacy [{name,labels,values}] form.
function normalizeChartData(chartConfig, rawType) {
  // Legacy simplified shape — already in the right form.
  const legacy = chartConfig.data;
  if (Array.isArray(legacy) && legacy.length && legacy[0]?.values && legacy[0]?.labels) {
    return legacy.map(s => ({ name: s.name || 'Series', labels: s.labels, values: s.values }));
  }

  const series = Array.isArray(chartConfig.series) ? chartConfig.series : [];
  if (!series.length) return [];

  const isCircular = ['pie', 'doughnut', 'nightingale', 'rose'].includes(rawType);
  if (isCircular) {
    // ECharts pie data: [{ name, value }, ...] → one pptx series.
    const pts = (series[0]?.data || []).filter(d => d && typeof d === 'object');
    return [{
      name:   series[0]?.name || 'Series',
      labels: pts.map(d => String(d.name ?? '')),
      values: pts.map(d => Number(d.value) || 0),
    }];
  }

  // Cartesian (bar/line/area/scatter): categories live on the category axis.
  const catAxis = (chartConfig.xAxis?.type === 'category') ? chartConfig.xAxis
                : (chartConfig.yAxis?.type === 'category') ? chartConfig.yAxis
                : chartConfig.xAxis;
  const labels = (catAxis?.data || []).map(String);
  return series.map((s, i) => ({
    name:   s.name || `Series ${i + 1}`,
    labels,
    // ECharts bar/line data is a flat number array; tolerate [{value}] too.
    values: (s.data || []).map(v => (v && typeof v === 'object') ? Number(v.value) || 0 : Number(v) || 0),
  }));
}

function renderChart(pptx, slide, el, changelogData, slideBg) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 560;
  const height = changelogData?.height || 360;
  const chartConfig = el.chartConfig || {};
  const rawType = (el.chartType || 'bar').toLowerCase();
  const chartType = CHART_TYPE_MAP[rawType] || 'bar';

  // Dark mode if the config says so, or the chart sits on a dark slide — then
  // force light axis/title/legend text so labels stay legible (pptxgenjs
  // defaults to dark text, invisible on a dark background).
  const cfgBg = chartConfig.backgroundColor;
  const panel = (cfgBg && cfgBg !== 'transparent') ? cfgBg : (slideBg || '#ffffff');
  const isDark = !!chartConfig.isDarkMode || !isLightHex(hex(panel));
  const textColor = isDark ? hex(chartConfig.textColor || '#F5F7FA') : '1c1917';
  const axisLineColor = isDark ? '5A6172' : 'D9DDE3';

  try {
    // pptxgenjs expects [{ name, labels, values }]. The generator emits NATIVE
    // ECharts options (chartConfig.series[].data + chartConfig.xAxis.data), so
    // normalize that here; fall back to the legacy [{name,labels,values}] shape.
    const pptxData = normalizeChartData(chartConfig, rawType);
    if (!pptxData.length || !pptxData[0].values?.length || !pptxData[0].labels?.length) {
      throw new Error('missing data/labels/values');
    }

    const chartColors = ['F96167', '2F3C7E', 'F9E795', '00B894', 'FDCB6E', '6C5CE7', 'E17055'];

    slide.addChart(chartType, pptxData, {
      x: px2in(pos.x),
      y: px2in(pos.y),
      w: px2in(width),
      h: px2in(height),
      chartColors,
      showTitle:  chartConfig.showTitle !== false,
      title:      chartConfig.title || '',
      titleColor: textColor,
      showLegend: pptxData.length > 1,
      legendPos:  'b',
      legendColor: textColor,
      catAxisLabelColor: textColor,
      valAxisLabelColor: textColor,
      catAxisLineColor: axisLineColor,
      valAxisLineColor: axisLineColor,
      dataLabelColor: textColor,
      dataLabelFontSize: 9,
    });
  } catch (err) {
    // Fallback: clean placeholder box with title + data summary
    slide.addShape(pptx.ShapeType.rect, {
      x: px2in(pos.x), y: px2in(pos.y),
      w: px2in(width), h: px2in(height),
      fill: { color: 'EEF6FF' },
      line: { color: '3B82F6', width: 1 },
    });
    const title = chartConfig.title || 'Chart';
    slide.addText(title, {
      x: px2in(pos.x + 16), y: px2in(pos.y + 16),
      w: px2in(width - 32), h: px2in(40),
      fontSize: 12, bold: true, color: '1e3a5f',
    });
    const series = normalizeChartData(chartConfig, rawType);
    if (series[0]?.values?.length) {
      const vals = series[0].values.map((v, i) => `${series[0].labels?.[i] ?? i}: ${v}`).join('  ');
      slide.addText(vals, {
        x: px2in(pos.x + 16), y: px2in(pos.y + 64),
        w: px2in(width - 32), h: px2in(height - 80),
        fontSize: 10, color: '374151', wrap: true,
      });
    }
    process.stderr.write(`  [chart fallback] ${title}: ${err.message}\n`);
  }
}

function renderTable(slide, el, changelogData) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 560;
  const height = changelogData?.height || 300;

  try {
    const cells = el.cells || {};
    // Extract rows and columns from cells map (format: "r-c")
    const rows = new Set();
    const cols = new Set();
    for (const key of Object.keys(cells)) {
      const [r, c] = key.split('-').map(Number);
      if (!isNaN(r) && !isNaN(c)) {
        rows.add(r);
        cols.add(c);
      }
    }
    const rowCount = Math.max(...rows, 0) + 1;
    const colCount = Math.max(...cols, 0) + 1;

    // Honor the deck's table styling (it carries dark-mode colors). pptxgenjs
    // defaults to black-on-white, which is invisible on a dark slide.
    const hex = (v, fb) => (v ? String(v).replace('#', '') : fb);
    const textColor = hex(el.tableColor, '1c1917');
    const bgColor   = hex(el.tableBg, 'ffffff');
    const fontSize  = el.tableFontSize || 18;
    // Subtle row divider derived from the text color (low-opacity look via mid-gray).
    const borderColor = isLightHex(bgColor) ? 'd9dde3' : '3a3f4a';
    // Header row: invert toward the accent for separation from body rows.
    const headerFill = isLightHex(bgColor) ? '1c1917' : '3E7BFA';
    const headerText = 'ffffff';

    const tableData = [];
    for (let r = 0; r < rowCount; r++) {
      const isHeader = r === 0;
      const row = [];
      for (let c = 0; c < colCount; c++) {
        const raw = cells[`${r}-${c}`];
        const txt = (raw && typeof raw === 'object' ? raw.text : raw) || '';
        row.push({
          text: String(txt).trim(),
          options: {
            color: isHeader ? headerText : textColor,
            fill:  { color: isHeader ? headerFill : bgColor },
            bold:  isHeader,
            align: 'left',
            valign: 'middle',
          },
        });
      }
      tableData.push(row);
    }

    const colW = (el.colWidths || []).map(px2in);
    const rowH = (el.rowHeights || []).map(px2in);
    slide.addTable(tableData, {
      x: px2in(pos.x),
      y: px2in(pos.y),
      w: px2in(width),
      ...(colW.length === colCount ? { colW } : {}),
      ...(rowH.length === rowCount ? { rowH } : {}),
      fontFace: 'Arial',
      fontSize,
      color: textColor,
      fill: { color: bgColor },
      border: { type: 'solid', pt: 1, color: borderColor },
      margin: [4, 8, 4, 8],
      valign: 'middle',
    });
  } catch (err) {
    throw new Error(`Table render failed: ${err.message}`);
  }
}

// ── Element kind classifier ───────────────────────────────────────────────────
const TEXT_TYPES = new Set(['text','title','subtitle','heading','subheading','paragraph','caption']);

function classifyKind(el) {
  const t = (el.type || '').toLowerCase();
  if (t === 'image') return 'image';
  if (t === 'shape') return 'shape';
  if (t === 'icon')  return 'icon';
  if (t === 'chart') return 'chart';
  if (t === 'table') return 'table';
  if (TEXT_TYPES.has(t)) return 'text';
  return null;
}

// ── Main converter ────────────────────────────────────────────────────────────
async function convertToPptx(deckData, outputPath) {
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = 'Bildory';

  // ── Detect format ─────────────────────────────────────────────────────────
  // Flat format:  data.slides[].elements[]  (editor / friend's JSON)
  // Split format: data.files.content.slides[].textElements[] + separate arrays
  const rawSlides = deckData.slides || deckData.files?.content?.slides || [];
  const isFlatFormat = rawSlides.length > 0 && Array.isArray(rawSlides[0]?.elements);

  // ── Build per-slide element lists ─────────────────────────────────────────
  const slideList = [];   // [{ slideData, allElements[] }]

  if (isFlatFormat) {
    for (const slideData of rawSlides) {
      const allElements = (slideData.elements || []).map(el => ({
        el,
        cl: el,   // all props are inline — element doubles as its changelog
        kind: classifyKind(el),
        zIndex: el.zIndex || 0,
      })).filter(e => e.kind !== null);
      allElements.sort((a, b) => a.zIndex - b.zIndex);
      slideList.push({ slideData, allElements });
    }
  } else {
    // Split format: merge content + changelog
    const changelog = deckData.files?.changelog?.slides || {};
    const contentArrays = deckData.files?.content || {};

    // group non-text elements by slideId, keeping the kind from the source
    // array — split-format content records carry no "type" field
    const ARRAY_KIND = {
      shapeElements: 'shape', chartElements: 'chart', iconElements: 'icon',
      imageElements: 'image', tableElements: 'table',
    };
    const nonTextBySlide = {};
    for (const [arrayKey, kind] of Object.entries(ARRAY_KIND)) {
      for (const el of (contentArrays[arrayKey] || [])) {
        if (!el.slideId) continue;
        (nonTextBySlide[el.slideId] = nonTextBySlide[el.slideId] || []).push({ el, kind });
      }
    }

    for (const slideData of rawSlides) {
      const clMap = (changelog[slideData.id] || {}).elements || {};
      const allElements = [];

      for (const el of (slideData.textElements || [])) {
        const cl = clMap[el.id] || {};
        allElements.push({ el, cl, kind: 'text', zIndex: cl.zIndex || 0 });
      }
      for (const { el, kind } of (nonTextBySlide[slideData.id] || [])) {
        const cl = clMap[el.id] || {};
        allElements.push({ el, cl, kind, zIndex: cl.zIndex || 0 });
      }
      allElements.sort((a, b) => a.zIndex - b.zIndex);
      slideList.push({ slideData, allElements });
    }
  }

  // ── Pre-fetch all image URLs ───────────────────────────────────────────────
  const allImageUrls = [];
  for (const { allElements } of slideList) {
    for (const { el, kind } of allElements) {
      if (kind === 'image' && el.src && (el.src.startsWith('http://') || el.src.startsWith('https://'))) {
        allImageUrls.push(el.src);
      }
    }
  }
  const uniqueUrls = [...new Set(allImageUrls)];

  const imageCache = new Map();

  // Local image cache (core/image_cache.py): images/<hash>.<ext> next to the
  // output .pptx (the run dir), mapped by manifest.json — reuse instead of
  // re-downloading what the pipeline already fetched.
  const MIME_BY_EXT = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png',
                        webp: 'image/webp', gif: 'image/gif', svg: 'image/svg+xml' };
  const imagesDir = path.join(path.dirname(path.resolve(outputPath)), 'images');
  const manifestPath = path.join(imagesDir, 'manifest.json');
  if (fs.existsSync(manifestPath)) {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
    for (const url of uniqueUrls) {
      const fname = manifest[url];
      if (!fname) continue;
      const fpath = path.join(imagesDir, fname);
      if (!fs.existsSync(fpath)) continue;
      const mime = MIME_BY_EXT[fname.split('.').pop()] || 'image/jpeg';
      imageCache.set(url, `data:${mime};base64,${fs.readFileSync(fpath).toString('base64')}`);
    }
    if (imageCache.size > 0) {
      process.stderr.write(`  [images] ${imageCache.size}/${uniqueUrls.length} from local cache\n`);
    }
  }

  const missingUrls = uniqueUrls.filter(u => !imageCache.has(u));
  if (missingUrls.length > 0) {
    process.stderr.write(`  [images] fetching ${missingUrls.length} image(s)...\n`);
    await Promise.all(missingUrls.map(async (url) => {
      try {
        const dataUri = await fetchImageAsDataUri(url);
        imageCache.set(url, dataUri);
        process.stderr.write(`  [images] ✓ ${url.substring(0, 70)}\n`);
      } catch (err) {
        process.stderr.write(`  [images] ✗ ${url.substring(0, 70)}: ${err.message}\n`);
      }
    }));
  }

  // ── Render slides ─────────────────────────────────────────────────────────
  for (const { slideData, allElements } of slideList) {
    const slide = pptx.addSlide();
    slide.background = { color: hex(slideData.backgroundColor || '#ffffff') };

    for (const { el, cl, kind } of allElements) {
      try {
        if (kind === 'text') {
          renderText(slide, el, cl);
        } else if (kind === 'shape') {
          renderShape(pptx, slide, el, cl);
        } else if (kind === 'icon') {
          renderIcon(pptx, slide, el, cl);
        } else if (kind === 'image') {
          renderImage(pptx, slide, el, cl, imageCache);
        } else if (kind === 'chart') {
          renderChart(pptx, slide, el, cl, slideData.backgroundColor);
        } else if (kind === 'table') {
          renderTable(slide, el, cl);
        }
      } catch (err) {
        process.stderr.write(`  [warn] slide ${slideData.id} / ${kind} ${el.id || '?'}: ${err.message}\n`);
      }
    }
  }

  await pptx.writeFile({ fileName: outputPath });
}

// ── Post-process: fix charset="0" → charset="1" so LibreOffice renders Unicode ─
function fixCharset(pptxPath) {
  const AdmZip = (() => { try { return require('adm-zip'); } catch { return null; } })();
  if (!AdmZip) return; // adm-zip not installed; skip silently

  const zip = new AdmZip(pptxPath);
  let changed = false;
  zip.getEntries().forEach(entry => {
    if (!entry.entryName.match(/^ppt\/slides\/slide\d+\.xml$/)) return;
    let xml = zip.readAsText(entry, 'utf8');
    if (xml.includes('charset="0"')) {
      xml = xml.replace(/charset="0"/g, 'charset="1"');
      zip.updateFile(entry.entryName, Buffer.from(xml, 'utf8'));
      changed = true;
    }
  });
  if (changed) zip.writeZip(pptxPath);
}

// ── Entry point ───────────────────────────────────────────────────────────────
(async () => {
  const [,, inputPath, outputPath] = process.argv;
  if (!inputPath || !outputPath) {
    process.stderr.write('Usage: node export_pptx.js <merged_deck.json> <output.pptx>\n');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  await convertToPptx(data, outputPath);
  fixCharset(outputPath);
  process.stdout.write(`written: ${outputPath}\n`);
})();
