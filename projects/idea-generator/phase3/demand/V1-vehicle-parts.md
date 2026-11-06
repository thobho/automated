# V1 — Vehicle parts and car-related buying: Polish demand signals

T09 of Phase 3 ([task](../tasks/09-demand-mining.md), [brief](../BRIEF.md)). Scan: [research/verticals/V1-vehicle-parts.md](../research/verticals/V1-vehicle-parts.md). All sources accessed **2026-11-06** unless a different date is given.

## Method and limits
- **Google autocomplete (AC):** Google's public suggestion endpoint, Polish interface (`hl=pl&gl=pl`), one request per query, about 25 queries for V1, e.g. [`części do chińskich samochodów`](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=cz%C4%99%C5%9Bci%20do%20chi%C5%84skich%20samochod%C3%B3w). A suggestion means enough people type that phrase for Google to propose it; it is **not** a volume figure. Suggestions are biased by the requester's location: city names in the results point to Lower Silesia (Wrocław, Legnica, Wałbrzych), so read city lists as an example only.
- **Forum and press:** web search plus reading the page. Elektroda.pl threads timed out for the fetch tool on 2026-11-06, so where only a search summary was seen this is said. Press articles that report owners' posts from Facebook groups are marked **secondary**.
- **Not available:** Google Trends and Allegro block the tools (see PROGRESS T01); OLX search for "szukam" in car parts returned mostly sale ads ("ponad 1000 ogłoszeń", nearly all offers, not requests), so OLX "szukam" is a weak source here. No keyword-planner volumes: **monthly volume is unverified for every item** and is given as a frequency proxy only.

## Signals
| # | Query or link | Type | What the person needed | What they were told / found |
|---|---|---|---|---|
| S1 | AC `części do chińskich samochodów` | AC | parts for Chinese-brand cars | suggestions include "dostępność części do chińskich samochodów", "czy są części do chińskich samochodów", "jaka jest dostępność części…", "czy części … są drogie": people ask whether parts exist at all |
| S2 | AC `części do mg` | AC | MG ZS, MG HS, MG3 parts | suggestions "dostępność części do mg", "czy czesci do mg sa drogie" |
| S3 | [Autoblog Spider's Web, 3 Jun 2026](https://autoblog.spidersweb.pl/ile-czeka-sie-na-czesci-do-chinskich-samochodow-klienci-rynek-polska) | press, secondary (Facebook group posts) | body parts after collisions, Omoda 5 and 9 | in the "Omoda Polska" group (over 30,000 members per the article) owners report about 8 months for an Omoda 9 rear bumper, 3–5 months for a front bumper, about 4 months for an Omoda 5 rear window; a BAIC owner waited over a month; importers say "wystarczy poczekać dwa lub trzy dni"; one owner says a UOKiK complaint threat sped things up |
| S4 | [Instalki, 21 Feb 2026](https://www.instalki.pl/news/motoryzacja/omoda-czesci-dostepnosc/) | press, secondary (Facebook post in an Omoda 9 group) | three parts for a collision repair, Omoda 9 | dealer: parts come "by container from China", first estimate two weeks, no repair date; owner expects to wait until spring |
| S5 | [Interia: 1280 zł za klocki do Jaecoo](https://motoryzacja.interia.pl/wiadomosci/news-1280-zl-za-klocki-do-jaecoo-mozna-je-kupic-tylko-w-aso,nId,21396613) (no date on page) | press, journalist's own search | front brake pads, Jaecoo 7 | "kupić można wyłącznie w ASO", 1280 zł per front set; no wholesaler offers aftermarket pads yet because demand is low |
| S6 | AC `części do saaba` | AC | Saab 9-3, 9-5 parts | suggestions "czy części do saaba są dostępne", "dostępność części do saaba", "części do saaba czy drogie" |
| S7 | [Forsal, 2013](https://forsal.pl/artykuly/722554,brak-nowych-czesci-do-samochodow-saab.html) (old) | press | new Saab parts after the maker's bankruptcy | seller ordered from a warehouse in Hungary with no delivery date; service admitted parts were "not in stock" because factories stopped making them (search summary; not re-read) |
| S8 | AC `części do tesli` | AC | Tesla Model 3/Y/S parts | suggestions "jak zamowic czesci do tesli", "gdzie kupic czesci do tesli", "czy czesci do tesli sa drogie": the ordering route itself is unclear to buyers |
| S9 | AC `części do aut z usa` | AC | parts for cars imported from the US | 9 of 10 suggestions add a city (Białystok, Warszawa, Rzeszów, Poznań, Łódź, Olkusz, Bydgoszcz, Lublin, Kraków): people look for a local specialist, not a general shop |
| S10 | AC `części do kampera` | AC | camper parts by habitation-body brand | suggestions by brand: Knaus, Rimor, Dethleffs, Hymer, Bürstner, LMC, Fiat Ducato, plus "olx" and "używane" |
| S11 | AC `części do przyczepy kempingowej` | AC | caravan parts | brands Dethleffs, Hobby, Adria, Fendt, Knaus, Niewiadów (N126, N126n) and "przyczepy kempingowej angielskiej" (UK-built caravans) |
| S12 | AC `lusterko do kampera` | AC | wide camper mirrors | "lusterko wsteczne do kampera", "lusterko boczne do kampera" |
| S13 | AC `opony do przyczepy` | AC | trailer and caravan tyres in odd sizes | "opony do przyczepy d47", "8.25-20 używane", "kempingowej 185r14c", "kempingowej 13", "d35" |
| S14 | [Autoblog Spider's Web, 23 Jul 2019](https://autoblog.spidersweb.pl/czesci-samochodowe-sklep-gorsze-zaopatrzenie) (old) | press, author's own shopping | 13-inch tyres, car audio, parts for Cinquecento, Maluch, Polonez | 13-inch tyres only "na zamówienie", used ones nearly impossible; classic parts (carburettors, fuel pumps, gaskets) scarce and overpriced |
| S15 | AC `części do fiata 126p` | AC | Fiat 126p parts | suggestions with "allegro", "olx", "sklep", "nowe" and six cities (Bielsko-Biała, Wrocław, Warszawa, Kraków …) |
| S16 | AC `części do starych motocykli` | AC | old motorcycle parts | "gdzie kupic czesci do starych motocykli", "…bmw", "…olx", city variants (Lublin, Warszawa) |
| S17 | AC `części do quada` | AC | quad parts for Chinese brands | Linhai 500, CF Moto 500, Loncin, Bashan 200, "125", "110 olx" |
| S18 | AC `części do skutera chińskiego` | AC | Chinese scooter parts | "części do skutera chińskiego 4t": no brand known, so buyers search by origin |
| S19 | AC `gdzie kupić oryginalne części` | AC | original (OE) parts | 10 suggestions by brand: Volkswagen, Toyota, Audi, Skoda, BMW, Honda, Kia, Mercedes, Mazda (plus Stihl) |
| S20 | AC `gdzie kupić części do` | AC | general | includes "gdzie kupić części do chińskich samochodów" and "do quada tgb" among the top ten, next to washing machines and Parkside tools |
| S21 | AC `części do busa` | AC | van parts | "części do busa radom/lublin", "czesci uzywane do busa", "czesci do zabudowy busa" (camper conversion parts) |

## Candidate hard-to-find items (feeds T10)
Frequency proxy: **AC** = Polish autocomplete suggests the phrase (number of distinct suggestions in brackets); **press** = reported in press; no item has a verified monthly search volume.

| # | Item | Signals | Frequency proxy (source) | Friction |
|---|---|---|---|---|
| V1-D01 | body and collision parts for Chinese brands (Omoda, Jaecoo, BAIC, MG) | S1–S4 | AC (8 suggestions on availability) + Facebook group >30,000 members (S3) | finding, logistics |
| V1-D02 | aftermarket service parts (pads, filters) for new Chinese brands | S5, S1 | press (S5); AC "czy części … są drogie" | price, finding |
| V1-D03 | Tesla parts for private owners and independent workshops | S8 | AC (8 suggestions) | finding (route unclear) |
| V1-D04 | parts for US-import cars, near the buyer | S9 | AC (10 suggestions, 9 with a city) | finding, logistics |
| V1-D05 | Saab parts (discontinued brand) | S6, S7 | AC (8 suggestions) | finding |
| V1-D06 | classic Polish car parts (126p, Polonez, Cinquecento), new old stock | S14, S15 | AC (10 suggestions for 126p) + press 2019 | finding, trust |
| V1-D07 | camper habitation parts by body brand (Knaus, Hymer, Rimor, LMC …) | S10, S21 | AC (10 suggestions) | finding, fit |
| V1-D08 | caravan parts for Niewiadów N126 and UK-built caravans | S11 | AC (10 suggestions) | finding, fit |
| V1-D09 | trailer and caravan tyres in odd sizes (13", 185R14C, D47) | S13, S14 | AC (10 suggestions) | finding |
| V1-D10 | camper mirrors and windows | S12 | AC (3 suggestions) | fit |
| V1-D11 | old motorcycle parts | S16 | AC (6 suggestions) | finding |
| V1-D12 | Chinese quad and scooter parts (Linhai, Loncin, Bashan, TGB) | S17, S18, S20 | AC (10 + 2 suggestions) | finding, fit |
| V1-D13 | original OE parts for mainstream brands outside the dealer | S19 | AC (10 suggestions) | trust, price |
| V1-D14 | van conversion (zabudowa busa) parts | S21 | AC (1 suggestion) | finding, fit |

## Notes for T10 and T11
- The strongest, freshest signal is **Chinese-brand parts** (S1–S5): owners wait months, aftermarket supply does not exist yet, importers promise days. A demand that is real today but may close as importers build warehouses (S3 mentions a Pomeranian warehouse; inference that it will close: unverified).
- Camper and caravan parts show the "brand list" pattern: buyers know the body brand but not where its parts are sold. T10 should test 3–5 of these by name.
- No forum thread with a "sprowadź z Niemiec" answer was found for car parts in this run; that phrase returned only whole-car import pages.
