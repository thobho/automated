# TH62 — AI-native engineering design (Poland check)

Theme: [THEMES.md#th62](../../themes/THEMES.md#th62) · rank 48, batch C · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Building-services CAD (installation design programs) | Calculation and drawing software for HVAC, sanitary and electrical design; rule-based, no AI design-as-outcome found | licences (not checked) | biura projektowe | autocomplete only (see §3); vendors not re-verified |
| Blue Boson (PL) | AI control of heating installations (operation, not design) | not found | not found | [itkey.media](https://itkey.media/?p=24780) |
| Biura projektowe instalacji | Human design offices; autocomplete lists many local offices (electrical, sanitary, gas) | per project | investors, contractors | §3 |

No Polish company selling AI-produced building-services design as an outcome (the Solvera/Endra model) was found in one web search in Polish and the R6 catalogue.

## 2. Does the Western leader already serve Poland?
- **Solvera** (NO): acts as the responsible designer (*ansvarlig prosjekterende*) for ventilation, piping and electrical; customers pay for the result; 10M+ NOK contracted in its first three months from July 2026; customer Betonmast; next office London, no other markets named ([Shifter, 2026-10](https://www.shifter.no/nyheter/henter-inn-60-millioner-kroner-etter-noen-maneder-i-drift/303542)). Not in Poland.
- **Endra** (SE) and **Trace.Space** (LV, requirements management) are home-market or horizontal; not checked further.
- The outcome model cannot be copied by software alone: in Poland design documentation must be signed by a person with *uprawnienia budowlane* in the right speciality and membership of the chamber (PIIB). Autocomplete for "uprawnienia instalacyjne" returns 10 suggestions, showing the role is well known.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "program do projektowania instalacji" → 10 (electrical, home electrical, free c.o., sanitary, lightning protection, hydraulic); "biuro projektowe instalacji" → 10 (electrical, sanitary, gas, city names); "warunki techniczne 2026 zmiany" → 4 incl. "warunki techniczne zmiany wrzesień 2026"; "ai projektowanie budynków" → echo only; "projekt instalacji wentylacji cena" → none.
- Regulatory churn: the 2002 *warunki techniczne* regulation was due to lapse on 2026-09-20 while the new one was not published; reports say transitional rules allow the old conditions for 18 more months, and PIIB and IARP published an open letter ([Murator Dom](https://muratordom.pl/prawo/formalnosci-budowlane/nowe-warunki-techniczne-spoznione-ratunek-w-prowizorce-stare-przepisy-jeszcze-przez-18-miesiecy-aa-xhtt-Q8pc-pTxz.html); [Inżynier Budownictwa: "Nowych warunków technicznych nie ma"](https://inzynierbudownictwa.pl/nowych-warunkow-technicznych-nie-ma-co-dalej/); [PIIB/IARP open letter PDF](https://inzynierbudownictwa.pl/wp-content/uploads/2026/09/List-otwarty-PIIB-IARP.pdf)). Read from search excerpts; status after September 2026 unverified.

## 4. What adaptation needs
Polish Prawo budowlane and the *warunki techniczne* regulation (in flux, see §3), Polish norms (PN-EN, PN-HD for electrical), *uprawnienia budowlane* and PIIB membership for signing, projekt budowlany vs projekt techniczny split, energy-performance (EP) limits, M28 Geoportal/MPZP for site data. None of these is a software integration; they are professional-liability rules.

## 5. Demographic or social driver
DD7: installers and electricians are shortage occupations; DD10: 208k completions in 2025 keep design offices busy. The bottleneck is licensed engineers' time.

## 6. CEE check
Trace.Space (LV) is requirements software, not design-as-outcome; no CZ/SK/RO/HU equivalent in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **open gap** (poor founder fit)
Nobody in Poland sells AI-produced building-services design, and Solvera is not coming soon. But the model needs licensed engineers who sign and carry liability, i.e. hiring staff and professional insurance, which the founder profile excludes; a software-only version competes with established installation CAD.

**Seed idea:** "Sprawdzacz WT": a pre-submission checker for design offices that reads a projekt budowlany/techniczny PDF and lists clauses of the applicable *warunki techniczne* (old or new, with the transition date logic) and the EP limits it may breach; 199–399 PLN/month per office. Weak until the new regulation is published.
