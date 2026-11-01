# United States: finance, tax, accounting and insurance (T05)

Part of the US scan; index in [united-states.md](united-states.md). All sources accessed **2026-11-01**. "Read" = page opened; "excerpt" = search-engine summary only (unverified).

## Findings

| # | Product | What it does | Traction (date) | Source | Polish angle |
|---|---|---|---|---|---|
| US-F01 | **Filed** | Full tax-return lifecycle for tax firms: reads documents, applies the firm's approach, enters data into the firm's software, flags review cases | 17.2M USD (Northzone), 2025-05 (read) | [TechCrunch](https://techcrunch.com/2025/05/21/field-raises-17m-to-automate-the-drudgery-of-tax-prep) | PIT/CIT preparation in biura rachunkowe: PIT-37/36/38, PIT-11 and broker statements, e-Urząd Skarbowy |
| US-F02 | **Accrual** | Combined tax preparation and review: agents organise client documents (K-1s, 1099s, photos, long statements), flag missing info, draft follow-up questions and returns | 75M USD (General Catalyst), 2026-02 (read) | [Yahoo Finance](https://finance.yahoo.com/news/accrual-debuts-75m-funding-build-120311209.html) | document intake + missing-docs chasing for biura rachunkowe (KSeF invoices, wyciągi, PIT-11) |
| US-F03 | **Accordance** | AI-native multi-agent co-pilot for accounting and tax firms trained on tax authorities | 13M USD (Khosla seed + GC pre-seed), 2025-09 (read) | [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2025/09/22/accordance-raises-13m-for-ai-platform-for-tax-accounting-practices/169424/) | Polish tax research over KIS interpretacje + NSA rulings (see TaxGPT R0, Blue J in Canada) |
| US-F04 | **Juno** | Tax-prep data entry for small and mid-size firms: ~90% of entry across 90+ document types; priced per return (~45 USD, low 30s at volume) | Seed 12M USD, 2026-04; nearly 500 customers; "mid-seven-figure ARR" in eight months (read) | [Crunchbase News](https://news.crunchbase.com/fintech/cpa-founded-ai-tax-return-startup-juno-seed-funding/) | per-return pricing fits biura rachunkowe; Polish forms differ fully |
| US-F05 | **Fifteenth** | Year-round AI-assisted tax planning for tech workers with equity, flat fee from 1,000 USD/year | Seed 8.25M USD (A*, General Catalyst), 2025-02 (read) | [FinTech Global](https://fintech.global/2025/02/10/fifteenth-raises-8-25m-to-revolutionise-tax-planning-for-tech-professionals-with-ai-driven-workflows/) | Polish IT B2B contractors: ryczałt vs liniowy vs IP Box choice, ESOP/RSU taxation (PIT-38) |
| US-F06 | **Deduction (Taylor, CPAI)** | Consumer AI tax accountant: files returns, organises documents, answers questions year-round | 2.8M USD, 2025-11 (read; round type not stated) | [AlleyWatch](https://www.alleywatch.com/2025/11/deduction-ai-tax-accountant-taylor-cpai-consumer-tax-preparation-filing-automated-sai-dhanak/embed/) | Twój e-PIT already pre-fills simple returns in PL (absorption risk); niche: foreign income, landlords (najem prywatny) |
| US-F07 | **Rillet** | AI-native ERP/general ledger with agents for accruals, reconciliation, reporting | Series A 25M USD (Sequoia), 2025-06; ~200 customers; revenue 5x YoY (read); Series B 70M USD 2025-08 (excerpt) | [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2025/06/02/rillet-raises-25m-series-a-from-sequoia-capital-to-bring-ai-to-mid-market-accounting/162164/) | mid-market close on Polish GAAP (UoR) + KSeF + JPK_CIT; heavy build |
| US-F08 | **Campfire** | AI-native ERP ("modern NetSuite") | ~100M USD across Series A and B in 2025 (excerpt) | [The Next Web (context)](https://thenextweb.com/news/rillet-100m-series-c-1bn-accounting-ai) | as Rillet |
| US-F09 | **Basis** | AI agents doing accounting work for accounting firms | 100M USD at 1.15B USD valuation (single source, unverified) | [CPA Trendlines](https://cpatrendlines.com/2026/08/24/rillets-raise-100-million-bets-on-fewer-accountants/) | agents for biura rachunkowe (księgowanie KSeF invoices, uzgodnienia) |
| US-I01 | **Outmarket** | AI workflow platform for insurance brokerages | Series A 17M USD, 2026-05 (excerpt) | [Axios Pro](https://axios.com/pro/fintech-deals/2026/05/13/outmarket-17-million-ai-insurance-workflows) | multiagencje and brokers: porównania OWU, oferty, IDD documentation |
| US-I02 | **Covu** | AI-native service operations for P&C insurance agencies (offload servicing) | Series A 12.5M USD equity+debt (excerpt; date not shown) | [The Insurer](https://theinsurer.com/?p=43300) | back office for Polish agencies (multiagencje), policy servicing |

**Seen but not catalogued (no checked home page):** Cara (AI platform for brokerages; seed 8M USD, "seven-figure ARR" in ~7 months, 2026-03, [Pulse 2.0](https://pulse2.com/cara-8-million-raised-for-ai-insurance-brokerage-platform), read), Novella (AI-native wholesale broker, 21M USD, 2026-05, [InsuranceNewsNet](https://insurancenewsnet.com/oarticle/ai-powered-wholesale-insurance-broker-novella-announces-21-million-capital-raise-to-expand-across-the-united-states-and-develop-ai-agents-to-create-super-producers), read; licensed broker → L7 knock-out), Fulcrum (25M USD, 2026-01, excerpt), QuoteWell (Cloudflare-blocked site).

**Also in R0 (US finance/insurance), not re-catalogued:** TaxGPT (R0-US-065), Rogo (R0-US-051), Corgi (R0-US-055), Harper (R0-US-080), FurtherAI (R0-US-067), CollectWise (R0-US-082), Bretton AI (R0-US-054), Trellis (R0-US-071).

## Patterns
1. **Tax-firm automation is a crowded 2025–26 US niche** (Filed, Accrual, Accordance, Juno, Magnetic, TaxGPT, Basis, Blue J from Canada). It is driven by the US accountant shortage. Juno shows the best durable shape: per-return pricing (signal 7) and ~500 firms in a year. Poland's analogue is the biura rachunkowe market on KSeF/JPK, where Phase 1 found crowding; the angle there is PIT season document intake, not bookkeeping.
2. **AI-native ERPs** (Rillet, Campfire) are capital-heavy, not founder-fit.
3. **Insurance-agency back office** (Outmarket, Covu, Cara) sells software to brokers without needing a licence; licensed AI brokers (Harper, Novella) fail the founder filter.
4. **Consumer tax** (Deduction, Fifteenth) faces absorption in Poland by Twój e-PIT pre-filled returns; only complex niches (IT contractors' tax-form choice, foreign income) remain.

## Coverage
- Products: 11 new + 8 R0 overlaps; 4 more seen but not catalogued. Sources read: 9 pages; 4 rows rest on excerpts.
- Searches run: 4 (AI tax prep CPA funding; Basis/Rillet/Campfire; AI insurance agency; consumer tax).
- Found nothing: retention/NRR for any of these; Soraban and Magnetic round sizes; checked home pages for Cara, Novella, Fulcrum.
