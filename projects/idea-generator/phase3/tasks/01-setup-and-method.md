# T01 — setup and method

**Model:** opus (medium effort) · **Needs:** —

Read `projects/idea-generator/phase3/BRIEF.md` first and follow its Rules. Commit and push after every small unit and keep your Resume line in `phase3/PROGRESS.md` current. Run the link check on changed files before reporting DONE.

Set up the Phase 3 method files. BRIEF.md, PROGRESS.md, RUNNER.md and tasks/ already exist.

1. `CHANGELOG.md` and `rejected.md` already exist (empty); keep them.
2. `method/criteria.md`:
   - for each lens F1–F9 of the brief, a 1–5 rubric saying what 1, 3 and 5 mean, with concrete anchors (examples: F1 5 = buyer needs hours or fails to find the item in 2–3 searches on Google/Allegro; F3 5 = supplier ships directly and takes returns, F3 1 = needs stock; F4 5 = gross profit per order covers delivery, returns and CAC with a margin; F6 1 = a big player already serves it well);
   - weights from the brief (change only with a reason);
   - map from weighted score to chance bands: copy the map and the hard rules from `../phase2/method/criteria.md`, adapted to F1–F9; add hard rules: F3 = 1 or F8 = 1 → drop and record in `rejected.md`; F6 = 1 or F1 = 1 → band `<5%`;
   - opportunity/risk rating and how it moves the band (copy the rule from Phase 2);
   - the **catalogue CSV columns**: id, name, country, vertical, url, launched, category, b2b_b2c, friction_types, how_it_earns, physical_step (what is done by hand), ai_role, traction (number + what), traction_source, repeat_signal, take_rate_or_margin, hype_warnings, works_in_poland (unknown/no/partly/yes), pl_adaptation_angle, pattern (filled in T11);
   - a durable-vs-hype rubric for commerce, based on the brief.
3. `method/verticals.md`: V1–V5 with the examples from the brief, search terms in English, Polish, German and one more language each, and the marketplaces and sites to look at.
4. `method/sources.md`: global sources for commerce (marketplace analyses, ecommerce trade media, Shopify and Amazon seller communities, Crunchbase or similar for funding, Similarweb public pages, Google Trends) and at least two local sources per region; for Poland: Allegro public pages, Ceneo, OLX, ecommerce trade media (e.g. wirtualnemedia, e-commerce.pl, Interaktywnie), Poczta/InPost reports, GUS retail data.

**Done when:** the four files exist and are complete, and the link check passes on them.
