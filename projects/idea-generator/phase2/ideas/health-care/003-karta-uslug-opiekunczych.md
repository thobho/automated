# 003 — "Karta usług opiekuńczych": voice-to-task-card and settlement app for bon senioralny providers

**One-liner:** A carer dictates a short visit note in Polish or Ukrainian; the app maps it to the gmina's catalogue of care tasks, logs time and check-in, and produces the monthly hours settlement and report that the provider's contract with the gmina (bon senioralny, MOPS-contracted usługi opiekuńcze, Opieka 75+) requires.
**Field:** health-care (social care, non-medical) | **Type:** mobile app + web back office | **B2B** · shortlist id L115 (merges L116 provider-onboarding kit, L119 NGO programme-reporting assistant)

**Western analogues:**
- **Birdie** (UK, since 2017), home-care software with a carer app; US$11.5M Series A (2021) and US$30M Series B (2022, Sofina, Index, OMERS) to expand into continental Europe; 700+ UK care providers as customers per a jobs-board profile (unverified) ([PR Newswire](https://prnewswire.co.uk/news-releases/birdie-raises-30m-series-b-to-transform-elderly-care-at-home-864971599.html); [Welcome to the Jungle](https://app.welcometothejungle.com/companies/Birdie)). Launched an AI tool in 2026 that records assessment conversations and drafts care plans (jobs-board profile, unverified).
- **Cera** (UK), AI-led home-care **provider**, ~US$150M debt and equity in January 2025 ([Digital Health](https://digitalhealth.net/2025/01/cera-secures-more-than-123m-to-roll-out-ai-led-home-healthcare)); ~US$500M business with >US$100M from non-home-care lines (Oct 2025) ([HTWorld](https://www.htworld.co.uk/?p=45079)). Cera is a provider, not software, so it is evidence for the AI-in-home-care pattern rather than a product to copy.
- **Minikai** (AU, NDIS notes and reporting), **NAGARA** (JP kaigo records), **Zingage/Axle/Arya** (US Medicaid home care): named in TH04; traction not re-verified here (unverified).

**Spread:** TH04 appears in UK, US, AU, JP (R1, R2, R7, R8) since 2023 for the LLM layer; carer apps (Birdie) since 2017. Each analogue is built around its national funder. No CEE analogue in the R6 catalogue.

**Does the Western leader already work in Poland?** No. Birdie is UK-only in practice (no Polish site; its planned European expansion did not reach CEE as far as found). It was not tried: demo-led. Its data model follows English local-authority care plans and CQC rules; Minikai follows NDIS line items. None knows a gmina uchwała task catalogue or a bon senioralny umowa.

**Polish adaptation, i.e. the edge:**
- **Ustawa z 11 czerwca 2026 r. o osobach starszych i koordynacji opieki długoterminowej**, in force 2026-08-07: the gmina qualifies the senior and signs a contract with them on the scope and hours; services can be delivered by the gmina, the OPS or a firm/NGO chosen in a call ([Interia](https://wydarzenia.interia.pl/kraj/news-dodatkowe-wsparcie-dla-seniorow-prezydent-podpisal-ustawe,nId,23522112); [Gazeta Prawna](https://www.gazetaprawna.pl/wiadomosci/kraj/artykuly/11284301,bon-senioralny-2026-senior-podpisze-umowe-z-gmina-rzad-pokazal-jak-ma-dzialac-nowe-wsparcie.html)). Programme regulation: Dz.U. 2026 poz. 1277 on the Programme of Bon Senioralny 2026–2028 ([infor.pl](https://www.infor.pl/akt-prawny/DZU.2026.272.0001277,rozporzadzenie-rady-ministrow-w-sprawie-programu-bonu-senioralnego-na-lata-20262028.html)). **The settlement format between gmina and provider was not found** (an earlier draft spoke of cumulative settlements sent to the voivode; unverified).
- Per-gmina task catalogues and price per hour set in each gmina's uchwała on usługi opiekuńcze (ustawa o pomocy społecznej); Opieka 75+ and "usługi opiekuńcze dla osób niepełnosprawnych" programme reports (TH04).
- Carers are often 50+ women or Ukrainians: dictation in Polish and Ukrainian, offline use, cheap Android phones.
- RODO art. 9 health data about seniors.
A foreign vendor would have to learn ~2,500 gminas' contracting habits (TH04); that is the moat and also the cost.

**Target customer in Poland:**
- Private home-care agencies, NGOs and social co-operatives delivering MOPS-contracted care and, from Q4 2026, bon senioralny services; and OPS units delivering care themselves. Counts of such providers not found (unverified); the budget is 1 bn PLN for 2026–2028, 100 million PLN in 2026 (TH04).
- Buyer: owner/coordinator of an agency with 5–50 carers; for OPS: kierownik działu usług.
- Size of need: 7.9 million people 65+, only ~8 per 1,000 seniors get municipal home care (D13 in [demography.md](../../research/poland/demography.md)).
- CEE: Czech "pečovatelská služba" and Slovak systems are funded differently; expansion is a new build.

**Demand driver:** DD1 ageing (7.9M 65+), DD2 bon senioralny as a new public buyer of care hours from Q4 2026, D38 carers on the shortage list, DD6 Ukrainian carers. Regulatory, dated: law in force 2026-08-07, programme 2026–2028.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Generic ERP (Odoo partner blog in Polish) | visit tracking, rosters, billing | not stated | not care-specific, no voice, no gmina catalogues ([dasolo.ai](https://www.dasolo.ai/pl/blog/odoo-wed%C5%82ug-branzy-8/odoo-opiekunowie-harmonogramy-rozliczenia-698)) |
| Paper karty pracy + Excel | what MOPS and providers do today (NIK audit) | staff time | slow, error-prone settlements ([NIK](https://nik.gov.pl/kontrole/wyniki-kontroli-nik/pobierz,lki~p_15_044_201508260909101440580150~id2~01,typ,kj.pdf)) |
| "program komputerowy dla dps" legacy tools | DPS records | unknown | institutional care, not home care; vendors not identified |
| WhatsApp/Messenger groups + ChatGPT | coordinators use these informally (estimate, not sourced) | free | no structure, RODO risk |

**Evidence of Polish demand:** indirect. Autocomplete "usługi opiekuńcze program" returns the funding programmes, not software; "dokumentacja opiekuńcza" returns nothing (TH04, 2026-11-03). Heavy media coverage of bon senioralny (Gazeta Prawna has a tag page; consumer threads on pepper.pl about free care from October 2026) shows public interest on the demand side, not provider pain. No provider forum or job post about care documentation was found. This is the weakest part of the idea.

**MVP scope (≤6 weeks):**
1. Android app (React Native/PWA): carer list of visits, check-in/check-out, record a 30–60 s voice note.
2. Transcribe (PL/UA) → LLM maps the note to the gmina task catalogue (JSON) and flags missing tasks against the senior's contract.
3. Back office: catalogue import from the uchwała PDF (LLM-assisted, human-confirmed), per-senior contract hours, monthly settlement per gmina in its format (start with 2 gminas whose formats a pilot provider shares), PDF/XLSX export.
4. Tests: fixture voice notes with expected task JSON; settlement golden files.

**Monetization:** 25 PLN per active carer per month (min. 99 PLN per provider); onboarding of a new gmina format 299 PLN one-off. Payer: the provider (its gmina contract pays per hour; the tool saves coordinator hours and settlement corrections).
**Unit economics:** a carer with ~60 visits/month × 1 min audio = 60 min. gpt-4o-mini-transcribe at US$0.003/min ([OpenAI pricing](https://developers.openai.com/api/docs/pricing), accessed 2026-11-05) → US$0.18; mapping 60 notes × ~3k tokens on Gemini 2.5 Flash (US$0.30/US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash)) → ~US$0.10. Total ≈ US$0.30 ≈ 1.2 PLN per carer per month vs. 25 PLN price; with hosting, SMS/push and payment fees, gross margin ~85–90% (estimate). The constraint is price sensitivity: 10k PLN MRR = 400 paid carers, i.e. ~20–40 providers.

**Distribution, first 10 customers:** (1) providers selected in the first bon senioralny calls: gminas publish nabory and results in BIP, giving a named list; (2) NGO channels: ngo.pl, regional ROPS/OWES support centres for social economy; (3) one pilot with a Warsaw or Kraków home-care agency, free for 3 months in exchange for its gmina formats.

**Regulation:** AI Act: not high-risk; no decision about eligibility for public assistance is made by the tool (Annex III point 5(a) covers systems used by public authorities to evaluate eligibility) ([AI Act Annex III](https://artificialintelligenceact.eu/annex/3/)); if sold to OPS, keep eligibility out of scope. Not a medical device: records non-medical care tasks; avoid clinical advice (MDR). RODO: art. 9 health data; DPA with provider, EU hosting, audio deleted after transcription.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Bon senioralny creates many new small providers that need a settlement tool from day one | M | H | gmina BIP calls show ≥5 new private providers per large city |
| O2 | Each mapped gmina catalogue is reusable for all providers in that gmina (data lock-in) | H | M | second provider in the same gmina onboards in <1 hour |
| O3 | OPS units buy it for their own carers (larger contracts, slower sale) | L | H | an OPS asks for a quote |
| O4 | Family-facing visit summary becomes a selling point for private-pay clients | M | M | providers forward summaries to families |
| O5 | Programme extended beyond 2028 or budget raised | M | M | government statements on 2029 budget |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Providers are thin-margin NGOs and micro-firms; 25 PLN per carer is too much | H | H | pilot providers ask for free use beyond 3 months |
| R2 | Bon senioralny rolls out slowly (100 million PLN in 2026), mostly delivered by OPS itself | M | H | first nabory show few external providers |
| R3 | Gminas demand settlement on their own paper forms; no digital format to target | M | M | pilot gminas reject PDF exports |
| R4 | Carers don't use the app (age, phone skills) | M | H | <60% of visits with a note in pilot month |
| R5 | A social-assistance software vendor used by OPS adds a provider module | L | M | vendor announcement |
| R6 | RODO complaint over audio of seniors | L | M | any family objection |

**Success signals:**
- Western analogue durable signals: Birdie has hundreds of UK provider customers and raised two rounds (expansion signal; unverified customer count), replaces paper care records and office admin; Cera shows the care-provider market pays for AI-led operations at scale. Hard-to-absorb: tied to funder rules (local authority, NDIS). No public retention or NRR.
- Hype warnings: none found; but no Birdie funding after 2022 was found, so growth may have slowed (unverified).
- Polish adaptation can reproduce: replaced spend = coordinator hours on monthly settlement and correction of rejected invoices; first channel = BIP lists of selected providers + NGO support centres; retention driver = per-gmina catalogue and contract data, plus monthly settlement cadence.

**Graveyard:** HomeHero (US home-care marketplace) raised ~US$23M and closed in 2017 (secondary source: [ideaproof.io](https://ideaproof.io/failure/homehero)); the lesson commonly drawn is that running the care supply itself is operations-heavy. Stay software for providers, not a marketplace for carers. No Polish failure found.

**Scores (1–5):** L1 4 · L2 3 · L3 4 · L4 4 · L5 4 · L6 2 · L7 3 · L8 3 · L9 3 | **Weighted:** 3.4 / 5 | **Chance band:** 5–15%. The driver is real and dated (law in force 2026-08-07, 1 bn PLN programme), there is no competitor, and token costs are tiny. But providers are poor, settlement formats are unknown until a pilot, and reaching 400 paying carers in 12 months needs a rollout that may be slow; this sits at the low end of 5–15%.
Quick scores confirmed. L5 stays 4 on sourced size + driver, though direct provider-side demand evidence is missing (would be 3 by a strict reading).

**Cheapest validation test (≤1 week, ≤200 PLN):** find 20 providers named in gmina bon senioralny or usługi opiekuńcze calls (BIP) in 3 large cities, phone the coordinators: "how do you settle hours with the gmina, how long does it take, would you pay 25 PLN per carer for automatic settlement?" Ask 3 of them for a blank settlement form. Cost: phone time only.

**Kill criteria:** fewer than 5 of 20 coordinators report >4 hours per month on settlement; or none would pay ≥15 PLN per carer; or the first gmina calls show OPS delivering >80% of hours themselves.

**Confidence:** low–medium (law and budget sourced; settlement formats, provider counts and willingness to pay not).

**Sources** (accessed 2026-11-05 unless noted):
1. https://prnewswire.co.uk/news-releases/birdie-raises-30m-series-b-to-transform-elderly-care-at-home-864971599.html
2. https://app.welcometothejungle.com/companies/Birdie
3. https://digitalhealth.net/2025/01/cera-secures-more-than-123m-to-roll-out-ai-led-home-healthcare
4. https://www.htworld.co.uk/?p=45079
5. https://wydarzenia.interia.pl/kraj/news-dodatkowe-wsparcie-dla-seniorow-prezydent-podpisal-ustawe,nId,23522112
6. https://www.gazetaprawna.pl/wiadomosci/kraj/artykuly/11284301,bon-senioralny-2026-senior-podpisze-umowe-z-gmina-rzad-pokazal-jak-ma-dzialac-nowe-wsparcie.html
7. https://www.infor.pl/akt-prawny/DZU.2026.272.0001277,rozporzadzenie-rady-ministrow-w-sprawie-programu-bonu-senioralnego-na-lata-20262028.html
8. https://www.dasolo.ai/pl/blog/odoo-wed%C5%82ug-branzy-8/odoo-opiekunowie-harmonogramy-rozliczenia-698 (2026-11-03, TH04)
9. https://nik.gov.pl/kontrole/wyniki-kontroli-nik/pobierz,lki~p_15_044_201508260909101440580150~id2~01,typ,kj.pdf (2026-11-03, TH04)
10. https://developers.openai.com/api/docs/pricing
11. https://openrouter.ai/google/gemini-2.5-flash
12. https://artificialintelligenceact.eu/annex/3/
13. https://ideaproof.io/failure/homehero
14. Internal: [TH04 check](../../poland-check/A/TH04-care-provider-documentation-operations.md), [demography DD1/DD2/DD6](../../research/poland/demography.md)

Coverage: 5 web searches/fetches for this write-up (bon senioralny law status, Cera, Birdie, home-care graveyard, transcription prices). Not found: the gmina–provider settlement format, number of bon senioralny providers, any Polish provider forum discussing documentation.
