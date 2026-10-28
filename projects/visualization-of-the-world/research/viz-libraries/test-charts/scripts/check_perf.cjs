// Renders the 2,479-gmina map in each library (3 runs, desktop viewport) and prints the timings the pages record.
// Usage: node scripts/check_perf.cjs <base-url> <out.json>
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const [base, outLog] = process.argv.slice(2); const root = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const out = [];
  for (const url of ['echarts.html', 'plot.html', 'vega-lite.html', 'vega-lite.html?renderer=canvas']) {
    for (let run = 1; run <= 3; run++) {
      const page = await (await browser.newContext({ viewport: { width: 900, height: 700 } })).newPage();
      const errors = []; page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); }); page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${base}/perf/${url}`); await page.waitForFunction('window.__ready === true', null, { timeout: 60000 }).catch(() => errors.push('never ready'));
      const perf = await page.evaluate(() => window.__perf);
      if (run === 1) await page.screenshot({ path: path.join(root, 'perf', url.replace(/[?=.]/g, '-') + '.jpg'), type: 'jpeg', quality: 60 });
      out.push({ page: url, run, perf, errors }); console.log(url, run, JSON.stringify(perf), errors);
    }
  }
  await browser.close(); fs.writeFileSync(outLog, JSON.stringify(out, null, 1));
})();
