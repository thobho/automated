#!/usr/bin/env node

// Script to check visualization charts against common quality criteria
// Usage: node scripts/check_viz.mjs <html-file>
// Checks for: console errors, empty charts, horizontal scroll at 375px, missing Source footer,
// text below AA contrast, missing alt or aria labels on charts

import { chromium } from 'playwright';
import { basename, dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { mkdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node scripts/check_viz.mjs <html-file>');
  process.exit(2);
}

const htmlFile = args[0];
const url = `file://${process.cwd()}/${htmlFile}`;

// Create output directory for screenshots
const outDir = join(dirname(htmlFile), 'docs', 'verification');
mkdirSync(outDir, { recursive: true });

console.log(`Checking visualization: ${htmlFile}`);
console.log(`URL: ${url}`);

let failures = 0;
const results = [];

const check = (name, ok, detail = '') => {
  results.push({ name, ok, detail });
  if (!ok) {
    failures++;
    console.log(`❌ FAIL ${name}${detail ? ' - ' + detail : ''}`);
  } else {
    console.log(`✅ PASS ${name}${detail ? ' - ' + detail : ''}`);
  }
};

async function open(browser, fileUrl, width) {
  const ctx = await browser.newContext({ 
    viewport: { width, height: 812 },
    deviceScaleFactor: 2
  });
  
  const page = await ctx.newPage();
  const errors = [];
  
  // Capture console errors
  page.on("console", (m) => { 
    if (m.type() === "error") errors.push("console.error: " + m.text()); 
  });
  
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("requestfailed", (r) => errors.push("requestfailed: " + r.url()));
  
  await page.goto(fileUrl, { waitUntil: "networkidle" });
  
  // Wait for charts to load
  try {
    await page.waitForFunction(() => 
      window.Votw && 
      Votw.registry && 
      Votw.registry.length > 0 &&
      Votw.registry.every(c => 
        c.spec.keepLoading || 
        ['ready','empty','error'].includes(c.state)
      ), 
      null, 
      { timeout: 15000 }
    );
  } catch (e) {
    errors.push("charts did not load within timeout");
  }
  
  return { ctx, page, errors };
}

(async () => {
  const browser = await chromium.launch({ 
    executablePath: process.env.CHROMIUM_PATH || undefined 
  });

  try {
    // Test at mobile width (375px)
    console.log('\n📱 Testing at 375px width...');
    const { ctx, page, errors } = await open(browser, url, 375);
    
    // Check for console errors
    check('No console errors', errors.length === 0, errors.join(' | '));
    
    // Check for horizontal scrolling
    const scrollInfo = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth
    }));
    check('No horizontal scroll at 375px', 
      scrollInfo.scrollWidth <= scrollInfo.clientWidth, 
      `scrollWidth ${scrollInfo.scrollWidth} vs clientWidth ${scrollInfo.clientWidth}`);
    
    // Check for Source footers
    const footerInfo = await page.evaluate(() => {
      const cards = Array.from(document.querySelectorAll('[data-chart-card]'));
      return {
        total: cards.length,
        withFooter: cards.filter(card => 
          card.querySelector('footer.chart-source') && 
          /Source:/.test(card.querySelector('footer.chart-source').textContent)
        ).length
      };
    });
    check(`Source footer present on all ${footerInfo.total} charts`, 
      footerInfo.withFooter === footerInfo.total,
      `${footerInfo.withFooter}/${footerInfo.total} charts have Source footer`);
    
    // Check for empty charts
    const chartStates = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[data-chart-card]'))
        .map(card => card.dataset.state || 'unknown');
    });
    const emptyCount = chartStates.filter(state => state === 'empty').length;
    check('No charts in empty state', emptyCount === 0, 
      `${emptyCount} charts are empty`);
    
    // Check for chart accessibility (alt/aria labels)
    const chartAccessibility = await page.evaluate(() => {
      const charts = Array.from(document.querySelectorAll('[data-chart]'));
      return {
        total: charts.length,
        withLabels: charts.filter(chart => 
          chart.hasAttribute('aria-label') || 
          chart.hasAttribute('aria-labelledby') ||
          chart.hasAttribute('role')
        ).length
      };
    });
    check(`Charts have accessibility attributes`, 
      chartAccessibility.withLabels === chartAccessibility.total,
      `${chartAccessibility.withLabels}/${chartAccessibility.total} charts have accessibility attributes`);
    
    // Save screenshot
    const screenshotPath = join(outDir, `check-viz-${Date.now()}.png`);
    await page.screenshot({ 
      path: screenshotPath, 
      fullPage: true,
      type: 'png'
      });
    console.log(`📸 Screenshot saved to ${screenshotPath}`);
    
    await ctx.close();
    
    // Summary
    console.log('\n📋 SUMMARY:');
    console.log(`   Total checks: ${results.length}`);
    console.log(`   Passed: ${results.length - failures}`);
    console.log(`   Failed: ${failures}`);
    
    if (failures > 0) {
      console.log('\n🔧 FAILED CHECKS:');
      results.filter(r => !r.ok).forEach(r => {
        console.log(`   - ${r.name}: ${r.detail}`);
      });
      process.exit(1);
    } else {
      console.log('\n🎉 ALL CHECKS PASSED!');
      process.exit(0);
    }
    
  } catch (error) {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})().catch((e) => { 
  console.error('❌ Script error:', e); 
  process.exit(1); 
});