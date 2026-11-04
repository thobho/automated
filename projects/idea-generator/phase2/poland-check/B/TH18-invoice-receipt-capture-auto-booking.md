# TH18 — Invoice and receipt capture with auto-booking (Poland check)

Theme: [THEMES.md#th18](../../themes/THEMES.md#th18) · rank 36, batch B · sources accessed **2026-11-04** · method: [README](README.md#method). Overlaps [batch A TH19](../A/TH19-ai-native-ledger-finance-agents.md) (AI posting agents).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| SaldeoSMART (Brainshare) | Document flow between firm and accounting office: OCR of cost documents, AI parameters for KSeF invoices, export to accounting systems | OCR billed in credits (1 credit = 1 page); AI parameters for a KSeF invoice 1 credit; KSeF functions free in all packages, with monthly limits in the smallest | accounting offices and their clients (numbers not checked) | [SaldeoSMART packages](https://pomoc.saldeosmart.pl/hc/pl/articles/37636576008861) |
| autoMEE (flowMEE) | "AI-native" accounting platform: document processing, posting, bank reconciliation, live P&L | not published | **700+ firms** via partner offices (2026-09); seed **10M PLN** (Level2 Ventures, 2026-09-30); ARR target >7M PLN by end-2026 | [xyz.pl](https://xyz.pl/?p=255867) |
| Comarch ERP Optima OCR, Symfonia AI Dekret | OCR service and AI posting inside the dominant SME suites (Comarch OCR reads Polish-language documents only) | inside licences | Optima/Symfonia users | [Comarch OCR FAQ](https://pomoc.comarch.pl/optima/pl/2022/kategorie/ocr-faq/); [batch A TH19](../A/TH19-ai-native-ledger-finance-agents.md) |
| Invoicing apps (Fakturownia, FakturaXL, inFakt, wFirma) | Photo/scan of a cost invoice → fields and line items read automatically | inside plans (Fakturownia 30-day trial; per-document price not shown) | hundreds of thousands of SMEs | [Fakturownia OCR](https://fakturownia.pl/funkcja-ocr); [FakturaXL](https://www.fakturaxl.pl/jak-dziala-ocr-do-faktur) |

## 2. Does the Western leader already serve Poland?
- **Digitoo** (CZ, 1M+ invoices, EUR 2.3M seed): help centre and case studies are Czech/English with Czech integrations (ABRA Flexi, Fakturoid); no Polish page or Polish customer found; its blog says it supports Latin script only ([Digitoo help](https://help.digitoo.ai/en/article/what-is-digitoo); [Digitoo blog](https://digitoo.ai/blog/invoice-processing)). **Not in PL.**
- **Outmin** (IE, 350+ businesses), **Autoboeker** (NL), **Cifrato** (CO, YC W25): home-market integrations and tax rules (catalogue rows). **Not in PL.**
- Could not check: Digitoo extraction quality on Polish invoices (would need an account).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "ocr faktur" → 10 (fakturownia, zakupu, api, co to, fakturaxl); "skanowanie paragonów" → 3 (do excela, aplikacja); "paragon z nip" → 10, several about KSeF ("a ksef", "jakie oznaczenie ksef", "do kiedy"); "księgowanie faktur ai", "odczyt faktur z pdf", "faktury zagraniczne księgowanie" → empty or echo.
- Trade press asks "will KSeF replace OCR?": vendors answer that receipts, foreign invoices and pre-KSeF documents still need OCR ([Fakturowo](https://www.fakturowo.pl/blog/czy-ksef-zastapi-ocr); [FakturaXL](https://www.fakturaxl.pl/czy-ksef-zastapi-ocr-faktur)).

## 4. What adaptation needs
M01 KSeF shrinks the capture problem: from 2026-04 most taxpayers issue in KSeF and from 2027-01 all do, so domestic B2B invoices arrive as structured XML. What stays is paper receipts with NIP (outside KSeF until 2026-12-31 per press), foreign invoices (ads, SaaS, EU suppliers), M04 biała lista checks, bank-statement matching, and posting rules per ERP (M41–M45), where Comarch and Symfonia are the competitors.

## 5. Demographic or social driver
DD7: accountant shortage (independent accountants on the shortage list) keeps demand for automation in accounting offices.

## 6. CEE check
Digitoo (CZ) and Profluo (RO, EUR 500k seed 2022) do document capture at home; neither has a Polish presence found. Payhawk (BG) already serves Poland on the spend side (batch A TH19).

## 7. Verdict: **taken**
Capture is bundled into every Polish invoicing and ERP product, SaldeoSMART owns office–client document flow, and autoMEE raised 10M PLN for the AI-native version; KSeF also removes most of the domestic invoice-capture job from 2027. A newcomer would compete with incumbents for a shrinking residue.

**Seed idea (weak, residue):** a "non-KSeF cost document" inbox for accounting offices: collects foreign SaaS/ad invoices (Google, Meta, AWS, Allegro Ads) straight from supplier portals and e-mail, adds NBP exchange rates and reverse-charge/import-of-services flags, exports to Optima/Symfonia; per client 10–20 PLN/month. Check overlap with SaldeoSMART first.
