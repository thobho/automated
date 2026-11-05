# 004 — Claim-file assistant for kancelarie odszkodowawcze

**One-liner:** A compensation-claims firm uploads a client's injury file (medical records, police notes, insurer decisions); the tool returns a dated medical chronology, a list of missing documents, a zadośćuczynienie range backed by similar Polish judgments from SAOS, and a draft wezwanie do zapłaty to the OC insurer.
**Field:** legal-compliance | **Type:** SaaS (web) | **B2B** · shortlist id L069 (merges L070 work-accident file builder, L071 FKZM patient-compensation file)

**Western analogues:**
- **EvenUp** (US, 2019; LLM product since 2023): AI demand letters and medical chronologies for personal-injury (PI) firms. **US$150M Series E at >US$2B valuation (Oct 2025)**, led by Bessemer; the company says ARR doubled y/y and 2,000+ firms use it, including 20% of the top-100 US PI firms ([Business Wire](https://www.businesswire.com/news/home/20251007138957/en/EvenUp-Raises-150M-Series-E-at-2B-Valuation-to-Redefine-Personal-Injury-Law-and-Level-the-Playing-Field-for-Injury-Victims); [Bloomberg Law](https://news.bloomberglaw.com/legal-ops-and-tech/ai-legal-tech-evenup-raises-150-million-at-2-billion-valuation)). LexisNexis/REV invested ([LexisNexis](https://www.lexisnexis.com/community/amp-pressroom/rev-and-lexisnexis-invest-in-evenup-the-leader-in-ai-for-personal-injury-law)).
- **Supio** (US): AI case-data platform for PI and mass-tort plaintiff firms; **US$60M Series B (Apr 2025)** led by Sapphire, with Thomson Reuters Ventures; reported 4× ARR growth since its Series A ([TechCrunch](https://techcrunch.com/2025/04/30/supio-an-ai-powered-legal-platform-lands-60m-in-fresh-capital)).
- **Eve** (US, plaintiff AI), **Turbo Law** (TR, litigation platform, 1,800+ active case files, company claim) ([Global Legal Post](https://www.globallegalpost.com/news/us-ai-litigation-platform-start-up-turbo-law-raises-38m-in-pre-seed-funding-round-1445015597)).

**Spread:** TH11 in US and Turkey (R1, R9), since 2023 for LLM products. Medical-record summarisers also in UK/CA claims (TH11). No CEE analogue in R6.

**Does the Western leader already work in Poland?** No. EvenUp and Supio are demo-led and built on US PI economics: US insurers, US medical billing codes as the damages base, contingency fees, English only (TH11; not re-opened hands-on). Polish zadośćuczynienie is not computed from medical bills but set by courts from case practice, so EvenUp's core (special damages from billing) does not transfer. Polish generic legal AI (Gaius-Lex, LEX Expert AI) does research and drafting but not injury-file chronologies or damages ranges (TH11).

**Polish adaptation, i.e. the edge:**
- Polish damages law: zadośćuczynienie (art. 445 and 446 KC), OC sprawcy claims first handled by insurers, ZUS jednorazowe odszkodowanie for work accidents (L070 module: ustawa wypadkowa rules still †, source before build), Rzecznik Finansowy route.
- **Amount benchmarks from SAOS and Portal Orzeczeń** ([M29, M30](../../research/poland/local-moats.md)): a corpus of Polish judgments with amounts per injury type, built once, reused per case. This is the proprietary data layer.
- **Fundusz Kompensacyjny Zdarzeń Medycznych** at the Rzecznik Praw Pacjenta: applications since 2023-09-06, 111 in 2023 and 1,574 in 2024 ([Sejm interpellation 8909 answer](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDGMHRA/i08909-o1.pdf)): a new out-of-court route with its own application.
- Polish medical records (EDM, IKP exports, handwritten scans), Polish medical vocabulary; RODO art. 9.

**Target customer in Poland:**
- Kancelarie odszkodowawcze (law firms and non-lawyer claims firms) from Votum S.A. (listed) down to local firms: autocomplete "kancelaria odszkodowawcza" yields 8 city variants (TH11). Total count not found (unverified; estimate several hundred to low thousands).
- Buyer: partner or head of a claims team; user: case handler.
- Case volume driver: 24,590 people injured (7,866 seriously) and 1,660 killed in 20,925 police-reported road accidents in 2025 ([Policja, Wypadki drogowe 2025](https://statystyka.policja.pl/download/20/473186/Wypadkidrogowe2025.pdf)); plus work accidents and medical incidents (FKZM).
- CEE: Czech and Slovak tort damages differ; expansion is a new corpus per country.

**Demand driver:** Weak demographic link (DD1/DD3 ageing and NFZ queues feed malpractice claims; no numeric driver found). Technological: LLMs can now read scanned Polish medical files. Negative driver: CHF (frankowe) litigation, the largest claimant-side revenue pool, is shrinking: Votum's Q1 2026 revenue was 105.6 M PLN vs 123.1 M a year earlier ([bankier.pl](https://www.bankier.pl/wiadomosc/VOTUM-S-A-Wyniki-finansowe-QSr-1-2026-9141854.html)), and some courts report up to 60% fewer new CHF suits ([podatki.biz](https://www.podatki.biz/artykuly/sprawy-frankowe-spadek-liczby-pozwow-i-poprawa-efektywnosci-sadow_16_58880.htm)). That could push firms back to injury claims and make them seek efficiency, or shrink their budgets.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Gaius-Lex (Kraków, 2024) | Polish legal AI: research, document analysis, drafting | not found | general, no injury chronology or damages range ([Stanford CodeX](https://techindex.law.stanford.edu/companies/gaius-lex)) |
| LEX Expert AI (Wolters Kluwer) | chat over LEX acts, judgments, commentaries | LEX subscription | research, not case files ([wolterskluwer.com](https://www.wolterskluwer.com/pl-pl/solutions/lex/expert-ai/dlaczego-lex-expert-ai)) |
| ChatGPT / Claude / Gemini | firms paste documents (estimate) | 0–100 PLN/month per seat | no SAOS-backed amounts, RODO art. 9 risk with consumer accounts |
| In-house case handlers | manual chronology and letters | salary | this is the replaced spend |
A Polish search for an AI program for compensation firms found articles about AI in PI law and no product (2026-11-05).

**Evidence of Polish demand:** consumer-side demand is large (autocomplete "odszkodowanie za wypadek", "zadośćuczynienie za", "pozew o zadośćuczynienie wzór", 10 suggestions each; TH11). Firm-side: "ai pismo procesowe" returns nothing, i.e. firms do not search for tools. No job posts or forum quotes from firms were collected. Demand from firms is inferred, not shown.

**MVP scope (≤6 weeks):**
1. Upload PDFs/scans; OCR + LLM extraction into an event table (date, facility, diagnosis, treatment, source page).
2. Chronology export (DOCX) with page citations; missing-document checklist (e.g. karta informacyjna, orzeczenie o stopniu uszczerbku, decyzja ubezpieczyciela).
3. SAOS corpus: download judgments with art. 445 KC, extract injury type and awarded amount (batch job, human-checked sample); retrieve 5–10 similar cases per file and show the range with links.
4. Draft wezwanie do zapłaty to the OC insurer from a template + extracted facts.
5. Tests: 20 anonymised fixture files with expected chronology rows; SAOS extraction precision measured on a labelled sample.

**Monetization:** 499 PLN/month per firm up to 20 new files, then 29 PLN per file; FKZM application pack 49 PLN per file. Payer: the firm (it earns a success fee, typically a share of the payout; level not verified).
**Unit economics:** a file of ~100 pages ≈ 60k input tokens + 20k retrieved judgments + 5k output. Gemini 2.5 Flash at US$0.30/US$2.50 per M ([OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.04; with a frontier model for the chronology pass (~US$3/US$15 per M, estimate) ≈ US$0.35 ≈ 1.3 PLN; OCR of scans ≈ 1–2 PLN (estimate). ≤4 PLN per file vs. 25–29 PLN effective price → gross margin ~85%. One-off cost: SAOS corpus build (a few hundred PLN of tokens, estimate). 10k PLN MRR = 20 firms.

**Distribution, first 10 customers:** list firms from the "kancelaria odszkodowawcza [miasto]" SERPs in 8 cities (~100 firms); offer a free chronology of one real (anonymised) file in 24 h; follow up by phone. Secondary: Polish legal-tech community (LinkedIn), the Izba Gospodarcza Doradców Odszkodowawczych if it exists (unverified).

**Regulation:** AI Act: not high-risk; Annex III point 8 covers AI used **by judicial authorities** to research and apply law, not by parties ([AI Act Annex III](https://artificialintelligenceact.eu/annex/3/)); transparency obligations only. RODO art. 9 health data: EU hosting, DPA with each firm, no training on client data, deletion policy; this is a selling point vs. consumer ChatGPT. Professional rules: the lawyer reviews and signs; the tool drafts. Claims firms that are not law firms may act out of court (not re-verified).

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | SAOS amount corpus becomes a unique asset that firms and insurers' adjusters want | M | H | firms ask for the range tool alone; an insurer asks for API access |
| O2 | FKZM route (1,574 applications in 2024) grows and needs a standard file | M | M | 2025 FKZM count above 2024 |
| O3 | Post-CHF firms redeploy staff to injury claims and want throughput | M | M | Votum and peers report growth in injury segment |
| O4 | Votum-size firm signs an enterprise deal | L | H | an RFP or pilot with a listed firm |
| O5 | Work-accident (ZUS) module opens HR/BHP consultants as a second buyer | L | M | BHP consultants respond to outreach |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Firms already paste files into ChatGPT and see little extra value | H | M | pilot users say the chronology is "what ChatGPT gives me" |
| R2 | Market is small and price-sensitive: Polish payouts are far below US PI, firms are local and few | M | H | <20 firms reply out of 100 |
| R3 | RODO art. 9 trust: firms won't upload medical files to a one-person vendor | M | H | requests for on-premise or ISO 27001 |
| R4 | SAOS amounts are hard to extract and biased (only published judgments) | M | M | extraction precision <80% on a labelled sample |
| R5 | Gaius-Lex or LEX adds a PI module | M | M | product announcements |
| R6 | CHF decline cuts firm budgets and headcount | M | M | further revenue drops at Votum |

**Success signals:**
- Western analogue durable signals: replaces paralegal and lawyer drafting hours (budget line: case-handler salaries); expansion (2,000+ firms, ARR doubling at EvenUp; 4× ARR at Supio); strategic investors (LexisNexis/REV, Thomson Reuters) suggest hard-to-absorb workflow; value-based per-case pricing. No public NRR or churn.
- Hype warnings: none found; valuation-led coverage, ARR claims are company-reported.
- Polish adaptation can reproduce: replaced spend = case-handler hours on chronology and letters; first channel = outbound to firms listed in city SERPs; retention driver = files live in the tool through the claim, plus the SAOS benchmark that improves with use.

**Graveyard:** DoNotPay ("robot lawyer", US, consumer) was ordered by the FTC in February 2025 to pay US$193,000 and stop claiming it matches a human lawyer without evidence ([FTC via getcoai summary](https://getcoai.com/news/ftc-bans-donotpays-ai-lawyer-claims-and-orders-refunds)). Lesson: sell to lawyers as drafting support, never market it as replacing them. No failed PI-AI product found.

**Scores (1–5):** L1 4 · L2 3 · L3 4 · L4 4 · L5 3 · L6 3 · L7 3 · L8 3 · L9 3 | **Weighted:** 3.4 / 5 | **Chance band:** 5–15%. The Western pattern is the strongest in this batch (EvenUp, Supio) and the SAOS corpus is a real local moat. But the Polish market is a few hundred local firms with small payouts and a shrinking CHF budget, firm-side demand is unproven, and RODO art. 9 trust is a hurdle for a solo founder.
Quick scores confirmed; L2 kept at 3 (strong durable signals but only 2 countries).

**Cheapest validation test (≤1 week, ≤200 PLN):** email/phone 50 firms from city SERPs: "send one anonymised injury file, get a chronology + 5 similar SAOS judgments with amounts in 24 h, free". Do it by hand with an LLM + SAOS search (concierge). Ask each a price question after delivery. Cost: ~0–100 PLN.

**Kill criteria:** <5 of 50 firms send a file; or none says it would pay ≥300 PLN/month after seeing the output; or ≥3 firms refuse because of medical-data hosting.

**Confidence:** medium (Western traction and Polish moat well sourced; Polish firm count and demand not).

**Devil's advocate (T24, 2026-11-06):**
- *EvenUp's economics do not cross the border.* EvenUp sells into a US market where one PI demand letter can unlock six-figure settlements and contingency fees pay for software. Polish zadośćuczynienie awards are far smaller and the firm's success fee is a share of that (level still unverified), so a 499 PLN/month tool is a much larger share of a Polish firm's revenue per case than EvenUp is of a US firm's.
- *It already works in Polish (partly).* A medical chronology from a 100-page PDF is exactly what Claude/Gemini do well in Polish today; R1 is the core risk, not a side risk. The only piece a general assistant lacks is the SAOS amount corpus, and SAOS covers only published judgments, while most claims settle with the OC insurer, which uses its own internal tables. The "range" may not match what firms actually negotiate.
- *Polish customers won't pay this.* Firm-side demand is still inferred ("ai pismo procesowe" returns nothing). The firm count is still an estimate; the criteria §3 sanity check (20 firms × 20 = 400 reachable firms, with a source) cannot be passed, so the band is capped at 5–15% before §4 anyway.
- *Western leader localizing.* Unlikely within 12 months (US-centric damages model). Local threat: Gaius-Lex or LEX adding a document-chronology feature, which is generic.
- *Second competitor search (2026-11-06):* "sztuczna inteligencja kancelaria odszkodowawcza program analiza dokumentacji medycznej zadośćuczynienie kalkulator orzeczeń" found no Polish product; it found more foreign analogues on the **insurer/defence** side (Wisedocs, CA, for insurers and defence counsel; CLARA Claims DocIntel; expert.ai at Plexus Law, UK, 2022) ([Wisedocs](https://www.ai.engineer/orgs/wisedocs); [CLARA](https://claraanalytics.com/products/claims-document-intelligence-pro/); [expert.ai Plexus PDF](https://www.expert.ai/wp-content/uploads/2022/10/Plexus-case-study.pdf), search excerpts). Spread widens to CA and UK, and it suggests a second Polish buyer: insurers' claims departments (who would build in-house).
- *Success signals.* EvenUp and Supio show expansion (ARR doubling, 4× ARR) and strategic investors; these are company-reported but sourced. Durable, not hype. L2 3 is conservative; spread now US, TR, CA, UK would allow 4, but the PI-firm pattern itself is still US-only, so 3 stays.
- *Opportunity/risk lists.* Independent; R1 should be H×M as written. §4 not applied in T21.

**Review changes (T24, 2026-11-06):** scores unchanged (L1 4 · L2 3 · L3 4 · L4 4 · L5 3 · L6 3 · L7 3 · L8 3 · L9 3; weighted **3.4**). §4: O 6+4+4+3+2 = 19, R 6+6+6+4+4+4 = 30, R − O = 11 ≥ 6 → down one band: 5–15% → **<5%** (the §3 customer-count sanity check would also cap it at 5–15%). Not rejected: the concierge test with 50 firms is cheap and decisive.

**Sources** (accessed 2026-11-05):
1. https://www.businesswire.com/news/home/20251007138957/en/EvenUp-Raises-150M-Series-E-at-2B-Valuation-to-Redefine-Personal-Injury-Law-and-Level-the-Playing-Field-for-Injury-Victims
2. https://news.bloomberglaw.com/legal-ops-and-tech/ai-legal-tech-evenup-raises-150-million-at-2-billion-valuation
3. https://www.lexisnexis.com/community/amp-pressroom/rev-and-lexisnexis-invest-in-evenup-the-leader-in-ai-for-personal-injury-law
4. https://techcrunch.com/2025/04/30/supio-an-ai-powered-legal-platform-lands-60m-in-fresh-capital
5. https://www.globallegalpost.com/news/us-ai-litigation-platform-start-up-turbo-law-raises-38m-in-pre-seed-funding-round-1445015597 (TH11)
6. https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDGMHRA/i08909-o1.pdf (T20)
7. https://statystyka.policja.pl/download/20/473186/Wypadkidrogowe2025.pdf
8. https://www.bankier.pl/wiadomosc/VOTUM-S-A-Wyniki-finansowe-QSr-1-2026-9141854.html (TH11)
9. https://www.podatki.biz/artykuly/sprawy-frankowe-spadek-liczby-pozwow-i-poprawa-efektywnosci-sadow_16_58880.htm (TH11)
10. https://techindex.law.stanford.edu/companies/gaius-lex (TH11)
11. https://www.wolterskluwer.com/pl-pl/solutions/lex/expert-ai/dlaczego-lex-expert-ai (TH11)
12. https://openrouter.ai/google/gemini-2.5-flash
13. https://artificialintelligenceact.eu/annex/3/
14. https://getcoai.com/news/ftc-bans-donotpays-ai-lawyer-claims-and-orders-refunds
15. https://www.ai.engineer/orgs/wisedocs (2026-11-06, T24, excerpt)
16. https://claraanalytics.com/products/claims-document-intelligence-pro/ (2026-11-06, T24, excerpt)
17. https://www.expert.ai/wp-content/uploads/2022/10/Plexus-case-study.pdf (2026-11-06, T24, excerpt)
18. Internal: [TH11 check](../../poland-check/B/TH11-plaintiff-litigation-casework.md), [shortlist notes († rules)](../shortlist-notes.md), [local-moats M29/M30](../../research/poland/local-moats.md)

Coverage: 5 web searches for this write-up (EvenUp, Supio, road-accident and OC payout data, Polish AI for claims firms, DoNotPay). Not found: number of claims firms in Poland, OC zadośćuczynienie payout totals (KNF), any Polish product for injury files.
