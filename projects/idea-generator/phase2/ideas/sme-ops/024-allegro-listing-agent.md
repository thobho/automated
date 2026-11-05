# 024 — Allegro listing and Allegro Ads agent for small sellers

**One-liner:** For a small Allegro seller (one person to a few staff, below ~200k PLN monthly turnover), an agent that fixes listings and runs ads: rewrites titles to Allegro search habits, fills missing category parameters (which drive filters and visibility), generates descriptions in Allegro's section format, flags quality-score issues, and runs Allegro Ads sponsored-offer campaigns to a target ROAS within a budget the seller sets; weekly report in plain Polish.
**Field:** sme-ops | **Type:** SaaS (web, Allegro REST API) | **B2B** · shortlist id L142

**Western analogues:**
- **Teikametrics** (US): AI optimisation of Amazon (later Walmart) ads for sellers; US$10M Series A (2018) and US$15M strategic round (2020) ([TechCrunch 2020-02-19](https://techcrunch.com/2020/02/19/teikametrics-funding), accessed 2026-11-06); a 2024 combination with Pacvue is reported by one directory only (unverified). Pre-LLM rules/ML.
- **Perpetua** (CA/US): Amazon ads automation, acquired by Ascential in 2021 (CB Insights excerpt, unverified details).
- **Uplane** (US, YC F25): AI ads and landing pages on Google/Meta, no marketplace ads (TH52 check).
- The marketplace-ads-agent pattern is mature on Amazon (2018–2021 vintage); the LLM-native part (listing copy, parameter filling) is a 2023+ add-on.

**Spread:** TH52 marketing/ad agents: US, FR (Photoroom), HK (Postiz), TR (SEOBOT) and others (R1, R5, R7, R9); marketplace-ads specifically: US/Amazon. Allegro-specific tools are Polish by nature.

**Does the Western leader already work in Poland?** Amazon-ads tools do not support Allegro (different API and ad system). Not tried hands-on. **But Polish players already cover the job:**
- **Senvio.ai** (PL): AI Allegro Ads campaigns to a target ROAS or margin, AI offer selection, "Optymalizacja ofert" (titles, descriptions, parameters, photos), dynamic pricing, competitor monitoring; "2000+ e-commerce firms trusted us"; typical customer from ~200k PLN monthly turnover; price set individually ([senvio.ai](https://senvio.ai/), fetched 2026-11-06). Its Chrome extension for Allegro Ads shows ~572 users ([Chromeboard](https://chromeboard.com/extension/senvioai-allegro-ads-aalppdlhbomgglfdbgnfhpjnnknhiojc), excerpt).
- **Allegro itself:** an AI assistant for sellers in the seller panel since **2026-04-29**, for all sales partners; today it analyses the account quality score and explains what changed it; **offer optimisation and intelligent price management are announced as next** ([Antyweb](https://antyweb.pl/asystent-ai-allegro-dla-sprzedawcow), fetched 2026-11-06). Allegro also runs Allegro GPT inside ChatGPT for buyers ([Bezprawnik](https://bezprawnik.pl/wspolpraca-allegro-z-openai-i-aplikacja-allegro-w-chatgpt/), excerpt).
- **Multichannel tools:** Apilo has a ChatGPT-based description generator for Allegro listings ([Poradnik Przedsiębiorcy](https://poradnikprzedsiebiorcy.pl/-jak-wykorzystac-ai-w-sprzedazy-online-poznaj-generator-opisow-produktow-i-ofert), excerpt); Base (BaseLinker) teaches AI-filled data and names in its Allegro listing course ([Base Akademia](https://base.com/pl-PL/akademia/lessons/wprowadzenie-do-kursu-5/), excerpt).

**Polish adaptation, i.e. the edge:** Allegro REST API and category parameter trees, Allegro's quality score and Super Sprzedawca rules, Allegro Ads (sponsored offers, graphic campaigns), Smart! delivery and InPost/One Box expectations, Polish search phrasing and keyword habits ([local-moats](../../research/poland/local-moats.md) M36, M39). The moat against foreigners is real; against Polish incumbents and Allegro itself it is zero.

**Target customer in Poland:** small Allegro sellers. Allegro's CEO wrote of "almost 150,000 sellers" in the 2023 annual report (search excerpt of the report, [Allegro annual report 2023](https://allegro.gcs-web.com/static-files/c0931d32-63d9-487f-8f24-84741ceb35bb), accessed 2026-11-06); the split by size was not found. The segment below Senvio's typical customer is the target (count unverified). CEE: Allegro runs allegro.cz/.sk (and Mall group); cross-border listing is a possible module (not researched here).

**Demand driver:** DD7 cost of agencies and staff; no demographic or regulatory trigger. Allegro's own push of sellers into Ads (commerce media) raises the need for ad management (Allegro presentation title only, [GrowthLoop webinar](https://www.growthloop.com/resources/webinars/allegro-commerce-media), not read).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Senvio.ai | AI Allegro Ads, offer optimisation, pricing, monitoring | individual (not published) | aimed at ≥200k PLN/month stores |
| Allegro seller AI assistant | quality-score analysis; offer optimisation announced | in seller panel | not yet an ads or listing agent |
| Apilo, Base, Sellasist | multichannel tools with AI descriptions | subscriptions (not checked) | descriptions, not ads |
| Allegro Ads agencies and freelancers | managed campaigns; agencies hire Allegro Ads specialists ([pracuj.pl Senior Allegro Ads Specialist](https://www.pracuj.pl/praca/senior-allegro-ads-specialist-kielce,oferta,1004950628)) | retainers (not checked) | expensive for small sellers |
| ChatGPT | titles and descriptions by copy-paste | free | no API, no parameters, no ads |

**Evidence of Polish demand:** agencies hire dedicated Allegro Ads specialists (pracuj.pl ad above; an agency's Rocketjobs ads for five cities seen in search results on 2026-11-06 had expired when checked), i.e. sellers pay for this job; Senvio claims 2,000+ customers; freelancers post "MVP web app (AI + Allegro API)" jobs on Useme (search result title, not read). Demand exists; the question is whether it is unserved.

**MVP scope (≤6 weeks):**
1. Allegro OAuth app; read listings, categories, parameters, quality data.
2. Listing doctor: missing parameters, title rewrite suggestions, description in Allegro's sections; seller approves, the agent writes via API.
3. Ads autopilot for sponsored offers: daily bid/budget rules toward ROAS, guarded by a margin floor the seller enters.
4. Weekly plain-Polish report; BLIK/VAT invoice billing.
5. Tests: sandbox account (Allegro offers a sandbox environment for developers, not re-checked), fixture listings with golden parameter fills.

**Monetization:** 99 PLN/month up to 200 listings, 199 PLN up to 1,000; ads module +1% of managed ad spend. **Unit economics:** listing rewrite ≈ 3k input / 1k output tokens; 1,000 listings once ≈ 3M / 1M tokens ≈ US$3.4 on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05), then ~10% monthly churn of listings ≈ US$0.35/month; ads decisions are rule-based. Margin >90% before support. **Customer count:** 10k PLN MRR ≈ 67 sellers at 149 PLN average; ~150k sellers is far above 20×.

**Distribution, first 10 customers:** Allegro seller Facebook groups and forums; outbound to small sellers found on Allegro listings (seller pages carry company data); YouTube tutorials on Allegro Ads for beginners.

**Regulation:** AI Act: minimal risk; Art. 50 transparency not triggered for listing text written for the seller ([Annex III](https://artificialintelligenceact.eu/annex/3/) not applicable). Allegro's terms for API apps and marketing content apply; consumer-law accuracy of listings stays with the seller (Omnibus price-display rules: not checked).

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Many of the ~150k sellers are below Senvio's typical size and cannot afford an Ads agency | M | M | ≥30% of surveyed small sellers run Allegro Ads without help |
| O2 | A 99–199 PLN agent replaces an agency retainer or the owner's evenings, a visible spend | M | M | trial sellers report the agency fee they pay |
| O3 | Allegro's CZ/SK sites let small sellers list abroad; parameter mapping and translation is a natural add-on | L | M | ≥10% of users ask for cross-border listing |
| O4 | Allegro's own push into commerce media raises ad spend that someone must manage | M | M | Allegro reports rising Ads revenue share |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Allegro ships offer optimisation and price management inside its free seller assistant, as announced | H | H | the assistant gains listing-edit or ads features |
| R2 | BaseLinker, Apilo and Sellasist already give AI descriptions inside the tools sellers use daily | H | M | trial users already use Base AI fields |
| R3 | Senvio adds a self-serve tier for small sellers | M | M | a published Senvio price list below 200 PLN |
| R4 | Allegro API or Ads API limits, or app review, block or throttle a third-party agent | M | H | API terms change or app approval is delayed |
| R5 | Small sellers have tiny budgets and churn fast | H | M | monthly churn >10% in the first quarter |

O sum 4+4+2+4 = 14; R sum 9+6+4+6+6 = 31. R − O = 17 and R1 is H×H without mitigation → **down one band** (rule §4.3).

**Success signals:**
- Western analogue durable signals: Amazon ads optimisers replace agency fees (signal 1), daily problem with an owner (signal 2), platform API integration (signal 8), price as % of ad spend (signal 7); consolidation by acquisition (Perpetua → Ascential) shows exits exist. No retention data found. Durability score ~3 → **unproven**.
- Hype warnings: crowded TH52 theme, thin LLM wrappers for descriptions.
- Polish adaptation can reproduce: replaced spend = Allegro Ads agency retainer; first channel = seller groups and outbound; retention driver = ads performance history, weak against Allegro's own tools.

**Graveyard:** none found for Allegro tools; on Amazon, the ads-tool market consolidated (Perpetua acquired; Teikametrics–Pacvue combination reported, unverified).

**Scores (1–5):** L1 3 · L2 2 · L3 2 · L4 4 · L5 3 · L6 3 · L7 3 · L8 3 · L9 1 | **Weighted:** 2.8 / 5 (2.75 rounded half-up) | **Chance band:** score → 5–15%; O 14, R 31, unmitigated H×H → **<5%**. Allegro launched a seller AI assistant in April 2026 with offer optimisation and pricing on its roadmap, Senvio already sells AI Allegro Ads and offer optimisation to 2,000+ firms, and multichannel tools generate descriptions; only the very small seller segment remains, with low budgets and full platform risk.
Changes vs. quick score: L3 3 → 2 (Senvio, Allegro assistant, Apilo found), L9 2 → 1 (platform owner shipping); weighted 3.0 → 2.8. Close to collapse; T24 should consider moving it to rejected.md.

**Cheapest validation test (≤1 week, ≤200 PLN):** survey 30 small Allegro sellers in seller groups: do they run Allegro Ads, who manages them, what they pay, and whether they tried Allegro's assistant or Senvio; offer a free listing audit of 20 offers to 10 of them and measure interest in a 99 PLN plan.

**Kill criteria:** Allegro's assistant gains offer editing within 3 months; or <5 of 30 sellers would pay 99 PLN; or Allegro app approval stalls.

**Confidence:** medium (competition and platform moves sourced; seller-size split and API terms not checked).

**Sources** (accessed 2026-11-06 unless noted):
1. https://techcrunch.com/2020/02/19/teikametrics-funding
2. https://senvio.ai/
3. https://chromeboard.com/extension/senvioai-allegro-ads-aalppdlhbomgglfdbgnfhpjnnknhiojc
4. https://antyweb.pl/asystent-ai-allegro-dla-sprzedawcow
5. https://bezprawnik.pl/wspolpraca-allegro-z-openai-i-aplikacja-allegro-w-chatgpt/
6. https://poradnikprzedsiebiorcy.pl/-jak-wykorzystac-ai-w-sprzedazy-online-poznaj-generator-opisow-produktow-i-ofert
7. https://base.com/pl-PL/akademia/lessons/wprowadzenie-do-kursu-5/
8. https://allegro.gcs-web.com/static-files/c0931d32-63d9-487f-8f24-84741ceb35bb (annual report 2023 PDF; 403 to the checker, figure from search excerpt)
9. https://www.growthloop.com/resources/webinars/allegro-commerce-media
10. https://www.pracuj.pl/praca/senior-allegro-ads-specialist-kielce,oferta,1004950628
11. https://openrouter.ai/google/gemini-2.5-flash (accessed 2026-11-05)
12. https://artificialintelligenceact.eu/annex/3/
13. Internal: [TH52 check](../../poland-check/B/TH52-marketing-seo-ad-agents.md)

Coverage: 5 web searches and 2 fetches for this write-up (Allegro seller AI, Allegro Ads tools, Senvio, seller count, Amazon ads analogues). Not found: number of small Allegro sellers, Senvio and Apilo prices, Allegro API terms for AI agents, any Allegro-tool graveyard case.
