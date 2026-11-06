# V2 — Home, climate and appliance parts and consumables: Polish demand signals

T09 of Phase 3 ([task](../tasks/09-demand-mining.md), [brief](../BRIEF.md)). Scan: [research/verticals/V2-home-climate-appliance.md](../research/verticals/V2-home-climate-appliance.md). All sources accessed **2026-11-06**.

## Method and limits
Same as [V1](V1-vehicle-parts.md#method-and-limits): Google autocomplete (AC) from the public suggestion endpoint with a Polish interface, about 30 queries for V2 (example: [`części do lidlomixa`](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=cz%C4%99%C5%9Bci%20do%20lidlomixa)); AC shows that a phrase is searched, not how often. Elektroda.pl threads were found through web search, but the forum timed out for the fetch tool on 2026-11-06, so their content comes from **search-result summaries** (marked "summary"); open them in a browser before quoting. Monthly volume is **unverified** for every item.

## Signals
| # | Query or link | Type | What the person needed | What they were told / found |
|---|---|---|---|---|
| S1 | [elektroda topic3633231](https://www.elektroda.pl/rtvforum/topic3633231.html) | forum (summary) | control module for a Bosch WAW24540PL washing machine (about 500 zł) | shop North.pl could not get it from the maker, "product unavailable"; another user said it can be ordered; module was repaired instead |
| S2 | [elektroda topic3961802](https://www.elektroda.pl/rtvforum/topic3961802.html) | forum (summary) | drum spider (krzyżak) for Electrolux EWT136551W | the service technician said there are no parts for this model any more |
| S3 | [elektroda topic4153141](https://www.elektroda.pl/rtvforum/topic4153141.html) | forum (summary) | programmer module for Electrolux EWC 1350 | technician: new part unavailable; user bought a used module from a donor machine and asked whether a different serial fits (fit friction) |
| S4 | [elektroda topic4096321](https://www.elektroda.pl/rtvforum/topic4096321.html) | forum (summary) | electronic module for a cooker hood | owners gave up on a new module because of the price and asked for one from a dismantled unit |
| S5 | [elektroda topic3854078](https://www.elektroda.pl/rtvforum/topic3854078.html) | forum (summary) | repair of an audio/RTV device | the service said it cannot repair it because the spare part is not available |
| S6 | [Enerad: Kaisai heat pump page](https://enerad.pl/producent/pompa-ciepla-kaisai-prezentacja-oferta-kontakt/) | installer page (summary) | Kaisai heat-pump parts | the installer lists "longer warranty repair when spare parts are not available" among the brand's drawbacks |
| S7 | AC `części do pompy ciepła` | AC | heat-pump parts | brands Kaisai, Haier, Panasonic, IVT, Stiebel Eltron, Buderus; "części zamienne do pompy ciepła" |
| S8 | AC `części do klimatyzatora` | AC | AC unit parts | Kaisai, Gree, Haier, AUX, LG, "przenośnego" |
| S9 | AC `pilot do klimatyzatora` | AC | replacement AC remote | Haier, Gree, LG, Kaisai, Sinclair, Mitsubishi, AUX, Eberg, "przenośnego" |
| S10 | AC `filtry do rekuperatora` | AC | ventilation (MVHR) filters by model | Wanas, Komfovent (Domekt R 450 V), Zehnder (Q350), Vaillant, Defro, Vent Clear, Aeris Next 350: buyers search by exact unit model |
| S11 | AC `części do lidlomixa` | AC | spare parts for Lidl's Monsieur Cuisine | "gdzie kupić części do lidlomixa", "części zamienne", "oryginalne", "lidl czesci do lidlomixa" (7 suggestions) |
| S12 | AC `części do termomixa` + `naprawa termomix` | AC | Thermomix TM5, TM6, TM31 parts and repair | parts for TM5/6/7; "naprawa thermomix po gwarancji" |
| S13 | AC `części do maszynki zelmer` | AC | Zelmer meat-grinder parts by model | model numbers ZMM4055B, 886.84, "Diana", "5", "8"; shops named (Media Expert, RTV Euro AGD, Allegro) |
| S14 | AC `akumulator do parkside` | AC | Parkside (Lidl) tool batteries | "akumulator do parkside zamiennik", "akumulator parkside do czego pasuje", 12V/20V, 4/8 Ah: compatibility question |
| S15 | AC `części do okapu` | AC | cooker-hood parts | store and house brands Kernau, Akpo, VDB, Berdsen, Amica, Franke |
| S16 | AC `części do kuchenki gazowej` | AC | gas cooker parts | Amica, Beko, Gorenje, Mastercook, Ravanson, Indesit |
| S17 | AC `części do kotła` / `części do pieca gazowego` | AC | boiler parts | coal/pellet boilers Defro, Kostrzewa, "na ekogroszek", Atmos; gas Vaillant, Junkers, Termet, Saunier Duval, Immergas, Viessmann |
| S18 | AC `uszczelka do lodówki` | AC | fridge door gasket by brand | Beko, Whirlpool, Amica, Samsung, Polar, Electrolux, Indesit, Bosch |
| S19 | AC `filtr do lodówki` | AC | side-by-side fridge water filters | Samsung (HAFEX/EXP), LG, Haier, Liebherr, Hisense |
| S20 | AC `filtr do oczyszczacza` | AC | air-purifier filters by model | Xiaomi (Air Purifier 4, 4 Compact), Philips, Samsung, Sharp, Electrolux |
| S21 | AC `części do odkurzacza` | AC | vacuum parts | Dyson, Xiaomi, Dreame, Silvercrest (Lidl), "piorącego parkside" |
| S22 | AC `gdzie kupić części do` | AC | general | top suggestions include "do parkside", "do pralki", "do kuchenki gazowej", "do lidlomiksa", "do maszynki zelmer" |

## Candidate hard-to-find items (feeds T10)
Frequency proxy as in V1 (AC = number of autocomplete suggestions for the phrase); no verified volumes.

| # | Item | Signals | Frequency proxy (source) | Friction |
|---|---|---|---|---|
| V2-D01 | control modules and programmers for older washing machines (Bosch, Electrolux) | S1, S3 | 2 forum threads (summary) | finding, fit |
| V2-D02 | drum spiders and bearings for discontinued washer models | S2 | 1 forum thread; AC "gdzie kupić łożyska do pralki electrolux" (see V5) | finding |
| V2-D03 | cooker-hood electronics and parts for store brands (Kernau, Akpo, Berdsen) | S4, S15 | AC (10) + 1 thread | finding |
| V2-D04 | heat-pump spare parts for Chinese/Asian brands (Kaisai, Haier) | S6, S7 | AC (9) + installer page | finding, logistics (warranty delay) |
| V2-D05 | AC unit parts and replacement remotes | S8, S9 | AC (7 + 10) | fit |
| V2-D06 | MVHR (rekuperator) filters by exact unit model, recurring | S10 | AC (10) | fit, recurring |
| V2-D07 | Lidlomix (Monsieur Cuisine) spare parts | S11 | AC (7) | finding (no official parts shop found) |
| V2-D08 | Thermomix out-of-warranty parts and repair | S12 | AC (5 + 10) | finding, price |
| V2-D09 | Zelmer grinder and kitchen-robot parts by model number | S13 | AC (10) | fit |
| V2-D10 | Parkside battery compatibility and replacements | S14 | AC (10) | fit |
| V2-D11 | gas-cooker parts (burners, knobs, thermocouples) by brand | S16 | AC (10) | fit |
| V2-D12 | coal and pellet boiler parts (Defro, Kostrzewa) | S17 | AC (10) | finding |
| V2-D13 | fridge door gaskets by model | S18 | AC (10) | fit |
| V2-D14 | side-by-side fridge water filters (originals vs. clones), recurring | S19 | AC (10) | fit, trust, recurring |
| V2-D15 | air-purifier filters by model, recurring | S20 | AC (10) | fit, recurring |
| V2-D16 | robot and cordless vacuum parts (Dyson, Xiaomi, Dreame) | S21 | AC (10) | fit |

## Notes for T10 and T11
- Two patterns: (1) **discontinued-model parts** where the maker's channel says "niedostępne" and the answer is a used part from a donor machine (S1–S5): a fit-checked used-parts exchange is the gap; (2) **recurring consumables by exact model** (filters S10, S19, S20) where the friction is fit, not availability.
- Store and private-label brands (Lidl Parkside/Silvercrest/Monsieur Cuisine, Kernau, Berdsen, MPM) appear often in autocomplete; T10 should test whether their parts can be bought at all.
- Not checked in this run: Czyste Powietrze paperwork demand (from the V2 scan takeaways); left for T10/T11.
