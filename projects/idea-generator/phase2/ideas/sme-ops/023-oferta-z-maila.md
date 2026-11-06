# 023 — "Oferta z maila": RFQ-to-quote and order entry for technical wholesalers

**One-liner:** For a Polish technical wholesaler (electrical, HVAC, plumbing, fasteners) on Subiekt nexo/GT or Comarch Optima, an agent reads the customer's e-mailed enquiry or order (PDF, Excel, photo of a handwritten list, free text such as "kabel YDYp 3x2,5 100 m"), matches each line to the wholesaler's own indeks and stock, applies the customer's price group, flags substitutes and missing items, and drafts a priced quote or a sales order for the salesperson to approve and send (merged L132 order entry).
**Field:** sme-ops | **Type:** SaaS (web + ERP connector) | **B2B** · shortlist id L131 (merges L132)

**Western analogues:**
- **Parspec** (US, 2021): AI quoting, submittals and product selection for MEP distributors; **US$11.5M seed (2024-02)** and **US$20M Series A led by Threshold (2025-07), US$31.5M total**; works with **4 of the 5 largest US electrical distributors**, reports **4× revenue growth in 12 months**, usage-based pricing per document ([Distribution Strategy 2025-07](https://distributionstrategy.com/2025/07/parspec-raises-20-million-to-bring-ai-automation-to-construction-distributors/); [Business Wire 2024-02-27](https://www.businesswire.com/news/home/20240227657482/en/Parspec-Announces-11.5M-Seed-Funding-led-by-Innovation-Endeavors-bringing-the-power-of-AI-to-construction-product-procurement), accessed 2026-11-06).
- **Mercura** (DE, Munich): quote and order automation for technical sales in industrial wholesale and construction; **seed of €1.8M+ (oversubscribed), reported 2026-01** ([Munich Startup](https://www.munich-startup.de/en/news/mercura-secures-e1-8-million), accessed 2026-11-06).
- **Duvo** (CZ): retail back-office agents across SAP, portals and e-mail, US$15M seed 2025-12 (R6 catalogue); **Definic** (SK): procurement offer benchmarking, €2.5M seed 2026-06 (R6 catalogue). Adjacent, not wholesale quoting.

**Spread:** TH61: US, DE, CZ, SK, EE (Pactum), JP (R1, R3, R4, R6, R7), 2024–2026. Wholesale-quoting specifically: US (Parspec) and DE (Mercura).

**Does the Western leader already work in Poland?** No Polish site, language or ERP connector found for Parspec (US catalogues, US distributors) or Mercura (DACH focus) (TH61 check; Mercura demo-only, not tried). Comarch ERP has a classic "porównanie ofert zakupu" module for the buyer side, not AI reading of customer enquiries ([Comarch help](https://pomoc.comarch.pl/cee/index.php/documentation/instrukcja-porownanie-ofert-zakupu/), via TH61). One Polish search for AI quoting with Subiekt found only e-commerce integrators (BaseLinker/Base.com partners such as e-merge, 1,380 PLN net/year for order and stock sync) ([Base.com](https://base.com/pl-PL/integracje/subiekt_nexo_pro/dextrum/), search excerpt, accessed 2026-11-06).

**Polish adaptation, i.e. the edge:**
- **ERP integration:** InsERT nexo serves "over 300 thousand firms" with nearly 600k licences (undated figure, [Benchmark.pl](https://www.benchmark.pl/aktualnosci/nowe-systemy-dla-firm-msp-z-rodziny-insert-nexo.html), accessed 2026-11-06); Subiekt GT Sfera allows extensions; nexo has extension points; whether Subiekt nexo PRO ships an SDK was not confirmed. Many installs are on-premise Windows ([local-moats](../../research/poland/local-moats.md) M44, M41).
- **Polish technical vocabulary and shorthand:** cable types (YDYp, YKY, OMY), Polish norms, local brand names, EAN vs. the wholesaler's own indeks; netto/brutto, VAT rates, payment terms, biała lista check for a new customer (M04), the invoice later in KSeF (M01).
- Industry structure: family-owned regional wholesalers with inside-sales desks; customers are installers who send lists by e-mail, phone photos or WhatsApp.
A foreign entrant would need Polish ERP connectors and Polish product vocabulary; both take months.

**Target customer in Poland:** regional technical wholesalers with 3–30 salespeople. **Count not found** (no association membership or GUS PKD 46.x count read; unverified). Buyer: owner or sales director. CEE: CZ/SK wholesalers use Pohoda/Money S3, a new connector each.

**Demand driver:** DD7 labour costs and shortages (D39); electrical-wholesale sales jobs advertised at **6,000–12,000 PLN gross/month** (EL-BAL, Warsaw, [pracodawcy.pracuj.pl](https://pracodawcy.pracuj.pl/company/1074156746), search excerpt, accessed 2026-11-06); a Warsaw customer-service/warehouse role lists "preparing orders and price quotes" at ~4,800–4,900 PLN gross ([pracuj.pl ad](https://www.pracuj.pl/praca/pracownik-ds-obslugi-klienta-magazynier-warszawa-aleja-krakowska-45,oferta,1004966178), excerpt). No regulatory trigger.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Comarch ERP purchase-offer comparison | buyer-side comparison inside ERP | in licence | not customer RFQ reading |
| Base.com / BaseLinker integrators for Subiekt | e-commerce order and stock sync | e.g. 1,380 PLN net/year | marketplace orders, not e-mailed lists |
| B2B e-shops of wholesalers (own platforms) | installers order online | varies | installers still e-mail lists and photos |
| Microsoft Copilot in Outlook/Excel, ChatGPT | ad hoc extraction | ~30 USD/user or free | no catalogue/stock/price-group match |
| Mimira, Minerva (PL) | AI for public tenders | not found | bid side, not wholesale quotes |

**Evidence of Polish demand:** weak. Autocomplete "ai zapytania ofertowe" → none (TH61); job ads show quoting is a named job step in wholesale customer service (above). No wholesaler quote about wanting automation was found.

**MVP scope (≤6 weeks):**
1. Mailbox connector (IMAP/Microsoft 365) → enquiry classifier → line extraction from PDF/Excel/photo/text into a JSON schema.
2. Catalogue import from Subiekt/Optima (CSV export first, then a Sfera/nexo connector) with embeddings over indeks names, EAN and brand codes; customer-specific alias memory.
3. Matching with confidence scores, stock and price group; a review screen where the salesperson fixes lines (corrections train the alias memory).
4. Output: quote PDF in the wholesaler's template, or a ZK/ZD document pushed back to the ERP (CSV/EDI++ import first).
5. Tests: 200 anonymised real enquiries per pilot with golden line matches; accuracy dashboard.

**Monetization:** 499 PLN net/month per wholesaler up to 3 seats + 1 PLN per processed enquiry above 500/month; setup 1,500 PLN. Budget line: inside-sales hours (one quote ≈ 15–60 min, estimate, unverified). **Unit economics:** a 50-line enquiry ≈ 10k tokens to extract + ~2k tokens per line to rerank candidates ≈ 110k input / 10k output on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.06; 300 enquiries/month ≈ US$18 (~75 PLN); embeddings and hosting ~40 PLN. Gross margin ~75% at 499 PLN. **Customer count:** 10k PLN MRR ≈ 20 wholesalers; plausible, but the market size is unverified, so the 20× check cannot be confirmed.

**Distribution, first 10 customers:** direct calls and visits to regional electrical and HVAC wholesalers (lists from Google Maps and CEIDG/KRS by PKD 46.43/46.73/46.74); InsERT and Comarch resellers as partners (they sell and install the ERP); trade fairs (not checked).

**Regulation:** AI Act: minimal risk (not Annex III) ([Annex III](https://artificialintelligenceact.eu/annex/3/)). RODO: customer e-mails with contact data; processor agreement; EU hosting. Commercial liability for quoted prices stays with the wholesaler (human approval before sending).

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Only ~20 wholesalers are needed and each has a visible cost (salespeople at 6–12k PLN gross) | H | M | 5 of 20 called wholesalers agree to send 50 sample enquiries |
| O2 | Usage-based pricing grows with volume, as Parspec's per-document model does | M | M | pilot volume ≥300 enquiries/month |
| O3 | One Subiekt/Optima connector serves many wholesalers (300k firms on nexo overall) | M | M | the second pilot needs <2 days of connector work |
| O4 | Customer-specific alias memory compounds, raising switching costs | M | M | match accuracy rises ≥10 points after a month |
| O5 | CEE entrants (Duvo, Definic) and Mercura have not entered Poland, leaving first-mover time | L | M | no Polish job ads from them in 6 months |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Owners do not see quoting as a problem worth paying for: demand is unproven and buyers do not search | M | H | <3 of 20 wholesalers agree to a pilot |
| R2 | Family-owned wholesalers buy slowly and want visits; the founder's 40 h/month stretches the cycle | H | M | first paid contract takes >3 months |
| R3 | On-premise Subiekt/Optima installs make each deployment custom, adding support work | M | M | each pilot needs remote-desktop sessions |
| R4 | Wrong matches on technical products (cable cross-section, IP rating) produce wrong quotes and lost trust | M | H | line accuracy <90% after tuning |
| R5 | InsERT, Comarch or BaseLinker add AI enquiry reading to their own products | M | M | release notes mention AI order import |
| R6 | Copilot in Outlook plus an Excel lookup is "good enough" for small desks | M | L | prospects show a Copilot workflow |

O sum 6+4+4+4+2 = 20; R sum 6+6+4+6+4+2 = 28. R − O = 8 → **down one band** (rule §4.3); no H×H risk.

**Success signals:**
- Western analogue durable signals: replaces inside-sales hours (signal 1), daily problem with an owner (signal 2), 4× revenue growth with the largest distributors as customers (expansion-like; no NRR, signal 4 not counted), value-based per-document pricing (signal 7), ERP and catalogue integration (signal 8) ([Distribution Strategy](https://distributionstrategy.com/2025/07/parspec-raises-20-million-to-bring-ai-automation-to-construction-distributors/)). Durability score ~4–5 → **promising**.
- Hype warnings: none found.
- Polish adaptation can reproduce: replaced spend = salesperson hours on quotes; first channel = direct outreach and ERP resellers; retention driver = alias memory and ERP connector.

**Graveyard:** none found for wholesale quoting.

**Scores (1–5):** L1 4 · L2 4 · L3 4 · L4 3 · L5 2 · L6 3 · L7 3 · L8 2 · L9 3 | **Weighted:** 3.1 / 5 | **Chance band:** score → 5–15%; O 20, R 28, R − O = 8 → **<5%**. The gap is clean and the US/DE analogues show durable B2B pull, but Polish demand is unproven, the market size is unknown, and selling to conservative family wholesalers with on-premise ERPs is slow for a 40 h/month founder. Of this batch it has the best gap and analogue; a positive outreach test would justify a rescore to 5–15%.
Changes vs. quick score: L2 3 → 4 (Parspec Series A, 4× revenue, top US distributors), others kept; weighted 3.0 → 3.1.

**Cheapest validation test (≤1 week, ≤200 PLN):** call 20 regional electrical/HVAC wholesalers; ask how many e-mailed enquiries they get a day and how long a quote takes; ask 5 to send 50 anonymised enquiries plus a catalogue export; run them through an LLM prototype and show the matched quotes.

**Kill criteria:** <3 wholesalers send samples; or match accuracy <85% on samples; or quotes take <10 minutes today.

**Confidence:** medium-low (Western traction and job-step evidence sourced; market size and Polish willingness to pay not found).

**Devil's advocate (T24, 2026-11-06):**
- *The Western leader is closer than "DACH focus" suggests.* Mercura's seed release (re-fetched 2026-11-06) says the round was led by TQ Ventures, SignalFire and Y Combinator, the company has been profitable from the start, targets double-digit million euro revenue for 2026, has customers in Europe and the US (Bauder, Reisser, Siteco, BME Group), works with existing ERP/CRM systems and will use the money to grow internationally ([Munich Startup, 2026-01-07](https://www.munich-startup.de/en/news/mercura-secures-e1-8-million)). Poland is not named, but a profitable, YC-backed team selling exactly this to electrical and building-technology wholesalers can add a Polish catalogue faster than a solo founder can build ERP connectors. "Localizes in 12 months" is plausible, not likely: no Polish page or job ad found.
- *Generic e-mail-to-order agents already sell in Polish.* Virtual Workforce (Rotterdam) publishes Polish pages for AI agents that turn customer order e-mails into sales orders, for SAP, Dynamics/Business Central and QuickBooks, with a 14-day trial ([virtualworkforce.ai/pl](https://virtualworkforce.ai/pl/konwertuj-e-maile-zamowien-klientow-na-zamowienia-sprzedazy/), fetched 2026-11-06); parsers such as Parseur do rule-based extraction ([Parseur PL](https://parseur.com/pl/blog/zastosowania-parsera-e-mail), search result). They miss Subiekt/Optima and Polish technical vocabulary, which is the real moat (L4 3), but they cover the larger wholesalers on SAP or Dynamics.
- *ChatGPT will absorb it.* Copilot in Outlook can extract a list into Excel; the hard part is matching "YDYp 3x2,5" to the wholesaler's own indeks and price group, which general assistants cannot do without the catalogue. This is the strongest defence in the batch.
- *Polish customers won't pay this, or won't buy it quickly.* Demand is still unproven (no wholesaler quote, no searches), the number of target wholesalers is still unknown, and family firms with on-premise Subiekt buy through resellers and visits. The 499 PLN price is reasonable against a 6–12k PLN salesperson, but nobody has been asked.
- *Second competitor search (2026-11-06):* "AI automatyczne wprowadzanie zamówień z e-maili hurtownia ... Subiekt Comarch agent", "InsERT nexo sztuczna inteligencja AI Subiekt 2026": no Polish product and no InsERT AI feature found; Comarch's 2026 agents (see 016) cover bank matching, collections and KSeF checks, not customer enquiries (ITwiz). Comarch e-Sklep order import is e-commerce, not e-mail.
- *Success signals.* Parspec (Series A, 4× revenue, top US distributors) and Mercura (profitable, double-digit million target) are durable, value-priced and integration-heavy; no hype warning. L2 4 holds.
- *Opportunity/risk lists.* O1 "5 of 20 wholesalers agree" rated H with no evidence of willingness → M×M. O5 (Western entrants absent) is honest at L. Risks independent and fair; R5 could add Mercura, but as M×M it does not change the sums.

**Review changes (T24, 2026-11-06):** scores unchanged (L1 4 · L2 4 · L3 4 · L4 3 · L5 2 · L6 3 · L7 3 · L8 2 · L9 3; weighted **3.1**; shortlist quick 3.0 replaced). O1 H×M → M×M. §4: O 4+4+4+4+2 = 18, R 28, R − O = 10 → down one → **<5%** (unchanged). Not rejected: still the cleanest gap of the batch; the 20-call outreach test decides L5, and a Mercura Polish page or ad would be a kill signal.

**Sources** (accessed 2026-11-06 unless noted):
1. https://distributionstrategy.com/2025/07/parspec-raises-20-million-to-bring-ai-automation-to-construction-distributors/
2. https://www.businesswire.com/news/home/20240227657482/en/Parspec-Announces-11.5M-Seed-Funding-led-by-Innovation-Endeavors-bringing-the-power-of-AI-to-construction-product-procurement
3. https://www.munich-startup.de/en/news/mercura-secures-e1-8-million
4. https://pomoc.comarch.pl/cee/index.php/documentation/instrukcja-porownanie-ofert-zakupu/ (accessed 2026-11-03)
5. https://base.com/pl-PL/integracje/subiekt_nexo_pro/dextrum/
6. https://www.benchmark.pl/aktualnosci/nowe-systemy-dla-firm-msp-z-rodziny-insert-nexo.html
7. https://pracodawcy.pracuj.pl/company/1074156746
8. https://www.pracuj.pl/praca/pracownik-ds-obslugi-klienta-magazynier-warszawa-aleja-krakowska-45,oferta,1004966178
9. https://openrouter.ai/google/gemini-2.5-flash (accessed 2026-11-05)
10. https://artificialintelligenceact.eu/annex/3/
11. Internal: [TH61 check](../../poland-check/A/TH61-procurement-rfq-order-handling.md), R6 catalogue rows (Duvo, Definic)
12. https://www.munich-startup.de/en/news/mercura-secures-e1-8-million (2026-11-06, T24, re-fetched)
13. https://virtualworkforce.ai/pl/konwertuj-e-maile-zamowien-klientow-na-zamowienia-sprzedazy/ (2026-11-06, T24)
14. https://parseur.com/pl/blog/zastosowania-parsera-e-mail (2026-11-06, T24, search result)
15. https://itwiz.pl/comarch-wpuszcza-ai-do-biur-rachunkowych/ (2026-11-06, T24)

Coverage: 6 web searches for this write-up (Mercura, Parspec, Polish AI quoting with Subiekt, wholesaler associations, Subiekt user base, wholesale job ads). Not found: number of technical wholesalers in Poland, a Polish wholesaler association's membership, Subiekt nexo SDK confirmation, any Polish AI quoting product.
