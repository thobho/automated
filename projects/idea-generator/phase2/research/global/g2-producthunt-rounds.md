# G2 fastest-growing, Product Hunt, and notable Series A/B rounds (T04)

Source family: buyer-adoption rankings (G2), launch platforms (Product Hunt) and European applied-AI rounds. All sources accessed **2026-11-01**. Catalogue rows: `R0-DE-097` … `R0-US-104` in [../../catalogue/R0-global.csv](../../catalogue/R0-global.csv).

**Choices**
- **G2 Best Software Awards 2026, Fastest-Growing Products** (published 2026-02-18): the [list page](https://www.g2.com/best-software-companies/fastest-growing) blocks bots; the [announcement](https://company.g2.com/news/g2s-2026-best-software-awards) names only the top five: 1 TradeInt, 2 n8n, 3 Retell AI, 4 Synthflow, 5 Handoff. 86 of the top 100 are new for 2026. Retell AI is catalogued in the YC file (`R0-US-060`). TradeInt was not catalogued: what it does could not be verified.
- **Product Hunt**: Product Hunt sunset the Golden Kitty Awards and replaced them with quarterly "Orbit Awards" covering vibe-coding tools, AI automation builders, AI meeting note-takers and coding agents ([Product Hunt post](https://www.producthunt.com/p/producthunt/rip-golden-kitty-awards-long-live-orbit-awards)). Leaderboards and category pages block bots and no Orbit winner list was found. Per the brief, launch votes are a hype signal, not traction; no row is catalogued on Product Hunt evidence alone. The categories Orbit names are already represented (Lovable, Replit, Gumloop, n8n, Granola, Cursor, Cognition).
- **European rounds**: the [tech.eu funding tracker, AI Q1 2026](https://funding.tech.eu/sectors/ai/2026/q1) (63 deals, €2.8B; top 15 visible) plus targeted searches. Rows added only where the product was verified on its own site.

## Findings

| # | Finding | Source |
|---|---|---|
| G-G01 | Three of G2's five fastest-growing products in 2026 are **voice agents or agent builders** (Retell AI, Synthflow, n8n), measured by buyer reviews, not funding. | [G2 2026 awards](https://company.g2.com/news/g2s-2026-best-software-awards) |
| G-G02 | **Handoff** (AI estimating for residential remodelers) is G2 #5; the company says 40K+ contractors have used it; strategic round from Nemetschek and Masco (2025-06). A trade-specific estimating tool built on US cost data beats horizontal tools on G2 momentum. | [G2](https://company.g2.com/news/g2s-2026-best-software-awards), [Handoff blog](https://handoff.ai/blog/handoff-raises-5-8m-for-residential-construction) |
| G-G03 | **Voice agents are Europe's largest applied-AI rounds**: Parloa (Berlin) 350M USD Series D at 3B (2026-01), revenue ~50M USD per a third-party estimate (60× multiple); Synthflow (Berlin) 20M Series A (2025-06); Elyos AI (London; trades front office) 13M Series A (2026-01). ElevenLabs raised €423M in Q1 2026. | [Parloa](https://www.parloa.com/parloa-in-the-press/parloa-valued-at-3-billion-with-350m-series-d/), [Verdict](https://www.verdict.co.uk/synthflow-ai-raises-20m-to-expand-voice-ai-platform/), [Pulse 2.0](https://pulse2.com/elyos-ai-13-million-series-a/), [tech.eu tracker](https://funding.tech.eu/sectors/ai/2026/q1) |
| G-G04 | **Regulated customer operations in finance** attract European Series A money: Gradient Labs (London) 13M USD extension (2026-06); investors back agents "in high-friction, regulated environments" (roundup view). | [Axios](https://www.axios.com/pro/fintech-deals/2026/06/01/gradient-labs-ai-agents-series-a) |
| G-G05 | European AI funding is lumpy: Q1 2026 €2.8B across 63 companies; June 2026 €506M across 27 (−43.6% YoY); July €1.8B across 31 rounds. | [tech.eu Q1](https://funding.tech.eu/sectors/ai/2026/q1) (June/July via search summary of tech.eu monthly pages) |
| G-G06 | **Valuation-to-revenue gap as a hype marker**: Parloa at ~60× estimated revenue; Higgsfield burning ~4M USD/month (see a16z file). | [Parloa](https://www.parloa.com/parloa-in-the-press/parloa-valued-at-3-billion-with-350m-series-d/) |

**Poland relevance.** Trade-specific tools (Handoff for remodelers, Elyos for trades) translate directly: Polish remodelling estimates run on KNR norms and Sekocenbud prices, and Polish trades lose jobs to missed calls; both are SME markets with no LLM-native local tool found so far (to check in T16–T18). Voice-agent platforms (Parloa, Synthflow, Retell) are horizontal; the Polish gap is vertical workflows on top of them, not the voice layer.

**Not catalogued (product unverified in time box):** TradeInt (G2 #1), Wonderful (€131M Series B, Mar 2026; listed only as a Parloa competitor), Andercore (€34M Series B), Plato (€12M seed), Orbio (Madrid, 21M USD Series A, AI agents for hiring and onboarding).

## Coverage
- Sources read: G2 awards announcement; Product Hunt Orbit post (via search); tech.eu Q1 2026 AI tracker; 6 company/press pages. 8 catalogue rows.
- Countries: Germany 3, United Kingdom 2, United States 3.
- Searches run: 6.
- Searched and found nothing: Product Hunt Orbit Awards winners; Golden Kitty 2025 winners (discontinued); TradeInt product; n8n funding/ARR; Wonderful product page.

## Gaps
- G2 ranks 6–100 not visible (bot-blocked); a browser session would add ~95 products with buyer-review momentum.
- Product Hunt top AI launches by year not compiled (bot-blocked leaderboards; awards discontinued).
- tech.eu monthly trackers list only top 15 deals per page without country or product.
