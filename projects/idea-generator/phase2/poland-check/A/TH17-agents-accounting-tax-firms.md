# TH17 — Agents for accounting and tax firms (Poland check)

Theme: [THEMES.md#th17](../../themes/THEMES.md#th17) · rank 13, batch A · sources accessed **2026-11-03** · method: [README](README.md#method). See also [TH19](TH19-ai-native-ledger-finance-agents.md) and [TH16](TH16-ai-accountant-micro-businesses.md).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Comarch ERP Optima agents | KSeF invoice verification, cost qualification, categorisation, posting, ZUS ZWUA agent; run automatically on each KSeF document | in licence | biura rachunkowe on Optima | [Comarch help](https://pomoc.comarch.pl/optima/pl/2026_5/dokumentacja/agenci-ai-w-comarch-erp-optima/) |
| Symfonia AI Dekret | Posting proposals for KSeF invoices | not published | Symfonia users | [symfonia.pl](https://symfonia.pl/oprogramowanie/finanse-i-ksiegowosc/ai-w-ksiegowosci/) |
| SaldeoSMART | Document circulation/OCR for accounting offices, KSeF integrated for all customers incl. **3,000 accounting offices** | not checked | 3,000 biura rachunkowe | [INFOR expert page](https://www.infor.pl/eksperci/6473,SaldeoSMART.html) |
| AutoMEE (flowMEE), Księgoboty | AI booking and workflow for offices | not found | not found | ai-landscape S34, S37 |

## 2. Does the Western leader already serve Poland?
- **DataSnipper** (NL, audit automation in Excel; 400k+ auditors in 125 countries incl. Big Four) is used by Big Four teams, which include Polish offices (presence in PL not separately confirmed). English-first UI.
- **Juno** (US tax prep), **Ravical** (BE), **TreuhandGPT** (CH), **Repodo** (DK): home-market tax systems; no Polish presence. **Not in PL.**
- Could not check: DataSnipper Polish-language support.

## 3. Polish demand signals
- Autocomplete: "ai dla biur rachunkowych" → echo only.
- Press: INFOR, prawo.pl and podatki.biz run recurring "AI w biurze rachunkowym" pieces and trainings ([prawo.pl](https://www.prawo.pl/podatki/ksiegowanie-e-faktur-co-zmieni-ksef-w-praktyce-biur-rachunkowych,536594.html); [podatki.biz](https://www.podatki.biz/artykuly/ksef-ai-i-automatyzacja-ksiegowosci-jak-zmienia-sie-praca-biur-rachunkowych-w-2026-roku_40_62261.htm)); INFOR on offices that price clients poorly ("1 na 60") ([infor.pl](https://www.infor.pl/biura-rachunkowe/prowadze-biuro/7594837,1-na-60-dlaczego-biura-rachunkowe-nadal-nie-budzetuja-klientow.html)).

## 4. What adaptation needs
M01 KSeF, M02 JPK, M07 ZUS via PEL power of attorney, M41–M44 (Optima, Symfonia, enova, Rewizor), M51 offices as the channel, M05 EUREKA for interpretations; tax-advice monopoly limits what an agent may tell clients (A26).

## 5. Demographic or social driver
DD7: independent accountants on the shortage list (D38).

## 6. CEE check
Quillon (BG, technical-accounting AI) is global; Digitoo (CZ) and Bookkeepie (HU) not seen in PL ([R6 README](../../research/regions/R6-cee-peers/README.md)).

## 7. Verdict: **partial**
Posting and document capture inside the ledger are taken by Comarch, Symfonia and Saldeo. What sits outside the ledger is open: chasing clients for missing documents and answers, explaining month-end results, pricing clients by workload.

**Seed idea:** "Asystent klienta biura": agent that runs the **office–client conversation** for a biuro rachunkowe: compares KSeF purchase invoices with bank statements, asks each client on WhatsApp/e-mail for missing receipts and explanations, collects answers into Optima/Saldeo, and reports per-client workload for repricing; priced per client of the office.
