// Fails when any chart card on any page lacks a "Source:" footer (or when a page has no chart cards).
// Usage: node scripts/check_footers.cjs <base-url>   (site/ served over http; needs playwright, CHROMIUM_PATH optional)
const { chromium } = require("playwright");
const base = (process.argv[2] || "http://localhost:8000").replace(/\/$/, "");
const PAGES = ["index", "charts", "interaction", "maps", "formats", "polish"];
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  let bad = 0, total = 0;
  for (const p of PAGES) {
    const page = await browser.newPage();
    await page.goto(`${base}/${p}.html`);
    await page.waitForFunction("window.Votw && Votw.registry.length && Votw.registry.every(c => c.spec.keepLoading || ['ready','empty','error'].includes(c.state))", null, { timeout: 20000 });
    const cards = await page.evaluate(() => Array.from(document.querySelectorAll("[data-chart-card]")).map((c) => ({ id: c.dataset.chartCard, ok: /^Source:/.test((c.querySelector("footer.chart-source")?.innerText || "").trim()) && !!c.querySelector("footer.chart-source a[href]") })));
    total += cards.length;
    cards.filter((c) => !c.ok).forEach((c) => { bad++; console.error(`MISSING Source footer: ${p}.html #${c.id}`); });
    if (!cards.length) { bad++; console.error(`no chart cards found on ${p}.html`); }
    await page.close();
  }
  await browser.close();
  console.log(bad ? `${bad} problem(s)` : `OK: ${total} charts on ${PAGES.length} pages all have a Source footer`);
  process.exit(bad ? 1 : 0);
})();
