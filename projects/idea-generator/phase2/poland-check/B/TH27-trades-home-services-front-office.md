# TH27 — Trades and home-services front office (Poland check)

Theme: [THEMES.md#th27](../../themes/THEMES.md#th27) · rank 27, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| "Kalkulator Kosztorysu" (Android) | Mobile quotes/estimates for contractors and renovation firms: own price catalogue, net/VAT/gross, PDF export; no AI | not found | not stated | [instalki.pl listing](https://www.instalki.pl/download/android/produktywnosc/kalkulator-kosztorysu/) |
| "Koszty budowy" (iOS) | Construction cost estimator app | not checked | not stated | [App Store](https://apps.apple.com/vu/app/koszty-budowy/id6443808069) |
| Formal estimating software (Norma PRO, Zuzia and similar, KNR/Sekocenbud catalogues) | Kosztorysy for tenders and investors; desktop, for professional estimators rather than small crews | licence (not checked) | kosztorysanci, construction firms | first-thought list in [THEMES.md#th27](../../themes/THEMES.md#th27), not re-verified |
| Lead marketplaces (Fixly by OLX, Oferteo) | Connect homeowners with tradespeople; Fixly covers 12 service categories | pay-per-lead (rates not found) | tradespeople | [Dealroom: Fixly](https://app.dealroom.co/companies/fixly) |
| Elektroda forum thread | Developer discussing an AI quoting tool for electricians: AI drafts the quote skeleton, electrician verifies; idea stage | — | — | [elektroda.pl topic](https://www.elektroda.pl/rtvforum/topic4133476.html) (page timed out on fetch; summary from search excerpt) |

No Polish product that turns a phone call, WhatsApp photos or a site visit voice note into a priced offer, schedule and invoice (the plancraft/Handoff pattern) was found.

## 2. Does the Western leader already serve Poland?
- **plancraft** (DE): 30,000+ craftsmen; locales DE, AT, UK, NL, IT, ES; **no Polish locale or mention of Poland** ([plancraft.com](https://plancraft.com/)). German Handwerk workflow (Angebot → Auftrag → Rechnung, GAEB/DATANORM).
- **Handoff** (US, AI remodel estimates), **Avoca** and **Elyos AI** (US/UK AI call answering for trades), **Installer** (NO), **autarc** (DE heat-pump installers): home markets only, English/German.
- Could not check: plancraft or Handoff trial signup (no Polish option visible, so not attempted).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "program dla firmy budowlanej" → 2 (incl. "księgowy"); "kosztorys ai" → "kosztorys budowlany ai"; "aplikacja dla fachowców" → echo only; "program do wyceny remontów", "program do ofert dla instalatorów" → none; "czyste powietrze wniosek pomoc" → 1. **Low search volume** for software; tradespeople do not search for tools.
- Czyste Powietrze requires an energy audit and devices from the ZUM list before a heat-pump grant; the device list is updated until the programme ends in 2029, a paperwork step installers carry for clients ([GLOBEnergia](https://globenergia.pl/7-zasad-dla-pomp-ciepla-co-nalezy-ustalic-przed-inwestycja-w-programie-czyste-powietrze/); [gramwzielone.pl](https://www.gramwzielone.pl/walka-ze-smogiem/103941/nowa-lista-urzadzen-kwalifikujacych-sie-do-dotacji-z-czystego-powietrza)).

## 4. What adaptation needs
M46 Fakturownia/inFakt/wFirma (most crews invoice there), M01 KSeF for B2B jobs, M50 VAT invoices (8% VAT for renovation in housing vs 23%), M40 OLX/Fixly leads, M32 BLIK deposits, KNR/Sekocenbud price catalogues, Czyste Powietrze/Mój Prąd paperwork (NFOŚiGW, ZUM list), M53 no Polish Siri/Alexa, so voice capture must be built in. The buying habit is phone + WhatsApp/Messenger photos.

## 5. Demographic or social driver
DD7: construction installers are on the shortage list and unemployment is 3.1%, so trades are overbooked; the pain is admin time per quote, not lead flow. DD9/DD10 suburban houses and 208k completions in 2025 sustain fit-out and renovation demand.

## 6. CEE check
No CZ/SK/RO/HU trades front-office AI in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **open gap**
No Polish AI quoting/front-office product for small crews, and plancraft (the European leader) has no Polish locale. Demand is unproven: tradespeople barely search for software, so distribution through wholesalers (hurtownie), manufacturers' installer programmes (Viessmann-type) or Fixly would be needed.

**Seed idea:** "Wycena z notatki": voice note or WhatsApp photos from a site visit → itemised offer with materials from the installer's own price list, correct 8%/23% VAT, PDF/SMS to the client, then invoice via Fakturownia/inFakt; start with heat-pump and PV installers and add a Czyste Powietrze checklist (audit, ZUM device, wniosek documents); 79–149 PLN/month per firm.
