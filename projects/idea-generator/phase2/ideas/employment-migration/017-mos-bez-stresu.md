# 017 — "MOS bez stresu": self-service MOS 2.0 assistant for foreigners

**One-liner:** A Ukrainian/Russian/English web assistant that interviews a foreigner about their situation, picks the right procedure (CUKR, pobyt czasowy for work, pobyt stały, rezydent długoterminowy UE), lists the documents for their urząd wojewódzki, pre-checks photos and scans, drafts any written justification in Polish, and walks the person screen by screen through MOS 2.0, including the part the employer must sign. Add-on: photo of an official letter (wezwanie, decision) → explanation in the user's language and a draft reply (merged L045).
**Field:** employment-migration | **Type:** SaaS (web, mobile-first) | **B2C**, with a B2B2C employer package · shortlist id L040 (merges L045). Shares its rules engine with [002 Teczka legalizacyjna](002-teczka-legalizacyjna.md) (B2B case files for agencies).

**Western analogues:**
- **Boundless** (US, Seattle): guided self-service for family green cards and naturalisation at flat fees, pre-LLM (2017 launch); **US$25M Series B in 2021, US$45.3M total** ([Built In](https://builtin.com/articles/boundless-immigration-raises-25m-series-b-hiring), accessed 2026-11-06). Earlier reports listed flat fees of US$750 (marriage green card) and US$395 (naturalisation) (search excerpt, not re-checked). The "served 100k+ immigrants" figure is from a secondary profile, unverified.
- **Visabot** (US): Facebook Messenger bot for US visa forms since 2016, later a US$150 green-card service, ~50k clients reported (search excerpts; [Smithsonian](https://www.smithsonianmag.com/innovation/could-chatbot-prevent-some-deportations-180962435/), accessed 2026-11-06). Current status unverified.
- **State and NGO navigators** in the TH59 theme: Kol Zchut AI chat (IL, ~31.5M Hebrew visits to the rights site in 2024), mAigov (GR, 2M+ queries by 2025, excerpt), Bürokratt (EE, 18 public bodies) (R4/R5/R8 catalogue rows). These are free public services, not products with revenue.
- **Elterngeld Buddy** (DE): guided form-filling for one German benefit, 29.90 EUR per application, top-grossing #21 in DE App Store Finance on 2026-11-01 (R3 catalogue row). Closest pay-per-application B2C pattern, but no LLM claimed.

**Spread:** TH59 appears in IL, EE, GR, AE, BH, US and DE (R1, R3, R4, R5, R8, R9) since 2023, but almost all of it is state-run. Paid B2C immigration self-service is US-only (Boundless, Visabot) and pre-dates LLMs.

**Does the Western leader already work in Poland?** No. Boundless and Visabot cover only US forms (USCIS). Kol Zchut, Bürokratt and mAigov are tied to their own states. Not tried hands-on: none has a Polish flow to try. The real "leaders" in Poland are free: the mObywatel PLLuM assistant (live since 2025-12-31, covers mObywatel services, not MOS) ([iMagazine](https://imagazine.pl/2026/01/02/mobywatel-wchodzi-w-2026-rok-z-polskim-ai/), accessed 2026-11-06), the UdSC/voivodeship pages in UA/EN, and ChatGPT, which answers MOS questions in Ukrainian but does not know each office's attachment demands or the current MOS screens (not tested in this pass; unverified).

**Polish adaptation, i.e. the edge:**
- **MOS 2.0 as the only channel** for temporary, permanent and long-term-resident applications since 2026-04-27; a new account is required for everyone, login via login.gov.pl ([MOS: jak zacząć](https://mos.cudzoziemcy.gov.pl/jak-zaczac/); [Dolnośląski UW](https://www.gov.pl/web/dolnoslaski-uw/cudzoziemcy-info), both accessed 2026-11-06).
- **Signature:** the application must be signed with profil zaufany, a qualified signature or podpis osobisty ([UW Poznań: podpis elektroniczny](https://migrant.poznan.uw.gov.pl/pl/node/5099), accessed 2026-11-06); employers' body Lewiatan and the RPO flagged that many third-country nationals lack these, and getting them depends on PESEL (search excerpts of their position papers, e.g. [Lewiatan 2025-10-02](https://lewiatan.org/wp-content/uploads/2025/10/2025.10.02-stanowisko-Konfederacji-Lewiatan-do-projektu-ustawy-o-zmianie-ustawy-o-cudzoziemcach-oraz-niektorych-innych-ustaw-MOS-Druk-nr-1630.pdf), not read in full).
- **CUKR** for PESEL UKR holders: applications only via MOS from 2026-05-04 to 2027-03-04; 340 PLN stamp duty + 100 PLN card fee, each paid to a separate account ([UdSC: CUKR procedura](https://www.gov.pl/web/udsc/CUKR-procedura); [Zielona Linia](https://zielonalinia.gov.pl/karta-pobytu-cukr-mozna-juz-skladac-wnioski/), accessed 2026-11-06; fees from search excerpts of voivodeship pages).
- 16 voivodeship offices with different attachment demands and backlogs; Polish-only official letters (wezwanie do uzupełnienia braków with a 7- or 14-day deadline, decisions) (deadline types per [local-moats](../../research/poland/local-moats.md) M52, not re-checked here).
A foreign entrant would have to learn the ustawa o cudzoziemcach, the specustawa ukraińska exit, MOS 2.0 screens and each office's practice; translation alone gets nowhere.

**Target customer in Poland:**
- Foreigners filing themselves: about **614,000 residence applications in 2023** (280,000 in 2020); **754,310 temporary and 125,121 permanent permits** held in mid-2025 ([OKO.press 2025-07-24](https://oko.press/chaos-cyfryzacja-wnioskow-o-legalizacje-pobytu-cudzoziemcy), accessed 2026-11-06).
- Plus the CUKR wave: 900k+ temporary-protection beneficiaries, ~800k CUKR applications expected ([ceo.com.pl](https://ceo.com.pl/en/?p=5085), via TH59 check, accessed 2026-11-04). No figure for applications filed so far was found (searched 2026-11-06).
- Payer: the foreigner, or the employer buying a package for its staff. CEE: Czechia has a similar Ukrainian population but different law; a new build per country.

**Demand driver:** DD6 migration (1.56M Ukrainians with valid permits, 1.29M foreigners in ZUS, [demography.md](../../research/poland/demography.md)); regulatory: MOS-only filing from 2026-04-27 and the CUKR window ending 2027-03-04; employer fines of 3,000–50,000 PLN for illegal employment (002 sources).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Legalisation agencies, kancelarie | human preparation and filing | average **4,457 PLN** per person in 2026, excl. fees ([cenauslug.pl](https://cenauslug.pl/firma-i-biuro/legalizacja-pobytu-i-zatrudnienia-cudzoziemcow), accessed 2026-11-04) | expensive, slow, quality varies |
| Right to Protection "Legal Adviser 2.0" | free Telegram bot in Ukrainian, escalates to humans | free | NGO capacity, no document pre-check ([r2p.org.ua](https://r2p.org.ua/page/legal-adviser-20-for-ukrainians-in-poland-chatbot-is-launched), accessed 2026-11-04) |
| UdSC, voivodeship pages, Zielona Linia | static guides in PL/UA/EN, a survey of entry options | free | not personalised, no scan check |
| mObywatel assistant (PLLuM) | state chatbot | free | covers mObywatel, not MOS step by step |
| ChatGPT / Gemini | general answers in Ukrainian | free / ~20 USD | no office-specific checklist, may be out of date |
| Waypass (hackathon project, AI Tinkerers Poland) | AI case handling for lawyers | n/a | B2B, status unknown ([AI Tinkerers](https://poland.aitinkerers.org/hackathons/h_qfzjGGzYIdw/teams/ht_BDdXbyZ565I), accessed 2026-11-06) |

**Evidence of Polish demand:** autocomplete "mos cudzoziemcy" → "logowanie", "rejestracja", "infolinia", "nie działa"; "karta cukr" → "warunki", "dokumenty", "opłaty" (TH59 check, 2026-11-04). OKO.press quotes an intermediary: "Tylko pośrednik jest z tym na bieżąco" (only an intermediary keeps up), and describes a ~2,500-person online community tracking appointment slots ([OKO.press](https://oko.press/chaos-cyfryzacja-wnioskow-o-legalizacje-pobytu-cudzoziemcy)). Staffing firms hire legalisation specialists (pracuj.pl ads, 002). The article pre-dates MOS 2.0 (2025-07); post-switch complaints were not found in this pass.

**MVP scope (≤6 weeks):**
1. Interview flow in UA/RU/EN → procedure decision (CUKR, pobyt czasowy praca, stały, rezydent UE) with a rules table, not free LLM judgement; out-of-scope cases (asylum, family reunification abroad, still paper) are sent to a human list.
2. Checklist per procedure × voivodeship (start with Mazowieckie, Wielkopolskie, Dolnośląskie); fee amounts and account numbers.
3. Photo/scan pre-check with a vision model: legibility, expiry dates, name match with the passport, missing pages.
4. MOS 2.0 walkthrough: screenshots and field-by-field values in Polish, generated from the interview; signature path (profil zaufany vs. podpis osobisty) explained.
5. Letter explainer (L045): photo of a wezwanie → deadline, what is missing, draft reply.
6. Employer package: a code an employer buys for N workers, with a dashboard of who has filed.
7. Tests: golden interview transcripts → expected procedure and checklist; fixture scans with known defects.

**Monetization:** 149 PLN per application (one-off, BLIK/Przelewy24), letter explainer 29 PLN each; employer package 99 PLN per worker. **Unit economics:** interview ~20k tokens, 10 scanned pages ~15k tokens, outputs ~10k tokens → ~50k input / 10k output on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.04 per application; with retries and support chat ≈ US$0.20 (~1 PLN). Payment fees ~2% (estimate). Gross margin >90% before support time; support time is the real cost. **Customer count:** 10k PLN MRR ≈ 67 applications a month at 149 PLN, or ~100 workers a month through employers; the market is hundreds of thousands of applications a year, far above 20×.

**Distribution, first 10 customers:** Ukrainian-language Facebook and Telegram groups for Ukrainians in Poland (post a free CUKR checklist generator, upsell the full check); 2–3 staffing agencies that already use 002 buying the employer package; Ukrainian-language SEO on "MOS як подати заяву".

**Regulation:** AI Act: Annex III point 7 (migration, asylum, border control) lists systems used **by or on behalf of public authorities** ([Annex III](https://artificialintelligenceact.eu/annex/3/), accessed 2026-11-06); a private helper for the applicant is not in that list, so limited-risk transparency duties only (own reading, not checked with counsel). Legal services: preparing documents is not reserved to advocates in Poland, but representation needs a pełnomocnictwo; the product prepares, the foreigner signs. RODO: passport and residence data, special care with nationality data; EU hosting.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | The CUKR window (to 2027-03-04) concentrates hundreds of thousands of first-time MOS users into a few months | H | M | ≥5% of free-checklist users pay in the first month |
| O2 | Employers facing 3,000–50,000 PLN fines buy packages for whole crews, turning B2C into a few B2B deals | M | H | one staffing agency buys ≥50 worker codes |
| O3 | Ukrainian Telegram and Facebook communities spread a tool that works, at near-zero cost | H | M | a post in one large group brings ≥300 sign-ups |
| O4 | Temporary permits renew every 1–3 years and letters keep coming, so a user returns | M | M | ≥15% of users buy the letter explainer within 3 months |
| O5 | The rules engine is shared with 002, so B2B and B2C maintenance costs are paid once | H | L | the same rules table passes both products' tests |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Free help (NGO bot, voivodeship pages, ChatGPT in Ukrainian) keeps B2C willingness to pay near zero | H | H | <2% conversion from free checklist to paid check |
| R2 | A wrong procedure or missed attachment leads to a refusal or illegal stay, and word spreads fast in small communities | M | H | first complaint posts in a Ukrainian group |
| R3 | The CUKR wave ends 2027-03-04, leaving a smaller steady market before the 12-month mark | H | M | monthly applications fall >50% after March 2027 |
| R4 | Many users lack profil zaufany or podpis osobisty, so they cannot file at all and drop out | M | M | >30% of users stop at the signature step |
| R5 | Users trust a human agent they know (often paid in cash) more than a website | M | M | users ask "who will go to the urząd with me?" |
| R6 | UdSC improves MOS help or adds a state assistant in Ukrainian | L | M | UdSC announcement of a MOS chatbot |

O sum 6+6+6+4+3 = 25; R sum 9+6+6+4+4+2 = 31. R − O = 6 → **down one band** (rule §4.3). R1 is H×H; the employer package in the MVP is a partial mitigation, so the second clause of §4.3 is not applied on top.

**Success signals:**
- Western analogue durable signals: Boundless replaces lawyer fees (signal 1, flat fees vs. attorneys), a painful one-off-but-high-stakes problem (signal 2), value-based pricing per application (signal 7), and raised three rounds over 2019–2021 ([Built In](https://builtin.com/articles/boundless-immigration-raises-25m-series-b-hiring)). Elterngeld Buddy shows pay-per-application B2C revenue in a top-grossing chart (R3 catalogue). No retention or NRR figures (retention is structurally low: one application per person per 1–3 years). Durability score ~3 → **unproven**.
- Hype warnings: none found, but the LLM-era analogues are state services without revenue.
- Polish adaptation can reproduce: replaced spend = a 4,457 PLN agency fee or the employer's HR hours; first channel = Ukrainian community groups and staffing agencies using 002; retention driver = renewals and the letter explainer, weak.

**Graveyard:** Visabot (US, 2016–2017 coverage) has no recent public trace (status unverified). DoNotPay's move into asylum forms ended in its FTC case (cited in 009, not re-read). Lesson: consumer legal bots get reach fast but struggle to keep paying users and attract regulator attention.

**Scores (1–5):** L1 4 · L2 2 · L3 3 · L4 4 · L5 4 · L6 2 · L7 3 · L8 3 · L9 2 | **Weighted:** 3.1 / 5 | **Chance band:** score → 5–15%; O 25, R 31, R − O = 6 → **<5%**. The need is large and dated (MOS 2.0, CUKR) and the localisation is deep, but B2C willingness to pay competes with free state and NGO help, and the wave ends in March 2027. The idea is stronger as the B2C front end of 002 than as a stand-alone business.
Changes vs. quick score: none on the lenses (L5 4 now sourced with OKO.press application counts); weighted 3.1 unchanged; band lowered by §4.

**Cheapest validation test (≤1 week, ≤200 PLN):** a Ukrainian-language landing page with a free CUKR/pobyt czasowy checklist generator and a "paid document check, 149 PLN" pre-order button (BLIK); post it in 5 Ukrainian groups in Poland and spend 150 PLN on Meta ads in Ukrainian; count checklist users and pre-orders.

**Kill criteria:** <1% of checklist users click the paid button; or <20 pre-orders from ~2,000 visitors; or no staffing agency wants the employer package.

**Confidence:** medium-low (rules and market size sourced; willingness to pay, ChatGPT quality on MOS and post-MOS-2.0 complaints not tested).

**Sources** (accessed 2026-11-06 unless noted):
1. https://builtin.com/articles/boundless-immigration-raises-25m-series-b-hiring
2. https://www.smithsonianmag.com/innovation/could-chatbot-prevent-some-deportations-180962435/
3. https://imagazine.pl/2026/01/02/mobywatel-wchodzi-w-2026-rok-z-polskim-ai/
4. https://mos.cudzoziemcy.gov.pl/jak-zaczac/
5. https://www.gov.pl/web/dolnoslaski-uw/cudzoziemcy-info
6. https://migrant.poznan.uw.gov.pl/pl/node/5099
7. https://lewiatan.org/wp-content/uploads/2025/10/2025.10.02-stanowisko-Konfederacji-Lewiatan-do-projektu-ustawy-o-zmianie-ustawy-o-cudzoziemcach-oraz-niektorych-innych-ustaw-MOS-Druk-nr-1630.pdf
8. https://www.gov.pl/web/udsc/CUKR-procedura
9. https://zielonalinia.gov.pl/karta-pobytu-cukr-mozna-juz-skladac-wnioski/
10. https://oko.press/chaos-cyfryzacja-wnioskow-o-legalizacje-pobytu-cudzoziemcy
11. https://ceo.com.pl/en/?p=5085 (accessed 2026-11-04)
12. https://cenauslug.pl/firma-i-biuro/legalizacja-pobytu-i-zatrudnienia-cudzoziemcow (accessed 2026-11-04)
13. https://r2p.org.ua/page/legal-adviser-20-for-ukrainians-in-poland-chatbot-is-launched (accessed 2026-11-04)
14. https://poland.aitinkerers.org/hackathons/h_qfzjGGzYIdw/teams/ht_BDdXbyZ565I
15. https://openrouter.ai/google/gemini-2.5-flash (accessed 2026-11-05)
16. https://artificialintelligenceact.eu/annex/3/
17. Internal: [TH59 check](../../poland-check/B/TH59-citizen-sme-public-service-navigators.md), [002](002-teczka-legalizacyjna.md), R3/R4/R5/R8 catalogue rows

Coverage: 7 web searches and 3 page fetches for this write-up (CUKR application counts, MOS problems, Polish B2C helpers, Boundless and Visabot traction and fate). Not found: CUKR applications filed so far, post-MOS-2.0 complaint coverage, any paid Polish B2C MOS helper, Boundless current revenue.
