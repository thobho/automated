# TH45 — Natural-language analytics over company data (Poland check)

Theme: [THEMES.md#th45](../../themes/THEMES.md#th45) · rank 51, batch C · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| **Comarch ChatERP** | AI assistant inside Comarch ERP: guidance, questions over stored data ("top five debtors"), actions (set a credit limit); **beta**, demo in Comarch ERP Optima; to be integrated in all Comarch ERPs, on-premise and cloud; queries go to Comarch or subcontractors | not published | beta users | [Comarch: ChatERP](https://www.comarch.com/erp/ai-assistant/) |
| Comarch BI Point + ChatERP | Comarch's 2025 annual report lists natural-language reporting and analysis and a move "toward autonomous AI agents" in its ERPs | bundled (not published) | Comarch ERP base | [Comarch Annual Report 2025 (PDF)](https://www.comarch.com/files-com/file_975/Comarch-Annual-Report-2025.pdf) (read from search excerpt) |
| Symfonia eDokumenty AI chat | Help assistant over Symfonia's manuals (BETA), not a data-query tool | bundled | Symfonia users | [Symfonia blog](https://symfonia.pl/blog/procesy-w-firmach/obieg-dokumentow/czat-ai-w-symfonii-edokumenty/) |
| enova365 | Marketing mentions BI reports and AI in document workflow; no natural-language data chat found | — | — | search excerpt only, not verified |
| InsERT (Subiekt GT/nexo), Asseco WAPRO | No AI or natural-language reporting found in one search | — | — | — |

## 2. Does the Western leader already serve Poland?
- **Zeit AI** (DE, YC S24, 12 staff): plain-English questions over SAP/ERP/CRM data; no Polish ERP connectors found ([YC directory](https://www.ycombinator.com/companies/zeit-ai)).
- **iGenius/Domyn** (IT) sells to large enterprises (Allianz, Intesa); **Primero** (MX) to LatAm enterprises ([LatamList](https://latamlist.com/primero-raises-12m-seed-round-led-by-kaszek-and-general-catalyst/)).
- Microsoft Power BI Copilot and general assistants with database connectors answer Polish questions over any SQL source; autocomplete shows "power bi comarch optima", so some Optima users already pipe data into Power BI.
- Could not check: ChatERP beta itself (requires the Optima demo install).

## 3. Polish demand signals
- Autocomplete (2026-11-05): "ai comarch optima" → 3 incl. "agenci ai comarch optima" and "ai w comarch optima"; "chaterp comarch" → 2 incl. "comarch chaterp beta"; "power bi comarch optima" → echo; "raporty z subiekta", "analiza sprzedaży subiekt gt", "dashboard dla właściciela firmy" → none. Interest concentrates on the platform owner's own AI.

## 4. What adaptation needs
M41 Comarch Optima/XL (partner API), M44 InsERT Sfera SDK (paid licence) for Subiekt GT/nexo, M43 enova365 SDK, M45 WAPRO databases; Polish accounting concepts (JPK, VAT registers, *należności/zobowiązania*, KSeF numbers from M01) in the semantic layer; on-premise SQL Server installations are common, so a local connector is needed. M51: accounting offices hold the books of many SMEs and could be the channel.

## 5. Demographic or social driver
None direct; DD12 rising wages make the owner's own analysis time more expensive. Weak.

## 6. CEE check
No CZ/SK/RO/HU NL-analytics product for local ERPs (Pohoda, Money S3) in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **partial**
Comarch, the largest Polish ERP vendor, is shipping ChatERP inside Optima (beta), so the biggest installed base will get the feature from its platform owner. InsERT (Subiekt), enova365 and WAPRO users have no natural-language data layer yet, but each vendor can add one in a release, and generic tools (Power BI Copilot, assistants with SQL connectors) already work in Polish.

**Seed idea:** "Zapytaj Subiekta": read-only connector for Subiekt GT/nexo databases with a Polish semantic layer (margins, overdue receivables, stock rotation, sales by sales rep), answering owners' questions in Polish and sending a Monday summary; 99–199 PLN/month per firm, sold through InsERT partners. Platform risk: InsERT can build it.
