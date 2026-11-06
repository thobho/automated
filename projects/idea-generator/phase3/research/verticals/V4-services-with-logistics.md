# V4 — Services with a logistics step: vertical scan

T07 of Phase 3 ([task](../../tasks/07-scan-v4-services-with-logistics.md), [brief](../../BRIEF.md)). Catalogue: [catalogue/V4-services-with-logistics.csv](../../catalogue/V4-services-with-logistics.csv) (37 businesses, 11 countries). All sources accessed **2026-11-06**. Friction types use the brief's six: **finding, fit, trust, logistics, coordination, price**. Pattern ids P1–P10 are from [friction-patterns.md](../global/friction-patterns.md). "Computed" marks my arithmetic; "unverified" marks what I could not confirm; "inference" marks my reading, not a source.

Overlap with earlier scans: home-appliance repair and heat-pump or boiler installation (Murfy, BOXT, Thermondo, Hometree, Kurashi no Market) are in [V2](V2-home-climate-appliance.md); car workshops and collection (Fixter, ClickMechanic, Autofixer) are in [V1](V1-vehicle-parts.md). They are not repeated here.

## 1. What the vertical is

Buying a service where something must travel: the item goes to a craftsman (repair by post, sharpening, dry cleaning) or a person comes to the buyer (assembly, mounting, mobile repair). The buyer's problem is less "which service" than "who, how do I get the item there, and can I trust them with it". The scan found six kinds of business:

| Type | Rows | Examples |
|---|---|---|
| Lead and booking marketplaces for trades | 10 | Thumbtack, Checkatrade, MyHammer, Werkspot, Mittanbud, Soomgo, Fixly, Oferteo, NejŘemeslníci, Helpling |
| Repair or care by post (central workshop) | 9 | Clothes Doctor, Repamera, Knife Aid, Knife Sharp, Cobbler Concierge, Orange Heel, MyPhoneRepair, The Restory (dead), Digital Care |
| Pickup and return by courier or locker | 7 | Laundryheap, Laundrapp (folded), Zipjet (merged), Lenet, Laundrygo, Sojo, Shyp (dead) |
| Installation or assembly booked with a purchase | 4 | Angi (Walmart), Taskrabbit (IKEA), Puls, Otovo |
| Craftsman networks sold through brands or shops | 4 | Tilli, The Seam, woshwosh (Żabka), Velofix (franchise vans) |
| Trade-in by post | 3 | ecoATM/Gazelle, musicMagpie, iCracked (on-demand repair, status unclear) |

## 2. Friction types present

| Friction | How it shows up in V4 | Who removes it (catalogue rows) |
|---|---|---|
| **Finding** | good craftsmen (cobbler, tailor, sharpener) are local, offline and not searchable; outside big cities there may be none | Clothes Doctor, Cobbler Concierge (brings big-city quality to the whole country, [The Manual](https://themanual.com/fashion/cobbler-concierge-shoe-repair)), The Seam, Fixly, Oferteo |
| **Fit** | weak in V4: the question is whether a repair is possible and what it costs, answered by a photo quote | Clothes Doctor (quote from photos, [Ellen MacArthur Foundation](https://ellenmacarthurfoundation.org/circular-examples/clothes-doctor)), Cobbler Concierge (text estimate) |
| **Trust** | handing over a valuable item (designer bag, phone with data) to an unknown workshop; quality of a home visitor | Checkatrade (vetting and 6 m reviews), Stiftung Warentest-tested repairers, Digital Care (90-day warranty) |
| **Logistics** | the item must get to the workshop and back; the visitor must come with tools | Knife Aid (prepaid envelopes both ways), Lenet and Laundrygo (courier or door locker), Żabka shops as drop-off (Digital Care, woshwosh) |
| **Coordination** | booking a slot that fits the delivery of a purchased TV or wardrobe | Angi at Walmart checkout, Taskrabbit for IKEA, Otovo (quote, installer, financing) |
| **Price** | quotes are opaque; buyers ring three trades | Thumbtack, Oferteo, MyHammer (multiple quotes); Angi fixed prices (assembly from USD 49) |

**Logistics and finding dominate.** Fit, the strongest friction in V1–V2, is almost absent: a service has no part number. The AI role is therefore narrower: classify a photo into a repair type and price, route the job to a craftsman, draft the quote (§9).

## 3. Patterns seen

| Pattern | V4 businesses | Evidence | Note for a Polish founder |
|---|---|---|---|
| **New: repair by post to one central workshop** | Clothes Doctor, Knife Aid, Cobbler Concierge, Orange Heel, MyPhoneRepair, Digital Care | Clothes Doctor customers order 3–4 times a year at about GBP 80 per order ([Ellen MacArthur Foundation](https://ellenmacarthurfoundation.org/circular-examples/clothes-doctor)); Orange Heel about 20,000 pairs a year ([ecnomikata](https://ecnomikata.com/pr/387)); Knife Aid USD 89 for 7 knives with free shipping both ways, about USD 12.7 per knife (computed, [Zwilling](https://www.zwilling.com/us/zwilling-sharpening-service-knife-aid-professional-knife-sharpening-by-mail-7-knives-9800481/9800481.html)) | founder-sized when the workshop is a partner, not owned (The Restory owned its workshop and was liquidated, §5); InPost lockers make the round trip cheap |
| P2 product plus the physical step in one checkout | Angi at Walmart, Taskrabbit at IKEA, Otovo | Walmart sells 150+ Angi services online, furniture assembly from USD 49, TV mounting from USD 79 ([Localogy](https://www.localogy.com/2022/02/whats-behind-the-angi-walmart-partnership/)); IKEA bought Taskrabbit ([TechCrunch](https://techcrunch.com/2017/09/28/ikea-buys-taskrabbit/)) | the retailer owns the customer and takes the slot in-house; in Poland Media Expert and Morele already sell mounting at checkout (§7) |
| Lead fee / subscription for trades (P9-adjacent) | Thumbtack, Oferteo, Soomgo, MyHammer, Werkspot, Mittanbud, Checkatrade | Thumbtack about USD 400 m revenue FY2024 ([Wikipedia](https://en.wikipedia.org/wiki/Thumbtack_(company))); Soomgo KRW 62.4 bn revenue and KRW 13.7 bn operating profit 2024 ([demoday](https://demoday.co.kr/recruits/6293)); Oferteo PLN 42 m net revenue FY2022/23 ([Oferteo](https://biuroprasowe.oferteo.pl/releases/finanse)) | profitable and durable, but the Polish market is taken by Oferteo and Fixly |
| P10-like owned pickup network | Laundrygo, Lenet, Laundryheap | Laundrygo KRW 55.7 bn revenue 2024, about 35× its 2019 revenue (computed, [Startup Recipe](https://en.startuprecipe.co.kr/archives/23206)); Lenet 400,000+ users by 2020 ([ITmedia](https://www.itmedia.co.jp/business/articles/2011/30/news012_4.html)) | the winners own factories and lockers and raised large rounds; not founder-sized |
| **New: shop network as the drop-off point** | Digital Care and woshwosh via Żabka | about 10,000 Żabka shops accept phones for repair ([wiadomoscihandlowe](https://www.wiadomoscihandlowe.pl/handel-i-dystrybucja/siec-zabka-dorzuca-kolejna-propozycje-do-pakietu-wygodnych-uslug-tym-razem-chodzi-o-mozliwosc-szybkiej-naprawy-smartfona-2505449)); shoe repair since June 2023 and tailoring since Dec 2025 ([wiadomoscihandlowe](https://www.wiadomoscihandlowe.pl/najwieksze-sieci-handlowe/zabka/zabka-naprawi-i-wyczysci-ci-buty-siec-convenience-i-firma-woshwosh-wprowadza-nowa-usluge-ile-kosztuje-2447238), [wiadomoscihandlowe](https://www.wiadomoscihandlowe.pl/franczyza-w-handlu/franczyza-spozywcza/poprawki-krawieckie-w-zabce-tak-jest-to-mozliwe-2530830)) | a Polish-specific pattern; Żabka is a strong incumbent for the drop-off step |
| **New: repair-as-a-service sold to brands (B2B2C)** | Tilli, The Seam, Clothes Doctor (brand vouchers) | Tilli: about 250 tailors in about 20 cities (2022), Shopify app for brands, extended to Europe in 2024 ([FashionUnited](https://fashionunited.fr/actualite/mode/tilli-de-la-retouche-a-domicile-aux-partenariats-avec-marques-premiums-et-grands-magasins/2022010628716), [FashionUnited](https://fashionunited.fr/actualite/mode/la-start-up-francaise-tilli-exporte-son-offre-en-europe/2024022834381)) | the brand pays and brings the customer, which removes CAC; EU textile rules could create a timing window (to check in T09, not sourced here) |

## 4. What the numbers say

1. **The money in V4 is in lead fees, not in doing the service.** Thumbtack (about USD 400 m), Checkatrade (GBP 131.5 m in 2025, 53,000+ member trades, [Wikipedia](https://en.wikipedia.org/wiki/Checkatrade)), Soomgo (operating margin about 22%, computed) and Oferteo (PLN 42 m) are profitable or large. Oferteo earns about PLN 23 per confirmed order (computed: PLN 42 m / 1.85 m orders). Mittanbud and three Nordic sister sites sold at NOK 550 m enterprise value ([Vend](https://vend.com/ir/releases/vend-marketplaces-asa-vend-signs-agreement-to-sell-its-skilled-trades-marketplace-portfolio)).
2. **Doing the physical step yourself is where V4 businesses die** (§5): Shyp, Laundrapp, The Restory, Zipjet (merged). Survivors either own heavy assets with large funding (Laundrygo, Lenet) or route the job to partners.
3. **Repeat is real in care services**: Clothes Doctor reports 3–4 orders per customer per year at about GBP 80 (GBP 240–320 a year per customer, computed), and Lenet runs a paid membership. Phone repair and installation are one-off.
4. **Price points for the physical step** (anchors for T13 unit economics): Knife Aid about USD 12.7 per knife sharpened with shipping included (computed); Angi assembly from USD 49, TV mounting from USD 79; in Poland TV mounting costs on average about PLN 200 above 50 inches and PLN 100–160 below (cost guide, may be outdated, [cenauslug](https://cenauslug.pl/dom-i-ogrod/montaz-uchwytu-tv-na-scianie)).
5. **Regulation as a driver**: France's bonus réparation nearly quadrupled subsidised repairs in 2024; smartphone repairs rose from about 70,000 (2023) to almost 250,000 (2024) ([Linfodurable/AFP](https://www.linfodurable.fr/conso/lutilisation-du-bonus-reparation-en-forte-progression-en-2024-48895)). No equivalent Polish subsidy was found in this run (not searched in depth; T09).
6. **Published take rates are rare.** None of the 37 rows published a commission percentage; only Soomgo's margin can be computed.

## 5. Graveyard and warnings

| Business | Country | What happened | Lesson | Source |
|---|---|---|---|---|
| Shyp | US | shut 27 Mar 2018; CEO said it chased consumers too long and expanded too fast; cut NY, Chicago, LA in 2017 | the pickup step costs more than consumers pay; in Poland InPost already solved it | [TechCrunch](https://techcrunch.com/2018/03/27/on-demand-shipping-startup-shyp-is-shutting-down/) |
| The Restory | UK | founders left Feb 2023 after US investors took control; proposed liquidation; high costs, thin margins; about 850 items returned | do not own the workshop; luxury repair margins are thin | [FashionUnited](https://fashionunited.com/executive/report/the-restory-put-into-proposed-liquidation-after-co-founders-exit/2023022852532), [Leatherbiz](https://leatherbiz.com/News/164361) |
| Laundrapp | UK | merged with Zipjet 2019, administration Feb 2020, sold to Laundryheap 2022 | laundry pickup is a consolidating, low-margin market | [tech.eu](https://tech.eu/2020/02/18/laundrapp-acquired/), [tech.eu](https://tech.eu/2022/04/25/dirty-business-on-demand-laundry-service-platform-laundryheap-buys-laundrapp/) |
| Zipjet | UK/DE | Rocket Internet laundry start-up; Series B 2018, merged into Laundrapp 2019 | as above | [deutsche-startups](https://www.deutsche-startups.de/2019/03/11/zipjet-laundrapp-fusion/?amp=1) |
| iCracked | US | 2013 "Uber for iPhone repairs"; current status unverified | on-demand technician visits did not become the norm; mail-in and shop drop-off did | [TechCrunch](https://techcrunch.com/2013/02/23/icracked) |
| Puls (pivot) | US | from phone repair to TV mounting, appliances and a warranty product; over USD 90 m raised by 2018 | one-off repair visits needed a wider basket and insurance revenue | [Globes](https://en.globes.co.il/en/article-device-repair-co-puls-raises-50m-1001251661) |
| Clothes Doctor (shift) | UK | added care products and detergent subscriptions in 2019 next to repair | products give repeat revenue that repair alone lacks | [Ellen MacArthur Foundation](https://ellenmacarthurfoundation.org/circular-examples/clothes-doctor) |
| Tilli (pivot) | FR | from at-home tailoring for consumers to B2B for fashion brands | brands pay; consumers are expensive to acquire (inference) | [FrenchWeb](https://www.frenchweb.fr/retail-la-startup-tilli-leve-12-million-deuros-pour-semparer-de-la-tendance-de-lupcycling/378546) |
| musicMagpie | UK | revenue fell to GBP 136.6 m FY2023 and 13% in H1 2024, losses widened | trade-in holds stock and is price-competitive | [Shares](https://sharesmagazine.co.uk/news/market/1719566488584253300/musicmagpie-widens-loss-as-revenue-slumps-13-in-first-half) |

Also in [friction-patterns.md §4](../global/friction-patterns.md): Homejoy and Washio (same lessons: disintermediation, cheap service margin).

## 6. Poland: what exists

- **Lead platforms are taken**: Oferteo (PLN 42 m revenue, IPO prospectus filed, [Comparic](https://comparic.pl/oferteo-zlozylo-prospekt-do-knf-spolka-planuje-debiut-na-gpw/)) and Fixly (OLX Group).
- **Drop-off is taken by Żabka**: phone repair (Digital Care), shoes and tailoring (woshwosh). Buyers bring the item to a shop and collect it there, not door to door.
- **Installation at checkout is done by the retailers themselves**: Media Expert sells a carry-in, wall-mounting and set-up package (promotion page, [Media Expert](https://www.mediaexpert.pl/lp,k-5174-pakiet-uslug-za-1zl)); Morele adds TV mounting in the basket and delivery takes one working day longer ([Morele](https://www.morele.net/montaz-telewizora-na-scianie-6894959/)).
- **Not found in quick searches** (each one query, 2026-11-06, see §8): a Polish knife sharpening by post service, a laundry or dry-cleaning pickup app, a tailor-by-post service outside Żabka.

## 7. Ten most promising analogues for Poland (quick Polish check)

| # | Analogue (rows) | Exists in Poland? (quick search 2026-11-06) | What a Polish version would need |
|---|---|---|---|
| 1 | Clothing repair by post with a photo quote (Clothes Doctor, Repamera) | partly: woshwosh tailoring through Żabka since Dec 2025, drop-off only | 3–5 partner tailors, InPost labels both ways, photo-to-price classifier, invoice for the repair (umowa o dzieło, rękojmia for work, [Infor](https://www.infor.pl/prawo/prawa-konsumenta/konsument-uslugi/685499,Zle-wykonana-usluga-u-szewca.html)) |
| 2 | Knife sharpening by post (Knife Aid, Knife Sharp) | not found (1 query) | 1–2 sharpeners; check InPost and courier rules for blades (not found in search); a channel through knife shops or chefs' groups |
| 3 | Shoe repair by post (Cobbler Concierge, Orange Heel) | partly: woshwosh via Żabka since June 2023 (current status unverified) | partner cobblers outside Żabka's model; door-to-door courier rather than shop drop-off |
| 4 | Repair service sold to fashion brands (Tilli, The Seam) | not checked | a Shoper/Shopify app that books repair for a brand's customers; tailor network; brand pays |
| 5 | Installation slot for marketplace sellers (Angi at Walmart, Taskrabbit at IKEA) | big chains do it themselves (Media Expert, Morele); for Allegro sellers not checked | local installers per city, a booking widget, a fixed price list (TV mounting PLN 100–200, [cenauslug](https://cenauslug.pl/dom-i-ogrod/montaz-uchwytu-tv-na-scianie)) |
| 6 | Dry cleaning by courier or locker (Lenet, Laundryheap) | not found (1 query) | a partner cleaner with spare capacity; InPost locker round trip; graveyard warns on margins |
| 7 | Mobile bike service booking (Velofix) | not checked | booking layer over existing mobile mechanics (no vans owned); seasonal |
| 8 | Vetted-trade badge (Checkatrade) | Oferteo and Fixly offer reviews; real vetting not checked | checks of registration (CEIDG), insurance and references; trades pay a yearly fee |
| 9 | Mail-in device repair with an independent quality test (MyPhoneRepair) | yes: Digital Care (Żabka and operators) | no gap |
| 10 | Instant-quote coordinated installation (Otovo) | V2 found Pompy.app and Enerad for heat pumps and PV | see V2; no new gap here |

## 8. Coverage

- **Businesses catalogued:** 37 rows: United States 10, United Kingdom 10, Germany 3, Poland 4, Norway 2, Japan 2, South Korea 2, Netherlands 1, France 1, Sweden 1, Czechia 1. Nordics: SE, NO (plus FI and DK sites inside the Mittanbud row). JP/KR: both. CEE: PL, CZ.
- **Searches:** about 40 web searches (English, Polish, German, French, Czech, Japanese, Korean) and 1 page fetch (Ellen MacArthur Foundation), then the link checker.
- **Searches that found nothing useful (14):** The Restory funding, iCracked closure, Hodinový manžel network size (CZ, dropped from the catalogue), MyHammer revenue, Werkspot/Instapro revenue, Helpling 2024 figures, Cobbler Concierge funding, Repamera prices and volumes, Checkatrade 2024 revenue, German mail-in repair market size, Japanese shoe-repair-by-post volumes beyond one press release, Polish laundry pickup app, Polish knife sharpening by post, Polish tailoring by post.
- **Polish quick queries (2026-11-06):** "pralnia z odbiorem i dostawą kurier aplikacja Warszawa startup", "ostrzenie noży wysyłkowo paczkomat usługa ostrzenia noży przez pocztę", "naprawa telefonu z odbiorem kurierem darmowy kurier serwis door-to-door Polska", "Fixly OLX usługi liczba wykonawców zleceń", "Oferteo.pl liczba zapytań wykonawców przychody", "krawiec online przeróbki krawieckie wysyłkowo paczkomat naprawa ubrań przez internet", "naprawa butów wysyłkowo szewc online kurier Żabka naprawa obuwia", "montaż telewizora na ścianie usługa przy zakupie RTV Euro AGD Media Expert cena montażu". Findings in §6–7.
- **Gaps:** no Dutch, Nordic or CEE repair-by-post business with figures; no published commission rates; watch, jewellery, instrument and camera repair by post not searched; Baltic and Slovak services not found; EU right-to-repair and textile rules as a Polish timing window not checked.

## 9. Takeaways for T09–T11

1. Do not build a lead marketplace or a drop-off network: Oferteo, Fixly and Żabka hold them in Poland.
2. The founder-shaped V4 ideas are **repair or care by post to partner craftsmen** (clothing, shoes, knives), with InPost lockers both ways and a photo-to-quote classifier as the AI step, and **repair-as-a-service sold to fashion brands** (Tilli pattern), where the brand pays and brings customers.
3. Repeat must come from care, not repair: Clothes Doctor's 3–4 orders a year and detergent subscriptions are the model; one-off repairs (phones) do not carry a small business.
4. The graveyard says: never own the workshop or the fleet (Shyp, The Restory, Laundrapp).
5. T09 should mine Polish demand for: "ostrzenie noży wysyłkowo", "krawiec przeróbki wysyłka", "naprawa butów kurier", "pralnia z odbiorem", "montaż telewizora Allegro", "naprawa kurtki puchowej", "wymiana zamka w kurtce".

## Unverifiable links (403, timeouts; open in a browser)
Link check 2026-11-06: 0 dead after fixes. Unverifiable (403/500): mediaexpert.pl (installation package), angi.com, icracked.com, eu-startups.com (Sojo), pl.trustpilot.com (Knife Sharp), se.trustpilot.com (Repamera), winfuture.de (Stiftung Warentest report), soomgo.com. Figures from search-result summaries only (page not fetched): Thumbtack revenue, Soomgo revenue, Laundrygo revenue, Oferteo revenue, Checkatrade revenue, Lenet users, Orange Heel volume, Otovo units, Mittanbud project count, bonus réparation counts, Polish TV mounting prices.
