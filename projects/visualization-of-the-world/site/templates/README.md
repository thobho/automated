# Chart Templates

This directory contains copy-and-adapt templates for the most commonly used visualization components. Each template is already in the design system and passes the required checks.

## Available Templates

### Basic Structure Templates
- `chart-template.html` - Basic chart page structure with all required components
- `line-chart-template.html` - Line chart with time series data
- `bar-chart-template.html` - Bar chart for categorical comparisons
- `stacked-chart-template.html` - Stacked area/bar charts showing composition

### Map Templates
- `map-choropleth-template.html` - Geographic choropleth maps with regional data
- `map-bubbles-template.html` - Point data bubble maps

### Interactive Component Templates
- `timeline-slider-template.html` - Charts with timeline playback controls
- `place-toggle-template.html` - Charts with place type filtering
- `source-footer-template.html` - Proper source footer implementation

## How to Use Templates

1. Copy the template that best matches your chart type
2. Rename the file appropriately
3. Modify the chart specification in the JavaScript section:
   - Update `id`, `title`, and `subtitle`
   - Adjust the `source` object with proper attribution
   - Customize the `load()` function for your data
   - Modify the `build()` function for your visualization
   - Adjust the `csv()` function for data export
4. Test the chart with the verification script

## Design System Compliance

All templates follow the project's design system rules:
- Use only CSS variables from `tokens.css`
- Include proper source footers with attribution
- Implement responsive layouts
- Follow accessibility guidelines
- Use vendored libraries only (no CDNs)

## Verification

After creating a chart, verify it passes all checks:

```bash
# Serve the site
cd projects/visualization-of-the-world/site
python3 -m http.server 8000

# Run verification (requires Playwright)
node scripts/check_footers.cjs http://localhost:8000/
node scripts/verify_site.cjs http://localhost:8000/ docs/verification/

# Or use our simplified checker
node ../scripts/check_viz.mjs path/to/your/chart.html
```

## Common Modifications

### Changing Data Source
Replace the `load()` function with your data loading logic:

```javascript
async load() {
  // For JSON data
  return fetch('/path/to/data.json').then(r => r.json());
  
  // For CSV data
  const csvText = await fetch('/path/to/data.csv').then(r => r.text());
  return VotwCore.parseCsv(csvText);
  
  // For existing data functions
  return await Votw.data.regions();
}
```

### Customizing Visuals
Use design system tokens for consistent styling:

```javascript
build(d) {
  return Votw.base({
    // Use color tokens
    color: [Votw.cssVar("--data-cat-1"), Votw.cssVar("--data-cat-2")],
    
    // Use spacing tokens
    grid: Votw.grid({ top: 20, bottom: 40 }),
    
    // Use typography tokens
    textStyle: Votw.textStyle({ fontSize: 12 }),
    
    // Use chart-specific tokens
    itemStyle: { color: Votw.placeColor("villages") }
  });
}
```

### Adding Interactions
Add custom controls using the `controls()` function:

```javascript
controls(container, ctl) {
  container.innerHTML = `
    <div class="custom-controls">
      <button id="custom-button">Custom Action</button>
    </div>
  `;
  
  container.querySelector('#custom-button').addEventListener('click', () => {
    // Custom interaction logic
    ctl.render();
  });
}
```

## Troubleshooting

### Source Footer Issues
Ensure every chart spec includes a complete `source` object:

```javascript
source: { 
  label: "Publisher, table", 
  url: "https://...", 
  meta: "access date etc." 
}
```

### Empty Charts
Return `"empty"` from the `build()` function to show the empty state:

```javascript
build(d) {
  if (!d || d.length === 0) return "empty";
  // ... rest of chart building
}
```

### Mobile Responsiveness
Use responsive functions for sizing:

```javascript
height: (w) => (w < 600 ? 320 : 360)
```

### Accessibility
Ensure charts have proper `aria-label` attributes and semantic HTML.