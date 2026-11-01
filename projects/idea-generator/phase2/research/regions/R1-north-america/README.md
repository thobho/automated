# R1 North America (T05): patterns and coverage

United States and Canada. All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R1-north-america.csv](../../../catalogue/R1-north-america.csv), **65 rows** (US 55, Canada 10), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [united-states.md](united-states.md) | US index, App Store chart snapshot, US-specific champions, US coverage |
| [us-legal-public.md](us-legal-public.md) | legal, immigration, municipal permitting (10 rows) |
| [us-health-admin.md](us-health-admin.md) | scribes, front-desk voice, coding, home care, pharmacy (11) |
| [us-finance-tax-insurance.md](us-finance-tax-insurance.md) | tax-firm automation, AI ERPs, insurance-agency ops (11) |
| [us-smb-realestate.md](us-smb-realestate.md) | home services, dealerships, restaurants, freight, real estate (12) |
| [us-people-education-consumer.md](us-people-education-consumer.md) | recruiting, payroll, teachers, language, consumer apps (11) |
| [canada.md](canada.md) | Canada incl. Québec (10) |

## Choices recorded
- **"US ≥80 products" vs "region 40–80 rows"**: the US research covers **90 products** (55 new + 35 already in [R0-global.csv](../../../catalogue/R0-global.csv), listed per vertical file). The CSV holds only new products, so the region lands at 65 rows, inside 40–80.
- IDs `R1-<CC>-NNN` run across the file (R1-US-001…055, R1-CA-056…065), as in R0.
- `works_in_polish` is `unknown` everywhere: no product was tried in this task (rule applies per idea in T16–T18).
- Facts taken only from a search-engine summary (page not opened or bot-blocked) are marked "excerpt" in the research files and in the `traction` cell; treat them as unverified until T15–T18 re-read them.
- Licensed AI firms (AI-native law firms, AI insurance brokers) are catalogued where they show a pattern, with the L7 issue noted; licensed brokers without a checked home page (Novella, Harper in R0) are not re-added.
- Google Play (Similarweb) charts were not read in this run; App Store top-grossing feeds were (7 genres × 2 countries).

## Cross-country patterns
1. **Vertical B2B LLM products cluster in regulated document work**: law (plaintiff PI, immigration, contracts, litigation research), tax (firm automation, research), health admin (scribes, front desk, coding). Both countries show it; Canada's champions (Blue J, Spellbook, Alexi, Clio) sell mostly into the US.
2. **The best durable evidence in R1 is Canadian**: Blue J (>50% of ARR on multi-year contracts, ARR tripled two years running) and Spellbook (NRR 130%). Most US rows have funding and headcount, not retention: `durable_signals` is `unknown` in 49 of 65 rows.
3. **AI scribes are the clearest two-country theme** with three channels: direct-to-clinician self-serve (Freed: 17,000+ paying; App Store grossing chart), enterprise (Abridge/Ambience, R0), and **state-funded licences** (Canada Health Infoway: up to 10,000 licences, 9 Canadian vendors). EMR vendors acquire scribes (MEDFAR–CareWay).
4. **Front-office voice agents per vertical** (specialty clinics, home services, dealerships, restaurants, freight) attract the largest SMB rounds (Avoca 1B USD valuation). The voice layer is commodity; value sits in integrations (ServiceTitan, EHRs, DMS, TMS) — repeats R0 pattern 2.
5. **Civil-law and registry work is the most Poland-like problem**: Paraito (Québec notaries, land records, French only, per-search pricing) and US municipal permitting against local codes (GovWell, Govstream). Polish analogues: księgi wieczyste, MPZP/Prawo budowlane checks for architects.
6. **Shortage-driven admin automation**: accountant shortage (Filed, Accrual, Juno, Basis), carer shortage (Zingage, Arya, Axle), dispatcher/CSR shortage (Netic, Probook). Poland shares all three drivers (see `research/poland/demography.md`).
7. **Consumer charts reward general assistants and note-takers**; vertical consumer winners show hype markers (Cal AI: paid influencer growth, no renewal data). No Canadian-built LLM app ranks in Canada's charts.

## Products also in R0 (spread signal)
35 products from [R0-global.csv](../../../catalogue/R0-global.csv) belong to the US scan and were not re-catalogued: Harvey, EvenUp, Eudia, PointOne, Comp AI (legal); Abridge, Ambience, Hippocratic AI, Tennr, OpenEvidence, Codes Health, mdhub, Kibu (health); TaxGPT, Rogo, Corgi, Harper, FurtherAI, CollectWise, Bretton AI, Trellis (finance/insurance); EliseAI, Handoff, Domu, Retell AI, Uplane, OffDeal (SMB/real estate); Mercor, micro1, Rezi, Gamma, Perplexity, Character.ai, Suno, Ember (people/consumer). Perplexity (R0-US-008) and Manus (R0-SG-011) also rank in **Canada's** top-grossing Productivity chart, so they appear in both R1 countries.

## Shortlist of Polish adaptation angles from R1 (for T15–T18)
- Tax research over KIS interpretacje + NSA rulings for doradcy podatkowi (Blue J, Accordance, TaxGPT).
- Księgi wieczyste / akta KW analysis for notaries, banks and agents (Paraito).
- Compensation-claims files for kancelarie odszkodowawcze (Eve, Supio, EvenUp).
- Work/residence-permit casework for employers of foreigners (Manifest, Alma, Visalaw.ai).
- Building-permit completeness checks vs MPZP/WZ and Prawo budowlane for architects (GovWell, Govstream).
- Direct-to-doctor Polish AI scribe with EDM export; exit to EDM vendors (Freed, Tali, CareWay).
- Home-care agency scheduling and settlements (Zingage, Arya).
- Installer front office + subsidy paperwork (Netic, Avoca + autarc R0).
- Carrier outreach for spedycja on load exchanges (FleetWorks, HappyRobot; entry risk from Cargofy).
- Teacher tools on podstawa programowa via a browser extension (Brisk, MagicSchool).
- Polish-for-migrants speaking tutor aimed at the B1 certificate (Speak).
- BIK/KRD error disputes (Dovly AI).

## Coverage

| Country | Status | New rows | R0 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| United States | done | 55 | 35 | 90 | ~32 pages + 7 App Store feeds | 26 | ~25 rows partly on excerpts |
| Canada | done | 10 | 2 in charts (Perplexity, Manus) | 12 | 9 pages + 5 App Store feeds | 7 | English + French (Québec) queries |
| **R1** | done | **65** | 35 | 102 | ~41 pages + 12 feeds | 33 | |

- Durable signals: sourced for 16 of 65 rows; hype warnings for 5 (Manifest valuation, Accrual round with no customers, Assort valuation ~250x ARR, Toma possible pivot, Cal AI influencer growth). First channel known for 9 rows.
- Searched and found nothing: retention/NRR for nearly all US products; AI dental, home-health documentation, mortgage processing and IEP startups with verifiable funding; Canadian HR/payroll and real-estate LLM startups; home pages for Cara, Novella, Fulcrum; Google Play charts (not run).
- Bot-blocked or failed fetches: Business Wire (403), GeekWire (403), techleap feed (403), Eudia legal-deals page (404).
- Link check 2026-11-01 (R1 files + CSV): 141 links, 134 ok, 0 dead, 7 unverifiable (403/401 to bots: thelogic.co, theinsurer.com, insurancenewsnet.com, mobihealthnews.com, seedtable.com, finder.techleap.nl, clio.com).

## Gaps
- ~25 rows rest partly on search excerpts; T15 should re-read those sources before ranking themes.
- Google Play charts and Canada's French-language startup media (e.g. Les Affaires) not read.
- Accelerator batches beyond YC (Techstars, CDL, MaRS) not screened one by one.
