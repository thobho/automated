# V3 — Hobby niches with thin coverage: Polish demand signals

T09 of Phase 3 ([task](../tasks/09-demand-mining.md), [brief](../BRIEF.md)). Scan: [research/verticals/V3-hobby-niches.md](../research/verticals/V3-hobby-niches.md). All sources accessed **2026-11-06**.

## Method and limits
Same as [V1](V1-vehicle-parts.md#method-and-limits): Google autocomplete (AC), Polish interface, about 35 queries for V3 (example: [`klocki lego na sztuki`](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=klocki%20lego%20na%20sztuki)); AC shows a phrase is searched, not how often. Web search for Polish forum threads in hobbies returned mostly shops and English forums (gunpla, aquarium, keyboards), so V3 rests more on AC than V1/V2. **Facebook group sizes were not collected:** group pages need a login to show counts and search snippets did not show them; the V3 scan's unverified hobby sizes stay unverified. Monthly volume is **unverified** for every item.

## Signals
| # | Query or link | Type | What the person needed | What they were told / found |
|---|---|---|---|---|
| S1 | AC `klocki lego na sztuki` | AC | single LEGO bricks | "…gdzie kupić", "…bricklink", "…sklep", "…olx" and five cities (Warszawa, Kraków, Poznań, Katowice): buyers look for a local or Polish-language BrickLink |
| S2 | AC `gunpla gdzie kupić` | AC | Gundam plastic kits | the only suggestion is "gdzie kupić gunpla w polsce" |
| S3 | web search "gdzie kupić gunpla w Polsce …" (2026-11-06) | search | Polish gunpla shop | results were Japanese proxy services (e.g. [Japan Rabbit](https://japanrabbit.com/buy-japan/gunpla)), eBay and desertcart; no Polish shop or forum in the top results |
| S4 | AC `keycapy` | AC | keyboard keycaps | "keycapy pbt", "…do klawiatury 60", "…do klawiatury mechanicznej", "keycaps pudding", "keycapy allegro" |
| S5 | [kbd.news: keyboard vendors in Poland](https://kbd.news/keyboard-vendors/Poland) | directory | Polish enthusiast keyboard shops | lists 5 vendors for Poland (FalbaTech, KEEBMAT, Keyspace Store, Shelter, Typebuilders): thin local supply |
| S6 | [Pepper.pl: "moja pierwsza klawiatura mechaniczna"](https://www.pepper.pl/dyskusji/moja-pierwsza-klawiatura-mechaniczna-1256336) | forum (summary) | first mechanical keyboard and switches | advice centres on AliExpress models and waiting for promotions (search summary, not read in full) |
| S7 | AC `filament gdzie kupić` | AC | 3D-printing filament | "gdzie kupić filament stacjonarnie", "filament pla gdzie kupić", "…do drukarki 3d" |
| S8 | AC `części do drukarki 3d` | AC | 3D-printer parts | "czesci do budowy drukarki 3d" |
| S9 | AC `części do drona` | AC | drone parts | "fpv", DJI Mini 2, 3, 4 Pro, 4K, 5 Pro, E88 (cheap Chinese drone) |
| S10 | AC `sprzęt pszczelarski` | AC | beekeeping equipment | "…używany", "…z ukrainy", "…na refundację", "…na dotacje", "…temu", "łysoń", "konigin": buyers look for cheaper sources and subsidy-eligible kit |
| S11 | AC `matki pszczele` | AC | queen bees | "unasiennione od ręki", "buckfast", "olx dolnośląskie", "2026", "allegro": availability "od ręki" is a search term |
| S12 | AC `sklep krótkofalarski` | AC | ham-radio shop | 9 of 10 suggestions add a city (Wrocław, Warszawa, Łódź, Poznań, Radom, Szczecin, Lublin, Rzeszów, Bydgoszcz) |
| S13 | AC `części do gramofonu` + `igła do gramofonu` | AC | turntable parts and styli | Polish Unitra models (Daniel, Bernard, Adam, Fonica, Artur) next to Technics, Dual, Audio-Technica, Lenco |
| S14 | AC `lampy do wzmacniacza` | AC | valves (tubes) for amplifiers | "jakie lampy do wzmacniacza lampowego", "najlepsze lampy…", Marshall, guitar amps: a "which one" question |
| S15 | AC `części do silnika zaburtowego` | AC | outboard-motor parts | Yamaha, Suzuki, Mercury, Honda, Johnson, Mariner, Evinrude (discontinued), Storm |
| S16 | AC `części do kołowrotka` | AC | fishing-reel spare parts | Okuma, Mikado, Shimano, Prologic, DAM Quick, Jaxon, Daiwa, Mistrall, Dragon |
| S17 | AC `przynęty japońskie` | AC | Japanese lures | "japońskie przynęty spinningowe", "…gumowe" |
| S18 | AC `części do maszyny do szycia` | AC | sewing-machine parts | Łucznik (884, 466), Singer 834, Husqvarna, Privileg, Toyota, Minerva |
| S19 | AC `części do roweru elektrycznego` | AC | e-bike parts | Dutch brands Gazelle, Sparta, Batavus next to Indiana, Ecobike, Cube, Giant: imported second-hand Dutch e-bikes need parts |
| S20 | AC `części do hulajnogi elektrycznej` | AC | e-scooter parts | Xiaomi, Kamikaze K1 Max, Motus 10 Pro, plus cities (Poznań, Szczecin, Kielce) |
| S21 | [Bezprawnik, 27 Apr 2026](https://bezprawnik.pl/pistia-rozetkowa-nielegalna-w-akwarium/) | press (reader's letter) | water lettuce (pistia) for an aquarium | the pet shop said it "recently became illegal in Poland"; the ban on keeping and trade applies from 2 Aug 2024 (invasive-species list). A legal block, **not** an opportunity |
| S22 | AC `krewetki akwariowe gdzie kupić` | AC | aquarium shrimp | the phrase itself is suggested (1 suggestion) |
| S23 | AC `zestawy do haftu` + `włóczka gdzie kupić` | AC | embroidery kits and yarn | brands Ariadna, Lanarte, Dimensions; "włóczka drops gdzie kupić", "chenille", "bawełniana" |
| S24 | AC `części do zegarka` | AC | watch parts | Orient, Casio, Garmin, Omega, Delbana, Atlantic, Diesel |

## Candidate hard-to-find items (feeds T10)
Frequency proxy as in V1 (AC = number of autocomplete suggestions); no verified volumes.

| # | Item | Signals | Frequency proxy (source) | Friction |
|---|---|---|---|---|
| V3-D01 | single LEGO bricks from Polish sellers | S1 | AC (10) | finding, logistics |
| V3-D02 | gunpla and Japanese model kits in Poland | S2, S3 | AC (1); no Polish shop in top web results | finding, logistics (import) |
| V3-D03 | enthusiast keycaps and switches with EU delivery | S4–S6 | AC (10) + 5 local vendors (S5) | finding, trust |
| V3-D04 | 3D filament bought locally, same day | S7 | AC (5) | logistics |
| V3-D05 | parts to build or repair 3D printers | S8 | AC (2) | finding |
| V3-D06 | DJI and FPV drone spare parts | S9 | AC (10) | fit |
| V3-D07 | used or subsidy-eligible beekeeping equipment | S10 | AC (10) | price |
| V3-D08 | queen bees available now (od ręki) | S11 | AC (10) | logistics, timing |
| V3-D09 | ham-radio equipment near the buyer | S12 | AC (10, 9 with a city) | finding |
| V3-D10 | Unitra turntable parts and styli | S13 | AC (10 + 10) | fit |
| V3-D11 | amplifier valves (which one fits) | S14 | AC (10) | fit |
| V3-D12 | outboard-motor parts incl. discontinued brands (Evinrude, Johnson) | S15 | AC (10) | finding |
| V3-D13 | fishing-reel spare parts by model | S16 | AC (10) | fit |
| V3-D14 | Japanese lures | S17 | AC (3) | finding, import |
| V3-D15 | sewing-machine parts (Łucznik, Singer) | S18 | AC (10) | fit |
| V3-D16 | parts for imported Dutch e-bikes (Gazelle, Sparta, Batavus) | S19 | AC (10) | finding, fit |
| V3-D17 | e-scooter parts (Xiaomi, Kamikaze, Motus) | S20 | AC (10) | fit |
| V3-D18 | aquarium shrimp and plants (legal species) | S21, S22 | AC (1); legal limits (S21) | finding, regulation |
| V3-D19 | embroidery kits and imported yarn brands (Drops, Lanarte) | S23 | AC (10 + 5) | finding |
| V3-D20 | watch spare parts | S24 | AC (10); see V4 watch repair | fit |

## Notes for T10 and T11
- The repeated "city" suffix (ham radio S12, LEGO S1, scooters S20) suggests buyers want a local shop or pickup; T10 should test whether an online Polish source exists at all.
- Import-dependent hobbies (gunpla S2–S3, keyboards S4–S6, Japanese lures S17) fit the V3 scan's "consolidated buying in Polish" gap; customs and VAT were not checked here.
- Regulated items (invasive aquarium species S21; drones above certain classes) need a legal check before any idea.
