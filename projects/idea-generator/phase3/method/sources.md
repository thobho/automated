# Phase 3 sources

Starting sources for the Poland baseline (T02), friction patterns (T03), the vertical scans (T04–T08), demand mining (T09) and the findability test (T10). A starting list, not a limit: add sources found during research under "Sources added during research" at the end, with URL, what it gives and the access date. Vertical-specific shops and marketplaces are in [verticals.md](verticals.md); the Phase 2 lists of startup media and funding trackers by region stay useful: [phase2 sources](../../phase2/method/sources.md).

All links below were checked on 2026-11-06 with `tools/check_links.py` and by reading the page title. "(blocks bots)" means the site exists but returned 403/429, a timeout or a challenge page to the fetch tool; read it in a browser by hand. Prefer primary sources: the business's own site, pricing and fee pages, investor reports, founder posts. Media and lists are for finding businesses, not for citing traction when a primary source exists.

## 1. Global sources for commerce

| Source | What it gives | Access notes |
|---|---|---|
| [Marketplace Pulse](https://www.marketplacepulse.com/) | Analysis of Amazon, marketplaces and their sellers; marketplace fees and seller counts | Readable |
| [a16z Marketplace 100](https://a16z.com/marketplace-100/) | Ranking of consumer marketplace start-ups by gross bookings | Readable; US-centred |
| [Digital Commerce 360](https://www.digitalcommerce360.com/) | Ecommerce research and news, online sales rankings | Readable |
| [Modern Retail](https://www.modernretail.co/) | DTC and retail business news, unit economics stories | Readable |
| [Retail Dive](https://www.retaildive.com/) | Retail and ecommerce news | Readable |
| [Practical Ecommerce](https://www.practicalecommerce.com/) | Merchant-side how-to and analysis | Readable |
| [Ecommerce News Europe](https://ecommercenews.eu/) | European ecommerce news by country | Readable |
| [ECDB](https://ecommercedb.com/) | Store and market rankings with revenue estimates by country | Readable; detailed data paid; revenue figures are estimates |
| Eurostat [E-commerce statistics for individuals](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=E-commerce_statistics_for_individuals) | Share of people buying online, by country and category | Readable; official |
| [Statista](https://www.statista.com/) | Market sizes and charts | Mostly paid; cite the underlying source, not Statista alone |

**Seller communities** (what merchants complain about, fees, suppliers, returns):
- [Shopify Community](https://community.shopify.com/) and the [Shopify blog](https://www.shopify.com/blog).
- [Amazon Seller Forums](https://sellercentral.amazon.com/seller-forums) and [Sell on Amazon](https://sell.amazon.com/) (fees and programmes).
- Reddit: [r/ecommerce](https://www.reddit.com/r/ecommerce/), [r/shopify](https://www.reddit.com/r/shopify/), [r/FulfillmentByAmazon](https://www.reddit.com/r/FulfillmentByAmazon/). Phase 1 found reddit.com hard to read with the fetch tool; use a browser.

**Funding and traction:**
- [Crunchbase News](https://news.crunchbase.com/) (funding rounds; the database needs an account), [Dealroom](https://dealroom.co/) (European start-up database, reports public), [Tracxn](https://tracxn.com/) (company profiles by sector, partly free), [PitchBook News](https://pitchbook.com/news).
- [Similarweb](https://www.similarweb.com/top-websites/poland/) public pages: top sites by country and category, and per-site pages, e.g. [allegro.pl](https://www.similarweb.com/website/allegro.pl/). Traffic and the split by channel (search, direct, paid) are estimates; they show reach and owned distribution, not repeat purchase.
- [Google Trends](https://trends.google.com/trends/explore?geo=PL) (blocks bots; open in a browser): relative search interest, seasonality. [Google autocomplete JSON](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=cz%C4%99%C5%9Bci%20do%20pralki) shows that a phrase is searched, not its volume (pattern from Phase 2; change `q`).

**Graveyard:** [Failory Startup Cemetery](https://www.failory.com/cemetery), [CB Insights startup post-mortems](https://www.cbinsights.com/research/startup-failure-post-mortem/). Also search media for "shuts down", "pivot", "insolvency" / "Insolvenz" / "upadłość" with the business name.

**EU law texts** (flag, do not give legal advice): General Product Safety Regulation [(EU) 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj) (GPSR), F-gas Regulation [(EU) 2024/573](https://eur-lex.europa.eu/eli/reg/2024/573/oj).

## 2. Poland

**Allegro (platform owner and main incumbent)**
- [Allegro Pomoc](https://allegro.pl/pomoc): help pages for buyers and sellers, including seller fees and Smart! delivery rules. Allegro blocks the fetch tool on most pages; use a browser by hand.
- [Allegro investor relations / about](https://about.allegro.eu/): annual and quarterly reports (GMV, active buyers, take rate, advertising revenue).
- Allegro affiliate programme: run through affiliate networks, e.g. [BUY.BOX programme page](https://getbuybox.com/allegro/); commission rates differ by category and change, so read the current terms (third-party summaries found on 2026-11-06 disagree with each other).

**Price comparison, classifieds, reviews**
- [Ceneo](https://www.ceneo.pl/) and its shop panel [shops.ceneo.pl](https://shops.ceneo.pl/) (CPC model for shops).
- [OLX](https://www.olx.pl/) and [Allegro Lokalnie](https://www.allegrolokalnie.pl/) (classifieds, second-hand).
- Shop trust: [Opineo](https://www.opineo.pl/) (shop reviews), [Trusted Shops PL](https://www.trustedshops.pl/).
- [e-commerce.pl](https://www.e-commerce.pl/): a product-opinion site (not trade media, despite the name); useful for demand signals.

**Ecommerce trade media**
- [Wirtualnemedia.pl](https://www.wirtualnemedia.pl/) (media, internet and ecommerce business news).
- [Interaktywnie](https://interaktywnie.com/) (online marketing and ecommerce).
- [Wiadomości Handlowe](https://www.wiadomoscihandlowe.pl/) and [DlaHandlu.pl](https://www.dlahandlu.pl/) (retail trade news).
- [NowyMarketing](https://nowymarketing.pl/) and [Marketer+](https://marketerplus.pl/) (marketing, ecommerce campaigns).
- [MamStartup](https://www.mamstartup.pl/) (Polish start-ups and funding).
- Industry body: [e-Izba (Izba Gospodarki Elektronicznej)](https://eizba.pl/) (reports on Polish ecommerce). Audience measurement: [Gemius](https://www.gemius.pl/) (search its site for the yearly Polish ecommerce report; unverified).

**Logistics and payments**
- [InPost Investors](https://inpost.eu/investors) (parcel volumes, locker counts, prices in reports) and [InPost PL](https://inpost.pl/) (price lists).
- [Poczta Polska](https://www.poczta-polska.pl/), [DPD Polska](https://www.dpd.com/pl/pl/).
- Parcel brokers with public price lists: [Furgonetka](https://www.furgonetka.pl/), [Apaczka](https://www.apaczka.pl/).
- Postal market regulator: [UKE](https://www.uke.gov.pl/) (yearly postal market report).
- Payments: [Przelewy24](https://www.przelewy24.pl/), [BLIK](https://www.blik.com/).

**Statistics and registries**
- [GUS](https://stat.gov.pl/): retail sales, including the online share, under [Handel](https://stat.gov.pl/obszary-tematyczne/ceny-handel/handel/); [BDL](https://bdl.stat.gov.pl/) (local data bank).
- Vehicles: [PZPM](https://www.pzpm.org.pl/) (car fleet and registration reports), [SDCM](https://www.sdcm.pl/) (Polish association of parts distributors and producers; aftermarket reports).

**Law and consumer protection**
- [UOKiK](https://uokik.gov.pl/) (consumer rights, withdrawal right, rękojmia guidance).
- [ISAP](https://isap.sejm.gov.pl/) (official texts of Polish laws, e.g. ustawa o prawach konsumenta).

**Affiliate networks** (commission rates for T02 monetisation): [webePartners](https://www.webepartners.pl/), [Convertiser](https://www.convertiser.com/), [Tradedoubler](https://www.tradedoubler.com/).

**Demand signals** (T09): [Wykop](https://www.wykop.pl/), Facebook groups per vertical (need a browser and often membership; record group name and member count, never log in to scrape), Allegro and OLX listing counts by hand.

## 3. Local sources by region (at least two each)

### Germany and Austria (DACH)
- [etailment](https://www.etailment.de/) (ecommerce trade magazine), [INTERNET WORLD Business](https://www.internetworld.de/), [t3n](https://t3n.de/).
- Associations: [bevh](https://www.bevh.org/) (German ecommerce and mail-order association; market data), [HDE](https://einzelhandel.de/) (retail association).

### France
- [Fevad](https://www.fevad.com/) (French ecommerce federation; yearly key figures), [EcommerceMag](https://www.ecommercemag.fr/), [LSA](https://www.lsa-conso.fr/) (retail trade; blocks bots).

### UK and Ireland
- [InternetRetailing](https://internetretailing.net/), [Retail Gazette](https://www.retailgazette.co.uk/), [IMRG](https://www.imrg.org/) (online retail industry body).

### Netherlands and Benelux
- [Thuiswinkel.org](https://www.thuiswinkel.org/) (Dutch ecommerce association; market monitor), [Ecommerce News Europe](https://ecommercenews.eu/), [Marktplaats](https://www.marktplaats.nl/) (classifieds, for demand).

### United States
- [Marketplace Pulse](https://www.marketplacepulse.com/), [Modern Retail](https://www.modernretail.co/), [Digital Commerce 360](https://www.digitalcommerce360.com/), [Retail Dive](https://www.retaildive.com/).

### Japan
- [BRIDGE](https://thebridge.jp/) (Japanese start-up media), [Similarweb Japan top sites](https://www.similarweb.com/top-websites/japan/), and the MRO and hobby players' own investor pages (see [verticals.md](verticals.md)).

### CEE peers and expansion markets (CZ, SK, Baltics)
- Czechia: [CzechCrunch](https://www.czechcrunch.cz/), [APEK](https://www.apek.cz/) (Czech ecommerce association), [Heureka.cz](https://www.heureka.cz/) (price comparison; blocks bots).
- Slovakia: [Heureka.sk](https://www.heureka.sk/) (blocks bots).
- Baltics: [Pigu.lt](https://pigu.lt/) (Lithuanian online marketplace).
- Region-wide: [The Recursive](https://therecursive.com/) (CEE start-up media).

## Sources added during research
(none yet)
