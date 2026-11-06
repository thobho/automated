# V5 — Small business and professional buying: Polish demand signals

T09 of Phase 3 ([task](../tasks/09-demand-mining.md), [brief](../BRIEF.md)). Scan: [research/verticals/V5-small-business-buying.md](../research/verticals/V5-small-business-buying.md). All sources accessed **2026-11-06**.

## Method and limits
Same as [V1](V1-vehicle-parts.md#method-and-limits): Google autocomplete (AC), Polish interface, about 32 queries for V5 (example: [`części do minikoparki`](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=cz%C4%99%C5%9Bci%20do%20minikoparki)). Professional buyers search less on Google and more through wholesalers and phone calls, so AC under-represents V5 (inference). City suffixes are biased to Lower Silesia by the requester's location; the strong local pattern ("hurtownia X [town]") is still a real signal that buyers look for a nearby wholesaler. No forum threads were read for V5 in this run. Monthly volume is **unverified** for every item.

## Signals
| # | Query | Type | What the buyer needed | What AC shows |
|---|---|---|---|---|
| S1 | AC `hurtownia dla` | AC | wholesalers by trade | gastronomy, carpenters (stolarzy), florists, nail stylists, confectioners, pets, pigeons |
| S2 | AC `hurtownia fryzjerska` | AC | hairdressing wholesaler | all 10 suggestions are local (Wrocław, Jelenia Góra, Świdnica, Legnica …): buyers look for a nearby shop |
| S3 | AC `hurtownia gastronomiczna` | AC | catering wholesaler | local towns plus "online", "spożywcza" |
| S4 | AC `części do maszyn gastronomicznych` + `części do pieca konwekcyjnego` | AC | catering equipment parts | "części do pieca konwekcyjnego unox" |
| S5 | AC `części do maszyn do lodów` | AC | soft-serve machine parts | Carpigiani, "do lodów włoskich" |
| S6 | AC `części do ekspresu kolbowego` | AC | espresso-machine parts | De'Longhi and generic; `części do zmywarki gastronomicznej` returned **no** suggestions |
| S7 | AC `hurtownia stomatologiczna` | AC | dental wholesaler | Aneks (named), cities (Wrocław, Warszawa, Poznań, Koszalin, Zabrze, Łódź, Szczecin, Gdańsk) |
| S8 | AC `części do unitu stomatologicznego` | AC | dental-chair (unit) parts | "części składowe unitu stomatologicznego" |
| S9 | AC `hurtownia weterynaryjna` | AC | veterinary wholesaler | "online", "leki", cities |
| S10 | AC `części do wózka widłowego` | AC | forklift parts | RAK and Bułgar (old Bulgarian Balkancar forklifts), GPW, Mitsubishi, Toyota, Linde, Clark, Yale, Jungheinrich |
| S11 | AC `części do minikoparki` | AC | mini-excavator parts | Kingway (Chinese), Yanmar, Bobcat, Wacker Neuson, Kubota, JCB 8018/8014, Hitachi |
| S12 | AC `części do koparki` | AC | excavator parts | Liebherr, Atlas, KM 251, O&K, Ford 550, "ostrówek" (old Polish excavators) |
| S13 | AC `części do zagęszczarki` | AC | plate-compactor parts | Project, Wacker, Zipper, Bomag, Kaltmann, Ammann, Pezal, Lumag, Dro-Masz |
| S14 | AC `części do agregatu` | AC | generator and farm-implement parts | "prądotwórczego", "malarskiego" (paint sprayer), farm cultivators (Agro-Masz, Mandam, Unia) |
| S15 | AC `części do kombajnu` | AC | combine-harvester parts | Anna Z-644 and Z-614, Bolko, Bizon (old Polish machines), Claas, Volvo S830 |
| S16 | AC `części do ciągnika` | AC | tractor parts | Ursus C-330, MTZ, Zetor, Zefir 85, Solis, Case, Massey Ferguson, Ford 2000 |
| S17 | AC `części do maszyn szwalniczych` | AC | industrial sewing-machine parts | Juki, "przemysłowych", Łódź and Pabianice (textile cluster), Majmasz |
| S18 | AC `łożyska gdzie kupić` | AC | bearings | "gdzie kupić łożyska do pralki (electrolux)", "…w warszawie", "…do hulajnogi" |
| S19 | AC `uszczelnienia hydrauliczne` | AC | hydraulic seals | "sklep", "katalog", "tłokowe", "rodzaje", cities: buyers need the right profile |
| S20 | AC `paski klinowe` | AC | V-belts | "wymiary", "do kosiarek", "castorama", towns |
| S21 | AC `części do kas fiskalnych` | AC | cash-register parts | the phrase is suggested (1 suggestion) |
| S22 | AC `części do myjki` | AC | pressure-washer parts | Kärcher (K5, window vac), Lavor, Riwall, Parkside |
| S23 | AC `zakupy dla firm` | AC | business buying | "allegro zakupy dla firm", "ikea…", "auchan…", "zakupy hurtowe dla firm", "zakupy firmowe z prywatnego konta" (invoice question) |

## Candidate hard-to-find items (feeds T10)
Frequency proxy as in V1 (AC = number of autocomplete suggestions); no verified volumes.

| # | Item | Signals | Frequency proxy (source) | Friction |
|---|---|---|---|---|
| V5-D01 | parts for old Eastern-bloc forklifts (RAK, Bułgar/Balkancar) | S10 | AC (10) | finding |
| V5-D02 | parts for Chinese mini-excavators (Kingway and similar) | S11 | AC (10) | finding, fit |
| V5-D03 | parts for old Polish excavators (KM 251, Ostrówek) | S12 | AC (10) | finding |
| V5-D04 | plate-compactor parts across many small brands | S13 | AC (10) | fit |
| V5-D05 | parts for old Polish combines (Anna, Bolko, Bizon) | S15 | AC (10) | finding |
| V5-D06 | tractor parts (Ursus C-330, MTZ, Zetor) | S16 | AC (10) | price, fit |
| V5-D07 | farm implement parts (cultivators, Agro-Masz, Mandam) | S14 | AC (10) | fit |
| V5-D08 | catering equipment parts (Unox ovens, Carpigiani) | S4, S5 | AC (2 + 3) | finding, logistics (downtime) |
| V5-D09 | dental-unit spare parts | S8 | AC (2) | finding, regulation |
| V5-D10 | one checkout across dental wholesalers | S7 | AC (10) | price |
| V5-D11 | nearby hairdressing and beauty wholesaler with delivery | S1, S2 | AC (10, all local) | logistics |
| V5-D12 | industrial sewing-machine parts (Juki) | S17 | AC (8) | fit |
| V5-D13 | hydraulic seals by profile and size | S19 | AC (10) | fit |
| V5-D14 | bearings and V-belts by size | S18, S20 | AC (6 + 10) | fit |
| V5-D15 | pressure-washer parts (Kärcher, Lavor) | S22 | AC (10) | fit |
| V5-D16 | business purchases with VAT invoice from consumer shops | S23 | AC (10) | coordination (invoice) |

## Notes for T10 and T11
- The densest V5 cluster is **parts for machines whose maker is gone or far away** (old Polish and Eastern-bloc machines S10, S12, S15, S16; Chinese mini-excavators S11): the same "discontinued or orphan brand" pattern as V1 (Saab, Chinese cars) and V2 (discontinued washers).
- Trade wholesalers are searched by town (S2, S3, S7): a delivery-to-salon or ordering-app idea (V5 scan takeaway) would compete with nearby counters.
- Not checked: Polish dental distributor names, food-wholesaler counts, laser-cutting quote demand (V5 scan list).
