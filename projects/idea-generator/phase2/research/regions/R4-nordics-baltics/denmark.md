# Denmark (T08)

All sources accessed **2026-11-01**. "Read" = page opened; "excerpt" = search summary only (unverified). Catalogue rows R4-DK-001…005 in [../../../catalogue/R4-nordics-baltics.csv](../../../catalogue/R4-nordics-baltics.csv). Searches in Danish ("AI-startup rejser millioner", "kapitalrunde AI-agent", "Skatteguiden AI skat") and English. techsavvy.media and sifted.eu returned 403 to the fetch tool; their items were taken from search results and marked excerpt.

Context: the Danish state funds open Danish-language models (Danish Foundation Models, 30.7M DKK from the Ministry of Digital Affairs, [KU](https://di.ku.dk/english/news/2024/ministry-of-digital-affairs-grants-30-7-million-to-ambitious-danish-language-model-project/), excerpt). Light and Complir (Copenhagen) are already in [R0-global.csv](../../../catalogue/R0-global.csv).

## Findings

| # | Product | What it does | Traction (date) | Source | Polish angle |
|---|---|---|---|---|---|
| DK-001 | **Pandektes** (Copenhagen) | AI legal research on legislation, rulings and decisions collected from public bodies | Series A 13.5M EUR led by Alstin Capital, 2026-10-05; 500+ customers, up from ~100 in early 2025; revenue x6 in a year; ~2 of 3 trialists buy, many cancel their previous subscription; DK, DE, CH (read). Seed 2.9M EUR 2025-02 ([tech.eu](https://tech.eu/2025/02/04/danish-ai-startup-raises-2-9m-to-revolutionize-the-legal-sector-in-europe/), excerpt) | [The Next Web](https://thenextweb.com/news/pandektes-13-5m-series-a-legal-research) | Challenger to publisher incumbents (Karnov, Beck) built on open legal data. Polish equivalent: ISAP, SAOS, CBOSA, tax interpretations (EUREKA) vs LEX/Legalis; but Libra already runs on LEX in PL (R3) |
| DK-002 | **Repodo** (Copenhagen) | AI-native audit firm: AI does data collection, reconciliations, documentation; auditors sign off | Pre-seed 8.2M EUR led by Hedosophia and Seed Capital, 2026-08-25; SMEs in Denmark first (read); largest Danish pre-seed (Sifted, excerpt) | [tech.eu](https://tech.eu/2026/08/25/lunar-co-founders-launch-ai-audit-startup-repodo-raising-over-eur8m/) | AI-native firm needs a licensed biegły rewident (L7 problem); the founder-fit version is software for small audit firms |
| DK-003 | **Skatteguiden** | Automatic personal-tax app: estimates the annual statement up to 5 weeks before SKAT, finds deductions | **#1 top-grossing Finance** App Store DK on 2026-11-01 ([feed](https://itunes.apple.com/dk/rss/topgrossingapplications/limit=100/genre=6015/json), read); tiers 19/39/79 DKK ([App Store](https://apps.apple.com/dk/app/skatteguiden/id1521428782), excerpt); 200,000 downloads by 2021 ([KU SODAS](https://sodas.ku.dk/research/news-2021/kristoffer-glavind-on-skatteguiden/), excerpt). Not an LLM product | [skatteguiden.dk](https://www.skatteguiden.dk/) | Chart evidence that people pay monthly for personal-tax help. Polish version on Twój e-PIT data with an LLM explaining ulgi and tax letters |
| DK-004 | **Wilmo** (Copenhagen) | Ticketing system built for AI agents: returns, tracking, cancellations, refunds via Shopify, warehouse and shipping integrations | Pre-seed ~1.1–1.3M EUR led by Ugly Duckling Ventures, 2026-08-01; annualised MRR 500k USD in 2026-08 vs 75k USD in 2026-01; 80–95% automation within days (company) (read) | [Nordic9](https://nordic9.com/news/wilmo-raises-11-million-pre-seed-round-at-66m/) | Polish e-commerce support agent on Allegro, Shoper, IdoSell, BaseLinker, InPost |
| DK-005 | **Corti** (Copenhagen) | Medical speech-to-text, ambient documentation and coding models sold to health-IT vendors | Series B 60M USD, 2023-09 (read); 2025–2026 partnerships with Dedalus and Philips SpeechLive (aggregator, excerpt); no 2025–2026 funding or revenue found | [Maginative](https://www.maginative.com/article/corti-secures-60m-in-series-b-funding-to-fuel-healthcare-ai-innovation/), [AI Market Watch](https://www.ai-market-watch.com/company/corti) | Model layer sold through EDM vendors (Asseco, Kamsoft, CGM PL) |

Seen, not catalogued: **Capturi** (Danish conversation analytics, 14M DKK in 2024, pre-LLM framing), **Velatir** (AI governance infrastructure, 5M EUR 2026-08, horizontal), **Cernel** (agentic-commerce infrastructure, 4M EUR seed 2026), **Palette** (3M EUR pre-seed 2026-06, product unclear), Danish insurance-AI and rental-problem startups named only in techsavvy headlines (no names in excerpts).

## App Store charts (top-grossing DK, 2026-11-01)
Local or country-specific: **Skatteguiden** (#1 Finance), **Dinløn** (payslip check, Finance), moneyCapp, **Lectio+** (#2 Education; client for the Lectio school system), Teorikortet (driving theory), Kørebog (mileage log, Business), Selfcast (Business). LLM-era: global apps (ChatGPT, Claude, Plaud, Praktika, Talkpal, Summary AI). The Danish top Finance pair (Skatteguiden, Dinløn) shows **personal tax and payslip checking** as a paid consumer category; neither is LLM-based.

## Patterns (Denmark)
1. **Open-data legal research beats publishers on price** (Pandektes: x6 revenue, customers cancel incumbents). In Poland the same open data exists (ISAP, SAOS, CBOSA, EUREKA), but the publisher LEX already ships LLM search.
2. **AI-native professional firms** (Repodo audit; in R3 Skalar and mika for tax) keep the licensed professional and replace the junior work.
3. **Consumer tax and payslip apps top the Finance chart** without LLMs; an LLM layer that reads PIT-11, payslips and tax letters in Polish would be the next step.

## Coverage (Denmark)
- Products: 5 catalogued (meets ≥5) + 2 in R0 (Light, Complir). Seen, not catalogued: 6. Products researched: 13.
- Sources read: 6 pages + 4 App Store feeds; techsavvy.media and sifted.eu blocked (403), bebeez list 404.
- Searches: 7.
- Found nothing: Danish LLM startups for kommuner, borger.dk/MitID-based services, Danish payroll or property management with public traction; Skatteguiden revenue; Corti revenue.
