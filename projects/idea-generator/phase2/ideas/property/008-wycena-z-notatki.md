# 008 — "Wycena z notatki": voice note and photos → priced offer for heat-pump and PV installers

**One-liner:** After a site visit the installer records a voice note and sends a few photos (boiler room, roof, fuse box); the app drafts an itemised offer from the installer's own price list with the right VAT rate (8% inside the envelope of a house ≤300 m², 23% outside it), a Czyste Powietrze checklist (ZUM-listed device, documents), and sends it as PDF/SMS to the client; on acceptance it creates the invoice in Fakturownia or inFakt.
**Field:** property (home installation trades) | **Type:** SaaS (mobile-first web) | **B2B** · shortlist id L097 (merges L098–L100: general renovation crews, electricians, plumbers)

**Western analogues:**
- **plancraft** (DE, Hamburg): offer-to-invoice software for Handwerk; **€38M Series B in August 2025** led by Headline, total funding >€50M, money earmarked for "voice-first" AI and expansion to AT, NL, IT ([tech.eu](https://tech.eu/2025/08/13/plancraft-raises-eur38m-series-b-to-drive-ai-transformation-in-european-construction/)); >20,000 customers in 11 countries per its investor HTGF ([HTGF](https://www.htgf.de/en/plancraft-series-b/)); €12M Series A in June 2024.
- **Handoff** (US, Austin): AI estimates, proposals and invoicing for residential remodelers; **US$5.8M strategic round (June 2025)** led by Nemetschek and Masco; says 40k+ contractors have used it ([Handoff blog](https://www.handoff.ai/blog/handoff-raises-5-8m-for-residential-construction); [Nemetschek release](https://www.mynewsdesk.com/nemetschek-ag/pressreleases/nemetschek-group-announces-strategic-investment-in-handoff-an-ai-platform-for-contractors-3391479)).
- **autarc** (DE, heat-pump installers), **Installer** (NO), **Payaca** (UK, heat pumps/PV/EV chargers), Avoca and Elyos AI (AI call answering for trades): named in TH27; traction not re-verified here (unverified).

**Spread:** TH27 trades front office in DE, AT, UK, NO, US (R1, R2, R3, R4); plancraft sells in 11 countries. No CEE analogue in R6 ([TH27 check](../../poland-check/B/TH27-trades-home-services-front-office.md)).

**Does the Western leader already work in Poland?** No. plancraft lists DE, AT, UK, NL, IT, ES locales and no Polish one (TH27 check); its 2025 expansion plan names AT, NL and IT, not CEE (tech.eu). Handoff is US-only. Not tried hands-on (no Polish option, so no trial was started). **For the PV segment, though, international design-and-proposal tools already serve Poland:** OpenSolar's core app is free and Polish is one of 13 proposal languages (manual template translation); PV\*SOL premium has a Polish interface at €845/user/year ([SurgePV comparison, updated 2026-11-03](https://www.surgepv.com/best-solar-software/poland), a vendor's own list).

**Polish adaptation, i.e. the edge:**
- **VAT rate per job:** 8% under art. 41 ust. 12 of the VAT act only for work inside the envelope (bryła) of a residential building within "budownictwo objęte społecznym programem mieszkaniowym" (houses ≤300 m², flats ≤150 m²), 23% outside it (e.g. a heat-pump unit on the ground in the garden); KIS interpretations 2019 and 2023 ([poradnikprzedsiebiorcy.pl](https://poradnikprzedsiebiorcy.pl/-montaz-pompy-ciepla-jaka-stawka-podatku-vat)). The rate depends on facts the installer sees on site, which is exactly what the voice note/photo step captures.
- **Czyste Powietrze:** relaunched 31 March 2025 with operators who check the contractor before an advance payment; heat pumps must be on the ZUM list, now only with full lab tests from EU/EFTA labs; air-to-air pumps removed ([bezprawnik.pl](https://bezprawnik.pl/program-czyste-powietrze-2025-wraca-na-nowych-zasadach/); TH27 check). Only about one in five heating heat pumps was subsidised in 2025 (PORT PC, search excerpt).
- **Invoicing stack:** most small firms invoice in Fakturownia/inFakt/wFirma; Fakturownia's API is public with token auth, VAT invoices, proformas and "estimate" documents ([Fakturownia API](https://github.com/fakturownia/api)); KSeF for B2B jobs (M01).
- Polish product names, wholesalers' price lists, client habits (phone + WhatsApp/Messenger photos, BLIK deposits). This is weeks of learning, not months: a determined foreign entrant (plancraft) could add it.

**Target customer in Poland:**
- Heat-pump and PV installation firms and one-person crews. UDT reported close to **9,000 certificates for OZE installers** in its 1/2023 bulletin ([UDT INSPEKTOR 1/2023](https://www.udt.gov.pl/images/biuro-prasowe/files/pdf/INSPEKTOR_1_2023_Instalacje_Fotowoltaiczne_WCAG.pdf)); number of firms not found (certificates ≠ firms; many crews work uncertified).
- Market volume: **72.1 thousand heat pumps sold in to wholesalers and installers in 2025**, central-heating units +~20% y/y in Q1 2026, 2026 forecast ~83.4 thousand ([gramwzielone.pl, PORT PC, 2026-04-29](https://www.gramwzielone.pl/pompy-ciepla/20358484/polacy-kupuja-wiecej-pomp-ciepla-nadzieja-na-przelamanie-impasu)), after falls of ~40% in 2023 and ~35% in 2024 (search excerpt).
- Later: renovation crews, electricians, plumbers (L099); CEE: CZ/SK have similar subsidy programmes (Nová zelená úsporám, not checked).

**Demand driver:** DD7 labour shortage (installers on the shortage list, so crews are overbooked and admin time is the bottleneck); the heat-pump market is recovering in 2026; Czyste Powietrze paperwork got heavier in 2025 (operator checks, ZUM). KSeF obligation for B2B invoices pushes firms onto e-invoicing software.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Fakturownia / inFakt / wFirma | invoices, proformas, simple estimate documents | subscription | no voice/photo drafting, no item list from a site visit ([Fakturownia API](https://github.com/fakturownia/api)) |
| OpenSolar, PV\*SOL, PVsyst, SurgePV | PV design, yield and proposal | OpenSolar free; PV\*SOL €845/yr | PV only; Polish net-billing and VAT not built in per the comparison ([SurgePV](https://www.surgepv.com/best-solar-software/poland)) |
| ecoPartner | PV/heat-pump quoting app with CRM for sellers, "quote in 2 minutes" | not stated | 2021 sponsored article; current status unknown ([GLOBEnergia](https://globenergia.pl/ecopartner-rewolucyjna-aplikacja-wkrotce-zarobia-na-niej-nie-tylko-sprzedawcy-fotowoltaiki/)) |
| "Kalkulator Kosztorysu" app, Norma PRO and other kosztorys software | price-list quotes; formal KNR estimates | not found / licence | no AI; formal estimates are for tenders, not crews (TH27) |
| Manufacturers' selection tools and configurators | heat-pump sizing | free | brand-locked, no offer/invoice |
| ChatGPT + Word/Excel | ad hoc | 0–20 USD | no price list memory, VAT rule, or invoice link |

**Evidence of Polish demand:** weak. Autocomplete for "program do ofert dla instalatorów" and "program do wyceny remontów" returns nothing; one Elektroda thread discusses an AI quoting tool for electricians at idea stage (TH27 check). Tradespeople do not search for software, so demand must be tested by outreach, not search.

**MVP scope (≤6 weeks):**
1. Price-list import (CSV/Excel from the installer or a wholesaler).
2. Voice note (Polish ASR) + up to 5 photos → structured job facts (building type, area, envelope vs outside, existing heating) → line items from the price list, via LLM with a JSON schema; VAT rate decided by deterministic rules from the facts.
3. Offer PDF + SMS/e-mail link with "accept" button; Czyste Powietrze checklist (ZUM device check against the published list).
4. On acceptance: proforma/invoice in Fakturownia via API (inFakt in v2).
5. Tests: 40 recorded site-visit notes with hand-made offers as golden files; VAT rule table as fixtures.

**Monetization:** 99 PLN/month per firm (1 user, unlimited offers), 149 PLN for 3 users; VAT invoice, card or BLIK. **Unit economics:** per offer ≈ 2 min of audio + 5 photos + price list ≈ 20k input / 3k output tokens; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.015 for text and images; audio priced separately (estimate ≤US$0.02). ~US$0.03 per offer; at 60 offers/month ≈ US$2 (≈8 PLN) per firm. Gross margin ~90%. **Customer count:** 10k PLN MRR = ~101 firms at 99 PLN; the reachable pool (~9,000 certified installers plus general trades) is above 20× that, so the sanity check in criteria §3 is met (pool size is an estimate).

**Distribution, first 10 customers:** wholesalers (hurtownie instalacyjne) and heat-pump manufacturers' installer programmes as partners (free tool for their installers, price list pre-loaded); installer Facebook groups; outbound to firms on manufacturers' "find an installer" maps. No evidence yet that any partner wants this.

**Regulation:** AI Act: not high-risk ([Annex III](https://artificialintelligenceact.eu/annex/3/)). VAT: the app suggests the rate, the installer confirms; a wrong 8% rate is the installer's tax risk, so the rule must be conservative and explained. RODO: client addresses and house photos; EU hosting. KSeF: invoices issued through Fakturownia/inFakt, which handle the KSeF link.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | A wholesaler or heat-pump manufacturer distributes it to its installer network | L | H | one partner agrees to a pilot with 20 installers |
| O2 | Heat-pump market recovery in 2026 (+~20% Q1) means more offers per crew and less time for admin | M | M | PORT PC H1/full-year 2026 growth confirmed |
| O3 | Extension to renovation crews, electricians, plumbers (L099) widens the pool many times | M | M | the same flow works on 10 renovation notes without new code |
| O4 | Offer-acceptance data shows which items and prices win, a useful benchmark for installers and wholesalers | L | M | 50 firms with 6 months of offers |
| O5 | KSeF adoption pushes small firms to pick an invoicing stack in 2026, an opening for a bundled offer-to-invoice tool | M | L | installers asking about KSeF in groups |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Crews keep quoting by phone and Excel; no organic channel, paid acquisition too costly at 99 PLN/month | H | H | <5% reply rate to outbound; trial users stop after one offer |
| R2 | Fakturownia or inFakt add an AI offer generator to their existing customer base | M | H | AI features in their release notes |
| R3 | plancraft adds Polish (it already runs in 11 countries and raised €38M for expansion) | L | H | Polish job posts or locale |
| R4 | Heat-pump demand swings with Czyste Powietrze rules, cutting installers' willingness to pay | M | M | programme suspension or rule change like Nov 2024 |
| R5 | Wrong VAT rate or wrong item in an offer damages the installer's trust | M | M | >10% of golden-file offers need manual fixes |

O sum 3+4+4+2+2 = 15; R sum 9+6+3+4+4 = 26. R − O = 11 ≥ 6, and R1 is H×H with no MVP mitigation beyond outreach → **band down one** (criteria §4.3).

**Success signals:**
- Western analogue durable signals: plancraft replaces office hours of Handwerk firms (budget line = the owner's evenings or an office assistant), raised a Series A and a larger Series B 14 months apart, and sells in 11 countries ([tech.eu](https://tech.eu/2025/08/13/plancraft-raises-eur38m-series-b-to-drive-ai-transformation-in-european-construction/), [HTGF](https://www.htgf.de/en/plancraft-series-b/)); Handoff has strategic investors from the industry (Nemetschek, Masco), i.e. a distribution path through incumbents. No public retention or NRR found.
- Hype warnings: none found; plancraft's base predates its AI features, so the AI-driven part of traction is not separable.
- Polish adaptation can reproduce: replaced spend = owner's admin hours per offer (not measured in PL); first channel = wholesaler/manufacturer partners (unproven); retention driver = stored price list and offer history, invoicing link.

**Graveyard:** no shutdown in this theme found in one search; small quoting apps for trades are numerous and some are listed for sale on micro-acquisition sites with tiny revenue (search excerpt, not verified), which suggests the self-serve B2C-like channel is hard.

**Scores (1–5):** L1 4 · L2 3 · L3 4 · L4 3 · L5 3 · L6 3 · L7 3 · L8 2 · L9 2 | **Weighted:** 3.1 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). The gap is real for heat-pump and general trades (plancraft has no Polish locale, no Polish AI tool found) and the economics work at 99 PLN, but the localisation is learnable in weeks, Polish invoicing vendors sit on the same customers, and there is no evidence that crews look for or adopt such tools without a wholesaler or manufacturer partner. **Recommendation: only worth building if a partner (wholesaler or manufacturer) commits to a pilot first.**
Changes vs. quick score: L4 4 → 3 (VAT rule, ZUM and Fakturownia API are weeks of work), L7 4 → 3 (open-ended voice input is hard to test), L8 2 kept, L3 4 kept (PV tools exist, heat-pump/trades gap open); weighted 3.3 → 3.1.

**Cheapest validation test (≤1 week, ≤200 PLN):** record 5 real site-visit notes with 2 friendly installers, produce offers by hand-run prompt in a day, and show them; in parallel, call 3 hurtownie instalacyjne and 2 heat-pump manufacturers' installer-programme managers and ask whether they would co-brand a free pilot for their installers. Cost ≈ 0–100 PLN.

**Kill criteria:** installers say the offer saves <15 minutes or they would not pay 99 PLN/month; or 0 of 5 partners agree to a pilot conversation.

**Confidence:** low-medium (Western traction and Polish rules sourced; Polish installer counts, willingness to pay and channel not).

**Sources** (accessed 2026-11-05):
1. https://tech.eu/2025/08/13/plancraft-raises-eur38m-series-b-to-drive-ai-transformation-in-european-construction/
2. https://www.htgf.de/en/plancraft-series-b/
3. https://www.handoff.ai/blog/handoff-raises-5-8m-for-residential-construction
4. https://www.mynewsdesk.com/nemetschek-ag/pressreleases/nemetschek-group-announces-strategic-investment-in-handoff-an-ai-platform-for-contractors-3391479
5. https://www.surgepv.com/best-solar-software/poland
6. https://poradnikprzedsiebiorcy.pl/-montaz-pompy-ciepla-jaka-stawka-podatku-vat
7. https://bezprawnik.pl/program-czyste-powietrze-2025-wraca-na-nowych-zasadach/
8. https://github.com/fakturownia/api
9. https://www.udt.gov.pl/images/biuro-prasowe/files/pdf/INSPEKTOR_1_2023_Instalacje_Fotowoltaiczne_WCAG.pdf
10. https://www.gramwzielone.pl/pompy-ciepla/20358484/polacy-kupuja-wiecej-pomp-ciepla-nadzieja-na-przelamanie-impasu
11. https://globenergia.pl/ecopartner-rewolucyjna-aplikacja-wkrotce-zarobia-na-niej-nie-tylko-sprzedawcy-fotowoltaiki/
12. https://openrouter.ai/google/gemini-2.5-flash
13. https://artificialintelligenceact.eu/annex/3/
14. Internal: [TH27 check](../../poland-check/B/TH27-trades-home-services-front-office.md)

Coverage: 12 web searches/fetches for this write-up (plancraft and Handoff rounds, Polish PV/heat-pump offer tools, OpenSolar in Polish, installer counts, heat-pump sales, VAT 8%/23% rule, Czyste Powietrze 2025 changes, Fakturownia API, trades-app graveyard). Not found: number of installation firms in Poland, prices of Polish quoting apps, any retention data for plancraft or Handoff, a shutdown case.
