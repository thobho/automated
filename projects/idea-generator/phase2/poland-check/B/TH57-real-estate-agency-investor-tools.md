# TH57 — Real-estate agency and investor tools (Poland check)

Theme: [THEMES.md#th57](../../themes/THEMES.md#th57) · rank 43, batch B · sources accessed **2026-11-05** · method: [README](README.md#method).

Overlap: plot reports and title diligence are in [TH15](TH15-property-transaction-title-diligence.md); this file covers agents' CRM chasing, listings and valuations, and investors' plot potential.

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| ASARI CRM | Agency CRM: deals pipeline, property and client base, under-a-minute export to portals, WordPress site, field-agent GPS app, MLS ASGAL access; **no AI features described** | not public; 14-day trial | Polish agencies (count not stated) | [adresowo.pl on ASARI](https://adresowo.pl/wspolpraca/crm/asari-opis/) |
| EstiCRM and other agency CRMs | Agency CRM with fixed pricing; AI features not described | not found | Polish agencies | [radiozw.com.pl](https://radiozw.com.pl/funkcje-i-mozliwosci-oprogramowania-esti-crm) |
| Otodom (OLX Group) | AI in the listing form that suggests titles and descriptions from several data sources, also for listings imported from CRMs; positioned as a "first step" | included | all advertisers on Otodom | [otodom.pl](https://www.otodom.pl/wiadomosci/sprzedaje/ai-otodom-jak-ulatwia-dodawanie-ogloszen) |
| Online valuations (Otodom, adresowo and others) | Free consumer price estimates, often as a lead form for agents | free | sellers | autocomplete below |
| OnGeo, Cenatorium | Spatial plot reports with MPZP and prices (OnGeo); property price information since 2012 (Cenatorium) | per report / not found | agents, valuers, banks | [TH15](TH15-property-transaction-title-diligence.md); [revenuebase proptech PL](https://revenuebase.ai/companies/proptech-startups/poland) |
| Rejestr Cen Nieruchomości (state) | Real transaction prices from notarial deeds; **free for everyone since 2026-02-13**, map and WFS download per country, voivodeship or powiat | free | everyone | [OnGeo blog](https://blog.ongeo.pl/news-rejestr-cen-nieruchomosci-za-darmo-od-13-lutego-2026); [geoportal.gov.pl news](https://www.geoportal.gov.pl/aktualnosci/rcn-dla-362-powiatow-dostepny-w-serwisie-www-geoportal-gov-pl/) |

No Polish AI assistant for agents (follow-up chasing, buyer matching, CMA generation) was found; a Polish-language overview of AI tools for agents lists only US products and says other markets' tools are immature ([techsy.io/pl](https://techsy.io/pl/blog/ai-narzedzia-nieruchomosci-2026)).

## 2. Does the Western leader already serve Poland?
- **Tapusor** (TR): Turkish App Store top-grossing Business #19 per the theme record; Turkish-market app; **not in PL** ([App Store TR](https://apps.apple.com/tr/app/tapusor/id1260192075)).
- **Propcorn** (AT): plot building-potential analysis using Austrian zoning (Flächenwidmungsplan); site only in German, Poland not mentioned; **not in PL** ([propcorn.ai](https://www.propcorn.ai/)).
- **HouseWhisper** (US), **Agentsy** (AU), **Prop-AI** and **Coraly.ai** (AE): built around local portals and MLS data; no Polish presence found (sites not opened individually for this check).
- **onOffice** (DE) sells an AI writer for listing texts and has a Croatian site; Polish presence not checked ([hr.onoffice.com](https://hr.onoffice.com/en/real-estate-software/marketplace/ai-writer/)).
- Not tried: signing up to any agent CRM.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "wycena mieszkania online" → 10 ("za darmo", "bez logowania", "kalkulator", "otodom", "adresowo", "bez podawania maila"); "rcn ceny transakcyjne" → only itself; "crm dla agenta nieruchomości", "ai opis nieruchomości", "chatgpt agent nieruchomości", "analiza działki pod inwestycję" → empty. Consumer demand for free valuations is strong (and wary of lead capture); agent-side search for AI tools is very low.
- Industry: Drees & Sommer survey cited by Eurobuild: almost 30% of real-estate staff in PL/CZ/HU use AI, 38% of them daily ([eurobuildcee.com](https://eurobuildcee.com/news/60086-sztuczna-inteligencja-na-co-dzien)).

## 4. What adaptation needs
- Free RCN data (new in 2026) plus Geoportal parcels and MPZP (M28), EKW (M27), Otodom/OLX listings (M40), CEPiK-style public data as precedent; Portal DOM (housing statistics) planned for 2027-04-02 ([pewnylokal.pl](https://pewnylokal.pl/portal-dom-czy-rejestr-cen-nieruchomosci-co-sie-zmieni)).
- Polish agency practice: umowy pośrednictwa (open vs exclusive), MLS ASGAL, phone-first clients, offer export via CRM to portals.
- Portal terms of service for automated reading of listings must be checked (Otodom, OLX).

## 5. Demographic or social driver
DD10: housing revives (208 thousand completions in 2025, D48) and prices fall relative to wages (D50), raising transaction volume; DD9 suburbanisation drives plot purchases around metros.

## 6. CEE check
No CZ/SK/RO/HU real-estate agent AI in the [R6 catalogue](../../catalogue/R6-cee-peers.csv). onOffice (DE) with a Croatian site is the most likely European software entrant; Otodom (OLX Group) is the platform owner and can absorb description and valuation features.

## 7. Verdict: **partial**
Listing descriptions are absorbed by Otodom and generic ChatGPT, and consumer valuations are free; Polish agency CRMs show no AI layer, and no product turns the newly free RCN transaction data into agent-ready price analyses. The gap is real but the buyers (small agencies) search little for such tools, and Otodom could add the same feature.

**Seed idea:** RCN-based comparative market analysis (CMA) for agents: enter an address, get a branded PDF with nearby notarial transaction prices, current competing Otodom/OLX offers, price per m² trend and a plain-Polish pitch for the seller meeting, generated in minutes; 99–199 PLN/agent/month, sold via ASARI/EstiCRM integrations or agent Facebook groups.
