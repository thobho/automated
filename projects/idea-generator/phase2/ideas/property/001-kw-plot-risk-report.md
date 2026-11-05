# 001 — "Czy ta księga jest czysta?" KW + plot risk report

**One-liner:** Upload a księga wieczysta odpis (PDF from EKW or mObywatel) for a flat or plot; the tool reads działy I–IV of the flat, building and land KW, cross-checks the parcel against EGiB/ULDK and the zoning layer, and returns a plain-Polish risk list with "ask the seller / ask the notary" questions. B2B tier for estate agents and mortgage brokers.
**Field:** property | **Type:** SaaS (web) | **B2C with B2B tier** · shortlist id L079 (merges L080 agents tier, L081 notary pre-deed check, L082 spółdzielcze prawo module)

**Western analogues:**
- **Orbital (formerly Orbital Witness)**, UK, [orbital.tech](https://www.orbital.tech/) — AI title and property due diligence for lawyers; founded 2018, AI product since 2023; 5,000+ professionals, 250,000+ transactions/year, logos DLA Piper and A&O Shearman (TH15 check). **US$60M Series B in January 2026** led by Brighton Park Capital, after a £7.5M Series A in May 2023 ([CFOtech UK](https://cfotech.co.uk/story/orbital-raises-usd-60m-to-scale-ai-for-real-estate-law); [The Negotiator](https://thenegotiator.co.uk/news/orbital-witness-raises-7-5m-in-boost-for-conveyancing-market/)). In 2023 it announced a move into residential conveyancing ([Estate Agent Today](https://www.estateagenttoday.co.uk/breaking-news/2023/5/ai-property-due-diligence-platform-to-enter-residential-market)).
- **Moverly, Conveyd** (UK, property packs on UK Land Registry), **Beglaubigt.de** (DE notarial), **Paraito** (CA title) — named in the TH15 check; no traction figures re-verified here (unverified).

**Spread:** TH15 appears in UK, US, DE, CA (R1, R2, R3); no CEE analogue in the R6 catalogue. The B2C "explain my title register" form exists nowhere as a scaled product; the scaled form is B2B for law firms.

**Does the Western leader already work in Poland?** No. Orbital's site offers only US and GB selectors and is demo-led, so there is no free tier to try (checked in TH15, 2026-11-04). Its value is wired to HM Land Registry titles and English/US conveyancing. Not tried: uploading a Polish KW odpis to ChatGPT or Gemini. A generic assistant will read a text PDF of an odpis and list hipoteki in Polish; what it does not do is fetch the building and land KW, match the parcel to EGiB, or know which wzmianki and roszczenia matter. That is the real gap, and also the main absorption risk (see Risks).

**Polish adaptation, i.e. the edge:**
- EKW structure ([M27](../../research/poland/local-moats.md)): działy I-O, I-Sp, II, III, IV; wzmianki (pending entries) that warn of a sale or mortgage in progress; hipoteka przymusowa (ZUS/US/komornik); służebność przesyłu; roszczenia and ostrzeżenia; the flat KW referring to the land KW. No public API and CAPTCHA, so the user supplies the PDF.
- Geoportal/ULDK ([M28](../../research/poland/local-moats.md)): parcel geometry and area by TERYT id, free; MPZP / plan ogólny layers per gmina (mixed formats).
- Polish notarial practice (who checks what), spółdzielcze własnościowe prawo do lokalu often without a KW (L082 module: unsourced, drop or source before build).
- Common mistake in Polish listings: KW area including piwnica/komórka, distorting PLN/m² ([pewnylokal.pl guide](https://pewnylokal.pl/porady/sprawdzenie-mieszkania-przed-kupnem), accessed 2026-11-05).
A foreign team would have to rebuild the parser, the risk taxonomy and the Polish legal vocabulary; none of Orbital's UK data plumbing carries over.

**Target customer in Poland:**
- B2C: buyers of resale flats and plots. GUS: 545.8k notarial sale deeds in 2024 (+6.8% y/y) ([GUS, Obrót nieruchomościami w 2024 r.](https://stat.gov.pl/obszary-tematyczne/infrastruktura-komunalna-nieruchomosci/nieruchomosci-budynki-infrastruktura-komunalna/obrot-nieruchomosciami-w-2024-r-,4,22.html)); ~255k resale flats sold in 2024 per a secondary analysis of GUS data ([comparic.pl](https://comparic.pl/60-polakow-wybralo-mieszkania-z-rynku-wtornego-roznica-dochodzi-do-85-000-zl/), unverified against GUS tables). Accessed 2026-11-05.
- B2B: estate agencies and mortgage brokers who want a report to hand to buyers (count not sourced here; estimate several thousand agencies).
- CEE: Czech katastr nemovitostí and Slovak kataster are online and structured differently; expansion means rebuilding the parser per country (medium effort).

**Demand driver:** DD10 (housing revival: 208k completions in 2025, mortgage lending +27% y/y in Q2 2026) and DD9 (suburban plot buying), both in [demography.md](../../research/poland/demography.md). Technological: LLMs can now read scanned odpisy reliably enough to make a 49–99 PLN report possible.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Pewny Lokal | lawyer reviews KW of flat, building and land, "supported by advanced statistical methods"; report | not on page (booking/phone); 499 PLN plot package per search excerpt (unverified) | human, slow, priced for hundreds of PLN ([pewnylokal.pl](https://pewnylokal.pl/analiza-ksiegi-wieczystej-mieszkania-zadluzenia-i-zatajone-wpisy), accessed 2026-11-05) |
| OnGeo Raport o terenie | automated spatial plot report | point packages | no KW reading ([OnGeo](https://www.blog.ongeo.pl/raport-o-terenie-narzedzie-dla-posrednikow)) |
| e-mapa.net Raport planistyczny | zoning per plot | ~20 PLN (excerpt) | no KW reading ([e-mapa.net](https://e-mapa.net/DzialkaRaport/start/mpzp.php)) |
| mObywatel Księgi wieczyste | KW access for **own** properties | free / court fees | no interpretation, not for buyers ([Spider's Web](https://spidersweb.pl/2026/04/mobywatel-ksiegi-wieczyste.html)) |
| Notary, bank, free guides (kb.pl, infor.pl) | checks at the deed / mortgage stage | free to buyer | late in the process, not explained to buyer |
| ChatGPT / Gemini | paste the odpis | free–100 PLN/month | no cross-KW and parcel checks, no risk taxonomy |

**Evidence of Polish demand:** "sprawdzenie księgi wieczystej" autocomplete returns 10 variants (po numerze, za darmo, po adresie, po numerze działki, mieszkania) while "analiza księgi wieczystej" returns none (TH15, 2026-11-04): people search for **access**, rarely for **interpretation**. A commercial EKW scraper on Apify ([Apify](https://apify.com/regdata/ekw-ksiegi-wieczyste-scraper?fpr=data)) shows paid demand for KW data at scale. The PFSRM valuers' AI newsletter (2026-04) calls KW review the step "requiring great precision", still manual ([PFSRM PDF](https://psrwn.pl/wp-content/uploads/2026/04/2026_04_PFSRM_ZESPOL_ds_AI_newsletter-nr-1.pdf)). Many lawyer marketing pages for paid KW review (Pewny Lokal has 10+ guide pages) suggest SEO competition for the same phrases.

**MVP scope (≤6 weeks):**
1. Upload 1–3 odpis PDFs (text or scanned); parse into JSON per dział (OCR fallback). Golden-file tests on 30 anonymised odpisy.
2. Rule layer + LLM for risk items: hipoteka (amount, creditor), hipoteka przymusowa, służebności, roszczenia, wzmianki, owner mismatch, area check, missing building/land KW.
3. Parcel lookup via ULDK by działka id → area and geometry, compare with dział I-O; link to the gmina zoning layer (no extraction in MVP; that is idea 006).
4. Report PDF in Polish with a question list for seller and notary; Przelewy24/BLIK checkout.
5. B2B: agent account with per-report credits and their logo.

**Monetization:** B2C 69 PLN per property (flat + building + land KW); B2B 199 PLN/month for 10 reports, then 15 PLN each.
**Unit economics:** one report ≈ 3 odpisy × ~10k tokens = ~30k input + ~3k output tokens. Gemini 2.5 Flash on OpenRouter at US$0.30 / US$2.50 per M tokens ([OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) → ~US$0.017 ≈ 0.07 PLN; a two-pass check with a frontier model at ~US$3/US$15 per M (estimate) → ~0.5 PLN. OCR and hosting ~0.5 PLN, payments ~2% (estimate) → cost ≤ 2.5 PLN on 69 PLN, gross margin >95%. Token cost is not the constraint; volume is: 10k PLN MRR = ~145 B2C reports/month, or ~50 agencies on the B2B plan.

**Distribution, first 10 customers:** (1) SEO pages on the existing access-intent phrases ("sprawdzenie księgi wieczystej po numerze" → "and here is what it means"); (2) 10 estate agencies and 5 mortgage brokers in one city, approached with a free report on a listing they have; (3) Facebook groups for first-time buyers and plot buyers (posting a free sample report).

**Regulation:** AI Act: not an Annex III high-risk use (no credit scoring, no essential-service eligibility); transparency only. If mortgage brokers use it, it must not score creditworthiness. RODO: odpisy contain names and PESEL of owners; process in the EU, delete after 30 days, DPA for B2B. Legal services: in Poland, legal advice outside court representation is not reserved to advocates (unverified, ask counsel); keep wording "information, not legal advice; confirm with notary". Automated EKW access is avoided by design (user uploads).

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Agents and brokers buy it as a sales tool ("listing with a clean-title report") | M | H | 3 of 10 agencies in a pilot reuse it on new listings within a month |
| O2 | Merge with idea 006 (plot buildability) into one plot-buyer product sharing ULDK and channel | H | M | both MVPs share >50% code; plot report bundle sells at 99 PLN |
| O3 | Notary offices use the pre-deed checklist (L081) to save clerk time | L | M | one notary office agrees to a trial |
| O4 | Hipoteka przymusowa and wzmianka alerts become a monitoring subscription for investors with many flats | L | M | investors ask for re-check on change |
| O5 | Mortgage boom (DD10) lifts transaction volume through 2027 | M | M | GUS 2025/2026 deed counts keep rising |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Buyers see notary and bank checks as enough; B2C willingness to pay stays near zero | H | H | SEO landing converts <0.5% at 69 PLN |
| R2 | ChatGPT/Gemini "read this odpis" is good enough for most buyers | M | H | testers say "I can paste it into ChatGPT" |
| R3 | mObywatel extends KW features to buyers (e.g. seller shares KW with explanation) | L | H | Ministry of Digital Affairs roadmap mentions KW sharing |
| R4 | Wrong "clean" verdict leads to a buyer loss and liability claim | L | H | any reported miss in pilot; need disclaimer + human-review add-on |
| R5 | Low frequency: one buyer buys once every ~10 years, no retention | H | M | B2C repeat rate ≈ 0 (expected); B2B must carry MRR |
| R6 | Law firms (Pewny Lokal and others) add an AI tier at lower prices | M | M | new "AI" pages from KW-audit firms |

**Success signals:**
- Western analogue durable signals: replaces lawyer hours on title review (budget line: fee-earner time) and serves 250k transactions/year (TH15); expansion into US and a large Series B from strategic investors including RELX's REV and Grosvenor ([CFOtech UK](https://cfotech.co.uk/story/orbital-raises-usd-60m-to-scale-ai-for-real-estate-law)); hard to absorb (Land Registry integrations). No public retention or NRR figures (unverified).
- Hype warnings: none found for Orbital; but its proof is B2B law-firm use, not B2C.
- Polish adaptation can reproduce: replaced spend = a 300–500 PLN lawyer KW review (B2C) or agent time spent explaining KW to buyers (B2B); first channel = SEO on access-intent phrases + agencies in one city; retention driver = B2B report credits per listing. B2C retention cannot be reproduced.

**Graveyard:** Doma (US, AI-driven "instant" title insurance) shrank from US$400M to US$311M revenue in 2023 as mortgage volume fell and was sold to Title Resources Group for ~US$85M in 2024 ([National Mortgage News](https://nationalmortgagenews.com/news/doma-to-sell-to-title-resources-group-for-85-million); [ALTA](https://alta.org/news-and-publications/news/20241001-TRG-Completes-Deal-for-Doma)). Lessons: title tech tied to transaction volume is cyclical, and taking on liability (insurance) is capital-heavy; stay an information product. No Polish failure found.

**Scores (1–5):** L1 4 · L2 3 · L3 4 · L4 5 · L5 3 · L6 3 · L7 4 · L8 3 · L9 3 | **Weighted:** 3.6 / 5 | **Chance band:** 5–15%. (3.6 is in the 15–30% range, but none of L5/L6/L8 reaches 4, so criteria §3 drops it to 5–15%.) The moat and margins are strong and the MVP is very testable (golden files on odpisy), but B2C willingness to pay is unproven against free notary checks and generic chatbots, and the purchase is once per decade. Reaching 10k PLN MRR depends on the agency/broker tier, which has no demand evidence yet.
Changes vs. quick score: L5 4 → 3 (search shows access intent, not interpretation intent; no paying-for-workaround evidence beyond lawyer services); L7 3 → 4 (upload design removes the EKW dependency; ULDK is free and documented).

**Cheapest validation test (≤1 week, ≤200 PLN):** a landing page "Wgraj odpis księgi wieczystej, w 10 minut dostaniesz listę ryzyk — 69 PLN" with a BLIK pre-order button (refund if not delivered), 150 PLN of Google Ads on "sprawdzenie księgi wieczystej mieszkania"; in parallel email/phone 10 estate agencies in one city offering 3 free reports. Pass: ≥5 pre-orders or ≥3 agencies asking for a price.

**Kill criteria:** <2 pre-orders from ~300 ad clicks and no agency interested after 3 free reports each; or a test on 20 real odpisy shows that a free ChatGPT paste finds the same risks as the MVP in ≥18 of 20.

**Confidence:** medium (moat and competition well sourced; demand and B2B willingness to pay not).

**Sources** (accessed 2026-11-05 unless noted):
1. https://www.orbital.tech/ (2026-11-04, TH15)
2. https://cfotech.co.uk/story/orbital-raises-usd-60m-to-scale-ai-for-real-estate-law
3. https://thenegotiator.co.uk/news/orbital-witness-raises-7-5m-in-boost-for-conveyancing-market/
4. https://www.estateagenttoday.co.uk/breaking-news/2023/5/ai-property-due-diligence-platform-to-enter-residential-market
5. https://stat.gov.pl/obszary-tematyczne/infrastruktura-komunalna-nieruchomosci/nieruchomosci-budynki-infrastruktura-komunalna/obrot-nieruchomosciami-w-2024-r-,4,22.html
6. https://comparic.pl/60-polakow-wybralo-mieszkania-z-rynku-wtornego-roznica-dochodzi-do-85-000-zl/
7. https://pewnylokal.pl/analiza-ksiegi-wieczystej-mieszkania-zadluzenia-i-zatajone-wpisy
8. https://pewnylokal.pl/porady/sprawdzenie-mieszkania-przed-kupnem
9. https://www.blog.ongeo.pl/raport-o-terenie-narzedzie-dla-posrednikow (2026-11-04, TH15)
10. https://e-mapa.net/DzialkaRaport/start/mpzp.php (2026-11-04, TH15)
11. https://spidersweb.pl/2026/04/mobywatel-ksiegi-wieczyste.html (2026-11-04, TH15)
12. https://apify.com/regdata/ekw-ksiegi-wieczyste-scraper?fpr=data (2026-11-04, TH15)
13. https://psrwn.pl/wp-content/uploads/2026/04/2026_04_PFSRM_ZESPOL_ds_AI_newsletter-nr-1.pdf (2026-11-04, TH15)
14. https://openrouter.ai/google/gemini-2.5-flash
15. https://nationalmortgagenews.com/news/doma-to-sell-to-title-resources-group-for-85-million
16. https://alta.org/news-and-publications/news/20241001-TRG-Completes-Deal-for-Doma
17. Internal: [TH15 check](../../poland-check/B/TH15-property-transaction-title-diligence.md), [local-moats M27/M28](../../research/poland/local-moats.md), [demography DD9/DD10](../../research/poland/demography.md)

Coverage: 5 web searches/fetches run for this write-up (Orbital funding, Polish KW-analysis services, Pewny Lokal price page, GUS transactions, Doma graveyard); Pewny Lokal price page gave no price; no AI KW reader found in Polish search.
