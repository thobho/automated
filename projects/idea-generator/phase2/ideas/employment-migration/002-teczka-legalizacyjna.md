# 002 — "Teczka legalizacyjna": MOS case-file agent for legalisation agencies and staffing firms

**One-liner:** From a passport scan, the employment contract and the employer's KRS/CEIDG data, the agent fills the MOS 2.0 application fields, builds the attachment checklist for the specific urząd wojewódzki, drafts the employer annex and ponaglenie letters, and tracks every worker's legal-stay deadline. Sold to legalisation agencies, agencje zatrudnienia and HR teams of firms with many foreign staff.
**Field:** employment-migration | **Type:** SaaS (web) | **B2B** · shortlist id L036 (merges L027 deadline tracker, L037 voivodeship practice tracker, L038, L039 ponaglenie/skarga module, L041 CUKR bulk package)

**Western analogues** (all US, all built on USCIS petitions):
- **Alma** (Palo Alto), "AI-native immigration law firm" for skilled-worker visas; US$17M Series A led by Bling Capital ([Dealroom news](https://dealroom.co/news/151371-ai-native-law-firm-alma-raises-17m-to-automate-immigration-cases/), date of round unverified).
- **CaseBlink** (Miami), AI case preparation for immigration attorneys; US$2M pre-seed in March 2025 led by Tower Research Ventures, with immigration law firm Fakhoury Global Immigration as investor ([Tower Research](https://tower-research.com/caseblink-raises-2m-in-pre-seed-funding-to-transform-immigration-case-preparation-with-ai/)).
- **Visalaw.ai** (Memphis), spun out of law firm Siskind Susser, drafting tools for immigration lawyers; US$1.6M seed led by Valor Ventures ([VentureNashville](https://www.venturenashville.com/article/2143/memphis-based-visalaw-ai-raises-1-6mm-seed-to-fund-growth-innovation)).
- **Manifest** (US), named in the TH12 check; traction not re-verified (unverified).
Traction is early: funding rounds, no revenue, retention or customer counts found.

**Spread:** TH12 evidence comes from the US only (R1); the theme carries the L2 ≤ 2 rule in T20 for that reason. No CEE analogue in the R6 catalogue. Czechia and Slovakia have the same Ukrainian-population driver but no product found.

**Does the Western leader already work in Poland?** No. All four are built on US forms (I-129, O-1, EB-1) and US evidence-heavy petitions; Alma is a US law firm, not software. Not tried hands-on: CaseBlink and Visalaw.ai are demo-led for US attorneys. The Polish problem is different: short, form-heavy, high-volume cases where the work is getting the attachments and the deadlines right for one of 16 offices. Big advisers (EY, Fragomen) serve Polish employers with human teams (TH12 check).

**Polish adaptation, i.e. the edge:**
- **MOS 2.0 as the only channel** for residence applications since 2026-04-27, with login.gov.pl and e-signature, and the employer co-signing its annex ([MOS: jak zacząć](https://mos.cudzoziemcy.gov.pl/jak-zaczac/)). No API: the product prepares data and documents; the agency pastes or uses a browser helper.
- **CUKR**: residence card for PESEL UKR holders, applications from 2026-05-04 until 2027-03-04, only via MOS, 3-year card ([UdSC: CUKR procedura](https://www.gov.pl/web/udsc/CUKR-procedura); [Zielona Linia](https://zielonalinia.gov.pl/karta-pobytu-cukr-mozna-juz-skladac-wnioski/)).
- **2025 act on employing foreigners** (in force 2025-06-01): fines 3,000–50,000 PLN, at least 3,000 PLN per foreigner, and a duty to check and keep each worker's residence document ([poradnikprzedsiebiorcy.pl](https://poradnikprzedsiebiorcy.pl/-kary-za-nielegalne-zatrudnienie-cudzoziemca); [infor.pl](https://www.infor.pl/prawo/nowosci-prawne/6866783,do-50-tys-zl-grzywny-za-nielegalne-zatrudnienie-kontrole-bez-zapowiedzi-nowa-ustawa-o-pracy-cudzoziemcow-w-polsce.html)).
- 16 voivodeship offices with different attachment demands and backlogs; art. 37 KPA ponaglenie before a skarga na bezczynność ([WSA Wrocław II SAB/Wr 287/26](https://dlajurysty.pl/orzeczenia/pokaz/489740/II-SAB-Wr-287-26), via T20 notes); praca.gov.pl work permits and oświadczenia ([M08](../../research/poland/local-moats.md)); employer data from KRS/CEIDG; clients speaking UA/RU/EN/Hindi/Nepali.
A US entrant would need all of this rebuilt; nothing carries over except the idea of drafting a case file.

**Target customer in Poland:**
- **Agencje zatrudnienia:** 8,550 entities in the KRAZ register at end-2024 (−2.2% y/y); in kujawsko-pomorskie foreigners were 61.7% of people placed by agencies ([WUP Toruń analysis 2024](https://wuptorun.praca.gov.pl/documents/d/wuptorun/analiza-agencje-zatrudnienia-2024)). KRAZ is downloadable, i.e. a full outbound list.
- Plus non-lawyer legalisation agencies and kancelarie imigracyjne (count unverified) and HR teams of manufacturers, logistics and food firms with dozens of foreign staff.
- Buyer: owner or legalisation specialist; staffing firms hire dedicated "specjalista ds. legalizacji" roles (pracuj.pl postings in Gorzów and Poznań, TH12 check).
- CEE: Czech and Slovak law packs would be new builds on the same engine (medium effort).

**Demand driver:** DD6: 1.56 million Ukrainians with valid permits and 1.29 million foreigners insured in ZUS; the end of the special act moves 900k+ people to CUKR and standard permits (TH59, [demography.md](../../research/poland/demography.md)). DD7 labour shortages keep employers recruiting from Asia. Regulatory: MOS-only filing (2026-04), CUKR window (to 2027-03), higher employer fines (2025-06).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| HRappka | HR/payroll for staffing agencies with a legalisation module (permits, deadlines) | not listed, 14-day trial | tracking only, no drafting or MOS data prep ([HRappka](https://hrappka.pl/?p=63478)) |
| Legalisation agencies / law firms | human case preparation | average 4,457 PLN per person (aggregator, 2026) | this is the customer, not the competitor ([cenauslug.pl](https://cenauslug.pl/firma-i-biuro/legalizacja-pobytu-i-zatrudnienia-cudzoziemcow)) |
| EY, Fragomen | advisory for large employers | hourly | human, large clients only |
| Excel + ChatGPT | what small agencies use today (estimate, not sourced) | ~0–100 PLN/month | no office-specific checklists, no deadline engine, RODO risk |
| Right to Protection "Legal Adviser 2.0" | free NGO bot for Ukrainians | free | consumer, not case files |

**Evidence of Polish demand:** autocomplete (2026-11-05, TH12): "legalizacja pobytu" → incl. "cennik", "dokumenty", "praca"; "zezwolenie na pracę typ a" → "jakie dokumenty", four voivodeship offices, "koszt"; "mos 2.0" → "instrukcja", "cukr", "karta pobytu". "program do legalizacji cudzoziemców" → none, i.e. nobody searches for software. Job posts for legalisation specialists in staffing firms show a salaried job step. The RPO keeps flagging slow proceedings ([RPO BIP](https://bip.brpo.gov.pl/pl/content/rpo-cudzoziemcy-legalizacja-pobytu-przewleklosc-mswia)), which makes ponaglenia a recurring task.

**MVP scope (≤6 weeks):**
1. Case intake: passport photo page (vision), contract PDF, employer NIP → KRS/CEIDG lookup; JSON case schema.
2. Two case types first: CUKR (simplest, highest volume until 2027-03) and zezwolenie na pobyt czasowy i pracę.
3. Output: MOS field-by-field answer sheet, attachment checklist per voivodeship (start with 3 offices: mazowiecki, wielkopolski, dolnośląski), employer annex draft, ponaglenie generator after the statutory deadline.
4. Deadline board per worker (residence document expiry, notification duties) with email alerts.
5. Tests: fixture cases with expected field sheets (golden files); rules versioned with source links.

**Monetization:** per agency 399 PLN/month up to 30 active cases + 15 PLN per extra case; CUKR bulk package for employers 29 PLN per worker. Who pays: the agency (it charges the foreigner or employer thousands per case) or the employer's HR budget.
**Unit economics:** a case ≈ passport image + 5-page contract + rules context ≈ 20k input and 5k output tokens across steps. Gemini 2.5 Flash at US$0.30 / US$2.50 per M ([OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) → ~US$0.02 per case; even ×10 for a frontier model on hard cases, <1 PLN. Hosting ~50 PLN/month total, payment fees ~2% (estimate). Gross margin >90%. The real cost is **rules maintenance** (founder time per office per month), not tokens. 10k PLN MRR = ~25 agencies.

**Distribution, first 10 customers:** download KRAZ, filter to agencies whose sites mention "cudzoziemcy/legalizacja" in 2–3 voivodeships, phone and email 100 of them with a free CUKR answer sheet for one real worker; join Facebook groups of agency owners and HR specialists for foreigners; partner with one payroll office (biuro kadrowo-płacowe) that serves staffing firms.

**Regulation:** AI Act: Annex III point 7 (migration) covers systems used **by or on behalf of public authorities**; a tool for private agencies is not in it; point 4 (employment) covers recruitment and decisions on workers, which this tool does not make ([AI Act Annex III](https://artificialintelligenceact.eu/annex/3/)). Keep it a document and deadline tool, no "chance of approval" scoring. RODO: passport data and possibly art. 9 data (health insurance, family); EU hosting, DPA with each agency, retention limits. Legal services: representation before the voivode appears open to any natural person (KPA art. 33, not re-verified); avoid "legal advice" wording.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | CUKR wave (900k+ people, deadline 2027-03-04) creates urgent bulk demand from employers | H | H | employers ask for "all our PESEL UKR staff at once" in first outreach |
| O2 | Office practice tracker (L037) becomes a network asset: each agency reports what an office demanded | M | H | agencies contribute updates without being asked |
| O3 | Fine exposure (≥3,000 PLN per foreigner) sells the deadline board to employers' HR, beyond agencies | M | M | HR managers mention a PIP/SG control as purchase reason |
| O4 | Payroll and HR software (HRappka-type) wants to resell or integrate | L | H | a vendor asks for API access |
| O5 | Same engine powers the B2C MOS assistant (idea L040) | M | M | shared rules cover ≥70% of B2C cases |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | MOS 2.0 form and office practice change often; rules go stale and a wrong checklist costs a client's case | H | H | ≥2 MOS changes per month in the first quarter |
| R2 | Agencies see their know-how as their value and refuse a tool that commoditises it | M | H | "we already know what each office wants" in calls |
| R3 | CUKR volume is a one-off wave; after 2027 volume drops to standard permits | H | M | case counts per agency fall in 2027 |
| R4 | The state adds guided filling in MOS that removes the field-sheet value | M | M | UdSC announces MOS wizard features |
| R5 | RODO incident with passport data | L | H | any customer asks for an audit you can't answer |
| R6 | HRappka or another HR vendor adds an LLM drafting feature | M | M | vendor release notes mention AI legalisation |

**Success signals:**
- Western analogue durable signals: replaces paralegal and attorney drafting hours (budget line: fee-earner time); investors include immigration law firms (CaseBlink: Fakhoury Global Immigration), a sign of customer pull; Alma replaces the law firm itself. No retention, NRR or revenue found.
- Hype warnings: early stage only (pre-seed/seed) and one country; no public customer counts. L2 kept at 2.
- Polish adaptation can reproduce: replaced spend = a legalisation specialist's salary hours (job posts exist) and fine risk; first channel = KRAZ outbound list + agency Facebook groups; retention driver = each worker's deadline board lives in the tool for years (residence cards renew), plus per-office practice knowledge.

**Graveyard:** no failed AI immigration-casework product found in two searches (funding news only). Adjacent lesson: US immigration tools sell to attorneys because filings are long; Polish volume is in short filings, so value must come from checklists and deadlines, not prose drafting. Unverified whether any Polish HR vendor's legalisation module was discontinued.

**Scores (1–5):** L1 4 · L2 2 · L3 4 · L4 5 · L5 4 · L6 3 · L7 3 · L8 3 · L9 3 | **Weighted:** 3.6 / 5 | **Chance band:** 5–15%. The moat, the dated driver (CUKR to 2027-03) and a complete outbound list (KRAZ) are real, and agencies already charge thousands per case. Against that, Western traction is thin, agencies may not want to commoditise their know-how, and keeping 16 offices' rules current is a heavy load for a 40 h/month founder.
Quick scores confirmed; L5 4 now rests on the KRAZ count, the CUKR driver and job posts for the job step.

**Cheapest validation test (≤1 week, ≤200 PLN):** pull 100 agencies from KRAZ in mazowieckie and wielkopolskie that mention foreigners; call/email offering "CUKR answer sheet + checklist for 5 of your workers for free in 24 h, then 399 PLN/month". Produce the sheets by hand + ChatGPT (concierge). Cost: phone time, maybe 100 PLN for a domain and email tool. Pass: ≥5 agencies send real cases and ≥2 say yes to the price.

**Kill criteria:** <3 of 100 agencies reply; or agencies say the field sheet saves <30 minutes per case; or MOS changes break the checklist twice during the test week.

**Confidence:** medium (rules, fines and target-group size sourced; willingness to pay and agency attitude untested).

**Sources** (accessed 2026-11-05):
1. https://dealroom.co/news/151371-ai-native-law-firm-alma-raises-17m-to-automate-immigration-cases/
2. https://tower-research.com/caseblink-raises-2m-in-pre-seed-funding-to-transform-immigration-case-preparation-with-ai/
3. https://www.venturenashville.com/article/2143/memphis-based-visalaw-ai-raises-1-6mm-seed-to-fund-growth-innovation
4. https://mos.cudzoziemcy.gov.pl/jak-zaczac/ (TH12)
5. https://www.gov.pl/web/udsc/CUKR-procedura
6. https://zielonalinia.gov.pl/karta-pobytu-cukr-mozna-juz-skladac-wnioski/
7. https://poradnikprzedsiebiorcy.pl/-kary-za-nielegalne-zatrudnienie-cudzoziemca
8. https://www.infor.pl/prawo/nowosci-prawne/6866783,do-50-tys-zl-grzywny-za-nielegalne-zatrudnienie-kontrole-bez-zapowiedzi-nowa-ustawa-o-pracy-cudzoziemcow-w-polsce.html
9. https://wuptorun.praca.gov.pl/documents/d/wuptorun/analiza-agencje-zatrudnienia-2024
10. https://hrappka.pl/?p=63478 (TH12)
11. https://cenauslug.pl/firma-i-biuro/legalizacja-pobytu-i-zatrudnienia-cudzoziemcow (TH59)
12. https://bip.brpo.gov.pl/pl/content/rpo-cudzoziemcy-legalizacja-pobytu-przewleklosc-mswia (TH12)
13. https://dlajurysty.pl/orzeczenia/pokaz/489740/II-SAB-Wr-287-26 (T20 notes)
14. https://artificialintelligenceact.eu/annex/3/
15. https://openrouter.ai/google/gemini-2.5-flash
16. Internal: [TH12 check](../../poland-check/C/TH12-immigration-casework.md), [TH59 check](../../poland-check/B/TH59-citizen-sme-public-service-navigators.md), [local-moats](../../research/poland/local-moats.md), [demography DD6/DD7](../../research/poland/demography.md)

Coverage: 4 web searches run for this write-up (US analogues' funding, CUKR application statistics, employer fines, KRAZ agency count). Not found: any count of CUKR applications filed so far, any failed AI immigration product, prices for HRappka.
