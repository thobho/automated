# TH67 — Agents inside SMB retail and hospitality systems (Poland check)

Theme: [THEMES.md#th67](../../themes/THEMES.md#th67) · rank 44, batch B · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| POSbistro (Kraków) | Tablet POS for food service plus POSowner, POSdriver, POScaller, DirectBistro; **AI chat in the admin panel** (v4.0.4, 2026-02) for finding functions, configuration and reports; AI image generation for menu items (2025-10); KSeF integration in preparation | not public (Standard, Delivery, Enterprise) | not stated | [posbistro.com 2026-02](https://posbistro.com/en/2026/02/19/Posbistro-system-updates-February-2026/); [posbistro.com 2025-10](https://posbistro.com/en/2025/10/21/New-in-Posbistro%3A-AI-image-generation-for-menu-items/) |
| UpMenu, GoPOS, S4H, Wealthon POS, Foodsoft, RePOS, IzzyRest and others | Polish gastro POS and ordering; a 2026-02 ranking mentions **no AI features** for any of 11 systems | UpMenu 169–499 PLN/month per venue; GoPOS 79–129; S4H 69–199; Wealthon 149 net | not stated | [upmenu.com ranking](https://www.upmenu.com/pl/blog/systemy-pos) |
| Dotykačka (CZ) | Czech POS for gastronomy, retail, services, sold in Poland | 62.30–139.30 PLN net/month | not stated | [upmenu.com ranking](https://www.upmenu.com/pl/blog/systemy-pos) |
| eFitness | Gym management SaaS (CRM, finance and sales analytics, access control), member app integrated with Benefit Systems (MultiSport) and Medicover Sport; 600+ clubs in Poland and Europe (2021) | not public | 600+ clubs | [comparic.pl 2021](https://comparic.pl/efitness-dopiero-sie-rozgrzewa-i-zapowiada-wprowadzenie-akcji-do-obrotu-na-rynku-newconnect/); [eFitnessApp](https://apps.apple.com/pl/app/efitnessapp/id1054978020?l=pl) |
| AInora (LT) | White-label voice AI for fitness clubs, Polish site | not checked | not checked | [ainora.lt/pl](https://ainora.lt/pl/white-label-kluby-fitness) |

## 2. Does the Western leader already serve Poland?
- **TabSense** (SA): AI-native restaurant POS with 1,000+ clients in Saudi Arabia and Jordan, built on ZATCA e-invoicing; **not in PL** ([wamda.com](https://www.wamda.com/en/2025/10/tabsense-attracts-5-million-backing-jasoor-ventures)).
- **Emilia AI** (CO), **Órale AI** (MX): Spanish-language, Latin American; not in PL.
- **Sigvi** (LT): agent-run car-rental operations (pricing, bookings, keyless access, inspections); **launched in Poland 2026-06** per its funding news ([tech.eu](https://tech.eu/2026/07/29/sigvi-raises-eur12m-to-expand-automated-car-rental-operations/)).
- **1club AI** (BG): AI platform for gyms, seed USD 2.5M (aggregator source, product details unverified); Polish presence not found.
- Not tried: no POS or gym software trial accounts created.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "system pos dla gastronomii" → 5 ("cena", "co to", "ranking"); "program dla restauracji" → 3 ("lojalnościowy", "magazynowy"); "ai w gastronomii" → 2 ("wykorzystanie ai w gastronomii"); "food cost kalkulator" → 7 ("online", "excel darmowy", "unilever"); "system dla klubu fitness" → empty; "program dla siłowni" → only workout plans. Owners search for software by price and for food-cost tools, not for AI agents; the gym-software query is too small to register.

## 4. What adaptation needs
Kasy fiskalne online and receipts, KSeF invoices for B2B buyers (M01, M50), BLIK and Polish payment terminals (M32), delivery aggregators (Pyszne.pl, Glovo, Wolt, Uber Eats), Sanepid/HACCP records, MultiSport/Medicover Sport visit settlement for gyms. An agent must run **inside** the POS, so the realistic route is an add-on through POS vendors' APIs, not a new POS.

## 5. Demographic or social driver
DD7: labour is scarce and costly (66% of firms cite labour costs, D39), which is acute in gastronomy; DD12 rising incomes keep eating-out demand growing.

## 6. CEE check
Dotykačka (CZ) already sells POS in Poland; Sigvi (LT) entered Poland in 2026; 1club AI (BG) is in the [R6 catalogue](../../catalogue/R6-cee-peers.csv) and could add Polish. CEE entry risk is concrete.

## 7. Verdict: **partial**
Polish POS vendors have barely started with AI (POSbistro's admin chat and menu images; none of 11 ranked systems lists AI), so the "agent that runs menus, stock and pricing" is not served. But the agent only works inside the POS, the POS vendors own the data and the customer, and owners do not search for it; an outside founder must partner with or sell through those vendors.

**Seed idea:** food-cost and menu-margin agent for independent restaurants as a POS add-on: reads sales from GoPOS/UpMenu/POSbistro exports and supplier invoices from KSeF, flags dishes whose margin fell after price changes, proposes price and portion changes, and writes the weekly order list; 149–249 PLN/month per venue, sold via POS vendor marketplaces and gastro Facebook groups.
