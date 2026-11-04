# TH03 — Healthcare back-office automation (Poland check)

Theme: [THEMES.md#th03](../../themes/THEMES.md#th03) · rank 38, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| HIS and clinic software (Asseco AMMS, KAMSOFT, CGM, Optimed, MyDr) | NFZ reporting and settlement (SWIAD messages via Portal Świadczeniodawcy/SZOI) built into the hospital or clinic system | licences (not checked) | almost every NFZ contractor | catalogue note for Parallel ([R0 catalogue](../../catalogue/R0-global.csv)); job-ad systems via search (pracuj.pl blocked to fetcher) |
| JGP groupers and "optimisers" (e.g. SGA) | Grouper with a "prompter" that shows settlement variants for diagnoses and procedures; one case can fit about four JGP groups with different prices | not published | hospitals | [rp.pl interview](https://www.rp.pl/wydarzenia/art12966831-to-system-finansowania-zdrowia-stworzyl-patologie) |
| NFZ tools | NFZ's own JGP query returns the list of JGP codes a provider could report, to be checked against its contract | free | NFZ contractors | [NFZ JGP komunikat](https://www.nfz.gov.pl/dla-swiadczeniodawcy/jednorodne-grupy-pacjentow/komunikaty-jgp/komunikat,37.html); [NFZ JGP guide (2021)](https://www.nfz.gov.pl/gfx/nfz/userfiles/_public/o_nfz/publikacje/2021/jednorodne_grupy_pacjentow_-_przewodnik_po_systemie.pdf) |
| Human staff and outsourcing | "Specjalista ds. rozliczeń z NFZ" is a common job title in Kraków, Łódź, Warsaw (job-board search results; pracuj.pl blocks the fetcher); training seminars on JGP coding and NFZ audits appear in search (seminar PDF now 404, unverified) | salaries (not checked) | hospitals and clinics | autocomplete in section 3 |

No Polish LLM product for coding or settlement was found in web search.

## 2. Does the Western leader already serve Poland?
- **Tennr** (US, Series C USD 101M): reads faxed referrals for US practices; Poland's referrals are already electronic (e-skierowanie, M24). **Not in PL**, and the core job does not exist here.
- **Parallel** (FR, YC W24): computer-use agents on French hospital software. **Not in PL.**
- **Asepha** (CA): pharmacy admin agents for North American workflows. **Not in PL.**
- US coding/claims players (Codes Health, Trellis, Candid, Arintra): built on US payers and ICD-10-CM/CPT. **Not in PL.**
- Could not check: whether Parallel plans other EU countries (no public statement found).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "rozliczenia nfz" → 10, mostly job-seeking ("praca", "praca zdalna", "kurs", "szkolenie", "cennik", city names); "kodowanie jgp" and "sprawozdawczość nfz program" → echo or empty.
- Recurring job ads and paid training show the work is done by people, but searches are by staff, not buyers of software.

## 4. What adaptation needs
NFZ settlement rules (zarządzenia Prezesa NFZ change often), JGP grouper logic, ICD-10 and ICD-9 PL procedure codes, SWIAD/SZOI interfaces, M24 P1 platform and EDM records; integration with the HIS (AMMS, KAMSOFT, CGM), which is the hard part and is where incumbents sit. Patient data is special-category under RODO, and hospitals are NIS2/KSC entities.

## 5. Demographic or social driver
DD3: queues and private spending grow, and DD7: medical admin staff are scarce. Most settlement value sits with hospitals, which buy via tenders (excluded by the brief).

## 6. CEE check
No R6 healthcare back-office agent in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **partial**
No LLM product does NFZ coding or settlement checks, and Western leaders solve US-payer problems that do not exist here. But the buyers who gain most (hospitals) buy through tenders and through their HIS vendor, the data is sensitive, and upcoding risk is under NFZ audit, which makes a solo-founder product hard. A narrower B2B segment is open: private outpatient clinics with NFZ contracts (AOS, rehabilitation) that settle monthly and lose money on rejected or unreported services.

**Seed idea:** "Kontrola rozliczeń NFZ" for outpatient clinics: before monthly submission, an agent reads the export of visits and documentation, flags services missing from the report, codes that will be rejected, and limit overruns against the contract, with a plain-Polish explanation for the settlement clerk; 299–799 PLN/month per clinic. Needs a pilot clinic to supply anonymised exports; no clinical decisions, so outside AI Act high-risk.
