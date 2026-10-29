# 013 — Bank-statement reader and categoriser for bookkeeping offices
**One-liner:** Upload a client's bank statement in any format (PDF, scan, photo, odd CSV) and get clean, categorised transaction rows plus suggested account/cost-type assignments learned from the office's earlier decisions, exported to the office's accounting program.
**Field:** ai-agents-automation | **Type:** SaaS
**Target customer:** Polish bookkeeping offices (biura rachunkowe) that process statements for KPiR/ryczałt clients, particularly clients whose banks, credit unions or foreign neobanks give no clean MT940/CSV. Count: unverified.
**Problem:** Matching bank lines to documents and cost categories is manual. wFirma's page shows what exists: import of CSV and MT940 from many Polish banks, automatic pairing to invoices by account number, amount and number, and manual handling for the rest. Where the bank offers no structured file, someone retypes or uses a PDF converter.
**MVP scope (≤6 weeks):** (1) PDF/scan/photo/CSV upload with LLM extraction to a fixed schema and a running-balance check (L5-F27, L5-F28); (2) office-specific categorisation rules learned from past labelled lines, with a "review needed" flag; (3) export CSV and MT940-style for the common programs; (4) per-office usage billing. Not in MVP: ledger posting, bank feeds (PSD2), tax advice.
**Why now:** Cheap, schema-constrained LLM extraction (OpenAI Structured Outputs Aug 2024; Mistral OCR about 1,000 pages per dollar since Mar 2025; Gemini Flash-Lite $0.10 input per 1M tokens) makes any-bank parsing viable for a solo builder (L5-F27, F28). No regulatory trigger.
**Foreign analogues:** DocuClipper (US): from $20.30/month for 60 pages up to $279.30 for 1,800+ pages, automatic categorisation from the Starter tier, claims "10,000+ finance teams" and 4.7/5 from 124 G2 reviews (own page, unverified). Dext includes free credits for bank-statement sheets in its trial (own page). Many cheap converters exist (Statement Desk Workspace add-on, BankStatementLab on Product Hunt, FormulaBot); no revenue figures found for any.
**Competition (PL / global):** Already served in Polish: invoicedataextraction.com has a Polish page ("wyciąg bankowy do Excela"): 50 pages free per month, then pay per page, any bank, PDF/scan/photo, custom categorisation rules, "Review Needed" flag; the page itself says MT940/CSV is usually the better source when the bank provides one. wFirma imports CSV/MT940 from mBank, PKO BP, ING, Santander, Alior and points to AI-assisted import for others; Comarch Optima and Fakturownia (Millennium MT940 app) import structured files. Gap: nothing found that learns an office's own category mapping across many clients; unverified.
**Evidence of pain:** Weak. The competitor page above concedes structured files are the better path, which shrinks the segment to banks without clean exports. No office or accountant was found complaining about bank-statement entry (searched in Polish 2026-10-29; no forum threads read). Search-trend data unreadable; unverified.
**Monetization:** Pay per page (about 0.3–0.5 PLN per page, estimate, undercutting DocuClipper) or 99–299 PLN/month per office by volume. Payer: office. Anchor: JDG fee 150–500 PLN/month (L3-F25) shows the budget exists, but this saves minutes per client, not the whole fee.
**Revenue sketch (estimate):** Assumes 150 PLN per office per month. 6 months: 15 offices = 2,250 PLN MRR. 12 months: 45 offices = 6,750 PLN MRR. 10,000 PLN MRR needs about 67 offices. Market size unverified, 20x check cannot be passed.
**First 10 customers:** Offices working with clients on foreign or small banks; the same cold e-mail list and referral route as idea 012; a free 50-page tier like the competitor's to start usage.
**Build complexity:** medium. Extraction accuracy on multi-column statements, running-balance verification, GDPR for financial data processed by LLM APIs, format variety of exports.
**Pros / Cons / Risks:** Pros: very cheap per page; clear before/after; easy to test with fixtures. Cons: commodity feature, free tiers exist, Polish banks give structured exports, usage-based revenue is lumpy. Risks: customers' bank data (high sensitivity), tool-chain integrations differ per office, accuracy liability.
**Scores (1–5):** L1 2, L2 2, L3 3, L4 3, L5 3, L6 2, L7 4, L8 3, L9 2 | **Weighted:** 2.7 / 5 (computed 2.67) | **Chance band:** <5% (shortlist 2.9; L2 lowered 3 to 2 because a Polish-language any-bank converter with categorisation and a free tier exists; L4 raised 2 to 3 on DocuClipper's claimed scale; L5 lowered 4 to 3; L9 lowered 3 to 2 for commodity pricing)
**Cheapest validation test (≤1 week, ≤200 PLN):** Collect 30 real statements from 6 volunteer offices (PDF), run them through the extractor, report accuracy and time saved; ask each office to pre-order at 99 PLN/month. Success: ≥97% line accuracy and 2 pre-orders.
**Kill criteria:** Fewer than 3 of 15 offices say they handle PDF-only statements monthly; or competitor's free tier satisfies the pilot offices.
**Confidence:** low
**Sources:** (accessed 2026-10-29)
- DocuClipper pricing: https://www.docuclipper.com/pricing/
- Polish any-bank converter page: https://invoicedataextraction.com/pl/wyciag-bankowy-do-excela
- wFirma bank import and matching: https://pomoc.wfirma.pl/-bank
- Comarch Optima MT940 import: https://pomoc.comarch.pl/optima-online/pl/?p=2967
- Fakturownia Millennium MT940 import: https://fakturownia.pl/apps/millenium-mt940-import-app
- mBank MT940 statements: https://www.mbank.pl/firmy/uslugi-serwis-transakcyjny/wyciagi-mt940/
- Dext home page (free bank-statement credits): https://dext.com/
- Converter landscape (Statement Desk add-on): https://workspace.google.com/marketplace/app/statement_desk/131304611577
- Structured Outputs (L5-F28): https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Mistral OCR launch (L5-F27): https://mistral.ai/news/mistral-ocr
- Office fees 150–500 PLN: https://cenauslug.pl/poradniki/ile-kosztuje-prowadzenie-ksiegowosci-porownanie-biur-rachunkowych-i-programow-online
