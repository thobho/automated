# T15 — consolidate catalogue into themes

**Model:** fable (medium effort) · **Needs:** T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14

Read `projects/idea-generator/phase2/BRIEF.md` first and follow its Rules. Commit and push after every small unit and keep your Resume line in `phase2/PROGRESS.md` current. Run the link check on changed files before reporting DONE.

Merge every `catalogue/*.csv` (expect 500+ rows) and cluster the products into **40–80 themes**, i.e. patterns such as "AI receptionist for local service businesses" or "AI scribe for X". Fill the `theme` column in every catalogue row.

Write `themes/THEMES.md`. For each theme give:
- a one-line description and the LLM role;
- example products (links to catalogue rows);
- the countries where it appears and the earliest/latest launch dates (diffusion signal);
- the best traction evidence, and a **durability verdict** (durable / mixed / hype) based on the members' durable signals and hype warnings;
- B2B/B2C;
- a first thought on the Polish angle.

Rank the themes by spread across countries, durable traction (not raw growth) and novelty, and explain the ranking rule at the top. Split the ranked list into three equal batches, **A / B / C** (A = highest ranked), for the Poland checks.

**Done when:** every catalogue row has a theme, THEMES.md lists 40–80 ranked themes in batches A/B/C, and the link check passes.
