#!/usr/bin/env node

// Simple verification script for visualization charts
// Checks for common issues without requiring additional dependencies

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node scripts/check_viz.mjs <html-file>');
  process.exit(2);
}

const htmlFile = args[0];
const filePath = join(process.cwd(), htmlFile);

console.log(`🔍 Checking visualization: ${htmlFile}`);
console.log(`📂 File path: ${filePath}`);

try {
  const htmlContent = readFileSync(filePath, 'utf8');
  
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
  
  // Check 1: Source footer present
  const hasSourceFooter = htmlContent.includes('chart-source') && 
    (htmlContent.includes('Source:') || htmlContent.includes('Źródło:'));
  check('Source footer present', hasSourceFooter, 
    'Every chart must have a Source footer with proper attribution');
  
  // Check 2: No console errors pattern (basic check)
  const hasScriptErrors = htmlContent.includes('console.error') || 
    htmlContent.includes('ReferenceError') || 
    htmlContent.includes('TypeError');
  check('No obvious script errors', !hasScriptErrors, 
    'Check browser console for JavaScript errors');
  
  // Check 3: Has chart container
  const hasChartContainer = htmlContent.includes('id="figures"') || 
    htmlContent.includes('[data-chart]') || 
    htmlContent.includes('class="chart"');
  check('Chart container present', hasChartContainer, 
    'HTML should contain chart mounting points');
  
  // Check 4: Has Votw.figure usage
  const usesVotwFigure = htmlContent.includes('Votw.figure') || 
    htmlContent.includes('votw-charts.js');
  check('Uses Votw.figure()', usesVotwFigure, 
    'Charts should be created with Votw.figure()');
  
  // Check 5: Has proper source attribute
  const hasSourceAttribute = htmlContent.includes('source:') || 
    htmlContent.includes('DEMO_SOURCE');
  check('Proper source attribution', hasSourceAttribute, 
    'Chart specs must include source information');
  
  // Check 6: Uses design system tokens
  const usesTokens = htmlContent.includes('var(--') || 
    htmlContent.includes('cssVar(') || 
    htmlContent.includes('tokens.css');
  check('Uses design system tokens', usesTokens, 
    'All styling should use design system tokens only');
  
  // Check 7: Has accessibility attributes
  const hasAccessibility = htmlContent.includes('aria-') || 
    htmlContent.includes('role="img"') || 
    htmlContent.includes('alt="');
  check('Has accessibility attributes', hasAccessibility, 
    'Charts should include proper accessibility attributes');
  
  // Summary
  console.log('\n📋 VERIFICATION SUMMARY:');
  console.log(`   Total checks: ${results.length}`);
  console.log(`   Passed: ${results.length - failures}`);
  console.log(`   Failed: ${failures}`);
  
  if (failures > 0) {
    console.log('\n🔧 FAILED CHECKS:');
    results.filter(r => !r.ok).forEach(r => {
      console.log(`   - ${r.name}: ${r.detail}`);
    });
    console.log('\n⚠️  Note: This is a basic static check. For full verification,');
    console.log('   serve the page and run the full browser-based checks.');
    process.exit(1);
  } else {
    console.log('\n🎉 ALL BASIC CHECKS PASSED!');
    console.log('\n💡 For complete verification, serve the page and run:');
    console.log('   python3 -m http.server 8000');
    console.log('   node projects/visualization-of-the-world/site/scripts/check_footers.cjs http://localhost:8000/');
    process.exit(0);
  }
  
} catch (error) {
  console.error('❌ Error reading file:', error.message);
  process.exit(1);
}