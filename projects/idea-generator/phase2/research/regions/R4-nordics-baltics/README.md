# R4 Nordics & Baltics (T08): patterns and coverage

Sweden, Norway, Denmark, Finland, Iceland, Estonia, Latvia, Lithuania (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R4-nordics-baltics.csv](../../../catalogue/R4-nordics-baltics.csv), **40 rows** (SE 7, NO 5, DK 5, FI 5, IS 2, EE 6, LV 5, LT 5), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [sweden.md](sweden.md) | scribe, municipal AI platform, accounting agents, legal knowledge, MEP design, property ops, interview bot (SE-001…007) |
| [norway.md](norway.md) | GP scribe, legal agent harness, AI engineering firm, installer voice agent, invoice-vs-contract checks (NO-001…005) |
| [denmark.md](denmark.md) | open-data legal research, AI audit firm, consumer tax app, e-commerce support agents, medical speech (DK-001…005) |
| [finland.md](finland.md) | GTM agents, private-company M&A data, Finnish-for-residents tutor, specialty-care scribe, light-entrepreneur invoicing (FI-001…005) |
| [iceland.md](iceland.md) | HR agent workflows, receipt app; why Iceland is thin (IS-001…002) |
| [estonia.md](estonia.md) | AI procurement negotiation, AI account managers, voice coach, state chatbot network Bürokratt, budgeting app, language app (EE-001…006) |
| [latvia.md](latvia.md) | Latvian legal research, LLM localization, national-language LLM vendor, requirements engineering, MCP desktop agent (LV-001…005) |
| [lithuania.md](lithuania.md) | SMB AI helpers, enterprise AI gateway, car-rental ops agent (already in PL), AI accounting service, diet app (LT-001…005) |

## Choices recorded
- IDs `R4-<ISO>-NNN`, numbered per country.
- Products already in R0–R3 are not re-added (listed below).
- `works_in_polish` is `unknown` unless a source shows the product handling Polish or operating in Poland. Sigvi (LT-003) is the only row with direct evidence of operating in Poland (launched 2026-06).
- Non-LLM or AI-unclear products are catalogued only where the local pattern matters for Poland, and `llm_role` says so: Skatteguiden (DK), Truster (FI), Kvittun (IS), Persikas (LT), Bilance and Lingvist (EE, LLM use not stated), RoboLabs (LT, AI claimed by a law-firm deal note, not described on its site). That is 7 of 40.
- Bürokratt (EE-004) is a state programme, not a startup; it is catalogued because it decides whether a private public-services assistant has room, which is a Poland-check question.
- Lingvist (EE-006) was added after Lithuania to reach the 40-row floor; it had already been seen in the Estonian chart.
- Region total **40** is at the 40–80 floor. Reasons it is not higher: 5 Stockholm/Copenhagen LLM leaders already sit in R0 (below); Iceland has 2 rows ([iceland.md](iceland.md)); the Baltic and Finnish applied-LLM pipelines are small and mostly horizontal; local-language startup media returned little in the searches used (Breakit and Di Digital paywalled or not surfaced, Estonian/Latvian/Lithuanian queries returned global AI news).

## Cross-country patterns
1. **National case-law research with cited answers is the region's clearest country-specific LLM product.** Pandektes (DK: 500+ customers, revenue x6, customers cancel incumbent subscriptions), Lexu (LV: 2,400+ legal professionals, bar partnership, EE/LT next), Aloi and Newcode for law firms (SE/NO), plus Legora (SE, in R0). Poland has the same open data (ISAP, SAOS, CBOSA), but Libra on LEX already launched in Poland (R3), so general legal research counts as taken; niche regulators' decisions (KIO, UODO, UOKiK, KRRiT) may not be.
2. **National-language clinical scribes spread fast and get bought or go pan-European**: Tandem Health (SE, 10,000 care organisations, 14 markets), Noteless (NO, 61% of Norwegian GPs tried speech-to-note in 2025), Corti (DK), Gosta Labs (FI, backed by a care provider). Same as R2/R3 (Accurx, Juvoly). For Poland the scribe itself is an entry-risk theme; the wedge is NFZ/P1 integration.
3. **The state builds sovereign assistants for the public sector**: Bürokratt (EE, 18 agencies on one LLM chatbot network), Intric (SE, municipalities share assistants), Tilde (LV, sovereign national-language LLM), Danish Foundation Models (DK). In Poland the parallels are Bielik/PLLuM and mObywatel; a private vendor selling to gminy must expect the state to build its own.
4. **AI-native professional firms keep the licensed professional and replace junior work**: Repodo (DK audit), Bluebook (SE accounting agents, site down: warning), RoboLabs (LT AI-based accounting service, 1,300+ firms, acquired by a Norwegian software owner), Paysera's planned AI-first bookkeeping for LT/EE/LV/**PL**. Matches R3's mika and Skalar. For Poland: biura rachunkowe with KSeF/JPK/ZUS.
5. **Learning the national language for residents is a paid local category**: Kielo (FI, LLM-native, #22 Education), WordDive (FI), Speakly and Lingvist (EE). Poland has the bigger driver (~1.5–2M Ukrainians and other migrants needing B1 Polish for residence and citizenship).
6. **AI-native engineering and trades services** (Endra SE, Solvera NO, Installer NO) sell outcomes instead of software.
7. **Baltic founders enter Poland first**: Sigvi launched in Poland in 2026-06; Paysera plans PL bookkeeping; Polish apps (MIA Biznes, Fakturownia, 4grosze) chart in LV and LT Finance, so the markets overlap both ways. For Poland checks this is an entry warning and evidence that CEE adaptation pays.
8. **Consumer charts are global** in all eight countries (ChatGPT, Praktika, Talkpal, Cal AI, BitePal by Reface Lithuania). Local paid apps are utilities without LLMs: tax apps (Skatteguiden DK), invoicing (Truster FI, MobiArve EE), school registers (eKool EE, TAMO LT), driving-theory tests (four KET apps in the LT Education top 30). An LLM tutor for the Polish driving-theory test is an untested idea worth one line in T19.

## Products also in R0 (spread signal)
5 R4-based companies in [R0-global.csv](../../../catalogue/R0-global.csv) were not re-catalogued: **Lovable** (R0-SE-005), **Legora** (R0-SE-032), **Brickanta** (R0-SE-081) from Sweden, and **Light** (R0-DK-036) and **Complir** (R0-DK-092) from Denmark. Seen in R4 top-grossing charts on 2026-11-01: ChatGPT, Claude, Perplexity (global), Praktika (R2), Cal AI (R1), Talkpal. Themes repeating from R1–R3: AI scribes (Tandem/Noteless/Corti vs Abridge/Accurx/Juvoly), legal research (Pandektes/Lexu vs Libra/Legal Mind), AI-native accounting (Repodo/RoboLabs vs mika/Skalar/Basis), voice agents for trades (Installer vs fonio), SMB AI employees (Sintra vs R0 agents).

## Polish adaptation angles from R4 (for T15–T18)
- **Polish-for-migrants conversation tutor** tied to B1 exams, urząd letters and workplace vocabulary, sold to employers, schools and gminy (Kielo, Lingvist).
- **Regulator-decision research** (KIO, UODO, UOKiK, KRRiT, RIO) where LEX/Legalis coverage is thin (Pandektes, Lexu).
- **Assistant for gminy/powiaty** over BIP, uchwały and ePUAP forms, hosted on Bielik/PLLuM, with the Bürokratt risk in mind (Bürokratt, Intric, Tilde).
- **Supplier-invoice vs contract checks** for Polish SMEs with KSeF data (Watchdog NO).
- **SME supplier negotiation agent** in Polish, PLN and VAT for tail spend (Pactum, enterprise-only today).
- **Tech-enabled biuro rachunkowe** on KSeF/JPK/ZUS (RoboLabs, Repodo), with Paysera as a named entrant.
- **PIT/payslip explainer** for employees and light entrepreneurs (Skatteguiden, Truster; no LLM yet in either).

## Coverage

| Country | Status | New rows | R0–R3 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Sweden | done | 7 | 3 (R0) | 21 | 7 pages + 4 feeds | 7 | Bluebook site down |
| Norway | done | 5 | 0 | 10 | 5 pages + 4 feeds | 8 | 3 fetches blocked |
| Denmark | done | 5 | 2 (R0) | 13 | 6 pages + 4 feeds | 7 | 2 non-LLM/older rows (Skatteguiden, Corti founded 2016) |
| Finland | done | 5 | 0 | 12 | 5 pages + 4 feeds | 8 | 1 non-LLM row (Truster) |
| Iceland | thin | 2 | 0 | 7 | 1 page + 4 feeds | 2 | tiny market; reason in iceland.md |
| Estonia | done | 6 | 0 | 12 | 6 pages + 4 feeds | 7 | 1 state programme, 2 chart rows with unclear LLM use |
| Latvia | done | 5 | 0 | 8 | 7 pages + 4 feeds | 6 | 3 of 5 horizontal/global |
| Lithuania | done | 5 | 0 | 13 | 8 pages + 4 feeds | 6 | 1 already operating in PL (Sigvi) |
| **R4** | done | **40** | 5 | 96 | 45 pages + 32 feeds | 51 | |

- Durable signals: sourced for most rows, mostly 1 (replaced spend), 5 (channel), 7 (pricing) and 8 (hard to absorb). Retention/expansion (signals 3/4): Pandektes (customers ~100 → 500+, revenue x6, trialists cancel incumbents), Pactum (2024 ARR x2.5, value handled +489%), Vocal Image (ARR 6.5M → 12M USD), Sintra (12M USD ARR, 40,000+ paying). Hype warnings: Bluebook's site down 20 months after its pre-seed, Handhold and Sintra pivot/relaunch before their rounds, Bürokratt publishes no usage metrics, Desktop Commander has no paid product yet.
- Searched and found nothing: LLM startups with traction for Skatteverket, NAV, Kela, Vero, EMTA, VID or VMI filings; benefit applications (Försäkringskassan, NAV, Kela, Sodra); Nordic or Baltic LLM payroll startups; NRR or cohort retention for any R4 row. Google Play (Similarweb) charts were not read; accelerator batches (Startup Wise Guys, Tehnopol, Sting, Antler Nordics) were seen only through news items.
- Bot-blocked or failed fetches: techsavvy.media (403), sifted.eu (403), tidsskriftet.no (403), startupresearcher.com (429), lithuania.lt (403), techindex.law.stanford.edu (TLS certificate rejected), The Recursive Latvia list (paywalled after the first round).
- Link check 2026-11-01 (R4 files + CSV): 115 links, 109 ok, 0 dead, 6 unverifiable (di.ku.dk and sodas.ku.dk timeouts, tech.slator.com 403, lsm.lv 403 but read with the fetch tool, regjeringen.no 403, techsavvy.media 454). One dead link was fixed earlier in the Iceland commit.
