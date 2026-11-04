# TH55 — Insurance operations agents (Poland check)

Theme: [THEMES.md#th55](../../themes/THEMES.md#th55) · rank 39, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| CUK Ubezpieczenia (WebCUK) | Multiagency network with its own system to compare and issue policies of about 40 insurers in one place; recruits agents and franchise points | agent commission model (not checked) | "over 600" points (company) | [cuk.pl for agents](https://cuk.pl/wspolpraca/z-jaka-multiagencja-warto-wspolpracowac) |
| Online comparison sites (Rankomat, Mubi, Punkta and others) | Motor OC/AC quote comparison for consumers; average OC premium ~667 PLN in Q1 2026 per CUK | free to users, paid by insurers | consumers | [cuk.pl OC guide](https://cuk.pl/porady/gdzie-oc) |
| Minte.ai | AI that reviews medical claim documents against OWU and proposes payout or denial with reasons | B2B (not published) | UNIQA Polska live; 2 paid PoCs, 2 pilots; 2M PLN raised (2025-01) | [polandinsight.com](https://polandinsight.com/minte-ai-secures-pln-2-million-for-ai-driven-insurance-innovation-16644/) |
| Generic CRMs and Insly (EE) | Insurance CRMs/policy admin marketed in Polish (Pipedrive, Creatio, Insly in Polish-language rankings) | various | not checked | [croclub.com ranking](https://croclub.com/pl/tools/10-najlepszych-programow-crm-dla-ubezpieczen-przeglad-na-2026-rok/) |

No Polish LLM agent for broker submission intake or servicing was found.

## 2. Does the Western leader already serve Poland?
- **Handle** (MX, a16z seed USD 6M, 75+ brokers): unifies e-mail, WhatsApp, CRM and Mexican insurer portals. **Not in PL.**
- **Foliume** (UY): quotes, renews and handles claims from PDFs and e-mails; clients in Spain, Germany and Portugal per catalogue row. **Not in PL** (no Polish client found).
- **Outmarket**, **Covu**, **FurtherAI**, **Harper** (US): US P&C agency and carrier workflows, ACORD forms, US licences. **Not in PL.**
- Could not check: Foliume's language support beyond its listed markets (demo-led).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "program dla multiagencji" → 2 (incl. "ubezpieczeniowej"); "program dla agenta ubezpieczeniowego" → echo only. Low search volume, as expected for a niche B2B tool.
- Job ads for "partner multiagencji" appear on job boards (search results), showing the agent network model.

## 4. What adaptation needs
Polish insurer portals and calculators (each TU has its own), OWU documents in Polish and their comparison, UFG and CEPiK data for motor (M21), KNF agent/broker registers, IDD rules (APK needs analysis must be documented before sale), RODO on health data for life and claims, VAT-exempt insurance commissions. Commercial lines (SME property, OC działalności, transport OC przewoźnika, linked to [TH60](TH60-freight-logistics-agents.md)) run on e-mail RFQs to insurers' underwriters.

## 5. Demographic or social driver
DD7: agent and broker offices are small and short of staff; DD10: mortgage revival brings property and life insurance volume. No strong specific driver.

## 6. CEE check
Insly (EE, outside R6) sells policy admin in the region; no R6 insurance agent in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **partial**
Retail motor and home comparison is served by multiagency systems (WebCUK) and consumer comparison sites, and the claims side has a Polish AI player selling to insurers (Minte.ai). The broker back office for **commercial lines**, where submissions go by e-mail with spreadsheets and OWU must be compared clause by clause, has no LLM product found and no Western entrant.

**Seed idea:** submission and OWU comparison agent for small Polish brokers in SME lines: reads the client's questionnaire and documents, drafts RFQs to 5–8 insurers, parses returned offers and OWU into a side-by-side table of limits, exclusions and franchises, and pre-fills the IDD needs analysis; 299–599 PLN/month per broker office. Start with one line (OC przewoźnika or SME property).
