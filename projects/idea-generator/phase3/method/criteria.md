# Phase 3 scoring criteria

How Phase 3 businesses and ideas are recorded and scored. Used by the vertical scans (T04–T08, catalogue columns), demand mining (T09), the findability test (T10), the longlist (T11), the shortlist (T12), the write-ups (T13–T14) and the review (T15).

Each of the 9 lenses F1–F9 in [BRIEF.md](../BRIEF.md) gets a score from 1 to 5. The anchors below describe 1, 3 and 5; 2 and 4 sit in between.

**Evidence rule.** A score of 4 or 5 needs at least one cited source (URL + access date) showing the evidence named in the anchor. Without a source the score is capped at 3. A score that rests on an estimate says so ("estimate"). When in doubt, score lower: most ideas should land at 2–3. (Kept from Phase 2's [criteria](../../phase2/method/criteria.md).)

## 1. Rubric (1 / 3 / 5)

### F1 — Size of the friction (weight 15%)
How much the buyer suffers today when trying to buy this. Scored from the T10 findability result, demand quotes (T09) and the six friction types of the brief (finding, fit, trust, logistics, coordination, price discovery).
- **1:** The buyer types an obvious phrase into Google or Allegro and gets a fitting, fairly priced offer on the first page; fit is obvious (one size, one standard); delivery is a normal parcel. T10 result: found in the first try.
- **3:** The item or service can be found, but only with the right part number, model code or jargon, or after comparing several shops; or one friction type is clearly present (e.g. fit is uncertain, returns are a hassle, booking takes phone calls). T10 result: found in 2–3 tries, or found but fit/trust unclear. Forum threads show people asking "which one fits".
- **5:** The buyer needs hours, phone calls or a specialist, or fails to find the item in 2–3 searches on Google/Allegro (T10 result "not found" or "found only abroad"); two or more friction types stack (e.g. unknown part number + uncertain fit + no one to install); demand evidence shows people giving up, buying the wrong item, or paying a middleman to find it.

### F2 — Breadth and frequency of demand in Poland (weight 15%)
- **1:** Very rare purchase by a small group (a few thousand people in Poland), no search or forum signal, or only a one-off purchase with no reason to come back.
- **3:** A clear group exists in Poland with indirect evidence of size (forum activity, Facebook group members, Google autocomplete, Allegro listing counts) and a purchase that recurs every year or two, or a large group buying once.
- **5:** Sourced size of the buyer group (GUS/BDL, CEPiK vehicle counts, industry association data, registry counts) of at least hundreds of thousands of buyers or tens of thousands of firms, **plus** repeat purchase at least yearly (consumables, replenishment, seasonal service) or a steady flow of new buyers, **plus** at least 15 concrete Polish search or forum signals (T09).

### F3 — Simplicity of fulfilment (weight 10%)
Supply, shipping and returns without the founder holding inventory.
- **1:** Needs stock held by the founder (buying ahead, a warehouse, minimum orders), or bulky / hazardous / temperature-controlled goods the founder must handle, or each order needs the founder on site. **Knock-out** (see section 3).
- **3:** A supplier or partner ships or performs the service, but with friction: the founder relays orders by hand, returns come back to the founder, delivery is oversized or slow, or only one supplier is willing and terms are unclear.
- **5:** The supplier ships directly to the buyer (dropship or marketplace fulfilment) or the service provider does the physical step, **and** takes returns and warranty claims; orders can be passed on by API, feed or a simple email; standard parcel size (InPost locker or courier).

### F4 — Unit economics in PLN (weight 15%)
Computed per order (or per subscriber per month): margin, commission or fee **minus** delivery not paid by the buyer, returns, payment fees (BLIK/Przelewy24/card), support time at a stated hourly value and customer acquisition cost (CAC). Show the arithmetic.
- **1:** Gross profit per order is below delivery + payment fee, or CAC (realistic Google Ads cost per click × conversion) exceeds the first-order profit with no repeat purchase to recover it; or affiliate commission is a few PLN on a rarely bought item.
- **3:** Gross profit per order covers delivery, returns and payment fees with something left, and CAC is recovered within 2–3 orders or in the first year of a subscription; numbers are estimates from comparable shop prices and published commission rates.
- **5:** Gross profit per order covers delivery, returns and CAC with a margin already on the first order (or CAC is near zero thanks to an owned channel), on numbers grounded in sources (published commission or take rates, supplier price lists, InPost/DPD rates, Google Ads keyword planner or comparable data); 10,000 PLN monthly gross profit needs an order count that the demand evidence (F2) supports.

### F5 — AI leverage (weight 10%)
Whether cheap prediction and classification is a real edge here, not a chat box.
- **1:** AI adds nothing a filter, a lookup table or a human answer in an email couldn't do; or ChatGPT/Google already answers the question fully and the value would sit in the answer alone.
- **3:** AI does one real job step (matching a description or photo to a part number, normalising messy supplier catalogues, classifying requests, drafting supplier messages), but a rules-based shop could do most of it with more manual effort.
- **5:** The business only works at its price because AI does the matching or classification at near-zero cost per order: e.g. identifying a part from a photo, label or VIN across messy catalogues from many suppliers, keeping cross-references current, or routing service requests, where a human doing it would eat the whole margin. Value sits in data, supplier links or workflow that ChatGPT and Google don't have.

### F6 — Competition (weight 12%)
Allegro, Amazon.pl, Ceneo, OLX, producers' own shops, existing specialist shops, and foreign players shipping to Poland.
- **1:** A big player already serves it well in Polish: e.g. Allegro or a large specialist (Oponeo, Autodoc, Inter Cars, Media Expert service) offers the fit filter, the fast delivery and the returns; T10 found it in one try. Also 1 if Allegro could close the gap with a filter it is already building.
- **3:** Players exist but leave a visible gap: generic listings without fit data, only a foreign shop (German or English UI, slow shipping), only phone or showroom ordering, or prices that are not comparable; the gap could be closed by an incumbent within a year if they cared.
- **5:** No Polish player does the job, the obvious incumbents were actually checked (T10 queries on Google, Allegro, Ceneo, OLX, Amazon.pl) and fail, and there is a reason they ignore it (niche too small for them, needs supplier work or data they don't have, conflicts with their model).

### F7 — Regulation and liability (weight 8%)
Higher score = lower burden. Flags only, not legal advice.
- **1:** Needs a licence or certification the founder can't get (e.g. F-gas certificate for handling refrigerants, a pharmacy or alcohol licence, financial licence), or carries liability that one wrong match could make serious (safety-critical parts such as brakes or gas fittings sold as "fits" with the founder liable), or regulated import.
- **3:** Normal consumer-sale obligations apply and need care: 14-day withdrawal right, rękojmia (warranty), GPSR product-safety information for the seller, electrical equipment (WEEE / CE marking), RODO for customer data; manageable with templates and supplier documents, but a mis-match costs returns.
- **5:** Little regulation beyond a standard shop or intermediary: commission or lead-fee model where the seller of record is someone else, non-hazardous goods, no safety-critical fit claims, standard RODO.

### F8 — Founder fit (weight 8%)
40 h/month of non-code work, about 8 h/month physical work at launch, no inventory, no staff, no licence, no large capital (brief).
- **1:** Needs inventory, staff, a licence, large upfront capital, heavy on-call operations, or physical work well above ~8 h/month at the first 50 orders. **Knock-out** (see section 3).
- **3:** Fits the limits at launch but needs one hard thing: a supplier deal that takes months of phone calls, a data source with uncertain access, or physical work that grows linearly with orders and hits the limit at ~100 orders/month.
- **5:** MVP in ≤6 weeks on known tech; supply and data openly available (affiliate feeds, supplier APIs, public catalogues with allowed use); physical work ≤8 h/month even at 200 orders/month; non-code work ≤40 h/month.

### F9 — Defensibility (weight 7%)
- **1:** Anyone, including an Allegro seller, Allegro itself or ChatGPT/Google, can copy it in a month: the value is a filter, a list or an answer.
- **3:** Some protection: a cleaned compatibility dataset that took months, a niche community, supplier relations, or repeat-purchase lock-in (saved devices, subscription), but nothing that compounds.
- **5:** Value compounds with each order: proprietary fit/compatibility data improved by every match and return, exclusive or preferential supplier terms, a community or B2B accounts with switching costs, and incumbents have shown no sign of entering.

## 2. Weights

| Lens | Weight |
|---|---|
| F1 Size of the friction | 15% |
| F2 Breadth and frequency of demand in Poland | 15% |
| F3 Simplicity of fulfilment | 10% |
| F4 Unit economics in PLN | 15% |
| F5 AI leverage | 10% |
| F6 Competition | 12% |
| F7 Regulation and liability | 8% |
| F8 Founder fit | 8% |
| F9 Defensibility | 7% |
| **Total** | **100%** |

These are the weights from the brief, unchanged: they sum to 100% and put the most weight on the Phase 3 question (how big the friction is, how many people have it, and whether removing it pays). Change them only with a reason written here and a line in [CHANGELOG.md](../CHANGELOG.md); then rescore every shortlisted idea with the new weights.

**Weighted score** = Σ (score × weight), a number from 1.0 to 5.0, rounded to one decimal.
Example: F1 4, F2 3, F3 4, F4 3, F5 3, F6 3, F7 4, F8 4, F9 2 → 0.60 + 0.45 + 0.40 + 0.45 + 0.30 + 0.36 + 0.32 + 0.32 + 0.14 = **3.34 → 3.3**.

**Quick score (T12 shortlist).** Same lenses and weights, scored from the catalogue, demand and findability files only; mark it "quick". Write-ups rescore with full evidence.

## 3. From weighted score to chance band

Success = **≥10,000 PLN MRR-equivalent (monthly gross profit or fees, not turnover) within 12 months of launch**. The base rate for solo commerce businesses is low, so the default band is `<5%` and the score has to earn its way up.

| Weighted score | Chance band | Extra conditions |
|---|---|---|
| < 2.8 | `<5%` | — |
| 2.8 – 3.4 | `5–15%` | — |
| 3.5 – 4.1 | `15–30%` | F1, F2 and F4 each ≥ 3, and at least two of them ≥ 4 with sources; F6 ≥ 3; a T10 findability result exists |
| ≥ 4.2 | `>30%` | All of the above, plus a written argument: who the first 100 buyers are and through which channel, why they pay, and why the order or subscriber count for 10,000 PLN monthly gross profit is reachable |

**Knock-outs** (override the table):
- F3 = 1 (needs stock or founder-handled goods) or F8 = 1 (inventory, staff, licence, capital, heavy on-call, physical work far above ~8 h/month): drop the idea and record it in [rejected.md](../rejected.md) with the reason.
- F6 = 1 (a big player already serves it well) or F1 = 1 (no real friction): band is `<5%` whatever the score.
- F7 = 1: band is `<5%` unless the write-up shows a model where the licence or liability sits with a partner (e.g. a certified installer is the seller of record).
- If a condition for a band isn't met, use the next band down.

**Sanity check on order count.** Divide 10,000 PLN by the gross profit per order (or per subscriber per month). At 25 PLN gross profit per order that is 400 orders per month; at 8 PLN commission it is 1,250 orders per month; at 19 PLN/month subscription ~526 subscribers. If the reachable Polish buyer group, with a source for its size, is not at least ~20× the monthly order or subscriber count, cap the band at `5–15%`. Also check the physical work at that order count against F8.

Bands are judgments backed by evidence, not computed probabilities. Every band above `<5%` points to the sources behind the scores that put it there.

## 4. Opportunities (szanse) and risks (ryzyka)

Copied from Phase 2. Write the two lists independently: list opportunities first without looking at risks, then risks without looking at opportunities. Don't write a risk as the negation of an opportunity ("demand may not exist" next to "demand exists"). Aim for 3–6 items in each list.

**Each item** gets:
- **Likelihood** H / M / L: H = more likely than not within 12 months, with evidence; M = plausible, some evidence; L = possible but no evidence yet.
- **Impact** H / M / L on reaching 10,000 PLN monthly gross profit: H = changes whether the idea reaches the goal at all; M = changes the time or size noticeably (±30% of gross profit or ±3 months); L = minor.
- **What would make it true** (for an opportunity) or **early warning sign** (for a risk): something observable within the first 3 months.

**Points:** H = 3, M = 2, L = 1; item weight = likelihood × impact (1–9). An item with weight ≥ 6 is **major**.

**How they move the band** (after the score table and knock-outs):
1. Sum opportunity weights (O) and risk weights (R).
2. **Up one band** only if O − R ≥ 6 **and** at least one major opportunity has a source, **and** the extra conditions of the higher band are met. Never more than one band up; never into `>30%` by this rule alone.
3. **Down one band** if R − O ≥ 6, or if any risk is H likelihood × H impact (weight 9) with no mitigation in the MVP plan.
4. **Down two bands** (floor `<5%`) if two or more risks have weight 9.
5. Otherwise the band stays where the score put it. Record the sums and the rule applied, e.g. "O 14, R 11, no H×H risk → band unchanged".

Typical risk sources to consider (from the brief): Allegro or the platform owner adding the filter or service; ChatGPT/Google answering the fit question; supplier refusing a newcomer or changing terms; catalogue data licence or scraping terms; returns and wrong-fit cost; delivery cost for oversized goods; seasonality; consumer law (withdrawal right, rękojmia, GPSR); F-gas or other regulated goods; graveyard lessons from closed vertical marketplaces; growth only from paid ads or delivery subsidies.

## 5. Catalogue CSV columns

One row per business in `catalogue/VN-<name>.csv`, UTF-8, comma-separated, header row exactly as below, fields with commas in double quotes. `unknown` when not found; never leave a cell blank except `pattern` before T11.

Header:
```
id,name,country,vertical,url,launched,category,b2b_b2c,friction_types,how_it_earns,physical_step,ai_role,traction,traction_source,repeat_signal,take_rate_or_margin,hype_warnings,works_in_poland,pl_adaptation_angle,pattern
```

| Column | Content | Example (format only) |
|---|---|---|
| `id` | `VN-CC-NNN`: vertical number, ISO 3166-1 alpha-2 country code, running number | `V1-DE-003` |
| `name` | Business name as on its site | `Autodoc` |
| `country` | Country where it is based or first grew (English name) | `Germany` |
| `vertical` | `V1`–`V5` | `V1` |
| `url` | Home page (checked) | `https://www.autodoc.de/` |
| `launched` | Year (or year-month) of launch, with "launch"/"breakout"; `unknown` | `2008 launch` |
| `category` | Short label reused across rows (e.g. car-parts, tyres, appliance-parts, filters, hvac-parts, hobby-parts, repair-by-post, mro, trade-supplies) | `car-parts` |
| `b2b_b2c` | `B2B`, `B2C` or `B2B2C` | `B2C` |
| `friction_types` | Which of the six friction types it removes, semicolon-separated: `finding; fit; trust; logistics; coordination; price` | `finding; fit` |
| `how_it_earns` | Model(s), main one first: `margin`, `dropship-margin`, `commission`, `affiliate`, `service-fee`, `subscription`, `lead-fee`, `ads` | `margin` |
| `physical_step` | What is done by hand or physically, and by whom (business, supplier, partner) | `"own warehouses; ships parcels"` |
| `ai_role` | What AI or automated matching does, a few words; `none found` | `"vehicle lookup by registration"` |
| `traction` | Number + what it measures + date | `"revenue 1.2B EUR, 2023"` |
| `traction_source` | URL of the source for `traction` + access date `YYYY-MM-DD` | `<source URL> 2026-11-06` |
| `repeat_signal` | Evidence of repeat purchase or retention (subscription count, repeat rate, replenishment model), with source; `unknown` | `"subscriptions for filters (url)"` |
| `take_rate_or_margin` | Published take rate, commission or gross margin, with source; `unknown` | `"gross margin 30% (url)"` |
| `hype_warnings` | Hype warnings found (section 6), or `none found` | `"growth from free delivery subsidy (url)"` |
| `works_in_poland` | `unknown` / `no` / `partly` / `yes`: does it sell or operate in Poland in Polish? | `yes` |
| `pl_adaptation_angle` | One line: what a Polish version would need, or why one isn't needed | `"already in Poland; no gap"` |
| `pattern` | Friction pattern id (filled in T11 from T03's patterns) | `` |

The examples show the format only; every real row needs its own source.

## 6. Durable vs. hype rubric for commerce

Used when recording analogues in the catalogue and in write-ups (Success signals). A signal counts only with a source (URL + date); "probably" doesn't count.

**Durable signals** (the brief's ten, from [Phase 2 BRIEF](../../phase2/BRIEF.md), read for commerce):
1. **Replaces a spend:** the buyer stops paying for something else (a mechanic's markup, a wasted wrong part, a call-out fee, time off work).
2. **Frequent problem with an owner:** the purchase recurs (consumables, seasonal parts, servicing) or the buyer is a professional who buys weekly.
3. **Retention / repeat purchase:** published repeat-purchase rate, share of orders from returning customers, subscriber retention.
4. **Expansion:** average order value or categories per customer grow; B2B accounts add users or sites.
5. **Owned distribution:** most traffic from organic search, direct, community or partners, not paid ads.
6. **Time to value in minutes:** the buyer finds the fitting item or books the service in one session.
7. **Value-based pricing:** take rate or margin held without discounting; premium for certainty of fit.
8. **Hard to absorb:** value sits in inventory data, supplier links, fulfilment or a workflow that Allegro, Google or ChatGPT can't copy with a filter or an answer.
9. **Pull from customers:** buyers ask for it (forums, waiting lists, inbound suppliers wanting to join).
10. **Timing window:** a dated change that creates demand (a regulation, a new device generation, a ban, a subsidy programme ending).

**Commerce metrics to record whenever public** (brief): repeat-purchase rate, gross margin or take rate, return rate, share of traffic from search or marketplaces. Each counts as evidence for the signal it shows (repeat rate → 3, take rate held → 7, organic traffic share → 5).

**Hype warnings:** growth only from paid ads or influencers · growth from subsidies (free delivery, deep discounts, cashback) that were later cut · traffic spike without repeat purchase · negative unit economics per order publicly reported · heavy layoffs, pivot or market exits after funding · a "marketplace" with listings but no transactions · rapid fee or commission cuts to keep sellers.

Signals 3 (retention / repeat) and 4 (expansion) are the strongest evidence: count each of them double.

**Durability score** = durable points (signals, with 3 and 4 double) − 2 × hype warnings.

| Durability score | Label | Use |
|---|---|---|
| ≤ 0, or only hype evidence | **hype** | the analogue can't support F2 or F4 above 3 |
| 1 – 3 | **unproven** | the analogue supports at most 3 on F2/F4 |
| 4 – 6 | **promising** | supports up to 4 |
| ≥ 7, including signal 3 or 4 | **durable** | supports 5 if the Polish evidence also qualifies |

An analogue is evidence that the model can work, not that it will work in Poland: Polish scores still need Polish evidence (T09, T10). For a Polish idea (write-ups), list which durable signals the Polish version can realistically reproduce: the spend it replaces (1), the owned channel (5), the repeat driver (3) and what makes it hard to absorb (8).
