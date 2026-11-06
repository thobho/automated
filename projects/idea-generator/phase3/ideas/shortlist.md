# Phase 3 shortlist (T12, quick scores)

Human-readable view of [shortlist.csv](shortlist.csv) (final scores from write-ups: [T13 batch A](#write-ups-t13-batch-a), [T14 batch B](#write-ups-t14-batch-b), [T15 review](#review-t15-sceptical-pass)) ([task](../tasks/12-filter-and-shortlist.md)). Scores are **quick** ([criteria](../method/criteria.md) §2): judged from the longlist evidence (T04–T11 files), not re-researched; weighted scores and bands are computed by [shortlist_score.py](shortlist_score.py). Rejected ideas and reasons: [rejected.md](../rejected.md). 2026-11-06.

## How it was filtered

1. Knock-outs from criteria §3: F3 = 1 or F8 = 1 (stock, capital, heavy physical work) and F7 = 1 dropped (#3, #16, #29, #94).
2. Ideas where T10 found the item at once or a Polish incumbent already serves it (F1 or F6 at 1–2) dropped (19 ideas).
3. Near-duplicates merged into the stronger sibling (#9, #10 → #8; #26 → #24; #34, #38 → #36; #68 → #67).
4. Of the rest, the ~26 highest quick scores kept, with a spread across V1–V5 and models; untested ideas with no supplier or size dropped.

**Result:** no idea reaches `15–30%`. #81 scores 3.5 but F2 and F4 are only 3 (no sourced size, no supplier prices), so it stays `5–15%`. #30 stays on the list at `<5%` as the HVAC replenishment test. Opportunity/risk sums (criteria §4) are not applied at this quick stage; each row has its top opportunity and top risk with likelihood/impact.

**Spread:** V1 6, V2 6, V3 5, V4 4, V5 5. Models: margin 8, service fee 5, commission 4, subscription 4, lead fee 3, service fee + margin 1, subscription (supplier pays) 1. Owner areas: car 6, hobby 5, HVAC 3.

## Shortlist

| Rank | # | Idea | V | Model | Weighted | Band | First supplier | First channel |
|---|---|---|---|---|---|---|---|---|
| 1 | 81 | Catering-equipment spare parts from EU distributors for restaurants | V5 | margin | 3.5 → **2.8** ([001](v5-small-business/001-catering-equipment-parts.md)) | 5-15% → **<5%** | Nisbets (IE) or Parts Town (US) seen in T10; EU distributor terms unverified | SEO on uszczelka Unox and Carpigiani czesci phrases (V5-D08, 2+3 suggestions) |
| 2 | 17 | Photo-based body-damage quote to partner body shops | V1 | lead fee | 3.5 → **2.9** ([002](v1-vehicle/002-body-damage-photo-quote.md)) | 5-15% → **<5%** | local body shops (none named; kb.pl price lists show them) | unverified (cash-paying drivers after small damage; no channel named) |
| 3 | 52 | Instant multi-bureau 3D-print quote from an uploaded file | V3 | commission | 3.4 → **2.8** ([003](v3-hobby/003-3d-print-instant-quote.md)) | 5-15% → **<5%** | Polish print bureaus quoting on Oferteo (none contacted) | SEO on druk 3D na zamowienie cena (V3-D04) |
| 4 | 36 | Video or photo diagnosis before the part, ending in a dropshipped part | V2 | service fee + margin | 3.4 → **2.8** ([004](v2-home-appliance/004-diagnosis-then-part.md)) | 5-15% → **<5%** | CzęściAGD.pl (also a wholesaler); BSH shop by E-Nr | SEO on co sie zepsulo w pralce type phrases (V2 scan 8) |
| 5 | 8 | Camper habitation parts by body brand, dropshipped from DE | V1 | margin | 3.3 → **3.0** ([005](v1-vehicle/005-camper-habitation-parts.md)) | 5-15% → **<5%** | Reimo (seen in T10 item 7); Dometic windows via one OLX seller | SEO on the camper-parts autocomplete phrases (V1-D07, 10 suggestions) |
| 6 | 24 | Spare parts for distributor-only heat-pump brands, for installers | V2 | margin | 3.3 → **2.7** ([006](v2-home-appliance/006-heat-pump-parts-for-installers.md)) | 5-15% → **<5%** | KLIMA-THERM (Kaisai distributor, T10) | heat-pump installers searching the V2-D04 phrases (9 suggestions) |
| 7 | 33 | Fit-checked used modules for discontinued washers from donor machines | V2 | commission | 3.3 → **2.7** ([007](v2-home-appliance/007-used-washer-modules.md)) | 5-15% → **<5%** | independent repairers and OLX donor machines | elektroda.pl forum threads on washer modules (V2-D01) |
| 8 | 1 | Collision-part sourcing desk for Chinese brands | V1 | service fee | 3.2 → **2.7** ([008](v1-vehicle/008-chinese-brand-collision-parts.md)) | 5-15% → **<5%** (F8 knock-out) | brand importers and dealers (ASO); used parts on OLX | Omoda Polska Facebook group (>30,000 members, V1 demand S3) |
| 9 | 19 | Fitment data for Allegro and Shoper parts sellers | V1 | subscription | 3.2 → **3.0** ([009](v1-vehicle/009-fitment-data-for-parts-sellers.md)) | 5-15% → **<5%** | TecDoc or OE data licence, or AI extraction from listings (rights unverified) | Allegro and Shoper parts sellers (none contacted) |
| 10 | 84 | Industrial sewing-machine parts for the Lodz textile cluster | V5 | margin | 3.2 | 5-15% | unverified (no Juki parts distributor named) | unverified (Lodz/Pabianice sewing workshops, not listed) |
| 11 | 87 | Ordering app between restaurants and their wholesalers | V5 | subscription (supplier pays) | 3.2 | 5-15% | Polish food wholesalers (none named; unverified) | unverified (direct sales to wholesalers) |
| 12 | 67 | Down-jacket repair and refill by post | V4 | service fee | 3.2 | 5-15% | unverified (no partner tailor named) | SEO on naprawa kurtki puchowej (V4-D03, 10 suggestions) |
| 13 | 72 | Car premium-audio module repair by post | V4 | service fee | 3.2 | 5-15% | UK and US module repair services (no Polish repairer found) | SEO on naprawa wzmacniacza Bose phrases (V4-D09, 10 suggestions) |
| 14 | 53 | Fishing subscription box for the PZW audience | V3 | subscription | 3.1 → **2.4** ([010](v3-hobby/010-fishing-subscription-box.md)) | 5-15% → **<5%** | unverified (no dropshipping lure wholesaler named) | PZW angler groups (about 500,000 members, V3 scan 6); channel unverified |
| 15 | 91 | Instant laser-cutting quote from a CAD file to local job shops | V5 | margin | 3.1 | 5-15% | unverified (5-10 laser-cutting shops, none named) | SEO on ciecie laserem na wymiar wycena online (V5 scan 9) |
| 16 | 37 | Rating-plate photo to part number, widget for appliance-parts shops | V2 | subscription | 3.1 | 5-15% | CzęściAGD.pl as a possible customer (unverified) | direct sales to appliance-parts shops (none contacted) |
| 17 | 85 | Hydraulic-seal matcher by profile and size | V5 | margin | 3.0 | 5-15% | RS PL distributor (shaft seals) | SEO on uszczelniacz hydrauliczny wymiar phrases (V5-D13, 10 suggestions) |
| 18 | 11 | Van-conversion component kits from DE/US makers | V1 | margin | 3.0 | 5-15% | Brandrup (DE) or Nomadic Supply (US); Reimo PL hinged only | SEO on zabudowa busa phrases (V1-D14, 1 suggestion only) |
| 19 | 65 | Mail-in smartwatch repair routed to partner technicians | V4 | service fee | 3.0 | 5-15% | one OLX technician (Lodz); iFixit parts abroad | SEO on naprawa zegarka Garmin / Huawei phrases (V4-D01, 10 suggestions) |
| 20 | 47 | Fishing-reel spare parts by exploded-diagram code | V3 | margin | 2.9 | 5-15% | Decathlon PL reel-parts category; private ads on Allegro Lokalnie | PZW anglers (about 500,000 members, V3 scan 6); channel inside PZW unverified |
| 21 | 69 | Post-warranty repair by post for robot and cordless vacuums | V4 | service fee | 2.9 | 5-15% | dysonserwis.pl and maker services; independent technicians unverified | SEO on naprawa Roborock po gwarancji (V4-D05, 5 suggestions) |
| 22 | 2 | Aftermarket cross-reference for Chinese-brand service parts | V1 | commission | 2.9 | 5-15% | unverified (no wholesaler stocks Jaecoo pads, V1 demand S5) | Chinese-brand owners' Facebook groups (V1 demand S3) |
| 23 | 58 | Available-now board for mated queen bees | V3 | lead fee | 2.9 | 5-15% | private breeders on OLX | SEO on matka pszczela od reki phrases (V3-D08, 10 suggestions) |
| 24 | 28 | Heat-pump installer comparison that files Czyste Powietrze paperwork | V2 | lead fee | 2.8 | 5-15% | installers with UDT / F-gas certificates (PORT PC guidance), none contacted | unverified (Enerad and Pompy.app already hold comparison traffic) |
| 25 | 50 | Model-kit price and stock comparison across Polish and nearby shops | V3 | commission | 2.8 | 5-15% | plastmodel.pl and other Polish shops (feed permission unverified) | IPMS Polska and modelling festivals (V3 scan 6); reach unverified |
| 26 | 30 | MVHR (rekuperator) filter subscription by unit model | V2 | subscription | 2.8 | <5% | unverified (Komfovent filters sold by >=4 shops on Ceneo; no dropship supplier named) | SEO on filtr do rekuperatora phrases (V2-D06, 10 suggestions) |

## Recurring and subscription ideas: why people keep paying

- **#24 Spare parts for distributor-only heat-pump brands, for installers** (margin): installers order parts at every repair, and a parts subscription is possible.
- **#19 Fitment data for Allegro and Shoper parts sellers** (subscription): sellers add listings every week and need fit data for each.
- **#87 Ordering app between restaurants and their wholesalers** (subscription (supplier pays)): restaurants order several times a week and suppliers pay monthly for clean orders.
- **#53 Fishing subscription box for the PZW audience** (subscription): anglers fish all season and a monthly box gives new lures without shop trips.
- **#37 Rating-plate photo to part number, widget for appliance-parts shops** (subscription): shops pay monthly for a widget that cuts wrong-part returns.
- **#2 Aftermarket cross-reference for Chinese-brand service parts** (commission): service parts (pads, filters) recur at each service.
- **#30 MVHR (rekuperator) filter subscription by unit model** (subscription): MVHR filters must be changed 2-4 times a year and owners forget the exact set.

Ideas marked "partly" in the CSV (#47, #52, #58, #67, #81, #84, #85, #91) have some repeat purchase but no subscription reason yet.

## Write-ups (T13, batch A)

Final scores from full write-ups replace the quick scores for these rows in [shortlist.csv](shortlist.csv) (new `writeup_path` column; `band_note` records the opportunity/risk rule). Ranks are kept from T12. 2026-11-06.

| # | Write-up | Quick → final weighted | Final band | Main reason for the change |
|---|---|---|---|---|
| 81 | [001 Catering-equipment parts](v5-small-business/001-catering-equipment-parts.md) | 3.5 → 2.8 | <5% | Gastroparts (Toruń, 80,000 parts, 24 h shipping) and GEV sell online in Polish: the T10 "foreign only" gap did not hold |
| 17 | [002 Body-damage photo quote](v1-vehicle/002-body-damage-photo-quote.md) | 3.5 → 2.9 | <5% | Fixico left the consumer model for fleets in 2016; ~PLN 12 fee per request after CAC |
| 52 | [003 3D-print instant quote](v3-hobby/003-3d-print-instant-quote.md) | 3.4 → 2.8 | <5% | Treatstock, Craftcloud and JLC3DP quote instantly (in English); commission per order below CAC |
| 36 | [004 Diagnosis then part](v2-home-appliance/004-diagnosis-then-part.md) | 3.4 → 2.8 | <5% | free help (elektroda.pl, AI assistants); Spareka relies on a French repair subsidy Poland lacks |
| 8 | [005 Camper habitation parts](v1-vehicle/005-camper-habitation-parts.md) | 3.3 → 3.0 | <5% | hardest parts are dealer-only at retail price; small seasonal owner base |

All five score in the `5–15%` range and drop one band on the opportunity/risk sums (criteria §4). None is killed outright; each has a ≤300 PLN validation test.

## Write-ups (T14, batch B)

The next five by quick score after batch A (ranks 6–9), plus #53 (rank 14) in place of ranks 10–13 so the batch has a hobby idea and a second subscription idea (task T14). Final scores replace the quick scores in [shortlist.csv](shortlist.csv), edited with the csv module as in T13. 2026-11-06.

| # | Write-up | Quick → final weighted | Final band | Main reason for the change |
|---|---|---|---|---|
| 24 | [006 Heat-pump parts for installers](v2-home-appliance/006-heat-pump-parts-for-installers.md) | 3.3 → 2.7 | <5% | Klima-Therm (Kaisai) sells parts in and after warranty through its own service desk, and CNC Pompy Ciepła runs a 1,000-item parts warehouse for major brands: a middleman adds a call, not a route |
| 33 | [007 Used washer modules](v2-home-appliance/007-used-washer-modules.md) | 3.3 → 2.7 | <5% | no listable supply of tested modules in Poland; ~PLN 10 commission per order; WEEE law limits dismantling to licensed plants. Spareka/ENVIE show the model works with a subsidised reuse network |
| 1 | [008 Chinese-brand collision parts](v1-vehicle/008-chinese-brand-collision-parts.md) | 3.2 → 2.7 | <5% (F8 knock-out) | importers hold body stock and built Polish warehouses (Duchnice, 20% late-part rebate); phone work per case breaks 40 h/month; added to [rejected.md](../rejected.md#t14--write-ups-batch-b-2026-11-06) |
| 19 | [009 Fitment data for parts sellers](v1-vehicle/009-fitment-data-for-parts-sellers.md) | 3.2 → 3.0 | <5% | Allegro's "Pasuje do" runs on TecDoc IDs and auto-fills from catalogue products; Ovoko syncs dismantlers to Allegro; best of the batch on score but Allegro can absorb it |
| 53 | [010 Fishing subscription box](v3-hobby/010-fishing-subscription-box.md) | 3.1 → 2.4 | <5% | Catch Co. (Mystery Tackle Box) assets bought by Gordon Brothers in 2024 after USD 56 m raised; ~PLN 9 gross profit per box before CAC; needs a shop that packs from its own stock |

All five end in `<5%`, like batch A. Finding that changes T10: Jaecoo 7 front pads (T10 V1 #1, N) are now sold by Inter Cars (PLN 229) and Iparts.pl (PLN 119) per Auto Świat, 8 June 2026 (noted in 008; affects #2, the T10 file is not edited).

## Review (T15, sceptical pass)

Each write-up gets **Devil's advocate** and **Review changes** sections (fresh findability queries, supplier terms, unit economics with sourced parcel prices, return rates and a Google Ads CPC-based CAC). Scores in [shortlist.csv](shortlist.csv) are updated for reviewed rows; the T13/T14 tables above keep their values. 2026-11-06.

| # | Write-up | Before → after T15 | Band after T15 | Main reason |
|---|---|---|---|---|
| 81 | [001](v5-small-business/001-catering-equipment-parts.md) | 2.79 → 2.64 | <5% | F4 3→2: at CPC PLN 2.5 and 2% conversion (CAC ~PLN 125) the first order loses ~PLN 53; Gastroparts shows only retail prices; REPA (ex-GEV) confirmed as Unox distributor for DACH, no public reseller terms |
| 17 | [002](v1-vehicle/002-body-damage-photo-quote.md) | 2.88 → 2.51 | **rejected** | Oferteo runs a multi-shop body-shop quote category; PZU and LINK4 already estimate damage from photos with AI; fee per request ~PLN 0 after CAC; moved to [rejected.md](../rejected.md#t15--independent-critical-review-2026-11-06) |
| 8 | [005](v1-vehicle/005-camper-habitation-parts.md) | 3.00 → 2.63 | <5% | Reimo PL delivers "only to Germany" and routes Poles to dealers; DE→PL parcel ~PLN 91–108 (DHL EU tariff) wipes the margin; window seals are findable at Reimo PL |
<!-- T15 rows end -->

## Caveats

- Scores of 4–5 rest on the T10 verdicts and scan rows linked in the CSV `evidence` column; F2 is never above 4 because no Polish search volume was verified (T09 used autocomplete only).
- Every supplier is unverified as to terms; none has been contacted. "unverified" in the supplier or channel column means the research files name none.
- T10 could not test Allegro (HTTP 403), so findability gaps are likely overstated.
