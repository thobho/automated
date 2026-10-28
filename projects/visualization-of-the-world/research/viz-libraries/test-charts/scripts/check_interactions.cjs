// Exercises real interactions in headless Chromium at 375 px: tooltips, legend toggle, animation progress.
// Usage: node scripts/check_interactions.cjs <base-url> <out.json>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const [base, outLog] = process.argv.slice(2);
const root = path.resolve(__dirname, '..');
const hash = b => crypto.createHash('md5').update(b).digest('hex').slice(0, 8);
(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const res = [];
  for (const lib of ['echarts', 'd3-plot', 'vega-lite']) {
    const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', m => { if (['error', 'warning'].includes(m.type())) errors.push(m.text()); });
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));
    const shot = async n => page.screenshot({ path: path.join(root, lib, 'screenshots', n + '.png') });
    // --- line: tooltip + legend toggle
    await page.goto(`${base}/${lib}/line.html`); await page.waitForFunction('window.__ready === true'); await page.waitForTimeout(1200);
    const box = await (lib === 'echarts' ? page.locator('#chart canvas') : page.locator('#chart svg')).first().boundingBox();
    if (lib === 'vega-lite') await page.locator('.mark-symbol path').nth(40).hover(); // a data point
    else await page.mouse.move(box.x + box.width * 0.6, box.y + box.height * 0.45);
    await page.waitForTimeout(600);
    const tipVisible = await page.evaluate(lib => {
      const t = lib === 'echarts' ? [...document.querySelectorAll('#chart div')].map(e => e.innerText).join(' ')
        : lib === 'd3-plot' ? [...document.querySelectorAll('#chart [aria-label="tip"]')].map(e => e.textContent).join(' ')
        : (document.querySelector('.vg-tooltip.visible') || {}).innerText || '';
      return /Series [ABC] \(demo\)/.test(t) ? t.replace(/\s+/g, ' ').trim().slice(0, 80) : false;
    }, lib);
    await shot('line-tooltip-375');
    const before = hash(await page.screenshot());
    if (lib === 'echarts') await page.mouse.click(225, 80);          // legend entry "Series B" (canvas coordinates)
    else if (lib === 'd3-plot') await page.getByText('Series B (demo)').click();
    else await page.locator('.role-legend text', { hasText: 'Series B' }).first().click();
    await page.mouse.move(5, 700); await page.waitForTimeout(700);
    const after = hash(await page.screenshot()); await shot('line-legend-toggled-375');
    let toggled;
    if (lib === 'echarts') toggled = await page.evaluate(() => echarts.getInstanceByDom(document.getElementById('chart')).getOption().legend[0].selected);
    else if (lib === 'd3-plot') toggled = await page.evaluate(() => document.querySelectorAll('#chart g[aria-label="line"] path').length + ' line paths');
    else toggled = 'screenshot hash changed';
    res.push({ lib, check: 'line tooltip+legend', tooltipTextOrElementFound: tipVisible, screenshotChangedAfterToggle: before !== after, state: toggled });
    // --- bar animation: two samples
    await page.goto(`${base}/${lib}/bar-animation.html`); await page.waitForFunction('window.__ready === true'); await page.waitForTimeout(900);
    const a = hash(await page.screenshot()); await page.waitForTimeout(1600); const b = hash(await page.screenshot());
    res.push({ lib, check: 'bar animation advances without input', frameChanged: a !== b });
    // --- choropleth tooltip
    await page.goto(`${base}/${lib}/choropleth.html`); await page.waitForFunction('window.__ready === true'); await page.waitForTimeout(1200);
    const px = [230, 270]; // inside the central voivodeships at 375 px for all three pages
    await page.mouse.move(px[0] - 20, px[1] - 10); await page.mouse.move(px[0], px[1], { steps: 8 }); await page.waitForTimeout(700); await shot('choropleth-tooltip-375');
    res.push({ lib, check: 'choropleth hover screenshot taken', errors });
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(outLog, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1));
})();
