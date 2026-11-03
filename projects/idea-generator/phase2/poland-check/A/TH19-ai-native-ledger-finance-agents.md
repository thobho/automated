# TH19 — AI-native ledger and finance-team agents (Poland check)

Theme: [THEMES.md#th19](../../themes/THEMES.md#th19) · rank 5, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Comarch ERP Optima / XL — "Agenci AI" | Five AI agents in Optima 2026.5.1 for repetitive accounting and payroll tasks: cost-invoice posting (dekretator), seller verification, categorisation on KSeF invoice lists; Comarch says agent features reach most Comarch ERP products by end-2026, with human oversight | inside Optima licences (add-on price not checked) | Optima is the most common SME accounting suite (M41) | [Comarch help: Agenci AI w Optima](https://pomoc.comarch.pl/optima/pl/2026_5/dokumentacja/agenci-ai-w-comarch-erp-optima/); [ITwiz](https://itwiz.pl/comarch-wpuszcza-ai-do-biur-rachunkowych/) |
| Symfonia AI Dekret | Add-on proposing postings for KSeF invoices, learns from accountant corrections; needs Symfonia KSeF Plus | not published on the page | Symfonia F&K users | [symfonia.pl AI w księgowości](https://symfonia.pl/oprogramowanie/finanse-i-ksiegowosc/ai-w-ksiegowosci/); [Symfonia blog](https://symfonia.pl/blog/finanse-i-ksiegowosc/ksef-zmienil-import-faktur-czas-zmienic-takze-dekretacje/) |
| AutoMEE, Profluo, Księgoboty | Document automation for firms and offices | not found | not found | ai-landscape S34, S36, S37 |

## 2. Does the Western leader already serve Poland?
- **Payhawk** (BG, >100M USD ARR): Warsaw office, Poland a standalone commercial region (2026-09-30), platform in Polish, **KSeF invoices received directly into AP**, ~30% growth in Polish demand without local sales ([Payhawk blog](https://payhawk.com/en-us/blog/payhawk-expands-in-poland); [FinancialIT](https://financialit.net/news/artificial-intelligence/payhawk-expands-poland-support-growing-businesses-ai-native-spend)). **Serves PL.**
- **Bakuraku (LayerX, JP)**: Japan-only (theme row, R7). **Not in PL.**
- **Xero JAX**: Xero has no Polish localisation known (not checked further).
- Could not check: Payhawk PLN pricing (quote-based), demo access.

## 3. Polish demand signals
- Autocomplete: "ai do faktur" → "agent ai do faktur", "ai faktury"; "ai dla biur rachunkowych" → echo only.
- Press: Comarch and Symfonia market AI posting as a KSeF follow-on (sources above); podatki.biz on KSeF + AI in accounting offices ([podatki.biz](https://www.podatki.biz/artykuly/ksef-ai-i-automatyzacja-ksiegowosci-jak-zmienia-sie-praca-biur-rachunkowych-w-2026-roku_40_62261.htm)).

## 4. What adaptation needs
M01 KSeF, M02 JPK_KR/JPK_CIT, M04 biała lista VAT, M41–M45 ERP integrations (the ERP vendors are the competitors), M50. Polish specifics: split payment (MPP), VAT qualification rules that must stay with an authorised person, plan kont conventions per ERP.

## 5. Demographic or social driver
DD7: accountant shortage (D38) makes posting automation valuable, but incumbents capture it.

## 6. CEE check
Payhawk (BG) has already entered (above). No other R6 ledger player heading to PL ([R6 README](../../research/regions/R6-cee-peers/README.md)).

## 7. Verdict: **taken**
The two dominant Polish ERP vendors ship AI posting agents on KSeF data in 2026, and Payhawk covers mid-market spend and AP with a Warsaw team. An AI-native ledger would have to displace Comarch/Symfonia, a heavy build with an entrenched partner channel.

**Seed idea:** none for the core. Possible residue for TH17/TH18: a vendor-neutral KSeF "anomaly and missing-cost-invoice chaser" that emails suppliers and clients of a biuro rachunkowe, sitting across Optima, Symfonia and Rewizor; check overlap there.
