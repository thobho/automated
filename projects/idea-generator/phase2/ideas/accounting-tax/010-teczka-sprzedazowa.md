# 010 — Teczka sprzedażowa (sale pack for small-business owners)

**One-liner:** The owner of a JDG or a small sp. z o.o. who wants to sell connects KSeF (or exports from inFakt/wFirma) and uploads the last statements; the agent builds a normalised P&L (owner's salary, one-offs), a valuation range from comparable Polish companies' eKRS filings, an anonymous teaser and an information memorandum, and explains the legal route (sale of *przedsiębiorstwo* under art. 55¹ KC, conversion of a JDG to a company, zarząd sukcesyjny) and the tax questions to take to an accountant. Sold per package, through listing sites and accounting offices.
**Field:** accounting-tax | **Type:** SaaS | **B2B** (owner-sellers; partner tier for listing sites and accounting offices) · shortlist id L023 (merges L026 KRS comparables)

**Western analogues:**
- **OffDeal** (US, YC): "AI-native investment bank" for small-business sell-side; **US$12M Series A led by Radical Ventures (2025-07-29), US$17M total**, founders say it has "launched over 30 sell-side M&A transactions"; closed deals, deal values and fees not disclosed ([OffDeal](https://offdeal.io/news/offdeal-series-a-funding-radical-ventures-2025)). A reported ~US$100M valuation is unconfirmed.
- **Comparables.ai** (FI): self-serve private-company comparables, claims 370M+ companies in 110+ countries; Polish KRS coverage **unverified** ([comparables.ai](https://www.comparables.ai/); TH63 check). Not signed up.
- OffDeal is a brokerage (people plus AI, success fees), not software; this idea copies only its document-generation step.

**Spread:** TH63 (finance and M&A research agents): sell-side for small firms seen only in the US (OffDeal); research tools in US/UK/FI. No CEE player ([TH63 check](../../poland-check/C/TH63-finance-ma-research-agents.md)). One country for the sell-side pattern.

**Does the Western leader already work in Poland?** No. OffDeal sells US businesses only (its site and announcement mention no other market); Comparables.ai might list Polish companies but produces no Polish legal route, no KSeF data and no Polish-language teaser. Not tried hands-on (OffDeal has no self-serve product).

**Polish adaptation, i.e. the edge:**
- **A JDG cannot be sold as an entity.** The route is a sale of the *przedsiębiorstwo* (art. 55¹ KC), a conversion into a company first, or zarząd sukcesyjny after the owner's death (2018 act) (TH63 check). Ten thousand-plus owners had registered a successor manager by the first year of the act ([money.pl, MPiT](https://www.money.pl/gielda/mpit-ponad-10-tys-przedsiebiorcow-ustanowilo-zarzadcow-sukcesyjnych-6431466225674370a.html)); a later undated e-prawnik.pl figure says 12.5k applications (search excerpt, unverified).
- **Revenue verification from KSeF and invoicing apps** (inFakt, wFirma): mandatory KSeF in 2026 makes sales invoices machine-readable; BizShop plans to verify figures this way (TH63 check).
- **Comparables from eKRS:** financial statements of sp. z o.o. are public as XML (Polish GAAP) or iXBRL (IFRS) at the Ministry of Justice's repository, but there is **no official API** and the portal blocks datacenter IPs; commercial scrapers sell access at ~US$40 per 1,000 statements ([Apify RegData](https://apify.com/regdata/poland-krs-financial-scraper); [dev.to](https://dev.to/getregdata/how-to-extract-polish-company-financial-data-with-a-single-api-call-bj)). Terms of use for bulk download not checked.
- **Tax questions** owners ask (PIT and VAT on sale of a business; autocomplete "sprzedaż firmy jednoosobowej a vat", TH63 check) must be flagged for an accountant, not answered.
A foreign team would need KSeF, eKRS parsing, Polish GAAP line items and the JDG sale law: months of work. A Polish accounting-software firm could do it faster.

**Target customer in Poland:** owners selling a running small business. **Sprzedambiznes.pl gets ~1.3k new listings a year (about double five years ago) and holds 1.6k active ones; OLX "firmy na sprzedaż" had ~316 new listings a month in 2024, +17% in 2025, a record 449 in January 2026** ([Bankier, 2026-03-24](https://www.bankier.pl/wiadomosc/Firma-z-ogloszenia-Internetowy-boom-na-gotowe-biznesy-9102769.html)). So ~5–6k listings a year on the two largest sites (estimate; overlap unknown). Many are very small (an online shop at 7.9k PLN, a beauty salon at 16k PLN in the same article). Partners: accounting offices and listing sites. CEE: CZ/SK have similar registries but different law; expansion is new work.

**Demand driver:** demographic: ageing 1990s founders without successors; up to 80,000 succession processes by 2030 (Mastercard report) and few children wanting to take over (Pekao, GUESSS), but these come from older surveys ([XYZ.pl, 2025-11-12](https://xyz.pl/przejecie-rodzinnego-biznesu-nie-dziekuje-ida-ciezkie-czasy-dla-sukcesji-w-polsce/)). Listing growth on OLX and sprzedambiznes (above) is the current, sourced signal. Technological: KSeF makes verified revenue cheap.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Sprzedambiznes.pl (since 2011) | marketplace for businesses for sale | listing fees, not found | no valuation or document generation |
| BizShop (2026) | structured listing pages for small offline firms, plans KSeF/wFirma/inFakt verification | first listings free (early access) ([Product Hunt](https://www.producthunt.com/products/bizshop)) | no AI described; closest future competitor |
| OLX | classified listings | listing fees | free-text ads |
| Brokers and M&A boutiques (e.g. Marktlink Warsaw) | human sell-side | success fees (typically a % of price, not checked for PL) | serve mid-market, not 50k-PLN salons |
| Accounting offices | prepare figures informally | hourly or not charged | no teaser/IM, no comparables |
| ChatGPT | drafts a teaser from typed figures | free / 20 USD | no verified data, no comparables, no legal route |

**Evidence of Polish demand:** listing growth (above); autocomplete "sprzedaż firmy" → "jednoosobowej", "z pracownikami", "a podatek dochodowy"; "wycena firmy" → "kalkulator", "do sprzedaży", "online" (TH63 check). No evidence that small sellers pay for preparation; the closest proxy is broker fees in larger deals.

**MVP scope (≤6 weeks):**
1. Inputs: KSeF invoice export or inFakt/wFirma CSV, last 2–3 years of statements (PDF or eKRS XML), a 15-question owner interview.
2. Normalised P&L in code (rules for owner's pay, ZUS, one-offs flagged by the LLM, confirmed by the user).
3. Valuation range: SDE/EBITDA multiple bands per PKD from a seeded set of ~2,000 parsed eKRS statements (bought, not scraped, to start), plus a clear "indicative, not a wycena by a rzeczoznawca" label.
4. Generated teaser (1 page, anonymised) and IM (8–12 pages) in Polish, every number traced to an input row; legal-route explainer from a fixed decision tree.
5. Tests: fixture companies (inputs → expected normalised P&L and multiples), numeric checks that every figure in the IM matches the model.

**Monetization:** 399 PLN "teczka" (teaser + valuation range), 999 PLN with IM and legal route; partner price for listing sites and accounting offices (resell with margin). Optional L026 module: comparables report per PKD for valuers and advisers, 149 PLN per report (unproven). **Unit economics:** one package ≈ 200k input / 30k output tokens (statements, invoices summary, IM generation, two revisions); on Gemini 2.5 Pro (US$1.25 / US$10 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-pro), accessed 2026-11-05) ≈ US$0.55; eKRS data ~US$0.04 per statement; payment fees ~2%. Gross margin >95%. **Volume needed:** 10k PLN MRR ≈ 10–25 packages a month, i.e. 2–5% of the ~480 listings a month on the two largest sites; but packages do not recur.

**Distribution, first 10 customers:** offer sprzedambiznes.pl and BizShop a free "verified teczka" for their next 20 sellers in exchange for a badge on the listing; 10 accounting offices in one city with ageing clients (via their local SKwP branch); direct outreach to OLX sellers whose ads lack figures.

**Regulation:** AI Act: not high-risk (business valuation is not in [Annex III](https://artificialintelligenceact.eu/annex/3/); credit scoring of natural persons is, and does not apply). Not investment advice and not brokerage: the product produces the seller's own documents and does not intermediate the deal (no KNF licence; the founder will not take success fees). Liability: an IM with wrong figures can ground buyer claims against the seller; every number must trace to a source document and the seller signs off. RODO: employee data in statements; EU hosting.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | A listing site sells the pack as a paid upsell, giving a ready flow of sellers (listings growing fast, Bankier) | M | H | sprzedambiznes.pl or BizShop agrees to a 20-seller pilot |
| O2 | Accounting offices resell it to clients who retire, earning a margin | M | M | 3 of 10 offices contacted name a client who wants to sell this year |
| O3 | KSeF-verified revenue becomes a trust badge that buyers ask for | L | M | buyers on a pilot listing ask for the verification report |
| O4 | The L026 comparables report sells to valuers, brokers and banks as a recurring subscription | M | M | 2 brokers pay for 3 reports each in month 2 |
| O5 | Rising listing volume (OLX record January 2026) keeps the seller pool growing | H | L | OLX monthly listings stay above 400 |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Most sellers are micro firms priced at 10–100k PLN who will not pay 399–999 PLN for documents | H | H | <2% of contacted OLX sellers accept even a 399 PLN offer |
| R2 | Owners sell through trust (accountant, family, competitor) and never buy online | H | M | partners refer no clients within 2 months |
| R3 | A wrong figure in a generated IM leads to a buyer dispute and reputational damage | M | H | sellers repeatedly correct normalisation in beta |
| R4 | eKRS access (no API, WAF blocks datacenter IPs) breaks the comparables pipeline or breaches terms | M | M | the paid data vendor changes price or stops |
| R5 | BizShop or a listing site adds its own AI teaser for free | M | M | AI features announced on BizShop's page |

O sum 6+4+2+4+3 = 19; R sum 9+6+6+4+4 = 29. R − O = 10 ≥ 6, and R1 is H×H (the 399 PLN tier only partly mitigates it) → **band down one** (rule §4.3).

**Success signals:**
- Western analogue durable signals: OffDeal replaces a broker's work (signal 1) on a high-value, owned problem (signal 2) and raised a follow-on round within 10 months ([OffDeal](https://offdeal.io/news/offdeal-series-a-funding-radical-ventures-2025)); no retention, expansion or revenue figures (signals 3, 4 absent). Durability score ~3 → **unproven**; one country → L2 capped low.
- Hype warnings: none found, but traction is "launched transactions", not closed deals.
- Polish adaptation can reproduce: replaced spend = accountant hours and part of a broker's fee; first channel = listing sites and accounting offices; retention driver = none for sellers (one-off); only the comparables report (L026) could recur.

**Graveyard:** none found in this pass for AI small-business sell-side (the pattern is two years old). Not searched: older US online business-brokerage startups.

**Scores (1–5):** L1 4 · L2 2 · L3 4 · L4 4 · L5 3 · L6 2 · L7 3 · L8 2 · L9 3 | **Weighted:** 3.1 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). The gap and the moat are real (no Polish AI product, KSeF + eKRS + JDG sale law), and listing volume is sourced and growing, but most Polish sellers are micro firms that will not pay hundreds of PLN for documents and each customer buys once, so 10k PLN MRR depends on a listing-site partnership that does not exist yet. **Recommendation: test the listing-site partnership before writing code; if it fails, drop.**
Changes vs. quick score: L7 4 → 3 (eKRS has no API and blocks datacenter IPs; IM quality is subjective to test), L1, L2, L3, L4, L5, L6, L8, L9 kept; weighted 3.3 → 3.1.

**Cheapest validation test (≤1 week, ≤200 PLN):** hand-make 3 teasers + valuation ranges for real OLX sellers (with consent, using their figures and ChatGPT + a spreadsheet) and offer them free; ask each seller whether they would have paid 399 PLN; in parallel, pitch sprzedambiznes.pl and BizShop a co-branded pilot. Cost: time only.

**Kill criteria:** neither listing site agrees to a pilot within 3 weeks; or 0 of 20 contacted sellers willing to pay 399 PLN after seeing a sample.

**Confidence:** medium-low (listing volumes and eKRS access sourced; seller willingness to pay, succession numbers and listing fees not).

**Sources** (accessed 2026-11-05):
1. https://offdeal.io/news/offdeal-series-a-funding-radical-ventures-2025
2. https://www.comparables.ai/
3. https://www.bankier.pl/wiadomosc/Firma-z-ogloszenia-Internetowy-boom-na-gotowe-biznesy-9102769.html
4. https://www.money.pl/gielda/mpit-ponad-10-tys-przedsiebiorcow-ustanowilo-zarzadcow-sukcesyjnych-6431466225674370a.html
5. https://apify.com/regdata/poland-krs-financial-scraper
6. https://dev.to/getregdata/how-to-extract-polish-company-financial-data-with-a-single-api-call-bj
7. https://xyz.pl/przejecie-rodzinnego-biznesu-nie-dziekuje-ida-ciezkie-czasy-dla-sukcesji-w-polsce/
8. https://www.producthunt.com/products/bizshop
9. https://openrouter.ai/google/gemini-2.5-pro
10. https://artificialintelligenceact.eu/annex/3/
11. Internal: [TH63 check](../../poland-check/C/TH63-finance-ma-research-agents.md)

Coverage: 6 web searches/fetches for this write-up plus the TH63 check's sources (OffDeal funding and traction, Polish listing volumes, zarząd sukcesyjny counts, sprzedambiznes prices, eKRS bulk access). Not found: sprzedambiznes.pl listing fees, a current zarząd sukcesyjny count, Polish broker fee levels for small deals, any graveyard case, Comparables.ai's Polish coverage.
