// Failure path: block the data files and check each page shows a readable error instead of a blank chart.
// Usage: node scripts/check_failure.cjs <base-url> <out-dir>
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const [base, outDir] = process.argv.slice(2); let failed = 0;
(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  for (const lib of ['echarts', 'd3-plot', 'vega-lite']) for (const [name, block] of [['line', 'demo-data.json'], ['choropleth', 'voivodeships']]) {
    const page = await (await browser.newContext({ viewport: { width: 375, height: 812 } })).newPage();
    await page.route(new RegExp(block), r => r.abort());
    await page.goto(`${base}/${lib}/${name}.html`); await page.waitForTimeout(1500);
    const msg = await page.evaluate(() => (document.querySelector('p[style*="b00020"]') || {}).textContent || '');
    const ok = /fail/i.test(msg); if (!ok) failed++;
    console.log(lib, name, ok ? 'error shown:' : 'NO ERROR MESSAGE', msg.slice(0, 70));
    if (name === 'choropleth' && lib === 'echarts') await page.screenshot({ path: path.join(outDir, 'failure-blocked-data-375.png') });
  }
  await browser.close(); process.exit(failed ? 1 : 0);
})();
