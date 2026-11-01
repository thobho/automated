# R3 DACH & Benelux (T07): patterns and coverage

Germany, Netherlands, Switzerland, Austria, Belgium, Luxembourg (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R3-dach-benelux.csv](../../../catalogue/R3-dach-benelux.csv), **41 rows** (DE 17, NL 5, CH 6, AT 5, BE 6, LU 2), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [germany.md](germany.md) | law, tax/DATEV, health admin, property, trades, benefits, education, horizontal; charts (DE-001…017) |
| [netherlands.md](netherlands.md) | GP scribe, audit, tenders, legal, accounting (NL-001…005) |
| [switzerland.md](switzerland.md) | legal search, fiduciary AI via association, hospital documentation and coding, study app, invoicing (CH-001…006) |
| [austria.md](austria.md) | voice agents, payroll, symptom check, plot potential (AT-001…005) |
| [belgium.md](belgium.md) | freelancer AI tax, legal, firm agents, scribe, pensions (BE-001…006) |
| [luxembourg.md](luxembourg.md) | fund regtech, sales training; why Luxembourg is thin (LU-001…002) |

## Choices recorded
- IDs `R3-<ISO>-NNN`, numbered per country (DE-001…017; Skalar was found during the Austria searches and added as DE-017).
- Products already in R0/R1/R2 are not re-added (listed below).
- `works_in_polish` is `unknown` unless a source shows the product in Poland. Only Libra (DE-004) has such evidence: Wolters Kluwer launched it on LEX content in Poland in 2026-02.
- Non-LLM or AI-planned products are catalogued only where the pattern matters for Poland, and `llm_role`/`hype_warnings` say so: Elterngeld Buddy (no LLM), plancraft and Lohnbot (AI planned, not shipped).
- Licensed or capital-heavy models (Limetax and Buena roll-ups, XUND medical device, Warren pension fund) are catalogued for theme spread with the L7 problem stated in `pl_adaptation_angle`.
- Region total **41** is just above the 40–80 floor. Reasons it is not higher: 11 DACH/Benelux companies already sit in R0 (below); the Dutch, Swiss and Austrian applied-AI pipelines are thin (most large 2025–2026 rounds were deep tech); Luxembourg has 2 rows (reason in [luxembourg.md](luxembourg.md)).
- Rows partly on excerpts: TreuhandGPT (CH-002), Warren (BE-006), Legal Mind's 2026 top-up, XUND insurer counts, Libra's Polish launch (PAP release seen only as a search summary). 5 of 41.

## Cross-country patterns
1. **AI-native accounting and tax firms are the region's biggest applied theme.** Germany alone produced mika (750+ GmbHs, 1M EUR run-rate, +20%/month), Skalar (12M EUR, 100+ clients per adviser) and Limetax (36M EUR roll-up on DATEV) in 2026, plus Belgium's Ravical (agents for firms) and Accountable (freelancer AI accountant, #1 BE / #3 DE Finance chart), the Netherlands' Autoboeker and Switzerland's TreuhandGPT. The licensed adviser always stays in the loop (StBerG, Belgian accountant rules). For Poland this maps onto biura rachunkowe and doradcy podatkowi with KSeF/JPK/ZUS ([local-moats.md](../../poland/local-moats.md) sections A–B).
2. **National-language clinical scribes win national share fast, then get bought.** Juvoly reached 35% of Dutch GP practices and was acquired by Tandem Health (Sweden); Belgium's Cavell, Switzerland's 44ai and Saipient (with Tarmed coding) follow; Aaron.ai (phone) went to Doctolib. In R2 the UK showed the same with Accurx/TORTUS. Polish analogue: POZ and private clinics with gabinet.gov.pl/P1, e-recepta, e-skierowanie, NFZ coding, with clear entry risk from Tandem and Docplanner.
3. **Legal AI consolidates into publishers, and that has already reached Poland.** Libra (Berlin) → Wolters Kluwer, launched in Poland on LEX in 2026-02; Henchman (Ghent) → LexisNexis; Noxtua is led by C.H. Beck money. General legal research and drafting in Polish should be treated as **taken**; niches (notaries: LawX; firm secretariat: JUPUS) remain.
4. **SMB voice agents are crowded in DACH**: fonio (7,500+ customers, 20VC seed), goai, Mediform, Aaron.ai, plus R0's telli, Synthflow, Parloa. The Polish opportunity, if any, is vertical (clinics, workshops) with Polish booking integrations.
5. **Distribution through the incumbent channel** is the repeated go-to-market: an association (TREUHAND|SUISSE → 2,000 fiduciary offices), a hospital-IT vendor (Cistec → 44ai), state education ministries (fobizz), health insurers (XUND), Excel (DataSnipper). For a solo Polish founder the association route (biura rachunkowe, doradcy) is the realistic one.
6. **Registry-plus-AI property tools appear again** (Austria's Propcorn plot potential, Germany's Buena for property managers), extending R2's Orbital/Moverly theme. Polish data: MPZP/WZ, EGiB, Geoportal, KW.
7. **People pay to get state forms right** (Elterngeld Buddy and formie in Germany, without LLMs; Accountable's tax checks). LLM layers that read payslips, decisions and letters (mika explains tax-office letters) are the next step.
8. **Consumer charts are global** in all six countries (ChatGPT, Claude, Plaud, Perplexity, calorie and language apps). Local LLM-era chart apps are education (Knowunity, Jurafuchs, Studyflash) and freelancer finance (Accountable, Magic Heidi). Luxembourg's charts show Luxembourgish-learning apps driven by naturalisation rules, a parallel to Polish-language demand from migrants.

## Products also in R0 (spread signal)
11 R3-based companies in [R0-global.csv](../../../catalogue/R0-global.csv) were not re-catalogued: autarc, Beglaubigt.de, telli, Mercura, Tabula, Zeit AI, ComplyDo, Parloa, Synthflow, n8n (Germany) and Spott (Belgium). Seen in R3 top-grossing charts on 2026-11-01: Perplexity, Manus, Lovable (R0), Plaud, Cal AI (R1) and Praktika (R2). Themes repeating from R1/R2: AI scribes (Juvoly/Cavell vs Accurx/Abridge), tender writers (Brainial vs AutogenAI), national tax/legal copilots (Legal Mind vs Leapifai/Blue J), voice receptionists (fonio/Mediform vs Linda AI/Assort), teacher AI (fobizz vs TeachMateAI/MagicSchool), AI-native accounting (mika/Skalar vs Basis/Rillet/Outmin).

## Shortlist of Polish adaptation angles from R3 (for T15–T18)
- **AI-native księgowość for sp. z o.o.** with a partner doradca podatkowy: KSeF, JPK_V7, CIT-8, e-sprawozdanie, "explain this letter from US/ZUS" (mika, Skalar, Accountable).
- **AI tax assistant for JDG** on Polish rules (ryczałt/liniowy/skala, ZUS reliefs), sold as an app with a tax guarantee (Accountable).
- **Agent layer for biura rachunkowe** on Comarch/Symfonia/enova (Limetax's software without the roll-up; Ravical; Autoboeker), distributed via accounting associations (TreuhandGPT model).
- **Notary-office AI** (akty, wypisy, KW/CRWZ reporting): LawX shows notaries buy separately from law firms.
- **Medical coding assistant** for private clinics with NFZ contracts (JGP, ICD-9 PL) (Saipient); a scribe only with a clear angle against Tandem/Docplanner entry.
- **Plot-potential report** from MPZP/WZ + EGiB + Geoportal for developers and agents (Propcorn).
- **Benefit-application assistant** (ZUS świadczenia, zasiłek macierzyński, 800+) with document reading (Elterngeld Buddy pattern plus an LLM).
- **Law-student and aplikant tutor** on Polish kazusy, sold via campus licences (Jurafuchs).

## Coverage

| Country | Status | New rows | R0–R2 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Germany | done | 17 | 10 (R0) | 38 | 21 pages + 6 feeds | 22 | 1 row partly on excerpt (Libra PL launch) |
| Netherlands | done | 5 | 0 | 11 | 7 pages + 6 feeds | 9 | thin applied-AI pipeline |
| Switzerland | done | 6 | 0 | 12 | 6 pages + 6 feeds | 6 | 1 row on excerpt (TreuhandGPT) |
| Austria | done | 5 | 0 | 9 | 5 pages + 6 feeds | 4 | |
| Belgium | done | 6 | 1 (Spott, R0) | 11 | 7 pages + 6 feeds | 6 | 1 row partly on excerpt (Warren) |
| Luxembourg | thin | 2 | 0 | 8 | 2 pages + 6 feeds | 4 | small market; startups serve the fund industry |
| **R3** | done | **41** | 11 | 89 | ~48 pages + 36 feeds | 51 | |

- Durable signals: sourced for 35 of 41 rows, mostly 1 (replaced spend), 5 (channel), 7 (pricing) and 8 (hard to absorb). Retention/expansion (signals 3/4): JUPUS (users and cases doubled, ARR ×4), mika (customers 400 → 750), Lohnbot (customers ×3), Jurafuchs (profitable 2+ years), fobizz (licence extended for demand), DeepJudge (+500% revenue), DataSnipper (revenue doubled several years running), Knowunity (usage 5+ times a week). Hype warnings: AI features planned but not shipped (plancraft, Lohnbot), one-off purchase (Elterngeld Buddy), sponsored source (Autoboeker). No layoffs or pivots found. First channel known for 16 rows.
- Searched and found nothing: LLM startups for German Kommunen, Dutch gemeenten/woningcorporaties or Luxembourg's public services; German or Austrian LLM payroll startups with shipped AI; German ambient-scribe startups; NRR or cohort retention for any R3 row. Google Play (Similarweb) charts were not read; accelerator batches (Start it @KBC, Techleap, Venture Kick) were seen only through news items, not screened one by one.
- Bot-blocked or failed fetches: deutsche-startups.de (403), wolterskluwer.com news (403), dutchitchannel.nl (403), organisator.ch (403), markt-kom.com (403), venturekick.ch (503), belganewsagency.eu Ravical article (404).
- Link check 2026-11-01 (R3 files + CSV): 104 links, 101 ok, 0 dead, 3 unverifiable (manda.be ×2 returning 520 to the checker, both read with the fetch tool; organisator.ch 403, TreuhandGPT excerpt). One dead Belga link was removed.
