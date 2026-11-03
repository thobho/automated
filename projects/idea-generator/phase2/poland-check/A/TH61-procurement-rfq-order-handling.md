# TH61 — Procurement, RFQ and order handling (Poland check)

Theme: [THEMES.md#th61](../../themes/THEMES.md#th61) · rank 10, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Comarch ERP (CEE) "Porównanie ofert zakupu" | Classic purchase-offer comparison module inside ERP (no AI reading of emailed RFQs described) | in ERP licence | Comarch ERP users | [Comarch help](https://pomoc.comarch.pl/cee/index.php/documentation/instrukcja-porownanie-ofert-zakupu/) |
| Mimira, Minerva (Poznań) | AI for **public tenders** (bid side), not supplier RFQs; Mimira raised 4M PLN | not found | bidders | [WBJ on Minerva](https://wbj.pl/ai-targets-tenders/post/149513); [Rzeczpospolita PRO](https://pro.rp.pl/pro/art43775851-ai-zdobywa-dla-firm-kontrakty-dotacje-i-klientow-oto-narzedzia-warte-poznania) |
No Polish product that reads emailed customer RFQs/orders and drafts a quote from a wholesaler's catalogue was found in one Polish search.

## 2. Does the Western leader already serve Poland?
- **Mercura** (DE, quote automation for technical wholesalers), **Pactum** (EE, supplier negotiation for enterprises), **zaico** (JP, inventory), **Duvo** (CZ, retail ops agents), **Definic** (SK): no Polish site or Polish customer found (theme rows; not individually re-checked in Polish). Pactum sells to global enterprises that may include Polish subsidiaries (unverified).
- Could not check: Mercura's language support (demo-only).

## 3. Polish demand signals
- Autocomplete: "ai zapytania ofertowe" → none. Low search volume; the buyer is a sales-office manager who would not search this way.
- Indirect: Polish wholesalers advertise RFQs through supplier portals (e.g. Orlen Connect RFx), showing the volume of B2B quoting (not quantified).

## 4. What adaptation needs
M44 InsERT Subiekt/nexo and M41 Comarch (stock and price lists), M04 biała lista for new customers, M11 GUS REGON lookup, M01 KSeF for the resulting invoice, M39 BaseLinker for e-commerce wholesalers; Polish technical vocabulary (EAN/indeks, PKWiU), quotes with netto/brutto and VAT rates, payment terms.

## 5. Demographic or social driver
DD7: labour costs and shortages (D39) push wholesalers to automate inside-sales desks.

## 6. CEE check
Duvo (CZ) and Definic (SK) are in this theme; no evidence either has entered Poland ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **open gap**
No Polish or Western product for AI quoting from emailed RFQs was found serving Polish wholesalers, and the integration targets (Subiekt, Optima) are Polish. Demand is unproven because buyers do not search for it; validation must be through direct outreach.

**Seed idea:** "Oferta z maila": agent for **technical wholesalers (electrical, HVAC, plumbing, fasteners)** on Subiekt nexo or Optima that reads an emailed list of items (PDF, Excel, photo), matches it to the catalogue and stock, and drafts a priced quote for the salesperson to send; priced per seat or per quote.
