# TH63 — Finance and M&A research agents (Poland check)

Theme: [THEMES.md#th63](../../themes/THEMES.md#th63) · rank 57, batch C · sources accessed **2026-11-05** · method: [README](README.md#method). Two sub-segments: research tools for bankers and PE (Rogo, Model ML, Comparables.ai) and AI-native sell-side for small businesses (OffDeal).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| SprzedamBiznes.pl | Marketplace for buying and selling companies, commercial property and stakes, since 2011; no AI described | listing fees (not checked) | sellers, brokers | [Village.ai profile](https://village.ai/company/sprzedambiznes) |
| BizShop (Warsaw, 2026) | Structured listing pages for small offline businesses (salons, pizzerias): revenue, profit, payback, risks; plans to verify figures via KSeF, wFirma, inFakt; no AI mentioned | first listings free (early access) | not stated | [Product Hunt: BizShop](https://www.producthunt.com/products/bizshop) |
| OLX "firmy na sprzedaż" | Classified listings of businesses for sale (autocomplete "firmy na sprzedaż olx") | listing fees | small sellers | §3 |
| Brokers and boutiques | Human sell-side advisers (e.g. Marktlink has a Warsaw office) | success fees | mid-market owners | [Marktlink Warsaw](https://www.marktlink.com/uk/about-us/offices/warsaw) |

No Polish AI sell-side boutique or AI research agent for Polish bankers was found.

## 2. Does the Western leader already serve Poland?
- **Comparables.ai** (FI): self-serve free tier without a credit card, claims 370M+ companies in 110+ countries including private firms with financials "where released"; Poland is not named, so coverage of Polish KRS filings is **unverified**; full multiples are Premium ([comparables.ai](https://www.comparables.ai/)). Not signed up.
- **Rogo, Model ML** sell to large banks; Polish bulge-bracket offices (if any) would get them from headquarters. Not a solo-founder market.
- **OffDeal** (US) runs AI-assisted sell-side for US small businesses; not in Europe.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "sprzedaż firmy" → 10 incl. "jednoosobowej", "z pracownikami", "a podatek dochodowy", "jednoosobowej a vat"; "wycena firmy" → 10 incl. "kalkulator", "do sprzedaży", "online"; "firmy na sprzedaż" → 10 (cities, regions, OLX); "sukcesja w firmie" → 5 incl. "jednoosobowej", "rodzinnej"; "sprawozdanie finansowe krs pobierz" → echo.
- Succession: up to 80,000 succession processes in Polish firms by 2030 (Mastercard report), 8.1% of students from family firms planned to continue the business (2017 GUESSS), 85% of successors have other plans (Pekao); typical first owner aged 60–70 (PwC) ([XYZ.pl, 2025-11-12](https://xyz.pl/przejecie-rodzinnego-biznesu-nie-dziekuje-ida-ciezkie-czasy-dla-sukcesji-w-polsce/)). Some of these numbers come from older surveys.

## 4. What adaptation needs
M09 KRS and eKRS financial statements (XML) for comparables of Polish sp. z o.o.; JDG cannot be "sold" as an entity: sale goes through *przedsiębiorstwo* transfer (art. 55¹ KC), conversion to a company, or *zarząd sukcesyjny* (2018 act); tax (PIT/VAT on sale of an enterprise, autocomplete shows these questions); M10 CEIDG; M01/M46 KSeF and invoicing data to verify revenue (BizShop's plan). Owners buy through trust and accountants (M51), not online.

## 5. Demographic or social driver
DD1-adjacent: ageing 1990s founders without successors (see §3); DD7 labour scarcity raises the value of firms with staff.

## 6. CEE check
No CZ/SK/RO/HU AI sell-side or comparables product in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **partial**
Banker research agents are an enterprise market (out of scope), but the small-business sale side is served only by classifieds (SprzedamBiznes, OLX) and a new non-AI BizShop, while succession volume is rising. The OffDeal model itself (an AI-run brokerage taking success fees) needs a regulated-feeling trust relationship and deal work the founder cannot staff.

**Seed idea:** "Teczka sprzedażowa": owner of a JDG or small sp. z o.o. connects KSeF/inFakt/wFirma and uploads statements; the agent builds a normalised P&L, a valuation range from KRS comparables, a teaser and an information memorandum, and explains the legal route (JDG → sp. z o.o., sale of *przedsiębiorstwo*, tax); 499–1,499 PLN per package, sold via accounting offices and listing sites.
