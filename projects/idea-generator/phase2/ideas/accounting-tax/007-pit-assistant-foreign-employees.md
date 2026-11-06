# 007 — PIT assistant for foreign employees ("Мій PIT")

**One-liner:** A Ukrainian/English/Russian web app for foreigners employed in Poland: the user photographs their PIT-11 (or IFT-1R), answers a short residency questionnaire, and the app decides which case they are in (resident on PIT-37, resident with Ukrainian income on PIT-36 + PIT/ZG, or non-resident), finds the refunds Twój e-PIT leaves out (unused ulga na dziecko, joint filing), explains it in their language and hands them a pre-checked return to accept in Twój e-PIT. Employers and staffing agencies buy it in bulk as a staff benefit.
**Field:** accounting-tax | **Type:** SaaS (web, mobile-first) | **B2C with B2B tier** (employers, agencje pracy tymczasowej) · shortlist id L014 (merges L015 employer channel)

**Western analogues:**
- **Samjjeomsam / 삼쩜삼** (KR, Jobis & Villains, launched May 2020): finds missed refunds for gig and freelance workers and files the claim. **23 million cumulative subscribers and 1.67 trillion won of refund claims by April 2025** (12.19 million claims) ([Venture Square](https://www.venturesquare.net/en/982378)); 24 million subscribers by July 2025 (search excerpt, not re-read). In March 2026 it moved to "refund first, fee later" (search excerpt; [Asia Business Daily](https://www.asiae.co.kr/en/article/2026031708331058189)). Revenue not found.
- **TaxDown** (ES, also MX): AI tax-return app; **€4M financing from BBVA Spark (March 2026)**; company says >4 million users, 500+ B2B partners, sales income growth >100% in 2025 and profitability ([The Next Web](https://thenextweb.com/news/taxdown-secures-e4m-financing-to-expand-ai-tax-platform)). Company-reported figures.
- **Taxfix** (DE, also ES, IT, UK): mobile tax-return app, US$220M Series D at a >US$1B valuation in April 2022 ([Index Ventures](https://www.indexventures.com/perspectives/taxfix-announces-220-million-funding-round/)); bought TaxScouts to enter the UK in July 2024 ([Taxfix press release](https://taxfix.de/en/pm-taxscouts-acquisition)). Revenue estimates (US$56.6M in 2024, Latka) are third-party and unverified.
None of them targets **foreign workers** specifically; the Polish adaptation borrows the "find the refund you missed, explained simply" pattern and points it at a group the state pre-fill serves badly.

**Spread:** TH21 consumer tax filing: KR, ES, MX, DE, IT, UK, plus Heru (MX) and Cenit (CL) in R10 ([TH21 check](../../poland-check/A/TH21-consumer-tax-filing.md)). No CEE consumer tax app in R6.

**Does the Western leader already work in Poland?** No. Taxfix files German, Italian, Spanish and UK returns only; Samjjeomsam and TaxDown are tied to their national systems (TH21 check; not tried hands-on, since none offers a Polish return). The relevant comparison is Polish (below): the state pre-fill and free programs are Polish-only.

**Polish adaptation, i.e. the edge:**
- **The data:** in tax year 2025 employers issued PIT-11 for **1,541,808 people with non-Polish citizenship**, and IFT-1R (the non-resident form) for **58,953** non-Polish citizens; 63,523 PIT-11 recipients had a foreign address ([MF answer to interpelacja 16977, 2026-05-29](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDUMJ6S/i16977-o1.pdf)). The PIT-11 vs IFT-1R choice is the payer's view of residency, which the worker may need to correct.
- **Residency rules:** 183 days or centre of vital interests; the Poland–Ukraine double-tax treaty decides dual cases; Polish residents must declare income from a Ukrainian employer on PIT-36 with PIT/ZG, and undeclared income risks back tax and penalties ([Komersant, 2026-07-13](https://komersant.ua/en/ukrainczyam-u-polshhi-zagrozhuyut-shtrafi-za-viddalenu-robotu-na-ukrainski-kompanii-shho-potribno-znati/)). The RPO raised dual-residency problems of Ukrainians with the MF in 2022 ([prawo.pl](https://www.prawo.pl/podatki/problemy-podatkowe-ukraincow-w-polsce-rpo-interweniuje-w-mf,517119.html)).
- **Twój e-PIT gaps:** ulga na dzieci is carried over automatically only if it was claimed in earlier returns, and the **unused part of the relief is refunded only if the taxpayer ticks the option**; low earners with children lose up to ~1,000 PLN ([money.pl](https://direct.money.pl/artykuly/porady/twoj-e-pit-zaniza-ulge-na-dziecko-sprawdz,-jak-nie-stracic-1000-zl-zwrotu-z-podatku); [podatki.gov.pl FAQ](https://www.podatki.gov.pl/twoj-e-pit-rozlicz-roczny-pit-online/pytania-i-odpowiedzi/ulgi-i-odliczenia)). That is the Samjjeomsam "missed refund" in Polish form. Whether the relief applies when the child lives in Ukraine was **not confirmed** in this pass (art. 27f; KIS interpretations to check).
- **Login and submission:** Twój e-PIT works with PESEL via login.gov.pl or the "Twoje dane podatkowe" route (PESEL/NIP, date of birth, an income amount) ([podatki.gov.pl](https://podatki.gov.pl/twoj-e-pit-rozlicz-roczny-pit-online/pytania-i-odpowiedzi/logowanie-i-wysylka/jak-sie-zalogowac-do-uslugi-twoj-e-pit)); the interface is Polish; no Ukrainian version was found (a 2020 Ukrainian KAS leaflet turned up in search but its URL is now dead). A foreign team would need to learn all of the above plus PIT-11 field semantics; it is months of work, not translation.

**Target customer in Poland:**
- B2C: foreign employees with PIT-11, ~1.54 million in 2025 (above); 857.1 thousand Ukrainians insured in ZUS at end-2025, of 1,288.8 thousand foreigners ([infor.pl, 2026-06-16](https://www.infor.pl/prawo/nowosci-prawne/7606553,ilu-cudzoziemcow-placi-skladki-na-zus-a-ilu-dostaje-z-zus-emerytury-i-renty-najnowsze-dane.html)). Paying segment = the complex share (children, spouse, Ukrainian income, residency doubt); its size is **not known** (estimate 10–20%, unverified).
- B2B: employers and staffing agencies of foreigners; 8,550 agencies in KRAZ at end-2024 ([WUP Toruń analysis](https://wuptorun.praca.gov.pl/documents/d/wuptorun/analiza-agencje-zatrudnienia-2024)).
- CEE: CZ also has a large Ukrainian workforce, but the tax system is different; expansion is a new rules engine.

**Demand driver:** demographic (DD6: foreign workforce settling, families reunited, so more residents with children and more residency questions) plus the yearly 30 April deadline. No new dated regulation found.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Twój e-PIT (KAS) | pre-filled PIT-37, auto-accepted 30 April | free | Polish UI; misses unused ulga refund unless ticked; no residency guidance ([TH21](../../poland-check/A/TH21-consumer-tax-filing.md)) |
| PITax, e-pity, Program PIT | free PIT programs with relief questionnaires | free (1.5% OPP model) | Polish only, no IFT-1R or residency flow found ([pitax.pl](https://www.pitax.pl/)) |
| Biura rachunkowe | file PIT for individuals | 50–150 PLN for simple returns ([bankier.pl, 2024](https://www.bankier.pl/wiadomosc/Ile-kosztuje-rozliczenie-PIT-Formularz-mozna-wypelnic-za-darmo-online-8689300.html)) | in Polish; Ukrainian-speaking offices exist but prices not found |
| Euro-Tax.pl | foreign tax refunds (DE, NL, UK…) for Poles, UA version | success fee | refunds **from abroad**, not Polish returns of foreigners |
| Guides (Kyiv Post, TransferGo, city migrant portals) | how to file PIT-37, in Ukrainian | free | content, no per-person answer ([Kyiv Post](https://www.kyivpost.com/uk/post/40179)) |
| ChatGPT | ask in Ukrainian | free / 20 USD | explains rules, can't read Twój e-PIT, residency answers unverified |

**Evidence of Polish demand:** autocomplete "pit dla ukraińca" → "pit 11 czy ift dla ukraińca", "rozliczenie pit dla ukraińca", "… jaki urząd skarbowy" (TH21 check); Ukrainian-language guides from Kyiv Post, TransferGo and city portals (Wrocław, Poznań voivodeship "все про PIT-37 для іноземців" events) show recurring need; 41,038 PIT-11 corrections for foreigners in 2025 (MF answer) show data errors at source. No evidence yet that foreigners pay for help beyond the accountant market.

**MVP scope (≤6 weeks):**
1. PIT-11 / IFT-1R photo → structured fields (vision LLM + schema check, golden files on 50 anonymised forms).
2. Rules engine (deterministic code, not the LLM) for residency, form choice, ulga na dzieci incl. the unused-relief refund, joint filing; PIT/ZG for Ukrainian income in v2.
3. Ukrainian/English/Russian explanations generated from the rules output; a "what to click in Twój e-PIT" walkthrough with screenshots; PDF summary.
4. Employer tier: bulk invite link, dashboard of who finished, no access to workers' results.
5. Tests: rule tables as fixtures (each case → expected form and refund), run in CI.

**Monetization:** B2C 39 PLN per return when the app finds a refund ≥100 PLN (refund-first pricing, like Samjjeomsam 2026), free otherwise. B2B: 15 PLN per worker per season, invoiced annually to employers/agencies (VAT invoice). **Unit economics:** a PIT-11 image plus ~20 chat turns ≈ 30k input / 5k output tokens; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.02 per user. Payment fees ~2% (estimate). Gross margin >95%. **The problem is the calendar, not cost:** 10k PLN MRR = 120k PLN/year ≈ 3,100 paid B2C returns, or 8,000 B2B seats, almost all sold in February–April. Reaching an MRR-shaped business needs annual B2B contracts or a year-round product (e.g. residency and PIT/ZG checks, NIP/PESEL help) that does not exist yet.

**Distribution, first 10 customers:** B2C: Ukrainian-language Facebook and Telegram groups for Ukrainians in Polish cities, posts with a free "do I get a refund?" check in February; Ukrainian-language SEO on "PIT-11 українцям", "ulga na dziecko" ("пільга на дитину"). B2B: outbound to staffing agencies from KRAZ (the same list as idea 002) offering a free season for 50 workers; HR teams of meat, logistics and construction firms.

**Regulation:** AI Act: not high-risk (not in [Annex III](https://artificialintelligenceact.eu/annex/3/)). Doradztwo podatkowe: preparing returns on behalf of taxpayers is regulated in Poland; a self-service tool where the user files is the safer design, as the TH21 check notes (the exact scope of art. 2–3 of the act was **not confirmed** in this pass; counsel check before launch). RODO: PIT-11 data and children's PESEL are personal data; EU hosting, delete after the season. Korea's lesson: the tax accountants' association fought Samjjeomsam in police and prosecutors' offices from March 2021 to May 2025 before the case was finally dismissed ([Asia Business Daily](https://www.asiae.co.kr/en/article/2025061209385663023)).

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Staffing agencies buy it as a benefit and a retention tool, paid per worker per year | M | H | 2 of 20 agencies contacted take a free pilot season |
| O2 | The unused-ulga refund is common among low-earning foreign parents, giving a concrete "we found you X PLN" hook | M | M | ≥25% of beta users with children get a refund they had missed |
| O3 | Shared customers and outbound list with idea 002 (teczka legalizacyjna): one agency relationship, two products | M | M | agencies using 002 ask for PIT help |
| O4 | Viral spread inside Ukrainian community groups at deadline time | M | M | a group post brings >300 checks in a week |
| O5 | Year-round add-ons (PIT/ZG for Ukrainian income, residency certificate help) turn it into a subscription | L | M | users ask for these during beta |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Seasonality: revenue concentrated in Feb–April, so no stable 10k PLN MRR within 12 months | H | H | B2B pilots refuse annual contracts |
| R2 | Most foreign workers are simple PIT-37 cases that Twój e-PIT handles free, so few find a refund | H | M | <15% of checks show a refund ≥100 PLN |
| R3 | PITax or e-pity adds a Ukrainian UI (free, millions of users) | M | H | Ukrainian language switch on their sites |
| R4 | Doradztwo podatkowe complaint or wrong residency advice leads to a penalty for a user | L | H | a tax-adviser body comments publicly; a user gets a KAS letter |
| R5 | Trust: foreigners won't upload PIT-11 and children's PESEL to an unknown app | M | M | upload step drop-off >60% |

O sum 6+4+4+4+2 = 20; R sum 9+6+6+3+4 = 28. R1 is H×H; the MVP's mitigation is the annual B2B tier, which is unproven. R − O = 8 ≥ 6 → **band down one** (rule §4.3).

**Success signals:**
- Western analogue durable signals: Samjjeomsam replaces a tax accountant's fee and recovers money users would lose (budget line = the refund itself), with a decade-scale user base and repeat use each May ([Venture Square](https://www.venturesquare.net/en/982378)); TaxDown reports profitability and a B2B partner channel ([The Next Web](https://thenextweb.com/news/taxdown-secures-e4m-financing-to-expand-ai-tax-platform)); Taxfix expanded by acquisition (TaxScouts). Value-based pricing (per refund) is the norm.
- Hype warnings: none serious; but all three serve **their whole national population**, not a migrant niche, and traction is seasonal everywhere.
- Polish adaptation can reproduce: replaced spend = a 50–150 PLN accountant visit or the missed refund; first channel = Ukrainian community groups and agencies from KRAZ; retention driver = yearly return (seasonal), stored profile and children data.

**Graveyard:** no shutdown found for this theme (Taxfix/TaxScouts merged, not failed). The warning case is Samjjeomsam's four-year legal fight with the tax accountants' association (above): a profession can attack the model even when it wins.

**Scores (1–5):** L1 3 · L2 3 · L3 3 · L4 4 · L5 4 · L6 2 · L7 4 · L8 3 · L9 2 | **Weighted:** 3.2 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). Demand is large and sourced (1.54 million foreign PIT-11 recipients) and the build is cheap and testable, but the free state pre-fill covers the simple majority, the payer is unclear, and revenue arrives in three months a year, so a 10k PLN MRR business inside 12 months is unlikely without annual employer contracts. **Recommendation: do not build standalone; offer as a seasonal add-on to idea 002's agency customers and test whether agencies pay for it.**
Changes vs. quick score: L3 4 → 3 (Twój e-PIT and free programs handle the simple case; gap is language and edge cases), L7 4 kept, L5 4 kept (now sourced with MF counts); weighted 3.3 → 3.2.

**Cheapest validation test (≤1 week, ≤200 PLN):** in February, a one-page Ukrainian-language "Do you have a missed PIT refund?" checker (questionnaire only, rules engine, no upload) posted in 5 Ukrainian Facebook/Telegram groups; measure checks done and share with a refund; in parallel, email 20 staffing agencies from KRAZ offering a free season for their workers and ask for a price. Cost ≤100 PLN (domain, small boost).

**Kill criteria:** <15% of 300 checks show a refund ≥100 PLN; or 0 of 20 agencies willing to pay anything for next season.

**Confidence:** medium (counts and Twój e-PIT gaps sourced; refund frequency, willingness to pay and the child-abroad rule not).

**Devil's advocate (T24, 2026-11-06):**
- *It already works in Polish, and the Polish tools already target Ukrainians.* e-pity runs a dedicated "PIT dla Ukraińca" section (PIT-11, which form, tax office, missing PESEL, a residency explainer PDF) and its program fills PIT-37 from the employer's PIT-11 automatically ([e-pity](https://www.e-pity.pl/pit-dla-ukrainca/rozliczenie-pit-w-polsce/), fetched 2026-11-06; the deadline on the page is still 2024, so it is not kept current). PITax and podatnik.info have Ukrainian-citizen guides too ([PITax](https://www.pitax.pl/wiedza/poradnik-rozliczenia/rozliczenie-podatku-dochodowego-obywateli-ukrainy/); [podatnik.info](https://www.podatnik.info/publikacje/pit-11-dla-ukrainca-rozliczenie,6158d0), search excerpts). The UI is Polish, but the free programs already own the SEO and the flow; adding a Ukrainian UI (R3) is a translation job for them, not a moat for us.
- *ChatGPT will absorb it.* For the simple majority (one PIT-11, PIT-37, accept in Twój e-PIT) a Ukrainian-language chat answer is enough. The paid value sits only in residency doubt, Ukrainian income (PIT/ZG) and the unused child-relief refund, and the child-abroad rule for that refund is **still unconfirmed** after a second search (no KIS interpretation found). If children living in Ukraine do not qualify, the "we found you X PLN" hook shrinks to foreign parents whose children live in Poland.
- *Polish customers won't pay this.* The B2C payer is a low-earning worker deciding between a free state pre-fill and 39 PLN; the B2B payer (agencies) has no budget line for "PIT help" today; at best it is a retention perk. Paid human help exists at the margin (Ukrainian-language legal/accounting services such as [consultant.net.pl](https://consultant.net.pl/en/consultant-article/filing-a-pit-declaration-for-ukrainians-in-poland-legal-support-0), search excerpt; prices not found), which caps price expectations rather than proving willingness to pay.
- *Western leader localizing in 12 months.* No: Taxfix is still DE/IT/ES/UK, no TaxDown or Taxfix move into Poland or CEE found (second search 2026-11-06). The threat is local (e-pity, PITax, Pitbot, which partner content says can import from e-PIT; its Ukrainian-language claim could not be verified: comparic.pl returns 403).
- *Second competitor search (2026-11-06):* "rozliczenie PIT dla Ukraińców aplikacja po ukraińsku", "Pitbot PIT po ukraińsku", "Taxfix/TaxDown Poland": no Ukrainian-language PIT product confirmed; free Polish programs with Ukrainian-targeted content (above) and money-transfer firms' guides (Profee) found. No CEE (CZ) analogue for foreigners found.
- *Success signals.* Samjjeomsam and TaxDown are durable (repeat yearly use, refund-based pricing, profitability claimed by TaxDown, company-reported). But the durable signal is **national-population scale with an annual cycle**; the migrant-niche version has no Western analogue at all, and the seasonality that is harmless at 24 million users is fatal at a few thousand. L2 3 stays, not raised.
- *Opportunity/risk lists.* Independent. O3 (shared customers with 002) is a portfolio choice, not market evidence. R1 H×H is honest; its mitigation (annual B2B tier) is unproven, so the §4 move stands. R2 H likelihood is plausible but unmeasured.

**Review changes (T24, 2026-11-06):** scores unchanged (L1 3 · L2 3 · L3 3 · L4 4 · L5 4 · L6 2 · L7 4 · L8 3 · L9 2; weighted **3.2**; shortlist quick 3.3 with L3 4 replaced). §4 already applied in T21: O 20, R 28, R − O = 8 and R1 H×H with unproven mitigation → **<5%** confirmed. **Rejected as a standalone idea** and recorded in [rejected.md](../../rejected.md) as merged into L036 (write-up [002](../employment-migration/002-teczka-legalizacyjna.md)) as a seasonal add-on for the same agency customers, which is what T21 itself recommended. Open check carried over: ulga na dziecko for children living in Ukraine (art. 27f, KIS interpretations).

**Sources** (accessed 2026-11-05):
1. https://www.venturesquare.net/en/982378
2. https://www.asiae.co.kr/en/article/2026031708331058189
3. https://www.asiae.co.kr/en/article/2025061209385663023
4. https://thenextweb.com/news/taxdown-secures-e4m-financing-to-expand-ai-tax-platform
5. https://www.indexventures.com/perspectives/taxfix-announces-220-million-funding-round/
6. https://taxfix.de/en/pm-taxscouts-acquisition
7. https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDUMJ6S/i16977-o1.pdf
8. https://komersant.ua/en/ukrainczyam-u-polshhi-zagrozhuyut-shtrafi-za-viddalenu-robotu-na-ukrainski-kompanii-shho-potribno-znati/
9. https://www.prawo.pl/podatki/problemy-podatkowe-ukraincow-w-polsce-rpo-interweniuje-w-mf,517119.html
10. https://direct.money.pl/artykuly/porady/twoj-e-pit-zaniza-ulge-na-dziecko-sprawdz,-jak-nie-stracic-1000-zl-zwrotu-z-podatku
11. https://www.podatki.gov.pl/twoj-e-pit-rozlicz-roczny-pit-online/pytania-i-odpowiedzi/ulgi-i-odliczenia
12. https://podatki.gov.pl/twoj-e-pit-rozlicz-roczny-pit-online/pytania-i-odpowiedzi/logowanie-i-wysylka/jak-sie-zalogowac-do-uslugi-twoj-e-pit
13. https://www.infor.pl/prawo/nowosci-prawne/7606553,ilu-cudzoziemcow-placi-skladki-na-zus-a-ilu-dostaje-z-zus-emerytury-i-renty-najnowsze-dane.html
14. https://wuptorun.praca.gov.pl/documents/d/wuptorun/analiza-agencje-zatrudnienia-2024
15. https://www.pitax.pl/
16. https://www.bankier.pl/wiadomosc/Ile-kosztuje-rozliczenie-PIT-Formularz-mozna-wypelnic-za-darmo-online-8689300.html
17. https://www.kyivpost.com/uk/post/40179
18. https://openrouter.ai/google/gemini-2.5-flash
19. https://artificialintelligenceact.eu/annex/3/
20. https://www.e-pity.pl/pit-dla-ukrainca/rozliczenie-pit-w-polsce/ (2026-11-06, T24)
21. https://www.pitax.pl/wiedza/poradnik-rozliczenia/rozliczenie-podatku-dochodowego-obywateli-ukrainy/ (2026-11-06, T24, excerpt)
22. https://www.podatnik.info/publikacje/pit-11-dla-ukrainca-rozliczenie,6158d0 (2026-11-06, T24, excerpt)
23. https://consultant.net.pl/en/consultant-article/filing-a-pit-declaration-for-ukrainians-in-poland-legal-support-0 (2026-11-06, T24, excerpt)
24. Internal: [TH21 check](../../poland-check/A/TH21-consumer-tax-filing.md), [write-up 002](../employment-migration/002-teczka-legalizacyjna.md)

Coverage: 16 web searches/fetches for this write-up (Samjjeomsam traction and legal case, TaxDown, Taxfix, MF interpellation answer on foreigners' PIT, Twój e-PIT login and ulga rules, Ukrainian-language PIT services, accountant prices, ZUS foreigner counts, doradztwo podatkowe scope). Not found: a Ukrainian-language PIT product, prices of Ukrainian-speaking accountants, the ulga rule for children living abroad, the current text of art. 2–3 of the doradztwo podatkowe act, any shutdown in the theme.
