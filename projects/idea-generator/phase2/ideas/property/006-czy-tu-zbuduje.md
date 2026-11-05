# 006 — "Czy tu zbuduję?": parcel → plan ogólny / MPZP / WZ eligibility reader

**One-liner:** Enter a parcel id (or click the map); the tool says which plan ogólny zone and which MPZP apply, whether the plot lies in an obszar uzupełnienia zabudowy (so a WZ decision is possible where there is no MPZP), and extracts the binding parameters (use, max height, intensity, biologically active share, frontage) from the plan text, in plain Polish with links to the source resolution.
**Field:** property | **Type:** SaaS (web) | **B2C with B2B tier** (architects, small developers, agents) · shortlist id L092 (merges L090 plot-potential report for small developers)

**Western analogues:**
- **PermitFlow** (US, permitting agents for builders): **US$54M Series B (Dec 2025)** led by Accel, after a Series A in Feb 2024; reported total ~US$90M ([Built In](https://builtin.com/articles/ai-construction-platform-permitflow-secures-54m-series-b-20251203)). Its job is permit applications, a step after "can I build here?".
- **Archistar** (AU): automated zoning and building-code checks; A$6M round in 2021 ([Business News Australia](https://www.businessnewsaustralia.com/articles/property-and-planning-design-intelligence-venture-archistar-raises--6m-for-global-ambitions.html)); Austin, Texas contracted its AI platform for residential permit review ([BDC Network](https://www.bdcnetwork.com/codes-and-standards/news/55237400/austin-texas-adopts-ai-driven-building-permit-software)).
- **Propcorn** (AT), **GovWell** (US): named in TH58/TH57; traction not re-verified (unverified).
Most traction in this theme is on the **government** side (Austin) or on permits (PermitFlow), not on consumer site-feasibility reports.

**Spread:** TH58 private-side zoning/permit tools in US, AU, AT (R1, R3, R8). No CEE analogue in R6.

**Does the Western leader already work in Poland?** No. Archistar and PermitFlow are tied to their national codes and demo-led (not tried hands-on). The relevant comparison is Polish: see competition below, where free and cheap tools already cover much of the job.

**Polish adaptation, i.e. the edge:**
- **2023 planning reform:** each gmina must adopt a plan ogólny; WZ decisions only inside the obszar uzupełnienia zabudowy (OUZ) where there is no MPZP; existing MPZP stay in force. The deadline was 2026-08-31; **946 of ~2,479 gminas had adopted and published a plan ogólny by then**, 1,843 were at least at the consultation stage, 95 had not started; gminas without a plan lose KPO funds but WZ decisions continue on the old basis for now ([wartowiedziec.pl, Sejm committee 2026-09-03](https://wartowiedziec.pl/zarzadzanie-przestrzenia/81841-stan-uchwalania-planow-ogolnych-gmin-przedmiotem-obrad-sejmowej-komisji-samorzadu-terytorialnego-i-polityki-regionalnej)).
- **Plans ogólne are digital (GML)**, downloadable and shown on rejestrplanowogolnych.pl; zone parameters and OUZ are structured data ([e-mapa.net, plan ogólny Iława](https://e-mapa.net/plan_ogolny/280703-ilawa)). This makes the plan-ogólny half a **GIS job, not an LLM job**.
- **MPZP**: tens of thousands of older resolutions in PDF text with drawings, mixed quality, published in BIP and Dziennik Urzędowy ([M20](../../research/poland/local-moats.md)). Reading MPZP text for one parcel's parameters is the part that needs an LLM.
- Geoportal/ULDK parcel geometry (M28), TERYT.

**Target customer in Poland:**
- Plot buyers (DD9 suburban building); 545.8k notarial sale deeds of all property in 2024 ([GUS](https://stat.gov.pl/obszary-tematyczne/infrastruktura-komunalna-nieruchomosci/nieruchomosci-budynki-infrastruktura-komunalna/obrot-nieruchomosciami-w-2024-r-,4,22.html)); plot share not found.
- B2B: architects (feasibility before a design), small developers (L090), estate agents selling plots. Counts not sourced here.
- CEE: Czech územní plán differs; expansion is a new build.

**Demand driver:** regulatory and dated: plan ogólny adoptions through 2026–2027 change what can be built on many plots (OUZ limits WZ), so owners and buyers need to re-check. DD9 suburbanisation. Media coverage warns owners that gminas "will block thousands of houses" ([infor.pl](https://www.infor.pl/prawo/nowosci-prawne/7628484,gminy-zablokuja-budowe-tysiecy-domow-juz-31-sierpnia-2026-r-to-juz-ostatnia-szansa-dla-wlascicieli-nieruchomosci-na-wniosek-do-gminy.html)).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| e-mapa.net | per-gmina plan ogólny pages (zones, OUZ area, GML download); "Raport planistyczny" per plot | plan pages free; report ~20 PLN (excerpt, TH15) | does the plan-ogólny half already; MPZP parameter extraction not shown ([e-mapa.net](https://e-mapa.net/plan_ogolny/280703-ilawa)) |
| OnGeo Raport o terenie | automated plot report, 50+ pages of maps, MPZP name and number | point packages | non-LLM; parameters not extracted from text ([OnGeo blog](https://www.blog.ongeo.pl/jak-sprawdzic-czy-dzialka-jest-budowlana)) |
| LEX Budownictwo + Expert AI | MPZP compliance help for professionals | LEX subscription | professional, generic ([Wolters Kluwer](https://www.wolterskluwer.com/pl-pl/solutions/lex/mpzp)) |
| Geoportal, local SIP, wypis i wyrys from the gmina | free / small fee | — | raw data, user must read the resolution |
| Guides (Otodom, Pewny Lokal, rankomat) | how-to articles | free | no per-plot answer |

**Evidence of Polish demand:** many "jak sprawdzić czy działka jest budowlana" guides from portals and insurers (Otodom, OnGeo, rankomat, Link4) indicate search demand (volume not measured); "mapa mpzp" autocomplete returns 10 city variants (TH15). No evidence that people pay more than ~20 PLN for a plot report.

**MVP scope (≤6 weeks):**
1. Parcel lookup (ULDK) → intersect with plan ogólny GML (adopted gminas) → zone, OUZ yes/no, zone parameters.
2. MPZP layer: for 1–2 voivodeships, find the MPZP covering the parcel (national MPZP WMS/WFS where available), fetch the resolution PDF, LLM-extract the parameters for the parcel's teren symbol (e.g. 3MN) into JSON with page citations.
3. Plain-Polish answer page + PDF; flag "plan ogólny not yet adopted in this gmina" with the status.
4. Tests: 50 parcels with hand-checked parameters as golden files.

**Monetization:** 39 PLN per plot (B2C); 149 PLN/month for architects/agents (30 plots). Bundle with idea 001 (KW report) at 99 PLN per plot purchase.
**Unit economics:** an MPZP resolution ≈ 20–40 pages ≈ 30k tokens; extraction on Gemini 2.5 Flash (US$0.30/US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.015; cached per resolution, so repeat parcels cost ~0. Gross margin >90%. The cost is coverage work (finding each gmina's MPZP sources), not tokens. 10k PLN MRR = ~67 B2B seats or ~250 B2C reports/month.

**Distribution, first 10 customers:** SEO on "czy działka jest budowlana [gmina]" and "plan ogólny [gmina]" long-tail pages generated from GML (free data → programmatic SEO); architects' Facebook groups; agents selling plots in suburban rings around Warsaw, Kraków, Wrocław.

**Regulation:** AI Act: not high-risk ([AI Act Annex III](https://artificialintelligenceact.eu/annex/3/)). Liability: information only; courts stress the authority itself assesses MPZP compliance (TH58, [OnGeo blog](https://blog.ongeo.pl/uprawnienia-architekta-nie-decyduja-o-zgodnosci-projektu-z-mpzp)). Public data, no personal data beyond the user's account.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Programmatic SEO from free GML data captures "plan ogólny [gmina]" search traffic as more gminas adopt | M | M | pages rank top-10 within 3 months |
| O2 | Bundled with idea 001 into one plot-buyer report, raising price per purchase | H | M | bundle converts better than either alone |
| O3 | Architects pay monthly for MPZP parameter extraction across many plots | L | M | 3 architects in a pilot use it weekly |
| O4 | Gminas that miss the deadline adopt plans in 2027, renewing demand for re-checks | M | L | adoption counts rise in 2027 |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | e-mapa.net and OnGeo already cover the plan-ogólny half free or for ~20 PLN; price ceiling is low | H | H | testers say "e-mapa shows this" |
| R2 | MPZP extraction errors (drawings, amendments, partial annulments) lead to a wrong answer | M | H | golden-file accuracy <90% |
| R3 | e-mapa or OnGeo add LLM extraction of MPZP parameters | M | H | product updates |
| R4 | One-off B2C purchase, no retention | H | M | repeat rate ≈ 0 |
| R5 | National MPZP coverage data is patchy, so the product works only in some gminas | M | M | >30% of test parcels lack an MPZP source |

**Success signals:**
- Western analogue durable signals: PermitFlow replaces permit-expediter and consultant fees for builders (budget line) and raised repeatedly; Archistar won a city contract (government buyer). No retention data.
- Hype warnings: none serious; but traction is in permits and government review, not consumer feasibility.
- Polish adaptation can reproduce: replaced spend = a wypis i wyrys plus an architect's hour; first channel = programmatic SEO on free GML; retention driver = B2B only (architects, agents), weak.

**Graveyard:** none found in this pass (not searched separately). Warning case is local: e-mapa.net already monetises plot reports at ~20 PLN, which caps prices.

**Scores (1–5):** L1 3 · L2 2 · L3 3 · L4 4 · L5 3 · L6 2 · L7 3 · L8 3 · L9 2 | **Weighted:** 2.9 / 5 | **Chance band:** 5–15% (bottom edge). Plans ogólne are published as free GML and e-mapa.net already shows zones and OUZ per gmina, so the "reading resolutions by hand" gap from TH58 is mostly closed; the remaining LLM job is MPZP text extraction, sold at prices capped near 20–40 PLN. **Recommendation: do not build standalone; fold the MPZP-extraction module into idea 001 as a plot add-on.**
Changes vs. quick score: L1 4 → 3 (plan-ogólny part is GIS, not LLM), L3 4 → 3 (e-mapa covers plan ogólny and OUZ), L4 5 → 4 (data is public and structured), L6 3 → 2 (price ceiling), L9 3 → 2; L7 2 → 3 (GML is open and testable). Weighted 3.3 → 2.9.

**Cheapest validation test (≤1 week, ≤200 PLN):** take 30 parcels listed for sale on Otodom in 3 suburban gminas, run e-mapa.net/OnGeo on each and record what they miss (MPZP parameters); then post the 30 results as a free sample in a plot-buyers' Facebook group and ask for 39 PLN pre-orders. Cost ≤100 PLN.

**Kill criteria:** e-mapa/OnGeo already give the parameters for ≥25 of 30 parcels; or <3 pre-orders from the group post.

**Confidence:** medium (reform status and competition sourced; demand and willingness to pay not).

**Sources** (accessed 2026-11-05):
1. https://builtin.com/articles/ai-construction-platform-permitflow-secures-54m-series-b-20251203
2. https://www.businessnewsaustralia.com/articles/property-and-planning-design-intelligence-venture-archistar-raises--6m-for-global-ambitions.html
3. https://www.bdcnetwork.com/codes-and-standards/news/55237400/austin-texas-adopts-ai-driven-building-permit-software
4. https://wartowiedziec.pl/zarzadzanie-przestrzenia/81841-stan-uchwalania-planow-ogolnych-gmin-przedmiotem-obrad-sejmowej-komisji-samorzadu-terytorialnego-i-polityki-regionalnej
5. https://e-mapa.net/plan_ogolny/280703-ilawa
6. https://www.infor.pl/prawo/nowosci-prawne/7628484,gminy-zablokuja-budowe-tysiecy-domow-juz-31-sierpnia-2026-r-to-juz-ostatnia-szansa-dla-wlascicieli-nieruchomosci-na-wniosek-do-gminy.html
7. https://www.blog.ongeo.pl/jak-sprawdzic-czy-dzialka-jest-budowlana
8. https://blog.ongeo.pl/uprawnienia-architekta-nie-decyduja-o-zgodnosci-projektu-z-mpzp (TH58)
9. https://www.wolterskluwer.com/pl-pl/solutions/lex/mpzp (TH58)
10. https://stat.gov.pl/obszary-tematyczne/infrastruktura-komunalna-nieruchomosci/nieruchomosci-budynki-infrastruktura-komunalna/obrot-nieruchomosciami-w-2024-r-,4,22.html
11. https://openrouter.ai/google/gemini-2.5-flash
12. https://artificialintelligenceact.eu/annex/3/
13. Internal: [TH58 check](../../poland-check/C/TH58-government-back-office-ai.md), [TH15 check](../../poland-check/B/TH15-property-transaction-title-diligence.md), [write-up 001](001-kw-plot-risk-report.md)

Coverage: 5 web searches/fetches for this write-up (PermitFlow/Archistar, plan ogólny adoption count, Polish plot-check tools, e-mapa plan ogólny page, Sejm committee article). Not found: share of plot transactions in GUS data, counts of architects, any graveyard case.
