// Loads every page of the demo site in headless Chromium like a user would and checks it.
// Usage: node scripts/verify_site.cjs <base-url> <out-dir>      (python3 -m http.server in site/ serves <base-url>)
// Needs `playwright` resolvable (NODE_PATH=.../node_modules). CHROMIUM_PATH optionally points to a browser.
// Checks: no console errors, no horizontal scroll at 375/768/1280, every chart card has a Source footer,
// every figure reaches a final state, interactions (tooltip, play, filter, brush, drill-down, zoom, touch tap,
// theme switch, exports) and the forced failure path. real.html must show the REAL DATA provenance instead of
// the demo banner and export source_id columns. Exit 1 on any failed check.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const [base, outDir] = process.argv.slice(2);
if (!base || !outDir) { console.error("usage: node verify_site.cjs <base-url> <out-dir>"); process.exit(2); }
fs.mkdirSync(outDir, { recursive: true });
const B = base.replace(/\/$/, "");
const PAGES = ["index", "charts", "interaction", "maps", "formats", "polish", "matrix", "real"];
const results = []; let failures = 0;
const check = (name, ok, detail = "") => { results.push({ name, ok, detail }); if (!ok) failures++; console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail ? " - " + detail : ""}`); };
const shot = (page, name, opts = {}) => page.screenshot({ path: path.join(outDir, name), type: "jpeg", quality: 55, fullPage: true, ...opts });

async function open(browser, url, width, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width, height: width < 600 ? 812 : 900 }, hasTouch: width < 600, acceptDownloads: true, colorScheme: opts.dark ? "dark" : "light", ...(opts.ctx || {}) });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push("console.error: " + m.text()); });
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("requestfailed", (r) => errors.push("requestfailed: " + r.url()));
  page.on("response", (r) => { if (r.status() >= 400) errors.push(`http ${r.status()}: ${r.url()}`); });
  if (opts.setup) await opts.setup(page);
  await page.goto(url, { waitUntil: "load" });
  return { ctx, page, errors };
}
const settled = (page) => page.waitForFunction("window.Votw && (!document.getElementById('figures') || Votw.registry.length) && Votw.registry.every(c => c.spec.keepLoading || ['ready','empty','error'].includes(c.state))", null, { timeout: 20000 }).then(() => page.waitForTimeout(900));
const pt = async (page, sel, fn, args) => page.evaluate(([s, f, a]) => { const el = document.querySelector(s); const r = el.getBoundingClientRect(); const c = Votw.registry.find((x) => x.el.contains(el)).chart; return new Function("c", "r", "a", "return " + f)(c, r, a); }, [sel, fn, args]);

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });

  // 1. every page: errors, overflow, footers, states, at three widths
  for (const w of [375, 768, 1280]) {
    for (const p of PAGES) {
      const { ctx, page, errors } = await open(browser, `${B}/${p}.html`, w);
      if (p !== "matrix") await settled(page); else { await page.waitForSelector("table.matrix"); await page.waitForTimeout(300); }
      const isReal = p === "real";
      const info = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
        cards: Array.from(document.querySelectorAll("[data-chart-card]")).map((c) => ({ id: c.dataset.chartCard, src: !!c.querySelector("footer.chart-source .chart-source__label") && /Source:/.test(c.querySelector("footer.chart-source").textContent) && !!c.querySelector("footer.chart-source a, footer.chart-source span:not(.chart-source__label):not(.chart-source__meta)"), state: c.dataset.state, text: c.innerText })),
        banner: document.querySelector(".provenance-banner")?.innerText || "", body: document.body.innerText,
        tags: Array.from(document.querySelectorAll("[data-chart-card]")).every((c) => /DEMO DATA, NOT REAL/.test(c.innerText)),
        realTags: Array.from(document.querySelectorAll("[data-chart-card]")).every((c) => /REAL DATA/.test(c.innerText)),
        kpi: Array.from(document.querySelectorAll("[data-kpi]")).map((c) => ({ id: c.dataset.kpi, src: !!c.querySelector("footer.chart-source .chart-source__label") && /^Source:/.test((c.querySelector("footer.chart-source")?.innerText || "").trim()) && !!c.querySelector("footer.chart-source a[href]") })),
        tables: document.querySelectorAll("table.matrix").length, srcAll: Array.from(document.querySelectorAll("table.matrix")).every((t) => t.closest(".card")?.querySelector("footer.chart-source")),
      }));
      const demoText = /DEMO DATA, NOT REAL/.test(info.body);
      check(`${p} @${w}: no console errors / failed requests`, errors.length === 0, errors.join(" | "));
      check(`${p} @${w}: no horizontal scroll`, info.sw <= info.cw, `scrollWidth ${info.sw} vs ${info.cw}`);
      if (isReal) check(`${p} @${w}: REAL DATA banner, REAL DATA tags, no DEMO wording`, /^REAL DATA —/.test(info.banner) && info.realTags && !demoText && info.cards.every((c) => !/DEMO DATA, NOT REAL/.test(c.text)), info.banner.slice(0, 60));
      else check(`${p} @${w}: DEMO DATA banner and per-chart tag`, /DEMO DATA, NOT REAL/.test(info.banner) && info.tags);
      check(`${p} @${w}: ${info.cards.length} chart cards all have a Source footer`, info.cards.every((c) => c.src), info.cards.filter((c) => !c.src).map((c) => c.id).join(","));
      if (isReal) check(`${p} @${w}: KPI cards carry a manual Source footer and no DEMO flag`, info.kpi.length === 3 && info.kpi.every((c) => c.src), info.kpi.map((c) => c.id + ":" + c.src).join(","));
      if (p !== "polish" && p !== "matrix") check(`${p} @${w}: every chart reached ready`, info.cards.every((c) => c.state === "ready"), info.cards.filter((c) => c.state !== "ready").map((c) => c.id + ":" + c.state).join(","));
      if (p === "matrix") check(`matrix @${w}: table has a Source footer`, info.tables > 0 && info.srcAll);
      if (w === 375 || w === 1280) await shot(page, `${p}-${w}${w === 375 ? "" : "-desktop"}.jpg`.replace("-1280-desktop", "-desktop"));
      await ctx.close();
    }
  }

  // 2. dark theme via the switch (and screenshots)
  {
    const { ctx, page, errors } = await open(browser, `${B}/charts.html`, 1280); await settled(page);
    await page.selectOption("#theme-top", "dark"); await page.waitForTimeout(1200);
    const dark = await page.evaluate(() => document.documentElement.classList.contains("theme-dark") && getComputedStyle(document.body).backgroundColor);
    check("theme switch: dark class applied", !!dark, String(dark));
    await shot(page, "charts-desktop-dark.jpg");
    await page.reload(); await settled(page);
    check("theme switch: choice remembered after reload", await page.evaluate(() => document.documentElement.classList.contains("theme-dark")));
    check("theme switch: no console errors", errors.length === 0, errors.join("|"));
    await ctx.close();
    const m = await open(browser, `${B}/maps.html`, 375, { dark: true }); await settled(m.page); await shot(m.page, "maps-375-dark.jpg"); await m.ctx.close();
  }

  // 3. tooltip on hover, table view, exports
  {
    const { ctx, page } = await open(browser, `${B}/charts.html`, 1280); await settled(page);
    const box = await page.locator('[data-chart="line"]').boundingBox();
    await page.locator('[data-chart="line"]').scrollIntoViewIfNeeded();
    const b2 = await page.locator('[data-chart="line"]').boundingBox();
    await page.mouse.move(b2.x + b2.width * 0.5, b2.y + b2.height * 0.5); await page.waitForTimeout(500);
    const tip = await page.evaluate(() => { const c = document.querySelector('[data-chart="line"]'); return Array.from(c.querySelectorAll("div")).map((d) => d.innerText).join(" "); });
    check("tooltip shows on hover (line chart)", /Big cities/.test(tip) && /%/.test(tip), tip.slice(0, 80));
    await page.screenshot({ path: path.join(outDir, "tooltip-line-desktop.jpg"), type: "jpeg", quality: 60, clip: { x: b2.x - 30, y: Math.max(0, b2.y - 80), width: b2.width + 60, height: b2.height + 120 } });
    await page.click('[data-chart-card="line"] [data-act="table"]');
    check("table view opens with rows", (await page.locator('[data-chart-card="line"] .data-table tbody tr').count()) > 20);
    const dl = async (act) => { const [d] = await Promise.all([page.waitForEvent("download"), page.click(`[data-chart-card="line"] [data-act="${act}"]`)]); const f = path.join(outDir, "export-line." + act); await d.saveAs(f); return { name: d.suggestedFilename(), text: fs.readFileSync(f, act === "png" ? undefined : "utf-8"), file: f }; };
    const csv = await dl("csv"), svg = await dl("svg"), png = await dl("png");
    check("export CSV (has DEMO flag, 26 data rows)", /DEMO DATA, NOT REAL/.test(csv.text) && csv.text.trim().split("\n").length === 27, csv.name);
    check("export SVG (valid, carries Source line)", /^<svg/.test(svg.text) && /Source:/.test(svg.text) && /<path|<polyline/.test(svg.text), svg.name + " " + svg.text.length + " bytes");
    check("export PNG (PNG signature)", png.text[0] === 0x89 && png.text[1] === 0x50 && png.text.length > 5000, png.name + " " + png.text.length + " bytes");
    fs.unlinkSync(csv.file); fs.unlinkSync(svg.file); // keep only the PNG sample, small
    fs.renameSync(png.file, path.join(outDir, "export-sample.png"));
    await ctx.close();
  }

  // 3b. real page: provenance, exports carry source ids
  {
    const { ctx, page, errors } = await open(browser, `${B}/real.html`, 1280); await settled(page);
    const dl = async (id, act) => { const [d] = await Promise.all([page.waitForEvent("download"), page.click(`[data-chart-card="${id}"] [data-act="${act}"]`)]); const f = path.join(outDir, `export-${id}.${act}`); await d.saveAs(f); return { file: f, text: fs.readFileSync(f, act === "png" ? undefined : "utf-8") }; };
    const csv = await dl("real-housing-vs-pop", "csv");
    const head = csv.text.replace(/^\uFEFF/, "").split(/\r?\n/)[0];
    check("real export CSV: source_id column with per-row ids, proxy/direct basis, no DEMO flag",
      /source_id/.test(head) && /S41;S42/.test(csv.text) && /S43/.test(csv.text) && /proxy/.test(csv.text) && /direct/.test(csv.text) && !/DEMO DATA, NOT REAL/.test(csv.text), head);
    fs.unlinkSync(csv.file);
    const png = await dl("real-cities-map", "png");
    check("real export PNG: rendered map bubble chart", png.text[0] === 0x89 && png.text[1] === 0x50 && png.text.length > 5000, png.text.length + " bytes");
    const tips = await page.evaluate(() => Array.from(document.querySelectorAll("[data-chart-card] [role=img]")).map((c) => c.getAttribute("aria-label")));
    check("real page: aria-labels name the real sources, not a demo warning", tips.length > 0 && tips.every((t) => /Real data/.test(t) && !/DEMO DATA, NOT REAL/.test(t)), tips[0].slice(0, 80));
    check("real page: no console errors", errors.length === 0, errors.join("|"));
    await ctx.close();
  }

  // 4. interaction page: play, filter, region click, brush
  {
    const { ctx, page, errors } = await open(browser, `${B}/interaction.html`, 1280); await settled(page);
    await page.click("[data-play]"); await page.waitForTimeout(1700);
    const y = await page.evaluate(() => +document.querySelector("#year-range").value);
    check("timeline play advances the year", y > 0 && y !== 2025, "year " + y);
    await page.click("[data-play]");
    await page.evaluate(() => { const r = document.querySelector("#year-range"); r.value = 2000; r.dispatchEvent(new Event("input", { bubbles: true })); }); await page.waitForTimeout(900);
    check("slider drives linked ranking, map and timeline", await page.evaluate(() => SpecsInteraction.state.year === 2000 && Votw.registry.find((c) => c.spec.id === "rank").option.series[0].data.length === 16));
    await shot(page, "interaction-year-2000-desktop.jpg");
    await page.click('[data-place="big-cities"]'); await page.waitForTimeout(700);
    check("place-type filter updates the shared state", await page.evaluate(() => SpecsInteraction.state.active.join() === "small_cities"), await page.evaluate(() => SpecsInteraction.state.active.join()));
    const name = await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "rank").option.series[0].name);
    check("filter changes the metric label in the ranking", name === "Small cities", name);
    check("filter changes the brush scatter (one series left)", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "brush").option.series.length === 1));
    await page.click('[data-place="big-cities"]'); await page.waitForTimeout(500);
    // click a region on the linked map
    await page.locator('[data-chart="map"]').scrollIntoViewIfNeeded();
    const mp = await pt(page, '[data-chart="map"]', "(() => { const p = c.convertToPixel({ seriesIndex: 0 }, [21, 52.2]); return [r.x + p[0], r.y + p[1]]; })()");
    await page.mouse.click(mp[0], mp[1]); await page.waitForTimeout(800);
    check("clicking the map selects a region shared with the ranking and timeline", await page.evaluate(() => SpecsInteraction.state.region === "14"), await page.evaluate(() => String(SpecsInteraction.state.region)));
    // brush
    await page.locator('[data-chart="brush"]').scrollIntoViewIfNeeded();
    const bb = await page.locator('[data-chart="brush"]').boundingBox();
    await page.mouse.move(bb.x + bb.width * 0.55, bb.y + bb.height * 0.3); await page.mouse.down(); await page.mouse.move(bb.x + bb.width * 0.9, bb.y + bb.height * 0.7, { steps: 8 }); await page.mouse.up(); await page.waitForTimeout(900);
        const nb = await page.evaluate(() => (SpecsInteraction.state.brushedPts || []).length);
    check("brush selects cities and the linked bars update", nb > 0, nb + " cities brushed");
    await page.locator('[data-chart-card="brushsum"]').scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
    await shot(page, "interaction-brush-desktop.jpg", { fullPage: false });
    // zoom and pan on the timeline: dataZoom
    await page.locator('[data-chart="timeline"]').scrollIntoViewIfNeeded();
    await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "timeline").chart.dispatchAction({ type: "dataZoom", start: 40, end: 70 })); await page.waitForTimeout(500);
    const zr = await page.evaluate(() => { const o = Votw.registry.find((c) => c.spec.id === "timeline").chart.getOption().dataZoom[0]; return [o.start, o.end]; });
    check("timeline zoom window changes (dataZoom)", Math.abs(zr[0] - 40) < 1 && Math.abs(zr[1] - 70) < 1, zr.join("-"));
    // shape morph
    await page.click('[data-kind="pie"]'); await page.waitForTimeout(900);
    check("morph: bars to pie renders", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "morph").chart.getOption().series[0].type === "pie"));
    check("interaction: no console errors", errors.length === 0, errors.join("|"));
    await ctx.close();
  }

  // 5. maps: drill-down, back, zoom to region, hover tooltip
  {
    const { ctx, page, errors } = await open(browser, `${B}/maps.html`, 1280); await settled(page);
    await page.locator('[data-chart="choropleth"]').scrollIntoViewIfNeeded();
    const p0 = await pt(page, '[data-chart="choropleth"]', "(() => { const p = c.convertToPixel({ seriesIndex: 0 }, [21, 52.2]); return [r.x + p[0], r.y + p[1]]; })()");
    await page.mouse.move(p0[0], p0[1]); await page.waitForTimeout(500);
    const tip = await page.evaluate(() => document.querySelector('[data-chart="choropleth"]').innerText);
    check("choropleth hover tooltip names the region and value", /Mazowieckie/.test(tip) && /Villages 2025/.test(tip), tip.replace(/\n/g, " ").slice(0, 70));
    await page.screenshot({ path: path.join(outDir, "maps-hover-tooltip-desktop.jpg"), type: "jpeg", quality: 60 });
    await page.mouse.click(p0[0], p0[1]); await page.waitForTimeout(1000);
    check("drill-down: click opens powiats of the voivodeship", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "choropleth").extra.level === "14" && Votw.registry.find((c) => c.spec.id === "choropleth").option.series[0].map === "pl-14"));
    await page.screenshot({ path: path.join(outDir, "maps-drilldown-mazowieckie-desktop.jpg"), type: "jpeg", quality: 60 });
    await page.click("[data-back]"); await page.waitForTimeout(700);
    check("drill-down: back to Poland", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "choropleth").option.series[0].map === "pl"));
    await page.selectOption("#zoom-choro", "12"); await page.waitForTimeout(900);
    check("zoom to region (select)", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "choropleth").option.series[0].zoom > 2));
    await page.selectOption("#zoom-bub", "22"); await page.waitForTimeout(900);
    await page.locator('[data-chart="bubbles"]').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(outDir, "maps-bubbles-zoom-pomorskie-desktop.jpg"), type: "jpeg", quality: 60 });
    await page.selectOption("#zoom-bub", ""); await page.waitForTimeout(500);
    await page.click('[data-chart-card="bubbles"] [data-place="small-cities"]'); await page.waitForTimeout(600);
    check("bubble map place-type filter (big cities only)", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "bubbles").option.series.length === 1));
    check("maps: no console errors", errors.length === 0, errors.join("|"));
    await ctx.close();
  }
  // 5b. touch: tap on map shows tooltip, tap drills down (375 px, touch emulation)
  {
    const { ctx, page, errors } = await open(browser, `${B}/maps.html`, 375); await settled(page);
    await page.locator('[data-chart="choropleth"]').scrollIntoViewIfNeeded();
    const p0 = await pt(page, '[data-chart="choropleth"]', "(() => { const p = c.convertToPixel({ seriesIndex: 0 }, [21, 52.2]); return [r.x + p[0], r.y + p[1]]; })()");
    await page.touchscreen.tap(p0[0], p0[1]); await page.waitForTimeout(1000);
    const st = await page.evaluate(() => ({ lvl: Votw.registry.find((c) => c.spec.id === "choropleth").extra.level, w: document.documentElement.scrollWidth }));
    check("touch: tap on a voivodeship drills down", st.lvl === "14", JSON.stringify(st));
    await page.screenshot({ path: path.join(outDir, "maps-touch-tap-drilldown-375.jpg"), type: "jpeg", quality: 60 });
    await page.locator('[data-chart="bubbles"]').scrollIntoViewIfNeeded();
    const p1 = await pt(page, '[data-chart="bubbles"]', "(() => { const p = c.convertToPixel({ geoIndex: 0 }, [21.0122, 52.2297]); return [r.x + p[0], r.y + p[1]]; })()");
    await page.touchscreen.tap(p1[0], p1[1]); await page.waitForTimeout(700);
    const tip = await page.evaluate(() => document.querySelector('[data-chart="bubbles"]').innerText);
    check("touch: tap on a city bubble shows its tooltip", /Size index/.test(tip), tip.replace(/\n/g, " ").slice(0, 60));
    await page.screenshot({ path: path.join(outDir, "maps-touch-tap-bubble-375.jpg"), type: "jpeg", quality: 60 });
    check("touch: no console errors", errors.length === 0, errors.join("|"));
    await ctx.close();
  }

  // 6. forced failure path: block the data file, expect the error state, then recover on retry
  {
    let block = true;
    const { ctx, page, errors } = await open(browser, `${B}/charts.html`, 375, { setup: (pg) => pg.route("**/data/demo.json", (r) => (block ? r.abort() : r.continue())) });
    await page.waitForFunction("Votw.registry.every(c => c.state === 'error')", null, { timeout: 15000 });
    const msg = await page.evaluate(() => document.querySelector('[data-chart-card="line"] .state--error')?.innerText);
    check("failure path: blocked data shows the error state with a message", /Could not load the data/.test(msg || "") && /Try again/.test(msg || ""), (msg || "").replace(/\n/g, " ").slice(0, 80));
    check("failure path: footer still present in error state", await page.evaluate(() => document.querySelectorAll("[data-chart-card] footer.chart-source").length === Votw.registry.length));
    await page.screenshot({ path: path.join(outDir, "failure-path-error-state-375.jpg"), type: "jpeg", quality: 60 });
    block = false;
    await page.click('[data-chart-card="line"] [data-retry]'); await page.waitForTimeout(1500);
    check("failure path: Try again recovers", await page.evaluate(() => Votw.registry.find((c) => c.spec.id === "line").state === "ready"));
    check("failure path: only the expected request error", errors.every((e) => /demo\.json|ERR_FAILED|Failed to load/.test(e)), errors.join("|").slice(0, 200));
    await ctx.close();
  }

  fs.writeFileSync(path.join(outDir, "results.json"), JSON.stringify({ failures, results }, null, 1));
  await browser.close();
  console.log(failures ? `\n${failures} check(s) FAILED` : "\nall checks passed");
  process.exit(failures ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
