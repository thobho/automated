# R2 UK & Ireland (T06): patterns and coverage

United Kingdom and Ireland. All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R2-uk-ireland.csv](../../../catalogue/R2-uk-ireland.csv), **40 rows** (UK 29, Ireland 11), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [united-kingdom.md](united-kingdom.md) | UK index, customer ops/people/education rows (GB-021…029), App Store chart snapshot, UK coverage |
| [uk-legal-property.md](uk-legal-property.md) | AI law firms, contract AI, conveyancing, property packs, lettings, planning (GB-001…010) |
| [uk-tax-health.md](uk-tax-health.md) | Making Tax Digital tools, accounting AI, NHS scribes and AI phone calls, clinical AI (GB-011…020) |
| [ireland.md](ireland.md) | Ireland incl. charts, Irish-language search, accelerators (IE-030…040) |

## Choices recorded
- **IDs** use ISO `GB` for the UK (as in R0 and [criteria.md](../../../method/criteria.md)), not the `UK` in the task text; numbering runs across the file (GB 001–029, IE 030–040).
- **Region total 40** is the bottom of the 40–80 range. The reason it is not higher: 15 UK-based products already sit in R0 (listed below) and were not re-added, and Ireland's Irish-specific LLM startups are mostly pre-seed with no traction figure. The UK research covers 50 products and Ireland 17 (catalogued + R0 + seen).
- `works_in_polish` is `unknown` everywhere: no product was tried in this task (that check belongs to T16–T18).
- Rows with facts only from a search summary say "excerpt" in the `traction` cell and in the research file; 10 of 40 rows rest partly on excerpts (fewer than R1's ~25). Sites that blocked the fetch tool (403) are listed under Coverage.
- Products with no LLM role were catalogued only where the pattern matters for Poland (Moverly: rule-based property packs) and say so in `llm_role`; Pie Tax (Irish, UK charts, no AI) is noted but not catalogued.
- Licensed or staffed delivery models (Flok, Limbic, Cera, Dwelly roll-up, Seapoint account) are catalogued for theme spread with the L7 problem noted in `pl_adaptation_angle`.
- Intercom Fin is listed under Ireland (Dublin-founded, SF HQ). Eolas Medical (Belfast) is UK. Newcode (Norwegian, Dublin office) is left for R4.

## Cross-country patterns
1. **Registry-backed, regulated processes are where UK/IE LLM products cluster**: small-debt claims (Garfield.Law, SRA-authorised), title review and conveyancing (Orbital, Conveyd, Moverly), Making Tax Digital filings (ANNA, Record OS, PeTAR), NHS admin (Accurx Scribe, Dora calls), employment tribunals (Valla), national tax research (Leapifai). Each one maps onto a Polish registry or procedure in [local-moats.md](../../poland/local-moats.md): EPU/KRS/CEIDG, EKW/EGiB/MPZP, KSeF/JPK/PIT, NFZ appointments, sąd pracy/PIP, EUREKA/CBOSA.
2. **Dated mandates open windows.** MTD for Income Tax (April 2026 at £50k, 2027 at £30k, 2028 at £20k) produced a wave of AI tax tools within months, and banks answered with free tools at once. The window is real but the consumer filing layer commoditises fast; firm-side automation (PeTAR, Outmin) looks more defensible.
3. **AI plus a licensed human is the dominant model**: Lawhive, Conveyd, Garfield, Record OS, ANNA, Outmin. AI does the volume, a regulated professional signs off. For Poland this means partnering with a radca/doradca/biuro rachunkowe rather than replacing them.
4. **Distribution through installed bases and the state**: Accurx shipped its scribe to 98% of GP practices it already served; Nurture won a whole education authority (1,100 schools); Oak's free Aila shows the state can also *absorb* a category. Watch Polish public bodies (MEN/ZPE, NFZ, CeZ) for both effects.
5. **National tax-research copilots appear in a third region**: Leapifai (IE) after Blue J (CA), Accordance and TaxGPT (US/R0). Leapifai is raising money specifically to add UK codes: each country's tax law is built separately, which is the moat.
6. **SMB vertical voice agents spread from the US to the UK/IE**: Linda AI (dental, 50+ sites) and Elyos AI (trades, R0) alongside enterprise PolyAI. Polish private dentistry, vets and physio are out-of-pocket markets with the same missed-call problem.
7. **Horizontal contract AI shows the first UK failure** (Robin AI: failed round, layoffs, excerpt) while vertical, registry-tied players keep raising (Orbital 60M USD, 2026).
8. **Consumer charts are the same as in the US**: general assistants, note-takers, calorie scanners, AI stock-signal apps (hype). The only local LLM-era apps in charts are education (Gizmo UK, SimpleStudy IE) and Praktika.

## Products also in R0/R1 (spread signal)
15 UK-based products in [R0-global.csv](../../../catalogue/R0-global.csv) belong to this region and were not re-catalogued: ElevenLabs, VEED, Cleo, Fyxer, Granola, Synthesia, Model ML, Conveo, throxy, Balance, Saturn, Brickwise, Cardamon, Elyos AI, Gradient Labs. Seen in UK and/or Irish top-grossing charts on 2026-11-01: Perplexity, Manus, Lovable (R0) and Plaud, Cal AI (R1). Themes repeating from R1: AI scribes (Accurx/TORTUS vs Freed/Abridge), tax research (Leapifai vs Blue J), front-desk voice (Linda AI vs Assort/Avoca), teacher tools (TeachMateAI/Aila vs MagicSchool/Brisk), language tutors (Praktika vs Speak).

## Shortlist of Polish adaptation angles from R2 (for T15–T18)
- **B2B debt-claims agent** for JDG/SMEs: wezwanie do zapłaty → EPU (e-Sąd) → nakaz zapłaty, with KRS/CEIDG/KRZ checks and 40 EUR rekompensata (Garfield.Law). Pre-court steps need no lawyer.
- **Real-estate due-diligence report** from EKW księgi wieczyste + EGiB + MPZP/Geoportal for notariusze, kancelarie, banks and biura nieruchomości (Orbital, Moverly, Conveyd).
- **Cited tax copilot** over interpretacje KIS (EUREKA), CBOSA rulings and ISAP for doradcy podatkowi and biura rachunkowe (Leapifai, Blue J).
- **Firm-side PIT/JDG automation** for biura rachunkowe (PeTAR, Outmin) rather than a consumer filing app.
- **Voice receptionist for private dental/vet/physio clinics** in Polish, with clinic-software integration and no-show reduction (Linda AI); a waiting-list confirmation agent for NFZ outpatient clinics (Dora) as a second step.
- **Bidder-side tender writer** for firms answering przetargi (e-Zamówienia, SWZ, JEDZ) (AutogenAI).
- **Employee-side labour-dispute assistant** (pozew do sądu pracy, skarga do PIP), incl. Ukrainian workers (Valla).
- **Exam revision on CKE materials** (SimpleStudy, Gizmo) and a voice maths tutor for egzamin ósmoklasisty (Third Space Learning).

## Coverage

| Country | Status | New rows | R0 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| United Kingdom | done | 29 | 15 UK-based + 5 in charts | 50 | ~30 pages + 7 App Store feeds | 24 | 8 rows partly on excerpts |
| Ireland | done | 11 | 0 Irish-based; 4 in charts | 17 | 14 pages + 7 App Store feeds | 11 (1 in Irish) | 2 rows partly on excerpts |
| **R2** | done | **40** | 15 | 67 | ~44 pages + 14 feeds | 35 | |

- Durable signals: sourced for 22 of 40 rows (mostly signal 1 replaced spend, 5 channel, 7 pricing, 10 timing). Retention or expansion evidence (signals 3/4) only for Moverly (Connells 12-month cohort), Dwelly (acquisitions) and Tines (task volume tripled). Hype warnings: Robin AI (layoffs after failed round), SimpleStudy (paywall complaints); chart-level hype in AI stock-signal apps. First channel known for 15 rows.
- Searched and found nothing: retention/NRR for UK legal, tax and health rows; UK SMB HR/payroll LLM startups; UK-HQ vertical voice receptionists; Irish LLM products for conveyancing, HSE admin or ROS filing; commercial Irish-language LLM products. Google Play (Similarweb) charts not read. Entrepreneurs First, Seedcamp and NDRC portfolios not screened one by one.
- Bot-blocked or failed fetches: sifted.eu (403), digitalhealth.net (403), local.gov.uk (403), thirdspacelearning.com (403), irishtechnews.ie (403), orbital.tech blog URL (404; the tech blog was used instead), tortus.ai news (404).
- Link check 2026-11-01 (R2 files + CSV): 106 links, 102 ok, 0 dead, 4 unverifiable (irishtechnews.ie 403, inspeq.ai 403, two arabfounders.net pages closing bot connections; both were read with the fetch tool earlier).

## Gaps
- 10 rows rest partly on search excerpts (Genie AI, Robin AI, Briefcase, TORTUS funding, Limbic, Cera, Third Space Learning, Aila, Jack & Jill Series A, SimpleStudy reviews); T15 should re-read them.
- Home pages not confirmed for Nurture (url `unknown`), Record OS, Audrey AI, Valon and Xylo (the last four not catalogued).
- No product tried in Polish; no revenue figure for any UK/IE row except Praktika (company claim, 2024) and Robin AI (excerpt).
