# V5 — Small business and professional buying: vertical scan

T08 of Phase 3 ([task](../../tasks/08-scan-v5-small-business-buying.md), [brief](../../BRIEF.md)). Catalogue: [catalogue/V5-small-business-buying.csv](../../catalogue/V5-small-business-buying.csv) (35 businesses, 12 countries). All sources accessed **2026-11-06**. Friction types use the brief's six: **finding, fit, trust, logistics, coordination, price**. Pattern ids P1–P10 are from [friction-patterns.md](../global/friction-patterns.md). "Computed" marks my arithmetic; "unverified" marks what I could not confirm; "inference" marks my reading, not a source.

Overlap with earlier scans: trade spare parts for HVAC and appliances (Parts Town, SupplyHouse.com, CzęściAGD.pl) are in [V2](V2-home-climate-appliance.md); car workshop parts (PartsTech, Inter Cars, Partly) are in [V1](V1-vehicle-parts.md); lead platforms for trades (Oferteo, Fixly, Checkatrade) are in [V4](V4-services-with-logistics.md). They are not repeated here. McMaster-Carr and MonotaRO are also cases in [friction-patterns.md](../global/friction-patterns.md) (P3); MonotaRO is kept here for its figures.

## 1. What the vertical is

A firm, a tradesperson or a professional practice buys what it needs to do its work: consumables (gloves, screws, cleaning agents, dental materials, food for a restaurant), spare parts, custom-made parts, and the materials for a whole job. The buyer is repeat by nature: the same restaurant orders several times a week, the same plumber buys parts on every job (inference). The friction is less "what is it called" than "where do I order it fast, at a fair price, with a VAT invoice, without phoning five wholesalers". The scan found seven kinds of business:

| Type | Rows | Examples |
|---|---|---|
| Long-tail MRO and trade-supply catalogues | 8 | MonotaRO, Zoro, Contorion, Droppe, Cronvall, TIM, Plieger, Installatiebalie.nl |
| Ordering apps between small buyers and their existing suppliers | 4 | Choco, REKKI, Marketboro, Suplery |
| Wholesale marketplaces for independent shops | 4 | Faire, Ankorstore, Orderchamp, merXu |
| Custom-parts marketplaces (upload a CAD file, get a price) | 3 | Xometry, meviy, CADDi (pivoted) |
| Construction materials: procurement software or delivery to site | 7 | Kojo, comstruct, BuildBuddy, Schüttflix, Fleaty, Buildiro, Snap It |
| One checkout for a professional practice | 2 | Torch Dental, Wellplaece |
| Horizontal B2B shops and purchasing agents | 7 | Allegro Biznes, ManoMano Pro, ASKUL, iMarketKorea, Material Bank, Fryzomania, Mapudo (dead) |

## 2. Friction types present

| Friction | How it shows up in V5 | Who removes it (catalogue rows) |
|---|---|---|
| **Finding** | long-tail items no local wholesaler stocks; products without EANs, matched only by attributes ([Mapudo retrospective](https://medium.com/swlh/why-mapudo-failed-5f3519f1b277)) | MonotaRO (24 m items), Zoro (14 m+), Contorion, Cronvall ([Distribution Strategy](https://distributionstrategy.com/2025/01/grainger-sales-hit-17-2b-in-2024-up-4-2/)) |
| **Fit** | weak for consumables; strong for custom parts (does the shop make this geometry?) | meviy and Xometry (price from a CAD file) |
| **Trust** | will the unknown shop pay, will the unknown brand deliver | Ankorstore, Faire (marketplace as the counterparty) |
| **Logistics** | material needed on site today; bulk goods need a truck | Snap It (delivery within the M25), Schüttflix (bulk), Material Bank (all samples in one box next morning) |
| **Coordination** | orders by phone, WhatsApp and email; delivery notes and invoices to reconcile | Choco, REKKI, Marketboro, Kojo, comstruct |
| **Price** | prices per customer, hidden behind a login or a phone call | Torch Dental (claims 16% saving, [Built In](https://builtin.com/articles/torch-rasies-28m-series-b)), Wellplaece (20–40% claimed, [TechCrunch](https://techcrunch.com/2023/05/30/wellplaece-dental-marketplace-commerce/)) |

**Coordination and price dominate.** The professional buyer usually knows the item; what costs time is placing the order with several suppliers and comparing their prices. Fit matters only for custom parts.

## 3. Patterns seen

| Pattern | V5 businesses | Evidence | Note for a Polish founder |
|---|---|---|---|
| P3 one catalogue for odd items | MonotaRO, Zoro, Contorion, Droppe, Cronvall | Grainger's Endless Assortment segment (Zoro + MonotaRO) USD 3.1 bn in 2024 ([Distribution Strategy](https://distributionstrategy.com/2025/01/grainger-sales-hit-17-2b-in-2024-up-4-2/)); MonotaRO over 10.1 m registered accounts ([Quartr](https://quartr.com/events/monotaro-co-ltd-3064-q4-2024_FeNFxz8P)); Droppe 1,500+ companies ([Pääomasijoittajat](https://paaomasijoittajat.fi/en/ajankohtaista/news/27402/droppe-secures-39-million-euros-in-funding-to-serve-a-new-generation-of-industrial-buyers/)); Cronvall 8,000+ clients ([BeBeez](https://bebeez.eu/2025/11/13/finnish-startup-cronvall-secures-e3-9m-to-scale-transparent-procurement-platform/)) | the big winners hold stock; Droppe and Cronvall show a drop-ship version is fundable in small markets |
| **New: free ordering app for buyers, suppliers pay (SaaS first, marketplace later)** | Choco, REKKI, Marketboro, Suplery | Marketboro total GMV KRW 2.75 tn in 2023 and a marketplace (Sikbom) added on top, KRW 14 bn monthly GMV in Aug 2024, +178% y/y ([Unicorn Factory](https://www.unicornfactory.co.kr/article/2024110115330126134), [Unicorn Factory](https://www.unicornfactory.co.kr/article/2024091116041752442)); Choco valued USD 1.2 bn in 2022 ([Restaurant Business](https://restaurantbusinessonline.com/technology/choco-raises-111m-wholesale-ordering-app)) | the founder's strongest fit in V5: software, no goods, repeat use several times a week; a failed construction-marketplace founder says they should have started as one-sided SaaS ([Notion post-mortem](https://phelipemartin.notion.site/Construction-Supplies-Marketplace-a48c6a6a75e34ad3a23dac8277321318), from a search summary, page not fetched) |
| Wholesale marketplace with commission (P3/P5 mix) | Faire, Ankorstore, Orderchamp, merXu | Ankorstore about 20% on first orders and 10% on reorders (2022, third-party) and 0% on reorders from Jan 2026 (unverified, [Garnet](https://garnetmarketplace.com/marketplaces/ankorstore.html)); Faire 15–25% (secondary, [Garnet](https://garnetmarketplace.com/marketplaces/faire.html)) | commission falls on reorders, so value is in the first match; capital-heavy and taken in the EU |
| **New: instant quote from a CAD file** | Xometry, meviy, CADDi | Xometry marketplace revenue USD 486 m in 2024 at 33.5% gross margin ([Xometry](https://xometry.gcs-web.com/news-releases/news-release-details/xometry-reports-fourth-quarter-and-full-year-2024-results)); CADDi dropped its marketplace for SaaS ([Fortune](https://www.fortune.com/2025/03/27/japanese-ai-startup-caddi-venture-capital-funding-atomico-supply-chain-optimization)) | AI pricing is real leverage, but quality disputes on custom parts sit with the platform; Poland has many small CNC and laser shops (not sourced here; T09) |
| Procurement workflow for contractors | Kojo, comstruct, BuildBuddy | Kojo: 600+ contractors buying over USD 5 bn a year through it ([Distribution Strategy](https://distributionstrategy.com/2025/09/kojo-secures-10-million-investment-from-wesco-expanding-construction-tech-platform/)) | B2B sales cycle to contractors; distributor (Wesco) invested, so suppliers welcome it |
| P10-like delivery to site | Schüttflix, Snap It, Fleaty, Buildiro | Schüttflix EUR 86.9 m revenue and EUR 26.6 m net loss in 2022 ([deutsche-startups](https://www.deutsche-startups.de/2024/07/03/schuettflix-zahlencheck-2022/)) | logistics-heavy; Fleaty's domain now redirects to its investor Hesus (checked 2026-11-06) |
| One checkout across a practice's suppliers | Torch Dental, Wellplaece | Torch: about 2,000 practices, up to 110 vendors ([Built In](https://builtin.com/articles/torch-rasies-28m-series-b)); Wellplaece takes a share of the sale from the supplier ([Becker's Dental](https://beckersdental.com/supply-chain/41139-dental-procurement-startup-receives-5-5m-in-seed-round-funding.html)) | a narrow professional group with recurring consumables; founder-sized if suppliers ship |

## 4. What the numbers say

1. **The big money holds stock.** MonotaRO (JPY 288 bn in 2024, [TipRanks](https://www.tipranks.com/news/company-announcements/monotaro-co-reports-strong-financial-results-for-2024)), ASKUL (about JPY 476 bn, aggregator), iMarketKorea (KRW 3.32 tn, [StockAnalysis](https://stockanalysis.com/quote/krx/122900/revenue/)) and Grainger (USD 17.2 bn) are distributors. The founder will not hold stock, so they are proof of demand, not models.
2. **Software take is small against GMV.** Marketboro: revenue about KRW 14.8 bn against KRW 2.75 tn GMV, about 0.5% (computed; the articles' figures differ). Kojo charges subscriptions ([Distribution Strategy](https://distributionstrategy.com/2025/09/kojo-secures-10-million-investment-from-wesco-expanding-construction-tech-platform/)). An ordering layer earns from suppliers' subscriptions, not from margin.
3. **Marketplace margins can be healthy when the platform sets the price.** Xometry 33.5% marketplace gross margin in 2024 (30.8% in 2023). Commission marketplaces (Ankorstore, Faire) cut fees on reorders.
4. **Professional buyers repeat.** Allegro Biznes reported 2024 growth of 31% in buyers, 36% in transactions and 25% in GMV to business accounts; over 80% of its buyers are sole traders and small firms ([Comparic](https://comparic.pl/zakupy-firmowe-na-allegro-robi-72-ankietowanych-przedsiebiorstw/), [Bezprawnik](https://bezprawnik.pl/allegro-biznes/)). Self-directed online sales at TIM were about PLN 73.2 m of PLN 104.1 m in Jan 2024, about 70% (computed, [BiznesRadar](https://www.biznesradar.pl/a/123432,styczen-w-tim-trudniejsza-sytuacja-na-rynku-i-finalizacja-wezwania)): Polish trades already order online from incumbents.
5. **Published take rates are rare**: only Ankorstore and Faire (third-party), Xometry's margin and Wellplaece's "a portion of the sale".

## 5. Graveyard and warnings

| Business | Country | What happened | Lesson | Source |
|---|---|---|---|---|
| Mapudo | DE | metals B2B marketplace, 2014–2019, insolvency; buyers used it only for secondary needs; fee too high on thin distributor margins; no EANs, attribute matching needed; data model sold to thyssenkrupp | a horizontal marketplace for thin-margin goods does not move main purchasing | [Medium](https://medium.com/swlh/why-mapudo-failed-5f3519f1b277), [Eurometal](https://eurometal.net/thyssenkrupp-acquires-data-model-from-e-commerce-platform-mapudo/) |
| CADDi (pivot) | JP | founders moved from parts marketplace to AI software about 2022 | the software is worth more than the matching margin | [Fortune](https://www.fortune.com/2025/03/27/japanese-ai-startup-caddi-venture-capital-funding-atomico-supply-chain-optimization) |
| Schüttflix (warning) | DE | EUR 26.6 m loss on EUR 86.9 m revenue in 2022; reports of job cuts and a sale (unverified) | owning bulk logistics burns capital | [deutsche-startups](https://www.deutsche-startups.de/2024/07/03/schuettflix-zahlencheck-2022/), [ms-aktuell](https://ms-aktuell.de/?p=174005) |
| merXu | PL | CEE B2B marketplace from ex-Allegro leaders, launched 2020; merxu.com did not resolve on 2026-11-06; Dealroom lists it as closed (unverified) | horizontal B2B in CEE did not last (status to confirm in T09) | [money.pl](https://www.money.pl/gielda/platforma-e-commerce-dla-firm-z-regionu-cee-merxu-rozpoczela-dzialalnosc-6576938942294145a.html) |
| Fleaty | SE | delivery of building materials in Stockholm; domain now redirects to investor Hesus | absorbed by a strategic investor | [Nordic9](https://nordic9.com/news/fleaty-to-raise-1-million-in-strategic-investment-from-the-french-hesus-news7140864442) |
| Katerra, Buildzar, mSupply, ShopX, Build-e | US / IN / IL | construction tech and materials marketplaces shut: overreach, low margins, slow traffic, failed fundraising (summary of short case notes) | pick one layer; margins in materials are thin | [ideaproof](https://ideaproof.io/startup-failures/katerra), [CB Insights](https://www.cbinsights.com/company/buildzar), [PYMNTS](https://www.pymnts.com/?p=1381061) |
| Korean construction e-marketplaces | KR | an academic study found most, except those led by large builders, performed poorly | supplier power decides | [KoreaScience](https://koreascience.kr/article/JAKO200416637999103.do) |

## 6. Poland: what exists

- **Online ordering by trades is already normal with incumbents**: TIM (Würth Group since Jan 2024) for electrical goods; Allegro Biznes for general SME buying with VAT invoices (row V5-PL-003).
- **Salon supplies are served by many online wholesalers**: Trena, Fryzomania (loyalty discounts up to 61%), KERN and others ([kb.pl](https://kb.pl/porady/dobra-i-tania-hurtownia-fryzjerska-gdzie-jej-szukac-_wp24/)). A cross-wholesaler reorder tool was not found.
- **Not found in quick searches** (one query each, 2026-11-06, see §8): a restaurant-to-wholesaler ordering app like Choco or Marketboro (found only Restimo, which aggregates delivery-app orders, not purchasing); a one-checkout or price comparison for dental materials; one-hour delivery of installation materials to a site in Warsaw; a multi-supplier platform for workwear and safety (BHP) items (found XBHP, a single wholesaler aiming at one basket, sponsored article, [Inżynier Budownictwa](https://inzynierbudownictwa.pl/nowa-hurtownia-bhp-na-polskim-rynku/)).

## 7. Ten most promising analogues for Poland (quick Polish check)

| # | Analogue (rows) | Exists in Poland? (quick search 2026-11-06) | What a Polish version would need |
|---|---|---|---|
| 1 | Ordering app for restaurants and their wholesalers (Choco, REKKI, Marketboro) | not found (1 query) | parsing of orders sent by SMS, WhatsApp or email into wholesaler systems (AI step); 5–10 food wholesalers willing to pay a subscription; integration with Polish ERP (Subiekt, Comarch; to check) |
| 2 | One checkout across dental suppliers (Torch Dental, Wellplaece) | not found (1 query) | price feeds from Polish dental distributors (names to collect in T09); medical-device rules for some items to check (T09) |
| 3 | Drop-ship MRO, workwear and safety catalogue for SMEs (Droppe, Cronvall, Zoro) | partly: single wholesalers (XBHP) and Allegro Biznes | supplier feeds with stock and price; VAT invoices and deferred payment (Allegro Biznes offers business accounts) |
| 4 | Cross-wholesaler reordering for salons (Suplery) | not found; many single wholesalers | catalogues of Trena, Fryzomania and others; licence check of the salon (as Suplery does) |
| 5 | Instant quote from a CAD file to local job shops (Xometry, meviy) | not checked | a pricing model per process (laser cutting first); 5–10 partner shops; quality and dispute handling |
| 6 | Procurement workflow for contractors (Kojo, comstruct) | not checked | TIM or Onninen as supplier partners (TIM already sells about 70% online, computed); long sales cycle |
| 7 | Stock lookup across builders' merchants with fast delivery (Buildiro, Snap It) | not found for one-hour delivery (1 query) | live stock from merchants (PSB group, to check); a courier partner (Stuart, Wolt Drive; to check) |
| 8 | Wholesale marketplace for independent shops (Faire, Ankorstore) | partly: Ankorstore serves EU retailers; merXu likely closed | no gap for gift-shop wholesale; a niche trade version would need a reason Allegro Biznes does not cover it |
| 9 | Sample box for architects (Material Bank) | not checked | brands pay; own sample hub (physical work too high for the founder) |
| 10 | Purchasing agent for large firms (iMarketKorea) | not checked | not founder-sized |

## 8. Coverage

- **Businesses catalogued:** 35 rows: United States 7, Germany 5, Japan 4, Poland 4, United Kingdom 3, Netherlands 3, South Korea 2, France 2, Finland 2, Sweden 1, Czechia 1, Ukraine 1. Nordics: FI, SE. JP/KR: both. CEE: PL, CZ, UA.
- **Searches:** about 33 web searches (English, Polish, German, Dutch, Czech, Korean) and the link checker; no page fetches (figures come from search-result summaries of the cited pages).
- **Searches that found nothing useful (9):** a Nordic construction-materials ordering startup with current figures (only Fleaty, absorbed), a Dutch installer-ordering startup with funding, Contorion revenue after 2017, ManoMano Pro 2024 share, Suplery commission, Fresha supply marketplace (none exists), Polish salon supply platform beyond single wholesalers, Polish gastronomy procurement app, merXu closure news.
- **Polish quick queries (2026-11-06):** "hurtownia fryzjerska kosmetyczna online dla salonów platforma zamówień Booksy marketplace produkty dla salonów", "Merkury Market OR Onninen OR \"TIM SA\" sprzedaż internetowa e-commerce B2B instalatorzy elektrycy 2024 przychody", "merXu B2B platforma Polska finansowanie liczba firm", "Allegro Biznes liczba firm kupujących faktura VAT 2024", "platforma zamówień dla gastronomii hurtownie restauracje aplikacja startup Polska", "merXu zamknięcie platformy B2B koniec działalności", "porównywarka cen materiałów stomatologicznych hurtownie stomatologiczne jeden koszyk", "dostawa materiałów instalacyjnych na budowę w godzinę Warszawa hurtownia kurier dla instalatorów", "platforma zakupowa B2B odzież robocza BHP dla firm wielu dostawców zamówienia online". Findings in §6–7.
- **Gaps:** no workshop (car-repair) consumables or beauty-salon ordering business with figures outside Suplery; no Baltic, Slovak, Romanian or Hungarian row; Onninen and Polish builders' merchants (PSB, Bims Plus) not researched; no French trade-supply startup beyond ManoMano Pro; repeat rates for professional buyers not published by any row; Polish dental and food-wholesaler counts not sourced (T09).

## 9. Takeaways for T09–T11

1. Do not build a horizontal B2B marketplace: Allegro Biznes and TIM serve Polish firms, and Mapudo and merXu show the failure mode.
2. The founder-shaped V5 idea is **an ordering layer between small professional buyers and the suppliers they already use** (restaurants, salons, dental practices), free for buyers, paid by suppliers, with AI turning messy orders (SMS, voice, email, photos of a list) into structured orders. It needs no stock and has repeat use built in.
3. Second line: **one checkout across a narrow profession's suppliers** (dental, salon) with drop-ship and a share of the sale, if suppliers share price feeds.
4. CAD-to-quote for local job shops has real AI leverage but carries quality liability; treat it as a stretch idea.
5. T09 should mine Polish demand for: "hurtownia stomatologiczna online", "zamówienia do hurtowni gastronomicznej aplikacja", "hurtownia fryzjerska zamówienie", "cięcie laserem na wymiar wycena online", "odzież robocza BHP hurtownia dla firm", "dostawa materiałów na budowę ekspres".

## Unverifiable links (403, timeouts; open in a browser)
Link check 2026-11-06: 0 dead after fixes (Fleaty, merXu and Wellplaece home pages replaced or marked as not resolving). Unverifiable (403/timeouts): xometry.gcs-web.com (2024 results), beckersdental.com, monotaro.com, zoro.com, meviy.misumi-ec.com, contorion.de, torchdental.com, snapitapp.com, allegro.pl/biznes. Figures from search-result summaries only (pages not fetched): all rows; aggregator figures (ASKUL, REKKI, Faire, Ankorstore take rates) are marked as secondary in the catalogue.
