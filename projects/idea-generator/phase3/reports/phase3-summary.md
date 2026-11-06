# Phase 3 summary: removing friction in buying and ordering

Written 2026-11-06 by T16. It summarises T01–T15 of Phase 3 ([brief](../BRIEF.md), [progress](../PROGRESS.md)). Every number below is taken or counted from the files on this branch, and the file is linked next to it. Estimates are marked as estimates. A Polish version for the owner is in [podsumowanie-pl.md](podsumowanie-pl.md).

**Bottom line.** No idea in Phase 3 reached the `5–15%` band of earning 10,000 PLN a month in gross profit or fees within 12 months. All 10 write-ups end in `<5%`. After the sceptical review (T15), 4 are still standing: [009 fitment data for Allegro parts sellers](../ideas/v1-vehicle/009-fitment-data-for-parts-sellers.md) (2.86), [001 catering-equipment parts](../ideas/v5-small-business/001-catering-equipment-parts.md) (2.64), [005 camper habitation parts](../ideas/v1-vehicle/005-camper-habitation-parts.md) (2.63) and [006 heat-pump parts for installers](../ideas/v2-home-appliance/006-heat-pump-parts-for-installers.md) (2.56). The other 6 were dropped. So there is **no honest top 5**: section 4 gives validation plans for the 4 survivors plus one dropped idea, labelled as "dropped but nearest".

The review kept finding the same three things: (1) a one-off consumer purchase leaves PLN 1–16 of profit per order, but a Google Ads customer costs PLN 50–125 (sourced CPC ranges, weak sources); (2) parcels from Germany (DHL EU tariff, roughly PLN 70–108 for 5–10 kg) remove most of the margin on German-sourced parts; (3) **no supplier anywhere published dropship, reseller or affiliate terms**, and none was contacted. Three of the four survivors are decided by **free supplier e-mails**, so the first month should go to e-mails and one seller pre-sale, not to code or ads.

## 1. Method and coverage in numbers

| Step | Task | What came out | File |
|---|---|---|---|
| Poland commerce baseline | T02 | ~47 sourced findings: marketplaces, fees, parcels, returns law, affiliate programmes | [research/poland/](../research/poland/ecommerce.md) |
| Friction patterns | T03 | 22 winning cases, 10 patterns (P1–P10), 7 graveyard and ceiling cases | [friction-patterns.md](../research/global/friction-patterns.md) |
| Vertical scans V1–V5 | T04–T08 | 201 catalogued businesses (V1 48, V2 42, V3 39, V4 37, V5 35) from 20 countries (counted in `catalogue/*.csv`; one row has country "unknown") | [catalogue/](../catalogue/V1-vehicle-parts.csv), [research/verticals/](../research/verticals/V1-vehicle-parts.md) |
| Demand mining | T09 | 114 Polish signals, 84 candidate items; mostly Google autocomplete, no verified volumes | [demand/](../demand/V1-vehicle-parts.md) |
| Findability test | T10 | 87 hard-to-find items searched by hand (Ceneo, OLX, web search) | [findability/](../findability/V1-vehicle-parts.md) |
| Longlist | T11 | 95 ideas in 20 themes | [longlist.md](../ideas/longlist.md) |
| Shortlist | T12 | 26 quick-scored, 69 rejected with reasons | [shortlist.md](../ideas/shortlist.md), [rejected.md](../rejected.md) |
| Write-ups | T13–T14 | 10 full write-ups | `ideas/<vertical>/NNN-*.md` |
| Sceptical review | T15 | 10 reviewed: 6 dropped (5 in T15, 1 already in T14), 4 standing; 131 links checked, 0 dead, 14 unverifiable | each write-up's **Devil's advocate** section |

Scoring: nine lenses F1–F9 with weights from [criteria.md](../method/criteria.md); a weighted score of 2.8–3.4 gives `5–15%`, below 2.8 gives `<5%`; the band then drops one step when risks outweigh opportunities by 6 or more, or there is an unmitigated high × high risk ([criteria §3–4](../method/criteria.md#3-from-weighted-score-to-chance-band)). T15 added one rule: an idea is dropped when F4 (unit economics) falls to 1, i.e. one order or customer cannot pay back a CPC-based acquisition cost ([CHANGELOG](../CHANGELOG.md)).

Quick scores fell by 0.34–0.99 points between the shortlist and the end of the review (computed from [shortlist.md](../ideas/shortlist.md)): every idea looked better before it was researched.

## 2. Findability results across verticals

T10 searched each item in at most 3 tries on 2026-11-06. Verdicts: **E** found easily, **W** found with effort or only used/classified, **N** not found or foreign only.

| Vertical | Items | E | W | N | Gap rate (W+N) | Where the gaps were |
|---|---|---|---|---|---|---|
| [V1 vehicle parts](../findability/V1-vehicle-parts.md#verdict-table) | 17 | 7 | 6 | 4 | 59% | new Chinese brands, camper habitation parts, some quad brands, sliding van windows |
| [V2 home, climate, appliance](../findability/V2-home-climate-appliance.md#verdict-table) | 18 | 11 | 2 | 5 | 39% | modules and structural parts for discontinued appliances; distributor-only heat-pump brands |
| [V3 hobby niches](../findability/V3-hobby-niches.md#verdict-table) | 16 | 11 | 5 | 0 | 31% | used parts by part code (reels, sewing machines), Dutch e-bike batteries, single LEGO parts |
| [V4 services with logistics](../findability/V4-services-with-logistics.md#verdict-table) | 19 | 4 | 10 | 5 | 79% | post-warranty brand electronics repair, down-jacket repair, car audio modules (foreign only) |
| [V5 small-business buying](../findability/V5-small-business-buying.md#verdict-table) | 17 | 6 | 4 | 7 | 65% | catering-equipment parts, orphan construction machinery, Juki industrial sewing parts |
| **Total** | **87** | **39** | **27** | **21** | **55%** (computed) | |

How far to trust it:
- **Allegro was never tested.** Its listing pages returned HTTP 403 to the fetch tool in T10 and again in T15. Google was replaced by a generic web-search tool not localised to google.pl. Both make the gaps look **bigger** than they are ([method and limits](../findability/V1-vehicle-parts.md#method-and-limits-same-for-v1v5)).
- **Later checks weakened at least 4 of the 21 N verdicts:** a Polish online catering-parts shop exists (Gastroparts, Toruń; V5 #8 and #9), Jaecoo 7 pads are now sold by Inter Cars and Iparts.pl (V1 #1), and Kaisai heat-pump parts can be ordered from the distributor's service desk (V2 #5). Reimo sells Seitz/Dometic camper window seals in Polish (V1 #17, W leaning to E). All logged in [CHANGELOG.md](../CHANGELOG.md).
- Plain reading: for anything with a model or part number on sale today, Polish buyers mostly find it. The real gaps are **orphan brands** (discontinued appliances, Chinese or old machinery), **distributor-only parts** that are sold by phone, and **post-warranty repair by post**. Most of these are small, rare purchases.

## 3. Ranking of all 10 write-ups

Ordered by the score after T15 review. "Quick" is the T12 shortlist score, "write-up" the T13/T14 score, "T15" the final score ([shortlist.csv](../ideas/shortlist.csv)).

| Rank | Write-up | # | V | Model | Quick → write-up → T15 | Status | Main reason |
|---|---|---|---|---|---|---|---|
| 1 | [009 Fitment data for Allegro and Shoper parts sellers](../ideas/v1-vehicle/009-fitment-data-for-parts-sellers.md) | 19 | V1 | subscription (B2B) | 3.2 → 3.01 → **2.86** | standing, `<5%` | no third-party "Pasuje do" filler found; ~PLN 97 gross profit per seller a month, but B2B click CAC PLN 400–1,070; Allegro can absorb it |
| 2 | [001 Catering-equipment parts](../ideas/v5-small-business/001-catering-equipment-parts.md) | 81 | V5 | margin (B2B) | 3.5 → 2.79 → **2.64** | standing, `<5%` | Gastroparts and REPA (ex-GEV) already sell online; first order loses ~PLN 53 at CAC ~PLN 125 |
| 3 | [005 Camper habitation parts](../ideas/v1-vehicle/005-camper-habitation-parts.md) | 8 | V1 | margin (B2C) | 3.3 → 3.00 → **2.63** | standing, `<5%` | Reimo delivers "only to Germany"; DE→PL parcel ~PLN 91–108 leaves about PLN −2 per order |
| 4 | [008 Chinese-brand collision parts](../ideas/v1-vehicle/008-chinese-brand-collision-parts.md) | 1 | V1 | service fee | 3.2 → 2.67 → **2.57** | rejected (F8 = 1 knock-out, T14) | phone work per case breaks 40 h/month; importers hold body stock |
| 5 | [006 Heat-pump parts for installers](../ideas/v2-home-appliance/006-heat-pump-parts-for-installers.md) | 24 | V2 | margin (B2B) | 3.3 → 2.71 → **2.56** | standing, `<5%` | each brand has one Polish distributor selling parts to its own installers; realistic margin 0–10%, ~PLN 45 per order |
| 6 | [004 Diagnosis then part](../ideas/v2-home-appliance/004-diagnosis-then-part.md) | 36 | V2 | service fee + margin | 3.4 → 2.78 → **2.53** | rejected (T15) | ~PLN 16 per customer vs CAC PLN 50–83; Bosch and LG run remote diagnostics |
| 7 | [003 3D-print instant quote](../ideas/v3-hobby/003-3d-print-instant-quote.md) | 52 | V3 | commission | 3.4 → 2.79 → **2.52** | rejected (T15) | PLN 11 per order vs CAC PLN 75–125; Shopify/WooCommerce plugins give any bureau an instant price in Polish |
| 8 | [002 Body-damage photo quote](../ideas/v1-vehicle/002-body-damage-photo-quote.md) | 17 | V1 | lead fee | 3.5 → 2.88 → **2.51** | rejected (T15) | Oferteo has a body-shop quote category; PZU and LINK4 already estimate damage from photos; ~PLN 0 per request after CAC |
| 9 | [007 Used washer modules](../ideas/v2-home-appliance/007-used-washer-modules.md) | 33 | V2 | commission | 3.3 → 2.67 → **2.45** | rejected (T15) | PLN 1–7 per order; module repair by post (~PLN 110) is cheaper and fits better; no listable supply |
| 10 | [010 Fishing subscription box](../ideas/v3-hobby/010-fishing-subscription-box.md) | 53 | V3 | subscription (B2C) | 3.1 → 2.40 → **2.28** | rejected (T15) | PLN 7–9 per box vs Meta CAC PLN 20–120; the US analogue's assets were sold after USD 56 m raised |

Note that 009's score (2.86) alone would give `5–15%`; it is `<5%` because its risks outweigh its opportunities by 10 points and it has an unmitigated high × high risk (Allegro extends VIN coverage itself).

## 4. Validation plans: 4 survivors and 1 "dropped but nearest"

Fewer than 5 ideas survived T15. Plans 4.1–4.4 are for the survivors. Plan 4.5 is for the best dropped idea that has no knock-out, and is clearly labelled. #1 (008) scores higher than it but is excluded because it failed on the founder's hours (F8 = 1), which no test can change. Each plan comes from the write-up's own "Cheapest validation test" and "Kill criteria", adjusted for what T15 found. Hours are estimates.

### 4.1 [009 Fitment data for Allegro and Shoper parts sellers](../ideas/v1-vehicle/009-fitment-data-for-parts-sellers.md): 2.86, `<5%`
- **What is tested:** whether Allegro motoring sellers whose offers lack "Pasuje do" data will pay PLN 149/month for AI-proposed compatibility, and whether the matches are good enough.
- **Landing page:** none needed at first. A one-page Polish description and a sample report are enough to attach to messages.
- **Ads budget:** **PLN 0.** T15 put B2B click CAC at PLN 400–1,070 per paying seller, so ads would test the wrong thing. About PLN 50 goes on model calls.
- **Manual fulfilment script:** (1) the owner picks 30 sellers with many motoring offers without "Pasuje do" by browsing Allegro category pages **by hand in a browser** (the fetch tool gets 403); (2) for each, take 20 offers and generate proposed compatibility with a prompted model, using Allegro vehicle IDs from the [compatibility-list API docs](https://developer.allegro.pl/compatibility_list); (3) send a free report: "these 20 offers are invisible in VIN search; here is the list we would add"; (4) offer a paid pilot at PLN 149/month; (5) record accepted vs rejected matches. In parallel, e-mail Cairo (TecDoc partner) to ask whether derived fitment may be sold to third parties and at what price.
- **Success in 2 weeks:** at least 3 of 30 sellers agree to a paid pilot **and** they accept at least 80% of the proposed matches.
- **Kill criteria:** fewer than 3 of 30 agree; or fewer than 80% of matches accepted; or Cairo/TecAlliance confirm a licence above PLN 2,000 a month is needed; or more than half of the high-volume sellers already use Ovoko's Allegro sync (write-up risk 3).
- **Hours:** ~12–15 h (estimate: list building, 30 reports, follow-ups).

### 4.2 [001 Catering-equipment parts](../ideas/v5-small-business/001-catering-equipment-parts.md): 2.64, `<5%`
- **What is tested:** first, whether any wholesaler gives a newcomer a trade discount; only then, whether restaurants send plate photos and pay a premium over Gastroparts.
- **Step 1, free:** e-mail Gastroparts, REPA (official Unox distributor for DACH, ex-GEV) and Parts Town for reseller or dropship terms. **Stop here** if no one offers ≥15% within 3 weeks.
- **Landing page (step 2):** "Wyślij zdjęcie tabliczki, podamy numer części i cenę w 2 godziny", for Unox, Carpigiani and Rational.
- **Ads budget:** PLN 250 on ~30 exact part-number and `części unox / carpigiani` phrases.
- **Manual fulfilment script:** read the plate, find the part number in the distributor catalogue, quote price and date within 2 hours, take payment by transfer or BLIK with a VAT invoice, order by hand from the supplier that gave terms, have it shipped to the restaurant. Log each enquiry as restaurant or technician.
- **Success in 2 weeks:** at least 5 photo enquiries from PLN 250 of ads, and buyers who pay 15–20% above Gastroparts' net price.
- **Kill criteria:** no trade discount ≥15% in 3 weeks; fewer than 5 enquiries; buyers mention Gastroparts/GEV and will not pay more; more than half of enquiries are technicians asking for a discount.
- **Hours:** ~2 h for e-mails; ~8–10 h for the ads step (estimate).

### 4.3 [005 Camper habitation parts](../ideas/v1-vehicle/005-camper-habitation-parts.md): 2.63, `<5%`
- **What is tested:** whether a German supplier will ship to Polish buyers (or accept a Polish dealer) at ≥20% margin, and whether brand-specific body parts (the only gap that held, e.g. the Knaus door seal) are asked for often enough.
- **Step 1, free, now:** e-mail Frankana Freiko, Reimo (ask for **dealer** terms, since Reimo PL delivers only to Germany) and two German Knaus/Hymer dealers.
- **Landing page (step 2):** a Polish "find your part" form (brand, model, year, photos).
- **Ads budget:** PLN 200 on 20 brand-part phrases, plus free posts in 3 Polish camper groups (with admin consent). **Run it in season (March–April 2027)**: the kill criterion is defined for the season and now is November.
- **Manual fulfilment script:** identify body brand and part from photos, quote within 24 h with freight shown separately (T15: free freight from Germany leaves about PLN −2 per order), order from the supplier, supplier ships.
- **Success in 2 weeks (in season):** at least 15 part requests, fewer than half dealer-only at retail price, and a quoted margin ≥20% after freight.
- **Kill criteria:** no supplier ships to Polish buyers at ≥20% margin; fewer than 15 requests in 2 weeks in season; more than half of requested parts dealer-only at retail. Also kill if the only route is becoming a Reimo/Frankana dealer that buys stock (breaks the no-inventory rule).
- **Hours:** ~2 h for e-mails now; ~10 h in season (estimate).

### 4.4 [006 Heat-pump parts for installers](../ideas/v2-home-appliance/006-heat-pump-parts-for-installers.md): 2.56, `<5%`
- **What is tested:** whether distributors give any reseller discount (T15 expects 0–10%), and whether installers see the distributor's service desk as a problem worth paying for.
- **Step 1, free:** e-mail Klima-Therm (Kaisai), Refsystem (named as Haier distributor, unverified), the Gree representative and CNC Pompy Ciepła for reseller terms.
- **Step 2, free:** phone 15 installers from the brands' service-partner lists: how do you get parts now, how long does it take, would you pay 15% for one multi-brand request form?
- **Landing page (step 3):** a B2B request form (plate photo, error code, symptom).
- **Ads budget:** PLN 250 on 10 `płyta pompa ciepła [brand]` phrases (installer-level CPC not found; T15 says these phrases have little volume).
- **Manual fulfilment script:** match plate and error code to the part, request a quote from the distributor by e-mail or phone, show price with margin and date, take payment, supplier ships to the installer. Time each order (risk: more than 20 minutes per order breaks the 40 h limit before 100 orders).
- **Success in 2 weeks:** at least one distributor offers a reseller discount, at least 5 of 15 installers name the desk as a problem, and at least 5 qualified part requests from ads.
- **Kill criteria:** no reseller discount from any distributor; fewer than 5 of 15 installers see a problem; fewer than 5 qualified requests.
- **Hours:** ~2 h for e-mails, ~5 h for 15 calls, ~6 h for the ads step (estimate).

### 4.5 Dropped but nearest: [004 Diagnosis then part](../ideas/v2-home-appliance/004-diagnosis-then-part.md): 2.53, rejected in T15
This idea is **rejected**. It is here only because it is the highest-scoring dropped idea without a knock-out and the only consumer-facing one close to the survivors. #52 (2.52) and #17 (2.51) are almost level with it. T15 dropped it because a one-off purchase leaves ~PLN 16 per customer against a CAC of PLN 50–83, Bosch Home Connect and LG Smart Diagnosis already do remote triage, and no appliance-parts wholesaler has public dropship terms. Run this test only if 4.1–4.4 all fail and you still want a consumer test.
- **Landing page:** 3 washer brands, free AI triage behind a form, a "15 min technician call PLN 39" button. Limit it to older, non-connected and store-brand machines (the gap T15 left open).
- **Ads budget:** PLN 250 on 20 error-code phrases.
- **Manual fulfilment script:** the model proposes the faulty part; one technician paid per call confirms it; the part is ordered by hand from CzęściAGD.pl.
- **Success in 2 weeks:** at least 3% of form starters pay for a call or a part, the technician confirms the triage in at least 40% of cases, and a wholesaler offers at least 15% margin. Even then, T15's arithmetic says it pays only on free traffic, so a pass means "look for an SEO channel", not "scale ads".
- **Kill criteria:** the write-up's three (under 3% pay, under 40% confirmed, no 15% margin).

**Not reviewed, possibly worth a write-up before any test:** shortlist ideas that were never written up still carry quick scores of 3.2 in `5–15%`: #84 Juki industrial sewing parts for the Łódź cluster, #87 restaurant–wholesaler ordering app, #67 down-jacket repair by post, #72 car premium-audio module repair by post ([shortlist.md](../ideas/shortlist.md)). Every written-up idea lost 0.34–0.99 points when researched, so these are likely `<5%` too. The repair-by-post ones (#67, #72) sit in V4, the vertical with the highest gap rate (79%).

## 5. Which business models look viable

From the unit economics recomputed in T15 (all estimates on sourced parcel prices and weak CPC sources):

| Model | Ideas | Profit per order/customer before CAC | Verdict |
|---|---|---|---|
| **Commission or affiliate**, consumer | 003, 007 | PLN 1–11 per order; Polish affiliate rates on parts ~3–8%, new customers only, unverified ([monetisation M4–M5](../research/poland/monetisation.md#1-affiliate-and-partner-programmes)) | **not viable on paid traffic**; at best a side income on SEO |
| **Lead fee**, consumer job | 002 | ~PLN 0 after CAC | not viable; Oferteo and Fixly own the format |
| **Service fee + margin**, consumer one-off | 004, 008 | PLN ~16 (004); 008 fails on hours | not viable on paid traffic |
| **Consumer subscription** | 010 | PLN 7–9 per box; Allegro Smart! anchors consumer subscriptions at PLN 59.90/year ([M9](../research/poland/monetisation.md#3-what-poles-pay-subscriptions-for-today)) | not viable; consumers do not pay a subscription to find something once |
| **Margin on resold parts**, consumer, cross-border | 005 | about PLN −2 with free freight from Germany | viable only if freight is passed on and a supplier ships direct; unproven |
| **Margin on resold parts**, B2B | 001, 006 | PLN 72 (001), PLN 45 (006) | **the only margin model with a positive repeat order**, but it depends on trade discounts nobody has offered yet |
| **B2B subscription (software)** | 009 | ~PLN 97 per seller a month; CAC PLN 400–1,070 by clicks, PLN ~600 by outreach (estimates) | **the most promising model on paper**: recurring, no parcels or returns; risk is Allegro absorption and data licences |

So the owner's starting guess (a small subscription) holds **only for professionals**, as the T03 patterns already suggested ([friction-patterns §5](../research/global/friction-patterns.md#5-takeaways-for-the-longlist-t11)): subscriptions work for replenishment and for professionals, not for consumers who want a part once. Consumer ideas only work where the traffic is free (SEO, communities), and none of the write-ups showed such a channel at scale.

## 6. Recommended order for the owner's 40 h/month

Budget: 500 PLN a month. Hours are estimates.

| When | What | Hours | Cost |
|---|---|---|---|
| Week 1 (November) | Send all supplier e-mails at once: Gastroparts, REPA, Parts Town (001); Klima-Therm, Refsystem, Gree representative, CNC Pompy Ciepła (006); Frankana, Reimo dealer terms, 2 Knaus/Hymer dealers (005); Cairo/TecDoc licence question (009) | ~6 h | 0 PLN |
| Weeks 1–3 | 009 seller pre-sale: 30 sellers, 30 reports, pilot offers | ~12–15 h | ~50 PLN |
| Week 2 | 006: 15 installer calls | ~5 h | 0 PLN |
| Weeks 3–4 | Only for 001 or 006, and only if a supplier offered terms that pass the kill line: one ads test | ~8–10 h | 250 PLN |
| December–January | If 009 passed: build the MVP (Allegro OAuth, import, AI proposals, bulk approve) with the agentic stack; owner time goes to the paying pilots | rest of the hours | — |
| March–April 2027 | 005 ads and group posts, in season, only if a German supplier agreed to ship | ~10 h | 200 PLN |
| Only if all above fail | 4.5 (004), or write up #84/#87/#67/#72 first | — | 250 PLN |

Decision rule: build only the idea that passes its success number. If 009 passes, it goes first, because it has no parcels, no returns and no physical work. If no supplier answers with terms and 009 fails, stop desk research: Phase 1 ended with one idea in `5–15%` ([Phase 1](../../reports/phase1-summary.md)) and Phase 2 and Phase 3 with none ([Phase 2](../../phase2/reports/phase2-summary.md)), so the next step is customer interviews in one trade, not more scanning.

## 7. Open questions for the owner

1. **Physical work:** is ~8 h a month still the limit? 005 may only work if you become a Reimo or Frankana dealer, which means briefly holding stock.
2. **Sales calls:** 009 and 006 need B2B outreach (8–20 h a month by the write-ups' estimates). Are you willing to phone sellers and installers?
3. **Things only you can check:** Allegro search and category pages in a browser (blocked for the agent), Google Keyword Planner volumes and CPC (needs a login), affiliate rates in network panels (need sign-up). One evening on these would replace the weakest numbers in this report.
4. **Supplier e-mails:** should they go from your name and company, or from a new brand? Wholesalers usually answer registered firms.
5. **Next research:** if the tests fail, would you rather write up the four untested quick-score ideas (#84, #87, #67, #72) or switch to interviews?

## 8. Honest limitations

- **Allegro unverified.** Every Allegro listing and search page returned 403 to the fetch tool in T10 and T15. T10 itself calls Allegro the main channel for used and classic parts, so findability gaps are overstated and competition is understated.
- **No real Google search.** A web-search tool not localised to google.pl stood in for Google; Google Maps, Booksy and Fixly were not used for V4 services.
- **Demand is weak evidence.** T09 used Google autocomplete; no search volumes, no Google Trends, no Facebook group sizes were verified. F2 was never scored above 4 for that reason.
- **CPC and conversion are weak.** The only Polish CPC source (Ardura Lab) states no method; conversion rates come from US benchmarks and a marketing blog with no primary source. Every CAC in this report rests on them.
- **Return rates are borrowed.** 15–25% from an auto-parts blog and 13% wrong-part incidence from a US trade body, both via search summaries; no Polish or appliance figure was found.
- **Supplier terms unverified.** No supplier was contacted, and none publishes dropship, reseller or affiliate terms. Every margin (15–25%) is an estimate.
- **Parcel prices are list prices.** The DHL EU tariff is retail; contract rates are lower and were not checked. FX rates are estimates.
- **Many facts come from search summaries**, not opened pages; the write-ups say so line by line. T15 left 14 links unverifiable (403/timeout/SSL) ([PROGRESS.md](../PROGRESS.md)).
- **Market sizes are mostly unsourced** for the buyer group that matters: Allegro motoring seller counts, heat-pump installer counts, the share of restaurants buying their own parts, the Polish camper fleet.
- **One pass, one day.** All tasks ran on 2026-11-06 by an agent, with one sceptical review. Nothing was tested with real buyers.
