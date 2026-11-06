# Poland: logistics, fulfilment, returns and the law (T02, part 2)

Baseline for Phase 3. Each finding has a source URL and the access date. "Computed" means the arithmetic is mine. "Unverified" means a secondary or dated source I could not confirm against a current primary one. Carrier prices change several times a year and brokers (Furgonetka, Apaczka, Sendit) sell below list price; their price tables load by script and could not be read with the fetch tool. **Law: flagged for business design, not legal advice.**

Related files: [ecommerce.md](ecommerce.md), [monetisation.md](monetisation.md).

## 1. Parcel network and prices

**L1. InPost is the default delivery network: 28,165 lockers in Poland and 763 m domestic parcels in 2025.** InPost FY2025: Poland APMs (Paczkomaty) 28,165 (+11%), 4.03 m locker compartments in Poland, 3,907 PUDO points; Polish Q4 2025 volume 220.2 m parcels (+5% YoY); 2026 outlook "mid single-digit volume growth in Poland" and lower expected profitability in Poland. A Kantar survey (Nov 2025) cited by InPost: 94% of consumers receive parcels via InPost lockers. Gemius 2025 (see [ecommerce.md](ecommerce.md) E4): 83% of online buyers use parcel lockers, 87% of them InPost. Domestic 2025 volume of 763.1 m (+8%) is from a search summary of InPost's trading update (unverified).
Source: [InPost FY 2025 press release](https://inpost.eu/sites/default/files/2026-03/InPost%20FY%202025%20Press%20Release_0.pdf), accessed 2026-11-06.

**L2. A locker parcel costs a business about PLN 14.55–21.04; returns about PLN 12.84–18.55.** InPost price list from 1 March 2026 (media report; net or gross not stated): business Paczkomat A 14.55, B 16.51, C 21.04 PLN; business returns from a locker A 12.84, B 14.55, C 18.55 PLN; retail (private sender) XS 11.49, A 16.49, B 18.49, C 20.49 PLN; retail "Szybkie Zwroty" 12.99 PLN for A–C. Volume contracts and brokers go lower (not public).
Source: [Chip.pl, "InPost zmienia cennik usług", Feb 2026](https://www.chip.pl/2026/02/inpost-zmiana-cennik-uslug-taniej), accessed 2026-11-06.

**L3. Courier cost per kg falls steeply with weight, then jumps above 30 kg.** InPost business courier, standard service, PLN excluding a 13% fuel surcharge (same source as L2): up to 1 kg 25.30; 2–5 kg 32.07; 5–10 kg 37.13; 15–20 kg 48.95; 25–30 kg 59.08; **30–40 kg 89.41; 40–50 kg 107.99**. Per kg at the top of each band (computed, with fuel surcharge): 10 kg ≈ PLN 4.20/kg, 30 kg ≈ PLN 2.23/kg, 50 kg ≈ PLN 2.44/kg. List prices: a contract rate is usually lower (unverified).
Source: [Chip.pl, Feb 2026](https://www.chip.pl/2026/02/inpost-zmiana-cennik-uslug-taniej), accessed 2026-11-06.

**L4. On Allegro the seller pays a Smart! delivery surcharge of PLN 0.99–11.49 per order.** Shoper Learn (March 2026), seller-paid Smart! surcharge by order value (30–44.99 / 45–64.99 / 65–99.99 / 100–149.99 / 150+ PLN): InPost lockers 1.59 / 3.09 / 4.99 / 7.59 / 9.99; ORLEN Paczka 0.99 / 1.89 / 3.59 / 5.89 / 7.79; DPD courier 1.99 (30–44.99), 5.79 (65–99.99), 11.49 (150+); DHL courier 1.79, 5.39, 10.89 for the same bands. Allegro negotiates far cheaper delivery than a small shop gets (compare L2): one reason sellers stay on Allegro. Secondary source (Allegro's help pages block the fetch tool).
Source: [Shoper Learn, "Prowizje Allegro"](https://www.shoper.pl/learn/?p=60750), accessed 2026-11-06.

**L5. ORLEN Paczka is the cheap alternative point/locker network, about PLN 12–15 gross via a broker.** Sendit broker, gross: S 12.76, M 13.39, L 14.67 PLN (informational; exact price after log-in); limit 25 kg for size L; surcharges (net): non-standard shipment PLN 243.90, large parcel PLN 19.00, wrong declared size/weight PLN 12.20. Other guides found by search give 11.99 / 12.99 / 13.99 PLN retail. Sources disagree slightly and the page's own dimension tables are inconsistent; ORLEN's official list was not read.
Source: [Sendit, "Orlen Paczka cennik"](https://www.sendit.pl/?p=10026), accessed 2026-11-06.

**L6. DPD list prices (late 2023) ran PLN 17–37.49 by weight up to 31.5 kg.** kb.pl table updated 13 Dec 2023: up to 1 kg 17.99, 3–5 kg 22.49, up to 10 kg 27.49, up to 20 kg 32.49, up to 31.5 kg 37.49 PLN; bands above 20 kg not accepted at DPD Pickup points. Dated; no 2026 domestic DPD list found: **treat as an old reference only**.
Source: [kb.pl, "Cennik DPD"](https://kb.pl/cenniki/uslugi/cennik-dpd-sprawdz-aktualne-ceny-nadania-paczek/), accessed 2026-11-06.

**L7. Pocztex (Poczta Polska) takes parcels up to 30 kg, and up to 50 kg for a fee.** Pocztex domestic sizes: S–XL up to 20 kg, 2XL (sum of sides ≤ 250 cm) up to 30 kg; 30–50 kg with a paid additional service; delivery by point, parcel machine or courier, D+1 expected, same-day "Na Dziś" on selected routes. Prices are in a PDF that was not read.
Source: [Pocztex, domestic parcels](https://www.pocztex.pl/en/pocztex-domestic-parcels), accessed 2026-11-06.

**L8. Oversized and heavy goods leave the cheap network.** Locker and point networks stop at size C (InPost), 25 kg (ORLEN, L5) or 20 kg (Pocztex S–XL, L7), and ORLEN charges PLN 243.90 net for a non-standard shipment; couriers stop at 31.5 kg (DPD; L6) or charge a step above 30 kg (L3, L7). Items like boiler parts, heat-pump units, tyres in sets or exhausts therefore cost PLN 60–110+ per shipment at list price (computed from L3), or need pallet freight. I found no public pallet price list in this run (gap for T05/T08). Sources: L3, L6, L7.

## 2. Fulfilment and dropshipping partners

**L9. Public 3PL prices start around EUR 1 per order plus storage per box.** Zunapro (a Polish fulfilment provider), net prices: storage per month small box EUR 2, medium EUR 4, large EUR 7, Euro pallet EUR 18; pick & pack EUR 1 for a one-item order, +EUR 0.35 per extra item, EUR 3 for a large-box order; returns processing EUR 0.60; minimum contract 3 months, start from 10 SKUs; shipping billed separately. Other 3PLs (Omnipack, Fulfillment Polska) publish no price list; Omnipack is listed with a USD 1,000+ minimum project on Clutch (unverified). Using a 3PL means holding inventory, which the founder excludes; it is a reference cost for a supplier's own fulfilment.
Source: [Zunapro, warehousing](https://www.zunapro.com/poland/en/warehousing), accessed 2026-11-06.

**L10. Allegro runs its own fulfilment (One Fulfillment), now with Arvato.** At launch (January 2022): basic fee PLN 2.49–17.70 net per product by volume and weight, extended storage from PLN 4.99 net, extra fees for returns and withdrawals, shipping at Allegro delivery rates; for business accounts. Search results (2026) report an agreement with Arvato to run a new central-Poland centre (unverified). Prices are from 2022: **historical**.
Source: [Antyweb, "One Fulfillment by Allegro", 25 Jan 2022](https://antyweb.pl/one-fulfillment-by-allegro), accessed 2026-11-06.

**L11. Dozens of Polish wholesalers ship direct to the end customer, with integration via XML/API.** Base.com list (updated 26 June 2026), "examples, not a ranking": electronics and appliances AB, Action, AGDpartner, Incom, TelForceOne, Unimet; home and garden Ikonka, Jumi, Mondex, VidaXL, Halmar; toys Leker.pl, MIKI, LEAN Toys; beauty Bio Planet, Primavera. Flow: the shop takes the retail price, pays the wholesale price, the wholesaler packs and ships (often "blind shipping"); the **seller handles returns and complaints**. Fees named but not priced: dropshipping surcharge, integration fee, handling fee, returns handling. Indicative margins (the article's own estimate): electronics single digits to 10–20%, accessories up to 30–35%, home and garden about 40%, toys 20–40%.
Source: [Base.com, "Hurtownie dropshipping w Polsce [LISTA 2026]"](https://base.com/pl-PL/blog/?p=23566), accessed 2026-11-06.

## 3. Return rates by category

**L12. Fashion returns are an order of magnitude above electronics, furniture and parts.** No current Polish category data found (Merce and a 2018 Trusted Shops piece give no usable numbers). Best proxy, EHI survey of 124 large DACH retailers (Nov 2025, not representative): 12.2% of fashion retailers get back more than half of orders and 24.5% get back 36–50%; 85.7% of electronics retailers have return rates up to 10%; about 93% of furniture retailers up to 10%; fashion is about 90% of all returned items. Zalando: about 50% of ordered items returned. Polish rates are believed to be lower than German (Poles pay return shipping by default, L14) but that is **unverified**.
Source: [TextilWirtschaft, "Neue EHI-Studie: So haben sich die Retourenquoten entwickelt", 27 Nov 2025](https://www.textilwirtschaft.de/business/news/neue-ehi-studie-so-haben-sich-die-retourenquoten-entwickelt-253155), accessed 2026-11-06; [Logistik Heute, 27 Nov 2025](https://logistik-heute.de/news/e-commerce-logistik-warum-die-zahl-der-retouren-nicht-sinkt-237100.html), accessed 2026-11-06.

## 4. Consumer law (flag, not legal advice)

**L13. 14-day withdrawal from receipt of the goods; up to 12 months more if the buyer was not told.** For distance contracts the period is 14 days, running from the day the consumer receives the item (from the last item for split deliveries, the first for recurring deliveries). If the trader did not inform about the right, it extends by 12 months. Sending the statement within the period is enough.
Source: [UOKiK, "Terminy" (prawo odstąpienia)](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/terminy-odstapienie/), accessed 2026-11-06.

**L14. The buyer pays return shipping unless the seller agreed otherwise; the seller refunds the cheapest delivery option.** The consumer bears direct costs of returning the item, unless the seller agreed to cover them or did not inform about them; the seller refunds original delivery up to the cheapest option offered; the consumer is liable for loss of value beyond normal inspection. A platform that promises "free returns" takes this cost on itself (L2: PLN 12.84–18.55 per locker return).
Source: [UOKiK, "Koszty"](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/koszty/), accessed 2026-11-06.

**L15. Exceptions that matter for Phase 3: custom-made goods and goods inseparably combined after delivery.** No withdrawal right for items made to the consumer's specification, perishable goods, sealed hygiene items once unsealed, and goods that "by their nature" become inseparably combined with other things after delivery; also sealed software/recordings once opened. Whether a part fitted into a car or boiler falls under the "combined" exception is a question for a lawyer; do not build a model on it.
Source: [UOKiK, "Wyłączenia prawa do odstąpienia"](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/wylaczenia-prawa-do-odstapienia/), accessed 2026-11-06.

**L16. The seller is liable for non-conformity for 2 years from delivery and must answer a complaint within 14 days.** Seller liability for non-conformity ("niezgodność towaru z umową", the successor of rękojmia in consumer sales) lasts 2 years from delivery; the seller must answer a complaint within 14 days or is deemed to accept it; the consumer chooses repair or replacement first, price reduction or withdrawal after (withdrawal only for a significant non-conformity). "The responsible party is the seller": a dropshipping reseller is the seller and carries this, even if the wholesaler shipped.
Source: [UOKiK, "Niezgodność towaru z umową"](https://prawakonsumenta.uokik.gov.pl/reklamacja/niezgodnosc/), accessed 2026-11-06.

**L17. GPSR applies since 13 December 2024: every online listing needs producer data and an EU responsible person.** Regulation (EU) 2023/988: Art. 16 requires an economic operator established in the EU for products placed on the market; Art. 19 sets information required in distance sales; Art. 22 sets obligations for online marketplaces. Allegro made producer and responsible-person contact data (email or contact form) mandatory in its API from 10 March 2025. Search summaries report a Polish enforcement act effective 3 January 2026 (Dz.U. 2025 poz. 1826) and UOKiK plans for over 10,000 checks in 2026 (**unverified**). Implication: importing direct from non-EU suppliers is a compliance burden; Polish/EU distributors carry it.
Source: [EUR-Lex, Regulation (EU) 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj), accessed 2026-11-06; [Allegro Developer, GPSR change, 24 Feb 2025](https://developer.allegro.pl/news/gpsr-10-marca-wdrozymy-zmiany-w-zarzadzaniu-danymi-teleadresowymi-producenta-i-osoby-odpowiedzialnej-wwPlY05GPfW), accessed 2026-11-06.

## 5. VAT for cross-border supply

**L18. Above EUR 10,000 a year of EU-wide B2C distance sales, VAT is due in the buyer's country, filed through OSS.** The EU-wide threshold of EUR 10,000 replaced national thresholds (July 2021); below it, VAT may be charged in the seller's state. The One Stop Shop lets a seller register in one member state and declare and pay EU VAT there (quarterly). IOSS covers imported low-value consignments up to EUR 150. For CZ/SK/Baltic expansion of a small shop this is an admin task, not a blocker. Polish sources give the threshold as PLN 42,000 (unverified).
Source: [European Commission, VAT One Stop Shop](https://vat-one-stop-shop.ec.europa.eu/index_en), accessed 2026-11-06.

## What this means for Phase 3 (my reading, not a sourced finding)
- **Small parcels are cheap and solved** (L1–L5): PLN 12–21 per locker parcel at list price, lower on contract. A PLN 15 parcel on a PLN 100 order is 15% of the price, which is why Allegro's subsidised delivery (L4) is hard to beat on small items.
- **Heavy and bulky goods are where logistics friction is real** (L3, L7, L8): above 30 kg costs jump; coordination (pallet, installer collects) could be a service.
- **Dropshipping shifts the legal risk to the reseller** (L11, L16, L17): the 2-year liability and GPSR data sit with whoever sells, so a no-inventory model still needs supplier terms that pass returns and complaints back.
- **Returns are low in parts, electronics and furniture** (L12), which favours V1, V2 and V5 over fashion-like hobby categories.
