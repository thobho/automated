# Idea generator — Phase 1 brief

This is the shared brief for every task in `tasks/`. Each task file says **what** to do and this brief says **how**. `PROGRESS.md` tracks which tasks are done, and `RUNNER.md` describes what a scheduled run does. This project doesn't use GitHub issues: all state lives in these files on the `research/idea-generator` branch.

## Goal
I'm a software developer based in Poland. Within a month I want to pick one product to build and sell: an app, SaaS, service, library/API or digital product. AI coding agents will do most of the building, so I can build a lot, but my time for marketing, sales and operations is limited.

Phase 1 = research, generate ideas, rank them, and design cheap validation tests for the best few. **Don't build anything.** The output is a ranked shortlist I can validate in week 2, not an encyclopedia.

### Founder profile (use it to judge fit)
- Skills: strong full-stack developer: Java, Python, Node.js, React/frontend, AWS, relational and NoSQL databases, and the common tools around them.
- Time: about 40 hours per month (~10 h/week) for everything that isn't code: marketing, sales, support, operations.
- Budget: 500 PLN per month for tools, ads and validation tests.
- Languages: Polish (native), English
- How it gets built: mostly by an agentic stack on my home server (Hermes agent, opencode, models via OpenRouter), with me reviewing. So favour products that are easy to specify and test automatically, on mainstream stacks. Mark down ideas that depend on pixel-perfect design, native mobile polish, hardware, or integrations that need manual certification or partner approval.
- Won't do: anything that needs a financial or medical licence, large upfront capital, hiring staff, physical inventory, or heavy on-call operations.

## Depth: spend it where it pays
Depth goes up as the funnel narrows:

| Stage | Items | Depth per item |
|---|---|---|
| Lens research | 9 lenses | 15–30 sourced findings each |
| Longlist | ~200 ideas | one line |
| Shortlist | ~100 ideas | one line + quick score + one-sentence reason |
| Write-ups | top ~25 | full template, ≥5 sources |
| Review | the same ~25 | separate skeptical pass |
| Validation plans | top 3–5 | concrete test I can run in ≤1 week |

- Read the sources themselves, not just search snippets: competitor pricing pages, reviews, forum threads, founder revenue posts. Prefer primary sources (company pages, official statistics, laws) over listicles.
- Search in several languages: English, Polish, German, plus the local language of any market you study.
- Use parallel research subagents when available, and check what they bring back.
- Report coverage in numbers, not as a feeling: at the end of each research file, list the sources read, countries covered and searches run, and what you searched for that found nothing.
- Long is fine if every line carries information. No filler.

## Rules
- **Never invent facts, numbers, companies, URLs or revenue figures.** Every factual claim needs a source URL plus the date you accessed it. Mark estimates and assumptions as such. If you can't verify something, write "unverified".
- **Link check before a task is marked done:** `python3 projects/idea-generator/tools/check_links.py <changed files>`. Fix or remove dead links. "Unverifiable" links (403/429 from sites that block bots) are fine; list them under the task in PROGRESS.md.
- Score honestly. Most ideas land in the middle. A 5/5 needs evidence. Use chance-of-success **bands**, not exact percentages: `<5%`, `5–15%`, `15–30%`, `>30%` (the last one needs a strong argument).
- Prefer concrete and niche over broad and vague. "AI for X" with no specific customer and no entry point (wedge) is not an idea.
- Write in English. Keep Polish names for Polish institutions, laws and communities (KSeF, ZUS, Allegro, Wykop).
- Work only in `projects/idea-generator/`. Research is not code: verification means the link check passed, and there is no CI to wait for.
- **Commit and push often.** A run can stop at any moment when the usage budget runs out, and anything not pushed is lost. Commit and push after every small finished unit: a few findings, one idea's write-up, one review. Never sit on more than ~20 minutes of uncommitted work. Use messages like `idea-generator: lens 03 — 6 findings on Allegro seller tools`. Before each commit, update the task's **Resume** line in PROGRESS.md (exactly where you stopped and what's next), so the next run can continue.
- If you find something that changes an earlier task's file (a new competitor, a dead source), update that file and add a line to `CHANGELOG.md`.

## Folder layout
```
projects/idea-generator/
  BRIEF.md               this file
  PROGRESS.md            task checklist with status markers, resume notes, run log
  RUNNER.md              what a scheduled run does
  tasks/NN-<slug>.md     instructions per task
  README.md              what this is, how to read it, current status
  CLAUDE.md              points agents to BRIEF.md; research verification = link check
  CHANGELOG.md           one line per change to already-merged findings or scores
  method/criteria.md     lenses, 1–5 rubric, weights, chance bands, source list
  tools/check_links.py   link checker (+ test)
  research/NN-<lens>/    one folder per lens
    README.md            summary, Seeds, Coverage, Gaps; links to the topic files
    <topic>.md           findings grouped by topic (e.g. dach-saas.md, allegro-sellers.md)
  ideas/longlist.md      ~200 one-liners, grouped by field
  ideas/shortlist.csv    ~100 ideas: id, name, field, type, quick scores, reason, write_up (y/n), path
  ideas/<field>/NNN-<slug>.md   full write-ups (top ~25 only), one folder per field
  rejected.md            every dropped idea + one-line reason (never drop silently)
  reports/phase1-summary.md
```
Keep folders small enough to browse on a phone. When a folder grows past ~15 files, split it into subfolders by a natural grouping (topic, country, field) and update the links that point into it. `<field>` uses short kebab-case names from the field list below (e.g. `ecommerce-sellers`, `legal-compliance`).

## The 9 lenses
Each lens is both a research direction and a scoring criterion.

1. **Proven abroad, missing in Poland.** Services popular in the US, UK, DACH, Nordics, Baltics, Czechia, Netherlands, France, Spain, Japan, Korea, Brazil or India that have no good Polish equivalent. Also consider the reverse: something Polish-specific that could sell across the EU.
2. **Weak or no competition.** Existing tools that are outdated, overpriced, badly reviewed, English-only, or missing. Look at 1–2 star reviews on G2, Capterra and app stores, and at "is there a tool that…" posts.
3. **Clear monetization.** Who pays, how much, and how often. B2B and recurring revenue are preferred. Name the price point and compare it with what customers pay today.
4. **Copy what already makes money.** Products with public revenue: Indie Hackers, TrustMRR, Starter Story, Acquire.com/Flippa, Product Hunt, top lists in the Chrome, Shopify and WordPress stores, Gumroad/Etsy bestsellers, profitable niche creators. For each, think about a localized or adjacent version. *(Overlaps with lens 1. When scoring, lens 1 is about the gap in Poland, lens 4 is about proof that the model makes money. Don't count the same evidence twice.)*
5. **Why now.** Regulation and technology shifts that force demand: KSeF e-invoicing, EU AI Act, European Accessibility Act, NIS2, CSRD/ESG, DAC7, GDPR enforcement, PSD3, energy and heat-pump subsidies, new LLM/agent capabilities (MCP, voice, vision).
6. **Evidence of pain.** Real complaints and requests on Reddit, Wykop, Polish Facebook groups, forums and GitHub issues, plus Google Trends and keyword volume. Quote short snippets with links.
7. **Founder fit and feasibility.** A solo dev with AI agents ships a sellable MVP in ≤6 weeks, with low ops burden and low regulatory risk, and it fits the profile above.
8. **Cheap distribution.** A concrete route to the first 100 customers without big ad spend: a marketplace, low-difficulty SEO, a niche community, a Polish-language moat, partnerships, or outbound to a narrow audience you can list.
9. **Unit economics and defensibility.** Margin after infrastructure and LLM costs, churn, switching costs, data or network moat, platform risk.

Default weights: monetization 15%, pain 15%, competition 12%, founder fit 12%, distribution 12%, unit economics 10%, proven abroad 8%, why now 8%, copy what works 8%. Success means **≥10,000 PLN MRR within 12 months of launch**. The baseline for solo products is low (most fail), and the weighted score moves an idea between bands. `method/criteria.md` spells this out.

## Fields for the longlist
Aim for 5–20 ideas per field: B2B SaaS for Polish SMEs · accounting/invoicing/tax · legal and compliance · HR and payroll-adjacent · e-commerce sellers (Allegro, Shopify, Amazon EU) · developer tools, libraries, APIs · AI agents and automation · data products (public Polish/EU data) · real estate and construction · energy/PV/heat pumps · agriculture · logistics and transport · healthcare admin (non-medical) · education and exams · local services and booking · hospitality and tourism · creators and media · digital products/templates/courses · browser extensions · mobile consumer apps · NGOs and public sector (no tenders) · niche B2B (dental, vet, beauty, workshops, law firms…).

Techniques to use: combine two findings, move a tool from one industry to another, unbundle a big platform, turn a recurring complaint into a product.

## Write-up template (top ~25 only)
```markdown
# NNN — <Name>
**One-liner:** …
**Field:** … | **Type:** SaaS / library / API / mobile app / extension / service / marketplace / digital product
**Target customer:** who, size, role, country; estimated number in PL/EU (with source)
**Problem:** …
**MVP scope (≤6 weeks):** …
**Why now:** …
**Foreign analogues:** name, country, URL, traction/revenue evidence
**Competition (PL / global):** names, prices, gaps
**Evidence of pain:** links + short quotes
**Monetization:** model, price point, who pays
**Revenue sketch (estimate):** MRR at 6 and 12 months, with assumptions
**First 10 customers:** concrete channel and action
**Build complexity:** low / medium / high + key technical risks
**Pros / Cons / Risks:** legal, platform dependency, seasonality, churn
**Scores (1–5):** L1 … L9 | **Weighted:** x.x / 5 | **Chance band:** …
**Cheapest validation test (≤1 week, ≤200 PLN):** …
**Kill criteria:** …
**Confidence:** low / medium / high
**Sources:** URLs + access dates
```
The review task (T16) adds a **Devil's advocate** section and a **Review changes** line to each write-up.
