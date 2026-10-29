# Lens 9 — Unit economics and defensibility

Research for lens 9 of [BRIEF.md](../../BRIEF.md); scoring anchors in [method/criteria.md](../../method/criteria.md) (L9: margin after infrastructure, LLM and payment costs; churn; switching costs; data/network moat; platform risk). All sources accessed 2026-10-29 (today). IDs `L9-Fnn` are stable anchors. Most pages were read through a summarising fetch tool; several findings rest on search summaries only and say so. Inputs from earlier lenses are referenced, not recounted: Paddle fees [L7-F18](../07-founder-fit/costs-and-ops.md), LLM prices and per-document cost [L7-F26, F27](../07-founder-fit/costs-and-ops.md), marketplace fees [L8-F03–F07](../08-distribution/marketplaces-and-directories.md), Allegro API pain [L6-F10](../06-pain-evidence/ecommerce-and-local-services-pl.md).

**Headline:** 27 findings (F01–F27) in six topic files; Poland, EU, USA/global platforms, one UK/Polish salon case, one German context. Patterns:
1. **Gross margin is not the problem; it is 80–95% for text/data products, even at 49 PLN.** Polish card/BLIK fees are 1.1–1.9% + 0.30–1.00 zł (F01–F03), e-mail is USD 0.10 per 1,000 (F07), a small server is EUR 6–43 a month (F07), an API request costs about USD 1.2 per million (F27), an LLM extraction about USD 0.001–0.02 (L7-F27). The exceptions are **SMS (0.14–0.17 PLN each, F06)**, WhatsApp (moving price, F21), store commissions (15% Apple/Google, F04–F05) and map/geocode calls (F23). My worked table: 78–96% gross margin depending on price and SMS (F08, estimate).
2. **Churn is the real risk at low prices.** Benchmarks for products with under USD 25/month per customer: 6.1% monthly (ChartMogul, F11); "good" SMB 2.5–5% monthly (F10); Baremetrics open startups 11.1% revenue churn (F11). Annual plans cut churn in every source (Buffer 7% → 2.4% a month, F12). At 99 PLN you need ~101 customers for 10,000 PLN MRR and ~5 gross adds a month just to stay level at 5% churn. Higher price and a narrow vertical move retention up (F26).
3. **Lock-in comes from accumulated tax/accounting records and a demand marketplace, not from data hostage-taking.** Accounting software imports contractors and products but not invoices (F15); salon tools export client lists as CSV (F14). The salon incumbents' moat is the consumer marketplace (Booksy: 25% of revenue from commissions, 5% from payments; Fresha PL sells software at PLN 29, F13). The EU Data Act abolishes switching charges for data processing services from 12 Jan 2027, with SaaS scope unverified (F16).
4. **Platform risk is concrete and frequent.** Allegro banned cross-marketplace offer export and keeps withdrawing endpoints (F17); Reddit's API price ended Apollo (F18); Shopify sunsets checkout surfaces on a 2025–2026 timetable (F19); Anthropic retires models with 60 days' notice, six families in 14 months (F20); Meta changed WhatsApp pricing twice (F21); Google re-priced Maps (F23).
5. **The state is a competitor.** Free Ministry of Finance tools (KSeF web/mobile, e-mikrofirma) and free German state validators cap what a compliance tool can charge for the same job (F22).
6. **Founder-level fixed costs sit under any margin.** A JDG at full ZUS pays about PLN 1,927 social + at least PLN 432.54 health contributions a month; ryczałt for software-related services is 12% of revenue (F24–F25, secondary sources).

## Topic files
| File | Findings |
|---|---|
| [costs-and-fees.md](costs-and-fees.md) | F01 Stripe PL, F02 PayU, F03 Przelewy24, F04 Apple 15%, F05 Google Play 15%/30%, F06 SMS cost (SMSAPI), F07 e-mail and hosting, F08 worked margin table |
| [churn.md](churn.md) | F09 Recurly, F10 Lenny/ProfitWell, F11 ChartMogul/Baremetrics/Tunguz, F12 annual vs monthly |
| [switching-and-lockin.md](switching-and-lockin.md) | F13 Booksy/Fresha moat, F14 salon export, F15 wFirma import, F16 EU Data Act Art. 29 |
| [platform-risk.md](platform-risk.md) | F17 Allegro REST API terms, F18 Reddit/Apollo, F19 Shopify checkout sunsets, F20 Anthropic deprecations, F21 WhatsApp pricing, F22 free Ministry tools, F23 Google Maps pricing |
| [poland-cost-basics.md](poland-cost-basics.md) | F24 ZUS 2026, F25 ryczałt 12% |
| [retention-and-api-costs.md](retention-and-api-costs.md) | F26 retention vs ACV, F27 Lambda/API Gateway cost |

## Unit-economics readings of recurring themes (my judgement, not scores)
Indicative L9 cap per theme (rubric: 5 = margin above 80%, sticky usage, no single platform able to cut off; 1 = margin below 50%, high churn or one platform can kill it). T12 must score concrete ideas.

| Theme | Margin | Churn / stickiness | Platform risk | Indicative L9 | Findings |
|---|---|---|---|---|---|
| KSeF / accounting-office tools (multi-client, archive) | 90%+ (document-level LLM ~USD 0.001–0.02) | Offices keep tools that hold a year of records; low-price tier worse | Low API risk but the state ships free tools and changes the API | 3–4 | F08, F15, F22, L7-F27 |
| KSeF receive-side tools for micro-firms (29–49 PLN) | 90%+ | 4–6% monthly at this price (estimate from F10–F11); free state app caps price | State app and rate limits | 2–3 | F10, F11, F22 |
| Allegro / BaseLinker seller tools | 90%+ | Medium; sellers use tools daily | **High**: Allegro terms and endpoints change, certified-integrator rivals own the channel | 2 | F17, L8-F02 |
| Shopify apps | 90% minus 0% (to USD 1M) revenue share | Merchant churn tracks store churn (not measured) | Medium: yearly breaking changes, review queue | 3 | F19, L8-F03 |
| Salon / local booking | **50–80%** if SMS included, 90% without | Switching = CSV; incumbents give software away | Medium: SMS/WhatsApp prices | 2 | F06, F13, F14, F21 |
| DE E-Rechnung tools | 90%+, but Peppol/AP costs unmeasured | Weak lock-in; Data Act pushes portability | Free validators; DATEV gate (L8-F06) | 2–3 | F16, F22 |
| NIS2 / CRA compliance documents | 90%+ | Annual cycle suits annual plans; no churn data found | Low platform risk | 3–4 (unverified) | F12, F26 |
| Dev tools / APIs / libraries | 95%+ (F27) | Dev-tool churn not found; libraries lower barriers (L7-F21) | Model deprecation and API terms | 3 | F20, F27 |
| Consumer / mobile apps | 70–85% after 15% store cut | Highest churn bracket (cheapest ARPC) | Store rules | 2 | F04, F05, F09 |

## Seeds
Idea sketches inspired by findings; none validated. Each states the economic argument only; competition, demand and feasibility come from other lenses.
1. **Annual-first KSeF archive and multi-client dashboard for accounting offices at 150–500 PLN/month per office.** Higher ACV band, annual billing, data accumulates with a year of invoices; margin 90%+. [L9-F11](churn.md), [L9-F12](churn.md), [L9-F15](switching-and-lockin.md), [L9-F26](retention-and-api-costs.md).
2. **Pass-through-priced booking add-on for salons (reminders and no-show deposits), billed at cost + margin for SMS/WhatsApp.** Avoids the SMS trap: charge per sent message or require the customer's own SMSAPI/WhatsApp key. [L9-F06](costs-and-fees.md), [L9-F21](platform-risk.md), [L9-F13](switching-and-lockin.md).
3. **CSV/API importer for "leaving Booksy/Versum/Fresha".** Owns the migration moment; lowers acquisition friction in a segment that complains about forced migration and commissions. Not a moat on its own (rivals can import). [L9-F14](switching-and-lockin.md), [L6-F09](../06-pain-evidence/ecommerce-and-local-services-pl.md).
4. **Invoice-history migrator between Polish accounting tools** (iFirma / inFakt / wFirma / Fakturownia → each other), since wFirma's import excludes invoices. Sold per migration (one-off) or to accounting offices onboarding new clients. [L9-F15](switching-and-lockin.md). One-off revenue: weak MRR, flag for T11.
5. **Allegro tool built only on the seller's own OAuth key, scoped to the seller's own Allegro sales** (stock, shipping, documents), avoiding the banned use cases (competitor sync, shared keys). [L9-F17](platform-risk.md), [L6-F10](../06-pain-evidence/ecommerce-and-local-services-pl.md).
6. **Model-agnostic extraction API with a published regression set** (invoice / receipt / contract fields), switchable across LLM suppliers when a model retires. Sells reliability, not the model. [L9-F20](platform-risk.md), [L7-F27](../07-founder-fit/costs-and-ops.md).
7. **Annual-plan pricing test as part of every validation plan:** offer 2 months free for annual on the landing page, measure the share choosing annual. Cheap, directly tied to the churn evidence. [L9-F12](churn.md), [L9-F01](costs-and-fees.md).
8. **Gap-filler for what the Ministry will not build:** per-client notifications, bank matching and reminders around the free KSeF app, designed to coexist with it. [L9-F22](platform-risk.md), [L2-F12](../02-weak-competition/reviews-and-app-stores.md).
9. **Cost-guard design rule for LLM features:** hard per-customer call budget, Haiku-class model by default, escalation only on low confidence; prevents agent loops from breaking margin. [L9-F08](costs-and-fees.md), [L7-F26](../07-founder-fit/costs-and-ops.md).

## Coverage
- **Sources:** about 36 page fetches attempted, about 31 returned content (Stripe PL, PayU PL, Przelewy24 offer, Apple, Google Play, SMSAPI, AWS SES / Lambda / API Gateway, Hetzner, Recurly, Lenny's Newsletter, Point Nine, Baremetrics, ChartMogul, SaaS Capital, wFirma help, Prighter (Data Act), Allegro community thread and developer news, Betakit, Shopify.dev, Anthropic docs, Meta developer docs, Wikipedia (Booksy), Fresha pricing). Failed: Przelewy24 `/cennik` (404), Apple `apple.com` URL (404), Shopify deprecation pages (404 x2), Allegro news post (404), Bookedin help (403), SAP partner page (403), SaaS Capital PDF (binary, not extractable here). About 20 more pages appeared only as search summaries and are marked as such.
- **Countries:** Poland (fees, ZUS, ryczałt, Allegro, KSeF tools, salons), EU (Data Act), Germany (Peppol/E-Rechnung context only, no German-language source read), USA/global (Recurly, ChartMogul, Reddit, Shopify, AWS, Meta), UK/Poland (Fresha). Czechia, Netherlands, Nordics, Brazil, India, Japan: not covered.
- **Searches:** 21 web searches (roughly 15 English, 6 Polish; zero in German or other languages): payment fees, SMB churn, Recurly, ChartMogul, annual vs monthly churn, Versum/Booksy migration (2), Allegro API terms (2), Data Act, wFirma import, salon switching, Twitter/Reddit API, Shopify checkout, e-mikrofirma, ryczałt IT, ZUS 2026, Google Maps pricing, Fresha, vertical SaaS retention, Peppol pricing.
- **Searched, nothing usable:** a Versum → Booksy official migration guide or Versum shutdown notice; Polish or German SMB SaaS churn studies; Treatwell export; iFirma export documentation; Peppol small-business price lists (only a EUR 2,000 setup + EUR 200/month ERP-partner offer via snippet, not fetched); ChartMogul 2025 retention report; ProfitWell "941 businesses" study on the Baremetrics page it was attributed to; Przelewy24 fee PDF; official Allegro news post on the 23 Sep 2025 terms.
- **Reliability notes:** no web page contained text addressed to AI assistants. Pages with promotional intent (competitor migration guides, vendor churn blogs) are marked.

## Gaps
1. **No Polish or DACH churn data** for SMB SaaS; all benchmarks are US/global billing networks. Look for: public Polish SaaS statements (inFakt, Fakturownia, Booksy investor decks), founder posts on churn; ask accounting offices in validation interviews.
2. **Recurly page is internally inconsistent** (annual vs monthly labels, 3.04% vs 3.22%); ChartMogul figure is from 2022; Point Nine's tables are images. Pull the original PDFs (SaaS Capital 2025 brief, ChartMogul reports) and read the charts.
3. **Allegro REST API terms text (art. 3.11) and penalties** were not read; only a moderator's summary. Look at developer.allegro.pl "Regulamin REST API" and the 23 Sep 2025 news post.
4. **Booksy / iFirma / inFakt current prices and export features** were not read from primary pages (lens 2 used secondary prices). Read Booksy's help centre for client export and Versum import.
5. **Data Act scope for small SaaS** (Art. 2(8) "data processing service") and Digital Omnibus changes: read EUR-Lex 2023/2854 Article 2 and the omnibus status.
6. **SMS vs WhatsApp unit cost in zloty** for Poland: Meta rate card (Poland market, from 1 Jul 2026) not read; compare with SMSAPI, Fresha's PLN 0.10 SMS.
7. **Peppol access-point price per invoice and German E-Rechnung provider pricing**: only one unverified snippet; read B2Brouter, Storecove, Pagero price pages.
8. **ZUS and ryczałt figures** are from secondary pages; confirm on zus.pl and podatki.gov.pl, and check how subscription SaaS is classified for ryczałt (needs an accountant).
9. **Apple standard commission (30%) and Google Play fees for EEA/Poland** not read from primary pages.
10. **Moat evidence is thin:** I found no source measuring data or network effects for a micro-SaaS; the Booksy marketplace commission share is the only quantified moat, and it is Wikipedia-sourced. Look for: marketplaces' take rates in small niches, accounting-office referral programmes (lens 8), and cohorts from TrustMRR (lens 4).
11. **Shopify Scripts sunset (30 Jun 2026?)**, Twitter/X API history, and Chrome extension policy changes were not verified on primary pages.
