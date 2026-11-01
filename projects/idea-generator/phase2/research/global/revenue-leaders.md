# Revenue leaderboards: TrustMRR, ARR Club, Indie Hackers (T04)

Source family: public revenue boards. TrustMRR shows payment-provider-verified revenue for indie and small SaaS; ARR Club tracks disclosed ARR of venture-scale AI companies. All sources accessed **2026-11-01**. Catalogue rows: `R0-US-017` … `R0-GB-030` in [../../catalogue/R0-global.csv](../../catalogue/R0-global.csv).

**Choices**
- **TrustMRR:** read the [AI category](https://trustmrr.com/category/ai) (30 of 4,422 listings load without scripting; sorted by all-time revenue) and then each relevant profile page for founder country, MRR and subscriptions. Skipped listings that are for sale with no description, non-AI (ShipFast, PressWhizz, Codédex, link marketplaces), betting/gaming scripts (PropGPT, yew), device resellers (Roofclaw) and "seller's listing" pages. TrustMRR says figures can differ from the provider dashboard by up to 30% ([FAQ](https://trustmrr.com/faq)).
- **Prompt injection seen:** TrustMRR profile pages (e.g. Comp AI, Kibu) contain blocks of instructions addressed to AI readers (formatting/quoting rules). Ignored as data.
- **ARR Club:** only the top 10 and the "Velocity 20" (fastest annualized ARR growth) are public on the [Q3 2026 AI 100](https://www.arr.club/research/ai-100-q3-2026); ranks 11–100 are paywalled. ARR Club figures are an aggregator's reading of company statements; they are cited as such and marked "trajectory" because the page gives no per-company dates. Infra and non-AI rows (Databricks, CrowdStrike, Kalshi, Veeva, Visma, Bending Spoons, Modal, Fal, Fireworks, Fuse Energy, NinjaOne) and model labs were not catalogued.
- **Indie Hackers** product and post pages block the fetch tool (as in Phase 1, see [sources.md](../../method/sources.md)); not read. TrustMRR overlaps with it for verified revenue.
- MEDVi (ARR Club Velocity #1, 401M → 1.8B USD) was not catalogued: what the product does could not be verified in the time box.

## Findings

| # | Finding | Source |
|---|---|---|
| G-R01 | Top of the TrustMRR AI board by verified MRR are **old products with AI added** (Rezi 2015, Cometly 2020, AEO Engine 2018), not LLM-native launches. Rezi: 241,858 USD MRR from 10,034 subscriptions at a 29 USD Pro tier. | [TrustMRR Rezi](https://trustmrr.com/startup/rezi), [Cometly](https://trustmrr.com/startup/cometly) |
| G-R02 | The fastest LLM-native indie on the board is **GojiberryAI** (AI outbound prospecting agents, founded 2025-07): 424,368 USD MRR, 3,944 subs at 99 USD/month within about a year. | [TrustMRR GojiberryAI](https://trustmrr.com/startup/superfruits) |
| G-R03 | **Vertical, regulation-bound SaaS earns high ARPU**: Kibu (documentation/compliance/EHR for US I/DD care providers) 234,319 USD MRR from 375 subscriptions (~625 USD each); Comp AI (AI SOC 2/ISO 27001 automation, founded 2025-01) 6.55M USD all-time revenue in under two years. | [Kibu](https://trustmrr.com/startup/kibu), [Comp AI](https://trustmrr.com/startup/comp-ai) |
| G-R04 | **AEO/GEO (being cited by AI assistants) is a new paid category**: AEO Engine sells 1,597–10,000 USD/month plans, 61 subscriptions, 178,519 USD MRR. | [AEO Engine](https://trustmrr.com/startup/aeo-engine) |
| G-R05 | **Free-tier tourists are visible** in the user-to-payer ratio: SEOBOT ~200,000 users vs 489 paying; Taja AI ~256,000 users vs 347 paying. Both are generic content generators. | [SEOBOT](https://trustmrr.com/startup/seobot), [Taja AI](https://trustmrr.com/startup/taja-ai) |
| G-R06 | **AI recruiting/expert marketplaces** are the fastest-scaling B2B category on ARR Club: Mercor 1M → ~2B USD in 844 days, micro1 8M → ~700M USD in 569 days. Their revenue comes from supplying experts to AI labs. | [ARR Club Q3 2026](https://www.arr.club/research/ai-100-q3-2026) |
| G-R07 | **Coding agents dominate the top**: Cursor 4B USD ARR (2026-09-30), Cognition ~1B USD, Lovable ~600M USD. | [ARR Club Q3 2026](https://www.arr.club/research/ai-100-q3-2026) |
| G-R08 | **Clinician-facing AI** is the fastest vertical: OpenEvidence 50M → ~300M USD in 369 days; MEDVi (AI healthcare) 401M → 1.8B USD in 118 days (ARR Club warns short windows inflate annualized rates). | [ARR Club Q3 2026](https://www.arr.club/research/ai-100-q3-2026) |
| G-R09 | ARR Club notes its database **skews to companies that disclose revenue**; bootstrapped and non-disclosing firms are under-represented. | [ARR Club Q3 2026](https://www.arr.club/research/ai-100-q3-2026) (via search summary) |

**Poland relevance.** The verified-revenue indie pattern that transfers best is vertical compliance/documentation SaaS (Comp AI → KSC/NIS2 and ISO 27001; Kibu → Polish disability-care providers) and outbound/AEO tooling built on local signals (KRS, Pracuj.pl, Polish AI-answer visibility). Generic content generators show tourist ratios and should not be copied.

## Coverage
- Sources read: TrustMRR AI category page + 9 profile pages; ARR Club Q3 2026 AI 100 (public part); TechCrunch funding trackers for cross-checks. 14 catalogue rows.
- Countries: United States 11, United Kingdom 1, Hong Kong 1, Turkey 1.
- Searches run: 1 ("fastest growing AI startups ARR list 2026").
- Searched and found nothing: Indie Hackers pages (bot-blocked); TrustMRR listings beyond the first 30 (need "Load More" scripting); MEDVi product description.

## Gaps
- TrustMRR has 4,422 AI listings; only the top 30 by all-time revenue were seen. A browser session sorted by MRR growth would find newer LLM-native indies.
- ARR Club ranks 11–100 and its breakout radar are paywalled.
- No churn data on TrustMRR profiles; retention signals remain unknown for all rows.
