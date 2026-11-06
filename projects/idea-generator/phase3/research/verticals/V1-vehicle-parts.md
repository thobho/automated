# V1 — Vehicle parts and car-related buying: vertical scan

T04 of Phase 3 ([task](../../tasks/04-scan-v1-vehicle-parts.md), [brief](../../BRIEF.md)). Catalogue: [catalogue/V1-vehicle-parts.csv](../../catalogue/V1-vehicle-parts.csv) (48 businesses, 13 countries). All sources accessed **2026-11-06**. Friction types use the brief's six: **finding, fit, trust, logistics, coordination, price**. Pattern ids P1–P10 are from [friction-patterns.md](../global/friction-patterns.md). "Computed" marks my arithmetic; "unverified" marks what I could not confirm; "inference" marks my reading, not a source.

## 1. What the vertical is

Buying anything a car, van or motorcycle needs: new and used parts, tyres and wheels, accessories and gear, and the service step around them (fitting, servicing, repair, collection, inspection). Three kinds of business appear in the scan:

| Type | Rows | Examples |
|---|---|---|
| Parts, tyre and motorcycle-gear retailers (hold stock) | 18 | Autodoc, RockAuto, Oscaro, Skruvat, Oponeo, Allopneus, Autoway, Louis |
| Used-parts marketplaces, software for dismantlers, used-parts stores | 5 | Ovoko (LT), Opisto (FR), Car-Part.com (US), Carsub (KR), UP GARAGE (JP, own stores) |
| Garage booking, quotes, mobile, collection and buy-plus-fit services | 15 | BookMyGarage, WhoCanFixMyCar, Vroomly, iDGARAGES, Autobutler, Fixter, ClickMechanic, Wrench, Mycle, Motointegrator, Caroobi (dead) |
| B2B data, ordering software and distribution | 6 | Partly (NZ), Versable (US), PartsTech (US), RevolutionParts (US), Inter Cars (PL distributor), Dr.Car (KR) |
| Other (history reports, diagnostics, EV install leads, body damage) | 4 | carVertical, FIXD, Aroundhome, Fixico |

## 2. Friction types present

| Friction | How it shows up in V1 | Who removes it (catalogue rows) |
|---|---|---|
| **Finding** | the buyer does not know the OE or aftermarket number; parts are listed under many cross-references | Autodoc, RockAuto, PartsTech, Partly, Versable, Ovoko |
| **Fit** | engine code, year, trim and option codes decide fit; the plate or VIN is the key | Allegro VIN search (Feb 2026, see §4), Winparts (kenteken, unverified), kfzteile24 (HSN/TSN, unverified), Partly |
| **Trust** | used-part condition, garage honesty, hidden repair costs, car history | carVertical, RepairPal fair price, Autobutler, Ovoko, UP GARAGE |
| **Logistics** | tyres and parts must reach the fitter; the car must reach the garage | Oponeo, Blackcircles, Allopneus, Autoway (delivery to fitter); Fixter, Flovi (car collection) |
| **Coordination** | booking a slot that matches the part's arrival; several quotes | BookMyGarage, Vroomly, iDGARAGES, Motointegrator, Mycle |
| **Price** | labour and parts prices are not comparable between garages | BookMyGarage, Autobutler, RepairPal, ClickMechanic (fixed prices) |

Fit is the friction everybody attacks first, and it is also the one incumbents absorb (Allegro VIN search, Autodoc, Inter Cars). The less-absorbed frictions are **price** and **trust in garages** and **logistics of the car itself** (getting it to and from the garage).

## 3. Patterns seen

| Pattern | V1 businesses | Evidence | Note for a Polish founder |
|---|---|---|---|
| P1 compatibility database | Autodoc, RockAuto, Partly, Versable, Winparts | Partly: USD 50 m Series B at USD 500 m valuation (June 2026; another source says USD 90 m at 900 m) ([SiliconANGLE](https://siliconangle.com/2026/06/23/partly-raises-50m-500m-valuation-crack-us-auto-parts-market/)) | investors pay for fit data, but mainstream Polish fit search is now inside Allegro |
| P2 product plus physical step | Oponeo, Blackcircles, Allopneus, Autoway, Tire Rack, Motointegrator | Allopneus: about EUR 310 m revenue, ~6,000 partner fitters ([press release, 2 Oct 2025](https://www.allopneus.com/page/espace-presse/communiqu%C3%A9-presse-20-ans-allopneus-franchise)); Autoway: over 2.8 m tyres a year shipped to fitting shops ([Response](https://matome.response.jp/articles/6418)) | the same pattern wins in PL, FR, UK, US and JP; Oponeo holds it in Poland |
| P3 one checkout across suppliers | PartsTech, Vroomly Parts | PartsTech: 15,000+ repair shops, USD 35 m Series C (2023) ([Business Wire](https://www.businesswire.com/news/home/20230518005047/en/PartsTech-Secures-35M-Series-C-Funding-to-Fuel-Growth-and-Further-Accelerate-Auto-Repair)) | B2B for workshops; needs wholesaler APIs (Inter Cars, others) |
| P4 price comparison | BookMyGarage, Autobutler, RepairPal, iDGARAGES, Vroomly | BookMyGarage: GBP 134 m retail work booked in 2025, bookings +39% ([S&P Aftermarket Insight](https://aftermarketinsight.spglobal.com/news/5084/uks-bookmygarage-sees-39-increase-in-bookings-with-record-134-million-retail-work-in-2025)) | a booking platform earns little per job: iDGARAGES made EUR 3.5 m revenue in 2021 on about 8,000 bookings a month ([J2R Auto](https://j2rauto.com/services/idgarages-une-croissance-a-deux-chiffres-en-2021)), about EUR 36 per booking (computed) |
| P5 trust layer | carVertical, Ovoko, Opisto, Car-Part.com, UP GARAGE | carVertical: revenue EUR 53.9 m (2024) to EUR 75.8 m (2025), Poland a key market ([Motonews](https://www.motonews.pl/wiadomosci/news-14889-przychody-carvertical-wzrosly-o-40-polska-wsrod-kluczowych-rynkow.html)); Ovoko: EUR 20 m Series B, 17 countries, ~6 m monthly visitors ([Vestbee](https://www.vestbee.com/blog/articles/ovoko-raises-20-m)) | both already strong in Poland |
| P6 fit answer sold to shops | Partly, Versable, RevolutionParts | RevolutionParts: nearly USD 3 bn parts sold through dealer shops, 1,800+ dealers (May 2023) ([IBTimes](https://ibtimes.com/revolutionparts-approaches-3-billion-automotive-parts-sold-3692040)) | sells to Allegro and Shoper parts sellers who lack fit data (inference) |
| P9 tool for the professional | PartsTech, Vroomly (SaaS for garages), Opisto, Ovoko (dismantler software) | Vroomly raised EUR 5 m in 2021 to become "the SaaS of all garages in Europe" ([Journal de l'Automobile](https://journalauto.com/services/vroomly-leve-5-millions-deuros-pour-son-developpement/)) | software for dismantlers and workshops is how Ovoko and Opisto got supply |
| New: **car collection and return** (not in T03's list) | Fixter, Flovi, Caroobi (dead), Wrench (mobile) | Flovi in Poland: 200+ partners, over 160,000 car transports in 2025, B2B now, B2C planned for 2026 ([Instalki, 1 Aug 2026](https://www.instalki.pl/news/motoryzacja/serwis-samochodu-bez-wychodzenia-z-domu-flovi-polska/)) | the logistics is the car itself; driver time is the cost; Flovi is ahead in Poland |
| New: **yearly trigger** | BookMyGarage (MOT), Mycle (maintenance reminders), FIXD (fault codes) | inference from the models; no repeat-rate figure found | Poland's yearly badanie techniczne and OC renewal are the analogous triggers (to check in T09) |

## 4. What the numbers say

1. **Retail margins are thin.** Oponeo net margin ~2.5% in 2025 (computed from [BiznesRadar](https://www.biznesradar.pl/a/146110,grupa-oponeo-pl-podsumowanie-wynikow-za-2025-rok)); Delticom operating EBITDA ~4% of EUR 484 m revenue (computed from [Börse Online](https://www.boerse-online.de/dpa-afx/eqs-news-delticom-veroeffentlicht-geschaeftsbericht-2025-umsatz-leicht-ueber-vorjahr-dividendenvorschlag-in-hoehe-von-012-eur-je-aktie-deutsch-512812.html)); Skruvat profit ~3% of SEK 1 bn (computed from [press release](https://www.mynewsdesk.com/se/skruvat-se/pressreleases/rekordomsaettning-foer-skruvat-punkt-se-och-bythjul-punkt-com-personalen-har-gjort-ett-fantastiskt-jobb-3225129)); CarParts.com lost USD 50.4 m on USD 547.5 m revenue in fiscal 2025 ([StockAnalysis](https://stockanalysis.com/stocks/PRTS)). Autodoc is the exception at ~42% gross profit (computed in T03), at scale with own logistics. A founder without inventory should not compete as a parts retailer.
2. **Repeat is moderate.** Autodoc: 18.9 m orders from 9.3 m active customers in 2025, about 2 orders per customer per year (computed from [Autodoc results](https://live.deutsche-boerse.com/news/EQS-News-AUTODOC-solidifies-European-leadership-with-strong-2025-performance-c76106a2-1307-4f01-9eb0-de73003f14c7)). No other repeat or return rate was published by any business in the scan.
3. **Polish incumbents are strong and growing.** Inter Cars group revenue about PLN 21.2 bn in 2025, ~9% up ([Parkiet](https://www.parkiet.com/komunikaty-espi/art44047541-inter-cars-sa-wstepne-wyniki-finansowe-grupy-kapitalowej-inter-cars-za-2025-rok)); Autofixer about EUR 41 m revenue in 10 months of 2026 ([tech.eu](https://tech.eu/2026/10/28/autofixer-receives-eur3m-from-orbit-capital-to-support-european-expansion/)).
4. **Allegro closed the mainstream fit gap in February 2026.** VIN search for car parts, tyres and rims covers about 56 m offers, more than half of ~104 m motoring offers, and marks fitting offers ([Instalki, 12 Feb 2026](https://www.instalki.pl/news/internet/allegro-wprowadza-wyszukiwanie-po-vin-dla-56-mln-ofert/)). Any "find the part that fits my car" idea now starts against this (brief §1, Allegro risk). The ~48 m offers not covered (computed) are where sellers lack fit data: a possible P6 angle.
5. **Money flows to data and software, not to booking.** Funded businesses in 2023–2026 are Partly, PartsTech, Ovoko, carVertical, Versable. Booking platforms are small or were sold: iDGARAGES (EUR 3.5 m revenue), WhoCanFixMyCar (sold to Niterra 2023, then a management buyout, [CAT Magazine](https://www.catmag.co.uk/article/niterra-formerly-ngk-acquires-whocanfixmycar)), Autobutler (owned by PSA).
6. **AI roles found** are fitment and listing data from part numbers (Versable, Partly), photo damage quotes (Fixico), fault-code translation (FIXD) and pricing engines (ClickMechanic, RepairPal). Most retailers show no AI beyond vehicle lookup.

## 5. Graveyard and warnings

| Business | Country | What happened | Lesson | Source |
|---|---|---|---|---|
| Caroobi | Germany | online garage service that took responsibility for the repair, arranged pick-up; USD 20 m Series B in 2018, about USD 30 m raised; domain caroobi.com no longer resolves (checked 2026-11-06); cause of closure not found (unverified) | owning the repair outcome as a middleman is costly; forum complaints about slow repairs | [TechCrunch](https://techcrunch.com/?p=1652030); [autoplenum forum](https://www.autoplenum.de/forum/d/70564/caroobi-erfahrungen-bewertungen-welcher-preis) |
| Tyres on the Drive | UK | mobile tyre fitting with own vans; Halfords stake of up to GBP 8 m in 2017; administrators called in at the end of January 2019 | own fitting vans are capital- and labour-heavy | [TheBusinessDesk, 11 Feb 2019](https://www.thebusinessdesk.com/northwest/?p=2036869); [MMC](https://mmc.vc/latest/tyres-on-the-drive-secures-strategic-investment-from-halfords) |
| CarParts.com | US | revenue down 7% and net loss USD 50.4 m in fiscal 2025 | scale alone does not make parts e-retail profitable | [StockAnalysis](https://stockanalysis.com/stocks/PRTS) |
| Autobutler | Denmark | Danish Competition Council found fixed-price agreements with several hundred garages on the platform (June 2023) | a platform that sets garage prices risks competition law | [KFST](https://en.kfst.dk/news/decisions/2023/20230628-the-danish-competition-council-autobutler-has-infringed-competition-law) |
| YourMechanic | US | absorbed by Wrench in 2022, terms not disclosed; consolidation of mobile repair | mobile repair needs scale in technicians | [GeekWire](https://www.geekwire.com/2022/mobile-car-repair-startup-wrench-acquires-another-competitor-swoops-up-yourmechanic/) |
| Openbay | US | last funding news found is a USD 8 m Series A in 2018; current status not found (unverified) | quote marketplaces stall | [Global Venturing](https://globalventuring.com/blog/2018/06/28/openbay-taps-shell-for-8m-series-a/) |

**Hype warnings in the catalogue:** Fixter's 200% growth figure comes from the 2020 lockdown only; FIXD has many complaints about automatic yearly renewals; Autoway coverage includes paid PR articles; Partly's round size is reported inconsistently; Mister Auto's EUR 300 m target for 2016 was not shown as met. No case of growth only from free delivery or discounts was found, but no business published its paid-ads share either.

## 6. Ten most promising analogues for Poland (quick Polish check)

The full check is in T09/T10. Quick searches on 2026-11-06 (Google via the search tool, 4 Polish queries, listed in §7).

| # | Analogue (row) | Why promising | Exists in Poland? (quick check) | What a Polish version would need |
|---|---|---|---|---|
| 1 | BookMyGarage (V1-UK-002) | price comparison + booking around a yearly trigger; GBP 134 m work booked in 2025 | partly: Dobry Mechanik (directory with paid workshop package), Motointegrator (booking with parts); no price-comparison-with-booking site found; an article says 20% of workshops do not answer price enquiries ([elektromobilni.pl](https://elektromobilni.pl/20-warsztatow-nie-odpowiada-na-zapytania-porownuj-ceny-przed-serwisem/)) | workshop price lists for 5–10 standard jobs (oil, brakes, timing belt), a booking calendar, a hook on badanie techniczne dates |
| 2 | Fixter (V1-UK-005) | collection and return removes the logistics of the car | yes, B2B: Flovi (160,000 transports in 2025, B2C planned 2026) | partner garages, drivers with insurance; Flovi is ahead; physical work is the founder's problem |
| 3 | Partly / Versable (V1-NZ-001, V1-US-012) | AI fitment data is a funded product | Allegro has VIN search for ~56 m offers; no Polish fit-data supplier for small sellers found (not searched yet) | TecDoc or OE data licence, or AI extraction from listings; buyers are Allegro/Shoper parts sellers |
| 4 | PartsTech (V1-US-003) | one search across wholesalers for workshops; 15,000+ shops in the US | not checked; workshops use wholesaler portals (Inter Cars) | API or catalogue access to Inter Cars, Auto Partner and other wholesalers; B2B sales to workshops |
| 5 | Fixico (V1-NL-001) | photo-based body damage quote | no photo-quote service found; only price lists ([kb.pl](https://kb.pl/cenniki/miejskie/wyciaganie-wgniecen-_mot/zielona-gora/)); a guide warns that quotes for the same damage can differ by 100% ([cenauslug.pl](https://cenauslug.pl/przewodnik/naprawy-blacharskie-i-powypadkowe)) | body-shop partners, a photo-to-estimate model; insurers and leasing firms steer most repairs (inference) |
| 6 | RepairPal (V1-US-006) | fair-price estimate plus certified garages | price lists by city exist ([kb.pl mechanics price list](https://kb.pl/porady/cennik-mechanikow-samochodowych-sprawdz-ceny-w-twoim-miescie-_mot/)); no guarantee programme found | labour-time data (licensed), local rates, garages willing to honour a price |
| 7 | Ovoko / Opisto (V1-LT-001, V1-FR-006) | used parts with software for dismantlers | yes: ovoko.pl in Polish | no gap at the general level; a niche (vans, classic cars, motorcycles) would need dismantler supply |
| 8 | Oponeo / Allopneus / Autoway (V1-PL-001, V1-FR-005, V1-JP-001) | delivery to fitter, proven in 4 countries | yes: Oponeo (~1,100 Polish fitting points), Motointegrator | none: closed; home fitting is the open variant, but see Tyres on the Drive |
| 9 | Aroundhome wallbox (V1-DE-006) | lead fee for EV charger installation | not checked; general lead platforms (Oferteo, Fixly) exist | certified electricians; EV fleet size data (T09) |
| 10 | Mroauto (V1-CZ-001) | small specialist (VAG parts, new/used/remanufactured) selling cross-border via eBay | not checked | a niche brand focus and supplier access; the model is a seller on Allegro/eBay, not a platform |

Common Polish needs across these: invoices with VAT for workshops (B2B), BLIK and Przelewy24 for consumers, InPost for parcels, a workshop network for anything with a physical step, and licensed catalogue data (TecDoc or OE) for anything that claims fit. Safety-critical parts (brakes, steering) sold as "fits" carry liability (criteria F7).

## 7. Coverage

- **Businesses catalogued:** 48 rows, 13 countries: United States 12, United Kingdom 6, France 6, Germany 6, Poland 5, South Korea 3, Netherlands 2, Japan 2, Lithuania 2, Denmark 1, Sweden 1, Czechia 1, New Zealand 1. Nordics: DK, SE. JP/KR: both. CEE: PL, LT, CZ.
- **Searches:** 49 web searches (English, Polish, German, French, Dutch, Swedish, Czech, Japanese), 12 page fetches, 3 batches of homepage link checks (about 60 homepages).
- **Searches that found nothing useful (13):** Caroobi insolvency (two queries), Goo-net Pit garage count (JA), Auto Kelly revenue (CZ), Bildelsbasen dismantler count (SE), Louis revenue (DE), Openbay status, wallbox installation start-up funding (DE), Oscaro 2024 revenue (FR), kfzteile24 2024 revenue (DE), Mister Auto recent revenue (FR), Dobry Mechanik traction (PL), RevZilla recent figures, Mroauto revenue (CZ). Also no plate-number (not VIN) parts search found in Poland.
- **Polish quick queries (2026-11-06):** "porównanie cen warsztatów samochodowych rezerwacja serwisu online", "odbiór samochodu do serwisu i odwiezienie usługa Warszawa", "części samochodowe wyszukiwanie po numerze rejestracyjnym sklep", "wycena naprawy blacharskiej ze zdjęcia online". Findings are in §6 and §4.4.
- **Gaps:** no motorcycle-parts or camper-parts specialist with traction figures beyond Louis and RevZilla; no Korean or Japanese parts-fit player; repeat and return rates are almost never public.

## 8. Takeaways for T09–T11

1. Do not build a parts retailer or a general "parts that fit" search: thin margins (2.5–4%) and Allegro's VIN search (Feb 2026).
2. The open frictions in Poland are **garage price and trust** (P4 + a yearly trigger) and **car logistics** (collection and return), but booking alone earns little per job (iDGARAGES ~EUR 36 per booking, computed) and Flovi is already in Poland.
3. **Fit data for sellers** (P6) is where investors put money abroad (Partly, Versable); in Poland the buyer would be the parts seller whose offers sit outside Allegro's VIN coverage. Data licensing (TecDoc/OE) is the first thing to check.
4. **Workshop-side tools** (P3/P9: multi-wholesaler search, dismantler software) are how Ovoko and Opisto got supply; B2B sales to workshops are slow for a 40 h/month founder.
5. T09 should mine Polish demand for: garage price comparison, "ile kosztuje wymiana ... w [miasto]", body-damage quotes from photos, used parts for vans and motorcycles, and fit data among Allegro sellers.

## Unverifiable links (403, timeouts; open in a browser)
In the catalogue: aftermarketnews.com (RockAuto), businesswire.com (PartsTech), repairpal.com, louis.de, thebusinessdesk.com (Tyres on the Drive), oscaro.com, auto-infos.fr (Opisto), autobutler.co.uk, skruvat.se, autoway.jp, mroauto.cz (468), ebay.de store page (Mroauto). The wowtale.net articles (Mycle, Carsub, Dr.Car) pass the link check but returned 403 to the fetch tool, so their figures come from search-result summaries only.
