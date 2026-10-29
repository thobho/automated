# T09 — regional scan R5 France & Southern Europe

**Model:** fable (medium effort) · **Needs:** T01

Read `projects/idea-generator/phase2/BRIEF.md` first and follow its Rules. Commit and push after every small unit and keep your Resume line in `phase2/PROGRESS.md` current. Run the link check on changed files before reporting DONE.

Scan **France & Southern Europe**: France, Spain, Portugal, Italy, Greece, Malta, Cyprus.

For **each country**:
- top-grossing and fastest-rising apps in the local App Store and Google Play charts (business, productivity, finance, health, education, lifestyle), using the public chart sources in `method/sources.md`;
- local startup media and funding news from 2024–2026 for LLM-based products, searched in the local language;
- local accelerator batches and "AI startup lists" for the country;
- **local champions that solve a country-specific problem with LLMs**: law, tax, public services, health administration, real estate, HR and payroll, education, SMB admin. These matter most: their Polish counterpart needs local knowledge, which is exactly the edge.

Record at least 5 products per country with traction evidence, or explain why fewer exist. For each product, look for the brief's **Success signals** (retention, expansion, replaced spend, first channel) and hype warnings, and fill those catalogue columns; "unknown" is a valid answer, a guess is not.

Output:
- `research/regions/R5-france-southern-europe/<country>.md` with findings and sources, plus `README.md` with cross-country patterns and a Coverage table per country;
- one row per product in `catalogue/R5-france-southern-europe.csv` (columns in `method/criteria.md`). Skip products already in another catalogue file, but mention in the README that they appear here too: spread across countries is a signal;
- update the region's rows in `method/countries.md` (status, products found).

Commit after each country.

**Done when:** every country in the region has a file and a status in countries.md, the region has 40–80 catalogue rows (or a stated reason for fewer), and the link check passes.
