# Lens 2 — Weak or no competition

Research for lens 2 of [BRIEF.md](../../BRIEF.md); scoring anchors in [method/criteria.md](../../method/criteria.md). All sources accessed 2026-10-29. Findings are in the topic files; IDs `L2-Fnn` are stable anchors.

**Headline:** 22 findings (F01–F22). **The honest result is that most Polish SMB software categories are not empty.** Allegro integrators, invoicing/KSeF, courier plugins, payments and mileage logs all have several working products, and several "gap" hypotheses were refuted (marked *counter-finding*). The real signals found are narrower: (1) price and support complaints against incumbents (Base/BaseLinker per-order pricing, iFirma 2.8 on Trustpilot, Booksy fees and billing complaints, the official KSeF app at 2.9 / 2.0 stars); (2) **developer-side gaps** — stale or missing Node/TypeScript clients for the Allegro API, InPost ShipX, CEIDG/KRS and Przelewy24, which fit the founder profile; (3) thin niches inside WooCommerce. No finding reached the criteria's L2 = 5 bar (incumbents ≤3★ with repeated quoted complaints about the exact job, plus unanswered requests); the strongest candidates reach L2 ≈ 3 and need follow-up.

## Topic files
| File | Findings |
|---|---|
| [allegro-and-ecommerce-tools.md](allegro-and-ecommerce-tools.md) | F01 BaseLinker price hike, F02 Base pricing, F03 Apilo, F04 WooCommerce–Allegro plugins, F05 Booksy fees, F06 KSeF WooCommerce plugins, F22 price monitoring |
| [dev-tools-and-polish-apis.md](dev-tools-and-polish-apis.md) | F07 Allegro API clients, F08 InPost SDKs, F09 CEIDG/KRS/REGON clients, F10 KSeF libraries (counter-finding), F11 Przelewy24 SDKs |
| [reviews-and-app-stores.md](reviews-and-app-stores.md) | F12 official KSeF app, F13 iFirma vs inFakt, F14 Fakturownia, F15 Booksy Trustpilot, F16 InPost shippers, F17 Vimcar, F18 Play Store scheduling/clinic apps, F19 WISO MeinVerein (unverified) |
| [woocommerce-pl-and-estimating.md](woocommerce-pl-and-estimating.md) | F20 WooCommerce PL plugins, F21 construction estimating |

## Strength at a glance
| Verdict | Findings |
|---|---|
| Documented complaint or price gap (candidate L2 ≈ 3) | F01, F02, F12, F15, F13 (iFirma only) |
| Developer-library gap (stale or missing) | F07, F08, F09, F11 |
| Thin or weak evidence (small n, ratings only, search summary) | F04, F14, F16, F18, F19, F20, F21, F22 |
| Counter-findings: well covered, not a gap | F03 (partly), F10, F13 (inFakt 4.8), F17 (DE), F20 (couriers/payments) |
| Context for other findings | F05, F06 |

## Seeds
Idea sketches for the longlist (T11). None is validated; each links to its finding. Several overlap with lens-1 seeds and must not be double-counted.

1. **Light Allegro/Woo/Shoper order hub for 500–5,000 orders/month with flat pricing, stock sync and a basic pick-and-pack screen.** Forum posters named exactly that mix as hard to find after the Base price rise. [L2-F01](allegro-and-ecommerce-tools.md#l2-f01--baselinker-price-hike-pushed-allegro-sellers-to-look-for-alternatives), [L2-F02](allegro-and-ecommerce-tools.md#l2-f02--base-baselinker-pricing-page-business-plan-per-order-fee-enterprise-above-5000-orders), [L2-F03](allegro-and-ecommerce-tools.md#l2-f03--apilo-flat-plans-but-erpstock-sync-extras-priced-separately-support-called-slow). Crowded (8+ alternatives) and integration-heavy; low founder-fit unless a clear wedge is found.
2. **Maintained TypeScript/Python SDK plus MCP server for the Allegro REST API** (typed, OAuth handled, rate limits, webhooks). [L2-F07](dev-tools-and-polish-apis.md#l2-f07--allegro-rest-api-clients-few-libraries-most-unmaintained). Who pays is unclear (agencies, in-house devs); pair with a hosted add-on.
3. **InPost ShipX client + tracking/webhook relay for Node/Python shops.** [L2-F08](dev-tools-and-polish-apis.md#l2-f08--inpost-shipx-api-sdks-are-php-centric-and-mostly-stale). Same payer question as seed 2.
4. **Polish company-data API (NIP/KRS/REGON → one clean JSON, cached, with change alerts)** for CRMs and onboarding forms. [L2-F09](dev-tools-and-polish-apis.md#l2-f09--ceidg-and-krs-company-data-api-clients-small-old-some-are-scrapers). Official feeds are free; the product is convenience and uptime. Check paid aggregators first.
5. **KSeF companion for people who send or receive a few invoices** (foreign-currency invoices, push notifications, simple login), aimed at JDG and micro firms. [L2-F12](reviews-and-app-stores.md#l2-f12--official-ksef-mobile-app-ministry-of-finance-29-on-google-play-20-on-the-app-store). The ministry may fix its own app; a native-mobile polish dependency lowers founder fit.
6. **Flat-fee booking page for salons and independent practitioners, no first-visit commission, Polish invoices.** [L2-F05](allegro-and-ecommerce-tools.md#l2-f05--booksy-145-złmonth-plus-45-first-visit-commission-a-recurring-salon-pain), [L2-F15](reviews-and-app-stores.md#l2-f15--booksy-29-on-trustpilot-16585-reviews-billing-and-cancellation-complaints). Competitors (Versum, Koalendar, Anolla) not assessed.
7. **Carrier-claim tracker for e-commerce sellers** (detect damaged/lost parcels across InPost/DPD/DHL, prepare reklamacja, follow up). [L2-F16](reviews-and-app-stores.md#l2-f16--inpost-42-overall-but-business-shippers-complain-about-claims-and-support). No existing product searched for; validate demand first.
8. **Reliable WooCommerce→invoice/KSeF bridge plus Ceneo/marketplace feed pack** for small Polish shops. [L2-F14](reviews-and-app-stores.md#l2-f14--fakturownia-woocommerce-connection-failures-cited-very-small-sample), [L2-F06](allegro-and-ecommerce-tools.md#l2-f06--ksef-add-ons-for-woocommerce-a-market-that-is-only-now-forming), [L2-F20](woocommerce-pl-and-estimating.md#l2-f20--polish-woocommerce-plugins-couriers-and-payments-are-covered-compliance-and-ceneo-are-thin). Evidence is thin (n=3 reviews).
9. **Quote (oferta) generator for small renovation crews** with Polish unit catalogue, PDF and invoice handoff. [L2-F21](woocommerce-pl-and-estimating.md#l2-f21--construction-estimating-kosztorysowanie-legacy-desktop-tools-and-training-courses-dominate). Overlaps lens-1 seed 9; no pain quotes yet.
10. **Affordable price-monitoring add-on for small Allegro sellers** (under $99/month, PLN billing, Allegro-only). [L2-F22](allegro-and-ecommerce-tools.md#l2-f22--competitor-price-monitoring-for-allegro-priced-in-usd-from-99-forum-asks-go-unanswered). Demand uncertain; repricing is bundled in Base.

## Coverage
Counted from this session (2026-10-29).
- **Sources read by fetch (distinct pages):** 40 — Allegro Community (3 threads), Base pricing, Apilo pricing, Priceva, Shoper app page, jakdorobic.pl, 6 WordPress.org search/plugin pages (allegro, ksef, paczkomat, blik, faktury polska, ceneo) + 2 plugin pages, 8 Trustpilot profiles read (iFirma, inFakt, Fakturownia, Booksy, Versum, ZnanyLekarz, Vimcar, InPost, easyVerein), 5 Google Play search pages, 1 App Store review page, 1 Google Play detail resolution, 8 GitHub search-API queries (allegro, inpost, ksef, ksef/TypeScript, regon, przelewy24, ceidg). Counts are approximate to ±3.
- **Searches run:** 17 web searches (EN 3, PL 11, DE 3).
- **Countries:** Poland (19 of 22 findings), Germany (F17, F19), Canada/Italy not covered here. EU outside DACH: none. This is a Poland-weighted result because the lens was scoped to Polish SMEs and Allegro sellers; the brief also asks for more EU examples.
- **Languages:** Polish, English, German. Not searched: Czech, Slovak, Spanish.
- **Searches that found nothing useful:** Reddit (blocked to the fetch tool), Hacker News (Algolia: 2 irrelevant hits for "Poland KSeF", 0 for "Allegro seller API"), Wykop and Facebook groups (not reachable; not searched directly), Polish forum threads for scheduling/HR software, wspólnoty mieszkaniowe software, vet software in Polish, Polish ERP complaints on Capterra (only foreign ERPs surfaced), Allegro integrator 1-star reviews on Capterra/G2, Shopify App Store (search pages failed to load), Chrome Web Store (not tried: JS-only).
- **Fetches blocked:** Capterra and G2 (403), trusted.de (403), Reddit, old.reddit, wFirma Trustpilot (404), Booksy/Versum primary pricing pages (not read).
- **Search quality note:** the web-search tool returns summaries; every number in the findings comes from a fetched page unless the finding says "search summary" or "unverified".

## Gaps
1. **Complaint text is thin.** Quotes come mostly from Allegro Community, Trustpilot and App Store reviews. Next: Polish Facebook groups for Allegro sellers, Wykop, Elektroda, and the Allegro Community search for "szukam", plus Google Play review text of competitor apps.
2. **No G2/Capterra data.** Both blocked the fetcher. Next: open https://www.capterra.pl/ and https://www.g2.com/ by hand for 1–2 star reviews of Polish-market tools (Subiekt, Comarch Optima, Symfonia, BaseLinker, Sellasist).
3. **Market sizes and platform shares missing.** Number of Allegro sellers using integrators, WooCommerce vs Shoper/IdoSell shares in Poland, salons per segment. Next: GUS/BDL, CEIDG by PKD, Allegro and Gemius/e-Commerce Polska reports.
4. **Developer-side demand unproven.** Stale SDKs show a gap in supply, not that anyone pays. Next: open issues in the stale repos, Stack Overflow questions tagged `allegro-api`/`inpost`, npm download counts (https://www.npmjs.com/), official Allegro SDK check at https://developer.allegro.pl/.
5. **Salon, clinic, vet, HR, wspólnoty and construction segments** only reached a few results each; no verdicts. Next: pricing pages of Versum, Koalendar, Anolla, Clinic/vet software vendors.
6. **EU outside Poland barely covered** (Germany only twice). Next: Czech (Fakturoid, Pohoda), Spain, France, NL via local review sites.
7. **F12 relies on app-store counts that change daily** and one review page for quotes; recheck before using in a write-up. Review year is not shown for several App Store quotes.
8. **F19 and F05** depend on search summaries or promotional pages: confirm on the primary page (trusted.de, Booksy's own pricing).
