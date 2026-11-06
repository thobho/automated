# V1 — Vehicle parts and car-related buying: findability test

T10 of Phase 3 ([task](../tasks/10-findability-test.md), [brief](../BRIEF.md)). Items come from [demand/V1-vehicle-parts.md](../demand/V1-vehicle-parts.md) (candidate IDs in brackets). All queries run by hand on **2026-11-06**.

## Method and limits (same for V1–V5)
- **Allegro:** public listing page returned **HTTP 403** to the fetch tool on 2026-11-06 (`allegro.pl/listing?string=…`). Not retried, no bypass. Allegro is therefore **not tested**; where web search showed Allegro Lokalnie or Allegro pages, that is noted.
- **Google (Polish):** not reachable directly. "Web" below means the **WebSearch tool** (engine not stated, results not localised to google.pl), queried in Polish. It is a stand-in for Google, weaker than a real google.pl search.
- **Ceneo:** public search page `ceneo.pl/;szukaj-<query>` read with the fetch tool: result count, titles, lowest price, number of shops per product. Ceneo does **not** show delivery times in the listing; shop names are mostly hidden in the listing (brand/shop prefixes in titles such as "Motoroy", "Wilmat", "Martig" are recorded as seen).
- **OLX:** public search page `olx.pl/oferty/q-<query>/`: count and first 10 titles. OLX listings do not show private vs business in the fetched text.
- At most 3 attempts per item. Each attempt is one query on one site. **Delivery time** was not visible on any of these listing pages unless stated; it is recorded as "not shown".
- Verdicts: **E** = found easily (1 try), **W** = found with effort (2–3 tries, guessing a name, or only used/classified), **N** = not found / foreign only.

## Items

### 1. Front brake pads, Jaecoo 7 (V1-D02)
- Try 1, Ceneo [`klocki hamulcowe jaecoo 7`](https://www.ceneo.pl/;szukaj-klocki+hamulcowe+jaecoo+7): 1 result, a **rear** OEM set "Chery … Jaecoo 7 Oem 204002032AA", 190 zł, 1 shop.
- Try 2, OLX [`klocki hamulcowe jaecoo`](https://www.olx.pl/oferty/q-klocki-hamulcowe-jaecoo/): 70 listings, nearly all other makes; two listings for **Jaecoo 5 / Omoda 5** discs+pads (370.53 zł, Łódź), none for Jaecoo 7 front.
- Try 3, web `klocki hamulcowe przód Jaecoo 7 zamiennik`: only the [Interia article](https://motoryzacja.interia.pl/wiadomosci/news-1280-zl-za-klocki-do-jaecoo-mozna-je-kupic-tylko-w-aso,nId,21396613) (ASO only, 1280 zł) and generic czesciauto24 pages without Jaecoo fitment.
- **Verdict: N.** Price: ASO 1280 zł (press); no aftermarket front set seen. Polish sellers: 0 for front. Seller type: dealer only.

### 2. Rear bumper, Omoda 5 (V1-D01)
- Try 1, Ceneo [`zderzak tylny omoda 5`](https://www.ceneo.pl/;szukaj-zderzak+tylny+omoda+5): 12 results, all "Martig" tuning diffusers and spoilers (80–242 zł), no bumper.
- Try 2, OLX [`zderzak omoda 5`](https://www.olx.pl/oferty/q-zderzak-omoda-5/): 238 listings; first 10 include used/new rear bumpers 370 zł (Knurów, part 602001563AA) and 2,399 zł (Opole, complete, pearl white), front bumpers 700–5,199 zł.
- Try 3, web `zderzak tylny Omoda 5 sklep`: no shop; an Allegro Lokalnie front-bumper ad and Czech accessory shops.
- **Verdict: W** (only classifieds, mostly used). Price 370–2,399 zł (rear). Sellers: ≥2 rear on OLX first page. Delivery not shown. Seller type: classified (private or dismantler, not labelled).

### 3. Oil filter, MG ZS (V1-D02)
- Try 1, Ceneo [`filtr oleju mg zs`](https://www.ceneo.pl/;szukaj-filtr+oleju+mg+zs): 29 results, mostly noise (cone air filters, "MG" as a Master-Sport code); "Mg Motor Filtr Oleju 10604737" 114.19 zł and "Oe Mg Filtr Oleju LPW100180" 100.23 zł, 1 shop each, ZS fitment not stated in the title.
- **Verdict: W** (the buyer must know the part number to tell which hit fits). Price ~100–114 zł OE. Sellers: 1 per product. Delivery not shown.

### 4. Control arm, Tesla Model 3 (V1-D03)
- Try 1, Ceneo [`wahacz tesla model 3`](https://www.ceneo.pl/;szukaj-wahacz+tesla+model+3): 21 results (Lemförder, Febi Bilstein, Triscan, GSP, NTY, Srline, Febest), 47–1,870 zł, 1–3 shops each.
- **Verdict: E.** Price 47–1,870 zł. Sellers: many products, 1–3 shops each. Delivery not shown. Shops (parts e-shops).

### 5. Ignition coil / DI cassette, Saab 9-3 (V1-D05)
- Try 1, Ceneo [`kaseta zapłonowa saab 9-3`](https://www.ceneo.pl/;szukaj-kaseta+zap%C5%82onowa+saab+9-3): 11 products (coils and cassettes, NTY, Maxgear, OE 12787707), 53–635 zł, 1–3 shops.
- **Verdict: E.** The orphan-brand signal from T09 does not hold for this common service part.

### 6. Carburettor, Fiat 126p (V1-D06)
- Try 1, Ceneo [`gaźnik fiat 126p`](https://www.ceneo.pl/;szukaj-ga%C5%BAnik+fiat+126p): 413 products but the first 30 contain **no carburettor** (body panels, toy models, shock absorbers).
- Try 2, Ceneo [`gaźnik 126p weber`](https://www.ceneo.pl/;szukaj-ga%C5%BAnik+126p+weber): 0 results.
- Try 3, web `gaźnik Fiat 126p nowy sklep cena`: only sprzedajemy.pl classifieds: new-old-stock Weber 28S1A 900 zł (private), rebuilt/used 100–500 zł, one company ad 200 zł; repair kit 100 zł.
- **Verdict: W.** Price 100–900 zł. Sellers: several private classifieds, no shop in results. Delivery not shown.

### 7. Entrance-door seal, Knaus camper (V1-D07)
- Try 1, web `uszczelka drzwi wejściowych Knaus kamper części sklep`: no Knaus door seal; Reimo (camper shop) and car-seal pages; sprzedajemy.pl has other Knaus parts and Thetford door seals.
- Try 2, OLX [`uszczelka drzwi knaus`](https://www.olx.pl/oferty/q-uszczelka-drzwi-knaus/): 70 listings, none Knaus (car and freezer seals).
- **Verdict: N** (no item seen in 2 tries; a third would need the part number from Knaus). Polish sellers: 0.

### 8. Window, Niewiadów N126 caravan (V1-D08)
- Try 1, OLX [`szyba niewiadów n126`](https://www.olx.pl/oferty/q-szyba-niewiad%C3%B3w-n126/): 71 listings; one used left side window 80 zł (Dobczyn), many other N126 parts.
- Try 2, web `szyba okno przyczepa Niewiadów N126 nowa sklep`: no shop; sprzedajemy.pl ad for a clear side window 900×550 mm 540 zł; the maker (niewiadow.pl) still exists and lists a company shop.
- **Verdict: W** (used or classified only; a new window needs a phone call to the maker). Price 80–540 zł. Sellers: 2 classifieds seen.

### 9. Caravan tyre 185R14C (V1-D09)
- Try 1, Ceneo [`opona 185R14C przyczepa kempingowa`](https://www.ceneo.pl/;szukaj-opona+185R14C+przyczepa+kempingowa): 5 results: tyre from 278.99 zł (2 shops, free delivery), complete wheels Linglong/Kenda 420–900 zł.
- **Verdict: E.** (Normal tyre shops not visible in this narrow query; Oponeo-type shops very likely stock it: not checked.)

### 10. Wide camper mirror for Fiat Ducato (V1-D10)
- Try 1, Ceneo [`lusterko kamperowe ducato`](https://www.ceneo.pl/;szukaj-lusterko+kamperowe+ducato): 0 results.
- Try 2, Ceneo [`lusterko fiat ducato kamper`](https://www.ceneo.pl/;szukaj-lusterko+fiat+ducato+kamper): 173 results: standard OE-type Ducato mirrors and glasses (Fast, TYC, View Max), 24–982 zł; no add-on wide "kamper" mirror in the first 30.
- **Verdict: W** (stock mirrors easy; the camper-specific wide mirror needs a different word).

### 11. CVT drive belt, Linhai 500 quad (V1-D12)
- Try 1, Ceneo [`pasek napędowy linhai 500`](https://www.ceneo.pl/;szukaj-pasek+nap%C4%99dowy+linhai+500): 15 results, none for Linhai (Suzuki, Polaris, CF 450/500 belt 262 zł).
- Try 2, web `pasek napędowy wariatora Linhai 500 quad sklep`: only eBay.de (belt 939×36.7 "for Linhai 500 Stels 600", about 195 USD per the search summary).
- **Verdict: N / foreign only.** Polish sellers: 0 seen.

### 12. Parts for Bashan 200 quad (V1-D12)
- Try 1, Ceneo [`części bashan 200`](https://www.ceneo.pl/;szukaj-cz%C4%99%C5%9Bci+bashan+200): 180 products (clutch 180 zł, stator 48.90 zł, gearbox 116.50 zł, axle 663 zł), shop prefixes Motoroy, Atut, Abiwa, Wilmat; 1 shop each.
- **Verdict: E.** Small specialist shops (single shop per product).

### 13. Brake pads, Dodge Ram 1500 2019, US import (V1-D04)
- Try 1, Ceneo [`klocki hamulcowe dodge ram 1500 2019`](https://www.ceneo.pl/;szukaj-klocki+hamulcowe+dodge+ram+1500+2019): 9 results, 60–775 zł; one explicitly "Ram 1500 DT 2019-2024" rear 198 zł; others for older generations.
- **Verdict: E** for the part; the generation fit still needs checking (3 of 9 are for 1993–2008).

### 14. Carburettor, WSK 125 (V1-D11)
- Try 1, Ceneo [`gaźnik wsk 125`](https://www.ceneo.pl/;szukaj-ga%C5%BAnik+wsk+125): 25 products: complete carburettors 66.50–157.78 zł plus repair kits 8–29 zł (Motoroy, Wilmat, Moretti), 1 shop each.
- **Verdict: E.**

### 15. Original Toyota oil filter 04152-YZZA1 outside the dealer (V1-D13)
- Try 1, Ceneo [`filtr oleju toyota 04152-YZZA1`](https://www.ceneo.pl/;szukaj-filtr+oleju+toyota+04152-YZZA1): 1 product "Toyota Oe … Oryginal", from 73.99 zł, 2 shops.
- **Verdict: E** (with the part number; trust that it is genuine is not checkable from the listing).

### 16. Sliding side window for a van conversion (V1-D14)
- Try 1, web `okno przesuwne do busa zabudowa kamper sklep`: Polish results (Reimo PL, Kaufland PL "PrimeVan" hinged windows 700×400 to 1200×500 mm) are **hinged**, not sliding; sliding windows only from US (Nomadic Supply) and Brandrup (DE, model-specific).
- **Verdict: N / foreign only** for sliding windows (hinged windows are easy).

### 17. Window glass for a Hymer camper (V1-D07)
- Try 1, OLX [`hymer okno`](https://www.olx.pl/oferty/q-hymer-okno/): 76 listings; most first-page windows from **one seller in Borkowo** (Dometic S4/S7P, Polyplastic, sized 500×300 to 1040×570 mm), 600–1,690 zł, titles list several body brands.
- **Verdict: W** (findable, but fit is by size and brand list; one dominant seller).

## Verdict table
| # | Item | Verdict | Price seen | PL sellers seen | Seller type |
|---|---|---|---|---|---|
| 1 | Jaecoo 7 front pads | N | ASO 1,280 zł (press) | 0 | dealer only |
| 2 | Omoda 5 rear bumper | W | 370–2,399 zł | ≥2 (OLX) | classifieds |
| 3 | MG ZS oil filter | W | 100–114 zł | 1 per product | shop |
| 4 | Tesla Model 3 control arm | E | 47–1,870 zł | many | shops |
| 5 | Saab 9-3 coil/cassette | E | 53–635 zł | many | shops |
| 6 | Fiat 126p carburettor | W | 100–900 zł | few | classifieds |
| 7 | Knaus door seal | N | – | 0 | – |
| 8 | Niewiadów N126 window | W | 80–540 zł | 2 | classifieds |
| 9 | 185R14C caravan tyre | E | 279–900 zł | ≥2 | shops |
| 10 | Wide camper mirror Ducato | W | 24–982 zł (stock mirrors) | many (stock only) | shops |
| 11 | Linhai 500 CVT belt | N | ~195 USD (eBay.de) | 0 | foreign |
| 12 | Bashan 200 parts | E | 7–663 zł | many | small shops |
| 13 | Dodge Ram 1500 2019 pads | E | 60–775 zł | several | shops |
| 14 | WSK 125 carburettor | E | 67–158 zł | several | small shops |
| 15 | Toyota OE oil filter | E | 74 zł | 2 | shops |
| 16 | Van sliding side window | N | – (hinged only in PL) | 0 sliding | foreign |
| 17 | Hymer camper window | W | 600–1,690 zł | 1 dominant | classifieds |

**Counts:** E 7, W 6, N 4 of 17. **Findability gap rate: 10/17 = 59%** (N or W). Allegro not tested (403), which likely **overstates** the gap: Allegro is the main channel for used and classic parts.

## Most promising item groups
1. **Service and collision parts for new Chinese brands (Jaecoo, Omoda, BAIC):** the only items where the part simply does not exist in Polish aftermarket channels (item 1), and body parts only appear used on OLX (item 2). Matches T09's strongest signal. Risk: the gap closes as importers stock parts.
2. **Camper and caravan habitation parts (Knaus, Hymer, Niewiadów):** fit is by body brand, size and part number; sellers are few or one dominant classified seller (items 7, 8, 17). A fit-checked catalogue over German suppliers is the gap.
3. **Chinese quad/ATV parts by exact model (Linhai):** some brands are well served (Bashan, item 12), others only via eBay.de (item 11): coverage is uneven by brand.
4. **Van-conversion components (sliding windows):** Polish supply covers hinged windows only; sliding units are foreign (item 16).
5. **Classic Polish car parts (126p):** findable but only through classifieds with unclear condition (item 6): a trust problem more than a finding problem.

Not promising on this evidence: mainstream service parts with a part number (Tesla, Saab, Toyota OE, US-import pads, WSK): **found easily** on Ceneo.
