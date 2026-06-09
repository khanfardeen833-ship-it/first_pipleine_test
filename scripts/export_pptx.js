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
const hex   = (color) => (color || '#000000').replace(/^#/, '');

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
};

function toKebab(name) {
  // Strip trailing "Icon" suffix some agents add (e.g. HandshakeIcon → handshake)
  const stripped = name.replace(/Icon$/, '');
  return stripped.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
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

  slide.addText(el.content || '', {
    x: px2in(pos.x),
    y: px2in(pos.y),
    w: px2in(width),
    h: px2in(height),
    fontSize: px2pt(fontSize),
    fontFace: fontFamily,
    color: hex(color),
    align: textAlign === 'center' ? 'center' : textAlign === 'right' ? 'right' : 'left',
    bold: fontWeight >= 700,
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
  const color = changelogData?.style?.color || '#000000';
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

function renderImage(slide, el, changelogData, imageCache) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 560;
  const height = changelogData?.height || 360;
  const src = el.src || '';

  const dataUri = imageCache && imageCache.get(src);
  if (!dataUri) {
    throw new Error(`Image not fetched: ${src.substring(0, 60)}`);
  }

  slide.addImage({
    data: dataUri,
    x: px2in(pos.x),
    y: px2in(pos.y),
    w: px2in(width),
    h: px2in(height),
  });
}

const CHART_TYPE_MAP = {
  bar:      'bar',
  line:     'line',
  pie:      'pie',
  doughnut: 'doughnut',
  area:     'area',
  scatter:  'scatter',
};

function renderChart(pptx, slide, el, changelogData) {
  const pos = changelogData?.position || { x: 0, y: 0 };
  const width = changelogData?.width || 560;
  const height = changelogData?.height || 360;
  const chartConfig = el.chartConfig || {};
  const rawType = (el.chartType || 'bar').toLowerCase();
  const chartType = CHART_TYPE_MAP[rawType] || 'bar';

  try {
    const rawData = chartConfig.data || [];
    if (!rawData.length || !rawData[0].values || !rawData[0].labels) {
      throw new Error('missing data/labels/values');
    }

    // pptxgenjs expects { name, labels, values } — field must be 'values'
    const pptxData = rawData.map(s => ({
      name:   s.name || 'Series',
      labels: s.labels,
      values: s.values,
    }));

    const chartColors = ['F96167', '2F3C7E', 'F9E795', '00B894', 'FDCB6E', '6C5CE7', 'E17055'];

    slide.addChart(chartType, pptxData, {
      x: px2in(pos.x),
      y: px2in(pos.y),
      w: px2in(width),
      h: px2in(height),
      chartColors,
      showTitle:  chartConfig.showTitle !== false,
      title:      chartConfig.title || '',
      showLegend: rawData.length > 1,
      legendPos:  'b',
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
    const series = (chartConfig.data || []);
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

    const tableData = [];
    for (let r = 0; r < rowCount; r++) {
      const row = [];
      for (let c = 0; c < colCount; c++) {
        row.push(cells[`${r}-${c}`] || '');
      }
      tableData.push(row);
    }

    slide.addTable(tableData, {
      x: px2in(pos.x),
      y: px2in(pos.y),
      w: px2in(width),
      h: px2in(height),
    });
  } catch (err) {
    throw new Error(`Table render failed: ${err.message}`);
  }
}

// ── Main converter ────────────────────────────────────────────────────────────
async function convertToPptx(deckData, outputPath) {
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_WIDE';   // 13.33×7.5 inches (16:9, 96 DPI)
  pptx.author = 'Bildory';

  const slides = deckData.files?.content?.slides || [];
  const changelog = deckData.files?.changelog?.slides || {};
  const contentArrays = deckData.files?.content || {};

  // Build maps of elements by slideId
  const elementsBySlide = {};
  for (const slideData of slides) {
    elementsBySlide[slideData.id] = {
      textElements: slideData.textElements || [],
      shapeElements: [],
      iconElements: [],
      imageElements: [],
      chartElements: [],
      tableElements: [],
    };
  }

  // Distribute non-text elements to their respective slides based on slideId
  for (const arrayKey of ['shapeElements', 'chartElements', 'iconElements', 'imageElements', 'tableElements']) {
    const array = contentArrays[arrayKey] || [];
    for (const el of array) {
      if (el.slideId && elementsBySlide[el.slideId]) {
        elementsBySlide[el.slideId][arrayKey].push(el);
      }
    }
  }

  // Pre-fetch all image URLs concurrently before rendering
  const allImageUrls = (contentArrays.imageElements || [])
    .map(el => el.src)
    .filter(src => src && (src.startsWith('http://') || src.startsWith('https://')));

  const imageCache = new Map();
  if (allImageUrls.length > 0) {
    process.stderr.write(`  [images] fetching ${allImageUrls.length} image(s)...\n`);
    await Promise.all(allImageUrls.map(async (url) => {
      try {
        const dataUri = await fetchImageAsDataUri(url);
        imageCache.set(url, dataUri);
        process.stderr.write(`  [images] ✓ ${url.substring(0, 70)}\n`);
      } catch (err) {
        process.stderr.write(`  [images] ✗ ${url.substring(0, 70)}: ${err.message}\n`);
      }
    }));
  }

  for (const slideData of slides) {
    const slide = pptx.addSlide();
    const bgColor = hex(slideData.backgroundColor || '#ffffff');
    slide.background = { color: bgColor };

    const slideChangelogData = changelog[slideData.id] || { elements: {} };
    const elementChangelogMap = slideChangelogData.elements || {};
    const slideElements = elementsBySlide[slideData.id];

    // Build unified list with zIndex from changelog, then sort ascending
    // so background shapes render first and text renders on top
    const allElements = [];

    for (const el of slideElements.textElements) {
      const cl = elementChangelogMap[el.id] || {};
      allElements.push({ el, cl, kind: 'text', zIndex: cl.zIndex || 0 });
    }
    for (const el of slideElements.shapeElements) {
      const cl = elementChangelogMap[el.id] || {};
      allElements.push({ el, cl, kind: 'shape', zIndex: cl.zIndex || 0 });
    }
    for (const el of slideElements.iconElements) {
      const cl = elementChangelogMap[el.id] || {};
      allElements.push({ el, cl, kind: 'icon', zIndex: cl.zIndex || 0 });
    }
    for (const el of slideElements.imageElements) {
      const cl = elementChangelogMap[el.id] || {};
      allElements.push({ el, cl, kind: 'image', zIndex: cl.zIndex || 0 });
    }
    for (const el of slideElements.chartElements) {
      const cl = elementChangelogMap[el.id] || {};
      allElements.push({ el, cl, kind: 'chart', zIndex: cl.zIndex || 0 });
    }
    for (const el of slideElements.tableElements) {
      const cl = elementChangelogMap[el.id] || {};
      allElements.push({ el, cl, kind: 'table', zIndex: cl.zIndex || 0 });
    }

    allElements.sort((a, b) => a.zIndex - b.zIndex);

    for (const { el, cl, kind } of allElements) {
      try {
        if (kind === 'text') {
          const type = (el.type || '').toLowerCase();
          if (['text', 'title', 'subtitle', 'heading', 'subheading', 'paragraph', 'caption'].includes(type)) {
            renderText(slide, el, cl);
          }
        } else if (kind === 'shape') {
          renderShape(pptx, slide, el, cl);
        } else if (kind === 'icon') {
          renderIcon(pptx, slide, el, cl);
        } else if (kind === 'image') {
          renderImage(slide, el, cl, imageCache);
        } else if (kind === 'chart') {
          renderChart(pptx, slide, el, cl);
        } else if (kind === 'table') {
          renderTable(slide, el, cl);
        }
      } catch (err) {
        process.stderr.write(`  [warn] slide ${slideData.id} / ${kind} ${el.id}: ${err.message}\n`);
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
