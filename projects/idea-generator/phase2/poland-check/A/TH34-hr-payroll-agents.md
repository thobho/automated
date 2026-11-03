# TH34 — HR and payroll agents (Poland check)

Theme: [THEMES.md#th34](../../themes/THEMES.md#th34) · rank 6, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Comarch ERP Optima — "Agent dokumentacji ZWUA" | Payroll AI agent: from termination date and reason, fills ZUS deregistration and termination-mode fields for the final payslip and ZUS ZWUA; shows its reasoning; one of 5 Optima agents | inside Optima licence | Optima installed base (M41) | [Comarch help](https://pomoc.comarch.pl/optima/pl/2026_5/dokumentacja/agenci-ai-w-comarch-erp-optima/) |
| Symfonia Kadry i Płace, enova365 HR, InsERT Gratyfikant | Classic Polish payroll suites (AI features not checked) | not checked | SMEs and accounting offices | M42–M44 |
| SD Worx (BE) via TribePerk | Acquired Polish cloud-payroll startup TribePerk to target Polish SMEs | not checked | not checked | [SD Worx press](https://sdworx.co.uk/en-gb/press/sd-worx-acquires-cloud-payroll-startup-tribeperk-expand-polish-sme-market) |

## 2. Does the Western leader already serve Poland?
- **Factorial** (ES, Factorial One agents): entering Poland in 2026 through local partners, no Polish office planned; hiring a Poland country manager and partnership managers ([XYZ](https://xyz.pl/?p=170044); [Antyweb](https://antyweb.pl/jednorozec-z-hiszpanii-wkracza-do-polski-pomoze-w-cyfryzacji-firm); [Factorial careers](https://careers.factorialhr.com/job_posting/partnership-country-manager-poland-market-261966)). **HR yes; Polish payroll (ZUS, PPK, PIT-11) not confirmed**, which fits a partner model where Polish payroll stays in local software.
- **Employment Hero** (AU): no Poland found. **Sloneek** (CZ/SK): Series A partly for a Polish team, announced 2026-06 (R6).
- Could not check: Factorial's Polish demo or PLN pricing (domain factorialhr.pl does not resolve; pricing is behind a demo form).

## 3. Polish demand signals
- Autocomplete: "ai kadry i płace" → echo only (low volume).
- Factorial's Polish hiring and SD Worx's acquisition show vendors expect SME demand ("fragmented HR market", XYZ above).

## 4. What adaptation needs
M07 ZUS PUE/KEDU (no API, highest moat), M06 PPK, e-ZLA sick notes, PIT-11/PIT-4R via M03, M08 praca.gov.pl for foreign workers, Kodeks pracy (urlop, nadgodziny, świadectwo pracy), umowy cywilnoprawne vs etat, M51 biura kadrowo-płacowe as the channel. Pay Transparency Directive (June 2026, brief trigger 10) adds pay-gap reporting work.

## 5. Demographic or social driver
DD6: 1.29M foreigners insured in ZUS (D33), each with permit/oświadczenie deadlines for the employer; DD7: labour shortage makes HR admin per hire heavier.

## 6. CEE check
Sloneek (SK/CZ) announced a Polish team (2026-06); Talentiqa (CZ) blue-collar hiring agent ([R6 README](../../research/regions/R6-cee-peers/README.md)).

## 7. Verdict: **partial**
Payroll calculation is held by Polish suites, and they are starting to add agents (Comarch ZWUA agent); Factorial and Sloneek bring HR suites without proven Polish payroll. Not covered: an agent layer for the employer's Polish HR obligations around the payroll engine, especially for foreign workers, where rules and deadlines multiply.

**Seed idea:** "Legalny pracownik": agent for SMEs and staffing agencies employing foreigners that tracks every worker's permit/oświadczenie/karta pobytu and PESEL UKR status, drafts praca.gov.pl applications and powiadomienia to the urząd pracy within statutory deadlines, and answers workers in Ukrainian; sold per worker per month, channel = biura kadrowo-płacowe.
