# 005 — "AI biuro zarządcy" for zarządcy wspólnot mieszkaniowych

**One-liner:** An inbox (and later phone) agent for property-management firms running 20–200 wspólnoty mieszkaniowe: it answers owners about balances and zaliczki from the manager's accounting exports, routes awarie to contractors, drafts uchwały and the protokół, and counts written votes weighted by udziały.
**Field:** property | **Type:** SaaS (web + email/phone integration) | **B2B** · shortlist id L083 (merges L084 meeting recorder → protokół, L085 media-settlement explainer, L086 defects agent for new estates)

**Western analogues:**
- **EliseAI** (US, multifamily rental): AI leasing and resident-communication agents; **US$250M Series E at US$2.2B valuation (Aug 2025)** led by a16z, with Bessemer and Sapphire ([SiliconANGLE](https://siliconangle.com/2025/08/20/property-management-startup-eliseai-nabs-250m-2-2b-valuation/)); a later US$350M round at ~US$4B was reported ([Dealroom news](https://dealroom.co/news/157636-eliseai-raises-350m-at-4b-valuation-to-push-ai-deeper-into-housing/); not checked against a primary source).
- **Buena** (DE, Berlin): AI-assisted property manager; **Re-Leased/Credia** (NZ), **RentBetter** (AU), **Dwelly** (UK), **Vessla** (SE): named in TH56; traction not re-verified here (unverified).
Note: EliseAI's customers are US rental landlords (leasing, rent, maintenance). Polish wspólnoty are owner-occupied condominiums; the closer analogue is a German WEG-Verwaltung (Buena) or US HOA management, for which no strong AI traction was found.

**Spread:** TH56 in US, DE, NZ, AU, UK, SE (R1, R2, R3, R4, R8): broad. The condominium-manager variant specifically is evidenced only in DE (Buena).

**Does the Western leader already work in Poland?** No. EliseAI is US-only and demo-led; Buena is itself a Berlin manager, not software sold abroad (TH56). Neither was tried hands-on. Neither knows ustawa o własności lokali, udziały-weighted votes or Polish media settlements.

**Polish adaptation, i.e. the edge:**
- **Ustawa o własności lokali:** uchwały adopted at a meeting or by indywidualne zbieranie głosów, votes weighted by udziały, zaliczki on costs of the common property, annual sprawozdanie and plan gospodarczy (TH56).
- **Media settlements** (heat-cost allocators, water) and the accounting/back-office software the manager already uses: Lokale, S.Bit (job-ad skills, TH56), MMSoft with the **LokaleNet** resident app, Mieszczanin's **e-kartoteka** portal.
- Owner payments via BLIK/Przelewy24 and bank transfers ([M32, M33](../../research/poland/local-moats.md)); KW lookups for owner lists (M27).
- Polish manager practice: the state licence was abolished but managers carry liability insurance (TH56).

**Target customer in Poland:**
- Property-management firms (zarządcy nieruchomości) handling wspólnoty; count not found (unverified).
- Size of the underlying stock: ~2.97 million flats were in wspólnoty mieszkaniowe in 2018 per a GUS table cited in a secondary summary (unverified against GUS; search summary); total stock 16.2 million dwellings at end-2025 ([bank.pl on GUS](https://bank.pl/zasoby-mieszkaniowe-wzrosly-do-162-mln-mieszkan-na-koniec-2025-roku-dane-gus/), accessed 2026-11-05). 208k completions in 2025 (DD10) add new wspólnoty every year.
- Buyer: owner of a management firm; user: administrator and the wspólnoty accountant (job posts "księgowa ds. wspólnot mieszkaniowych" in Kraków, Warsaw, Wrocław, Sosnowiec; TH56).
- CEE: Czech SVJ (společenství vlastníků jednotek) are a close equivalent; expansion needs a new law pack (medium).

**Demand driver:** DD10 housing completions (new wspólnoty), DD9 suburban estates; labour: managers report labour-intensive back offices (job posts). No regulatory trigger found.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Mieszczanin e-kartoteka | resident portal + app: balances, fee lists, media settlements, messages to manager, faults, uchwały, surveys | free for residents; manager price not found | no AI, answers come from people; app rated 2.6 from 5 ratings ([App Store](https://apps.apple.com/app/id1440618758)) |
| MMSoft LokaleNet | resident app for MMSoft users; voting on uchwały in-app, faults, meter readings | not found | no AI; tied to MMSoft ([App Store](https://apps.apple.com/app/id1670413194)) |
| Lokale, S.Bit | desktop accounting and media settlements | not found | back office only ([pracuj.pl ad](https://www.pracuj.pl/praca/specjalista-specjalistka-ds-rozliczen-mediow-warszawa-begonii-9,oferta,1002572495)) |
| ChatGPT + courses | managers taught to use ChatGPT; PARP-listed course at up to 10,000 PLN | 1,690–10,000 PLN per course | improvised ([PARP BUR](https://uslugirozwojowe.parp.gov.pl/wyszukiwarka/uslugi/drukuj-pdf?id=3561507)) |
**Correction to TH56:** resident portals with e-voting (e-kartoteka, LokaleNet) do exist; they have no AI. The gap is therefore **partial**, not open: the incumbents own the data and the resident channel and could add an AI layer.

**Evidence of Polish demand:** thin. Autocomplete "zarządca nieruchomości program" and "ai zarządzanie najmem" → none (TH56). Positive: job posts for wspólnoty accountants and media-settlement specialists (paid job step), paid AI courses for managers (willingness to spend on AI skills). No forum quotes collected.

**MVP scope (≤6 weeks):**
1. Import: CSV/XLSX exports from Lokale or S.Bit (balances, zaliczki, lokal → udział), contractor list per building.
2. Shared inbox agent (IMAP/Gmail/Outlook): classifies owner emails (balance, fault, document request, complaint), drafts replies with the owner's numbers, routes faults to the contractor with a ticket; the administrator approves.
3. Uchwała drafter + written-vote counter: generates the uchwała and voting card, tallies returned cards by udziały, produces the result notice.
4. Protokół from meeting audio (L084): transcription + uchwały list.
5. Tests: fixture exports and emails with expected answers; vote tallies as golden files.

**Monetization:** 1.5 PLN per lokal per month (a manager with 3,000 lokale pays 4,500 PLN/month; a small one with 500 lokale 750 PLN); minimum 299 PLN/month. Payer: the manager (cost of administrator hours); possibly re-billed to wspólnoty.
**Unit economics:** assume 0.3 emails per lokal per month, ~4k tokens each on Gemini 2.5 Flash (US$0.30/US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.002 per email → <0.01 PLN per lokal; meeting transcription 2 h × US$0.003/min ([OpenAI pricing](https://developers.openai.com/api/docs/pricing)) ≈ US$0.36 per meeting. Token cost <2% of revenue; gross margin >90% before support. 10k PLN MRR ≈ 7,000 lokale ≈ 3–10 firms.

**Distribution, first 10 customers:** outbound to management firms found via city searches and Panorama Firm; managers' associations and Facebook groups (names unverified); partnering with a Lokale/S.Bit reseller is possible but conflicts with vendors' own portals. Offer: inbox triage free for one month for 1 building group.

**Regulation:** AI Act: not high-risk; transparency (owners must know they are talking to an AI) ([AI Act Annex III](https://artificialintelligenceact.eu/annex/3/)). RODO: owners' names, balances, debts; manager is controller, product is processor; EU hosting. Uchwały validity rests with the wspólnota; the tool drafts and counts, the manager certifies.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Per-lokal pricing scales well: a few mid-size managers reach 10k PLN MRR | M | H | one pilot firm with ≥2,000 lokale converts |
| O2 | Written-vote counting by udziały saves days per uchwała; strong wedge | M | M | managers say voting rounds take ≥1 week of admin |
| O3 | New-estate defects agent (L086) sells to developers' after-sales teams too | L | M | a developer asks for it |
| O4 | Media-settlement explainer (L085) reduces annual complaint peaks | M | M | complaint volume data from a pilot |
| O5 | A legacy vendor (Mieszczanin, MMSoft) partners or acquires instead of building | L | H | vendor responds to partnership email |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Incumbent portal vendors add an AI assistant on their own data | M | H | AI features announced by e-kartoteka or LokaleNet |
| R2 | Export access: managers can't or won't export data regularly from Lokale/S.Bit | M | H | pilots fail to send a second export |
| R3 | Managers are conservative and phone-first; low adoption of a new inbox | M | M | administrators bypass the tool |
| R4 | Owners distrust AI answers about money; complaints to wspólnota boards | L | M | first complaint in pilot |
| R5 | Demand weaker than assumed; little budget in small firms | M | H | <3 of 30 firms agree to a call |
| R6 | Wrong vote tally invalidates an uchwała (court challenge) | L | H | any disputed tally |

**Success signals:**
- Western analogue durable signals: EliseAI replaces leasing-agent and resident-service hours (budget line: on-site staff); expansion to new verticals (healthcare) and repeated large rounds; per-unit pricing. Hard to absorb: integrations with property-management systems. No public NRR (unverified).
- Hype warnings: none found; valuation jumps within weeks suggest investor heat rather than evidence.
- Polish adaptation can reproduce: replaced spend = administrator and accountant hours on owner emails, votes and protokoły; first channel = outbound to management firms; retention driver = per-lokal data, contractor routing and vote history.

**Graveyard:** no failed property-management AI found in this pass (one search); not researched further. The relevant warning is incumbents: in PL the resident channel is already owned by legacy vendors.

**Scores (1–5):** L1 4 · L2 3 · L3 3 · L4 4 · L5 3 · L6 3 · L7 3 · L8 3 · L9 2 | **Weighted:** 3.2 / 5 | **Chance band:** 5–15%. Per-lokal pricing makes 10k PLN MRR reachable with a handful of firms and token costs are negligible, but incumbent portal vendors (e-kartoteka, LokaleNet) already sit on the data and the resident channel, and demand evidence is limited to job ads.
Changes vs. quick score: L3 4 → 3 (resident portals with e-voting found; gap partial); L9 3 → 2 (incumbents can add the AI layer on their own data). Weighted 3.4 → 3.2.

**Cheapest validation test (≤1 week, ≤200 PLN):** call 30 management firms in two cities; ask: how many owner emails per month, how long a written-vote round takes, which software, whether they can export. Offer a free 1-month inbox pilot to the 3 most interested. Cost: phone time.

**Kill criteria:** <5 of 30 firms report >100 owner emails/month or >3 days per vote round; or none can export data; or a legacy vendor announces an AI assistant before the pilot ends.

**Confidence:** low–medium (law and Polish incumbents sourced; demand and export access untested).

**Sources** (accessed 2026-11-05 unless noted):
1. https://siliconangle.com/2025/08/20/property-management-startup-eliseai-nabs-250m-2-2b-valuation/
2. https://dealroom.co/news/157636-eliseai-raises-350m-at-4b-valuation-to-push-ai-deeper-into-housing/
3. https://apps.apple.com/app/id1440618758
4. https://apps.apple.com/app/id1670413194
5. https://www.pracuj.pl/praca/specjalista-specjalistka-ds-rozliczen-mediow-warszawa-begonii-9,oferta,1002572495 (2026-11-03, TH56)
6. https://uslugirozwojowe.parp.gov.pl/wyszukiwarka/uslugi/drukuj-pdf?id=3561507 (2026-11-03, TH56)
7. https://bank.pl/zasoby-mieszkaniowe-wzrosly-do-162-mln-mieszkan-na-koniec-2025-roku-dane-gus/
8. https://openrouter.ai/google/gemini-2.5-flash
9. https://developers.openai.com/api/docs/pricing
10. https://artificialintelligenceact.eu/annex/3/
11. Internal: [TH56 check](../../poland-check/A/TH56-leasing-property-management-agents.md), [local-moats](../../research/poland/local-moats.md), [demography DD9/DD10](../../research/poland/demography.md)

Coverage: 4 web searches/fetches for this write-up (Polish manager/resident apps, EliseAI/Buena funding, number of wspólnoty, e-kartoteka App Store page). Not found: number of management firms, number of wspólnoty (only flats in wspólnoty, 2018), Buena funding, prices of e-kartoteka/LokaleNet for managers, any graveyard case.
