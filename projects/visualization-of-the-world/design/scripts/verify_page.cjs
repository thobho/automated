// Loads style-guide.html in headless Chromium like a user would and checks it.
// Usage: node scripts/verify_page.cjs <base-url> <out-dir>
//   base-url: where design/ is served, e.g. http://localhost:8714 (python3 -m http.server in design/)
//   out-dir : screenshots + results.json go here (docs/verification when run by hand)
// Needs `playwright` resolvable (NODE_PATH=.../node_modules). CHROMIUM_PATH optionally points to a browser.
// Exit 1 on any failed check.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const [base, outDir] = process.argv.slice(2);
if (!base || !outDir) { console.error("usage: node verify_page.cjs <base-url> <out-dir>"); process.exit(2); }
fs.mkdirSync(outDir, { recursive: true });
const URL_ = base.replace(/\/$/, "") + "/style-guide.html";
const FAMILIES = ["Public Sans Variable", "Schibsted Grotesk Variable", "IBM Plex Sans Variable", "Atkinson Hyperlegible Next Variable"];
const DIRECTION_FONTS = { baltyk: ["Public Sans Variable", "Schibsted Grotesk Variable"], beton: ["IBM Plex Sans Variable"], noc: ["Atkinson Hyperlegible Next Variable"] };
const results = [];
let failures = 0;
const check = (name, ok, detail = "") => {
  results.push({ name, ok, detail });
  if (!ok) failures++;
  console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail ? " - " + detail : ""}`);
};

async function newPage(browser, width, height, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, hasTouch: width < 600, ...opts });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") errors.push(`${m.type()}: ${m.text()}`); });
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("requestfailed", (r) => { if (!opts.allowFailed || !opts.allowFailed.test(r.url())) errors.push("requestfailed: " + r.url()); });
  page.on("response", (r) => { if (r.status() >= 400) errors.push(`http ${r.status()}: ${r.url()}`); });
  return { ctx, page, errors };
}
async function ready(page) {
  await page.waitForFunction("window.__ready === true", null, { timeout: 15000 });
  await page.waitForTimeout(300);
}

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});

  // 1. every direction x theme x width: errors, overflow, fonts, screenshot
  for (const dir of ["baltyk", "beton", "noc"]) {
    for (const theme of ["light", "dark"]) {
      for (const [label, w, h] of [["375", 375, 812], ["wide", 1280, 900]]) {
        const tag = `${dir}-${theme}-${label}`;
        const { ctx, page, errors } = await newPage(browser, w, h);
        await page.goto(`${URL_}?dir=${dir}&theme=${theme}`, { waitUntil: "load" });
        await ready(page);
        const info = await page.evaluate(async (fams) => {
          await document.fonts.ready;
          const faces = [...document.fonts].filter((f) => f.status === "loaded");
          const loaded = faces.map((f) => f.family.replace(/"/g, ""));
          // both subsets (latin + latin-ext) of every family loaded = Polish letters came from our files
          const subsets = fams.map((f) => [f, faces.filter((x) => x.family.replace(/"/g, "") === f).map((x) => /U\+0*100-/i.test(x.unicodeRange) ? "latin-ext" : "latin").sort().join("+")]);
          const cls = document.documentElement.className;
          const bg = getComputedStyle(document.body).backgroundColor;
          const tn = document.querySelector("[data-tnum-sample]");
          const probe = (txt, style) => { const s = document.createElement("span"); s.textContent = txt; Object.assign(s.style, { position: "absolute", visibility: "hidden", whiteSpace: "nowrap", font: getComputedStyle(tn).font }, style); document.body.appendChild(s); const wd = s.getBoundingClientRect().width; s.remove(); return wd; };
          return {
            overflow: document.documentElement.scrollWidth - window.innerWidth,
            loaded: [...new Set(loaded)], subsets,
            polish: fams.map((f) => [f, document.fonts.check(`16px "${f}"`, "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")]),
            cls, bg,
            h1Font: getComputedStyle(document.querySelector("h1")).fontFamily,
            tabular: [probe("1111111", { fontVariantNumeric: "tabular-nums" }), probe("8808080", { fontVariantNumeric: "tabular-nums" })],
            proportional: [probe("1111111", { fontVariantNumeric: "proportional-nums" }), probe("8808080", { fontVariantNumeric: "proportional-nums" })],
            sources: document.querySelectorAll("[data-chart-card] .chart-source a").length,
            charts: document.querySelectorAll("[data-chart-card] svg").length,
          };
        }, FAMILIES);
        check(`${tag}: no console errors`, errors.length === 0, errors.join(" | "));
        check(`${tag}: no horizontal scroll`, info.overflow <= 0, `scrollWidth - innerWidth = ${info.overflow}`);
        const need = DIRECTION_FONTS[dir];
        check(`${tag}: direction fonts loaded`, need.every((f) => info.loaded.includes(f)), `loaded: ${info.loaded.join(", ")}`);
        check(`${tag}: Polish glyphs available in all 4 families`, info.polish.every(([, ok]) => ok), JSON.stringify(info.polish));
        check(`${tag}: latin + latin-ext woff2 loaded for all 4 families`, info.subsets.every(([, s]) => s === "latin+latin-ext"), JSON.stringify(info.subsets));
        check(`${tag}: classes applied`, (dir === "baltyk" || info.cls.includes(`dir-${dir}`)) && info.cls.includes(`theme-${theme}`), `${info.cls} bg ${info.bg}`);
        check(`${tag}: tabular numerals equal width`, Math.abs(info.tabular[0] - info.tabular[1]) < 0.5, `tnum ${info.tabular.map((x) => x.toFixed(1))} vs proportional ${info.proportional.map((x) => x.toFixed(1))}`);
        check(`${tag}: 4 charts drawn, each with a source link`, info.charts >= 4 && info.sources >= 4, `svgs ${info.charts}, source links ${info.sources}`);
        // Full page for the chosen direction; for the token-only alternatives the first screen,
        // the controls and the charts (keeps the committed screenshots small).
        if (dir === "baltyk") {
          await page.screenshot({ path: path.join(outDir, `style-guide-${tag}-full.jpg`), fullPage: true, type: "jpeg", quality: 50 });
        } else {
          await page.screenshot({ path: path.join(outDir, `style-guide-${tag}-top.jpg`), type: "jpeg", quality: 60 });
          await page.evaluate(() => (document.querySelector(".topbar").style.position = "static"));
          await page.locator("#charts .grid").screenshot({ path: path.join(outDir, `style-guide-${tag}-charts.jpg`), type: "jpeg", quality: 60 });
          await page.locator("#controls .controls-grid").screenshot({ path: path.join(outDir, `style-guide-${tag}-controls.jpg`), type: "jpeg", quality: 60 });
        }
        await ctx.close();
      }
    }
  }

  // 2. interactions at 375 px (phone): menu, place toggle, play, tabs, chart keyboard
  {
    const { ctx, page, errors } = await newPage(browser, 375, 812);
    await page.goto(URL_ + "?theme=light", { waitUntil: "load" });
    await ready(page);
    await page.keyboard.press("Tab");
    check("keyboard: first Tab lands on the skip link", await page.evaluate(() => document.activeElement.classList.contains("skip-link")));
    await page.click("[data-menu-button]");
    check("mobile menu opens", await page.isVisible("#mobile-menu"));
    await page.screenshot({ path: path.join(outDir, "mobile-menu-open-375.png") });
    await page.keyboard.press("Escape");
    check("mobile menu closes with Esc", !(await page.isVisible("#mobile-menu")));
    const sizes = await page.evaluate(() => [...document.querySelectorAll("main button:not([disabled]), main input[type=range], main select, main input.input, .topbar button")]
      .filter((e) => e.offsetParent).map((e) => { const r = e.getBoundingClientRect(); return [e.textContent.trim().slice(0, 20) || e.getAttribute("aria-label") || e.tagName, Math.round(r.width), Math.round(r.height)]; })
      .filter(([, w, h]) => w < 44 || h < 44));
    check("touch targets >= 44 px", sizes.length === 0, JSON.stringify(sizes));
    await page.click("#place-toggle-line button[data-place='villages']");
    check("place toggle hides a series (color follows entity)", (await page.$$eval("[data-chart='line'] .series-line", (p) => p.map((x) => x.getAttribute("style")))).join() === "stroke:var(--data-place-big-cities),stroke:var(--data-place-small-cities)");
    await page.click("#place-toggle-line button[data-place='big-cities']");
    await page.click("#place-toggle-line button[data-place='small-cities']");
    check("place toggle keeps at least one on", (await page.$$eval("[data-chart='line'] .series-line", (p) => p.length)) === 1 &&
      (await page.textContent("#place-toggle-line [data-place-status]")).length > 0);
    await page.fill("#year-range", "2000"); await page.dispatchEvent("#year-range", "input");
    await page.click("[data-play]");
    await page.waitForTimeout(1600);
    const yr = +(await page.textContent(".year-player__year"));
    check("play button advances the year and updates the map", yr > 2000 && (await page.textContent("[data-map-year]")) === String(yr), `year ${yr}`);
    await page.click("[data-play]");
    await page.focus("#line-tab-chart"); await page.keyboard.press("ArrowRight");
    check("tabs: arrow key switches to the table", await page.isVisible("#line-panel-table table"));
    await page.keyboard.press("ArrowLeft");
    await page.focus("[data-chart='bars'] svg"); await page.keyboard.press("ArrowDown");
    check("chart keyboard focus shows a tooltip", await page.isVisible("[data-chart='bars'] .tooltip"));
    await page.locator("[data-chart='bars']").scrollIntoViewIfNeeded();
    await page.locator("[data-chart-card='bars']").screenshot({ path: path.join(outDir, "chart-tooltip-keyboard-375.png") });
    check("interactions: no console errors", errors.length === 0, errors.join(" | "));
    await ctx.close();
  }

  // 3. failure path: block the sample data, expect error states with a retry button, then retry succeeds
  {
    let block = true;
    const { ctx, page, errors } = await newPage(browser, 375, 812, { allowFailed: /sample-data\.json/ });
    await page.route("**/sample/sample-data.json", (route) => (block ? route.abort() : route.continue()));
    await page.goto(URL_ + "?theme=light", { waitUntil: "load" });
    await ready(page);
    const n = await page.$$eval("[data-chart-card] .state--error, [data-table-demo] .state--error", (e) => e.length);
    check("failure path: error state shown in every data view", n === 5 && (await page.getAttribute("body", "data-sample")) === "error", `${n} error states`);
    await page.locator("[data-chart-card='line']").scrollIntoViewIfNeeded();
    await page.locator("[data-chart-card='line']").screenshot({ path: path.join(outDir, "failure-path-error-state-375.png") });
    block = false;
    await page.click("[data-chart-card='line'] [data-retry]");
    await page.waitForFunction("document.body.dataset.sample === 'ok'", null, { timeout: 5000 }).catch(() => {});
    check("failure path: retry loads the data", (await page.$$eval("[data-chart-card] svg", (e) => e.length)) >= 4);
    // the blocked request itself logs "Failed to load resource: net::ERR_FAILED" (no URL in the text)
    const real = errors.filter((e) => !/sample-data\.json/.test(e) && !/Failed to load resource: net::ERR_FAILED/.test(e));
    check("failure path: no unexpected console errors", real.length === 0, real.join(" | "));
    await ctx.close();
  }

  // 4. reduced motion
  {
    const { ctx, page } = await newPage(browser, 375, 812, { reducedMotion: "reduce" });
    await page.goto(URL_, { waitUntil: "load" });
    await ready(page);
    const v = await page.evaluate(() => ["--dur-base", "--dur-slow", "--dur-story"].map((n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim()));
    const anim = await page.evaluate(() => getComputedStyle(document.querySelector(".skeleton__bar")).animationName);
    check("reduced motion: durations are 0ms and shimmer is off", v.every((x) => x === "0ms") && anim === "none", `${v} / ${anim}`);
    await ctx.close();
  }

  await browser.close();
  fs.writeFileSync(path.join(outDir, "results.json"), JSON.stringify({ url: URL_, date: new Date().toISOString(), failures, results }, null, 1) + "\n");
  console.log(`\n${results.length - failures}/${results.length} checks passed`);
  process.exit(failures ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
