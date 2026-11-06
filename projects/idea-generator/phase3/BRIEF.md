# Idea generator — Phase 3 brief: removing friction in buying and ordering

Shared brief for every task in `phase3/tasks/`. Each task file says **what** to do and this brief says **how**. `phase3/PROGRESS.md` tracks state, `phase3/RUNNER.md` describes what a scheduled run does. No GitHub issues or PRs: all state lives in files on the branch `research/idea-generator`. Phases 1 and 2 are finished; read their files freely, never change their tasks.

## Why Phase 3
Phases 1 and 2 looked for **B2B SaaS**. Phase 3 changes the question.

**Find businesses that create value by organising someone's purchase better: better search, matching and classification, a smoother order, a small physical step (a parcel, a booking, a coordination). The AI makes prediction and classification cheap; the money is in removing friction.**

Owner's reasoning, kept in his words: Oponeo, Uber and Deliveroo won by removing friction when ordering a thing. Look for places where the same can be done for products and services that are **needed widely but hard to find** (car parts, air-conditioning parts) and for **hobby niches with no coverage yet**. People may pay a small subscription (or a commission, or a margin) to reach something they currently cannot find.

### What "friction" means here (T03 refines this list)
1. **Finding:** the buyer does not know the right name, part number or search words.
2. **Fit:** the buyer cannot tell whether the item fits their model, car, device or room.
3. **Trust:** unknown seller, quality, fakes, warranty, who handles a return.
4. **Logistics:** it must be collected, delivered, installed or returned by someone.
5. **Coordination:** several parties must agree on a time, a price or a sequence.
6. **Price discovery:** many sellers, no comparable offers.

### Founder profile (same as Phase 2, with one change)
- Skills: strong full-stack developer: Java, Python, Node.js, React, AWS, databases.
- Time: about 40 hours per month for everything that isn't code: marketing, sales, support, operations.
- Budget: 500 PLN per month for tools, ads and validation tests.
- Languages: Polish (native), English.
- How it gets built: mostly by an agentic stack on a home server, with the owner reviewing.
- **Physical work (working assumption, the owner may change it):** at most ~8 hours per month at launch, e.g. sending a parcel, phoning a supplier, confirming a booking. Goods are shipped by the supplier or a fulfilment partner.
- Won't do: a financial or medical licence, large upfront capital, hiring staff, **holding inventory**, heavy on-call operations.

## Business models to consider for every idea
The owner's guess is a small subscription. Test it, do not assume it. Consumers rarely pay a subscription just to search. Record for each idea which models fit and which one is the likely main one:
- **Commission or affiliate:** a share of a sale made at an existing shop or marketplace (Allegro Partner, Ceneo, supplier programmes).
- **Margin on a resold item**, supplier ships directly (dropshipping), no inventory.
- **Service fee** for coordination (a booking, a collection, a managed repair).
- **Subscription:** makes sense for recurring replenishment (filters, cartridges), for professional buyers (HVAC installers, workshops) and for communities, less for one-off consumer purchases.
- **Lead fee** charged to the seller or installer.
Always compute the unit economics in PLN: margin or commission minus delivery, returns, payment fees, support time and customer acquisition cost.

## The test that decides most ideas: the findability gap
Allegro, Google, OLX and Amazon.pl are the incumbent. An idea is only worth building when a buyer who knows what they want **really cannot find it in 2–3 tries today**. T10 runs this test with a fixed protocol; every idea needs a result from it (or a reason why it could not be run).

## Verticals (V1–V5)
| # | Vertical | Examples to look at (not a limit) |
|---|---|---|
| V1 | Vehicle parts and car-related buying | parts by VIN or registration, accessories, tyres, motorcycle, camper, EV charging gear, workshop booking with the right part |
| V2 | Home, climate and appliance parts and consumables | air-conditioning and heat-pump parts, boiler and appliance spare parts by model number, water and air filters, vacuum, coffee machine, tool batteries, replenishment |
| V3 | Hobby niches with thin coverage | modelling, aquariums, 3D printing, mechanical keyboards, audio, fishing, bikes, RC, beekeeping, ham radio, boats |
| V4 | Services with a logistics step | repair by post, sharpening, tailoring, device repair, collection and return, coordinated installation |
| V5 | Small business and professional buying | spare parts for trades, MRO, workshop and salon supplies, "one order for the whole job" for a contractor |

## Depth
| Stage | Depth |
|---|---|
| Poland commerce baseline | 30–50 sourced findings: marketplaces, fees, logistics, returns law, affiliate programmes |
| Friction patterns | 20–30 winning cases, why they won, how they earn |
| Vertical scans (5) | 30–60 businesses per vertical, from ≥8 countries, with traction evidence |
| Demand mining | ≥15 concrete Polish search or forum signals per vertical |
| Findability test | ≥15 hard-to-find queries per vertical, run and recorded |
| Longlist | ~80 ideas, one line each |
| Shortlist | ~25 ideas, quick score |
| Write-ups | ~10 ideas, full template |
| Review | the same ~10, separate sceptical pass |
| Summary | top 5, validation test each, report in English **and Polish** |

Search in English, Polish and the local language where it matters (German for Autodoc-like players, Dutch, French, Japanese). Read product and pricing pages, not only snippets.

## What else matters in this research
1. **Allegro and the platform owner.** For every idea answer: why can't a seller on Allegro, or Allegro itself, do this? "They could add a filter" is a risk to rate.
2. **ChatGPT and Google absorption.** General assistants now answer "which filter fits my model". Value must sit in inventory data, supplier links, fulfilment, trust or a workflow, not in the answer.
3. **Supply side.** Who supplies the goods or the service, on what terms, and will they work with a newcomer? Name 3 real suppliers or distributors per promising idea.
4. **Data.** Where does the compatibility or catalogue data come from, who owns it, and is its use allowed (licences, scraping terms)?
5. **Consumer and product law.** 14-day withdrawal right, warranty (rękojmia), product safety and GPSR, electrical or pressure equipment, hazardous goods, refrigerants (F-gas), alcohol, import and customs. Flag, do not give legal advice.
6. **Logistics and returns economics.** InPost, DPD and others: parcel cost, oversized goods, return rate by category.
7. **Polish buying habits.** BLIK, Przelewy24, cash on delivery, trust in unknown shops, invoices with VAT for firms.
8. **Seasonality and frequency.** One-off purchase or recurring? Retention is the only thing that makes a small subscription work.
9. **Graveyard.** Vertical marketplaces that shut down or pivoted, and why.
10. **Expansion.** Does it extend to CZ/SK/Baltics?

## Success signals: durable vs. hype
Use the durable-signal list from `../phase2/BRIEF.md` (replaces a spend, frequent problem, retention, expansion, owned distribution, time to value, value-based pricing, hard to absorb, pull from customers, timing window) and the same hype warnings. For commerce also record: **repeat-purchase rate, gross margin or take rate, return rate, share of traffic from search or marketplaces** whenever public. An analogue whose growth came only from paid ads or from a subsidy (free delivery, discounts) is a hype warning.

## Rules
- **Never invent facts, numbers, companies, URLs or revenue figures.** Every factual claim needs a source URL plus the date accessed. Mark estimates as such; write "unverified" when you cannot check.
- **Link check before a task is reported done:** `python3 projects/idea-generator/tools/check_links.py <changed files>`. Fix or remove dead links. List "unverifiable" links (403/429 from bot-blocking sites) under the task in PROGRESS.md.
- **Opportunities and risks are separate lists**, each item rated for likelihood and impact (H/M/L); only then pick the chance band.
- **Findability and marketplace searches:** by hand only. Use public search pages in small numbers (tens of queries, not thousands), never log in, never crawl, respect robots.txt and terms. Record the exact query, date and what was found.
- Score honestly. Chance bands: `<5%`, `5–15%`, `15–30%`, `>30%` (the last needs a strong argument). Success means **≥10,000 PLN MRR-equivalent (monthly gross profit or fees, not turnover) within 12 months of launch**. Say clearly whether a figure is turnover, gross profit or recurring fees.
- Prefer concrete and niche over broad. "Marketplace for X" with no entry product and no first 100 buyers is not an idea.
- **Commit and push often** (at most ~20 minutes of uncommitted work). Before each commit update the task's **Resume:** line in `phase3/PROGRESS.md`.
- **Keep folders browsable.** Above ~15 files in a folder, split into subfolders and fix links.
- Write files in English; keep Polish names for institutions, laws and products. The final summary also gets a Polish version.
- Work only in `projects/idea-generator/phase3/`. If something changes an earlier Phase 3 file, update it and log it in `phase3/CHANGELOG.md`.

## Folder layout
```
phase3/
  BRIEF.md  PROGRESS.md  RUNNER.md  CHANGELOG.md  rejected.md
  tasks/NN-<slug>.md
  method/criteria.md  method/verticals.md  method/sources.md
  research/poland/ecommerce.md  logistics-and-returns.md  monetisation.md
  research/global/friction-patterns.md
  research/verticals/VN-<name>.md        one file per vertical scan
  catalogue/VN-<name>.csv                one row per business found
  demand/VN-<name>.md                    Polish demand signals
  findability/VN-<name>.md               test queries and results
  ideas/longlist.md  ideas/shortlist.csv
  ideas/<field>/NNN-<slug>.md            write-ups
  reports/phase3-summary.md  reports/podsumowanie-pl.md
```

## Lenses (1–5 each; `method/criteria.md` defines the rubric)
| # | Lens | Weight |
|---|---|---|
| F1 | Size of the friction (how much the buyer suffers today) | 15% |
| F2 | Breadth and frequency of demand in Poland (searches, repeat purchase) | 15% |
| F3 | Simplicity of fulfilment (supply, shipping, returns without inventory) | 10% |
| F4 | Unit economics in PLN (margin or fee after delivery, returns, CAC) | 15% |
| F5 | AI leverage (matching and classification as a real edge) | 10% |
| F6 | Competition (Allegro, Amazon.pl, producers, existing shops) | 12% |
| F7 | Regulation and liability (consumer law, product safety, data) | 8% |
| F8 | Founder fit (40 h/month, ~8 h physical, no inventory) | 8% |
| F9 | Defensibility (data, supplier ties, community, repeat use) | 7% |

## Write-up template
```markdown
# NNN — <Name>
**One-liner:** …
**Vertical:** V1–V5 | **Model:** commission / margin / service fee / subscription / lead fee | **B2B / B2C**
**Friction removed:** which of the six types, and what the buyer does today
**Analogues:** name, country, URL, launch, traction (revenue, GMV, funding, users, repeat rate)
**Findability gap in Poland:** exact queries tried, date, result (from T10)
**Supply side:** 3 named suppliers or distributors, terms, will they work with a newcomer
**Data:** where the catalogue or compatibility data comes from, rights to use it
**Polish competition:** Allegro sellers, shops, platforms, prices; why they leave a gap
**Demand evidence:** searches, forums, groups, quotes with links; size of the group (with source)
**How AI is used:** matching, classification, search, support; cost per order
**Physical work:** what you do by hand, hours per month at 10, 50 and 200 orders
**MVP (≤6 weeks):** …
**Monetisation:** model(s), PLN price or percentage, who pays; **unit economics per order or per subscriber**
**Distribution, first 100 buyers:** concrete channel and action (SEO, communities, installers, Google Ads)
**Regulation:** consumer law, product safety, F-gas or similar, RODO
**Opportunities (szanse):** items with likelihood H/M/L, impact H/M/L, what would make it true
**Risks (ryzyka):** items with likelihood H/M/L, impact H/M/L, early warning sign
**Success signals:** durable signals shown by analogues, hype warnings, what the Polish version can reproduce
**Graveyard:** similar businesses that failed, and why
**Scores (1–5):** F1 … F9 | **Weighted:** x.x / 5 | **Chance band:** … with 2 sentences of reasoning
**Cheapest validation test (≤2 weeks, ≤300 PLN):** e.g. landing page + Google Ads + manual fulfilment of the first orders
**Kill criteria:** …
**Confidence:** low / medium / high
**Sources:** URLs + access dates
```
The review task adds **Devil's advocate** and **Review changes** sections.
