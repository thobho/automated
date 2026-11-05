# 021 — School licence for pedagodzy and psycholodzy szkolni

**One-liner:** A school-wide web tool for the school's specialists (pedagog, pedagog specjalny, psycholog, logopeda, terapeuta) that drafts the records of psychological-pedagogical help from their notes: WOPFU (wielospecjalistyczna ocena poziomu funkcjonowania ucznia) with every required element checked, opinions for a poradnia or a family court, the half-year review of help given, and the support records for the school's annual report; pseudonymised input, names restored in the browser. Paid by the school, not the teacher.
**Field:** education | **Type:** SaaS (web) | **B2B** (school / organ prowadzący) · shortlist id L128. Sister of [015](015-opinia-i-sprawozdanie.md) (B2C teacher version).

**Western analogues:**
- **Al-Muwajjih** (SA, 2025): counsellor records app with AI drafting, Saudi Education top-grossing #22 (catalogue R9-SA-012, 2026-11-01); the other Saudi and Turkish paperwork apps (Shawahid, Öğretmen Evrak) are template-based (TH36 check).
- **MagicSchool** (US): teacher co-pilot including IEP and report drafts; **US$45M Series B (2025-02)**, "10,000+ partner schools", moving to district procurement ([MagicSchool blog](https://www.magicschool.ai/blog-posts/series-b-fundraise-for-teacher-ai), via 015).
- No funded US startup focused on IEP or school-psychologist reports was found; Waypoint Learning ("AI operating system for special education") is early-stage with no round found (search excerpt, 2026-11-06).

**Spread:** TH36: TR, SA; general teacher co-pilots in US and globally. Mandated-record tools exist where a ministry prescribes formats. Narrow evidence (TH36 L2 ≤ 2 in T20).

**Does the Western leader already work in Poland?** No for this job. MagicSchool works in Polish for lessons (TH35 check) but knows US IEP law, not WOPFU/IPET rules; the Saudi/Turkish apps are tied to their ministries. **Google AI Pro for Education** (Gemini in Workspace) costs US$20–24 per user per month and is a general tool ([Google Workspace](https://knowledge.workspace.google.com/admin/generative-ai/workspace-with-gemini/ai-pro-for-education?hl=pl), accessed 2026-11-06). Not tried hands-on.

**Polish adaptation, i.e. the edge:**
- Rozporządzenie on psychological-pedagogical help and on special education: WOPFU and IPET required elements and timing (IPET within 30 days of filing the orzeczenie) ([ORKE guide 2026-06](https://orke.pl/app/uploads/2026/06/WOPFU-i-IPET-%E2%80%93-od-przepisow-prawa-do-praktycznej-realizacji.pdf), via TH36).
- **Standard zatrudnienia specjalistów** in the Karta Nauczyciela: at least 2 specialist FTE per school plus 0.2 per additional group of pupils, target values from 2024-09-01, with psychologists and special pedagogues ≥25% of specialist FTE in schools above 50 pupils ([gov.pl: standardy](https://www.gov.pl/web/nauka/przepisy-okreslajace-standardy-zatrudniania-nauczycieli-specjalistow), search excerpt, accessed 2026-11-06).
- Kuratorium inspections check these records: in 2026-04 an inspection found a school's IPET lacked legally required information and was undated ([Kuratorium Kielce](https://kuratorium.kielce.pl/wp-content/uploads/2026/04/informacja-o-wynikach-kontroli-szkola-podstawowa-nr-32-im.-janusza-kusocinskiego-w-kielcach.pdf)).
- Data lives in Librus/Vulcan (no API, M25/M26); RODO special-category data of children; opinions for family courts follow the court's request.

**Target customer in Poland:** schools and preschools. ~14 thousand primary schools and ~6.9 thousand secondary schools (2024/2025), 22.3 thousand preschool institutions (GUS data via press, [GUS Polska szkoła w liczbach 2024/2025](https://stat.gov.pl/dla-mediow/informacje-prasowe/polska-szkola-w-liczbach-jak-wyglada-edukacja-w-roku-szkolnym-20242025,36,1.html), search excerpt, accessed 2026-11-06). **Psychologist FTE in schools covered by the standard rose from 10,548 to 12,508 (+18.6%) in 2024/2025** (MEN answer to the Rzecznik Praw Dziecka, [brpd.gov.pl](https://brpd.gov.pl/wp-content/uploads/2025/01/Odpowiedz-MEN-na-wystapienie-RPD.docx), search excerpt). Buyer: director (budget from organ prowadzący); users: specialists. CEE: different school law per country.

**Demand driver:** social and regulatory. Pupils with an orzeczenie o potrzebie kształcenia specjalnego up ~30% over 15 years while pupil numbers fell ([gov.pl](https://www.gov.pl/web/nauka/rekordowe-srodki-na-wsparcie-psychologiczne-i-pedagogiczne-w-szkolach), via 015); child mental-health demand (DD4); MEN still reports psychologist shortages in 2025/2026 (prawo.pl, excerpt).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| **Smart IPET** (ePedagogika / Portal Oświatowy content) | IPET draft from WOPFU and team decisions, .doc export | Mini 890.03 PLN gross/year (1 user); **Pro 2,997.76 PLN gross/year (30 users per institution)** ([smartipet.pl](https://smartipet.pl/ipet-w-kilka-minut/), fetched 2026-11-06) | IPET only; no WOPFU, opinions or help reviews listed |
| Librus / Vulcan | e-dziennik with specialist journals | school subscription | records, no drafting |
| Training firms (ORKE, BUR courses) | WOPFU/IPET courses | 199 PLN per person (BUR, via TH36) | knowledge, not a tool |
| ChatGPT, Gemini (incl. Google AI Pro for Education) | drafts from notes | free / US$20–24 per user/month | no required-element checks; data risk |
| Template sites | Word "wzory" | free | no drafting |

**Evidence of Polish demand:** autocomplete "wopfu" → "wzór wypełniony", "przykład", "ile razy w roku"; "opinia o uczniu" → "do poradni", "do sądu rodzinnego przykład" (TH36, 2026-11-05). Schools pay Smart IPET for 30-user institutional packages (testimonials from directors and pedagogues, TH36). Webinars and courses on WOPFU run by teacher-training centres (search excerpts). No direct evidence that specialists ask for an AI WOPFU tool.

**MVP scope (≤6 weeks):**
1. WOPFU builder: specialists' notes per area (strengths, difficulties, environment, effects of help) → draft with every required element; missing-element checklist.
2. Opinia o uczniu (poradnia, sąd rodzinny, other school) and half-year help review templates.
3. Pseudonymisation in the browser; no server-side storage of drafts by default; DPA template for the school's IOD.
4. School admin: seats, audit of who generated what, .docx export to paste into Librus/Vulcan.
5. Tests: golden WOPFU inputs with expected section coverage; fixture checks that no name or PESEL reaches the LLM call.

**Monetization:** school licence 990 PLN net/year up to 10 specialists (≈82 PLN/month), 1,990 PLN for school complexes; invoice to the school, payment on 14-day terms. **Unit economics:** a WOPFU draft ≈ 15k input / 4k output tokens; a school writing ~200 documents a year ≈ 3M / 0.8M tokens ≈ US$3/year on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05); EU-hosted model at 3× price still < US$10. Gross margin >95% before support. **Customer count:** 10k PLN MRR ≈ 121 schools at 990 PLN/year; ~21k schools is >170×.

**Distribution, first 10 customers:** pedagogues' and psychologists' Facebook groups (free WOPFU checklist), school directors' groups, partnerships with poradnie psychologiczno-pedagogiczne trainers; upsell from 015 teacher users to their school.

**Regulation:** AI Act Annex III point 3 lists AI used to evaluate learning outcomes, determine access or the appropriate level of education, and monitor pupils ([Annex III](https://artificialintelligenceact.eu/annex/3/)). A WOPFU is an assessment of a pupil's functioning that feeds decisions on help, so a drafting tool sits close to point 3; the art. 6(3) exception for preparatory tasks with human authorship may apply (own reading, needs counsel). Design: the specialist writes and signs; the tool never scores or recommends a level. RODO: children's health data (art. 9), school as controller; EU hosting, no training on inputs.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | The specialist-employment standard puts ≥2 specialist FTE in every school, and psychologist FTE grew 18.6% in a year: a growing user base that owns this paperwork | H | M | ≥300 specialists download a free WOPFU checklist in a month |
| O2 | Schools already pay for institutional packages (Smart IPET Pro ~3,000 PLN/year), so a school budget line exists | M | M | 3 directors accept a paid pilot invoice |
| O3 | Kuratorium findings on incomplete IPET/WOPFU give directors a compliance reason | M | M | directors cite an inspection in sales calls |
| O4 | A school licence brings 015's teacher module into the same account | M | L | ≥20% of licensed schools activate teacher seats |
| O5 | More orzeczenia and mental-health referrals raise document volume each year | H | L | pilot schools write ≥50 records a year |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Smart IPET / Portal Oświatowy add WOPFU and opinions to the package schools already buy, with their content and trust | M | H | Smart IPET product page lists WOPFU |
| R2 | School purchasing is slow (director approval, organ prowadzący budget, dead summer), so 121 schools take far longer than a year | H | M | <5 paying schools by the end of the first term |
| R3 | Specialists keep using free ChatGPT/Gemini despite data guidance | H | M | trial users say "I do this in ChatGPT" |
| R4 | School IODs block a cloud LLM for children's health data, or the AI Act point-3 question scares directors | M | H | DPA negotiations stall in pilots |
| R5 | Librus or Vulcan add AI drafting inside the specialist journal | L | H | e-dziennik release notes mention AI drafting |

O sum 6+4+4+2+3 = 19; R sum 6+6+6+6+3 = 27. R − O = 8 → **down one band** (rule §4.3); no H×H risk.

**Success signals:**
- Western analogue durable signals: replaces specialist hours on mandated records (signal 1), recurring duty with an owner (signal 2), MagicSchool's move from teacher sign-ups to district contracts (expansion-like, no NRR; signal 4 not counted), Saudi/Turkish top-grossing ranks for record apps (signal 5, app store). Durability score ~3 → **unproven**.
- Hype warnings: none specific; TH36 evidence is narrow (two countries).
- Polish adaptation can reproduce: replaced spend = specialist hours and the school's subscription to model documents; first channel = specialists' Facebook groups and 015 users; retention driver = yearly WOPFU/IPET cycles and stored drafts per pupil.

**Graveyard:** none found for school-specialist paperwork tools.

**Scores (1–5):** L1 3 · L2 2 · L3 3 · L4 4 · L5 4 · L6 3 · L7 4 · L8 2 · L9 2 | **Weighted:** 3.1 / 5 | **Chance band:** score → 5–15%; O 19, R 27, R − O = 8 → **<5%**. The user base is sourced and growing (psychologist FTE +18.6%), the records are mandated and inspected, and schools already pay Smart IPET; but school buying is slow, free general assistants are the default, and the content owner (Portal Oświatowy) can extend Smart IPET to WOPFU.
Changes vs. quick score: none on the lenses (L5 4 now sourced with MEN FTE data); weighted 3.1 unchanged; band lowered by §4.

**Cheapest validation test (≤1 week, ≤200 PLN):** a free "WOPFU: required elements checklist + example" PDF promoted in 5 pedagogue/psychologist Facebook groups, with a sign-up for a school pilot; call 10 directors among sign-ups and ask for a paid pilot at 490 PLN for the rest of the school year.

**Kill criteria:** <100 checklist downloads; or <2 directors accept a paid pilot; or a school IOD rejects the data design.

**Confidence:** medium-low (rules, user counts and the incumbent's prices sourced; specialists' willingness to switch from ChatGPT and school buying speed not tested).

**Sources** (accessed 2026-11-06 unless noted):
1. https://www.magicschool.ai/blog-posts/series-b-fundraise-for-teacher-ai (accessed 2026-11-05)
2. https://knowledge.workspace.google.com/admin/generative-ai/workspace-with-gemini/ai-pro-for-education?hl=pl
3. https://orke.pl/app/uploads/2026/06/WOPFU-i-IPET-%E2%80%93-od-przepisow-prawa-do-praktycznej-realizacji.pdf (accessed 2026-11-05)
4. https://www.gov.pl/web/nauka/przepisy-okreslajace-standardy-zatrudniania-nauczycieli-specjalistow
5. https://kuratorium.kielce.pl/wp-content/uploads/2026/04/informacja-o-wynikach-kontroli-szkola-podstawowa-nr-32-im.-janusza-kusocinskiego-w-kielcach.pdf (accessed 2026-11-05)
6. https://stat.gov.pl/dla-mediow/informacje-prasowe/polska-szkola-w-liczbach-jak-wyglada-edukacja-w-roku-szkolnym-20242025,36,1.html
7. https://brpd.gov.pl/wp-content/uploads/2025/01/Odpowiedz-MEN-na-wystapienie-RPD.docx
8. https://www.gov.pl/web/nauka/rekordowe-srodki-na-wsparcie-psychologiczne-i-pedagogiczne-w-szkolach (accessed 2026-11-05)
9. https://smartipet.pl/ipet-w-kilka-minut/
10. https://openrouter.ai/google/gemini-2.5-flash (accessed 2026-11-05)
11. https://artificialintelligenceact.eu/annex/3/
12. Internal: [TH36 check](../../poland-check/C/TH36-teacher-school-paperwork.md), [015](015-opinia-i-sprawozdanie.md), R9 catalogue rows

Coverage: 5 web searches and 1 fetch for this write-up (specialist FTE counts, AI WOPFU tools and prices, school counts, IEP-AI startups, Smart IPET scope). Not found: any Polish AI WOPFU tool, a funded IEP/school-psychology report startup, the number of pedagogues (only psychologists' FTE).
