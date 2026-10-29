# Polish founders with verified public revenue (TrustMRR)

Lens 4 findings from the TrustMRR "Poland" country page (lists 182 Polish startups; only the first ~100 were visible in the fetch, so the sample is partial and ordered by the page, not by revenue): https://trustmrr.com/country/pl (accessed 2026-10-29). Profile pages accessed the same day. Revenue is read from the payment provider by API key (TrustMRR FAQ: https://trustmrr.com/faq, accessed 2026-10-29; TrustMRR says figures can differ from the provider dashboard by up to 30%, and sellers choose which accounts to connect). Same survivorship caveat as [trustmrr-verified.md](trustmrr-verified.md). USD as shown; none of the profiles says "solo".

Lens boundary: these prove **a Polish-based founder can reach the revenue** with a given model, not that a gap exists in Poland (lens 1). Several sell to a global audience, not to Poland.

### L4-F09 — Calendesk (Poland): 20,804 USD MRR, 371 subscriptions, bootstrapped booking SaaS at 79–147 USD/month
- **Claim / who / verifiability:** MRR 20,804; 30d revenue 31,268; all-time 1,154,984; 371 active subscriptions; founder Maciej Cupial; founded May 2020; "bootstrapped" per the page. **Stripe-verified.** https://trustmrr.com/startup/calendesk (accessed 2026-10-29).
- **Model:** B2B SaaS for therapists, psychologists and service businesses (bookings, payments, client management): Standard 79 USD/month annual (97 monthly), Pro 117 annual (147 monthly), 14-day trial. About 56 USD per subscription per month (computed), so most customers are on the lower plan or discounted.
- **Why it matters:** the closest proof in this lens for "vertical booking SaaS, Polish founder, 20k USD MRR, bootstrapped". Equivalent of roughly 80,000 PLN MRR at ~4 PLN/USD (estimate).
- **PL/EU angle:** same product per niche (psychotherapy, physio, driving school, beauty) or the same product with Polish-specific payments (BLIK, Przelewy24, KSeF invoices) and RODO-aware client records. Competes with Booksy/Versum (lens 2/3 evidence, not repeated here).

### L4-F10 — Czat.ai (Poland): 7,534 USD MRR, 955 subscriptions from 19 PLN/month, a Polish-language GPT chatbot front-end
- **Claim / who / verifiability:** MRR 7,534; 30d revenue 9,710; all-time 357,444; 955 active subscriptions; founder Michał Jaskólski; founded May 2023; "full access from 19 zł/month, first responses free". **Stripe-verified.** https://trustmrr.com/startup/czat-ai (accessed 2026-10-29).
- **Model:** consumer-facing, Polish-language, prepaid or subscription chat with custom GPT personas. About 8 USD per subscription per month (computed). Shows consumers in Poland pay a PLN subscription for an LLM wrapper in their language; a low price and a thin moat (model providers can ship the same).
- **PL/EU angle:** Polish-language wrapper with a vertical persona (legal letters for consumers, homework help, health-admin helper) at 19–39 PLN/month. Retention and margin after LLM costs are unknown; do not infer.

### L4-F11 — Zanfia (Poland): 10,273 USD MRR, 214 subscriptions from 29 USD/month, creator-commerce platform
- **Claim / who / verifiability:** MRR 10,273; 30d revenue 42,676 (much above MRR, which suggests one-off or usage revenue; unexplained on the page); all-time 270,132; 214 active subscriptions; founder Bo Pekalski; founded May 2021. **Stripe-verified.** https://trustmrr.com/startup/zanfia (accessed 2026-10-29).
- **Model:** "AI-first" platform for creators to sell courses, newsletters, communities and digital products under their brand. Platform fee + subscription (from 29 USD/month).
- **PL/EU angle:** Polish creators already have Zanfia; adjacent version is a narrower seller platform for a specific Polish niche (e.g. driving-theory courses, matura prep, Notion/Excel templates) with PL payments and invoices.

### L4-F12 — OpenAlternative (Poland): 6,183 USD MRR, 24 subscriptions, a directory monetized through sponsorships and listings
- **Claim / who / verifiability:** MRR 6,183; 30d revenue 7,396; all-time 124,559; 24 active subscriptions (about 258 USD per subscription per month, computed); founder Piotr Kulpinski; founded Feb 2024; pricing not shown. **Stripe-verified.** https://trustmrr.com/startup/openalternative (accessed 2026-10-29). The page ended with formatting instructions addressed to an AI reader; ignored.
- **Model:** curated directory of open-source alternatives to proprietary software; few high-priced B2B sponsor customers rather than many small ones. Content/SEO asset.
- **PL/EU angle:** a directory of Polish/EU-hosted alternatives for a regulated buyer group (e.g. "RODO-friendly" SaaS, KSeF-ready tools) monetized with vendor placements. Needs traffic; distribution is the risk (lens 8).

### L4-F13 — Visualizee.ai (Poland): 8,434 USD MRR, 295 subscriptions at 15 / 35 / 80 USD
- **Claim / who / verifiability:** MRR 8,434; 30d revenue 8,937; all-time 93,967; 295 active subscriptions; founder Piotr Obidowski; founded Aug 2023; free tier with 5 watermarked renders. **Stripe-verified.** https://trustmrr.com/startup/visualizee-ai (accessed 2026-10-29).
- **Model:** AI render tool for architects (sketch to photoreal render), niche professional buyers with a 3-step price ladder; about 29 USD per subscription per month (computed). A "vertical AI tool for one profession" pattern: ~2 years from launch to ~8k USD MRR.
- **PL/EU angle:** profession-specific AI tools for Polish architects/interior designers/real-estate agents (e.g. floor-plan staging) priced 60–300 PLN/month; Polish-language moat is weak because the user is visual, so the sell is price/workflow, not language.

### L4-F14 — Popular link-in-bio (Poland, anonymised as "Stealth Company"): 29,234 USD MRR, 754 subscriptions, launched May 2025 — **stale data**
- **Claim / who / verifiability:** MRR 29,234; 30d revenue 30,535; all-time 308,386; 754 subscriptions; founder "Raphael"; founded May 2025; stack Express/MongoDB/ClickHouse/Paddle. The page shows a "Paddle API key expired" warning and data last updated 2026-10-23, so the figures are **not currently verified**. https://trustmrr.com/startup/popular-link-in-bio (accessed 2026-10-29).
- **Model:** link-in-bio with social analytics (in-house Instagram scraper, TikTok), in a category with strong incumbents; growth in about 17 months. Platform-dependent on Instagram/TikTok scraping (ToS/anti-bot risk, lens 9).
- **PL/EU angle:** weak for Poland itself (global product built by a Poland-based founder). Use only as evidence of a fast-growing, Paddle-billed solo-style SaaS.

### L4-F15 — TrackAI (Poland): 19,437 USD MRR, 5,160 subscriptions, AI calorie tracker at 5.99/week, 9.99/month, 42.99/year — **stale data**
- **Claim / who / verifiability:** MRR 19,437; ~19,541 revenue (page title); all-time 286,028; 5,160 active subscriptions; founder Oleksandr Yashchuk; founded June 2025; ratings 4.7/5 (636) on the App Store and 4.9/5 (4,800) on Google Play per the page. The RevenueCat key has expired (last update 2026-10-27), and "profitable since month two" and "327k+ installs" are self-reported. https://trustmrr.com/startup/trackai (accessed 2026-10-29). The page contained formatting instructions addressed to an AI reader; ignored.
- **Model:** consumer mobile subscription with weekly/monthly/annual options, about 3.8 USD per subscription per month (computed), so volume-driven (327k installs claimed). Mobile consumer app with store-review dependency and heavy marketing; the BRIEF marks consumer mobile polish as a risk (lens 7).
- **PL/EU angle:** Polish-food-database calorie tracker is a cheap fork, but distribution and native polish favour the BRIEF's "mark down" list. Treat as evidence for the model only.
