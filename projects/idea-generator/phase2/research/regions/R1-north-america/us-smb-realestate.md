# United States: SMB services, real estate, logistics and auto (T05)

Part of the US scan; index in [united-states.md](united-states.md). All sources accessed **2026-11-01**. "Read" = page opened; "excerpt" = search-engine summary only (unverified).

## Findings

| # | Product | What it does | Traction (date) | Source | Polish angle |
|---|---|---|---|---|---|
| US-S01 | **Netic** | Autonomous workflows for roofing, plumbing, HVAC: calls, texts, chat, lead qualification, booking; weather-driven demand campaigns | Series B 23M USD (Founders Fund), 2025-11 (read); Series A 20M USD 2025-06 (excerpt) | [Roofing Contractor](https://roofingcontractor.com/articles/101559-netic-ai-for-roofing-receives-23m-in-series-b-funding) | instalatorzy (pompy ciepła, fotowoltaika, HVAC): missed-call booking + Czyste Powietrze paperwork (see autarc R0) |
| US-S02 | **Avoca** | AI CSR for service businesses: inbound calls 24/7, scheduling, speed-to-lead, Google LSA and ServiceTitan integrations | >125M USD total at 1B USD valuation, Series B 2026-04 (read); 800+ customers (excerpt) | [Avoca blog](https://www.avoca.ai/blog/avoca-raises-125m-series-b-1b-valuation) | as Netic; Polish field-service tools are fragmented (no ServiceTitan) |
| US-S03 | **Probook** | "AI dispatcher" for home services | 40M USD (34M Series A a16z + 6M seed Sequoia), 2026-06 (excerpt) | [Fortune](https://fortune.com/2026/06/23/exclusive-this-startup-wants-to-be-the-ai-brain-for-home-services-and-it-just-raised-40-million-from-sequoia-and-a16z/) | dispatch for service firms (serwis kotłów, klimatyzacji) |
| US-S04 | **Broccoli AI** | AI customer-service rep for home services | Series A 25M USD (Khosla); revenue ~20x in 2025 (excerpt; date unclear) | [YC page](https://ycombinator.com/companies/broccoli-ai) | as Netic |
| US-S05 | **Toma** | Voice agents answering all car-dealership calls: service booking, recalls, parts, sales questions | 17M USD led by a16z, 2025-06; "millions of call minutes" (read). Home page title on 2026-11-01 reads "The Job Board for Agents" (possible repositioning, unverified) | [Auto Remarketing](https://www.autoremarketing.com/retail/toma-secures-17-million-in-funding-to-build-ai-agents-for-dealerships/) | Polish dealer service departments (ASO) phone queues |
| US-S06 | **Slang.ai** | Voice "superhost" answering restaurant phones (reservations, questions) | 20M USD, 2023-06 (excerpt) | [Voicebot.ai](https://voicebot.ai/2023/06/27/generative-ai-voice-startup-slang-ai-raises-20m-to-answer-phones-at-restaurants-and-retailers/embed/) | restaurants: Polish market served by booking apps; weak |
| US-S07 | **FleetWorks** | AI agents (voice + email) matching truckers with loads for freight brokers | Series A 17M USD (First Round), 2025-10 (excerpt) | [Seedtable](https://seedtable.com/companies/fleetworks/funding-rounds/series-a-2025-10) | Polish spedycja is Europe's largest road-freight sector: carrier calls on Trans.eu/Timocom loads |
| US-S08 | **HappyRobot** | AI voice/communication agents for freight brokers, 3PLs, warehouses | Series A 15.6M USD (a16z), 2024-12 (excerpt) | [DC Velocity](https://www.dcvelocity.com/happyrobot-lands-15-6-million-backing-for-its-agentic-ai) | as FleetWorks; Cargofy (Ukraine origin) already sells AI freight agents in Europe — entry risk |
| US-R01 | **HouseWhisper** | AI assistant for real-estate agents: CRM updates, follow-ups, scheduling, transaction chasing via text/calls | Seed 6.7M USD (Mayfield), 2025-02; HQ Seattle (read) | [The SaaS News](https://www.thesaasnews.com/news/housewhisper-raises-6-7m-in-seed-round) | pośrednicy nieruchomości: Otodom/OLX lead follow-up, umowa pośrednictwa, księgi wieczyste checks |
| US-R02 | **MaxHome.AI** | Transaction coordination, compliance and back office for residential brokerages | Seed 5M USD (Fika), total 7M USD, 2025 (excerpt) | [Techleap feed](https://finder.techleap.nl/news/feed/maxhome-ai-secures-5m-seed-funding) | transaction checklist: KW, wypis z MPZP, zaświadczenia, akt notarialny prep |
| US-R03 | **Nurture Boss** | AI leasing for multifamily | Series A 4.025M USD (excerpt; date unclear) | [Multifamily Executive](https://www.multifamilyexecutive.com/technology/nurture-boss-secures-4m-series-a-funding-to-advance-ai-driven-leasing-solutions_o) | PRS/najem instytucjonalny operators in PL (growing), short-term rental managers |
| US-R04 | **Findigs** | AI-native rental decisioning / resident screening | Series C 32M USD (excerpt; date unclear) | [Multifamily Executive roundup](https://www.multifamilyexecutive.com/index.php/technology/proptech-roundup-funding-rounds-ai-leasing-tools-and-new-integrations) | tenant screening: BIK/KRD consent flows (RODO-sensitive; credit-like scoring is AI Act high-risk if it is creditworthiness) |

**Also in R0 (US SMB/real estate), not re-catalogued:** EliseAI (R0-US-041), Handoff (R0-US-098), Domu (R0-US-061), Retell AI (R0-US-060), Uplane (R0-US-076), OffDeal (R0-US-077).

## Patterns
1. **Home-services front office is the biggest SMB vertical-AI bet of 2025–26**: Avoca (1B USD valuation), Netic, Probook, Broccoli, plus Handoff (R0) for estimates. The pitch is missed calls = lost jobs (durable signal 1: replaces CSR/dispatcher hours). Poland has the demand (heat-pump and PV installers, labour shortage) but fragmented field-service software; the moat is integrations and subsidy paperwork, not voice.
2. **Voice agents per vertical** (dealerships, restaurants, freight) repeat the R0 finding: the voice layer is commodity; value sits in the vertical system integration (DMS, ServiceTitan, TMS).
3. **Freight brokerage** (FleetWorks, HappyRobot) is a direct fit for Poland's large spedycja sector, but a European entrant (Cargofy) is already there.
4. **Real-estate agent assistants** (HouseWhisper, MaxHome) are small seed rounds; Polish transactions run through notaries, so the transferable piece is document collection (KW, MPZP).

## Coverage
- Products: 12 new + 6 R0 overlaps. Sources read: 5 pages; 7 rows rest on excerpts (marked).
- Searches run: 6 (property-management AI; home-services AI; Netic/Avoca; restaurant and dealership voice; freight brokerage AI; real-estate transaction AI).
- Found nothing: AI mortgage-processing rounds (search returned none); Acrely (now redirects to another brand) and Indigo (domain belongs to an Italian company) not catalogued.
