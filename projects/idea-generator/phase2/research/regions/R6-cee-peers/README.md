# R6 CEE peers (T10): patterns and coverage

Czechia, Slovakia, Hungary, Slovenia, Croatia, Romania, Bulgaria (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R6-cee-peers.csv](../../../catalogue/R6-cee-peers.csv), **40 rows** (CZ 11, SK 5, HU 5, SI 4, HR 4, RO 6, BG 5), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [czechia.md](czechia.md) | multi-model AI workspace entering PL (Everbot), compliance agent, retail agents, voice agents, invoice extraction, two legal-AI entrants, creator-clone English tutor, AI receptionists, study app, hiring chat agent (CZ-001…011) |
| [slovakia.md](slovakia.md) | legal + accounting Q&A for SMEs already in PL (Nexana.ai), HR agent with a PL go-to-market plan (Sloneek), ECG AI, comment moderation, IT procurement (SK-001…005) |
| [hungary.md](hungary.md) | accountant marketplace + tax bot (Bookkeepie), avatar video, legacy-code agent, synthetic data, AI language course; Wolters Kluwer's Jogtár/Libra hold legal (HU-001…005) |
| [slovenia.md](slovenia.md) | Astra AI (matura tutor turned pan-European top-grossing app), Mediately (drug reference + AI, in PL), Katalist, Codeplain; why Slovenia is thin (SI-001…004) |
| [croatia.md](croatia.md) | Infobip AgentOS, Robotiq.ai exit, FiskAI on the 2026 e-invoicing mandate, Microblink; why Croatia is thin (HR-001…004) |
| [romania.md](romania.md) | tech-enabled accounting firm on e-Factura/SPV (Declaro), three consumer legal-Q&A models, debt recovery, Bible Chat, Druid AI (RO-001…006) |
| [bulgaria.md](bulgaria.md) | Payhawk agents (>100M USD ARR, Warsaw office), technical-accounting AI, AI CV builder, gym AI, BgGPT in the tax authority (BG-001…005) |

## Choices recorded
- IDs `R6-<ISO>-NNN`, numbered per country. CZ-010 (StudyFi) and CZ-011 (Talentiqa) were found during the Slovakia searches and turned out to be Czech; SI-004 (Mediately) was found during the Croatia searches. Sloneek is filed under Slovakia because sources call it "Czech-Slovak".
- **T10 extra fields** (no new CSV columns, as criteria.md defines a fixed header): each row's `pl_adaptation_angle` starts with `adapts: <Western product or 'no single leader'>; PL: entered / announced / no / unknown`. The country files repeat them as "Adapts" and "Poland" columns. "Entered" means a Polish version, Polish office or Polish customer is evidenced; "announced" means a stated plan.
- `works_in_polish` is `unknown` unless a Polish version was seen (App Store language list, site locale or article); no product was tried in this scan (time budget).
- Rows with no or unclear LLM core are kept where the local pattern matters, and `llm_role` says so: PMcardio (SK-003, deep learning), DiffuseDrive (HU-004, diffusion), Xeropan (HU-005, pre-LLM app with AI layer), Robotiq.ai (HR-002, RPA), Microblink (HR-004, vision), Digitoo (CZ-005, LLM use not stated), Declaro (RO-001, selective AI). That is 7 of 40.
- BgGPT (BG-005) is a state programme, catalogued like Bürokratt (R4) and mAigov (R5).
- Weak-traction rows kept because they show local-champion attempts: Lawrence (CZ-007), Linca (CZ-009), Definic (SK-005), FiskAI (HR-003), Lawren.ai, AI+ Avocat, QuickLegal (RO-002…004), 1club AI (BG-004). That is 8 of 40; T15 should weight them low.
- Slovenia (4) and Croatia (4) are below 5 products; reasons are in each file and in the Coverage table.

## Poland signal: CEE products already in or heading to Poland
This is the main reason R6 matters (brief: "a warning that someone may enter Poland").

| Product | Country | Status in PL | What it means for a Polish idea |
|---|---|---|---|
| **Everbot** (CZ-001) | CZ | Entered 2026-09: Polish version, sales team, Katowice branch planned | SMB "all AI models in one place" is taken by a CEE player with a PL budget |
| **Nexana.ai** (SK-001) | SK | Entered (active on the Polish market per a 2026-03 sponsored article) | Legal + accounting Q&A for SMEs with citations already sells in PL |
| **Born Digital** (CZ-004) | CZ | Entered (Netia case study) | Enterprise voice agents in Polish exist via CEE vendors |
| **Payhawk** (BG-001) | BG | Entered (Warsaw office) | Mid-market AP/expense agents taken; room below (micro-firms, biura rachunkowe) |
| **Infobip AgentOS** (HR-001) | HR | Entered (Infobip sells in PL) | CX agents compete with the owner of the messaging pipes |
| **Mediately** (SI-004) | SI | Entered (Polish version live) | Drug/guideline Q&A for doctors has a CEE incumbent in PL |
| **Astra AI** (SI-001) | SI | Entered (Polish localisation, PL Education #84) | A matura/E8 tutor must win on CKE content and Polish teacher-creators |
| **Kuba** (CZ-008), **Xeropan** (HU-005) | CZ, HU | Entered (PL Education #90, #79) | AI English tutors already in PL charts |
| **Sloneek** (SK-002) | SK | Announced (Series A partly for a Polish team, 2026-06) | HR agent; the Polish moat stays kadry i płace (ZUS, PPK, L4) |
| **StudyFi** (CZ-010) | CZ | Announced (PL and DE planned, 2025-07) | Study-app category crowded |
| **DirectCase** (CZ-006) | CZ | Polish site locale; Polish data coverage not stated | Cited case-law research may follow; PL already has LEX/Legalis/Lexu |

Summary: **9 of 40 R6 products have entered Poland and 3 more have announced or prepared it.** CZ and SK companies treat Poland as their first export market, which confirms that local adaptation pays and that the window for Polish SMB legal/accounting Q&A, AI receptionists and HR agents is closing.

## Cross-country patterns
1. **Tech-enabled accounting for micro-businesses wired into national e-invoicing** is the most repeated local-champion pattern: Declaro (RO: e-Factura, SPV, SAF-T; 200 clients in 5 months; from 49 EUR/month), Bookkeepie (HU: 300-accountant marketplace + tax bot corrected by accountants), FiskAI (HR: 2026 e-invoicing mandate), Digitoo (CZ: invoice extraction for accounting firms). With R3/R4 AI-native accounting firms and LegalPlace (R5), this is the strongest theme for JDG/sp. z o.o. in Poland (KSeF, JPK, ZUS PUE, CEIDG/S24), with biura rachunkowe as partners or human-in-the-loop.
2. **SMB legal Q&A with citations, in three business models**: subscription Q&A (Nexana.ai SK, in PL), free AI + paid lawyer check (AI+ Avocat RO), law-firm chatbot (Lawren.ai RO). Professional research tools sit beside incumbents (DirectCase and Lawrence vs Codexis/ASPI in CZ; Wolters Kluwer's Jogtár/Libra in HU; ASPI AI/Praetor AI in SK). In all R6 countries, the legal publisher ships AI first, as in Poland.
3. **AI receptionists and voice agents** spread through app stores (Linca, Lorela in CZ Business charts) and enterprise sales (Born Digital, Infobip). Czech callers "are used to calling everywhere" (Born Digital CEO, 2020), as Polish customers are.
4. **National exam tutors scale abroad**: Astra AI (SI) started on Slovenian matura papers, a known maths teacher and a Telemach bundle, and now charts in 9 European stores incl. PL; Kuba (CZ) clones a YouTube English teacher; EduHub (HR) sells matura and medical-entrance prep. Creator + national exam is a repeatable distribution recipe.
5. **Agents inside finance and HR suites** (Payhawk >100M USD ARR, Sloneek, Talentiqa). These are the R6 products with the best durable signals (Payhawk NRR 173.5% estimate, 76% of support automated).
6. **States build sovereign LLMs and use them on-prem**: BgGPT in Bulgaria's revenue agency (2026), SLAIF and a Slovene LLM, Croatia joining a Polish-led AI factory consortium. Polish analogue: PLLuM/Bielik in public administration.
7. **Funded CEE AI companies mostly sell globally** (Duvo, Myriad, Kodesage, Colossyan, Codeplain, Katalist, Druid AI, Bible Chat, Quillon); they are pattern evidence, not adaptation targets.
8. **Exit benchmark**: Robotiq.ai (HR) sold to HCLSoftware at EUR 9M EV on EUR 1.4M revenue (2026-09); Doctrine/Henchman-style publisher exits (R3/R5) have no R6 equivalent yet.

## Products also in R0–R5 (spread signal)
Not re-catalogued: **Libra** (R3-DE-004) sold by Wolters Kluwer to Hungarian law firms; **Synthesia** (R0-GB-035) as the model for Colossyan; **Knowunity** (R3-DE-009) in Education top-grossing in CZ, SK, HR, SI, RO; **Sintra** (R4) in RO Productivity #38; **Brainly** (Polish) RO Education #10. Seen in all R6 charts: ChatGPT, Grok, Perplexity, Plaud, Lovable, Praktika, Loora, Talkpal, Quizlet. Themes repeating from R1–R5: AI-native accounting (Declaro/Bookkeepie vs Accountable, mika, LegalPlace), national legal AI (DirectCase/Lawrence vs Lexroom, Doctrine, Legal Mind), voice agents (Born Digital, Linca vs fonio, Vocca), study apps (StudyFi vs Knowunity, Kiwi AI), state LLMs (BgGPT vs Bürokratt, mAigov, Amália).

## Polish adaptation angles from R6 (for T15–T18)
- **Online accounting firm for JDG on KSeF** with free JDG/S24 registration as funnel, fixed price, accountants in the loop (Declaro, Bookkeepie). Watch Nexana.ai and Everbot.
- **Free AI legal answer + paid radca prawny check** for consumers and JDG (AI+ Avocat); legal-advice rules and the marketplace matter more than the model.
- **Windykacja for SMEs on e-Sąd EPU** using KSeF invoice data (QuickLegal).
- **AI receptionist app for Polish trades and clinics** sold via App Store/Google Play (Linca, Lorela); low moat, fast to test.
- **Matura/E8 tutor with a Polish teacher-creator** (Kuba, Astra AI); Astra already sells in Polish.
- **Blue-collar hiring chat agent** for agencies placing Ukrainian and other migrant workers (Talentiqa); AI Act high-risk.
- **On-prem PLLuM/Bielik deployments for public bodies** (BgGPT at the revenue agency); a public-sector sale, so mostly out of founder scope.

## Coverage

| Country | Status | New rows | R0–R5 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Czechia | done | 11 | 0 | 21 | 11 pages + 4 feeds | 9 | 2 rows found during SK searches; CZ firms already in PL |
| Slovakia | done | 5 | 0 | 14 | 6 pages + 4 feeds | 8 | Nexana source is sponsored; SK-005 funding-only |
| Hungary | done | 5 | 1 (Libra, R3) | 13 | 5 pages + 4 feeds | 8 | legal held by Wolters Kluwer; 2 rows weak on LLM/traction |
| Slovenia | thin | 4 | 0 | 9 | 6 pages + 4 feeds | 6 | ~2.1M people; ~EUR 9.25M startup funding H1 2026 |
| Croatia | thin | 4 | 0 | 12 | 6 pages + 4 feeds | 8 | relevant H1 2026 rounds behind paywall; Netokracija blocks bots |
| Romania | done | 6 | 0 | 14 | 6 pages + 4 feeds | 6 | 3 legal rows without traction |
| Bulgaria | done | 5 | 0 | 11 | 5 pages + 4 feeds | 5 | 1 state programme, 1 aggregator-only row |
| **R6** | done | **40** | 1 | 94 | 45 pages + 28 feeds | 50 | |

- Region total **40** is at the 40–80 floor. Reasons it is not higher: Slovenia and Croatia yield 8 rows together (small ecosystems, paywalled round lists); most funded CEE AI companies are global horizontal products, so local champions are few and early; Hungarian and Bulgarian searches returned macro AI news more than startups; the one-hour budget limited depth (no Google Play charts, no accelerator portfolios).
- Durable signals: mostly 1 (replaced spend), 5 (channel), 7 (pricing), 8 (hard to absorb). Retention/expansion (signals 3/4): Payhawk (NRR 173.5% estimate; ARR >100M USD), Druid AI (ARR x2.7 in 2024), Bible Chat (revenue x3 in 2025), Sloneek (500+ enterprise customers), Digitoo (8 in 10 trials convert, 2022), StudyFi (20% trial conversion, no freemium). Hype warnings: Everbot is a thin multi-model wrapper; Nexana.ai claims come from sponsored content; Astra AI's ARR and user counts are self-reported and inconsistent; Bible Chat is loss-making; Duvo's valuation runs ahead of revenue; FiskAI and several legal bots have no traction.
- Searched and found nothing: LLM startups with traction for payroll (mzdy/bérszámfejtés/salarizare), health administration (scribes, clinic phone agents) in any R6 country, real estate/land registries, public services by private vendors, notaries; any cohort retention figure. Google Play (Similarweb) charts and accelerator batches (StartupYard, ABC accelerator, Vitosha portfolio) were not screened.
- Bot-blocked or failed fetches: profit.ro (403), startup.si (503), app.dealroom.co (403), romania-insider.com (429), ceelegalmatters.com (403), The Recursive round lists (paywall), netokracija.com (not tried, known to drop bots).
- Link check 2026-11-01 (R6 files + CSV): 112 links, 3 dead fixed (CzechTrade Born Digital page, SIH AI:Dental page, a The Recursive channel page: replaced or unlinked and marked excerpt), then 0 dead, 3 unverifiable (ceelegalmatters.com 403, seedtable.com 403, businesswire.com 403). With countries.md included: 326 links, 316 ok, 0 dead, 10 unverifiable (the 3 above + 7 older non-R6 media links in countries.md: brutkasten.com, datanews.be, startupitalia.eu, timesofmalta.com, netokracija.com, qstp.org.qa, cuti.org.uy).
