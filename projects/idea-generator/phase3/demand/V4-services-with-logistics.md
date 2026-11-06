# V4 — Services with a logistics step: Polish demand signals

T09 of Phase 3 ([task](../tasks/09-demand-mining.md), [brief](../BRIEF.md)). Scan: [research/verticals/V4-services-with-logistics.md](../research/verticals/V4-services-with-logistics.md). All sources accessed **2026-11-06**.

## Method and limits
Same as [V1](V1-vehicle-parts.md#method-and-limits): Google autocomplete (AC), Polish interface, about 32 queries for V4 (example: [`naprawa wysyłkowa`](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=naprawa%20wysy%C5%82kowa)). For services, AC also shows **what people do not type**: an empty AC result for a phrase is recorded as a negative signal (the phrase is rare). City suffixes are biased to Lower Silesia by the requester's location. Monthly volume is **unverified** for every item.

## Signals
| # | Query or link | Type | What the person needed | What they were told / found |
|---|---|---|---|---|
| S1 | AC `naprawa wysyłkowa` | AC | repair by post | "naprawa wysyłkowa huawei", "wysyłkowa naprawa laptopów", "…zegarków", "…telefonów", "…obuwia" |
| S2 | AC `ostrzenie noży wysyłkowo`, `naprawa butów wysyłkowo`, `naprawa ekspresu wysyłkowo`, `naprawa telefonu kurierem`, `serwis laptopa wysyłkowo` | AC (negative) | mail-in phrasing | **no suggestions** for any of the five: buyers do not phrase these needs as "by post" (low volume or different wording) |
| S3 | AC `ostrzenie noży` | AC | knife sharpening | "ostrzenie nożyczek fryzjerskich", "…noży do maszynki do mięsa", "…nożyc do żywopłotu", "…noży do kosiarki", city variants: local, not mail-in |
| S4 | AC `naprawa zegarka` | AC | watch repair | smartwatches dominate: Garmin, Huawei Watch GT 2, Apple Watch, Amazfit, Garett Kids; mechanical: "automatycznego", Omega, Tissot |
| S5 | AC `naprawa kurtki puchowej` | AC | down-jacket repair | "po praniu", "rozdartej", "north face" and five cities (Kraków, Wrocław, Łódź, Katowice, Gdańsk, Poznań) |
| S6 | web search "gdzie oddać do naprawy kurtkę puchową …" (2026-11-06) | search | down-jacket repair workshop | top results were DIY guides (e.g. [Decathlon](https://www.decathlon.pl/c/learn/jak-zaszyc-dziure-w-kurtce-sposoby-by-naprawic-ja-w-domu_435134d5-b5b7-4ac0-8acc-529c0d19bfda)) and a price portal; no named workshop or forum answer |
| S7 | AC `wymiana zamka w kurtce` | AC | zip replacement | "cena", "zimowej", "motocyklowej", "puchowej", "skórzanej", Kraków, Lublin |
| S8 | AC `naprawa robota sprzątającego` | AC | robot-vacuum repair | Xiaomi, Tefal, Roborock, "ile kosztuje naprawa robota sprzątającego" |
| S9 | [Pepper.pl: serwis gwarancyjny Roborock Polska, 11 Feb 2026](https://www.pepper.pl/dyskusji/serwis-gwarancyjny-roborock-polska-1223149) | forum (summary) | warranty service for Roborock | the opening post asks whether anyone has experience with Roborock warranty service in Poland (replies not read) |
| S10 | AC `naprawa odkurzacza dyson` | AC | Dyson repair | V15 and nine cities: local repair shops sought, brand-specific |
| S11 | AC `naprawa termomix` | AC | Thermomix repair | "po gwarancji", TM5, TM6, TM31 and cities (Wrocław, Lubin, Warszawa, Szczecin, Poznań) |
| S12 | AC `naprawa gramofonu` | AC | turntable repair | Unitra models Daniel and Bernard; seven cities |
| S13 | AC `naprawa wzmacniacza` | AC | amplifier repair | car audio: Bose (Audi), Harman Kardon, Logic 7, BMW, Audi A6 C6 |
| S14 | AC `naprawa obiektywu` | AC | camera-lens repair | Canon, Nikon, Sigma, Tamron, Sony, Olympus, "cena" |
| S15 | AC `naprawa pada` + `naprawa konsoli` | AC | game-controller and console repair | PS5 (incl. "cena"), Xbox Series X, PS4; DJ consoles |
| S16 | AC `naprawa roweru elektrycznego` | AC | e-bike repair | "naprawa baterii roweru elektrycznego", "…sterownika", "…silnika", "…ładowarki", Sparta |
| S17 | AC `naprawa hulajnogi elektrycznej` | AC | e-scooter repair | nine small Lower Silesian and other towns (Lubin, Wałbrzych, Legnica, Gorzów Wlkp., Siedlce) |
| S18 | AC `naprawa instrumentów` | AC | instrument repair | wind instruments dominate ("dętych", "dętych blaszanych", "cennik"), keyboards, Korg |
| S19 | AC `naprawa walizki` | AC | suitcase repair | Wittchen, Ochnik, polycarbonate/ABS shells |
| S20 | AC `renowacja wózka` | AC | pram refurbishment | "renowacja wózka dziecięcego", "cybex", "stelaża" |
| S21 | AC `czyszczenie dywanów z odbiorem` | AC | carpet cleaning with pick-up | "z odbiorem z domu", Kraków, Warszawa: pick-up is already part of the search phrase |
| S22 | AC `naprawa parasola` | AC | umbrella repair | mostly garden umbrellas ("mechanizmu", "poszycia", "grzewczego"), "ile kosztuje" |
| S23 | AC `montaż mebli` | AC | furniture assembly | "w paczkach cena", "ikea", "agata meble", "kuchennych cennik" |
| S24 | AC `montaż klimatyzacji cena` | AC | AC installation price | "cena robocizny", "forum", "olx", "2025", cities: price discovery is the question |

## Candidate hard-to-find items (feeds T10)
Frequency proxy as in V1 (AC = number of autocomplete suggestions); no verified volumes.

| # | Item | Signals | Frequency proxy (source) | Friction |
|---|---|---|---|---|
| V4-D01 | smartwatch repair (Garmin, Huawei, Amazfit, Apple Watch) | S1, S4 | AC (10) | finding, logistics |
| V4-D02 | mechanical watch service by post | S1, S4 | AC ("wysyłkowa naprawa zegarków") | trust, logistics |
| V4-D03 | down-jacket repair and refill | S5, S6 | AC (10); no workshop in top web results | finding |
| V4-D04 | zip replacement in jackets (winter, leather, motorcycle) | S7 | AC (9) | finding, price |
| V4-D05 | robot-vacuum repair outside warranty | S8, S9 | AC (5) + 1 forum post | trust, logistics |
| V4-D06 | Dyson repair | S10 | AC (10) | finding |
| V4-D07 | Thermomix repair after warranty | S11 | AC (10) | finding, logistics |
| V4-D08 | turntable and vintage audio repair | S12 | AC (10) | finding |
| V4-D09 | car premium-audio amplifier repair (Bose, Harman, Logic 7) | S13 | AC (10) | finding, logistics (module by post) |
| V4-D10 | camera-lens repair | S14 | AC (10) | trust, price |
| V4-D11 | game-controller drift repair (PS5, Xbox) | S15 | AC (10) | price, logistics |
| V4-D12 | e-bike battery and controller repair | S16 | AC (8) | finding, logistics (battery shipping rules) |
| V4-D13 | e-scooter repair in small towns | S17 | AC (10) | finding |
| V4-D14 | wind-instrument repair | S18 | AC (10) | finding |
| V4-D15 | suitcase shell and wheel repair | S19 | AC (10) | finding |
| V4-D16 | pram refurbishment | S20 | AC (4) | finding |
| V4-D17 | knife and scissor sharpening (incl. hairdressing scissors) | S2, S3 | AC (10); no "wysyłkowo" suggestion | logistics |
| V4-D18 | AC installation price comparison | S24 | AC (10) | price |

## Notes for T10 and T11
- People search for repair **with a city**, not "by post" (S2 is empty for five mail-in phrasings). A mail-in repair service would have to capture "naprawa X [miasto]" searches with a "send it" offer, or work through brands and shops (V4 scan: B2B2C).
- Brand-specific electronics repair (Garmin, Dyson, Thermomix, Roborock, Bose car amplifiers) is the densest cluster.
- Not checked: Polish repair subsidies (V4 scan item); OLX/Fixly request volumes (blocked).
