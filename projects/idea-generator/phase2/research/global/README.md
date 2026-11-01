# Global trend lists (T04): patterns

Cross-country view of the fastest-growing new products, focused on LLM-native products launched or broken out since 2023. All sources accessed **2026-11-01**. Catalogue: [../../catalogue/R0-global.csv](../../catalogue/R0-global.csv), **104 rows**, every row with a traction figure and its source.

## Files (one per source family)

| File | Source family | Rows |
|---|---|---|
| [a16z-consumer.md](a16z-consumer.md) | a16z Top 100 Gen AI Consumer Apps (6th and 5th editions; all-star list across 5 editions) | 16 |
| [revenue-leaders.md](revenue-leaders.md) | TrustMRR (verified revenue), ARR Club Q3 2026 AI 100 / Velocity 20; Indie Hackers (bot-blocked) | 14 |
| [funding-and-rankings.md](funding-and-rankings.md) | Forbes AI 50 2026, CB Insights AI 100 2026, TechCrunch $100M+ trackers 2025–26, European leaders | 24 |
| [yc.md](yc.md) | Y Combinator W24–F26 (2,025 companies screened via the directory data) | 42 |
| [g2-producthunt-rounds.md](g2-producthunt-rounds.md) | G2 fastest-growing 2026, Product Hunt (awards discontinued), European Series A/B | 8 |

**Choices recorded**
- **IDs** use the prefix `R0` (global list) so they never collide with the regional catalogues of T05–T14: `R0-<ISO country>-<NNN>`, numbered across the file. The `region` column holds the HQ's real region (R1–R10), as `method/criteria.md` defines.
- **country** = HQ country (task rule). Founder origin is noted in `country_specific` where relevant (ElevenLabs: Polish founders; Higgsfield: Kazakh founders).
- Chinese and Russian apps, big-tech assistants, model labs, chips/compute and AI-lab data vendors were not catalogued (no adaptation angle or outside the 51 countries).
- The CSV is written with every field quoted, so the link checker reads URLs cleanly.
- `works_in_polish` is `unknown` in every row: no product was tried in this task (brief rule 1 applies per idea in T16–T18 and write-ups).
- `durable_signals` is filled only where a source shows the signal; otherwise `unknown`. "All-star on a16z" is recorded as a proxy for signal 3 and labelled as such.

## Patterns

1. **Coding agents and app builders are the revenue core of LLM-native software** (Cursor 4B USD ARR, Lovable ~600M, Cognition ~1B, Replit; Claude Code 1B run rate in ~6 months). Global, language-agnostic, no Polish angle except prebuilt local integrations for SMB app builders. ([revenue-leaders.md](revenue-leaders.md), [a16z-consumer.md](a16z-consumer.md))
2. **Voice agents are the most crowded B2B category in every source**: G2 (Retell #3, Synthflow #4), YC (Retell, telli, Freya, Domu, CollectWise), Europe's biggest applied rounds (Parloa 3B, ElevenLabs 11B), trades-specific (Elyos). The voice layer already handles Polish; the gap is vertical workflows on top (clinics, trades, couriers, collections).
3. **Regulated, document-heavy verticals carry the large B2B rounds**: legal (Harvey, Legora, EvenUp, Eudia), healthcare admin (Abridge, Ambience, Hippocratic, Tennr, OpenEvidence), insurance (FurtherAI, ClaimSorted, Corgi, Harper), financial-crime compliance (Bretton, Cardamon, Gradient Labs). Many need licences (insurance carriers/brokers, lending) and fail the founder's L7 filter; legal, claims, AML case work and admin documentation do not.
4. **"AI replaces the agency/outsourcer"**: Uplane (marketing agencies), throxy and Artisan (SDRs), AEO Engine (SEO agency → AI-answer visibility), Conveo (research fieldwork), OffDeal (SMB sell-side bank), ClaimSorted (claims TPA), Balance (in-house finance hire). These name the budget line they replace (durable signal 1) in their positioning.
5. **Country-bound back-office products exist outside the US and are the closest template for a Polish adaptation**: Beglaubigt.de (German registers and notaries), autarc (German energy installers), Tabula (German accounting), Cifrato (Colombian e-invoicing/tax for accounting firms), Parallel (French hospital admin), General Learning (per-curriculum tutors), Kibu (US disability-care documentation). 25 rows are marked `country_specific = y`, 23 `partly`.
6. **Trade-specific tools beat horizontal ones on adoption momentum**: Handoff (AI remodelling estimates; G2 #5, 40K+ contractors), Mercura (RFQ-to-quote for technical distributors), Sandra AI (car dealers), Brickanta (construction tenders), Elyos (trades front office).
7. **Compliance automation is a fast indie and seed category**: Comp AI (6.55M USD revenue in <2 years), Complir ("Vanta for physical products"), ComplyDo, Cardamon. Polish analogues ride dated triggers: KSC/NIS2, GPSR, BDO/EPR, AML.
8. **Hype markers are concentrated in consumer creative tools**: tourist ratios (SEOBOT ~200k users vs 489 payers; Taja ~256k vs 347), burn (Higgsfield ~4M USD/month), absorption (AI slides into ChatGPT/Canva; email/notes into Gmail/Outlook/Zoom), DeepSeek and Sora traffic falls, lifetime plans (Rezi). 18 rows carry a hype warning.

**Shortlist of adaptation angles worth carrying into T15–T18** (from `pl_adaptation_angle`): Polish compensation claims letters (EvenUp → kancelarie odszkodowawcze); remodelling estimates on KNR/Sekocenbud (Handoff); KRS/S24/CRBR company back office (Beglaubigt.de); installer paperwork for Czyste Powietrze/Mój Prąd (autarc); KSeF/JPK agents for biura rachunkowe (Cifrato, Tabula, Balance, Light); RFQ-to-quote for Polish technical wholesalers (Mercura); property-manager and housing-community messaging (EliseAI, Brickwise); AML case work for obliged entities (Bretton); KSC/NIS2 and GPSR/BDO compliance packs (Comp AI, Complir); disability-care documentation for ŚDS/DPS (Kibu); trades missed-call booking (Elyos); tax research over KIS interpretations (TaxGPT); matura prep on CKE criteria (General Learning).

## Coverage
- **Catalogue:** 104 rows; all 104 have a traction figure with source and access date. 15 rows have at least one sourced durable signal, 18 have a hype warning, 5 have a known first channel. B2B 82, B2C 16, B2B2C 6.
- **Countries (HQ):** United States 62, United Kingdom 15, Germany 10, France 4, Sweden 3, Denmark 2, Hong Kong 2, Turkey 2, Singapore 1, Australia 1, Belgium 1, Colombia 1. Regions: R1 62, R2 15, R3 11, R4 5, R5 4, R7 3, R9 2, R8 1, R10 1; R6 (CEE) 0.
- **Source families done:** 5 files covering all source families in the task: YC, a16z (all editions via the 6th/5th and all-star list), Forbes AI 50, CB Insights AI 100, Product Hunt, TrustMRR, Indie Hackers (blocked), G2, Series A/B rounds (TechCrunch, tech.eu).
- **Sources:** 193 distinct URLs across the 6 files and the CSV, about 75 of them sources read (the rest are product home pages and YC company pages; link check 2026-11-01: 193 links, 190 ok, 0 dead, 3 unverifiable: g2.com list page, verdict.co.uk, openevidence.com — all 403 bot-blocking).
- **Searches run:** about 25 web searches plus ~30 page fetches; YC directory data read directly (2,025 companies screened).
- **Searched and found nothing:** full Forbes AI 50 2026 list; Product Hunt Orbit Awards winners; G2 ranks 6–100; TrustMRR beyond the first 30 AI listings; Indie Hackers (blocked); retention/NRR figures for almost every product.

## Gaps
- **Durable signals are thin**: retention and expansion data were found for almost no product; `durable_signals` is `unknown` in 89 rows. T15 should treat most rows as "unproven" until regional scans add evidence.
- **US bias** (62 of 104): the global lists are US-centric. Regional scans T06–T14 must supply Europe, Asia and CEE; no CEE company appeared in any global list.
- **Weak traction type for YC rows** (42): team size only (fast-hiring proxy), no revenue.
- **Not catalogued for lack of a verified product or traction:** 47 CB Insights AI 100 2026 applied names (listed in funding-and-rankings.md), TradeInt, Wonderful, Andercore, Plato, Orbio, MEDVi.
- **works_in_polish** untested for all rows.
- CB Insights AI 100 2025, a16z 4th and earlier editions, Launch YC posts and Requests for Startups not read directly.
