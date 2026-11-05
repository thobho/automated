# 009 — Per-procedure letter engine ("Pismo w 10 minut")

**One-liner:** A Polish web app where a consumer photographs the document they received (wezwanie do zapłaty opłaty dodatkowej from ZTM/MPK, a parking-zone notice, a nakaz zapłaty from e-Sąd, a ZUS decision), answers a few questions, and gets a fileable, current letter for that exact procedure (reklamacja, odwołanie, sprzeciw) with the correct deadline, addressee, legal basis and city-specific rules, plus a reminder of what happens next. Starts with transit and parking fines in the largest cities, then EPU sprzeciw with a limitation (przedawnienie) check, then ZUS appeals.
**Field:** legal-compliance | **Type:** SaaS (web, mobile-first) | **B2C** (later B2B tier for legal-aid points and consumer advocates) · shortlist id L063 (merges L064–L067)

**Western analogues:**
- **Lawhive** (UK, now also US): began as software for solicitors, pivoted into an AI-enabled consumer law firm; **US$60M Series B in February 2026**, annualised revenue reported **above US$35M, up about sevenfold in a year**, operating in the UK and 35 US states ([Fortune, 2026-02-05](https://fortune.com/2026/02/05/lawhive-ai-law-firm-startup-series-b-venture-funding/); [Global Legal Post](https://www.globallegalpost.com/news/uk-new-law-start-up-lawhive-secures-fresh-funding-for-us-expansion-1810357469)). It sells lawyer time made cheaper by AI, not self-service letters.
- **LoFrayer** (IL, launched May 2026): scan a traffic or parking ticket, answer chat questions, get an appeal document; nominal **NIS 35 fee** for submission, free if the user files it. About three weeks after launch the Israel Bar Association demanded it take the site down within three days or face an injunction ([Globes, 2026-06-09](https://en.globes.co.il/en/article-1001545334)). No user numbers published.
- **DoNotPay** (US, 2015, the original "robot lawyer" for parking appeals): see Graveyard.
- Valla (UK employment claims) is listed in the TH13 check; not re-checked here.

**Spread:** TH13 consumer legal help: UK, US, IL, Gulf (Mohami/Legaline), RO (Lawren.ai, AI+ Avocat) ([TH13 check](../../poland-check/A/TH13-consumer-legal-help-ai-law-firms.md)). Four regions, but each player is bound to one jurisdiction.

**Does the Western leader already work in Poland?** No. Lawhive is a regulated firm in England & Wales and US states; LoFrayer is Hebrew and Israeli-law-only; DoNotPay is US-only. None has a Polish site (TH13 check). Not tried hands-on: Lawhive requires a UK postcode. The real comparison is Polish template sites and ChatGPT (below).

**Polish adaptation, i.e. the edge:**
- **Transit fines are civil claims set by city resolutions.** The opłata dodatkowa is a carrier's civil claim, not a mandat ([formularze.net](https://formularze.net/sprawy/odwolanie-mandat-bilet)); amounts, discounts (e.g. 40% off if paid to the inspector) and cancellation windows (7 days with a valid season ticket in Warsaw) come from each city's tariff resolution ([Warszawa 19115](https://warszawa19115.pl/-/oplaty-dodatkowe)). Complaint deadlines differ by carrier, and secondary sources disagree (from 7–14 days to 3 months), so the product must hold a verified per-city table, not a generic prompt ([infor.pl](https://www.infor.pl/prawo/prawa-konsumenta/konsument-uslugi/764903,Jak-sie-odwolac-od-oplaty-dodatkowej-ZTM.html)).
- **Parking zones** (strefa płatnego parkowania): reklamacja to the city road authority (ZDM in Warsaw), separate from transit fines ([Warszawa 19115, parkowanie](https://warszawa19115.pl/-/parkowanie-reklamacje)).
- **EPU sprzeciw:** 14 days from delivery, no court fee, on the official form when the claim came on the form ([captain.legal](https://www.captain.legal/pl/sprawy-osobiste/sprzeciw-od-nakazu-zap-aty-wzor-pdf-i-word/); [infor.pl](https://www.infor.pl/prawo/pozwy/informacje-ogolne/96961,Sprzeciw-od-nakazu-zaplaty.html)); przedawnienie: six years general, three for business and periodic claims, consumer rules since 2018-07-09 ([shortlist notes](../shortlist-notes.md)). Limitation is the most common real defence against debt buyers.
- **ZUS appeal:** one month from delivery, lodged through the ZUS branch, no fee ([shortlist notes](../shortlist-notes.md)).
- **Lower professional-monopoly risk than IL/UK:** out-of-court legal advice is not reserved to adwokaci/radcy in Poland (TH13 check theme note; not re-verified in statute here), while court representation is.
A foreign team would have to learn per-city tariff resolutions, KPC upominawcze rules and ZUS procedure; that is months of research, but each procedure is public and a Polish copycat could build it too.

**Target customer in Poland:** consumers who receive a fine, a nakaz zapłaty or a ZUS decision; urban public-transport users first (ZTM Warsaw alone sold 115.1 million tickets in 2024, per a search excerpt of an antyweb.pl article, not re-read). The number of opłaty dodatkowe issued per year was **not found** (ZTM annual report not read); the number of EPU nakazy in 2024 was **not found** (MS statistical yearbooks not parsed; EPU issued 613,153 nakazy in its first year, 2010, per [Gazeta Prawna](https://www.gazetaprawna.pl/twoje-prawo/artykuly/10848117,esad-prawie-700-tys-spraw-w-ciagu-roku.html)). B2B: 1,490 nieodpłatna pomoc prawna points in 2024 (TH13 check). CEE: each country is a new rules base; RO already has two local players.

**Demand driver:** social and economic (DD12: a 300–500 PLN lawyer consultation feels expensive versus a ~30 PLN letter), migrants facing Polish offices (DD6), seniors with ZUS matters (DD1). No dated regulatory trigger.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| captain.legal | fill-in templates (sprzeciw with dates-based przedawnienie section, many others) | from 21.90 PLN per document ([captain.legal](https://www.captain.legal/pl/sprawy-osobiste/sprzeciw-od-nakazu-zap-aty-wzor-pdf-i-word/)) | fixed templates, no reading of the user's document, no per-city fine rules |
| wonder.legal (PL) | questionnaire-generated parking reklamacja and odwołanie | "start for free", price not shown ([wonder.legal](https://www.wonder.legal/pl/modele/reklamacja-oplaty-za-nieoplacony-postoj)) | generic, parking only for fines |
| formularze.net, infor.pl, dlajurysty.pl | free wzory and guides | free | user must adapt facts and deadlines |
| e-prawnik.pl and online lawyers | human letters (e.g. ZUS) | per case, not checked | slower, more expensive |
| Nieodpłatna pomoc prawna, mObywatel assistant | free advice / information | free | appointment needed; mObywatel does not interpret law (TH13 check) |
| ChatGPT | drafts letters on request | free / 20 USD | no current city rules or deadlines; citizens send AI letters with prompts left in (TH13 check) |

**Evidence of Polish demand:** autocomplete "odwołanie od mandatu" → "… mpk wrocław", "… za parkowanie", "… wzór", "… za brak biletu wzór"; "porada prawna online" → "… za darmo", "… cena" (TH13 check). Several paid template sites exist (above), which shows people pay ~20 PLN per document. No data on volume or conversion.

**MVP scope (≤6 weeks):**
1. Upload or photo of the received document → structured fields (issuer, date, amount, case number, city) with a vision LLM + schema check; golden files from 30 anonymised samples.
2. Rules tables (code, not LLM) for 6 cities' transit fines (Warsaw, Kraków, Wrocław, Poznań, Gdańsk/Gdynia, Łódź) and Warsaw parking; deadline and addressee from the table, each row linked to its source resolution and a "last verified" date.
3. Short questionnaire on the facts (valid ticket? app failure? wrong person?) → letter text drafted by the LLM inside a fixed structure, with the legal basis inserted from the table.
4. EPU sprzeciw with przedawnienie calculator as the second procedure (v1.1).
5. Output: PDF/DOCX, sending instructions (e-mail address, ePUAP or post), deadline reminder e-mail.
6. Tests: per-city fixtures (document → expected deadline, addressee, amount), run in CI.

**Monetization:** 29 PLN per letter (fines), 49 PLN for sprzeciw with limitation check; BLIK/Przelewy24; free preview of the deadline and grounds. Optional B2B seat for legal-aid NGOs (99 PLN/month, unproven). **Unit economics:** one document image + questionnaire + letter ≈ 15k input / 3k output tokens; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.012 per letter. Payment fees ~1.5–2.5% plus a fixed fee (estimate). Gross margin >90%. **The problem is volume, not cost:** 10k PLN MRR ≈ 345 letters at 29 PLN **every month**, all from new buyers, since a person rarely needs a second letter.

**Distribution, first 10 customers:** SEO pages per city and procedure ("odwołanie od opłaty dodatkowej MPK Wrocław wzór") with a free deadline check; posts in city Facebook groups and r/Polska threads about fines; outreach to 5 local consumer advocates (miejski rzecznik konsumentów) and legal-aid NGOs offering free use.

**Regulation:** AI Act: not high-risk (Annex III covers administration of justice only for judicial authorities; [Annex III](https://artificialintelligenceact.eu/annex/3/)); transparency duty for generated text is light. Consumer law: a paid letter is a service to consumers, so UOKiK rules on unfair practices and clear claims apply; the DoNotPay case shows "acts like a lawyer" marketing is the risk. RODO: documents contain names, addresses, PESEL sometimes; EU hosting, delete after delivery. Court representation stays with the user.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Per-city, per-procedure SEO pages rank for purchase-intent "wzór" queries, giving owned distribution | M | M | 3 pages on page 1 of Google within 3 months |
| O2 | EPU sprzeciw with przedawnienie check wins real cases against debt buyers, giving a strong, quotable result | M | H | ≥20% of beta sprzeciw users report the claim was dropped or dismissed |
| O3 | Legal-aid NGOs and consumer advocates adopt it as their drafting tool, a recurring B2B line | L | H | 2 of 10 contacted organisations ask for a paid seat |
| O4 | Polish law lets non-lawyers advise outside court, so the bar cannot shut it down as in Israel | H | L | no bar response after launch |
| O5 | Ukrainian/English versions serve migrants who cannot read the Polish wezwanie | M | L | ≥10% of traffic chooses UA/EN |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | One-off, per-letter revenue: 345 new buyers a month are needed, and nothing recurs | H | H | repeat-purchase rate <5% after 3 months |
| R2 | ChatGPT (free) writes a "good enough" letter, so few pay 29 PLN | H | M | free-preview to paid conversion <3% |
| R3 | Template sites already rank and anchor price at ~20 PLN, so SEO is slow and price is capped | H | M | no page in top 10 after 3 months |
| R4 | A wrong deadline or rule in a city table makes a user miss a deadline, with refund claims and bad reviews | M | M | users report rejected complaints for formal reasons |
| R5 | Most opłaty dodatkowe are justified (no ticket), so few grounds exist and letters rarely succeed | M | M | <20% of transit-fine letters report cancellation |

O sum 6+6+3+3+2 = 20; R sum 9+6+6+4+4 = 29. R − O = 9 ≥ 6, and R1 is H×H with no MVP mitigation (the B2B tier is O3, unproven) → **band down one** (rule §4.3).

**Success signals:**
- Western analogue durable signals: Lawhive replaces solicitor fees (signal 1), shows fast revenue expansion (seven-fold in a year, but growth, not NRR) and investor follow-on ([Fortune](https://fortune.com/2026/02/05/lawhive-ai-law-firm-startup-series-b-venture-funding/)); its value sits in regulated lawyer work (signal 8), which this idea does **not** copy. Durability score ~3 (signals 1, 2, 8) → unproven-to-promising.
- Hype warnings: DoNotPay's growth on "robot lawyer" claims that the FTC found unsupported; LoFrayer is weeks old with no numbers. The self-service letter pattern itself has no durable evidence.
- Polish adaptation can reproduce: replaced spend = a 300–500 PLN lawyer consultation or the fine itself; first channel = SEO on "wzór" queries; retention driver = weak (one-off); only a B2B tier for advocates would recur.

**Graveyard:** **DoNotPay** (US): started in 2015 as a parking-ticket appeal bot; the FTC charged it in September 2024 for claiming it could replace a lawyer without testing, and the final order (approved 2025-01-16, announced 2025-02-11) required **US$193,000** in relief and notices to 2021–2023 subscribers ([FTC press release, 2025-02-11](https://www.ftc.gov/news-events/news/press-releases/2025/02/ftc-finalizes-order-donotpay-prohibits-deceptive-ai-lawyer-claims-imposes-monetary-relief-requires); [accountsrecovery.net](https://www.accountsrecovery.net/2025/02/12/robot-laywer-donotpay-to-pay-193k-in-settlement-with-ftc/)). Lesson: subscription for occasional letters plus overclaiming led to churn complaints and a regulator. **LoFrayer** (IL): threatened by the bar within weeks (current status not checked).

**Scores (1–5):** L1 3 · L2 3 · L3 3 · L4 4 · L5 3 · L6 2 · L7 4 · L8 3 · L9 2 | **Weighted:** 3.1 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). The local rules base is real but public and copyable, the closest paid substitutes cost ~20 PLN and ChatGPT is free, and revenue is one letter per person, so 345 new paying users every month within a year is unlikely for a solo founder with 40 h/month. **Recommendation: do not build standalone; at most reuse the EPU sprzeciw/przedawnienie module inside a debt-related product.**
Changes vs. quick score: L5 4 → 3 (no volume data found for fines or EPU nakazy; demand is autocomplete only), L8 4 → 3 (template sites already hold the SEO), L1, L2, L3, L4, L6, L7, L9 kept; weighted 3.3 → 3.1.

**Cheapest validation test (≤1 week, ≤200 PLN):** two landing pages ("Odwołanie od opłaty dodatkowej MPK Wrocław" and "Sprzeciw od nakazu zapłaty z e-Sądu: sprawdź przedawnienie") with a free deadline/limitation check and a 29/49 PLN "buy the letter" button (pre-order, refund if not delivered); 150 PLN of Google Ads on those exact phrases; measure check-to-buy clicks.

**Kill criteria:** <3% of visitors who run the free check click "buy" at 29 PLN; or <100 checks from 150 PLN of ads (cost per check >1.5 PLN means paid acquisition cannot work at 29 PLN).

**Confidence:** medium (procedures, competitor prices and the graveyard sourced; demand volume, conversion and the non-lawyer advice rule not).

**Sources** (accessed 2026-11-05):
1. https://fortune.com/2026/02/05/lawhive-ai-law-firm-startup-series-b-venture-funding/
2. https://www.globallegalpost.com/news/uk-new-law-start-up-lawhive-secures-fresh-funding-for-us-expansion-1810357469
3. https://en.globes.co.il/en/article-1001545334
4. https://www.ftc.gov/news-events/news/press-releases/2025/02/ftc-finalizes-order-donotpay-prohibits-deceptive-ai-lawyer-claims-imposes-monetary-relief-requires (returns 404 to scripts; read via WebFetch 2026-11-05)
5. https://www.accountsrecovery.net/2025/02/12/robot-laywer-donotpay-to-pay-193k-in-settlement-with-ftc/
6. https://formularze.net/sprawy/odwolanie-mandat-bilet
7. https://warszawa19115.pl/-/oplaty-dodatkowe
8. https://warszawa19115.pl/-/parkowanie-reklamacje
9. https://www.infor.pl/prawo/prawa-konsumenta/konsument-uslugi/764903,Jak-sie-odwolac-od-oplaty-dodatkowej-ZTM.html
10. https://www.captain.legal/pl/sprawy-osobiste/sprzeciw-od-nakazu-zap-aty-wzor-pdf-i-word/
11. https://www.infor.pl/prawo/pozwy/informacje-ogolne/96961,Sprzeciw-od-nakazu-zaplaty.html
12. https://www.wonder.legal/pl/modele/reklamacja-oplaty-za-nieoplacony-postoj
13. https://www.gazetaprawna.pl/twoje-prawo/artykuly/10848117,esad-prawie-700-tys-spraw-w-ciagu-roku.html
14. https://openrouter.ai/google/gemini-2.5-flash
15. https://artificialintelligenceact.eu/annex/3/
16. Internal: [TH13 check](../../poland-check/A/TH13-consumer-legal-help-ai-law-firms.md), [shortlist notes](../shortlist-notes.md)

Coverage: 10 web searches/fetches for this write-up (DoNotPay FTC order, Lawhive funding and revenue, LoFrayer, ZTM complaint rules and fine amounts, Warsaw parking reklamacje, EPU statistics, Polish AI/template letter generators and prices). Not found: number of opłaty dodatkowe per year in any city, EPU nakazy count for 2024, any Polish AI letter generator for consumers, LoFrayer's status after the bar's ultimatum, the statutory basis for non-lawyer advice in Poland.
