// Loads every test page in headless Chromium and records console errors, page errors,
// failed requests, horizontal overflow at 375 px, and screenshots.
// Usage: node scripts/check_pages.cjs <base-url> <out-log.json> [lib ...]
// Needs `playwright` resolvable (npm i playwright, or NODE_PATH=.../node_modules).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [base, outLog, ...libs] = process.argv.slice(2);
const LIBS = libs.length ? libs : ['echarts', 'd3-plot', 'vega-lite'];
const PAGES = ['line', 'bar-animation', 'choropleth'];
const root = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const log = [];
  for (const lib of LIBS) for (const name of PAGES) {
    const file = path.join(root, lib, name + '.html');
    if (!fs.existsSync(file)) continue;
    for (const [vp, w, h] of [['375', 375, 812], ['desktop', 1000, 640]]) {
      const ctx = await browser.newContext({ viewport: { width: w, height: h }, hasTouch: vp === '375', deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      const errors = [];
      page.on('console', m => { if (['error', 'warning'].includes(m.type())) errors.push(m.type() + ': ' + m.text()); });
      page.on('pageerror', e => errors.push('pageerror: ' + e.message));
      page.on('requestfailed', r => errors.push('requestfailed: ' + r.url()));
      page.on('response', r => { if (r.status() >= 400) errors.push('http ' + r.status() + ': ' + r.url()); });
      await page.goto(`${base}/${lib}/${name}.html`, { waitUntil: 'load' });
      await page.waitForFunction('window.__ready === true', null, { timeout: 8000 }).catch(() => errors.push('never became ready'));
      await page.waitForTimeout(name === 'bar-animation' ? 2500 : 1500);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      const dir = path.join(root, lib, 'screenshots'); fs.mkdirSync(dir, { recursive: true });
      const shot = path.join(dir, `${name}-${vp}.${vp === '375' ? 'png' : 'jpg'}`);
      await page.screenshot(vp === '375' ? { path: shot } : { path: shot, type: 'jpeg', quality: 70 });
      log.push({ lib, name, viewport: vp, overflowPx: overflow, errors });
      await ctx.close();
    }
  }
  await browser.close();
  fs.writeFileSync(outLog, JSON.stringify(log, null, 1));
  const bad = log.filter(r => r.errors.length || r.overflowPx > 0);
  for (const r of log) console.log(r.lib, r.name, r.viewport, 'overflow', r.overflowPx, r.errors.length ? r.errors : 'no console errors');
  if (bad.length) { console.error(bad.length + ' page run(s) with errors or overflow'); process.exit(1); }
})();
