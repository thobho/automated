# TH16 — AI accountant for micro-businesses and sole traders (Poland check)

Theme: [THEMES.md#th16](../../themes/THEMES.md#th16) · rank 1, batch A · all sources accessed **2026-11-03**.
Method for every batch-A file: [README.md](README.md#method). Nothing was signed up for; leaders were checked through their public site, pricing, language switcher and help pages.

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| inFakt Plus (Kraków) | Online accounting for JDG; AI books cost invoices from KSeF, PDF and photos ("up to 90% book themselves"), computes tax and ZUS | from 59.90 PLN net/month (annual); 30-day trial | "over 100 thousand firms" (company) | [infakt.pl/infakt-plus](https://www.infakt.pl/infakt-plus/) |
| mojaKsięgowa.ai "Klara" (Poznań) | AI-agent bookkeeping for JDG: invoices, KPiR, ZUS, KSeF | not found | not found (sponsored interview) | [Spider's Web, 2026-09](https://spidersweb.pl/2026/09/klara-mojaksiegowa-ai-wywiad.html); ai-landscape S33 |
| iFirma, wFirma, Fakturownia | Self-service invoicing/accounting apps, some with an accounting-office tier | third-party guide: from 29–49 PLN/month (self-service); online offices 250–900 PLN/month | not checked | [Freenance guide 2026](https://freenance.io/ile-kosztuje/ile-kosztuje-ksiegowa-jdg-2026-biuro-rachunkowe-vs-samoobsluga/) (secondary, prices unverified) |
| Bookeper AI, AutoMEE, Księgoboty | OCR/AI booking for JDG or for accounting offices | not found | not found | ai-landscape S34–S37 |

## 2. Does the Western leader already serve Poland?
- **Osome** (SG, theme leader by revenue): country selector shows only Singapore, Hong Kong, UK and UAE; no Polish, no Poland ([osome.com](https://osome.com/)). **Does not serve PL.**
- **Accountable** (BE/DE): Belgium and Germany only, NL/FR/EN, EUR pricing ([accountable.eu](https://www.accountable.eu/)). **Does not serve PL.**
- **Norman (Norman AI GmbH, DE)** — **already in Poland.** Polish site with KSeF invoice import, bank matching, KPiR, VAT register, JPK_V7 prepared for approval, PIT/ZUS calculation, Polish AI chat; PLN prices net + VAT: JDG Mini 9–12 PLN, **JDG Pro 29.25–39 PLN**, sp. z o.o. Pro 36.75–49 PLN, Max 89.25–119 PLN per month; 30-day trial without card; "8,000+ entrepreneurs across all markets"; states it is "software, not tax advice"; no human accountant included, the user's own accountant gets free access ([norman.finance/pl](https://norman.finance/pl)). It also runs Polish SEO content for JDG ([blog](https://norman.finance/pl/blog/jak-sprawdzic-ksiegowosc-ai)).
- Could not check: the signup flow itself, whether invoices from Norman carry Polish VAT/KSeF numbers, Polish customer case studies.

## 3. Polish demand signals
- Google autocomplete (pl): "księgowa ai" → "moja ksiegowa ai"; "księgowość ai" → "księgowość z ai", "agent ai ksiegowosc"; "biuro rachunkowe online" → "cennik", "ranking", "rozliczenie pit" (see README method). Searches exist but are low-variety: an early category.
- Press: INFOR reports that over 80% of accountants use AI outside employer control ([ksiegowosc.infor.pl](https://ksiegowosc.infor.pl/wiadomosci/7596279,kawa-z-inforlex-ai-w-ksiegowosci-i-biurach-rachunkowych.html)).
- Base: ~2.5M+ active JDG in CEIDG (local-moats M10); KSeF mandatory for all VAT firms in 2026 (M01).
- No forum threads about "AI accountant" services found in one search (Wykop/Facebook not searchable without login).

## 4. What adaptation needs
M01 KSeF, M02 JPK_V7, M03 e-Deklaracje, M07 ZUS PUE (no API: highest moat), M10 CEIDG, M46 integration with/replacement of Fakturownia/inFakt/wFirma, M50 Polish VAT invoices, M51 accounting offices as gatekeepers, M32 BLIK for payment. Polish-specific: choice of tax form (skala/liniowy/ryczałt), ZUS ulgi (ulga na start, mały ZUS plus), doradztwo podatkowe rules (A26) which push "software, not advice" positioning, and the liability question (who answers to US/ZUS at a control).

## 5. Demographic or social driver
DD7: independent accountants are a shortage occupation (demography D38), so accounting-office capacity is tight; DD6: 1.29M foreigners in ZUS, many running JDG, who need English/Ukrainian-language accounting.

## 6. CEE check
Pattern repeated in R6: Declaro (RO, e-Factura/SPV, from 49 EUR/month), Bookkeepie (HU), FiskAI (HR); none found entering Poland. Nexana.ai (SK, legal + accounting Q&A) is active in PL; Paysera AI bookkeeping (LT) reportedly includes PL (R4 log). See [R6 README](../../research/regions/R6-cee-peers/README.md).

## 7. Verdict: **taken** (for self-service AI bookkeeping) / **partial** (for done-for-you with a human accountant)
Self-service AI bookkeeping for JDG is crowded: inFakt (100k+ firms) ships AI booking, and a German AI-native entrant (Norman) already sells KSeF + JPK_V7 + ZUS at 29–39 PLN, below what a solo founder can undercut. What remains is the done-for-you, liability-bearing service (Osome/Hnry model: a licensed accountant signs, AI does the work) for niches the apps serve poorly. Overall: **partial**.

**Seed idea:** "Biuro rachunkowe AI dla obcokrajowców na JDG": fixed-price online accounting office for foreign sole traders in Poland (Ukrainian, Belarusian, Indian IT contractors on B2B), in UA/EN/RU, with AI doing KSeF/JPK/ZUS prep and a partner biuro rachunkowe signing; wedge = JDG registration in CEIDG + ZUS choice explained in the client's language.
