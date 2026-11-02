# Phase 2 themes (T15)

69 themes clustered from all 531 rows of `catalogue/*.csv` (R0-global and R1–R10). Every catalogue row carries its theme id in the `theme` column. Theme ids (TH01–TH69) are stable: later tasks refer to them; the rank may change, the id does not.

Built reproducibly: [taxonomy.py](taxonomy.py) (theme definitions, Polish angle, membership) → [build_themes.py](build_themes.py) `--write` (fills the catalogue column, writes [mapping.csv](mapping.csv) and [stats.csv](stats.csv)) → [render_themes.py](render_themes.py) (ranking and this file). To move a product, edit `MEMBERS` in taxonomy.py and rerun both scripts.

## Ranking rule

Score (0–100) = **40% spread + 35% durable traction + 25% novelty**. Raw growth, funding size and headline ARR are deliberately not inputs.

- **Spread** = 0.6 × min(countries, 10)/10 + 0.4 × min(regions, 6)/6, counting the distinct `country` and `region` values of the theme's rows (R0 rows count under their own country and region R0).
- **Durable traction** = min(D, 5)/5 − 0.1 × min(H, 3), floored at 0. D = members labelled *promising* or *durable*, H = members with at least one hype warning. Each member is labelled with the rubric in [criteria.md §6](../method/criteria.md): durable points = recorded signal numbers (1–10) in `durable_signals`, with 3 and 4 counted double, minus 2 × hype warnings. Hype warnings are only the brief's list (tourist spikes, one-off/lifetime revenue, paid-ads/influencer growth, novelty use case, thin wrapper, price cuts, layoffs/pivot); other text in `hype_warnings` (self-reported figures, weak traction, no LLM) is counted as a **caveat**, not hype.
- **Novelty** = (n − 1)/2 with n = 1–3 set per theme in taxonomy.py: 3 = LLM-native and replaces a job step or service end to end; 2 = the LLM does one real step in a familiar workflow; 1 = commodity, infrastructure, classic software or a novelty use case.
- **Durability verdict** per theme: *durable* if D ≥ 2 and H ≤ D/2; *hype* if H ≥ 2 and H > D; otherwise *mixed*. "thin" marks themes where half or more of the rows have no recorded signal or warning at all.
- Ties: more countries first, then theme id. Batches: ranks 1–23 = **A**, 24–46 = **B**, 47–69 = **C** (T16, T17, T18).

**Caveats.** (1) No member reaches the rubric's *durable* label (≥ 7 points incl. retention or expansion): the catalogue has very little retention/NRR data, so *durable* here means "several members with ≥ 4 recorded signal points and few hype warnings", a relative verdict. (2) Signals are counted as recorded in the catalogue; not every one carries its own URL, so T16–T18 must re-check the evidence before scoring L2. (3) Launch years are the last year written in `launched` (usually the LLM-era launch or breakout), not founding dates. (4) Spread counts where the scans found products, so regions scanned more deeply (R0/R1 US) inflate US-heavy themes less than it seems: spread caps at 10 countries and 6 regions.

## Ranked list

| Rank | Batch | Id | Theme | Rows | Countries | Regions | D | H | Verdict | Novelty | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | [TH16](#th16) | AI accountant for micro-businesses and sole traders | 21 | 16 | 8 | 4 | 0 | durable | 3 | 93.0 |
| 2 | A | [TH07](#th07) | Legal research on national law | 26 | 19 | 9 | 7 | 1 | durable | 2 | 84.0 |
| 3 | A | [TH09](#th09) | Contract drafting and review | 13 | 9 | 6 | 5 | 1 | durable | 2 | 81.6 |
| 4 | A | [TH01](#th01) | Ambient clinical scribe | 24 | 15 | 8 | 2 | 0 | durable | 3 | 79.0 |
| 5 | A | [TH19](#th19) | AI-native ledger and finance-team agents | 10 | 8 | 7 | 3 | 0 | durable (thin) | 2 | 68.7 |
| 6 | A | [TH34](#th34) | HR and payroll agents | 8 | 8 | 8 | 3 | 0 | durable | 2 | 68.7 |
| 7 | A | [TH02](#th02) | Patient call and scheduling agents | 12 | 8 | 6 | 1 | 0 | mixed | 3 | 67.2 |
| 8 | A | [TH56](#th56) | Leasing and property-management agents | 10 | 7 | 6 | 1 | 0 | mixed | 3 | 64.8 |
| 9 | A | [TH33](#th33) | AI recruiting interviews and screening | 13 | 9 | 7 | 0 | 0 | mixed | 3 | 62.6 |
| 10 | A | [TH61](#th61) | Procurement, RFQ and order handling | 7 | 7 | 5 | 1 | 0 | mixed | 3 | 62.1 |
| 11 | A | [TH23](#th23) | Enterprise customer-service agents | 15 | 12 | 8 | 1 | 0 | mixed | 2 | 59.5 |
| 12 | A | [TH54](#th54) | Compliance and regtech agents | 9 | 7 | 6 | 0 | 1 | mixed (thin) | 3 | 57.8 |
| 13 | A | [TH17](#th17) | Agents for accounting and tax firms | 12 | 8 | 5 | 0 | 1 | mixed | 3 | 57.5 |
| 14 | A | [TH26](#th26) | AI receptionist for SMEs | 6 | 5 | 5 | 1 | 0 | mixed | 3 | 57.3 |
| 15 | A | [TH24](#th24) | Local-language voice and CS agents | 10 | 7 | 4 | 2 | 0 | durable | 2 | 54.0 |
| 16 | A | [TH37](#th37) | Study material generators | 12 | 10 | 7 | 0 | 4 | hype | 2 | 52.5 |
| 17 | A | [TH21](#th21) | Consumer tax filing | 8 | 7 | 6 | 1 | 0 | mixed | 2 | 52.3 |
| 18 | A | [TH04](#th04) | Care-provider documentation and operations | 7 | 4 | 4 | 1 | 0 | mixed | 3 | 52.3 |
| 19 | A | [TH29](#th29) | Conversational commerce on messaging apps | 10 | 6 | 3 | 2 | 0 | durable | 2 | 48.9 |
| 20 | A | [TH06](#th06) | Consumer health coaching and triage | 9 | 8 | 6 | 0 | 2 | hype | 2 | 47.7 |
| 21 | A | [TH10](#th10) | Law-practice operations and AI secretariat | 6 | 5 | 4 | 0 | 0 | mixed (thin) | 3 | 47.7 |
| 22 | A | [TH13](#th13) | Consumer legal help and AI-enabled law firms | 8 | 5 | 4 | 0 | 0 | mixed | 3 | 47.7 |
| 23 | A | [TH40](#th40) | AI speaking and language tutors | 11 | 9 | 5 | 1 | 2 | hype | 2 | 47.4 |
| 24 | B | [TH15](#th15) | Property transaction and title diligence | 5 | 3 | 3 | 1 | 0 | mixed | 3 | 47.2 |
| 25 | B | [TH59](#th59) | Citizen and SME public-service navigators | 7 | 7 | 6 | 0 | 1 | mixed | 2 | 45.3 |
| 26 | B | [TH14](#th14) | Debt recovery agents | 5 | 4 | 4 | 0 | 0 | mixed | 3 | 45.3 |
| 27 | B | [TH27](#th27) | Trades and home-services front office | 9 | 4 | 4 | 0 | 0 | mixed (thin) | 3 | 45.3 |
| 28 | B | [TH32](#th32) | Tender and bid writing | 4 | 4 | 4 | 0 | 0 | mixed | 3 | 45.3 |
| 29 | B | [TH05](#th05) | Clinical evidence and decision support | 6 | 6 | 5 | 1 | 1 | mixed | 2 | 43.7 |
| 30 | B | [TH46](#th46) | Agent builder platforms and AI services | 17 | 14 | 8 | 1 | 1 | mixed | 1 | 43.5 |
| 31 | B | [TH20](#th20) | Tax research copilots for professionals | 5 | 5 | 4 | 1 | 0 | mixed | 2 | 42.2 |
| 32 | B | [TH35](#th35) | Teacher copilot | 8 | 5 | 4 | 1 | 0 | mixed | 2 | 42.2 |
| 33 | B | [TH38](#th38) | AI tutors for national curricula | 7 | 6 | 4 | 1 | 1 | mixed | 2 | 41.1 |
| 34 | B | [TH60](#th60) | Freight and logistics agents | 4 | 3 | 3 | 0 | 0 | mixed (thin) | 3 | 40.2 |
| 35 | B | [TH22](#th22) | Personal finance assistant | 10 | 10 | 7 | 0 | 1 | mixed (thin) | 1 | 40.0 |
| 36 | B | [TH18](#th18) | Invoice and receipt capture with auto-booking | 4 | 4 | 4 | 1 | 0 | mixed (thin) | 2 | 39.8 |
| 37 | B | [TH52](#th52) | Marketing, SEO and ad agents | 8 | 5 | 4 | 1 | 1 | mixed | 2 | 38.7 |
| 38 | B | [TH03](#th03) | Healthcare back-office automation | 11 | 3 | 2 | 0 | 0 | mixed (thin) | 3 | 37.5 |
| 39 | B | [TH55](#th55) | Insurance operations agents | 9 | 3 | 2 | 0 | 0 | mixed (thin) | 3 | 37.5 |
| 40 | B | [TH68](#th68) | Fraud, identity and trust | 4 | 4 | 3 | 1 | 0 | mixed | 2 | 37.1 |
| 41 | B | [TH30](#th30) | AI SDR and outbound prospecting | 6 | 5 | 4 | 0 | 1 | mixed (thin) | 2 | 35.2 |
| 42 | B | [TH39](#th39) | National and migration exam prep | 6 | 5 | 4 | 0 | 3 | hype | 2 | 35.2 |
| 43 | B | [TH57](#th57) | Real-estate agency and investor tools | 7 | 5 | 4 | 0 | 1 | mixed | 2 | 35.2 |
| 44 | B | [TH67](#th67) | Agents inside SMB retail and hospitality systems | 5 | 5 | 4 | 0 | 0 | mixed | 2 | 35.2 |
| 45 | B | [TH11](#th11) | Plaintiff litigation casework | 4 | 2 | 2 | 0 | 0 | mixed (thin) | 3 | 35.1 |
| 46 | B | [TH64](#th64) | AI-moderated market research | 2 | 2 | 2 | 0 | 0 | mixed (thin) | 3 | 35.1 |
| 47 | C | [TH08](#th08) | Law-firm AI workspace and knowledge | 8 | 6 | 3 | 0 | 0 | mixed | 2 | 34.9 |
| 48 | C | [TH62](#th62) | AI-native engineering design | 3 | 3 | 1 | 0 | 0 | mixed | 3 | 34.9 |
| 49 | C | [TH28](#th28) | Car-dealer agents | 3 | 3 | 3 | 1 | 1 | mixed | 2 | 31.2 |
| 50 | C | [TH31](#th31) | Sales conversation intelligence and coaching | 4 | 4 | 3 | 0 | 0 | mixed (thin) | 2 | 30.1 |
| 51 | C | [TH45](#th45) | Natural-language analytics over company data | 4 | 4 | 3 | 0 | 0 | mixed (thin) | 2 | 30.1 |
| 52 | C | [TH58](#th58) | Government back-office AI | 6 | 4 | 3 | 0 | 0 | mixed (thin) | 2 | 30.1 |
| 53 | C | [TH12](#th12) | Immigration casework | 4 | 1 | 1 | 0 | 0 | mixed (thin) | 3 | 30.1 |
| 54 | C | [TH41](#th41) | Meeting notes and transcription | 7 | 5 | 4 | 1 | 0 | mixed | 1 | 29.7 |
| 55 | C | [TH42](#th42) | Consumer general assistants | 8 | 6 | 5 | 0 | 3 | hype | 1 | 27.7 |
| 56 | C | [TH53](#th53) | Security operations agents | 4 | 3 | 3 | 0 | 0 | mixed (thin) | 2 | 27.7 |
| 57 | C | [TH63](#th63) | Finance and M&A research agents | 4 | 3 | 3 | 0 | 0 | mixed (thin) | 2 | 27.7 |
| 58 | C | [TH36](#th36) | Teacher and school paperwork | 4 | 2 | 1 | 1 | 0 | mixed | 2 | 27.0 |
| 59 | C | [TH50](#th50) | Creative media generation | 9 | 5 | 5 | 0 | 4 | hype | 1 | 25.3 |
| 60 | C | [TH43](#th43) | Sovereign and national-language LLMs | 6 | 6 | 4 | 0 | 0 | mixed | 1 | 25.1 |
| 61 | C | [TH47](#th47) | Coding agents | 7 | 5 | 4 | 0 | 0 | mixed | 1 | 22.7 |
| 62 | C | [TH25](#th25) | Voice agent platforms and APIs | 5 | 3 | 3 | 1 | 0 | mixed (thin) | 1 | 22.2 |
| 63 | C | [TH48](#th48) | AI infrastructure and APIs | 7 | 4 | 4 | 0 | 1 | mixed (thin) | 1 | 20.3 |
| 64 | C | [TH51](#th51) | Avatar and business video generation | 5 | 4 | 4 | 0 | 5 | hype | 1 | 20.3 |
| 65 | C | [TH44](#th44) | Enterprise LLM workspace and gateway | 3 | 3 | 3 | 0 | 0 | mixed | 1 | 15.2 |
| 66 | C | [TH49](#th49) | Prompt-to-app builders | 3 | 3 | 3 | 0 | 0 | mixed (thin) | 1 | 15.2 |
| 67 | C | [TH65](#th65) | AI companions | 3 | 2 | 2 | 0 | 3 | hype | 1 | 10.1 |
| 68 | C | [TH66](#th66) | Resume and career tools | 2 | 2 | 2 | 0 | 1 | mixed | 1 | 10.1 |
| 69 | C | [TH69](#th69) | Translation and localisation | 2 | 2 | 2 | 0 | 0 | mixed | 1 | 10.1 |

## Batch A (23 themes, Poland check T16)

### TH16

**1. AI accountant for micro-businesses and sole traders** · score 93.0 · batch A

- **What:** Tech-enabled accounting and tax filing for freelancers and small companies, licensed human in the loop. **LLM role:** agents + document understanding.
- **B2B/B2C:** B2B 14, B2C 6, B2B2C 1.
- **Examples:** [Osome](../catalogue/R7-east-asia.csv) `R7-SG-001`; [Cenit](../catalogue/R10-latin-america.csv) `R10-CL-002`; [Hnry](../catalogue/R8-oceania-israel.csv) `R8-NZ-003`; [LegalPlace](../catalogue/R5-france-southern-europe.csv) `R5-FR-001`; [Accountable](../catalogue/R3-dach-benelux.csv) `R3-BE-001`; [Bookkeepie](../catalogue/R6-cee-peers.csv) `R6-HU-001`.
- **Spread:** 16 countries in 8 regions (R2 R3 R4 R5 R6 R7 R8 R10): Belgium, Chile, Croatia, Finland, France, Germany, Hungary, Ireland, Japan, Lithuania, New Zealand, Romania, Singapore, Switzerland, Taiwan, United Kingdom. Launch/breakout: earliest 2015 (LegalPlace, France), latest 2026 (AI 運將助手 (taxi driver assistant), Taiwan); 21/21 rows dated.
- **Best traction:** Osome (Singapore): FY2025 revenue S$26.6M, CY2025 S$29M; EBITDA -S$11.8M (improved 50%); 2026-05-05 ([source](https://osome.com/sg/blog/osome-fy2025-results-ebitda-loss-cut-ai/)); durable signals recorded: 1, 2, 3, 8.
- **Durability: durable.** Members: 4 promising, 16 unproven, 0 hype, 1 no evidence; hype warnings: none; 12 rows with caveats.
- **Polish angle (first thought):** JDG and sp. z o.o.: KSeF, JPK_V7, ZUS, PIT/CIT, CEIDG/S24; partner with or become a biuro rachunkowe.
- **All members:** Cenit `R10-CL-002`, ANNA Money `R2-GB-011`, Briefcase `R2-GB-013`, Seapoint `R2-IE-034`, Accountable `R3-BE-001`, Magic Heidi `R3-CH-004`, Limetax `R3-DE-005`, mika `R3-DE-006`, Skalar `R3-DE-017`, Truster `R4-FI-005`, RoboLabs `R4-LT-004`, LegalPlace `R5-FR-001`, FiskAI `R6-HR-003`, Bookkeepie `R6-HU-001`, Declaro `R6-RO-001`, AIBOS `R7-JP-008`, Osome `R7-SG-001`, Sleek `R7-SG-002`, AI 運將助手 (taxi driver assistant) `R7-TW-007`, Hnry `R8-NZ-003`, Solo `R8-NZ-007`.

### TH07

**2. Legal research on national law** · score 84.0 · batch A

- **What:** Cited answers and drafting over a country's statutes and case law. **LLM role:** retrieval + generation.
- **B2B/B2C:** B2B 26.
- **Examples:** [Lexroom](../catalogue/R5-france-southern-europe.csv) `R5-IT-001`; [Jupytr](../catalogue/R9-gulf-turkey.csv) `R9-TR-001`; [Magnar](../catalogue/R10-latin-america.csv) `R10-CL-001`; [Pandektes](../catalogue/R4-nordics-baltics.csv) `R4-DK-001`; [Doctrine](../catalogue/R5-france-southern-europe.csv) `R5-FR-002`; [LBox / LBox AI](../catalogue/R7-east-asia.csv) `R7-KR-002`.
- **Spread:** 19 countries in 9 regions (R1 R3 R4 R5 R6 R7 R8 R9 R10): Australia, Canada, Chile, Czechia, Denmark, France, Germany, Greece, Italy, Japan, Kuwait, Latvia, Mexico, Netherlands, Singapore, South Korea, Taiwan, Turkey, United Arab Emirates. Launch/breakout: earliest 2017 (Alexi, Canada), latest 2026 (Jupytr, Turkey); 25/26 rows dated.
- **Best traction:** Lexroom (Italy): Series B 50M USD (Left Lane Capital), 2026-05; 73M USD total; 8,000+ law firms and legal teams (also given as 10,000+); 65% of users daily, 94% weekly; launched in Spain and Germany ([source](https://economyup.it/startup/lexroom-50-milioni-di-dollari-per-portare-in-europa-la-startup-dellai-per-il-legal)); durable signals recorded: 3, 4, 8.
- **Durability: durable.** Members: 7 promising, 18 unproven, 0 hype, 1 no evidence; hype warnings: thin wrapper; 15 rows with caveats.
- **Polish angle (first thought):** ISAP, SAOS, CBOSA open data; general research is taken by LEX/Libra and Legalis; niches (KIO, UODO, UOKiK decisions, notaries, komornicy) may be open.
- **All members:** Alexi `R1-CA-058`, Magnar `R10-CL-001`, LEXIMEX `R10-MX-003`, AIJusticia `R10-MX-004`, Noxtua `R3-DE-003`, Legal Mind `R3-NL-004`, Pandektes `R4-DK-001`, Lexu AI `R4-LV-001`, Doctrine `R5-FR-002`, Haiku `R5-FR-005`, dikaio.ai (Decode+) `R5-GR-001`, Lexroom `R5-IT-001`, DirectCase `R6-CZ-006`, Lawrence `R6-CZ-007`, Legalscape `R7-JP-004`, LBox / LBox AI `R7-KR-002`, SuperLawyer (Law&Company) `R7-KR-003`, LawNet AI / GPT-Legal (Singapore Academy of Law + IMDA) `R7-SG-007`, Lawsnote (七法) `R7-TW-002`, Isaacus `R8-AU-007`, MiAI Law `R8-AU-008`, Qanooni `R9-AE-004`, Wkeel AI `R9-KW-001`, Jupytr `R9-TR-001`, Apilex.ai `R9-TR-002`, Leagle `R9-TR-011`.

### TH09

**3. Contract drafting and review** · score 81.6 · batch A

- **What:** Reviews and drafts contracts against playbooks for in-house teams and SMEs. **LLM role:** document understanding + generation.
- **B2B/B2C:** B2B 13.
- **Examples:** [LegalOn](../catalogue/R7-east-asia.csv) `R7-JP-003`; [Checkbox](../catalogue/R8-oceania-israel.csv) `R8-AU-005`; [Chamelio](../catalogue/R8-oceania-israel.csv) `R8-IL-004`; [Ivo](../catalogue/R8-oceania-israel.csv) `R8-NZ-001`; [Spellbook](../catalogue/R1-north-america.csv) `R1-CA-057`; [Ordalie](../catalogue/R5-france-southern-europe.csv) `R5-FR-006`.
- **Spread:** 9 countries in 6 regions (R1 R2 R5 R7 R8 R9): Australia, Canada, France, Israel, Japan, New Zealand, Saudi Arabia, United Kingdom, United States. Launch/breakout: earliest 2016 (Luminance, United Kingdom), latest 2025 (Checkbox, Australia); 12/13 rows dated.
- **Best traction:** LegalOn (Japan): ARR > 10bn JPY (~67M USD), 7,000+ legal teams, >30% of Japanese listed companies, 2025-10-14 ([source](https://en.legalontech.jp/3274/)); durable signals recorded: 1, 3, 4, 8.
- **Durability: durable.** Members: 5 promising, 2 unproven, 1 hype, 5 no evidence; hype warnings: layoffs/pivot; 4 rows with caveats.
- **Polish angle (first thought):** Polish civil-law contract templates and KC clauses; crowded globally and multilingual by default, so the gap is probably marketing only.
- **All members:** Eudia `R0-US-045`, Spellbook `R1-CA-057`, Luminance `R2-GB-002`, Wordsmith AI `R2-GB-004`, Genie AI `R2-GB-005`, Robin AI `R2-GB-006`, Ordalie `R5-FR-006`, LegalOn `R7-JP-003`, Checkbox `R8-AU-005`, Lawpath AI `R8-AU-006`, Chamelio `R8-IL-004`, Ivo `R8-NZ-001`, Contracts (Aqood) `R9-SA-005`.

### TH01

**4. Ambient clinical scribe** · score 79.0 · batch A

- **What:** Listens to a consultation and drafts the clinical note, letters and codes into the EHR. **LLM role:** voice + generation.
- **B2B/B2C:** B2B 24.
- **Examples:** [Telepatia](../catalogue/R10-latin-america.csv) `R10-CO-001`; [Heidi (Heidi Health)](../catalogue/R8-oceania-israel.csv) `R8-AU-001`; [Freed](../catalogue/R1-north-america.csv) `R1-US-011`; [Huli (Notas Clínicas con IA)](../catalogue/R10-latin-america.csv) `R10-CR-001`; [Ubie 生成AI (Ubie)](../catalogue/R7-east-asia.csv) `R7-JP-005`; [Nabla](../catalogue/R5-france-southern-europe.csv) `R5-FR-003`.
- **Spread:** 15 countries in 8 regions (R1 R2 R3 R4 R5 R7 R8 R10): Australia, Belgium, Canada, Colombia, Costa Rica, Denmark, Finland, France, Japan, Netherlands, Norway, Sweden, Switzerland, United Kingdom, United States. Launch/breakout: earliest 2011 (Huli (Notas Clínicas con IA), Costa Rica), latest 2025 (Accurx Scribe, United Kingdom); 20/24 rows dated.
- **Best traction:** Heidi (Heidi Health) (Australia): Series B USD 65M led by Point72, 2025-10-05; 2M+ consults per week, 70% outside Australia (excerpt) ([source](https://www.businesswire.com/news/home/20251005012225/en/Heidi-Secures-%2465-Million-USD-in-Series-B-Funding-to-Advance-an-AI-Care-Partner-for-Every-Clinician)); durable signals recorded: 1, 2, 4, 6.
- **Durability: durable.** Members: 2 promising, 14 unproven, 0 hype, 8 no evidence; hype warnings: none; 6 rows with caveats.
- **Polish angle (first thought):** POZ and private clinics: notes into gabinet.gov.pl/P1 or clinic software, e-skierowanie/e-zwolnienie drafts, NFZ coding; entry risk from Tandem Health and Docplanner.
- **All members:** Abridge `R0-US-038`, Ambience Healthcare `R0-US-039`, Tali AI `R1-CA-061`, CareWay (MEDFAR) `R1-CA-062`, Scribeberry `R1-CA-063`, Mikata Health `R1-CA-064`, Freed `R1-US-011`, Chartnote `R1-US-012`, Telepatia `R10-CO-001`, Huli (Notas Clínicas con IA) `R10-CR-001`, Accurx Scribe `R2-GB-014`, TORTUS `R2-GB-015`, Cavell `R3-BE-004`, 44ai (Haidy) `R3-CH-005`, Saipient (Isaac) `R3-CH-006`, Juvoly `R3-NL-001`, Corti `R4-DK-005`, Gosta Labs `R4-FI-004`, Noteless `R4-NO-001`, Tandem Health `R4-SE-001`, Nabla `R5-FR-003`, Ubie 生成AI (Ubie) `R7-JP-005`, Heidi (Heidi Health) `R8-AU-001`, Lyrebird Health `R8-AU-002`.

### TH19

**5. AI-native ledger and finance-team agents** · score 68.7 · batch A

- **What:** AI-first general ledger, spend and close; agents chase payments and check invoices. **LLM role:** agents.
- **B2B/B2C:** B2B 10.
- **Examples:** [Bakuraku (LayerX)](../catalogue/R7-east-asia.csv) `R7-JP-002`; [Xero JAX](../catalogue/R8-oceania-israel.csv) `R8-NZ-002`; [Payhawk](../catalogue/R6-cee-peers.csv) `R6-BG-001`; [Watchdog](../catalogue/R4-nordics-baltics.csv) `R4-NO-005`; [Tabula](../catalogue/R0-global.csv) `R0-DE-088`; [Light](../catalogue/R0-global.csv) `R0-DK-036`.
- **Spread:** 8 countries in 7 regions (R1 R2 R3 R4 R6 R7 R8): Bulgaria, Denmark, Germany, Japan, New Zealand, Norway, United Kingdom, United States. Launch/breakout: earliest 2022 (Light, Denmark), latest 2026 (Balance, United Kingdom); 9/10 rows dated.
- **Best traction:** Bakuraku (LayerX) (Japan): Series B 15bn JPY (TCV lead), 2025-09-02; 15,000+ companies; ARR 100M -> 10bn JPY in 4 years per CEO ([source](https://thebridge.jp/2025/09/layerx-series-b-15-billion-yen-ai-agent-strategy)); durable signals recorded: 1, 4, 8, 10.
- **Durability: durable (thin).** Members: 3 promising, 2 unproven, 0 hype, 5 no evidence; hype warnings: none; 4 rows with caveats.
- **Polish angle (first thought):** Polish GL needs JPK_KR, KSeF, white list VAT; ERP incumbents (Comarch, Symfonia) slow; heavy build.
- **All members:** Tabula `R0-DE-088`, Light `R0-DK-036`, Balance `R0-GB-084`, Rillet `R1-US-028`, Campfire `R1-US-029`, Watchdog `R4-NO-005`, Payhawk `R6-BG-001`, Bakuraku (LayerX) `R7-JP-002`, Xero JAX `R8-NZ-002`, Sterling `R8-NZ-005`.

### TH34

**6. HR and payroll agents** · score 68.7 · batch A

- **What:** Agents inside HR/payroll suites answer employees, audit payroll and automate HR tasks. **LLM role:** agents.
- **B2B/B2C:** B2B 8.
- **Examples:** [Employment Hero (Hero AI agents)](../catalogue/R8-oceania-israel.csv) `R8-AU-011`; [Lohnbot](../catalogue/R3-dach-benelux.csv) `R3-AT-002`; [Factorial (Factorial One)](../catalogue/R5-france-southern-europe.csv) `R5-ES-002`; [Sloneek](../catalogue/R6-cee-peers.csv) `R6-SK-002`; [Buk AI](../catalogue/R10-latin-america.csv) `R10-CL-005`; [50skills](../catalogue/R4-nordics-baltics.csv) `R4-IS-001`.
- **Spread:** 8 countries in 8 regions (R1 R3 R4 R5 R6 R8 R9 R10): Australia, Austria, Chile, Iceland, Slovakia, Spain, United Arab Emirates, United States. Launch/breakout: earliest 2019 (Lohnbot, Austria), latest 2026 (Buk AI, Chile); 8/8 rows dated.
- **Best traction:** Employment Hero (Hero AI agents) (Australia): ~USD 163M ARR 2025-01 (Sacra estimate); company said >A$300M ARR, 2026-02 (excerpt, unverified) ([source](https://sacra.com/c/employment-hero/)); durable signals recorded: 1, 2, 4, 8.
- **Durability: durable.** Members: 3 promising, 4 unproven, 0 hype, 1 no evidence; hype warnings: none; 5 rows with caveats.
- **Polish angle (first thought):** Kadry i płace: ZUS, PPK, L4/e-ZLA, PIT-11; Polish payroll rules are the moat vs Factorial.
- **All members:** Warp `R1-US-048`, Buk AI `R10-CL-005`, Lohnbot `R3-AT-002`, 50skills `R4-IS-001`, Factorial (Factorial One) `R5-ES-002`, Sloneek `R6-SK-002`, Employment Hero (Hero AI agents) `R8-AU-011`, Bayzat AI `R9-AE-006`.

### TH02

**7. Patient call and scheduling agents** · score 67.2 · batch A

- **What:** Voice/text agents answer practice phones, book, confirm and follow up patients. **LLM role:** voice agent.
- **B2B/B2C:** B2B 12.
- **Examples:** [Tucuvi](../catalogue/R5-france-southern-europe.csv) `R5-ES-004`; [Cero](../catalogue/R10-latin-america.csv) `R10-CL-008`; [Vocca](../catalogue/R5-france-southern-europe.csv) `R5-FR-004`; [Hyro](../catalogue/R8-oceania-israel.csv) `R8-IL-006`; [Ufonia (Dora)](../catalogue/R2-uk-ireland.csv) `R2-GB-017`; [Linda AI](../catalogue/R2-uk-ireland.csv) `R2-IE-032`.
- **Spread:** 8 countries in 6 regions (R1 R2 R3 R5 R8 R10): Chile, France, Germany, Ireland, Israel, Spain, United Kingdom, United States. Launch/breakout: earliest 2015 (Eniax (Patricia), Chile), latest 2025 (Linda AI, Ireland); 11/12 rows dated.
- **Best traction:** Tucuvi (Spain): 2.5M+ patients supported, 80+ healthcare organisations, 4 countries, connectors to 50+ EHRs (company site); Series A 20M USD, 2026-01 (seedtable, excerpt); CE class IIb ([source](https://www.tucuvi.com/)); durable signals recorded: 1, 3, 8.
- **Durability: mixed.** Members: 1 promising, 9 unproven, 0 hype, 2 no evidence; hype warnings: none; 4 rows with caveats.
- **Polish angle (first thought):** Polish 'rejestracja telefoniczna' habit; integrations with Polish clinic booking software and ZnanyLekarz; private dentists, physio and vets pay out of pocket.
- **All members:** Hippocratic AI `R0-US-037`, Assort Health `R1-US-013`, Hello Patient `R1-US-014`, Cero `R10-CL-008`, Eniax (Patricia) `R10-CL-009`, Ufonia (Dora) `R2-GB-017`, Linda AI `R2-IE-032`, Mediform (MediVoice) `R3-DE-007`, Aaron.ai (Doctolib) `R3-DE-008`, Tucuvi `R5-ES-004`, Vocca `R5-FR-004`, Hyro `R8-IL-006`.

### TH56

**8. Leasing and property-management agents** · score 64.8 · batch A

- **What:** Agents handle tenant messages, leasing, maintenance and property-manager back office. **LLM role:** agents + voice.
- **B2B/B2C:** B2B 8, B2B2C 1, B2C 1.
- **Examples:** [Re-Leased (Credia)](../catalogue/R8-oceania-israel.csv) `R8-NZ-006`; [Buena](../catalogue/R3-dach-benelux.csv) `R3-DE-013`; [RentBetter](../catalogue/R8-oceania-israel.csv) `R8-AU-013`; [Dwelly](../catalogue/R2-uk-ireland.csv) `R2-GB-010`; [Vessla](../catalogue/R4-nordics-baltics.csv) `R4-SE-006`; [GoCanopy](../catalogue/R5-france-southern-europe.csv) `R5-FR-013`.
- **Spread:** 7 countries in 6 regions (R1 R2 R3 R4 R5 R8): Australia, France, Germany, New Zealand, Sweden, United Kingdom, United States. Launch/breakout: earliest 2023 (EliseAI, United States), latest 2026 (Vessla, Sweden); 9/10 rows dated.
- **Best traction:** Re-Leased (Credia) (New Zealand): US$12.5M led by Movac, 2024-09, half for AI; 1,400 customers, 350,000 tenants, US$7.5bn rent roll (excerpt) ([source](https://itbrief.co.nz/story/re-leased-raises-usd-12-5-million-to-boost-ai-in-real-estate)); durable signals recorded: 1, 3, 8.
- **Durability: mixed.** Members: 1 promising, 5 unproven, 0 hype, 4 no evidence; hype warnings: none; 3 rows with caveats.
- **Polish angle (first thought):** Zarządcy nieruchomości and wspólnoty mieszkaniowe (uchwały, rozliczenia mediów), PRS/najem instytucjonalny, OLX/Otodom leads.
- **All members:** Brickwise `R0-GB-090`, EliseAI `R0-US-041`, Nurture Boss `R1-US-043`, Findigs `R1-US-044`, Dwelly `R2-GB-010`, Buena `R3-DE-013`, Vessla `R4-SE-006`, GoCanopy `R5-FR-013`, RentBetter `R8-AU-013`, Re-Leased (Credia) `R8-NZ-006`.

### TH33

**9. AI recruiting interviews and screening** · score 62.6 · batch A

- **What:** Agents source, screen and interview candidates, often by voice. **LLM role:** voice + agents.
- **B2B/B2C:** B2B 12, B2B2C 1.
- **Examples:** [Hubert](../catalogue/R4-nordics-baltics.csv) `R4-SE-007`; [Maki](../catalogue/R5-france-southern-europe.csv) `R5-FR-009`; [Talentiqa](../catalogue/R6-cee-peers.csv) `R6-CZ-011`; [Carefam](../catalogue/R8-oceania-israel.csv) `R8-IL-007`; [Skillvue](../catalogue/R5-france-southern-europe.csv) `R5-IT-003`; [Alex](../catalogue/R1-north-america.csv) `R1-US-045`.
- **Spread:** 9 countries in 7 regions (R1 R2 R3 R4 R5 R6 R8): Belgium, Cyprus, Czechia, France, Israel, Italy, Sweden, United Kingdom, United States. Launch/breakout: earliest 2017 (Hubert, Sweden), latest 2025 (Talentiqa, Czechia); 12/13 rows dated.
- **Best traction:** Maki (France): Series A 26M EUR (Blossom Capital), 2025-01; clients H&M, BNP Paribas, Deloitte, FIFA; 50+ countries; growth 300% in 2024 (company) ([source](https://www.frenchweb.fr/26-millions-deuros-pour-maki-lia-qui-redefinit-les-kpis-du-recrutement/450693)); durable signals recorded: 1, 4.
- **Durability: mixed.** Members: 0 promising, 8 unproven, 0 hype, 5 no evidence; hype warnings: none; 4 rows with caveats.
- **Polish angle (first thought):** AI Act high-risk (hiring); blue-collar and migrant hiring in PL (agencje pracy, Ukrainian candidates) with multilingual screening.
- **All members:** Spott `R0-BE-063`, Mercor `R0-US-026`, micro1 `R0-US-027`, Alex `R1-US-045`, ConverzAI `R1-US-046`, Juicebox (PeopleGPT) `R1-US-047`, Jack & Jill `R2-GB-023`, Hubert `R4-SE-007`, Cleedee `R5-CY-002`, Maki `R5-FR-009`, Skillvue `R5-IT-003`, Talentiqa `R6-CZ-011`, Carefam `R8-IL-007`.

### TH61

**10. Procurement, RFQ and order handling** · score 62.1 · batch A

- **What:** Reads RFQs and orders, matches catalogues, negotiates suppliers, plans stock. **LLM role:** document understanding + agents.
- **B2B/B2C:** B2B 7.
- **Examples:** [zaico](../catalogue/R7-east-asia.csv) `R7-JP-007`; [Pactum](../catalogue/R4-nordics-baltics.csv) `R4-EE-001`; [Celes](../catalogue/R10-latin-america.csv) `R10-CO-008`; [Duvo](../catalogue/R6-cee-peers.csv) `R6-CZ-003`; [Definic](../catalogue/R6-cee-peers.csv) `R6-SK-005`; [Mercura](../catalogue/R0-global.csv) `R0-DE-083`.
- **Spread:** 7 countries in 5 regions (R3 R4 R6 R7 R10): Colombia, Costa Rica, Czechia, Estonia, Germany, Japan, Slovakia. Launch/breakout: earliest 2023 (Celes, Colombia), latest 2026 (Definic, Slovakia); 6/7 rows dated.
- **Best traction:** zaico (Japan): 180,000+ companies cumulative, retention 92%+, 2025-05; raised 300M JPY (2024-11) and 200M JPY (2025-05) (excerpt) ([source](https://thebridge.jp/2025/05/zaico-raises-200-million-yen-in-may2025)); durable signals recorded: 3, 6, 7.
- **Durability: mixed.** Members: 1 promising, 4 unproven, 0 hype, 2 no evidence; hype warnings: none; 5 rows with caveats.
- **Polish angle (first thought):** Polish technical wholesalers (hurtownie elektryczne, HVAC) quoting from emailed RFQs; Subiekt/Comarch integrations.
- **All members:** Mercura `R0-DE-083`, Celes `R10-CO-008`, Indax `R10-CR-003`, Pactum `R4-EE-001`, Duvo `R6-CZ-003`, Definic `R6-SK-005`, zaico `R7-JP-007`.

### TH23

**11. Enterprise customer-service agents** · score 59.5 · batch A

- **What:** Agents resolve support conversations end to end for large companies. **LLM role:** agents (chat/voice).
- **B2B/B2C:** B2B 15.
- **Examples:** [Omilia](../catalogue/R5-france-southern-europe.csv) `R5-CY-001`; [Intercom Fin](../catalogue/R2-uk-ireland.csv) `R2-IE-030`; [Lorikeet](../catalogue/R8-oceania-israel.csv) `R8-AU-003`; [Infobip AgentOS](../catalogue/R6-cee-peers.csv) `R6-HR-001`; [Wilmo](../catalogue/R4-nordics-baltics.csv) `R4-DK-004`; [Moveo.AI](../catalogue/R5-france-southern-europe.csv) `R5-GR-002`.
- **Spread:** 12 countries in 8 regions (R1 R2 R3 R4 R5 R6 R8 R9): Australia, Croatia, Cyprus, Denmark, Germany, Greece, Ireland, Portugal, Spain, Turkey, United Kingdom, United States. Launch/breakout: earliest 2023 (Gradient Labs, United Kingdom), latest 2026 (Infobip AgentOS, Croatia); 15/15 rows dated.
- **Best traction:** Omilia (Cyprus): Series B 67M USD (Expedition Growth Capital), 2026-08-06; ARR 60M USD (10x since 2020); 200+ enterprise deployments; Capital One, Discover, RBC; ~500 staff ([source](https://techcrunch.com/2026/08/06/omilia-raises-67m-to-scale-its-customer-support-platform/)); durable signals recorded: 1, 4, 8.
- **Durability: mixed.** Members: 1 promising, 9 unproven, 0 hype, 5 no evidence; hype warnings: none; 5 rows with caveats.
- **Polish angle (first thought):** Polish banks/telcos buy from global vendors or build; crowded; little solo-founder room.
- **All members:** Parloa `R0-DE-097`, Gradient Labs `R0-GB-101`, Sierra `R0-US-042`, Decagon `R0-US-043`, PolyAI `R2-GB-021`, Intercom Fin `R2-IE-030`, Wilmo `R4-DK-004`, Omilia `R5-CY-001`, GuruSup `R5-ES-007`, Moveo.AI `R5-GR-002`, Automaise `R5-PT-002`, Visor.ai `R5-PT-004`, Infobip AgentOS `R6-HR-001`, Lorikeet `R8-AU-003`, Jotform AI Agents `R9-TR-010`.

### TH54

**12. Compliance and regtech agents** · score 57.8 · batch A

- **What:** Map regulations to the firm, collect evidence, run AML and product-compliance checks. **LLM role:** document understanding + agents.
- **B2B/B2C:** B2B 8, B2B2C 1.
- **Examples:** [Binderr](../catalogue/R5-france-southern-europe.csv) `R5-MT-001`; [Myriad](../catalogue/R6-cee-peers.csv) `R6-CZ-002`; [Fundvis](../catalogue/R3-dach-benelux.csv) `R3-LU-001`; [ComplyDo](../catalogue/R0-global.csv) `R0-DE-096`; [Complir](../catalogue/R0-global.csv) `R0-DK-092`; [Saturn](../catalogue/R0-global.csv) `R0-GB-085`.
- **Spread:** 7 countries in 6 regions (R1 R2 R3 R4 R5 R6): Czechia, Denmark, Germany, Luxembourg, Malta, United Kingdom, United States. Launch/breakout: earliest 2020 (Binderr, Malta), latest 2026 (Complir, Denmark); 8/9 rows dated.
- **Best traction:** Myriad (Czechia): seed 7.8M USD (~160M CZK), led by Category Ventures, 2025-09-16; earlier 1.8M USD led by N1 ([source](https://www.lupa.cz/aktuality/cesky-startup-byvaleho-inzenyra-v-nvidii-a-googlu-ziskal-160-milionu-na-ai-pro-zvladani-byrokracie/)); durable signals recorded: 1, 10.
- **Durability: mixed (thin).** Members: 0 promising, 3 unproven, 1 hype, 5 no evidence; hype warnings: one-off/lifetime revenue; 2 rows with caveats.
- **Polish angle (first thought):** Dated triggers: KSC/NIS2, GPSR, BDO/EPR, AML for obliged entities (GIIF), AI Act; Polish legal texts are the moat.
- **All members:** ComplyDo `R0-DE-096`, Complir `R0-DK-092`, Saturn `R0-GB-085`, Cardamon `R0-GB-091`, Comp AI `R0-US-019`, Bretton AI `R0-US-054`, Fundvis `R3-LU-001`, Binderr `R5-MT-001`, Myriad `R6-CZ-002`.

### TH17

**13. Agents for accounting and tax firms** · score 57.5 · batch A

- **What:** Agents prepare returns, close books, collect client documents and audit evidence for firms. **LLM role:** agents + document understanding.
- **B2B/B2C:** B2B 12.
- **Examples:** [DataSnipper](../catalogue/R3-dach-benelux.csv) `R3-NL-002`; [Juno](../catalogue/R1-north-america.csv) `R1-US-025`; [Ravical](../catalogue/R3-dach-benelux.csv) `R3-BE-003`; [TreuhandGPT (Connect AI)](../catalogue/R3-dach-benelux.csv) `R3-CH-002`; [Repodo](../catalogue/R4-nordics-baltics.csv) `R4-DK-002`; [Quillon](../catalogue/R6-cee-peers.csv) `R6-BG-002`.
- **Spread:** 8 countries in 5 regions (R1 R2 R3 R4 R6): Belgium, Bulgaria, Denmark, Netherlands, Sweden, Switzerland, United Kingdom, United States. Launch/breakout: earliest 2024 (Filed, United States), latest 2026 (Quillon, Bulgaria); 11/12 rows dated.
- **Best traction:** DataSnipper (Netherlands): Series B 100M USD at 1B USD valuation, 2024-02; 400,000+ auditors in 125 countries incl. Big Four ([source](https://datasnipper.com/resources/datasnipper-raises-100m)); durable signals recorded: 4, 5.
- **Durability: mixed.** Members: 0 promising, 7 unproven, 1 hype, 4 no evidence; hype warnings: layoffs/pivot; 2 rows with caveats.
- **Polish angle (first thought):** Biura rachunkowe face staff shortage and KSeF workload; integrate with Symfonia, Optima, enova, Rewizor.
- **All members:** Filed `R1-US-022`, Accrual `R1-US-023`, Accordance `R1-US-024`, Juno `R1-US-025`, Basis `R1-US-030`, FD Intelligence (PeTAR) `R2-GB-012`, Ravical `R3-BE-003`, TreuhandGPT (Connect AI) `R3-CH-002`, DataSnipper `R3-NL-002`, Repodo `R4-DK-002`, Bluebook `R4-SE-003`, Quillon `R6-BG-002`.

### TH26

**14. AI receptionist for SMEs** · score 57.3 · batch A

- **What:** Answers missed calls, takes messages and books for small businesses. **LLM role:** voice agent.
- **B2B/B2C:** B2B 6.
- **Examples:** [IVRy (アイブリー)](../catalogue/R7-east-asia.csv) `R7-JP-001`; [fonio.ai](../catalogue/R3-dach-benelux.csv) `R3-AT-001`; [HeyDiga](../catalogue/R5-france-southern-europe.csv) `R5-ES-006`; [Linca](../catalogue/R6-cee-peers.csv) `R6-CZ-009`; [Slang.ai](../catalogue/R1-north-america.csv) `R1-US-038`; [goai](../catalogue/R3-dach-benelux.csv) `R3-AT-005`.
- **Spread:** 5 countries in 5 regions (R1 R3 R5 R6 R7): Austria, Czechia, Japan, Spain, United States. Launch/breakout: earliest 2023 (Slang.ai, United States), latest 2025 (Linca, Czechia); 6/6 rows dated.
- **Best traction:** IVRy (アイブリー) (Japan): Series D 4bn JPY, cumulative 10.61bn JPY, 2025-11-06; 50,000+ accounts and 70M calls cumulative, 2025-12 (excerpt) ([source](https://sogyotecho.jp/news/20251106ivry/)); durable signals recorded: 1, 2, 4.
- **Durability: mixed.** Members: 1 promising, 4 unproven, 0 hype, 1 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** Polish customers phone everywhere; Booksy/ZnanyLekarz/Google Calendar integrations; Linca (CZ) and fonio (AT) show the format.
- **All members:** Slang.ai `R1-US-038`, fonio.ai `R3-AT-001`, goai `R3-AT-005`, HeyDiga `R5-ES-006`, Linca `R6-CZ-009`, IVRy (アイブリー) `R7-JP-001`.

### TH24

**15. Local-language voice and CS agents** · score 54.0 · batch A

- **What:** Speech and CS agents tuned to a national language or dialect, sold to local enterprises. **LLM role:** voice agent.
- **B2B/B2C:** B2B 10.
- **Examples:** [Fano Labs](../catalogue/R7-east-asia.csv) `R7-HK-002`; [WIZ.AI](../catalogue/R7-east-asia.csv) `R7-SG-003`; [Born Digital](../catalogue/R6-cee-peers.csv) `R6-CZ-004`; [Wonderful](../catalogue/R8-oceania-israel.csv) `R8-IL-001`; [CNTXT AI (Munsit)](../catalogue/R9-gulf-turkey.csv) `R9-AE-002`; [Lucidya](../catalogue/R9-gulf-turkey.csv) `R9-SA-001`.
- **Spread:** 7 countries in 4 regions (R6 R7 R8 R9): Czechia, Hong Kong, Israel, Saudi Arabia, Singapore, Turkey, United Arab Emirates. Launch/breakout: earliest 2015 (Fano Labs, Hong Kong), latest 2025 (Sawt, Saudi Arabia); 10/10 rows dated.
- **Best traction:** WIZ.AI (Singapore): Series B tens of millions USD led by SMBC Asia Rising Fund, 2025-11-05; revenue +100% 2024-25 ([source](https://technode.global/2025/11/05/singapores-wiz-ai-raises-tens-of-millions-in-series-b-to-scale-enterprise-agi-solution-globally/)); durable signals recorded: 1, 4, 5.
- **Durability: durable.** Members: 2 promising, 5 unproven, 0 hype, 3 no evidence; hype warnings: none; 8 rows with caveats.
- **Polish angle (first thought):** Polish speech is handled by global voice stacks; Born Digital (CZ) and Wonderful (IL) are entry risks; enterprise sales cycle.
- **All members:** Freya `R0-TR-089`, Born Digital `R6-CZ-004`, Fano Labs `R7-HK-002`, WIZ.AI `R7-SG-003`, Wonderful `R8-IL-001`, CNTXT AI (Munsit) `R9-AE-002`, Lucidya `R9-SA-001`, Intella `R9-SA-002`, Wittify.ai `R9-SA-006`, Sawt `R9-SA-007`.

### TH37

**16. Study material generators** · score 52.5 · batch A

- **What:** Turns lectures, notes and PDFs into summaries, flashcards and quizzes. **LLM role:** generation + transcription.
- **B2B/B2C:** B2C 12.
- **Examples:** [Knowunity](../catalogue/R3-dach-benelux.csv) `R3-DE-009`; [StudyFi](../catalogue/R6-cee-peers.csv) `R6-CZ-010`; [Univ AI (유니브 AI, Singularity)](../catalogue/R7-east-asia.csv) `R7-KR-010`; [Gizmo](../catalogue/R2-uk-ireland.csv) `R2-GB-028`; [Algor Education](../catalogue/R5-france-southern-europe.csv) `R5-IT-005`; [MaxStudy](../catalogue/R8-oceania-israel.csv) `R8-IL-012`.
- **Spread:** 10 countries in 7 regions (R2 R3 R5 R6 R7 R8 R9): Czechia, France, Germany, Ireland, Israel, Italy, Saudi Arabia, South Korea, Switzerland, United Kingdom. Launch/breakout: earliest 2023 (Gizmo, United Kingdom), latest 2026 (MaxStudy, Israel); 12/12 rows dated.
- **Best traction:** Knowunity (Germany): Series B 27M EUR, 2025-06; 20M+ users in 15 countries; 1 in 3 German students ([source](https://tech.eu/2025/06/13/knowunity-raises-eur27m-to-bring-ai-tutor-to-1-billion-students/)); durable signals recorded: 3, 5.
- **Durability: hype.** Members: 0 promising, 5 unproven, 4 hype, 3 no evidence; hype warnings: thin wrapper; 4 rows with caveats.
- **Polish angle (first thought):** Polish students and matura; crowded and absorbable by ChatGPT/NotebookLM; curriculum alignment is the only edge.
- **All members:** Gizmo `R2-GB-028`, SimpleStudy `R2-IE-037`, Studyflash `R3-CH-003`, Knowunity `R3-DE-009`, Baobab `R5-FR-012`, Kiwi AI `R5-IT-004`, Algor Education `R5-IT-005`, StudyFi `R6-CZ-010`, Univ AI (유니브 AI, Singularity) `R7-KR-010`, MaxStudy `R8-IL-012`, Bites `R9-SA-014`, AcadAI `R9-SA-015`.

### TH21

**17. Consumer tax filing** · score 52.3 · batch A

- **What:** Apps file personal income tax, find deductions and refunds, often per-filing priced. **LLM role:** document understanding + assistant.
- **B2B/B2C:** B2C 8.
- **Examples:** [삼쩜삼 (Samjjeomsam, Jobis&Villains)](../catalogue/R7-east-asia.csv) `R7-KR-001`; [Heru](../catalogue/R10-latin-america.csv) `R10-MX-002`; [TaxDown](../catalogue/R5-france-southern-europe.csv) `R5-ES-001`; [Skatteguiden](../catalogue/R4-nordics-baltics.csv) `R4-DK-003`; [Taxcut](../catalogue/R5-france-southern-europe.csv) `R5-FR-011`; [Fifteenth](../catalogue/R1-north-america.csv) `R1-US-026`.
- **Spread:** 7 countries in 6 regions (R1 R3 R4 R5 R7 R10): Denmark, France, Germany, Mexico, South Korea, Spain, United States. Launch/breakout: earliest 2020 (Skatteguiden, Denmark), latest 2026 (삼쩜삼 (Samjjeomsam, Jobis&Villains), South Korea); 8/8 rows dated.
- **Best traction:** 삼쩜삼 (Samjjeomsam, Jobis&Villains) (South Korea): 24M cumulative sign-ups and >2 trillion KRW refunds filed, 2025-07; AI Q&A in Kakao since 2026-03 ([source](https://www.venturesquare.net/1109902/)); durable signals recorded: 1, 4, 7, 8.
- **Durability: mixed.** Members: 1 promising, 6 unproven, 0 hype, 1 no evidence; hype warnings: none; 3 rows with caveats.
- **Polish angle (first thought):** Twój e-PIT pre-fills most returns free; room in ulgi, rental ryczałt, foreign income for return migrants and Ukrainians.
- **All members:** Fifteenth `R1-US-026`, Deduction (Taylor, CPAI) `R1-US-027`, Heru `R10-MX-002`, Taxfix `R3-DE-016`, Skatteguiden `R4-DK-003`, TaxDown `R5-ES-001`, Taxcut `R5-FR-011`, 삼쩜삼 (Samjjeomsam, Jobis&Villains) `R7-KR-001`.

### TH04

**18. Care-provider documentation and operations** · score 52.3 · batch A

- **What:** Care records, compliance paperwork, scheduling and staffing for home, aged and disability care. **LLM role:** voice + generation + agents.
- **B2B/B2C:** B2B 6, B2C 1.
- **Examples:** [Minikai](../catalogue/R8-oceania-israel.csv) `R8-AU-010`; [NAGARA (ながらかいご)](../catalogue/R7-east-asia.csv) `R7-JP-010`; [Kibu](../catalogue/R0-global.csv) `R0-US-020`; [Cera](../catalogue/R2-uk-ireland.csv) `R2-GB-020`; [Zingage](../catalogue/R1-north-america.csv) `R1-US-017`; [Arya Health](../catalogue/R1-north-america.csv) `R1-US-018`.
- **Spread:** 4 countries in 4 regions (R1 R2 R7 R8): Australia, Japan, United Kingdom, United States. Launch/breakout: earliest 2016 (Cera, United Kingdom), latest 2025 (NAGARA (ながらかいご), Japan); 4/7 rows dated.
- **Best traction:** Minikai (Australia): seed A$2.5M led by Tidal Ventures with Antler, 2025-02-14; take-up by larger NDIS providers (excerpt) ([source](https://www.businessnewsaustralia.com/articles/tech-startup-minikai-secures--2-5m-in-seed-funding-amid-strong-take-up-by-ndis-service-providers.html)); durable signals recorded: 1, 2, 8, 10.
- **Durability: mixed.** Members: 1 promising, 3 unproven, 0 hype, 3 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** Ageing and carer shortage; DPS/ZOL/ŚDS and opieka wytchnieniowa documentation, MOPS-funded home care contracts.
- **All members:** Kibu `R0-US-020`, Zingage `R1-US-017`, Arya Health `R1-US-018`, Axle Health `R1-US-019`, Cera `R2-GB-020`, NAGARA (ながらかいご) `R7-JP-010`, Minikai `R8-AU-010`.

### TH29

**19. Conversational commerce on messaging apps** · score 48.9 · batch A

- **What:** WhatsApp/LINE agents sell, support and collect for merchants. **LLM role:** agents (chat).
- **B2B/B2C:** B2B 10.
- **Examples:** [Chattigo](../catalogue/R10-latin-america.csv) `R10-CL-004`; [Omnichat](../catalogue/R7-east-asia.csv) `R7-HK-001`; [Dapta](../catalogue/R10-latin-america.csv) `R10-CO-002`; [qeen.ai](../catalogue/R9-gulf-turkey.csv) `R9-AE-003`; [Avify](../catalogue/R10-latin-america.csv) `R10-CR-002`; [Yavendió](../catalogue/R10-latin-america.csv) `R10-MX-012`.
- **Spread:** 6 countries in 3 regions (R7 R9 R10): Chile, Colombia, Costa Rica, Hong Kong, Mexico, United Arab Emirates. Launch/breakout: earliest 2015 (Chattigo, Chile), latest 2026 (Pulpos, Mexico); 10/10 rows dated.
- **Best traction:** Omnichat (Hong Kong): Series A 10M USD led by Openspace, 2026-10-27; 5,000+ brands; ~300 brands adopted OmniClaw in two months ([source](https://kyodonewsprwire.jp/release/202610278750)); durable signals recorded: 1, 4, 8.
- **Durability: durable.** Members: 2 promising, 7 unproven, 0 hype, 1 no evidence; hype warnings: none; 8 rows with caveats.
- **Polish angle (first thought):** WhatsApp-centred buying does not transfer to PL (phone, email, Messenger, Allegro chat); pricing per qualified meeting is the transferable idea.
- **All members:** Vambe `R10-CL-003`, Chattigo `R10-CL-004`, Wots `R10-CL-010`, Dapta `R10-CO-002`, Truora `R10-CO-007`, Avify `R10-CR-002`, Yavendió `R10-MX-012`, Pulpos `R10-MX-013`, Omnichat `R7-HK-001`, qeen.ai `R9-AE-003`.

### TH06

**20. Consumer health coaching and triage** · score 47.7 · batch A

- **What:** Apps for symptom triage, therapy companions, physio, nutrition and family health logs. **LLM role:** conversation + vision.
- **B2B/B2C:** B2C 5, B2B2C 3, B2B 1.
- **Examples:** [Sword Health (AI Care / Mind)](../catalogue/R5-france-southern-europe.csv) `R5-PT-001`; [XUND](../catalogue/R3-dach-benelux.csv) `R3-AT-003`; [Persly (퍼슬리)](../catalogue/R7-east-asia.csv) `R7-KR-007`; [初日手帳 (Churi baby journal)](../catalogue/R7-east-asia.csv) `R7-TW-008`; [Limbic](../catalogue/R2-uk-ireland.csv) `R2-GB-016`; [Persikas](../catalogue/R4-nordics-baltics.csv) `R4-LT-005`.
- **Spread:** 8 countries in 6 regions (R1 R2 R3 R4 R5 R7): Austria, Cyprus, Lithuania, Portugal, South Korea, Taiwan, United Kingdom, United States. Launch/breakout: earliest 2020 (XUND, Austria), latest 2025 (初日手帳 (Churi baby journal), Taiwan); 8/9 rows dated.
- **Best traction:** Sword Health (AI Care / Mind) (Portugal): 40M USD at 4B USD valuation (General Catalyst), 2025-06; revenue run rate ~240M USD 2025 (TechCrunch, excerpt) ([source](https://hitconsultant.net/2025/06/17/sword-health-raises-40m-launches-ai-powered-mental-health-solution-mind/)); durable signals recorded: 1, 4.
- **Durability: hype.** Members: 0 promising, 4 unproven, 2 hype, 3 no evidence; hype warnings: novelty use case, paid ads/influencers; 2 rows with caveats.
- **Polish angle (first thought):** Health-system queues push people to self-help; medical-device and liability risk; IKP data access is the local hook.
- **All members:** Cal AI `R1-US-053`, Limbic `R2-GB-016`, Flok Health `R2-GB-018`, XUND `R3-AT-003`, Persikas `R4-LT-005`, Soula `R5-CY-003`, Sword Health (AI Care / Mind) `R5-PT-001`, Persly (퍼슬리) `R7-KR-007`, 初日手帳 (Churi baby journal) `R7-TW-008`.

### TH10

**21. Law-practice operations and AI secretariat** · score 47.7 · batch A

- **What:** Intake, time capture, case files and drafting chores for small law firms. **LLM role:** agents + document understanding.
- **B2B/B2C:** B2B 6.
- **Examples:** [JUPUS](../catalogue/R3-dach-benelux.csv) `R3-DE-001`; [Lemontech (LIA)](../catalogue/R10-latin-america.csv) `R10-CL-006`; [PointOne](../catalogue/R0-global.csv) `R0-US-069`; [Clio](../catalogue/R1-north-america.csv) `R1-CA-059`; [Safahat.ai](../catalogue/R9-gulf-turkey.csv) `R9-TR-003`; [LawX](../catalogue/R3-dach-benelux.csv) `R3-DE-002`.
- **Spread:** 5 countries in 4 regions (R1 R3 R9 R10): Canada, Chile, Germany, Turkey, United States. Launch/breakout: earliest 2023 (JUPUS, Germany), latest 2025 (Safahat.ai, Turkey); 6/6 rows dated.
- **Best traction:** JUPUS (Germany): Series A 13M EUR, 2026-06; 2,000+ lawyers, 2,000+ new cases/day; ARR quadrupled in 2025 (company) ([source](https://www.startbase.de/news/13-millionen-euro-fuer-jupus/)); durable signals recorded: 1, 4.
- **Durability: mixed (thin).** Members: 0 promising, 3 unproven, 0 hype, 3 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Kancelarie and radcy: Portal Informacyjny Sądów, e-Sąd/EPU, Polish court letters; small firms phone-first.
- **All members:** PointOne `R0-US-069`, Clio `R1-CA-059`, Lemontech (LIA) `R10-CL-006`, JUPUS `R3-DE-001`, LawX `R3-DE-002`, Safahat.ai `R9-TR-003`.

### TH13

**22. Consumer legal help and AI-enabled law firms** · score 47.7 · batch A

- **What:** Consumers get answers, drafted claims and appeals, with a lawyer behind the AI. **LLM role:** generation.
- **B2B/B2C:** B2C 5, B2B2C 3.
- **Examples:** [LoFrayer (לא פראייר)](../catalogue/R8-oceania-israel.csv) `R8-IL-011`; [Valla](../catalogue/R2-uk-ireland.csv) `R2-GB-024`; [Lawren.ai](../catalogue/R6-cee-peers.csv) `R6-RO-002`; [Mohami](../catalogue/R9-gulf-turkey.csv) `R9-SA-004`; [Legaline](../catalogue/R9-gulf-turkey.csv) `R9-AE-005`; [AI+ Avocat](../catalogue/R6-cee-peers.csv) `R6-RO-003`.
- **Spread:** 5 countries in 4 regions (R2 R6 R8 R9): Israel, Romania, Saudi Arabia, United Arab Emirates, United Kingdom. Launch/breakout: earliest 2023 (Valla, United Kingdom), latest 2026 (Legaline, United Arab Emirates); 6/8 rows dated.
- **Best traction:** LoFrayer (לא פראייר) (Israel): IL Finance top-grossing #12, 2026-11-01; 5 ratings (read); founder reports a demand letter from the Israel Bar Association claiming unauthorised legal practice (LinkedIn post, excerpt, URL not identified) ([source](https://apps.apple.com/il/app/lofrayer-%D7%A2%D7%A8%D7%A2%D7%95%D7%A8-%D7%93%D7%95%D7%97-%D7%97%D7%A0%D7%99%D7%94/id6762531291)); durable signals recorded: 1, 2.
- **Durability: mixed.** Members: 0 promising, 5 unproven, 0 hype, 3 no evidence; hype warnings: none; 6 rows with caveats.
- **Polish angle (first thought):** Unauthorised-practice risk is lower in PL (no bar monopoly on advice); mandaty, ZUS/US letters, consumer complaints, employment disputes.
- **All members:** Lawhive `R2-GB-001`, Valla `R2-GB-024`, Lawren.ai `R6-RO-002`, AI+ Avocat `R6-RO-003`, LoFrayer (לא פראייר) `R8-IL-011`, Legaline `R9-AE-005`, Mohami `R9-SA-004`, Malakah `R9-SA-016`.

### TH40

**23. AI speaking and language tutors** · score 47.4 · batch A

- **What:** Voice conversation partners for language practice. **LLM role:** voice + generation.
- **B2B/B2C:** B2C 11.
- **Examples:** [SpeakBUDDY](../catalogue/R7-east-asia.csv) `R7-JP-006`; [Toko](../catalogue/R7-east-asia.csv) `R7-TW-005`; [Vocal Image](../catalogue/R4-nordics-baltics.csv) `R4-EE-003`; [TalkMe (Inspired AI)](../catalogue/R7-east-asia.csv) `R7-SG-005`; [Speak](../catalogue/R1-north-america.csv) `R1-US-052`; [Xeropan](../catalogue/R6-cee-peers.csv) `R6-HU-005`.
- **Spread:** 9 countries in 5 regions (R1 R2 R4 R6 R7): Estonia, Finland, Hungary, Japan, Singapore, South Korea, Taiwan, United Kingdom, United States. Launch/breakout: earliest 2014 (Lingvist, Estonia), latest 2026 (Mochispi (モチスピ), Japan); 11/11 rows dated.
- **Best traction:** SpeakBUDDY (Japan): JP Education top-grossing #6, 63,645 ratings, 2026-11-01; 3.5M downloads and 1.85bn JPY total funding, 2024-09 (excerpt) ([source](https://apps.apple.com/jp/app/id1129621266)); durable signals recorded: 3, 4.
- **Durability: hype.** Members: 1 promising, 6 unproven, 2 hype, 2 no evidence; hype warnings: paid ads/influencers; 5 rows with caveats.
- **Polish angle (first thought):** Crowded for English; Polish-for-migrants (Ukrainians, B1 exam) is the local driver, as Kielo is for Finnish.
- **All members:** Speak `R1-US-052`, Praktika `R2-GB-029`, Vocal Image `R4-EE-003`, Lingvist `R4-EE-006`, Kielo `R4-FI-003`, Xeropan `R6-HU-005`, SpeakBUDDY `R7-JP-006`, Mochispi (モチスピ) `R7-JP-009`, Heyring (헤이링, Hypernova) `R7-KR-008`, TalkMe (Inspired AI) `R7-SG-005`, Toko `R7-TW-005`.

## Batch B (23 themes, Poland check T17)

### TH15

**24. Property transaction and title diligence** · score 47.2 · batch B

- **What:** Title, lease and registry checks, conveyancing chasing and company/notary filings. **LLM role:** document understanding + agents.
- **B2B/B2C:** B2B 4, B2C 1.
- **Examples:** [Moverly](../catalogue/R2-uk-ireland.csv) `R2-GB-009`; [Paraito](../catalogue/R1-north-america.csv) `R1-CA-060`; [Beglaubigt.de](../catalogue/R0-global.csv) `R0-DE-074`; [Orbital](../catalogue/R2-uk-ireland.csv) `R2-GB-008`; [Conveyd](../catalogue/R2-uk-ireland.csv) `R2-GB-007`.
- **Spread:** 3 countries in 3 regions (R1 R2 R3): Canada, Germany, United Kingdom. Launch/breakout: earliest 2023 (Orbital, United Kingdom), latest 2025 (Conveyd, United Kingdom); 4/5 rows dated.
- **Best traction:** Moverly (United Kingdom): 350+ agencies, 70,000+ properties; Connells: +43% completion rate, 35% faster exchange over 1,200 transactions ([source](https://moverly.com/)); durable signals recorded: 3, 5, 8.
- **Durability: mixed.** Members: 1 promising, 3 unproven, 0 hype, 1 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Księgi wieczyste (EKW), EGiB, MPZP, notarial deeds, KRS/S24 filings: strong registry moat.
- **All members:** Beglaubigt.de `R0-DE-074`, Paraito `R1-CA-060`, Conveyd `R2-GB-007`, Orbital `R2-GB-008`, Moverly `R2-GB-009`.

### TH59

**25. Citizen and SME public-service navigators** · score 45.3 · batch B

- **What:** Assistants guide citizens and SMEs through entitlements, forms and agencies. **LLM role:** retrieval + generation.
- **B2B/B2C:** B2C 3, B2B 2, B2B2C 1, B2G 1.
- **Examples:** [Kol Zchut AI chat (כל זכות)](../catalogue/R8-oceania-israel.csv) `R8-IL-009`; [Bürokratt](../catalogue/R4-nordics-baltics.csv) `R4-EE-004`; [mAigov (gov.gr)](../catalogue/R5-france-southern-europe.csv) `R5-GR-003`; [TAMM AutoGov (Abu Dhabi)](../catalogue/R9-gulf-turkey.csv) `R9-AE-007`; [Issa (Bahrain Chamber)](../catalogue/R9-gulf-turkey.csv) `R9-BH-001`; [EffiGov](../catalogue/R1-north-america.csv) `R1-US-010`.
- **Spread:** 7 countries in 6 regions (R1 R3 R4 R5 R8 R9): Bahrain, Estonia, Germany, Greece, Israel, United Arab Emirates, United States. Launch/breakout: earliest 2023 (mAigov (gov.gr), Greece), latest 2025 (Issa (Bahrain Chamber), Bahrain); 6/7 rows dated.
- **Best traction:** Kol Zchut AI chat (כל זכות) (Israel): site had ~31.5M Hebrew and 1.75M Arabic visits in 2024; chat funded by Ministry of Justice with National Digital Agency; retrieval model funded by Israel Innovation Authority, article 2025-07-29 (read) ([source](https://www.ice.co.il/career/news/article/1076864)); durable signals recorded: 2, 5, 8.
- **Durability: mixed.** Members: 0 promising, 5 unproven, 1 hype, 1 no evidence; hype warnings: one-off/lifetime revenue; 5 rows with caveats.
- **Polish angle (first thought):** mObywatel and gov.pl absorb basics; private intermediaries for 800+, ZUS benefits, migrants' paperwork may remain.
- **All members:** EffiGov `R1-US-010`, Elterngeld Buddy `R3-DE-015`, Bürokratt `R4-EE-004`, mAigov (gov.gr) `R5-GR-003`, Kol Zchut AI chat (כל זכות) `R8-IL-009`, TAMM AutoGov (Abu Dhabi) `R9-AE-007`, Issa (Bahrain Chamber) `R9-BH-001`.

### TH14

**26. Debt recovery agents** · score 45.3 · batch B

- **What:** Voice/text agents and drafted letters collect consumer and B2B debts, up to small claims. **LLM role:** voice + generation + agents.
- **B2B/B2C:** B2B 5.
- **Examples:** [Mozart](../catalogue/R10-latin-america.csv) `R10-UY-002`; [Garfield.Law](../catalogue/R2-uk-ireland.csv) `R2-GB-003`; [QuickLegal](../catalogue/R6-cee-peers.csv) `R6-RO-004`; [Domu Technology Inc.](../catalogue/R0-global.csv) `R0-US-061`; [CollectWise](../catalogue/R0-global.csv) `R0-US-082`.
- **Spread:** 4 countries in 4 regions (R1 R2 R6 R10): Romania, United Kingdom, United States, Uruguay. Launch/breakout: earliest 2023 (QuickLegal, Romania), latest 2025 (Garfield.Law, United Kingdom); 5/5 rows dated.
- **Best traction:** QuickLegal (Romania): pre-seed EUR 620K target incl. EUR 360K from EIT Digital and Bravva Angels, 2025-02; earlier EUR 236K from EEA/Norway grants and investors; goal of 1,000+ users ([source](https://ceelegalmatters.com/romania/23093-quicklegal-secures-eur-236-000-in-funding-to-develop-legal-platform)); durable signals recorded: 1, 2.
- **Durability: mixed.** Members: 0 promising, 3 unproven, 0 hype, 2 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** Windykacja polubowna under UOKiK rules, EPU e-court small claims, KRD/BIG registries; SMEs chasing invoices after KSeF.
- **All members:** Domu Technology Inc. `R0-US-061`, CollectWise `R0-US-082`, Mozart `R10-UY-002`, Garfield.Law `R2-GB-003`, QuickLegal `R6-RO-004`.

### TH27

**27. Trades and home-services front office** · score 45.3 · batch B

- **What:** Answers calls, dispatches, quotes and does paperwork for installers and contractors. **LLM role:** voice + agents + generation.
- **B2B/B2C:** B2B 9.
- **Examples:** [plancraft](../catalogue/R3-dach-benelux.csv) `R3-DE-012`; [Handoff](../catalogue/R0-global.csv) `R0-US-098`; [Installer (formerly Proptly)](../catalogue/R4-nordics-baltics.csv) `R4-NO-004`; [Elyos AI](../catalogue/R0-global.csv) `R0-GB-100`; [Avoca](../catalogue/R1-north-america.csv) `R1-US-034`; [autarc](../catalogue/R0-global.csv) `R0-DE-073`.
- **Spread:** 4 countries in 4 regions (R1 R2 R3 R4): Germany, Norway, United Kingdom, United States. Launch/breakout: earliest 2023 (Handoff, United States), latest 2025 (Installer (formerly Proptly), Norway); 7/9 rows dated.
- **Best traction:** plancraft (Germany): Series B 38M EUR, 2025-08; 20,000+ craft businesses in 11 countries ([source](https://www.htgf.de/plancraft-series-b/)); durable signals recorded: 4.
- **Durability: mixed (thin).** Members: 0 promising, 4 unproven, 0 hype, 5 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Fachowcy shortage; Czyste Powietrze/Mój Prąd paperwork, KNR/Sekocenbud estimates, Oferteo/Fixly leads.
- **All members:** autarc `R0-DE-073`, Elyos AI `R0-GB-100`, Handoff `R0-US-098`, Netic `R1-US-033`, Avoca `R1-US-034`, Probook `R1-US-035`, Broccoli AI `R1-US-036`, plancraft `R3-DE-012`, Installer (formerly Proptly) `R4-NO-004`.

### TH32

**28. Tender and bid writing** · score 45.3 · batch B

- **What:** Analyses tender documents and drafts bid answers from company knowledge. **LLM role:** document understanding + generation.
- **B2B/B2C:** B2B 4.
- **Examples:** [Cato](../catalogue/R5-france-southern-europe.csv) `R5-IT-002`; [AutogenAI](../catalogue/R2-uk-ireland.csv) `R2-GB-022`; [Brainial](../catalogue/R3-dach-benelux.csv) `R3-NL-003`; [Brickanta](../catalogue/R0-global.csv) `R0-SE-081`.
- **Spread:** 4 countries in 4 regions (R2 R3 R4 R5): Italy, Netherlands, Sweden, United Kingdom. Launch/breakout: earliest 2019 (Brainial, Netherlands), latest 2025 (Cato, Italy); 4/4 rows dated.
- **Best traction:** Cato (Italy): Seed 6M EUR (Keen Venture Partners), 2026-09; 7.6M EUR total; first client 2025-10; customer count not disclosed ([source](https://techfundingnews.com/cato-raises-6m-seed-keen-venture-partners-public-tenders-ai/)); durable signals recorded: 1, 8.
- **Durability: mixed.** Members: 0 promising, 3 unproven, 0 hype, 1 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** e-Zamówienia/BZP, JEDZ, Pzp; public tenders excluded as a sales channel but SMEs bidding into them are buyers.
- **All members:** Brickanta `R0-SE-081`, AutogenAI `R2-GB-022`, Brainial `R3-NL-003`, Cato `R5-IT-002`.

### TH05

**29. Clinical evidence and decision support** · score 43.7 · batch B

- **What:** Cited answers over literature, guidelines and drug databases for clinicians; pre-visit summaries. **LLM role:** search + generation.
- **B2B/B2C:** B2B 4, B2B2C 2.
- **Examples:** [Navina](../catalogue/R8-oceania-israel.csv) `R8-IL-005`; [Mediately](../catalogue/R6-cee-peers.csv) `R6-SI-004`; [PMcardio (Powerful Medical)](../catalogue/R6-cee-peers.csv) `R6-SK-003`; [OpenEvidence](../catalogue/R0-global.csv) `R0-US-029`; [Eolas Medical](../catalogue/R2-uk-ireland.csv) `R2-GB-019`; [EvidenceMD](../catalogue/R10-latin-america.csv) `R10-MX-009`.
- **Spread:** 6 countries in 5 regions (R1 R2 R6 R8 R10): Israel, Mexico, Slovakia, Slovenia, United Kingdom, United States. Launch/breakout: earliest 2021 (PMcardio (Powerful Medical), Slovakia), latest 2025 (Mediately, Slovenia); 6/6 rows dated.
- **Best traction:** Navina (Israel): Series C USD 55M (Goldman Sachs), 2025-03, total USD 100M; 10,000+ clinicians in 1,300 clinics (excerpt) ([source](https://en.globes.co.il/en/article-israeli-clinical-ai-co-navina-raises-55m-1001505824)); durable signals recorded: 1, 2, 4, 8.
- **Durability: mixed.** Members: 1 promising, 2 unproven, 1 hype, 2 no evidence; hype warnings: thin wrapper; 2 rows with caveats.
- **Polish angle (first thought):** Polish ChPL drug labels, Polish society guidelines and refund lists (obwieszczenia MZ); medical-device/MDR risk for decision support.
- **All members:** OpenEvidence `R0-US-029`, EvidenceMD `R10-MX-009`, Eolas Medical `R2-GB-019`, Mediately `R6-SI-004`, PMcardio (Powerful Medical) `R6-SK-003`, Navina `R8-IL-005`.

### TH46

**30. Agent builder platforms and AI services** · score 43.5 · batch B

- **What:** No-code/low-code platforms and services that build agents and 'AI employees' for companies. **LLM role:** agents.
- **B2B/B2C:** B2B 17.
- **Examples:** [Dust](../catalogue/R5-france-southern-europe.csv) `R5-FR-008`; [GeneXus Next](../catalogue/R10-latin-america.csv) `R10-UY-006`; [Robotiq.ai](../catalogue/R6-cee-peers.csv) `R6-HR-002`; [DRUID AI](../catalogue/R6-cee-peers.csv) `R6-RO-006`; [Augusta Labs](../catalogue/R5-france-southern-europe.csv) `R5-PT-005`; [Relevance AI](../catalogue/R8-oceania-israel.csv) `R8-AU-004`.
- **Spread:** 14 countries in 8 regions (R1 R3 R4 R5 R6 R8 R9 R10): Australia, Colombia, Croatia, France, Germany, Greece, Israel, Lithuania, Portugal, Romania, Saudi Arabia, Spain, United States, Uruguay. Launch/breakout: earliest 2022 (Distyl AI, United States), latest 2026 (Symphony by Wix, Israel); 16/17 rows dated.
- **Best traction:** Dust (France): Series B 40M USD (Sequoia, Abstract), 2026-05; ARR >20M USD (from ~1M two years earlier); 3,000+ business customers; 300,000+ agents ([source](https://www.maddyness.com/2026/05/18/ia-dust-leve-40-millions-de-dollars-pour-accelerer-sa-croissance-aux-etats-unis/)); durable signals recorded: 3, 4, 8.
- **Durability: mixed.** Members: 1 promising, 11 unproven, 0 hype, 5 no evidence; hype warnings: layoffs/pivot; 10 rows with caveats.
- **Polish angle (first thought):** Horizontal; pattern evidence only; possible as a services wedge for Polish SMEs.
- **All members:** n8n `R0-DE-102`, Distyl AI `R0-US-046`, Gumloop `R0-US-066`, Innovaitors `R10-CO-006`, Roma AI `R10-UY-003`, GeneXus Next `R10-UY-006`, Sintra `R4-LT-001`, Maisa `R5-ES-003`, Dust `R5-FR-008`, Twin `R5-FR-014`, Helvia.ai `R5-GR-004`, Augusta Labs `R5-PT-005`, Robotiq.ai `R6-HR-002`, DRUID AI `R6-RO-006`, Relevance AI `R8-AU-004`, Symphony by Wix `R8-IL-003`, Velents `R9-SA-009`.

### TH20

**31. Tax research copilots for professionals** · score 42.2 · batch B

- **What:** Cited answers over tax law, rulings and guidance for accountants and advisers. **LLM role:** retrieval + generation.
- **B2B/B2C:** B2B 5.
- **Examples:** [Blue J](../catalogue/R1-north-america.csv) `R1-CA-056`; [SavvyWise](../catalogue/R8-oceania-israel.csv) `R8-AU-009`; [Nexana.ai](../catalogue/R6-cee-peers.csv) `R6-SK-001`; [Leapifai](../catalogue/R2-uk-ireland.csv) `R2-IE-038`; [TaxGPT](../catalogue/R0-global.csv) `R0-US-065`.
- **Spread:** 5 countries in 4 regions (R1 R2 R6 R8): Australia, Canada, Ireland, Slovakia, United States. Launch/breakout: earliest 2015 (Blue J, Canada), latest 2026 (Nexana.ai, Slovakia); 5/5 rows dated.
- **Best traction:** Blue J (Canada): Series D 122M USD, 2025-08; 2,500+ organisations; revenue and customers more than doubled H1 2025 ([source](https://betakit.com/blue-j-series-d-after-doubling-revenue/)); durable signals recorded: 3, 4, 8.
- **Durability: mixed.** Members: 1 promising, 3 unproven, 0 hype, 1 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** KIS interpretations (EUREKA), NSA/WSA rulings, objaśnienia MF; doradcy podatkowi and biura rachunkowe as buyers.
- **All members:** TaxGPT `R0-US-065`, Blue J `R1-CA-056`, Leapifai `R2-IE-038`, Nexana.ai `R6-SK-001`, SavvyWise `R8-AU-009`.

### TH35

**32. Teacher copilot** · score 42.2 · batch B

- **What:** Lesson plans, feedback, grading and differentiation tools for teachers. **LLM role:** generation + vision.
- **B2B/B2C:** B2B2C 5, B2B 2, B2C 1.
- **Examples:** [Ed.ai](../catalogue/R5-france-southern-europe.csv) `R5-FR-007`; [fobizz](../catalogue/R3-dach-benelux.csv) `R3-DE-010`; [Brisk Teaching](../catalogue/R1-north-america.csv) `R1-US-050`; [Nurture](../catalogue/R2-uk-ireland.csv) `R2-IE-036`; [TeachMateAI](../catalogue/R2-uk-ireland.csv) `R2-GB-026`; [MagicSchool](../catalogue/R1-north-america.csv) `R1-US-049`.
- **Spread:** 5 countries in 4 regions (R1 R2 R3 R5): France, Germany, Ireland, United Kingdom, United States. Launch/breakout: earliest 2023 (MagicSchool, United States), latest 2024 (Ed.ai, France); 8/8 rows dated.
- **Best traction:** Ed.ai (France): Seed 5M EUR (Bpifrance, La Poste Ventures), 2026-09; ~2,500 papers/day in 2026-06 vs ~100/week in 2025-09; 100,000+ papers in 6 months ([source](https://www.boursedirect.fr/fr/actualites/categorie/opcvm/ed-ai-leve-5-millions-d-euros-boursier-5fc3295ce7d18f51b73c4d7c6b41c04e76f5765f)); durable signals recorded: 1, 4, 5.
- **Durability: mixed.** Members: 1 promising, 4 unproven, 0 hype, 3 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Podstawa programowa, reforma 'Kompas Jutra', e-Dziennik (Librus/Vulcan); state may build its own (ZPE).
- **All members:** MagicSchool `R1-US-049`, Brisk Teaching `R1-US-050`, SchoolAI `R1-US-051`, TeachMateAI `R2-GB-026`, Oak National Academy Aila `R2-GB-027`, Nurture `R2-IE-036`, fobizz `R3-DE-010`, Ed.ai `R5-FR-007`.

### TH38

**33. AI tutors for national curricula** · score 41.1 · batch B

- **What:** Tutors and homework helpers tied to a curriculum, teacher persona or national exam. **LLM role:** vision + generation + voice.
- **B2B/B2C:** B2C 6, B2B 1.
- **Examples:** [Astra AI](../catalogue/R6-cee-peers.csv) `R6-SI-001`; [默書啦喂 (Dictation Law Wai, LW Group)](../catalogue/R7-east-asia.csv) `R7-HK-004`; [NSWEduChat (NSW Department of Education)](../catalogue/R8-oceania-israel.csv) `R8-AU-014`; [Third Space Learning (Skye)](../catalogue/R2-uk-ireland.csv) `R2-GB-025`; [Mea Kal (מאה קל)](../catalogue/R8-oceania-israel.csv) `R8-IL-014`; [Kuba](../catalogue/R6-cee-peers.csv) `R6-CZ-008`.
- **Spread:** 6 countries in 4 regions (R2 R6 R7 R8): Australia, Czechia, Hong Kong, Israel, Slovenia, United Kingdom. Launch/breakout: earliest 2024 (General Learning, Hong Kong), latest 2025 (Mea Kal (מאה קל), Israel); 7/7 rows dated.
- **Best traction:** Astra AI (Slovenia): ARR 25M USD claimed, 2026-06-22 (ARR.Club, self-reported/unverified); Education top-grossing on 2026-11-01: HR #2, SI #3, CZ #4, BG #4, RO #14, SK #19, DE #25, AT #33, PL #84; 3,453 ratings in PL store; bootstrapped ([source](https://www.arr.club/astra-ai)); durable signals recorded: 4, 5, 7.
- **Durability: mixed.** Members: 1 promising, 4 unproven, 1 hype, 1 no evidence; hype warnings: paid ads/influencers; 4 rows with caveats.
- **Polish angle (first thought):** Matura and egzamin ósmoklasisty on CKE criteria; Astra AI (SI) already charts in PL; creator + exam recipe.
- **All members:** General Learning `R0-HK-070`, Third Space Learning (Skye) `R2-GB-025`, Kuba `R6-CZ-008`, Astra AI `R6-SI-001`, 默書啦喂 (Dictation Law Wai, LW Group) `R7-HK-004`, NSWEduChat (NSW Department of Education) `R8-AU-014`, Mea Kal (מאה קל) `R8-IL-014`.

### TH60

**34. Freight and logistics agents** · score 40.2 · batch B

- **What:** Voice/email agents book carriers, track loads and handle broker work. **LLM role:** voice + agents.
- **B2B/B2C:** B2B 3, B2B2C 1.
- **Examples:** [Nuvocargo (Nuvo AI)](../catalogue/R10-latin-america.csv) `R10-MX-011`; [ShipBee](../catalogue/R9-gulf-turkey.csv) `R9-QA-002`; [FleetWorks](../catalogue/R1-north-america.csv) `R1-US-039`; [HappyRobot](../catalogue/R1-north-america.csv) `R1-US-040`.
- **Spread:** 3 countries in 3 regions (R1 R9 R10): Mexico, Qatar, United States. Launch/breakout: earliest 2019 (Nuvocargo (Nuvo AI), Mexico), latest 2024 (ShipBee, Qatar); 3/4 rows dated.
- **Best traction:** ShipBee (Qatar): seed USD 500k led by GrowthX Capital, 2026-03; earlier USD 235k pre-seed 2025-06; partners Snoonu, Qatar Post, DHL (excerpt) ([source](https://meatechwatch.com/2026/03/12/shipbee-secures-500k-seed-funding-to-revolutionize-gcc-digital-logistics/)); durable signals recorded: 5.
- **Durability: mixed (thin).** Members: 0 promising, 2 unproven, 0 hype, 2 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** Poland is the EU's largest road-freight country; spedytorzy on Trans.eu/Timocom; Polish/Ukrainian drivers by phone.
- **All members:** FleetWorks `R1-US-039`, HappyRobot `R1-US-040`, Nuvocargo (Nuvo AI) `R10-MX-011`, ShipBee `R9-QA-002`.

### TH22

**35. Personal finance assistant** · score 40.0 · batch B

- **What:** Analyses bank data or statements, coaches spending, savings and credit. **LLM role:** classification + conversation.
- **B2B/B2C:** B2C 9, B2B2C 1.
- **Examples:** [RiseUp](../catalogue/R8-oceania-israel.csv) `R8-IL-010`; [Finno](../catalogue/R10-latin-america.csv) `R10-MX-008`; [Bilance](../catalogue/R4-nordics-baltics.csv) `R4-EE-005`; [Intellectia](../catalogue/R7-east-asia.csv) `R7-HK-005`; [Cleo](../catalogue/R0-global.csv) `R0-GB-030`; [Dovly AI](../catalogue/R1-north-america.csv) `R1-US-055`.
- **Spread:** 10 countries in 7 regions (R1 R2 R3 R4 R7 R8 R10): Belgium, Colombia, Estonia, Hong Kong, Iceland, Israel, Mexico, New Zealand, United Kingdom, United States. Launch/breakout: earliest 2017 (RiseUp, Israel), latest 2026 (Kvittun, Iceland); 8/10 rows dated.
- **Best traction:** RiseUp (Israel): IL Finance top-grossing #3, 2026-11-01 (read); USD 30M round 2022; halved workforce 2024-04 citing war (excerpt) ([source](https://thepaypers.com/online-mobile-banking/israel-based-riseup-raises-usd-30-mln--1255790)); durable signals recorded: 2, 3, 7.
- **Durability: mixed (thin).** Members: 0 promising, 4 unproven, 0 hype, 6 no evidence; hype warnings: layoffs/pivot; 5 rows with caveats.
- **Polish angle (first thought):** Open banking (PSD2) in PL; BIK credit reports; licence-heavy if it advises on investments; hype in AI stock-signal apps.
- **All members:** Cleo `R0-GB-030`, Dovly AI `R1-US-055`, Kebo `R10-CO-005`, Finno `R10-MX-008`, Warren `R3-BE-006`, Bilance `R4-EE-005`, Kvittun `R4-IS-002`, Intellectia `R7-HK-005`, RiseUp `R8-IL-010`, SortMe `R8-NZ-008`.

### TH18

**36. Invoice and receipt capture with auto-booking** · score 39.8 · batch B

- **What:** Extracts and codes invoices and receipts, matches bank lines, books entries. **LLM role:** document understanding.
- **B2B/B2C:** B2B 4.
- **Examples:** [Digitoo](../catalogue/R6-cee-peers.csv) `R6-CZ-005`; [Outmin](../catalogue/R2-uk-ireland.csv) `R2-IE-035`; [Cifrato](../catalogue/R0-global.csv) `R0-CO-093`; [Autoboeker](../catalogue/R3-dach-benelux.csv) `R3-NL-005`.
- **Spread:** 4 countries in 4 regions (R2 R3 R6 R10): Colombia, Czechia, Ireland, Netherlands. Launch/breakout: earliest 2021 (Digitoo, Czechia), latest 2025 (Cifrato, Colombia); 3/4 rows dated.
- **Best traction:** Digitoo (Czechia): 1M+ invoices processed (company/Forbes CZ, excerpt); 150,000 invoices/month and 650 sign-ups in 3 months, 2022-11; seed EUR 2.3M (Reflex Capital), 2023-12 ([source](https://cc.cz/vytvari-umelou-ucetni-a-hlasi-novou-investici-uz-jsme-mysleli-ze-to-nedame-rika-zakladatelka/)); durable signals recorded: 1, 3, 5.
- **Durability: mixed (thin).** Members: 1 promising, 1 unproven, 0 hype, 2 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** KSeF makes structured invoices standard, so capture of paper/foreign invoices and receipts shrinks; matching and booking stays.
- **All members:** Cifrato `R0-CO-093`, Outmin `R2-IE-035`, Autoboeker `R3-NL-005`, Digitoo `R6-CZ-005`.

### TH52

**37. Marketing, SEO and ad agents** · score 38.7 · batch B

- **What:** Agents write content, run SEO/AI-answer visibility, ads and social posting. **LLM role:** generation + agents.
- **B2B/B2C:** B2B 7, B2B2C 1.
- **Examples:** [Appier](../catalogue/R7-east-asia.csv) `R7-TW-004`; [AEO Engine](../catalogue/R0-global.csv) `R0-US-021`; [Photoroom](../catalogue/R0-global.csv) `R0-FR-004`; [Postiz](../catalogue/R0-global.csv) `R0-HK-023`; [SEOBOT](../catalogue/R0-global.csv) `R0-TR-024`; [Cometly](../catalogue/R0-global.csv) `R0-US-018`.
- **Spread:** 5 countries in 4 regions (R1 R5 R7 R9): France, Hong Kong, Taiwan, Turkey, United States. Launch/breakout: earliest 2020 (Cometly, United States), latest 2026 (Kolr (iKala), Taiwan); 8/8 rows dated.
- **Best traction:** Appier (Taiwan): FY2025 revenue JPY 43.7bn (+28% YoY), operating profit JPY 3.0bn; FY2026 guidance JPY 54bn (2026-02-13) ([source](https://kyodonewsprwire.jp/release/202602134109)); durable signals recorded: 3, 4.
- **Durability: mixed.** Members: 1 promising, 4 unproven, 1 hype, 2 no evidence; hype warnings: novelty use case, tourists/spike; 3 rows with caveats.
- **Polish angle (first thought):** Polish SMEs buy from local agencies; AI-answer visibility (AEO) in Polish; Allegro/Ceneo listings.
- **All members:** Photoroom `R0-FR-004`, Postiz `R0-HK-023`, SEOBOT `R0-TR-024`, Cometly `R0-US-018`, AEO Engine `R0-US-021`, Uplane `R0-US-076`, Kolr (iKala) `R7-TW-003`, Appier `R7-TW-004`.

### TH03

**38. Healthcare back-office automation** · score 37.5 · batch B

- **What:** Agents read referrals, code encounters, run prior authorisation, claims and records requests. **LLM role:** document understanding + agents.
- **B2B/B2C:** B2B 11.
- **Examples:** [Parallel](../catalogue/R0-global.csv) `R0-FR-086`; [Tennr](../catalogue/R0-global.csv) `R0-US-040`; [Asepha](../catalogue/R1-north-america.csv) `R1-CA-065`; [Codes Health](../catalogue/R0-global.csv) `R0-US-064`; [Trellis AI](../catalogue/R0-global.csv) `R0-US-071`; [mdhub](../catalogue/R0-global.csv) `R0-US-078`.
- **Spread:** 3 countries in 2 regions (R1 R5): Canada, France, United States. Launch/breakout: earliest 2023 (Tennr, United States), latest 2024 (Asepha, Canada); 8/11 rows dated.
- **Best traction:** Candid Health (United States): Series D 120M USD (excerpt; date not shown) ([source](https://www.mobihealthnews.com/news/arintra-raises-25m-ai-revenue-assurance-platform)); durable signals recorded: none recorded.
- **Durability: mixed (thin).** Members: 0 promising, 0 unproven, 0 hype, 11 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Mostly US payer bureaucracy; Polish analogue is NFZ settlement (SWIAD, JGP coding) for private providers with NFZ contracts: narrower but real.
- **All members:** Parallel `R0-FR-086`, Tennr `R0-US-040`, Codes Health `R0-US-064`, Trellis AI `R0-US-071`, mdhub `R0-US-078`, Ember `R0-US-079`, Asepha `R1-CA-065`, Arintra `R1-US-015`, Anterior `R1-US-016`, Foundation Health `R1-US-020`, Candid Health `R1-US-021`.

### TH55

**39. Insurance operations agents** · score 37.5 · batch B

- **What:** Submission intake, servicing, claims and brokerage work for insurers and brokers. **LLM role:** document understanding + agents.
- **B2B/B2C:** B2B 8, B2C 1.
- **Examples:** [Handle](../catalogue/R10-latin-america.csv) `R10-MX-001`; [Foliume](../catalogue/R10-latin-america.csv) `R10-UY-004`; [Corgi Insurance](../catalogue/R0-global.csv) `R0-US-055`; [Crabi](../catalogue/R10-latin-america.csv) `R10-MX-010`; [ClaimSorted](../catalogue/R0-global.csv) `R0-US-062`; [FurtherAI](../catalogue/R0-global.csv) `R0-US-067`.
- **Spread:** 3 countries in 2 regions (R1 R10): Mexico, United States, Uruguay. Launch/breakout: earliest 2022 (Foliume, Uruguay), latest 2026 (Handle, Mexico); 7/9 rows dated.
- **Best traction:** Handle (Mexico): seed USD 6M led by a16z; >75 active brokers in Mexico; claims registration time -94%, ~8 h/week saved per executive (company figures), 2026-03 ([source](https://latamlist.com/handle-raises-6m-seed-round-led-by-andreessen-horowitz/)); durable signals recorded: 1, 2, 8.
- **Durability: mixed (thin).** Members: 0 promising, 3 unproven, 0 hype, 6 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Polish multiagencje and brokers (KNF-registered), insurer portals, OC/AC comparison; licence needed only to sell, not for tools.
- **All members:** Corgi Insurance `R0-US-055`, ClaimSorted `R0-US-062`, FurtherAI `R0-US-067`, Harper `R0-US-080`, Outmarket `R1-US-031`, Covu `R1-US-032`, Handle `R10-MX-001`, Crabi `R10-MX-010`, Foliume `R10-UY-004`.

### TH68

**40. Fraud, identity and trust** · score 37.1 · batch B

- **What:** Scam call/message detection, ID verification, content moderation and counterfeit evidence. **LLM role:** classification + vision + agents.
- **B2B/B2C:** B2B 3, B2B2C 1.
- **Examples:** [Whoscall (Gogolook)](../catalogue/R7-east-asia.csv) `R7-TW-001`; [Signa](../catalogue/R10-latin-america.csv) `R10-CO-003`; [Microblink](../catalogue/R6-cee-peers.csv) `R6-HR-004`; [elv.ai](../catalogue/R6-cee-peers.csv) `R6-SK-004`.
- **Spread:** 4 countries in 3 regions (R6 R7 R10): Colombia, Croatia, Slovakia, Taiwan. Launch/breakout: earliest 2023 (Signa, Colombia), latest 2026 (Microblink, Croatia); 4/4 rows dated.
- **Best traction:** Whoscall (Gogolook) (Taiwan): 2024 revenue NT$867M (+12%), 24M MAU, 100M downloads, 46% subscription, 400 enterprise customers (2025-03) ([source](https://www.bnext.com.tw/article/82652/gogolook-2024-financial-statements)); durable signals recorded: 2, 3, 4, 8.
- **Durability: mixed.** Members: 1 promising, 3 unproven, 0 hype, 0 no evidence; hype warnings: none; 3 rows with caveats.
- **Polish angle (first thought):** Senior-targeted scams (na wnuczka, BLIK, fake bank calls); Allegro/OLX counterfeit evidence packs for brand owners.
- **All members:** Signa `R10-CO-003`, Microblink `R6-HR-004`, elv.ai `R6-SK-004`, Whoscall (Gogolook) `R7-TW-001`.

### TH30

**41. AI SDR and outbound prospecting** · score 35.2 · batch B

- **What:** Agents find prospects, write and send outreach, book meetings. **LLM role:** agents.
- **B2B/B2C:** B2B 6.
- **Examples:** [GojiberryAI](../catalogue/R0-global.csv) `R0-US-022`; [Zero](../catalogue/R4-nordics-baltics.csv) `R4-FI-001`; [Topo](../catalogue/R0-global.csv) `R0-FR-094`; [throxy](../catalogue/R0-global.csv) `R0-GB-058`; [Handhold](../catalogue/R4-nordics-baltics.csv) `R4-EE-002`; [Artisan](../catalogue/R0-global.csv) `R0-US-059`.
- **Spread:** 5 countries in 4 regions (R1 R2 R4 R5): Estonia, Finland, France, United Kingdom, United States. Launch/breakout: earliest 2024 (Topo, France), latest 2026 (Zero, Finland); 6/6 rows dated.
- **Best traction:** Zero (Finland): Seed 10.3M USD led by Primary Venture Partners, 2026-09-15 (pre-seed 2.7M USD 2024-12); 13 staff; generally available with 14-day trial ([source](https://tech.eu/2026/09/15/crm-challenger-zero-gets-backing-from-lovable-and-langdock-founders-in-10m-raise/)); durable signals recorded: 6.
- **Durability: mixed (thin).** Members: 0 promising, 2 unproven, 1 hype, 3 no evidence; hype warnings: layoffs/pivot; 2 rows with caveats.
- **Polish angle (first thought):** Polish B2B cold outreach under RODO and PKE (Prawo komunikacji elektronicznej) consent rules; CEIDG/KRS as lead data.
- **All members:** Topo `R0-FR-094`, throxy `R0-GB-058`, GojiberryAI `R0-US-022`, Artisan `R0-US-059`, Handhold `R4-EE-002`, Zero `R4-FI-001`.

### TH39

**42. National and migration exam prep** · score 35.2 · batch B

- **What:** AI scoring and practice for national, professional or visa exams. **LLM role:** generation + scoring.
- **B2B/B2C:** B2C 6.
- **Examples:** [Jurafuchs](../catalogue/R3-dach-benelux.csv) `R3-DE-011`; [MyMersi (마이메르시, MediCherry)](../catalogue/R7-east-asia.csv) `R7-KR-009`; [Mujtahid for Qudurat (مجتهد للقدرات)](../catalogue/R9-gulf-turkey.csv) `R9-SA-013`; [PTE Practice & AI Mock Tests (Language Academy)](../catalogue/R8-oceania-israel.csv) `R8-AU-015`; [English BeKalut: Amirnet/Psychometric (אנגלית בקלות)](../catalogue/R8-oceania-israel.csv) `R8-IL-013`; [APEUni PTE](../catalogue/R8-oceania-israel.csv) `R8-AU-016`.
- **Spread:** 5 countries in 4 regions (R3 R7 R8 R9): Australia, Germany, Israel, Saudi Arabia, South Korea. Launch/breakout: earliest 2018 (APEUni PTE, Australia), latest 2025 (English BeKalut: Amirnet/Psychometric (אנגלית בקלות), Israel); 6/6 rows dated.
- **Best traction:** Jurafuchs (Germany): 500k EUR growth capital, 2025-12; profitable 2+ years; 20,000+ MAU; AI answers several thousand forum questions/month ([source](https://www.startbase.de/news/jurafuchs-erhaelt-weitere-500-000-euro-wachstumskapital-von-bestandsinvestoren/)); durable signals recorded: 3, 5.
- **Durability: hype.** Members: 0 promising, 3 unproven, 3 hype, 0 no evidence; hype warnings: one-off/lifetime revenue; 2 rows with caveats.
- **Polish angle (first thought):** Certyfikat B1 z polskiego for residence/citizenship, driving-theory test, LEK/LDEK, aplikacje prawnicze.
- **All members:** Jurafuchs `R3-DE-011`, MyMersi (마이메르시, MediCherry) `R7-KR-009`, PTE Practice & AI Mock Tests (Language Academy) `R8-AU-015`, APEUni PTE `R8-AU-016`, English BeKalut: Amirnet/Psychometric (אנגלית בקלות) `R8-IL-013`, Mujtahid for Qudurat (مجتهد للقدرات) `R9-SA-013`.

### TH57

**43. Real-estate agency and investor tools** · score 35.2 · batch B

- **What:** Assistants for agents and investors: CRM chasing, listings, valuations, plot potential. **LLM role:** generation + data.
- **B2B/B2C:** B2B 5, B2C 2.
- **Examples:** [Tapusor](../catalogue/R9-gulf-turkey.csv) `R9-TR-006`; [Prop-AI](../catalogue/R9-gulf-turkey.csv) `R9-AE-008`; [Agentsy](../catalogue/R8-oceania-israel.csv) `R8-AU-012`; [HouseWhisper](../catalogue/R1-north-america.csv) `R1-US-041`; [Propcorn](../catalogue/R3-dach-benelux.csv) `R3-AT-004`; [Coraly.ai](../catalogue/R9-gulf-turkey.csv) `R9-AE-009`.
- **Spread:** 5 countries in 4 regions (R1 R3 R8 R9): Australia, Austria, Turkey, United Arab Emirates, United States. Launch/breakout: earliest 2017 (Tapusor, Turkey), latest 2026 (Agentsy, Australia); 6/7 rows dated.
- **Best traction:** Tapusor (Turkey): Turkey App Store top-grossing Business #19; 2,680 ratings, 4.6 stars, 2026-11-01 ([source](https://apps.apple.com/tr/app/tapusor/id1260192075)); durable signals recorded: 2, 7, 8.
- **Durability: mixed.** Members: 0 promising, 3 unproven, 1 hype, 3 no evidence; hype warnings: layoffs/pivot; 3 rows with caveats.
- **Polish angle (first thought):** Otodom/OLX listings, RCiWN transaction prices, MPZP/WZ plot potential, EKW.
- **All members:** HouseWhisper `R1-US-041`, MaxHome.AI `R1-US-042`, Propcorn `R3-AT-004`, Agentsy `R8-AU-012`, Prop-AI `R9-AE-008`, Coraly.ai `R9-AE-009`, Tapusor `R9-TR-006`.

### TH67

**44. Agents inside SMB retail and hospitality systems** · score 35.2 · batch B

- **What:** POS, gym and rental systems where agents run menus, stock, pricing and member messages. **LLM role:** agents + vision.
- **B2B/B2C:** B2B 4, B2B2C 1.
- **Examples:** [TabSense](../catalogue/R9-gulf-turkey.csv) `R9-SA-008`; [Emilia AI](../catalogue/R10-latin-america.csv) `R10-CO-004`; [Órale AI - Punto de Venta](../catalogue/R10-latin-america.csv) `R10-MX-007`; [Sigvi](../catalogue/R4-nordics-baltics.csv) `R4-LT-003`; [1club AI](../catalogue/R6-cee-peers.csv) `R6-BG-004`.
- **Spread:** 5 countries in 4 regions (R4 R6 R9 R10): Bulgaria, Colombia, Lithuania, Mexico, Saudi Arabia. Launch/breakout: earliest 2023 (Sigvi, Lithuania), latest 2026 (Órale AI - Punto de Venta, Mexico); 5/5 rows dated.
- **Best traction:** TabSense (Saudi Arabia): USD 5M led by Jasoor Ventures, 2025-10-21; 1,000+ clients in Saudi Arabia and Jordan; STC and Zain partnerships (read) ([source](https://www.wamda.com/en/2025/10/tabsense-attracts-5-million-backing-jasoor-ventures)); durable signals recorded: 2, 5, 8.
- **Durability: mixed.** Members: 0 promising, 4 unproven, 0 hype, 1 no evidence; hype warnings: none; 3 rows with caveats.
- **Polish angle (first thought):** Polish gastro POS and fiscal printers (KSeF, kasy online), gyms on Medicover/Multisport cards.
- **All members:** Emilia AI `R10-CO-004`, Órale AI - Punto de Venta `R10-MX-007`, Sigvi `R4-LT-003`, 1club AI `R6-BG-004`, TabSense `R9-SA-008`.

### TH11

**45. Plaintiff litigation casework** · score 35.1 · batch B

- **What:** Builds medical chronologies, demand letters and case files for plaintiff and injury firms. **LLM role:** document understanding + generation.
- **B2B/B2C:** B2B 4.
- **Examples:** [Turbo Law](../catalogue/R9-gulf-turkey.csv) `R9-TR-004`; [EvenUp](../catalogue/R0-global.csv) `R0-US-044`; [Eve](../catalogue/R1-north-america.csv) `R1-US-001`; [Supio](../catalogue/R1-north-america.csv) `R1-US-002`.
- **Spread:** 2 countries in 2 regions (R1 R9): Turkey, United States. Launch/breakout: earliest 2023 (EvenUp, United States), latest 2025 (Turbo Law, Turkey); 4/4 rows dated.
- **Best traction:** Turbo Law (Turkey): seed/pre-seed USD 3.8M led by Revo Capital, 2026-06-18; 1,800+ active case files, 5M+ pages processed (company claim, excerpt) ([source](https://www.globallegalpost.com/news/us-ai-litigation-platform-start-up-turbo-law-raises-38m-in-pre-seed-funding-round-1445015597)); durable signals recorded: 1, 2, 8.
- **Durability: mixed (thin).** Members: 0 promising, 1 unproven, 0 hype, 3 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Kancelarie odszkodowawcze: OC claims, zadośćuczynienie letters, medical record reading; Polish damages practice differs from US PI.
- **All members:** EvenUp `R0-US-044`, Eve `R1-US-001`, Supio `R1-US-002`, Turbo Law `R9-TR-004`.

### TH64

**46. AI-moderated market research** · score 35.1 · batch B

- **What:** AI runs and synthesises qualitative interviews. **LLM role:** voice agent + synthesis.
- **B2B/B2C:** B2B 2.
- **Examples:** [Bolt Insight (BoltChatAI)](../catalogue/R9-gulf-turkey.csv) `R9-TR-009`; [Conveo](../catalogue/R0-global.csv) `R0-GB-057`.
- **Spread:** 2 countries in 2 regions (R2 R9): Turkey, United Kingdom. Launch/breakout: earliest 2023 (Bolt Insight (BoltChatAI), Turkey), latest 2024 (Conveo, United Kingdom); 2/2 rows dated.
- **Best traction:** Bolt Insight (BoltChatAI) (Turkey): GBP 7M led by Pembroke VCT with 212 and others, 2025-12-09 ([source](https://www.research-live.com/article/news/bolt-insight-secures-7m-investment/id/5145333)); durable signals recorded: 1, 4.
- **Durability: mixed (thin).** Members: 0 promising, 1 unproven, 0 hype, 1 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Polish research agencies and FMCG; cheap fieldwork replacement; small market.
- **All members:** Conveo `R0-GB-057`, Bolt Insight (BoltChatAI) `R9-TR-009`.

## Batch C (23 themes, Poland check T18)

### TH08

**47. Law-firm AI workspace and knowledge** · score 34.9 · batch C

- **What:** Enterprise AI workspace over a firm's own documents, precedents and email. **LLM role:** document understanding + agents.
- **B2B/B2C:** B2B 8.
- **Examples:** [DeepJudge](../catalogue/R3-dach-benelux.csv) `R3-CH-001`; [Legora](../catalogue/R0-global.csv) `R0-SE-032`; [LEGALFLY](../catalogue/R3-dach-benelux.csv) `R3-BE-002`; [Libra](../catalogue/R3-dach-benelux.csv) `R3-DE-004`; [Newcode](../catalogue/R4-nordics-baltics.csv) `R4-NO-002`; [Harvey](../catalogue/R0-global.csv) `R0-US-031`.
- **Spread:** 6 countries in 3 regions (R1 R3 R4): Belgium, Germany, Norway, Sweden, Switzerland, United States. Launch/breakout: earliest 2021 (DeepJudge, Switzerland), latest 2025 (Aloi, Sweden); 8/8 rows dated.
- **Best traction:** DeepJudge (Switzerland): Series A 41.2M USD (Felicis), 2025-11; revenue +500% YoY; customers Freshfields, Holland & Knight, Schoenherr ([source](https://legaltechnology.com/2025/11/04/in-brief-deepjudge-raises-41-2m-series-a-announces-freshfields-as-a-customer/)); durable signals recorded: 4, 8.
- **Durability: mixed.** Members: 0 promising, 7 unproven, 0 hype, 1 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Large firms already buy Harvey/Legora-style tools; publishers (Wolters Kluwer, C.H. Beck) are entering; weak solo-founder fit.
- **All members:** Legora `R0-SE-032`, Harvey `R0-US-031`, LEGALFLY `R3-BE-002`, Henchman (Lexis Create) `R3-BE-005`, DeepJudge `R3-CH-001`, Libra `R3-DE-004`, Newcode `R4-NO-002`, Aloi `R4-SE-004`.

### TH62

**48. AI-native engineering design** · score 34.9 · batch C

- **What:** AI designs building services and manages engineering requirements, sold as an outcome. **LLM role:** generation + agents.
- **B2B/B2C:** B2B 3.
- **Examples:** [Solvera](../catalogue/R4-nordics-baltics.csv) `R4-NO-003`; [Endra](../catalogue/R4-nordics-baltics.csv) `R4-SE-005`; [Trace.Space](../catalogue/R4-nordics-baltics.csv) `R4-LV-004`.
- **Spread:** 3 countries in 1 regions (R4): Latvia, Norway, Sweden. Launch/breakout: earliest 2022 (Trace.Space, Latvia), latest 2026 (Solvera, Norway); 3/3 rows dated.
- **Best traction:** Solvera (Norway): Pre-seed 60M NOK led by Seedcamp, 2026-10-15; 10M+ NOK contracted revenue in first three months; customer Betonmast ([source](https://www.shifter.no/nyheter/henter-inn-60-millioner-kroner-etter-noen-maneder-i-drift/303542)); durable signals recorded: 1, 7.
- **Durability: mixed.** Members: 0 promising, 2 unproven, 0 hype, 1 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Polish building norms and projekt budowlany rules; licensed engineers (uprawnienia) needed to sign.
- **All members:** Trace.Space `R4-LV-004`, Solvera `R4-NO-003`, Endra `R4-SE-005`.

### TH28

**49. Car-dealer agents** · score 31.2 · batch C

- **What:** Agents book service, answer sales calls and follow up leads for dealerships. **LLM role:** voice + agents.
- **B2B/B2C:** B2B 3.
- **Examples:** [Flai](../catalogue/R10-latin-america.csv) `R10-UY-005`; [Sandra AI](../catalogue/R0-global.csv) `R0-FR-087`; [Toma](../catalogue/R1-north-america.csv) `R1-US-037`.
- **Spread:** 3 countries in 3 regions (R1 R5 R10): France, United States, Uruguay. Launch/breakout: earliest 2024 (Sandra AI, France), latest 2025 (Flai, Uruguay); 3/3 rows dated.
- **Best traction:** Flai (Uruguay): Series A USD 27M led by Base10; >50,000 appointments/month; >10 of the 50 largest US dealer groups; revenue 20x in a year, 2026-10 ([source](https://latamlist.com/flai-raises-27m-series-a-to-expand-ai-agents-for-us-car-dealerships/)); durable signals recorded: 1, 4, 8.
- **Durability: mixed.** Members: 1 promising, 0 unproven, 1 hype, 1 no evidence; hype warnings: layoffs/pivot; 0 rows with caveats.
- **Polish angle (first thought):** Polish dealer groups and independent workshops; Otomoto leads; DMS integrations.
- **All members:** Sandra AI `R0-FR-087`, Toma `R1-US-037`, Flai `R10-UY-005`.

### TH31

**50. Sales conversation intelligence and coaching** · score 30.1 · batch C

- **What:** Records and analyses sales calls, coaches reps, builds role-play training. **LLM role:** voice + generation.
- **B2B/B2C:** B2B 4.
- **Examples:** [deelan](../catalogue/R3-dach-benelux.csv) `R3-LU-002`; [Diio](../catalogue/R10-latin-america.csv) `R10-CL-007`; [Leracom AI](../catalogue/R10-latin-america.csv) `R10-MX-005`; [Overpath](../catalogue/R2-uk-ireland.csv) `R2-IE-039`.
- **Spread:** 4 countries in 3 regions (R2 R3 R10): Chile, Ireland, Luxembourg, Mexico. Launch/breakout: earliest 2025 (Diio, Chile), latest 2026 (Leracom AI, Mexico); 4/4 rows dated.
- **Best traction:** deelan (Luxembourg): Seed led by Expon Capital, 2026-06 (amount not disclosed; 740k EUR per Paperjam, excerpt); early adopters report 30%+ shorter ramp time (company) ([source](https://chronicle.lu/category/business/61494-deelan-ai-secures-luxembourg-led-investment-round)); durable signals recorded: 1.
- **Durability: mixed (thin).** Members: 0 promising, 1 unproven, 0 hype, 3 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** Polish-language call analysis; crowded by Gong-likes; niche in field sales of Polish distributors.
- **All members:** Diio `R10-CL-007`, Leracom AI `R10-MX-005`, Overpath `R2-IE-039`, deelan `R3-LU-002`.

### TH45

**51. Natural-language analytics over company data** · score 30.1 · batch C

- **What:** Ask questions in plain language over ERP, CRM and finance data. **LLM role:** agents + text-to-query.
- **B2B/B2C:** B2B 4.
- **Examples:** [Primero (Primia)](../catalogue/R10-latin-america.csv) `R10-MX-006`; [iGenius (now Domyn)](../catalogue/R5-france-southern-europe.csv) `R5-IT-006`; [Zeit AI](../catalogue/R0-global.csv) `R0-DE-095`; [Dataizen (Neural Coders)](../catalogue/R10-latin-america.csv) `R10-CR-004`.
- **Spread:** 4 countries in 3 regions (R3 R5 R10): Costa Rica, Germany, Italy, Mexico. Launch/breakout: earliest 2024 (Zeit AI, Germany), latest 2026 (Primero (Primia), Mexico); 3/4 rows dated.
- **Best traction:** iGenius (now Domyn) (Italy): Raised 650M EUR (unicorn), 2024-06; clients Allianz, Aon, Intesa Sanpaolo, Enel; ARR target 20M EUR end-2024; site now redirects to domyn.com ([source](https://forbes.it/2024/06/12/igenius-ha-raccolto-650-milioni-di-euro-e-il-primo-unicorno-italiano-nellia/)); durable signals recorded: 8.
- **Durability: mixed (thin).** Members: 0 promising, 2 unproven, 0 hype, 2 no evidence; hype warnings: none; 2 rows with caveats.
- **Polish angle (first thought):** Polish ERPs (Comarch Optima, Symfonia, enova, Subiekt) have weak analytics; SMB owners ask in Polish.
- **All members:** Zeit AI `R0-DE-095`, Dataizen (Neural Coders) `R10-CR-004`, Primero (Primia) `R10-MX-006`, iGenius (now Domyn) `R5-IT-006`.

### TH58

**52. Government back-office AI** · score 30.1 · batch C

- **What:** Permit and zoning checks, assistants for civil servants. **LLM role:** document understanding + generation.
- **B2B/B2C:** B2B 4, B2G 2.
- **Examples:** [Pair (GovTech / Open Government Products)](../catalogue/R7-east-asia.csv) `R7-SG-006`; [Intric](../catalogue/R4-nordics-baltics.csv) `R4-SE-002`; [HKGAI V1 / HKPilot](../catalogue/R7-east-asia.csv) `R7-HK-003`; [GovWell](../catalogue/R1-north-america.csv) `R1-US-007`; [Govstream.ai](../catalogue/R1-north-america.csv) `R1-US-008`; [Madison AI](../catalogue/R1-north-america.csv) `R1-US-009`.
- **Spread:** 4 countries in 3 regions (R1 R4 R7): Hong Kong, Singapore, Sweden, United States. Launch/breakout: earliest 2023 (GovWell, United States), latest 2025 (HKGAI V1 / HKPilot, Hong Kong); 5/6 rows dated.
- **Best traction:** Pair (GovTech / Open Government Products) (Singapore): 148 agencies, 55,000 public-officer users, 50% active (GovTech CTO, excerpt); >half of 150,000 officers regular users (2026, excerpt) ([source](https://govinsider.asia/intl-en/article/governments-role-important-to-ensure-use-of-ai-for-public-good-says-govtech-cto)); durable signals recorded: 2, 3.
- **Durability: mixed (thin).** Members: 0 promising, 3 unproven, 0 hype, 3 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Public tenders excluded; Prawo budowlane/MPZP checks could be sold to architects instead of gminy.
- **All members:** GovWell `R1-US-007`, Govstream.ai `R1-US-008`, Madison AI `R1-US-009`, Intric `R4-SE-002`, HKGAI V1 / HKPilot `R7-HK-003`, Pair (GovTech / Open Government Products) `R7-SG-006`.

### TH12

**53. Immigration casework** · score 30.1 · batch C

- **What:** AI drafts visa petitions and immigration case files, often inside an AI-native firm. **LLM role:** generation + agents.
- **B2B/B2C:** B2B 4.
- **Examples:** [Manifest (Manifest Law)](../catalogue/R1-north-america.csv) `R1-US-003`; [Visalaw.ai](../catalogue/R1-north-america.csv) `R1-US-005`; [Alma](../catalogue/R1-north-america.csv) `R1-US-004`; [CaseBlink](../catalogue/R1-north-america.csv) `R1-US-006`.
- **Spread:** 1 countries in 1 regions (R1): United States. Launch/breakout: earliest 2024 (Manifest (Manifest Law), United States), latest 2025 (CaseBlink, United States); 4/4 rows dated.
- **Best traction:** Visalaw.ai (United States): Seed 1.6M USD, 2025-02; hundreds of immigration law firms ([source](https://www.hypepotamus.com/visalawai-lands-seed-1-6-million-seed-investment/)); durable signals recorded: 1.
- **Durability: mixed (thin).** Members: 0 promising, 2 unproven, 0 hype, 2 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** ~1.5-2M Ukrainians and other migrants: karta pobytu, work permits (powiadomienia, zezwolenia), MOS portal; voivodeship-office queues.
- **All members:** Manifest (Manifest Law) `R1-US-003`, Alma `R1-US-004`, Visalaw.ai `R1-US-005`, CaseBlink `R1-US-006`.

### TH41

**54. Meeting notes and transcription** · score 29.7 · batch C

- **What:** Records meetings or lectures and writes notes, minutes and follow-ups; inbox agents. **LLM role:** voice + generation.
- **B2B/B2C:** B2B 4, B2C 3.
- **Examples:** [daglo (ActionPower)](../catalogue/R7-east-asia.csv) `R7-KR-005`; [Contented](../catalogue/R8-oceania-israel.csv) `R8-NZ-004`; [Atter (Oceanic Digital)](../catalogue/R7-east-asia.csv) `R7-TW-006`; [Fyxer](../catalogue/R0-global.csv) `R0-GB-033`; [Plaud](../catalogue/R1-north-america.csv) `R1-US-054`; [Tiro (ThePlato)](../catalogue/R7-east-asia.csv) `R7-KR-006`.
- **Spread:** 5 countries in 4 regions (R1 R2 R7 R8): New Zealand, South Korea, Taiwan, United Kingdom, United States. Launch/breakout: earliest 2022 (daglo (ActionPower), South Korea), latest 2025 (Atter (Oceanic Digital), Taiwan); 7/7 rows dated.
- **Best traction:** daglo (ActionPower) (South Korea): Series B 6bn KRW, total >20bn KRW, 2026-03-05; revenue ~4x YoY in 2025; 13M hours processed; KR Productivity top-grossing #7 (17,347 ratings), 2026-11-01 ([source](https://www.mt.co.kr/future/2026/03/05/2026030508344192225)); durable signals recorded: 3, 4, 6.
- **Durability: mixed.** Members: 1 promising, 3 unproven, 0 hype, 3 no evidence; hype warnings: none; 5 rows with caveats.
- **Polish angle (first thought):** Absorbed by Teams/Zoom/Gmail; Polish-language niche documents (protokoły zebrań wspólnot, rad gmin) are the only angle.
- **All members:** Fyxer `R0-GB-033`, Granola `R0-GB-034`, Plaud `R1-US-054`, daglo (ActionPower) `R7-KR-005`, Tiro (ThePlato) `R7-KR-006`, Atter (Oceanic Digital) `R7-TW-006`, Contented `R8-NZ-004`.

### TH42

**55. Consumer general assistants** · score 27.7 · batch C

- **What:** General chat, search and agent apps for consumers. **LLM role:** generation + agents.
- **B2B/B2C:** B2C 8.
- **Examples:** [Zapia](../catalogue/R10-latin-america.csv) `R10-UY-001`; [Gamma](../catalogue/R0-global.csv) `R0-US-001`; [Wrtn (뤼튼)](../catalogue/R7-east-asia.csv) `R7-KR-004`; [Manus](../catalogue/R0-global.csv) `R0-SG-011`; [Everbot](../catalogue/R6-cee-peers.csv) `R6-CZ-001`; [Chat & Ask AI (Codeway)](../catalogue/R9-gulf-turkey.csv) `R9-TR-007`.
- **Spread:** 6 countries in 5 regions (R1 R6 R7 R9 R10): Czechia, Singapore, South Korea, Turkey, United States, Uruguay. Launch/breakout: earliest 2022 (Perplexity, United States), latest 2026 (Everbot, Czechia); 8/8 rows dated.
- **Best traction:** Zapia (Uruguay): USD 7M round led by Prosus; >6M users in 6 LatAm countries, 2026-03; App Store UY Productivity top-grossing #47, 2026-11-02 ([source](https://latamlist.com/zapia-raises-a-7m-round/)); durable signals recorded: 2, 6.
- **Durability: hype.** Members: 0 promising, 3 unproven, 3 hype, 2 no evidence; hype warnings: novelty use case, thin wrapper; 3 rows with caveats.
- **Polish angle (first thought):** Global winners dominate; no local angle.
- **All members:** Manus `R0-SG-011`, Gamma `R0-US-001`, Genspark `R0-US-007`, Perplexity `R0-US-008`, Zapia `R10-UY-001`, Everbot `R6-CZ-001`, Wrtn (뤼튼) `R7-KR-004`, Chat & Ask AI (Codeway) `R9-TR-007`.

### TH53

**56. Security operations agents** · score 27.7 · batch C

- **What:** Agents investigate alerts and run penetration tests. **LLM role:** agents.
- **B2B/B2C:** B2B 4.
- **Examples:** [Ethiack](../catalogue/R5-france-southern-europe.csv) `R5-PT-003`; [Tines](../catalogue/R2-uk-ireland.csv) `R2-IE-031`; [7AI](../catalogue/R0-global.csv) `R0-US-047`; [Prophet Security](../catalogue/R0-global.csv) `R0-US-053`.
- **Spread:** 3 countries in 3 regions (R1 R2 R5): Ireland, Portugal, United States. Launch/breakout: earliest 2022 (Ethiack, Portugal), latest 2024 (Tines, Ireland); 4/4 rows dated.
- **Best traction:** Ethiack (Portugal): 4M EUR (Explorer), 2024-12; clients not disclosed ([source](https://srslegal.pt/pt/comunicacao/noticias/srs-legal-assessora-ethiack-em-ronda-de-financiamento-de-4m-liderada-pela-explorer/7144)); durable signals recorded: 1, 10.
- **Durability: mixed (thin).** Members: 0 promising, 2 unproven, 0 hype, 2 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** KSC/NIS2 obligations raise demand; enterprise sales; weak solo fit.
- **All members:** 7AI `R0-US-047`, Prophet Security `R0-US-053`, Tines `R2-IE-031`, Ethiack `R5-PT-003`.

### TH63

**57. Finance and M&A research agents** · score 27.7 · batch C

- **What:** Analysis, pitch books and deal processes for bankers and SMB sell-side. **LLM role:** agents + generation.
- **B2B/B2C:** B2B 4.
- **Examples:** [Comparables.ai](../catalogue/R4-nordics-baltics.csv) `R4-FI-002`; [Model ML](../catalogue/R0-global.csv) `R0-GB-056`; [Rogo](../catalogue/R0-global.csv) `R0-US-051`; [OffDeal](../catalogue/R0-global.csv) `R0-US-077`.
- **Spread:** 3 countries in 3 regions (R1 R2 R4): Finland, United Kingdom, United States. Launch/breakout: earliest 2021 (Comparables.ai, Finland), latest 2024 (OffDeal, United States); 4/4 rows dated.
- **Best traction:** Comparables.ai (Finland): Seed 6M USD (Pragmatech VC, Araya Ventures), 2026-10-06 ([source](https://arcticstartup.com/comparables-ai-raises-6m-seed/)); durable signals recorded: 8.
- **Durability: mixed (thin).** Members: 0 promising, 1 unproven, 0 hype, 3 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Polish SMB succession wave (owners from the 1990s retiring); KRS financials (eKRS) as data.
- **All members:** Model ML `R0-GB-056`, Rogo `R0-US-051`, OffDeal `R0-US-077`, Comparables.ai `R4-FI-002`.

### TH36

**58. Teacher and school paperwork** · score 27.0 · batch C

- **What:** Generates mandatory teacher records, plans and reports. **LLM role:** generation (often template-based).
- **B2B/B2C:** B2C 4.
- **Examples:** [Öğretmen Evrak](../catalogue/R9-gulf-turkey.csv) `R9-TR-005`; [Shawahid (شواهد)](../catalogue/R9-gulf-turkey.csv) `R9-SA-010`; [Al-Mu'allim Al-Dhaki (المعلم الذكي)](../catalogue/R9-gulf-turkey.csv) `R9-SA-011`; [Al-Muwajjih (الموجه)](../catalogue/R9-gulf-turkey.csv) `R9-SA-012`.
- **Spread:** 2 countries in 1 regions (R9): Saudi Arabia, Turkey. Launch/breakout: earliest 2021 (Öğretmen Evrak, Turkey), latest 2025 (Al-Muwajjih (الموجه), Saudi Arabia); 4/4 rows dated.
- **Best traction:** Öğretmen Evrak (Turkey): Turkey App Store top-grossing Education #20; 5,606 ratings, 4.6 stars, 2026-11-01 ([source](https://apps.apple.com/tr/app/%C3%B6%C4%9Fretmen-evrak/id1520664624)); durable signals recorded: 2, 3, 7.
- **Durability: mixed.** Members: 1 promising, 3 unproven, 0 hype, 0 no evidence; hype warnings: none; 4 rows with caveats.
- **Polish angle (first thought):** Polish teachers' paperwork (IPET, WOPFU, dziennik, sprawozdania, awans zawodowy); mostly non-LLM abroad, LLM version looks open.
- **All members:** Shawahid (شواهد) `R9-SA-010`, Al-Mu'allim Al-Dhaki (المعلم الذكي) `R9-SA-011`, Al-Muwajjih (الموجه) `R9-SA-012`, Öğretmen Evrak `R9-TR-005`.

### TH50

**59. Creative media generation** · score 25.3 · batch C

- **What:** Image, video, music and storyboard generation. **LLM role:** generation.
- **B2B/B2C:** B2C 6, B2B2C 2, B2B 1.
- **Examples:** [Leonardo.Ai](../catalogue/R0-global.csv) `R0-AU-013`; [Midjourney](../catalogue/R0-global.csv) `R0-US-014`; [Katalist](../catalogue/R6-cee-peers.csv) `R6-SI-002`; [Magnific (ex-Freepik)](../catalogue/R5-france-southern-europe.csv) `R5-ES-005`; [FERASET](../catalogue/R9-gulf-turkey.csv) `R9-TR-008`; [Runway](../catalogue/R0-global.csv) `R0-US-049`.
- **Spread:** 5 countries in 5 regions (R1 R5 R6 R8 R9): Australia, Slovenia, Spain, Turkey, United States. Launch/breakout: earliest 2022 (Leonardo.Ai, Australia), latest 2026 (Magnific (ex-Freepik), Spain); 9/9 rows dated.
- **Best traction:** Midjourney (United States): on a16z top-50 web list in all 5 editions 2023-2025; bootstrapped ([source](https://a16z.com/100-gen-ai-apps-5/)); durable signals recorded: 3.
- **Durability: hype.** Members: 0 promising, 3 unproven, 4 hype, 2 no evidence; hype warnings: layoffs/pivot, novelty use case, paid ads/influencers, thin wrapper; 1 rows with caveats.
- **Polish angle (first thought):** Global, hype-prone; no Polish angle.
- **All members:** Leonardo.Ai `R0-AU-013`, Suno `R0-US-003`, Higgsfield `R0-US-006`, Midjourney `R0-US-014`, Runway `R0-US-049`, Luma AI `R0-US-103`, Magnific (ex-Freepik) `R5-ES-005`, Katalist `R6-SI-002`, FERASET `R9-TR-008`.

### TH43

**60. Sovereign and national-language LLMs** · score 25.1 · batch C

- **What:** National-language foundation models and state-backed chat apps. **LLM role:** foundation models.
- **B2B/B2C:** B2B 2, B2B2C 2, B2C 2.
- **Examples:** [Mistral AI (Le Chat / Vibe)](../catalogue/R5-france-southern-europe.csv) `R5-FR-010`; [Arabic.AI (Tarjama)](../catalogue/R9-gulf-turkey.csv) `R9-AE-001`; [Tilde](../catalogue/R4-nordics-baltics.csv) `R4-LV-003`; [BgGPT (INSAIT)](../catalogue/R6-cee-peers.csv) `R6-BG-005`; [Fanar (QCRI)](../catalogue/R9-gulf-turkey.csv) `R9-QA-001`; [HUMAIN Chat](../catalogue/R9-gulf-turkey.csv) `R9-SA-003`.
- **Spread:** 6 countries in 4 regions (R4 R5 R6 R9): Bulgaria, France, Latvia, Qatar, Saudi Arabia, United Arab Emirates. Launch/breakout: earliest 2008 (Arabic.AI (Tarjama), United Arab Emirates), latest 2026 (BgGPT (INSAIT), Bulgaria); 6/6 rows dated.
- **Best traction:** Arabic.AI (Tarjama) (United Arab Emirates): Series A USD 15M, 2025-05; strategic investment from HUMAIN (PIF) 2026-09, amount undisclosed (excerpt) ([source](https://enterpriseam.com/uae/2025/05/22/tarjama-secures-usd-15-mn-in-series-a-round-to-expand-arabic-ai/)); durable signals recorded: 1, 8.
- **Durability: mixed.** Members: 0 promising, 4 unproven, 0 hype, 2 no evidence; hype warnings: none; 3 rows with caveats.
- **Polish angle (first thought):** Bielik and PLLuM already exist; raises the baseline for Polish-language claims; not a founder opportunity.
- **All members:** Tilde `R4-LV-003`, Mistral AI (Le Chat / Vibe) `R5-FR-010`, BgGPT (INSAIT) `R6-BG-005`, Arabic.AI (Tarjama) `R9-AE-001`, Fanar (QCRI) `R9-QA-001`, HUMAIN Chat `R9-SA-003`.

### TH47

**61. Coding agents** · score 22.7 · batch C

- **What:** Agents that write, review and modernise code. **LLM role:** agents.
- **B2B/B2C:** B2B 6, B2C 1.
- **Examples:** [Qodo](../catalogue/R8-oceania-israel.csv) `R8-IL-015`; [Kodesage](../catalogue/R6-cee-peers.csv) `R6-HU-003`; [Desktop Commander](../catalogue/R4-nordics-baltics.csv) `R4-LV-005`; [Codeplain](../catalogue/R6-cee-peers.csv) `R6-SI-003`; [Cursor](../catalogue/R0-global.csv) `R0-US-010`; [Cognition (Devin, Windsurf)](../catalogue/R0-global.csv) `R0-US-028`.
- **Spread:** 5 countries in 4 regions (R1 R4 R6 R8): Hungary, Israel, Latvia, Slovenia, United States. Launch/breakout: earliest 2023 (Cursor, United States), latest 2026 (Codeplain, Slovenia); 7/7 rows dated.
- **Best traction:** Qodo (Israel): Series B USD 70M (Qumra), 2026-03-30, total ~USD 120M; Walmart, NVIDIA, Red Hat, monday.com named (excerpt) ([source](https://www.techcrunch.com/2026/03/30/qodo-bets-on-code-verification-as-ai-coding-scales-raises-70m/)); durable signals recorded: 1, 2, 10.
- **Durability: mixed.** Members: 0 promising, 4 unproven, 0 hype, 3 no evidence; hype warnings: none; 3 rows with caveats.
- **Polish angle (first thought):** Global, language-agnostic; no Polish angle.
- **All members:** Cursor `R0-US-010`, Cognition (Devin, Windsurf) `R0-US-028`, Greptile `R0-US-068`, Desktop Commander `R4-LV-005`, Kodesage `R6-HU-003`, Codeplain `R6-SI-003`, Qodo `R8-IL-015`.

### TH25

**62. Voice agent platforms and APIs** · score 22.2 · batch C

- **What:** Speech-to-text, TTS and voice-agent infrastructure for builders. **LLM role:** voice.
- **B2B/B2C:** B2B 4, B2B2C 1.
- **Examples:** [ElevenLabs](../catalogue/R0-global.csv) `R0-GB-002`; [telli](../catalogue/R0-global.csv) `R0-DE-075`; [Deepgram](../catalogue/R0-global.csv) `R0-US-052`; [Synthflow](../catalogue/R0-global.csv) `R0-DE-099`; [Retell AI](../catalogue/R0-global.csv) `R0-US-060`.
- **Spread:** 3 countries in 3 regions (R1 R2 R3): Germany, United Kingdom, United States. Launch/breakout: earliest 2023 (Synthflow, Germany), latest 2024 (Retell AI, United States); 5/5 rows dated.
- **Best traction:** ElevenLabs (United Kingdom): ARR >500M USD, 2026-05 (company statement); Series D 500M USD at 11B, 2026-02 ([source](https://pulse2.com/elevenlabs-500-million-arr-reached-as-ai-voice-platform-adds-blackrock-nvidia-and-jamie-foxx-as-investors/)); durable signals recorded: 3, 4.
- **Durability: mixed (thin).** Members: 1 promising, 0 unproven, 0 hype, 4 no evidence; hype warnings: none; 0 rows with caveats.
- **Polish angle (first thought):** Infrastructure, already handles Polish; use as a component, not a product.
- **All members:** telli `R0-DE-075`, Synthflow `R0-DE-099`, ElevenLabs `R0-GB-002`, Deepgram `R0-US-052`, Retell AI `R0-US-060`.

### TH48

**63. AI infrastructure and APIs** · score 20.3 · batch C

- **What:** Search, parsing, evaluation, guardrail and data APIs for AI builders. **LLM role:** infrastructure.
- **B2B/B2C:** B2B 6, B2B2C 1.
- **Examples:** [Tavily](../catalogue/R8-oceania-israel.csv) `R8-IL-008`; [DiffuseDrive](../catalogue/R6-cee-peers.csv) `R6-HU-004`; [Arena (LMArena)](../catalogue/R0-global.csv) `R0-US-016`; [Jentic](../catalogue/R2-uk-ireland.csv) `R2-IE-033`; [Reducto](../catalogue/R0-global.csv) `R0-US-072`; [Inspeq AI](../catalogue/R2-uk-ireland.csv) `R2-IE-040`.
- **Spread:** 4 countries in 4 regions (R1 R2 R6 R8): Hungary, Ireland, Israel, United States. Launch/breakout: earliest 2023 (Arena (LMArena), United States), latest 2025 (Jentic, Ireland); 7/7 rows dated.
- **Best traction:** Tavily (Israel): USD 25M incl. USD 20M Series A (Insight, Alpha Wave), 2025-08; 1M+ monthly downloads with zero marketing (read via Insight release, excerpt) ([source](https://www.insightpartners.com/ideas/tavily-raises-25-million-to-power-the-internet-of-agents/)); durable signals recorded: 5, 6, 7.
- **Durability: mixed (thin).** Members: 0 promising, 2 unproven, 1 hype, 4 no evidence; hype warnings: layoffs/pivot; 2 rows with caveats.
- **Polish angle (first thought):** Global infrastructure; no Polish angle except Polish-document parsing as a feature.
- **All members:** Arena (LMArena) `R0-US-016`, Reducto `R0-US-072`, You.com `R0-US-104`, Jentic `R2-IE-033`, Inspeq AI `R2-IE-040`, DiffuseDrive `R6-HU-004`, Tavily `R8-IL-008`.

### TH51

**64. Avatar and business video generation** · score 20.3 · batch C

- **What:** Avatar videos, dubbing, subtitles and clip repurposing for business. **LLM role:** generation.
- **B2B/B2C:** B2B 4, B2C 1.
- **Examples:** [Colossyan](../catalogue/R6-cee-peers.csv) `R6-HU-002`; [VEED](../catalogue/R0-global.csv) `R0-GB-012`; [Taja AI](../catalogue/R0-global.csv) `R0-US-025`; [D-ID](../catalogue/R8-oceania-israel.csv) `R8-IL-016`; [Synthesia](../catalogue/R0-global.csv) `R0-GB-035`.
- **Spread:** 4 countries in 4 regions (R1 R2 R6 R8): Hungary, Israel, United Kingdom, United States. Launch/breakout: earliest 2021 (Colossyan, Hungary), latest 2023 (Taja AI, United States); 5/5 rows dated.
- **Best traction:** Colossyan (Hungary): Series A 22M USD (Lakestar), 2024-02; customers HP, BASF, BMW, Novartis, Porsche, Vodafone ([source](https://en.wikipedia.org/wiki/Colossyan)); durable signals recorded: 1, 5.
- **Durability: hype.** Members: 0 promising, 0 unproven, 5 hype, 0 no evidence; hype warnings: novelty use case, tourists/spike; 0 rows with caveats.
- **Polish angle (first thought):** Commoditising; avatar companies are a graveyard (Soul Machines); weak.
- **All members:** VEED `R0-GB-012`, Synthesia `R0-GB-035`, Taja AI `R0-US-025`, Colossyan `R6-HU-002`, D-ID `R8-IL-016`.

### TH44

**65. Enterprise LLM workspace and gateway** · score 15.2 · batch C

- **What:** Secure, EU-hosted chat, search and agents across models for companies. **LLM role:** search + agents.
- **B2B/B2C:** B2B 3.
- **Examples:** [Langdock](../catalogue/R3-dach-benelux.csv) `R3-DE-014`; [nexos.ai](../catalogue/R4-nordics-baltics.csv) `R4-LT-002`; [Glean](../catalogue/R0-global.csv) `R0-US-048`.
- **Spread:** 3 countries in 3 regions (R1 R3 R4): Germany, Lithuania, United States. Launch/breakout: earliest 2023 (Glean, United States), latest 2025 (nexos.ai, Lithuania); 3/3 rows dated.
- **Best traction:** Langdock (Germany): ARR 50M+ EUR from signed contracts, 13,000+ companies, 65 staff, 2026-09 (company) ([source](https://www.cloudmagazin.com/2026/09/30/ki-anbieter-langdock-verlaesst-delaware-fuer-deutschland/)); durable signals recorded: 4.
- **Durability: mixed.** Members: 0 promising, 2 unproven, 0 hype, 1 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** RODO/data-residency selling point; crowded (Langdock, nexos.ai already sell in PL).
- **All members:** Glean `R0-US-048`, Langdock `R3-DE-014`, nexos.ai `R4-LT-002`.

### TH49

**66. Prompt-to-app builders** · score 15.2 · batch C

- **What:** Build full apps and sites from chat. **LLM role:** agents.
- **B2B/B2C:** B2C 3.
- **Examples:** [Base44 (Wix)](../catalogue/R8-oceania-israel.csv) `R8-IL-002`; [Lovable](../catalogue/R0-global.csv) `R0-SE-005`; [Replit](../catalogue/R0-global.csv) `R0-US-015`.
- **Spread:** 3 countries in 3 regions (R1 R4 R8): Israel, Sweden, United States. Launch/breakout: earliest 2024 (Lovable, Sweden), latest 2025 (Base44 (Wix), Israel); 3/3 rows dated.
- **Best traction:** Base44 (Wix) (Israel): ~USD 59M ARR end-2025 and ~USD 100M ARR by 2026-03 per Wix; 2M users 2025-11 (read via Sacra, excerpt); ~USD 200M ARR 2026-08 (Sacra estimate) ([source](https://sacra.com/c/base44/)); durable signals recorded: 6, 7.
- **Durability: mixed (thin).** Members: 0 promising, 1 unproven, 0 hype, 2 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Global; a Polish angle only as prebuilt local integrations (Przelewy24, InPost, KSeF) for SMB apps.
- **All members:** Lovable `R0-SE-005`, Replit `R0-US-015`, Base44 (Wix) `R8-IL-002`.

### TH65

**67. AI companions** · score 10.1 · batch C

- **What:** Role-play, voice and faith companion chat. **LLM role:** generation.
- **B2B/B2C:** B2C 3.
- **Examples:** [Bible Chat](../catalogue/R6-cee-peers.csv) `R6-RO-005`; [Character.ai](../catalogue/R0-global.csv) `R0-US-009`; [Sesame](../catalogue/R0-global.csv) `R0-US-050`.
- **Spread:** 2 countries in 2 regions (R1 R6): Romania, United States. Launch/breakout: earliest 2019 (Bible Chat, Romania), latest 2025 (Sesame, United States); 3/3 rows dated.
- **Best traction:** Bible Chat (Romania): revenue 72.2M RON (~EUR 14.5M) in 2025, ~3x 2024, net loss 30.1M RON; 10M+ users in first year; Series A 14M USD (True Ventures), 2025-02 ([source](https://startupcafe.ro/startupul-romanesc-din-spatele-bible-chat-si-a-triplat-afacerile-la-145-milioane-de-euro-cum-a-crescut-pe-o-piata-putin-explorata-de-startupurile-europene-102861)); durable signals recorded: 2, 7.
- **Durability: hype.** Members: 0 promising, 0 unproven, 3 hype, 0 no evidence; hype warnings: novelty use case, paid ads/influencers; 0 rows with caveats.
- **Polish angle (first thought):** Global consumer apps; hype; Catholic devotional angle exists but weak.
- **All members:** Character.ai `R0-US-009`, Sesame `R0-US-050`, Bible Chat `R6-RO-005`.

### TH66

**68. Resume and career tools** · score 10.1 · batch C

- **What:** AI resume writing and job-application tailoring. **LLM role:** generation.
- **B2B/B2C:** B2C 2.
- **Examples:** [Enhancv](../catalogue/R6-cee-peers.csv) `R6-BG-003`; [Rezi](../catalogue/R0-global.csv) `R0-US-017`.
- **Spread:** 2 countries in 2 regions (R1 R6): Bulgaria, United States. Launch/breakout: earliest 2015 (Rezi, United States), latest 2023 (Enhancv, Bulgaria); 2/2 rows dated.
- **Best traction:** Enhancv (Bulgaria): ~250,000 users (co-founder, BNR interview, date unclear); revenue <5M USD (ZoomInfo estimate) ([source](https://pulse2.com/enhancv-profile-volen-vulkov-interview/)); durable signals recorded: 7.
- **Durability: mixed.** Members: 0 promising, 1 unproven, 1 hype, 0 no evidence; hype warnings: one-off/lifetime revenue; 1 rows with caveats.
- **Polish angle (first thought):** Commodity; absorbed by ChatGPT; Pracuj.pl owns the channel.
- **All members:** Rezi `R0-US-017`, Enhancv `R6-BG-003`.

### TH69

**69. Translation and localisation** · score 10.1 · batch C

- **What:** LLM translation orchestration and real-time voice translation. **LLM role:** generation + voice.
- **B2B/B2C:** B2B 1, B2C 1.
- **Examples:** [Owll / Owll Translator (Vocalbeats.AI)](../catalogue/R7-east-asia.csv) `R7-SG-004`; [Lokalise](../catalogue/R4-nordics-baltics.csv) `R4-LV-002`.
- **Spread:** 2 countries in 2 regions (R4 R7): Latvia, Singapore. Launch/breakout: earliest 2024 (Lokalise, Latvia), latest 2025 (Owll / Owll Translator (Vocalbeats.AI), Singapore); 2/2 rows dated.
- **Best traction:** Owll / Owll Translator (Vocalbeats.AI) (Singapore): #1 top-grossing Business in 22 markets (single-day peak), top 10 in 125 markets, 2026-08 (press release, excerpt); in JP/TW/KR/SG/HK Business top-grossing 2026-11-01 ([source](https://macaubusiness.com/vocalbeats-ai-applications-gain-strong-momentum-in-2026-reaching-top-grossing-charts-worldwide/)); durable signals recorded: 6, 7.
- **Durability: mixed.** Members: 0 promising, 2 unproven, 0 hype, 0 no evidence; hype warnings: none; 1 rows with caveats.
- **Polish angle (first thought):** Commoditised by LLMs (Unbabel insolvency); Polish-Ukrainian real-time translation for public services is the only angle.
- **All members:** Lokalise `R4-LV-002`, Owll / Owll Translator (Vocalbeats.AI) `R7-SG-004`.

## Coverage

- Catalogue rows tagged: 531 in 11 files; themes: 69; batches A/B/C: 23/23/23.
- Inputs also read: regional READMEs `research/regions/*/README.md` and `research/global/README.md` (their patterns informed the clustering and the Polish angles). No new web sources were added in T15; every traction link is copied from the catalogue's `traction_source` column.
- Smallest themes (2 rows: TH64, TH66, TH69) were kept separate rather than forced into a broader theme because their buyer and workflow differ; they rank low and sit in batch C.
