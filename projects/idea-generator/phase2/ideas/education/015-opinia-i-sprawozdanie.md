# 015 — Opinia i sprawozdanie w 10 minut (school paperwork drafts for teachers)

**One-liner:** A web app where a teacher, wychowawca or specialist fills a short guided form about a pupil or a class (observations in bullet points, no names) and gets a Polish draft of the record schools ask for most: *opinia o uczniu* (variants for a poradnia psychologiczno-pedagogiczna, a family court, another school), *sprawozdanie nauczyciela wspomagającego* and the half-year or year-end *sprawozdanie z pracy*, with the sections the school's procedure requires checked and pseudonymised input (the name is added back only in the browser). The awans-plan module of the merged L127 is dropped (see below).
**Field:** education | **Type:** SaaS (web) | **B2C** (teacher pays; later a school licence) · shortlist id L126 (merges L127)

**Western analogues:**
- **Öğretmen Evrak** (TR, 2021): generates personalised teacher paperwork (BEP plans, candidate-teacher file, annual plans) from templates; Turkey App Store top-grossing Education #20, 5,606 ratings, 4.6 stars (2026-11-01, [App Store](https://apps.apple.com/tr/app/%C3%B6%C4%9Fretmen-evrak/id1520664624), catalogue R9-TR-005). Template-based, not LLM.
- **Shawahid**, **Al-Mu'allim Al-Dhaki**, **Al-Muwajjih** (SA, 2025): teacher evidence reports, class records, counsellor records; Saudi Education top-grossing #3, #16, #22 (catalogue R9-SA-010…012). Only Al-Muwajjih drafts records with AI.
- **MagicSchool** (US, 2023): teacher co-pilot including IEP and report drafts; **US$45M Series B led by Valor (2025-02)**, "10,000+ partner schools", moving from teacher sign-ups to district procurement ([MagicSchool blog](https://www.magicschool.ai/blog-posts/series-b-fundraise-for-teacher-ai)). Broad, not paperwork-specific.

**Spread:** TH36 teacher paperwork: TR, SA (catalogue); MagicSchool-type co-pilots US and global. Mandated-record apps appear only where the ministry prescribes formats. TH36 carries a hype/narrow-evidence warning (L2 ≤ 2, shortlist-notes).

**Does the Western leader already work in Poland?** Öğretmen Evrak and the Saudi apps are Turkish/Arabic and tied to MEB/Noor formats: no. MagicSchool works in Polish for lessons (TH35 check) but knows US IEP law, not Polish opinions or IPET/WOPFU rules. Not re-tried hands-on in this pass. ChatGPT is the real incumbent: Polish teacher guides tell teachers to paste a short anonymised description and ask for a draft ([Antyweb](https://antyweb.pl/ai-dla-nauczyciela-jak-sztuczna-inteligencja-moze-pomoc-w-pracy)).

**Polish adaptation, i.e. the edge:**
- Polish document conventions: opinions are issued under each school's own procedure, typically by the wychowawca, a teacher or a specialist, on a written request, within e.g. 7 days, signed by the author and the director, containing only information confirmed by school records (example: SP Lubawa procedure, zarządzenie 23/2024, search excerpt of [the PDF](https://sp.lubawa.pl/wp-content/uploads/2024/07/Zalacznik-nr-1_23_2024_PROCEDURA-WYDAWANIA-OPINII-O-UCZNIU-W-Szkole-Podstawowej-im.-M.Kopernika-w-Lubawie.pdf)). No national template was found for the opinion itself; the family-court variant follows the court's or kurator's request (legal basis not confirmed).
- Rules on psychological-pedagogical help (WOPFU/IPET elements) and kuratorium inspections that flag missing elements (TH36 check: [Kuratorium Kielce, 2026-04](https://kuratorium.kielce.pl/wp-content/uploads/2026/04/informacja-o-wynikach-kontroli-szkola-podstawowa-nr-32-im.-janusza-kusocinskiego-w-kielcach.pdf)).
- **Awans plans are gone:** the 2022 Karta Nauczyciela reform cut promotion to two steps and dropped the staż, the *plan rozwoju zawodowego* and the report on it; only teachers who started a staż under the old rules still write them (Portal Oświatowy and ZPP summaries, search excerpt: [Portal Oświatowy](https://www.portaloswiatowy.pl/slowa-kluczowe/plan-rozwoju-zawodowego-4664/strona/3); [ZPP PDF](https://zpp.pl/storage/library/2022-05/6dddacbced7dca1ad5d46b9af7cc4932.pdf)). The autocomplete demand for "plan rozwoju zawodowego" seen in TH36 is therefore a fading transitional need, and the L127 module is dropped.
- RODO: children's health and behaviour data; the product must keep identities out of the LLM call. The moat is modest: conventions are learnable in weeks.

**Target customer in Poland:** teachers who write opinions and reports: wychowawcy, support teachers (nauczyciele wspomagający), pedagogues and psychologists. **511.0k FTE teachers in 2024/2025** (GUS, [stat.gov.pl](https://stat.gov.pl/dla-mediow/informacje-prasowe/polska-szkola-w-liczbach-jak-wyglada-edukacja-w-roku-szkolnym-20242025,36,1.html), search excerpt), slightly over 710k people on full and part-time contracts (Bankier citing GUS/MEN, search excerpt, [Bankier](https://www.bankier.pl/wiadomosc/Brakuje-ponad-20-tys-nauczycieli-Bez-nadgodzin-sie-nie-obejdzie-8991191.html)). Support teachers and specialists not counted separately. CEE: each country's school paperwork differs.

**Demand driver:** social and regulatory. The number of pupils with an orzeczenie o potrzebie kształcenia specjalnego rose by about 50k (~30%) over 15 years while pupil numbers fell (government communication, search excerpt, [gov.pl](https://www.gov.pl/web/nauka/rekordowe-srodki-na-wsparcie-psychologiczne-i-pedagogiczne-w-szkolach)); child mental-health demand raises poradnia referrals (DD4); teacher shortages (DD11, TH36) spread the paperwork over fewer people.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| **Smart IPET** (content from ePedagogika.pl / Portal Oświatowy; files on wip.pl, apparently Wiedza i Praktyka) | reads orzeczenie + WOPFU, drafts the IPET, .doc export | Mini 890.03 PLN gross/year (1 user), Pro 2,997.76 PLN/year (30 users) ([smartipet.pl](https://smartipet.pl/ipet-w-kilka-minut/)) | IPET only; no opinions or reports listed |
| Template sites and teacher shares ("wzór", "przykład") | Word templates | free / small fees | no drafting from the teacher's notes |
| Portal Oświatowy / ePedagogika subscriptions | articles, model documents | subscription (not checked) | content, not a tool |
| ChatGPT, Gemini, Copilot | draft from anonymised notes | free | no section checks, data-handling risk on the teacher |
| UPDF, TeachShare-type generators | parent letters, report comments, English-first | free tiers | not Polish school documents |
No Polish AI tool for opinions or support-teacher reports found (two searches).

**Evidence of Polish demand:** strong template-seeking autocomplete: "opinia o uczniu" → "do poradni", "do sądu", "do sądu rodzinnego przykład"; "sprawozdanie z pracy nauczyciela" → support-teacher, autism, preschool variants (TH36, 2026-11-05). Searches for "… ai" return nothing Polish, so teachers do not yet look for AI. Paid demand shown only for IPET (Smart IPET testimonials).

**MVP scope (≤6 weeks):**
1. Three document types: opinia o uczniu (poradnia / sąd / other school), sprawozdanie nauczyciela wspomagającego, półroczne/roczne sprawozdanie wychowawcy.
2. Guided form per type (observed behaviour, learning, social functioning, help given, effects) mapped to required sections; checklist warns about missing sections and about opinions not backed by records.
3. Pseudonymisation in the browser: the name and school are replaced by tokens before the LLM call and restored locally; no storage of drafts on the server by default.
4. .docx export with school header placeholders and signature lines.
5. Tests: fixture forms → expected sections present, no personal tokens sent, style checks (no diagnoses, no medical claims).
6. SEO pages for each "wzór/przykład" variant with a worked example and the form.

**Monetization:** 19 PLN/month or 99 PLN per school year per teacher (BLIK/Przelewy24), free first document; school licence 690 PLN/year for up to 30 staff (undercuts Smart IPET Pro). **Unit economics:** ~10 documents per teacher per month at peak × ~2k input + 1.5k output tokens; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash)) ≈ US$0.04 (~0.2 PLN) per teacher-month; payment fees ~2–3 PLN on a 19 PLN charge (estimate). Gross margin ~85%. **Customer count:** 10k PLN MRR ≈ 525 teachers at 19 PLN (or ~1,200 on the yearly plan averaged to ~8 PLN/month); 20× = 10.5k–24k, well below ~710k teachers, so the §3 check passes. The issue is conversion and seasonality, not market size.

**Distribution, first 10 customers:** SEO on the autocomplete phrases above; teacher Facebook groups (support teachers, wychowawcy, pedagogues) with a free worked example; one teacher-influencer partnership (Instagram/TikTok educators); later directors via the school licence.

**Regulation:** AI Act Annex III point 3 makes high-risk AI that evaluates learning outcomes, steers the learning process or decides access to education ([Annex III](https://artificialintelligenceact.eu/annex/3/)). An opinion for a poradnia or a court describes a child's functioning and may influence such decisions; the product drafts from the teacher's own observations and the teacher signs, which fits the art. 6(3) exemption for tools that improve the result of a completed human activity (to be confirmed by counsel). No scoring, no recommendations about placement. RODO: special-category data, pseudonymisation, no training, DPA template for schools that buy licences.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | High-volume "wzór/przykład" queries bring free organic traffic each January and June (TH36 autocomplete) | M | H | example pages reach page 1 for 5 phrases within 3 months |
| O2 | Directors buy a school licence for all specialists, as with Smart IPET Pro | M | M | 3 schools ask for an invoice after a teacher trial |
| O3 | More orzeczenia and more specialists in schools mean more support-teacher reports every term | M | M | support-teacher report is the most used document type |
| O4 | A teacher-influencer or a large FB group adopts it as "the safe way to use AI" | M | M | one post brings 200+ sign-ups |
| O5 | Kuratorium inspections push schools towards complete, dated records | L | M | a director cites an inspection when buying |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Teachers keep using free ChatGPT with anonymised notes, as guides already teach | H | H | free-to-paid conversion <2% after 500 sign-ups |
| R2 | Teachers pay from their own pocket and only at term ends; subscriptions churn after June | H | M | >50% cancel within 2 months of signing up |
| R3 | Smart IPET's publisher adds opinions and reports to its tool and its subscriber base | M | M | new document types on smartipet.pl |
| R4 | Directors or the school's IOD forbid AI for documents about children | M | M | teachers report bans in FB groups |
| R5 | Public criticism of "AI writing opinions about children" damages the brand | L | M | press or union statements on AI opinions |

O sum 6+4+4+4+2 = 20; R sum 9+6+4+4+2 = 25. R − O = 5 < 6, but R1 is H×H and the MVP's answer (section checks, pseudonymisation) is a differentiator, not a mitigation of a free substitute → **band down one** (§4.3).

**Success signals:**
- Western analogue durable signals: recurring yearly paperwork with a named owner (signal 2) and app-store distribution by teachers searching for "evrak" (signal 5) for Öğretmen Evrak; MagicSchool's bottom-up teacher sign-ups turning into school partnerships (signal 5, 4-like) ([MagicSchool](https://www.magicschool.ai/blog-posts/series-b-fundraise-for-teacher-ai)). No retention data. Hype/narrow evidence: TH36 analogues are template apps, mostly in two countries. Durability ~3 → **unproven**.
- Polish adaptation can reproduce: replaced spend = teacher's unpaid evening hours (no budget line), so WTP is weak; first channel = SEO on template queries; retention driver = term-end reports twice a year, which is seasonal, not monthly.

**Graveyard:** none found for Polish teacher-paperwork tools; not searched for failed Western report-comment generators.

**Scores (1–5):** L1 3 · L2 2 · L3 3 · L4 3 · L5 4 · L6 2 · L7 4 · L8 3 · L9 2 | **Weighted:** 2.9 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). Demand for the documents is large and sourced, but the job is a short text that free assistants already draft, teachers pay from their own pocket and only twice a year, and the awans module that made the bundle richer was abolished in 2022. **Recommendation: do not build as a subscription; at most an SEO side project or a module inside a school-licence product.**
Changes vs. quick score: L3 4 → 3 (ChatGPT with anonymised notes is the taught practice), L4 4 → 3 (no national template, conventions learnable in weeks), L5 4 kept (teacher count and orzeczenia growth sourced), L9 2 kept; weighted 3.2 → 2.9.

**Cheapest validation test (≤1 week, ≤200 PLN):** publish three example pages ("opinia o uczniu do poradni – przykład", "… do sądu rodzinnego", "sprawozdanie nauczyciela wspomagającego") with a working free form; post in 3 teacher FB groups; offer the 99 PLN/year plan with a pre-order button. Target: 300 form uses and 15 pre-orders.

**Kill criteria:** <1% of form users click pre-order; or teacher feedback says ChatGPT is "good enough"; or Smart IPET adds opinions.

**Confidence:** medium on demand size and regulation, low on willingness to pay.

**Sources** (accessed 2026-11-05/06):
1. https://apps.apple.com/tr/app/%C3%B6%C4%9Fretmen-evrak/id1520664624 (via catalogue, 2026-11-01)
2. https://www.magicschool.ai/blog-posts/series-b-fundraise-for-teacher-ai
3. https://smartipet.pl/ipet-w-kilka-minut/
4. https://antyweb.pl/ai-dla-nauczyciela-jak-sztuczna-inteligencja-moze-pomoc-w-pracy
5. https://sp.lubawa.pl/wp-content/uploads/2024/07/Zalacznik-nr-1_23_2024_PROCEDURA-WYDAWANIA-OPINII-O-UCZNIU-W-Szkole-Podstawowej-im.-M.Kopernika-w-Lubawie.pdf (search excerpt)
6. https://www.portaloswiatowy.pl/slowa-kluczowe/plan-rozwoju-zawodowego-4664/strona/3 (search excerpt)
7. https://zpp.pl/storage/library/2022-05/6dddacbced7dca1ad5d46b9af7cc4932.pdf (search excerpt)
8. https://stat.gov.pl/dla-mediow/informacje-prasowe/polska-szkola-w-liczbach-jak-wyglada-edukacja-w-roku-szkolnym-20242025,36,1.html (search excerpt)
9. https://www.bankier.pl/wiadomosc/Brakuje-ponad-20-tys-nauczycieli-Bez-nadgodzin-sie-nie-obejdzie-8991191.html (search excerpt)
10. https://www.gov.pl/web/nauka/rekordowe-srodki-na-wsparcie-psychologiczne-i-pedagogiczne-w-szkolach (search excerpt)
11. https://kuratorium.kielce.pl/wp-content/uploads/2026/04/informacja-o-wynikach-kontroli-szkola-podstawowa-nr-32-im.-janusza-kusocinskiego-w-kielcach.pdf (via TH36)
12. https://openrouter.ai/google/gemini-2.5-flash
13. https://artificialintelligenceact.eu/annex/3/
14. Internal: [TH36 check](../../poland-check/C/TH36-teacher-school-paperwork.md), [TH35 check](../../poland-check/B/TH35-teacher-copilot.md)

Coverage: 9 web searches/fetches (2022 awans reform, Polish AI opinion tools, MagicSchool funding, teacher and orzeczenia counts, Smart IPET scope and prices, opinion procedures and court basis, teacher-resource prices). Not found: national number of opinions requested per year, count of support teachers, prices teachers pay for template subscriptions (Twinkl PL price not found), legal basis for school opinions requested by family courts.
