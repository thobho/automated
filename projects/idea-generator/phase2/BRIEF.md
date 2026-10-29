# Idea generator — Phase 2 brief: innovative LLM products to adapt for Poland

Shared brief for every task in `phase2/tasks/`. Each task file says **what** to do and this brief says **how**. `phase2/PROGRESS.md` tracks state, and `phase2/RUNNER.md` describes what a scheduled run does. No GitHub issues or PRs: all state lives in files on the branch `research/idea-generator`.

## Why Phase 2
Phase 1 (`../reports/phase1-summary.md`) produced solid but **not innovative** ideas: mostly compliance and KSeF tooling in crowded markets. Phase 2 changes the question.

**Find genuinely new products, ideally LLM-native, that are growing fast in developed countries and are not yet adapted to Polish realities, where my edge is knowing how to adapt them for Poland.** B2B is preferred, B2C is fine.

The edge is **local knowledge**, not translation. Polish law and institutions, public data and systems, the industry structure, the way Polish customers buy and pay, the culture, and the demographic changes that are creating new demand in Poland.

### Founder profile
- Skills: strong full-stack developer: Java, Python, Node.js, React/frontend, AWS, relational and NoSQL databases.
- Time: about 40 hours per month for everything that isn't code: marketing, sales, support, operations.
- Budget: 500 PLN per month for tools, ads and validation tests.
- Languages: Polish (native), English.
- How it gets built: mostly by an agentic stack on my home server (Hermes agent, opencode, models via OpenRouter), with me reviewing. Favour products that are easy to specify and test automatically.
- Won't do: anything that needs a financial or medical licence, large upfront capital, hiring staff, physical inventory, or heavy on-call operations.

## What counts as innovative here
An idea qualifies when **at least two** of these hold:
1. **LLM-native:** it only became practical with LLMs since 2023 (agents, voice, vision, document understanding, generation), and isn't just a chat box bolted onto old software.
2. **Recent and growing abroad:** launched or broke out since 2023, with visible traction (revenue, funding, chart rank, user numbers, fast hiring).
3. **New behaviour or a new workflow:** it replaces a person's job step, a service or an agency, not just another dashboard.
4. **New demand:** it serves a need that is new or growing fast in Poland: demographic, social, regulatory or technological.

## Countries (51 developed markets)
Grouped into 10 regions. `method/countries.md` tracks coverage per country.

| Region | Countries |
|---|---|
| R1 North America | United States, Canada |
| R2 UK & Ireland | United Kingdom, Ireland |
| R3 DACH & Benelux | Germany, Austria, Switzerland, Netherlands, Belgium, Luxembourg |
| R4 Nordics & Baltics | Sweden, Norway, Denmark, Finland, Iceland, Estonia, Latvia, Lithuania |
| R5 France & Southern Europe | France, Spain, Portugal, Italy, Greece, Malta, Cyprus |
| R6 CEE peers | Czechia, Slovakia, Hungary, Slovenia, Croatia, Romania, Bulgaria |
| R7 East Asia | Japan, South Korea, Taiwan, Singapore, Hong Kong |
| R8 Oceania & Israel | Australia, New Zealand, Israel |
| R9 Gulf & Turkey | United Arab Emirates, Saudi Arabia, Qatar, Kuwait, Bahrain, Turkey |
| R10 Latin America (OECD) | Chile, Mexico, Colombia, Costa Rica, Uruguay |

CEE peers matter twice. Something already adapted in Czechia or Romania is a warning that someone may enter Poland. Something that works there and is absent here is strong evidence that local adaptation pays off. CEE is also the natural expansion path after Poland.

## Depth: broad first, deep at the end

| Stage | Items | Depth |
|---|---|---|
| Poland baseline | demography, AI landscape, local moats | 30–50 sourced findings each |
| Global trend lists | YC, a16z, Product Hunt, revenue boards, AI rankings | 100+ products |
| Regional scans | 10 regions, 51 countries | 40–80 products per region; ≥5 per country or a reason why not |
| Themes | all products clustered | 40–80 themes, ranked by spread across countries and traction |
| Poland check | every theme | gap verdict: open / partial / taken |
| Longlist | ~150 adaptation ideas | one line each |
| Shortlist | ~60 ideas | quick score + reason |
| Write-ups | top ~24 | full template, ≥6 sources, opportunities and risks scored separately |
| Review | the same ~24 | separate skeptical pass |
| Summary | top 5 | validation plan each, report in English **and Polish** |

- Read the sources themselves, not just search snippets: product sites, pricing pages, app store pages, founder posts, funding announcements.
- Search in English, Polish **and the local language** of each country studied (machine-translate as needed). Local startup media and local app store charts find what English sources miss.
- Report coverage in numbers at the end of every research file: sources read, countries, searches run, and what you searched for that found nothing.

## What else matters in this research
Check every idea against these. The write-up template asks about each one.
1. **The "it already works in Polish" trap.** LLM products are often multilingual by default, so a Western product may already serve Poland well in Polish. **Actually try the Western leader**: free tier, demo or docs. Record whether it handles Polish language, Polish documents, Polish integrations, PLN pricing and Polish invoices. If it does, the gap is only in marketing, and that is a weak moat.
2. **The ChatGPT/Copilot absorption risk.** General assistants absorb thin features every quarter. Prefer ideas whose value lives in a workflow, proprietary or local data, integrations, regulation or distribution, not in the prompt.
3. **The localization moat inventory** (`research/poland/local-moats.md`). Name the specific Polish thing a foreign entrant would struggle with: laws and forms (ZUS, KSeF, JPK, KRS, CEIDG, ePUAP, mObywatel, NFZ/IKP, e-Dziennik, księgi wieczyste, Geoportal, SAOS court rulings, ISAP), industry structure, payment habits (BLIK, Przelewy24), logistics (InPost, Allegro), and how Polish customers buy (phone, trust, invoices with VAT).
4. **Purchasing power vs. token costs.** Polish prices are often 40–60% of Western prices, but LLM inference costs are the same everywhere. Compute unit economics with real token prices; a margin that works at 49 USD may fail at 79 PLN.
5. **Polish-language model quality.** Check how well current models handle Polish for the task. Note local models (Bielik, PLLuM) and whether data residency or RODO pushes customers toward EU or local hosting.
6. **EU AI Act.** High-risk uses (hiring, education scoring, credit, essential services) carry heavy obligations. Flag them, and prefer ideas outside high-risk categories or plan for compliance.
7. **Diffusion lag and entry risk.** How long Western trends took to reach Poland before, whether the Western leader has hired in or launched in CEE, and whether a German or Czech adaptation is likely to move in.
8. **The graveyard.** Western products in the same theme that shut down or pivoted, and why. Failures are cheap lessons.
9. **Demographic and social demand in Poland:** ageing and caregiving, ~1.5–2 million Ukrainians and other migrants, low fertility, labour shortages, single-person households, return migration, the urban–suburban shift, health-system queues, mental health, education reforms, rising incomes, housing. A driver turns a "nice to have" into demand.
10. **Dated triggers 2026–2028:** EU Pay Transparency Directive (June 2026), AI Act milestones, European Accessibility Act, NIS2/KSC, CSRD scope changes, KSeF, PPK, EU Digital Identity Wallet, and new Polish regulations found during research.
11. **Who buys and how fast:** the sales cycle for Polish SMEs vs. corporations vs. the public sector (tenders excluded), and channels that work in Poland (associations, chambers, industry Facebook groups, local influencers, partners such as accounting offices).
12. **Exit and expansion:** who could acquire a Polish adaptation, and whether it extends to CZ/SK/RO/HU/Baltics.

## Success signals: durable vs. hype
Fast growth in AI is often temporary. Many AI apps collected revenue from curious users ("AI tourists") who left after a month. Separate **durable** products from **hype** with these signals, gathered for every Western product where they can be found, and later for every Polish idea:

**Durable signals** (the more, the better):
1. **Replaces an existing spend:** a salary, hours of work, an agency, a freelancer, or a penalty for mistakes. Name the line in the customer's budget it comes from.
2. **Frequent, painful problem with an owner:** daily or weekly, and someone is responsible for it.
3. **Retention:** cohort retention that flattens, public churn or NRR figures, "still paying after N months", G2/Capterra reviews from long-term users, renewals, case studies older than a year.
4. **Expansion:** customers pay more over time (seats, clients, volume); public net revenue retention above 100%.
5. **Owned distribution:** how the first customers came. A marketplace, SEO on purchase-intent phrases, a niche community, partners or a built-in viral loop count. "Launched on Product Hunt" alone doesn't.
6. **Time to value in minutes:** a self-serve signup that works without a sales call or week-long setup.
7. **Value-based pricing from day one:** per client, per call, per document or per outcome, not per feature list; no endless free tier.
8. **Hard to absorb:** integrations, data, regulation, trust or workflow that ChatGPT, Copilot or the platform owner can't add in one update.
9. **Pull from customers:** feature requests about integrations and workflow, not "how does this work"; complaints when it breaks.
10. **Timing window:** a regulation or new capability that opened the market recently, before incumbents react.

**Hype warnings:** traffic spikes without retention, revenue mostly from one-off or lifetime deals, growth driven by paid ads or influencers only, a novelty use case (avatars, one-time generators), a product that is a thin wrapper around one model's API, rapid price cuts, or heavy layoffs or a pivot after a funding round.

**How to use them:**
- the catalogue records the signals found for each product (columns `first_channel`, `durable_signals`, `hype_warnings`);
- theme ranking in T15 weighs durable signals, not only growth;
- every write-up has a **Success signals** section: which durable signals the Western analogue shows, with sources, and which ones the Polish adaptation can realistically reproduce;
- an idea whose Western analogue shows only hype warnings can't score above 3 on L2.

## Rules
- **Never invent facts, numbers, companies, URLs or revenue figures.** Every factual claim needs a source URL plus the date you accessed it. Mark estimates as such. If you can't verify something, write "unverified".
- **Link check before a task is reported done:** `python3 projects/idea-generator/tools/check_links.py <changed files>`. Fix or remove dead links. List "unverifiable" links (403/429 from sites that block bots) under the task in PROGRESS.md.
- **Opportunities and risks are separate.** For every idea, think through its opportunities (szanse) and its risks (ryzyka) as two independent lists. Rate each item for likelihood (high / medium / low) and impact (high / medium / low). Only then pick the chance band. Don't let one list mirror the other.
- Score honestly. Use chance bands: `<5%`, `5–15%`, `15–30%`, `>30%` (the last needs a strong argument). Success means **≥10,000 PLN MRR within 12 months of launch**.
- Prefer concrete and niche over broad and vague. "AI for X" with no specific customer and no entry point (wedge) is not an idea.
- **Commit and push often.** A run can stop at any moment when the budget runs out. Commit and push after every small unit: one country, a few products, one theme, one write-up. Never hold more than ~20 minutes of uncommitted work. Before each commit, update the task's **Resume:** line in `phase2/PROGRESS.md`.
- **Keep folders browsable.** When a folder passes ~15 files, split it into subfolders by a natural grouping (region, country, theme, field) and fix the links.
- Write files in English. Keep Polish names for Polish institutions and laws. The final summary also gets a Polish version.
- Work only in `projects/idea-generator/phase2/` (reading Phase 1 files is fine and encouraged). If you find something that changes an earlier Phase 2 file, update it and log it in `phase2/CHANGELOG.md`.

## Folder layout
```
phase2/
  BRIEF.md  PROGRESS.md  RUNNER.md  CHANGELOG.md  rejected.md
  tasks/NN-<slug>.md                 instructions per task
  method/criteria.md                 lenses, rubric, weights, chance bands, opportunity/risk scoring
  method/countries.md                51 countries × coverage status
  method/sources.md                  sources per region and country, plus global lists
  research/poland/                   demography.md, ai-landscape.md, local-moats.md
  research/global/                   cross-country trend lists
  research/regions/RN-<name>/        README.md (patterns, coverage) + one file per country
  catalogue/RN-<name>.csv            one row per product found (columns in criteria.md)
  themes/THEMES.md                   clustered themes, ranked
  poland-check/<batch>/<theme>.md    gap verdict per theme
  ideas/longlist.md  ideas/shortlist.csv
  ideas/<field>/NNN-<slug>.md        write-ups
  reports/phase2-summary.md  reports/podsumowanie-pl.md
```

## Lenses (1–5 each; `method/criteria.md` defines the rubric)
| # | Lens | Weight |
|---|---|---|
| L1 | Innovation / LLM-native | 12% |
| L2 | Durable traction abroad (retention, expansion, revenue and spread across countries, not just growth; see Success signals) | 12% |
| L3 | Poland gap (no Polish equivalent; Western leader serves Poland poorly) | 12% |
| L4 | Localization moat (how much local knowledge the adaptation needs) | 15% |
| L5 | Polish demand, including demographic and social drivers | 15% |
| L6 | Monetization and willingness to pay in PLN (unit economics with token costs) | 10% |
| L7 | Founder fit and buildability (agentic stack, MVP ≤6 weeks) | 8% |
| L8 | Distribution in Poland (first 100 customers) | 8% |
| L9 | Defensibility (against the Western leader entering, general assistants, local copycats) | 8% |

## Write-up template
```markdown
# NNN — <Name>
**One-liner:** …
**Field:** … | **Type:** SaaS / API / mobile app / extension / service / marketplace | **B2B / B2C**
**Western analogues:** name, country, URL, launch date, traction evidence (revenue, funding, rank, users)
**Spread:** in which of the 51 countries the theme appears, and since when
**Does the Western leader already work in Poland?** what you tried and what happened (language, documents, integrations, PLN, invoices)
**Polish adaptation, i.e. the edge:** what exactly must be local (laws, systems, data, industry structure, buying habits) and why a foreign entrant would struggle
**Target customer in Poland:** who, size, role; how many in PL (with source); CEE expansion
**Demand driver:** demographic / social / regulatory / technological, with data
**Polish competition:** names, prices, gaps (also generic tools such as ChatGPT that people use today)
**Evidence of Polish demand:** search trends, forums, job posts, quotes with links
**MVP scope (≤6 weeks):** …
**Monetization:** model, PLN price, who pays; **unit economics** with token cost per customer
**Distribution, first 10 customers:** concrete channel and action
**Regulation:** AI Act category, RODO, sector rules
**Opportunities (szanse):** items, each with likelihood H/M/L, impact H/M/L, and what would make it true
**Risks (ryzyka):** items, each with likelihood H/M/L, impact H/M/L, and the early warning sign
**Success signals:** durable signals the Western analogue shows (with sources), hype warnings, and which signals the Polish adaptation can realistically reproduce (budget line it replaces, first channel, retention driver)
**Graveyard:** similar products that failed, and why
**Scores (1–5):** L1 … L9 | **Weighted:** x.x / 5 | **Chance band:** … with 2 sentences of reasoning
**Cheapest validation test (≤1 week, ≤200 PLN):** …
**Kill criteria:** …
**Confidence:** low / medium / high
**Sources:** URLs + access dates
```
The review task adds **Devil's advocate** and **Review changes** sections.
