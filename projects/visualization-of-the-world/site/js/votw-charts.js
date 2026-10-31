// Chart framework on top of ECharts 6.1.0 and the design tokens.
// Votw.figure(host, spec) builds a card with title, provenance tag, states, chart, legend, tools and the
// mandatory "Source:" footer (a spec without `source` throws: no source, no chart).
// `real: true` marks a spec fed by the processed GUS/Eurostat CSVs: the tag becomes REAL DATA, the footer
// and exports name the source ids instead of the DEMO warning, and CSV exports carry a source_id column.
(function () {
  "use strict";
  const C = window.VotwCore;
  const E = window.echarts;
  const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const ms = (n) => parseFloat(cssVar(n)) || 0;
  const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const DEMO = "DEMO DATA, NOT REAL";
  const REAL = "REAL DATA";
  const REAL_ARN = "Real data: Statistics Poland (GUS) and Eurostat; exact sources in the footer.";
  const $ = (r, s) => r.querySelector(s);

  // ---------- data loading (cached promises) ----------
  const cache = new Map();
  async function fetchText(url) {
    const r = await fetch(url, { cache: "no-cache" });
    if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
    return r.text();
  }
  const fetchJson = async (u) => JSON.parse(await fetchText(u));
  function once(key, fn) { if (!cache.has(key)) cache.set(key, fn().catch((e) => { cache.delete(key); throw e; })); return cache.get(key); }
  const data = {
    regionsCsv: () => once("regionsCsv", async () => C.regionsFromCsv(C.parseCsv(await fetchText("data/demo-regions.csv")))),
    regionsJson: () => once("regionsJson", async () => fetchJson("data/demo.json")),
    powiats: () => once("powiats", async () => C.parseCsv(await fetchText("data/demo-powiats.csv"))),
    cities: () => once("cities", async () => C.parseCsv(await fetchText("data/demo-cities.csv"))),
    voivTopo: () => once("voivTopo", () => fetchJson("data/geo/voivodeships.topojson")),
    voivGeo: () => once("voivGeo", () => fetchJson("data/geo/voivodeships.geojson")),
    powiatTopo: () => once("powiatTopo", () => fetchJson("data/geo/powiats.topojson")),
    citiesGeo: () => once("citiesGeo", () => fetchJson("data/geo/cities.geojson")),
    // The canonical regions dataset: JSON (single fetch) as { years, regions:[{teryt,name,shares}] }
    regions: () => once("regions", async () => { const j = await fetchJson("data/demo.json"); return { years: j.years, regions: j.regions, meta: j.meta }; }),
    // Real data: verbatim copies of research/poland-demography-housing/data/processed/*.csv in data/real/.
    // Rows keep every column, including source_id, so footers and CSV exports can name the source.
    realPopulation: () => once("realPopulation", async () => C.parseCsv(await fetchText("data/real/population_by_class.csv"))),
    realCompletions: () => once("realCompletions", async () => C.parseCsv(await fetchText("data/real/housing_completions_by_class.csv"))),
    realHousingVsPop: () => once("realHousingVsPop", async () => C.parseCsv(await fetchText("data/real/housing_vs_population.csv"))),
    realStock: () => once("realStock", async () => C.parseCsv(await fetchText("data/real/housing_stock_by_class.csv"))),
    realMigration: () => once("realMigration", async () => C.parseCsv(await fetchText("data/real/migration_by_place_class.csv"))),
    realEurope: () => once("realEurope", async () => C.parseCsv(await fetchText("data/real/europe_annual.csv"))),
    realEuropeSummary: () => once("realEuropeSummary", async () => C.parseCsv(await fetchText("data/real/europe_summary.csv"))),
    realBigCities: () => once("realBigCities", async () => C.parseCsv(await fetchText("data/real/big_city_list.csv"))),
  };
  const topoFeatures = (topo, obj) => ({ type: "FeatureCollection", features: window.topojson.feature(topo, topo.objects[obj]).features });
  // Register the map names once. 'pl' = voivodeships (from TopoJSON), 'pl-<teryt>' = powiats of one voivodeship.
  async function ensureMaps() {
    const [vt, pt] = await Promise.all([data.voivTopo(), data.powiatTopo()]);
    const v = topoFeatures(vt, "voivodeships");
    const p = topoFeatures(pt, "powiats");
    if (!E.getMap("pl")) E.registerMap("pl", v);
    v.features.forEach((f) => {
      const id = "pl-" + f.properties.teryt;
      if (!E.getMap(id)) E.registerMap(id, { type: "FeatureCollection", features: p.features.filter((g) => g.properties.voivodeship_teryt === f.properties.teryt) });
    });
    return { voiv: v, powiats: p };
  }

  // ---------- tokens -> ECharts ----------
  const placeColor = (k) => cssVar("--data-place-" + k.replace(/_/g, "-"));
  const catColors = () => Array.from({ length: 8 }, (_, i) => cssVar("--data-cat-" + (i + 1)));
  const mapRamp = () => Array.from({ length: 7 }, (_, i) => cssVar("--data-map-" + (i + 1)));
  const divRamp = () => Array.from({ length: 7 }, (_, i) => cssVar("--data-div-" + (i + 1)));
  function textStyle(extra) { return Object.assign({ color: cssVar("--color-chart-text"), fontFamily: cssVar("--font-text"), fontSize: 12 }, extra); }
  function base(extra) {
    const o = {
      color: catColors(),
      backgroundColor: "transparent",
      textStyle: textStyle(),
      animation: !reduced(),
      animationDuration: ms("--dur-slow"),
      animationDurationUpdate: ms("--dur-slow"),
      animationEasing: "cubicOut",
      tooltip: tooltip(),
      aria: { enabled: true },
    };
    return Object.assign(o, extra);
  }
  function tooltip(extra) {
    return Object.assign({
      trigger: "axis", confine: true, enterable: false,
      triggerOn: "mousemove|click", // tap shows it on touch screens
      backgroundColor: cssVar("--color-bg-raised"), borderColor: cssVar("--color-border-subtle"), borderWidth: 1,
      padding: [8, 12], textStyle: { color: cssVar("--color-text-primary"), fontFamily: cssVar("--font-text"), fontSize: 14 },
      extraCssText: "box-shadow:" + cssVar("--shadow-md") + ";border-radius:" + cssVar("--radius-md") + ";",
      axisPointer: { type: "line", lineStyle: { color: cssVar("--color-chart-axis") }, label: { show: false } },
    }, extra);
  }
  function legend(extra) {
    return Object.assign({ top: 0, left: 0, icon: "roundRect", itemWidth: 14, itemHeight: 4, itemGap: 16, textStyle: textStyle({ color: cssVar("--color-text-secondary"), fontSize: 13 }), inactiveColor: cssVar("--color-text-muted") }, extra);
  }
  const axisCommon = () => ({
    axisLine: { lineStyle: { color: cssVar("--color-chart-axis") } },
    axisTick: { lineStyle: { color: cssVar("--color-chart-axis") } },
    axisLabel: textStyle(),
    nameTextStyle: textStyle(),
  });
  const valueAxis = (extra) => Object.assign({ type: "value", ...axisCommon(), axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: cssVar("--color-chart-grid") } } }, extra);
  const catAxis = (dataArr, extra) => Object.assign({ type: "category", data: dataArr, ...axisCommon(), splitLine: { show: false } }, extra);
  const grid = (extra) => Object.assign({ left: 4, right: 12, top: 44, bottom: 8, containLabel: true }, extra);
  const visualMapBase = (extra) => Object.assign({ textStyle: textStyle(), itemWidth: 14, itemHeight: 12, borderColor: cssVar("--color-border-subtle") }, extra);
  const fmt = (n, d) => (n === null || n === undefined || Number.isNaN(n) ? "no data" : Number(n).toLocaleString("en-GB", { minimumFractionDigits: d || 0, maximumFractionDigits: d === undefined ? 1 : d }));
  // Tooltip row markup that follows the design's .tooltip rules (swatch + label + value)
  function tipRows(title, rows) {
    return `<div style="font-weight:600;margin-bottom:4px">${esc(title)}</div>` + rows.map((r) =>
      `<div style="display:flex;align-items:center;gap:8px"><span style="width:10px;height:10px;border-radius:2px;background:${r.color};display:inline-block"></span><span>${esc(r.label)}</span><span style="margin-left:auto;padding-left:12px;font-weight:600;font-variant-numeric:tabular-nums">${esc(r.value)}</span></div>`).join("");
  }

  // ---------- download helpers ----------
  function download(name, blobOrUrl, type) {
    const a = document.createElement("a");
    let url = blobOrUrl;
    if (typeof blobOrUrl === "string" && !/^(data|blob):/.test(blobOrUrl)) url = URL.createObjectURL(new Blob([blobOrUrl], { type }));
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    if (url.startsWith("blob:")) setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
  function wrapText(ctx, text, maxW) {
    const words = text.split(" "), lines = []; let line = "";
    words.forEach((w) => { const t = line ? line + " " + w : w; if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
    if (line) lines.push(line); return lines;
  }

  // PNG: chart bitmap with title, subtitle, provenance tag and source line composed around it
  function exportPng(chart, meta) {
    const src = chart.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: cssVar("--color-chart-surface") });
    const img = new Image();
    img.onload = () => {
      const k = 2, W = img.width, pad = 16 * k;
      const probe = document.createElement("canvas").getContext("2d");
      const fam = cssVar("--font-text");
      probe.font = `${14 * k}px ${fam}`;
      const subLines = wrapText(probe, meta.subtitle, W - 2 * pad);
      const srcLines = wrapText(probe, `${meta.real ? REAL + ". " : DEMO + ". "}Source: ${meta.sourceText}`, W - 2 * pad);
      const head = pad + 22 * k + subLines.length * 18 * k + 8 * k, foot = srcLines.length * 18 * k + pad;
      const cv = document.createElement("canvas"); cv.width = W; cv.height = img.height + head + foot;
      const g = cv.getContext("2d");
      g.fillStyle = cssVar("--color-chart-surface"); g.fillRect(0, 0, cv.width, cv.height);
      g.fillStyle = cssVar("--color-text-primary"); g.font = `600 ${18 * k}px ${cssVar("--font-display")}`; g.textBaseline = "top";
      g.fillText(meta.title, pad, pad, W - 2 * pad);
      g.fillStyle = cssVar("--color-text-secondary"); g.font = `${14 * k}px ${fam}`;
      subLines.forEach((l, i) => g.fillText(l, pad, pad + 24 * k + i * 18 * k));
      g.drawImage(img, 0, head);
      g.fillStyle = cssVar("--color-text-secondary"); g.font = `${12 * k}px ${fam}`;
      srcLines.forEach((l, i) => g.fillText(l, pad, head + img.height + 6 * k + i * 16 * k));
      cv.toBlob((b) => download(slug(meta.title) + ".png", URL.createObjectURL(b)), "image/png");
    };
    img.src = src;
  }
  // SVG: render the same option with the SVG renderer in SSR mode (no DOM), then wrap with title and source
  function exportSvg(option, w, h, meta) {
    const ssr = E.init(null, null, { renderer: "svg", ssr: true, width: w, height: h });
    ssr.setOption(Object.assign({}, option, { animation: false }));
    let inner = ssr.renderToSVGString(); ssr.dispose();
    inner = inner.replace(/^<\?xml[^>]*>\s*/, "").replace(/<svg /, `<svg x="0" y="64" `);
    const fam = cssVar("--font-text").replace(/"/g, "'");
    const t = (x, y, s, size, color, weight) => `<text x="${x}" y="${y}" font-family="${fam}" font-size="${size}" fill="${color}"${weight ? ` font-weight="${weight}"` : ""}>${esc(s)}</text>`;
    const H = h + 64 + 40;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${H}" viewBox="0 0 ${w} ${H}"><rect width="100%" height="100%" fill="${cssVar("--color-chart-surface")}"/>` +
      t(16, 24, meta.title, 18, cssVar("--color-text-primary"), 600) + t(16, 46, meta.subtitle.slice(0, 140), 13, cssVar("--color-text-secondary")) + inner +
      t(16, h + 64 + 18, `${meta.real ? REAL + ". " : DEMO + ". "}Source: ${meta.sourceText}`.slice(0, 160), 12, cssVar("--color-text-secondary")) + "</svg>";
    download(slug(meta.title) + ".svg", svg, "image/svg+xml");
  }

  // ---------- the figure ----------
  const ICON = {
    empty: '<svg class="state__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4M8 11h6"/></svg>',
    error: '<svg class="state__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3 2 20h20L12 3zM12 10v4M12 17v.5"/></svg>',
  };
  const registry = [];

  function figure(host, spec) {
    if (!spec.source || !spec.source.label) throw new Error(`figure "${spec.id}": a Source footer is required`);
    const el = document.createElement("figure");
    el.className = "card figure " + (spec.className || "span-all");
    el.dataset.chartCard = spec.id;
    const src = spec.source;
    const real = !!spec.real;
    const sourceText = src.label + (src.meta ? " (" + src.meta + ")" : "");
    const tag = real
      ? `<span class="badge badge--good real-tag"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m3 8.5 3 3 7-7"/></svg>${REAL}</span>`
      : `<span class="badge badge--warning demo-tag">${DEMO}</span>`;
    const aria = spec.title + ". " + spec.subtitle + (real ? " " + REAL_ARN : " " + DEMO + ".");
    el.dataset.provenance = real ? "real" : "demo";
    el.innerHTML = `
      <div class="figure__head"><h3 class="figure__title">${esc(spec.title)}</h3>${tag}</div>
      <p class="figure__subtitle">${esc(spec.subtitle)}</p>
      <div class="figure__controls" data-controls hidden></div>
      <div class="chart-wrap"><div class="state-slot"></div><div class="chart" data-chart="${esc(spec.id)}" role="img" aria-label="${esc(aria)}" hidden></div></div>
      <ul class="legend legend-html" data-legend hidden></ul>
      <p class="status-line" data-status aria-live="polite" hidden></p>
      <div class="figure__tools" data-tools>
        <button class="btn btn--secondary" type="button" data-act="table" aria-pressed="false">Table view</button>
        <button class="btn btn--secondary" type="button" data-act="png">PNG</button>
        <button class="btn btn--secondary" type="button" data-act="svg">SVG</button>
        <button class="btn btn--secondary" type="button" data-act="csv">CSV</button>
      </div>
      <div class="table-view" data-table hidden></div>
      <footer class="chart-source"><span class="chart-source__label">Source:</span>${src.url ? `<a href="${esc(src.url)}">${esc(src.label)}</a>` : `<span>${esc(src.label)}</span>`}${src.meta ? `<span class="chart-source__meta">${esc(src.meta)}</span>` : ""}<span class="chart-source__meta">${real ? REAL + ". Accessed" : DEMO + ". Accessed"} ${esc(src.accessed || "2026-10-29")}.</span></footer>`;
    host.appendChild(el);

    const chartEl = $(el, "[data-chart]"), slot = $(el, ".state-slot");
    const ctl = { el, spec, data: null, chart: null, state: "init", option: null, extra: {} };
    const csvOf = () => {
      if (!spec.csv || ctl.data === null) return null;
      const t = spec.csv(ctl.data, ctl);
      if (!t || !real) return t;
      // Real charts export the source ids of every row, never a made-up "real" flag.
      return C.csvWithSourceIds(t, src.ids || src.id || null);
    };

    ctl.setState = (s, msg) => {
      ctl.state = s;
      chartEl.hidden = s !== "ready";
      slot.innerHTML = "";
      el.dataset.state = s;
      const tools = $(el, "[data-tools]");
      tools.querySelectorAll("[data-act]").forEach((b) => (b.disabled = s !== "ready"));
      if (s === "loading") {
        slot.innerHTML = `<div class="skeleton" role="status" aria-label="Loading data" style="min-height:${spec.height ? Math.min(typeof spec.height === "number" ? spec.height : 320, 360) : 260}px"><div class="skeleton__bar" style="width:40%"></div><div class="skeleton__bar" style="width:85%"></div><div class="skeleton__bar" style="width:65%"></div><div class="skeleton__bar" style="width:95%"></div><div class="skeleton__bar" style="width:55%"></div></div>`;
      } else if (s === "empty") {
        slot.innerHTML = `<div class="state" role="status">${ICON.empty}<p class="state__title">${esc((msg && msg.title) || "No data for this selection")}</p><p class="state__text">${esc((msg && msg.text) || "Nothing matches the current filters.")}</p>${spec.onReset ? '<button class="btn btn--secondary" type="button" data-reset>Reset filters</button>' : ""}</div>`;
        $(slot, "[data-reset]")?.addEventListener("click", () => spec.onReset(ctl));
      } else if (s === "error") {
        slot.innerHTML = `<div class="state state--error" role="alert">${ICON.error}<p class="state__title">Could not load the data</p><p class="state__text">${esc((msg && msg.text) || "Check the connection and try again.")}</p><button class="btn btn--secondary" type="button" data-retry>Try again</button></div>`;
        $(slot, "[data-retry]").addEventListener("click", () => ctl.load());
      }
    };

    const heightFor = (w) => (typeof spec.height === "function" ? spec.height(w) : spec.height || 320);
    ctl.render = () => {
      if (ctl.data === null || ctl.state === "loading" || ctl.state === "error") return;
      const w = chartEl.clientWidth || el.clientWidth - 32;
      let option;
      try { option = spec.build(ctl.data, Object.assign(ctl, { width: w })); } catch (e) { console.error(e); ctl.setState("error", { text: e.message }); return; }
      if (option === null || option === "empty") { ctl.setState("empty", ctl.emptyMsg); return; }
      // ECharts writes its own aria-label on the canvas host; real charts keep the provenance wording there too.
      if (real && option.aria) option.aria = Object.assign({}, option.aria, { label: Object.assign({}, option.aria.label, { description: aria }) });
      if (ctl.state !== "ready") ctl.setState("ready");
      chartEl.style.height = heightFor(chartEl.clientWidth || w) + "px";
      if (!ctl.chart) { ctl.chart = E.init(chartEl, null, { renderer: "canvas" }); ctl.chart.group = spec.group || ""; spec.onChart?.(ctl.chart, ctl); }
      ctl.chart.resize();
      ctl.option = option;
      ctl.chart.setOption(option, spec.setOpt ? Object.assign({ notMerge: false }, spec.setOpt) : spec.merge ? { notMerge: false } : { notMerge: true });
      spec.afterRender?.(ctl);
      renderLegend(); renderTable();
    };
    function renderLegend() {
      const ul = $(el, "[data-legend]");
      const items = spec.htmlLegend ? spec.htmlLegend(ctl.data, ctl) : null;
      ul.hidden = !items;
      if (items) ul.innerHTML = items.map((i) => `<li class="legend__item"><span class="legend__swatch" style="--swatch:${i.color}"></span>${esc(i.label)}</li>`).join("");
    }
    function renderTable() {
      const box = $(el, "[data-table]");
      const open = $(el, '[data-act="table"]').getAttribute("aria-pressed") === "true";
      box.hidden = !open;
      if (!open) return;
      const t = csvOf();
      if (!t) { box.innerHTML = '<p class="small secondary">No table for this chart.</p>'; return; }
      const rows = t.rows.slice(0, 60);
      const num = (v) => typeof v === "number";
      box.innerHTML = `<div class="table-scroll" tabindex="0" role="region" aria-label="Table: ${esc(spec.title)}"><table class="data-table"><thead><tr>${t.header.map((h, i) => `<th scope="col"${num(t.rows[0]?.[i]) ? ' class="n"' : ""}>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((v, i) => (v === null || v === "" ? '<td class="missing n">no data</td>' : `<td${num(v) ? ' class="n"' : ""}>${esc(num(v) ? fmt(v, 1) : v)}</td>`)).join("")}</tr>`).join("")}</tbody></table></div>${t.rows.length > 60 ? `<p class="figure__note">Showing 60 of ${t.rows.length} rows. The CSV button exports all rows.</p>` : ""}`;
    }
    ctl.load = async () => {
      ctl.setState("loading");
      try {
        const d = await spec.load();
        ctl.data = d;
        if (d === null || (Array.isArray(d) && !d.length)) { ctl.setState("empty", spec.emptyMsg); return; }
        ctl.state = "loaded";
        const c = $(el, "[data-controls]");
        if (spec.controls && !c.dataset.done) { c.dataset.done = "1"; c.hidden = false; spec.controls(c, ctl); window.VotwComponents?.init(c); }
        ctl.render();
        spec.onLoaded?.(ctl);
      } catch (e) {
        console.warn(`[${spec.id}]`, e.message);
        ctl.data = null;
        ctl.setState("error", { text: "The data could not be loaded (" + e.message + "). Check the connection and try again." });
      }
    };
    ctl.status = (txt) => { const s = $(el, "[data-status]"); s.hidden = !txt; s.textContent = txt || ""; };
    ctl.redraw = ctl.render;

    el.addEventListener("click", (e) => {
      const b = e.target.closest("[data-act]");
      if (!b || b.disabled) return;
      const act = b.dataset.act;
      const meta = { title: spec.title, subtitle: spec.subtitle, sourceText, real };
      if (act === "table") { b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true")); renderTable(); }
      if (act === "png" && ctl.chart) exportPng(ctl.chart, meta);
      if (act === "svg" && ctl.option) exportSvg(ctl.option, chartEl.clientWidth, chartEl.clientHeight, meta);
      if (act === "csv") {
        const t = csvOf(); if (!t) return;
        const table = real ? t : { header: [...t.header, "demo_flag"], rows: t.rows.map((r) => [...r, DEMO]) };
        download(slug(spec.title) + ".csv", C.toCsv(table.header, table.rows), "text/csv;charset=utf-8");
      }
    });
    if ("ResizeObserver" in window) {
      let last = 0;
      new ResizeObserver(() => { const w = chartEl.clientWidth; if (ctl.chart && Math.abs(w - last) > 1) { last = w; ctl.render(); } }).observe(el);
    } else window.addEventListener("resize", () => ctl.render());
    registry.push(ctl);
    ctl.load();
    return ctl;
  }
  const retheme = () => registry.forEach((c) => { c.chart && c.render(); });
  document.addEventListener("themechange", () => requestAnimationFrame(retheme));
  window.Votw = { figure, data, ensureMaps, topoFeatures, cssVar, ms, reduced, esc, fmt, placeColor, catColors, mapRamp, divRamp, base, tooltip, legend, valueAxis, catAxis, grid, textStyle, visualMapBase, tipRows, registry, download, DEMO, REAL, DEMO_SOURCE: { label: "Synthetic demo data (made up, not GUS)", url: "data/demo.json", meta: "generated by scripts/make_demo_data.py" }, GEO_NOTE: "boundaries: GUGiK PRG, simplified" };
})();
