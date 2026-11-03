# TH04 — Care-provider documentation and operations (Poland check)

Theme: [THEMES.md#th04](../../themes/THEMES.md#th04) · rank 18, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Generic ERP for home-care agencies (Odoo partner blog in Polish) | Visit tracking on mobile, carer rosters, client records, billing from visit data; not care-specific AI | not stated | private agencies (target) | [dasolo.ai blog](https://www.dasolo.ai/pl/blog/odoo-wed%C5%82ug-branzy-8/odoo-opiekunowie-harmonogramy-rozliczenia-698) |
| Paper and spreadsheet practice in MOPS and DPS | NIK audits describe a coordinator assigning carers and schedules, monthly/annual reports, carers' signatures on nursing records | — | ~2,500 gminas, DPS homes | [NIK audit (DPS)](https://nik.gov.pl/kontrole/wyniki-kontroli-nik/pobierz,lki~p_15_044_201508260909101440580150~id2~01,typ,kj.pdf) |
| Agencies placing Polish carers in Germany (Promedica24 and others) | Recruit and dispatch carers; PineBridge holds 75% of Promedica24 | — | German families | [rp.pl](https://www.rp.pl/rynek-pracy/art5038191-polskie-opiekunki-podbily-europe); [PrivateEquityWire](https://www.privateequitywire.co.uk/pinebridge-acquires-additional-25-cent-stake-promedica24/) |
Three searches (Polish) found **no Polish care-documentation or care-operations product with AI**, and no named SaaS for municipal home care (usługi opiekuńcze). Autocomplete "program dla dps" → "program komputerowy dla dps" exists, so some legacy tools are sought (vendors not identified: unverified).

## 2. Does the Western leader already serve Poland?
- **Minikai** (AU, NDIS), **NAGARA** (JP, Japanese kaigo records), **Cera** (UK), **Zingage/Axle/Arya** (US): each built around its national funder (NDIS, kaigo hoken, NHS/local authority, Medicaid). No Polish site, language or customer found. **Not in PL.**
- Could not check: demo flows (all demo-led).

## 3. Polish demand signals
- Autocomplete: "dokumentacja opiekuńcza" → none; "usługi opiekuńcze program" → "program usługi opiekuńcze 75+", "… dla osób niepełnosprawnych" (searches for the **funding programme**, not software); "program dla dps" → "program komputerowy dla dps".
- The new **bon senioralny**: gmina signs a contract with the senior and may deliver the service itself, via NGOs or private providers; first edition budget 1 bn PLN for 2026–2028, 100 million PLN in 2026 starting Q4; carers need first-aid training ([Bezprawnik](https://bezprawnik.pl/nowa-ustawa-o-opiece-dlugoterminowej/); [Gazeta Prawna](https://www.gazetaprawna.pl/praca/emerytury-i-renty/artykuly/11250625,nowe-swiadczenie-dla-seniorow-po-65-roku-zycia-od-wrzesnia-2026-dla-kogo-darmowa-pomoc-jakie-warunki-trzeba-spelnic-wniosek-pdf-kryterium-dochodowe-zasady-gov.html)). A new population of small providers must document hours for gminas.

## 4. What adaptation needs
Ustawa o pomocy społecznej and the long-term-care coordination law (bon senioralny), gmina contract and settlement formats, MOPS task catalogues per uchwała (scope of care activities differs per gmina), Opieka 75+ and "usługi opiekuńcze dla osób niepełnosprawnych" programme reporting, RODO special-category data (health), M18 Profil Zaufany/M17 ePUAP for submissions, ZOL documentation under NFZ (M22) if extended to medical care. Carers are often 50+ women or Ukrainians (voice notes in Polish/Ukrainian matter).

## 5. Demographic or social driver
**Strong.** DD1 (7.9 million 65+, only ~8 per 1,000 seniors get municipal home care, D13), DD2 bon senioralny as a new publicly funded buyer of care hours (D17), D18 nurse shortage, D38 carers on the shortage list, DD6 Ukrainian carers.

## 6. CEE check
No CZ/SK/RO/HU care-documentation product in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **open gap**
No Polish AI product and no foreign leader present, while the bon senioralny creates thousands of new small providers that must log and settle care hours with gminas from late 2026. The catch: money flows through gminas (low budgets, procurement habits) and providers are small NGOs and micro-firms with thin margins, so willingness to pay is unproven.

**Seed idea:** "Karta usług opiekuńczych": mobile app where a carer dictates a visit note (Polish or Ukrainian) and the app fills the gmina's task-card catalogue, logs time and GPS check-in, and produces the monthly settlement and report the gmina contract requires; sold to private agencies and NGOs delivering bon senioralny and MOPS-contracted care, per carer per month (e.g. 19–29 PLN).
