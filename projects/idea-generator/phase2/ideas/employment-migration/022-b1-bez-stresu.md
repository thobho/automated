# 022 — "B1 bez stresu": speaking and writing coach for the state Polish exam

**One-liner:** A mobile app in Ukrainian, Russian and English that prepares foreigners for the państwowy egzamin certyfikatowy z języka polskiego jako obcego at B1 (and B2): timed mock exams in the official format, AI feedback on written tasks (case endings, aspect, register) and on recorded oral answers against the exam's published criteria, a conversation partner, and a countdown plan to the next session; sold per exam period and through employers and universities.
**Field:** employment-migration | **Type:** mobile app | **B2C** (B2B2C via staffing agencies and universities) · shortlist id L048

**Western analogues:**
- **Speak** (US): speaking-first AI tutor; **US$78M Series C at a US$1B valuation (2024-12)**, 10M+ downloads, #11 top-grossing Education on the US App Store on 2026-11-01 ([TechCrunch 2024-12-10](https://techcrunch.com/2024/12/10/openai-backed-speak-raises-78m-at-1b-valuation-to-help-users-learn-languages-by-talking-out-loud), via R1 catalogue).
- **Praktika** (UK): AI-avatar tutor; **US$35.5M Series A (2024-05)**, 1.2M MAU, ~US$20M revenue over the prior 12 months (company claims) ([TechCrunch 2024-05-22](https://techcrunch.com/2024/05/22/praktika-raises-35-5m-to-use-ai-avatars-to-make-learning-languages-feel-more-natural), via R2 catalogue).
- **Exam/immigrant-specific:** Kielo (FI, Finnish and Swedish for residents, #22 top-grossing Education FI, 2026-11-01, R4 catalogue); YKI exam apps "Finnish it", YKI Trainer ("AI-powered preparation platform"), Kieli Pro (search excerpts, 2026-11-06). Finland's intermediate YKI exam in Finnish grew from 7,000 participants (2019) to over 8,400 (2024) ([OPH](https://www.oph.fi/en/news/2024/number-people-taking-intermediate-level-yki-test-finnish-has-increased-tests-become-fully), excerpt, accessed 2026-11-06).

**Spread:** TH40: US, UK, FI, EE, CZ, HU, JP, SG (R1, R2, R4, R6, R7), 2023–2026. Exam-prep for a host-country citizenship/residence exam: FI (YKI) clearly; elsewhere not catalogued.

**Does the Western leader already work in Poland?** Speak and Praktika teach English to Poles; neither teaches Polish for the state exam (TH40 check). **The niche is already entered locally:** **Mova — Polish Lessons** (developer Aliaksandr Mazouka) prepares for B1, B2 and C1 with past-session tasks, AI assessment of writing against exam criteria, speaking practice with transcription and AI evaluation, an AI tutor, interface in Polish, Ukrainian, Russian and English; **US$9.99/month or US$24.99/quarter (Standard), US$14.99/month (Pro)**; 1 rating at the time of fetch ([App Store](https://apps.apple.com/app/id6757133556), fetched 2026-11-06). Also Mówek (Ukrainian listing with AI dialogue) and Univext (speaking only) (TH40 check). Not tried hands-on.

**Polish adaptation, i.e. the edge:**
- Exam format and criteria set by the Państwowa Komisja and the 2026 regulation on certificates (Dz.U. 2026 poz. 676, TH40 check); past exam sheets published, e.g. a B1 sheet from 2024-02 ([certyfikatpolski.pl](https://certyfikatpolski.pl/wp-content/uploads/2025/02/4-5.02.2024-B1_arkusz_egzaminacyjny.pdf), accessed 2026-11-06).
- Polish morphology feedback (seven cases, aspect) for Ukrainian and Russian speakers, whose typical errors are interference errors.
- Exam logistics: sessions, registration that fills in minutes at some centres (excerpt), fee ~150 EUR at one centre ([Łazarski](https://lazarski.pl/en/offer/language-learning/panstwowe-egzaminy-certyfikatowe-z-jezyka-polskiego-jako-obcego), via TH40).
- Uses of the certificate: citizenship, long-term EU residence card, civil service (excerpt of [lexlege art. 11a](https://lexlege.pl/ustawa-o-jezyku-polskim/art-11a/) context). The moat is moderate: a foreign team with Polish teachers could build it in months, and a local one already has.

**Target customer in Poland:** exam candidates: **21,781 in 2024 vs. 2,803 in 2017** (justification to Sejm print 2361, [api.sejm.gov.pl](https://api.sejm.gov.pl/sejm/term10/prints/2361/2361-uzasadnienie.docx), via TH40). A 2025 figure was not found (searched 2026-11-06). Wider pool: 1.56M Ukrainians with permits; 108.6k foreign students needing B2 for study (demography D35). B2B: staffing agencies, universities.

**Demand driver:** DD6 migration and settling (citizenship and long-term residence applications), study admissions requiring B2. **Possible trigger:** a government draft would raise the citizenship requirement from B1 to B2 and add a ~40-question civics test, with cabinet adoption planned for Q4 2026; a PiS bill was rejected by the Sejm on 2026-01-09, and the president sent his own bill ([Grant Thornton](https://grantthornton.pl/publikacja/zatrudnianie-cudzoziemcow-2026-sejm-odrzucil-zmiany-w-obywatelstwie/); [Forsal](https://forsal.pl/kraj/aktualnosci/artykuly/11246150,dla-kogo-polskie-obywatelstwo-mswia-przygotowuje-zmiany-w-prawie.html), excerpts, accessed 2026-11-06). Not law yet.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| **Mova — Polish Lessons** | B1/B2/C1 exam prep, AI writing and speaking scoring, UA/RU/EN UI | US$9.99–14.99/month | very new (1 rating); quality unknown |
| Mówek, Univext | AI dialogue / speaking practice for Polish | not checked / free trial | not exam-focused |
| University and language-school courses, BUR-funded courses | human B1/B2 prep | course fees vary | schedule-bound, costly |
| Free past exam sheets + ChatGPT voice | self-study | free / ~20 USD | no rubric-based scoring, no plan |
| Duolingo Polish | general course | freemium | not exam prep |

**Evidence of Polish demand:** autocomplete "egzamin b1 polski" → "przykładowe testy 2026", "2026 rejestracja", "2026 cena", "przykładowe testy online"; Ukrainian "вивчення польської мови" → "безкоштовно", "для українців" (TH40, 2026-11-03). Exam candidates up ~8× in seven years (Sejm print 2361). A researcher notes growth in B2 candidates since 2025 (search excerpt of a Polish academic article). Many BUR-listed B1 prep courses exist (search results), i.e. people pay for prep.

**MVP scope (≤6 weeks):**
1. Mock exam engine in the official B1 format (listening, reading, grammar, writing, speaking), seeded with own items modelled on published sheets.
2. Writing feedback: errors tagged by type (case, aspect, agreement), with an estimated score on the published criteria.
3. Speaking: record answer → transcript → feedback on task completion, range and accuracy; pronunciation flags.
4. Plan to the user's exam date; Ukrainian/Russian/English UI; BLIK/App Store payments.
5. Tests: golden essays scored by two certified examiners (paid) to calibrate; regression set of 100 transcripts.

**Monetization:** 49 PLN/month or 129 PLN for a 3-month exam pack; employer/university seats 30 PLN per learner-month. **Unit economics:** per active user-month ≈ 30 min of recorded speech (~60k audio tokens) + 20 writing tasks (~100k input / 40k output text tokens) on Gemini 2.5 Flash (text US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05; audio input price not checked, assumed ≤ US$1 per M) ≈ US$0.25; a spoken conversation partner via a voice-agent platform at ~US$0.08/min (secondary, see 020) for 30 min adds ~US$2.4. Cost ≈ 10–11 PLN against 49 PLN less app-store fees (15–30%) → gross margin ~50–65%. **Customer count:** 10k PLN MRR ≈ 204 paying users at 49 PLN at any time; with ~3 months per candidate that is ~800 buyers a year, ~4% of 2024's 21,781 candidates; the reachable pool is ~5×, not 20×, the needed count unless the wider learner base buys → **cap at 5–15%** (criteria §3).

**Distribution, first 10 customers:** Ukrainian-language App Store/Play listing with "B1" keywords; Ukrainian Facebook/Telegram groups on legalisation; 2–3 university international offices (B2 for admissions); staffing agencies already buying 002/017.

**Regulation:** AI Act Annex III point 3 covers AI used to evaluate learning outcomes **by education and training institutions** or to assess the level of education a person will receive ([Annex III](https://artificialintelligenceact.eu/annex/3/)); a self-study practice app for individuals is outside it, but a B2B seat sold to a university for placement could fall inside (own reading). RODO: voice recordings are personal data; EU hosting, delete after feedback. No exam-board affiliation may be implied.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Candidates grew ~8× in seven years and sessions fill fast, so motivated, deadline-driven buyers exist | H | M | ≥2% of landing visitors from exam searches pay |
| O2 | A citizenship B2 + civics test law would open a second, larger exam market | L | H | cabinet adopts the MSWiA draft |
| O3 | Universities and staffing agencies buy seats, lifting volume without ads | M | M | one university buys ≥50 seats |
| O4 | App stores in Ukrainian give an owned channel; exam apps top charts in Finland | M | M | top-50 Education in PL App Store within 3 months |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Mova already sells the same product (B1–C1, AI writing and speaking scoring, UA/RU/EN) at ~US$10/month, so there is no gap to own | H | H | Mova's ratings and chart rank rise |
| R2 | Exam prep is one-off: users churn right after the exam, so MRR must be refilled every quarter | H | M | median subscription <3 months |
| R3 | Free ChatGPT voice plus free published sheets are good enough for most candidates | H | M | trial users ask for "free version" |
| R4 | AI speaking scores do not match examiners; users fail after "passing" mocks and leave bad reviews | M | M | calibration error >1 grade band on the golden set |
| R5 | The market is small (~22k candidates a year), capping MRR | M | M | paid conversion plateaus below 200 users |

O sum 6+3+4+4 = 17; R sum 9+6+6+4+4 = 29. R − O = 12 and R1 is H×H without a mitigation in the MVP → **down one band** (rule §4.3).

**Success signals:**
- Western analogue durable signals: Speak's long top-grossing presence and 10–20 min daily use (retention proxy, R1 catalogue), Praktika's ~US$20M revenue (company claim), app-store distribution (signal 5), subscription pricing (signal 7); exam-specific apps (Kielo, YKI) show a niche pattern but small install bases. Durability score ~4 → **promising** for the theme; TH40 rates the English-tutor segment hype-prone.
- Hype warnings: crowded category, many thin wrappers, self-reported growth (TalkMe, R7 catalogue).
- Polish adaptation can reproduce: replaced spend = a prep course or private tutor; first channel = Ukrainian app-store search and migrant groups; retention driver = weak (one exam), partly fixed by B2 after B1.

**Graveyard:** none found specific to host-country exam prep. Theme: many 2023 AI tutor launches compete on price; not catalogued as failures.

**Scores (1–5):** L1 4 · L2 3 · L3 2 · L4 3 · L5 4 · L6 3 · L7 3 · L8 3 · L9 2 | **Weighted:** 3.1 / 5 | **Chance band:** score → 5–15% (customer-count cap also 5–15%); O 17, R 29, unmitigated H×H → **<5%**. Demand is real and sourced, but a local app (Mova) already does exactly this in Ukrainian at a lower price, exam prep churns after the exam, and ~22k candidates a year is a thin base for 200 concurrent subscribers.
Changes vs. quick score: none on the lenses (L3 2 confirmed by Mova's App Store page); weighted 3.1 unchanged; band lowered by §3 cap and §4.

**Cheapest validation test (≤1 week, ≤200 PLN):** install Mova and score its feedback on 5 real B1 essays checked by a certified examiner (≈150 PLN); if Mova is weak, run a Ukrainian landing page "B1 mock exam with examiner-calibrated scoring" with a 129 PLN pre-order and post it in migrant groups.

**Kill criteria:** Mova's feedback matches the examiner on ≥4 of 5 essays; or <15 pre-orders from ~1,500 visitors.

**Confidence:** medium (exam volumes and the competitor sourced; scoring quality and willingness to pay untested).

**Devil's advocate (T24, 2026-11-06):**
- *It already works in Polish, several times over.* The second search found a crowded niche, not one early entrant:
  - **PolskiTest.pl** (web): mock B1/B2/C1 exams, "most of the tests ... are real exams from previous years", AI feedback on writing with a corrected version, recorded oral exam, tutor directory, UI in EN/PL/BE/RU/UA; **30 PLN for 1 month, 40 PLN for 2, 50 PLN for 3**, speaking packages 20–50 PLN ([polskitest.pl](https://polskitest.pl/en/), fetched 2026-11-06).
  - **PolskiPro: Polish B1 & B2 Exam Preparation** (developer Dzianis Hrynko): full exam simulator, essays, pronunciation beta, human-checked content, menu in PL/BE/UA/RU; **39.99 PLN/month, 109.99 PLN/3 months**, 4.3★ from 6 ratings ([App Store PL](https://apps.apple.com/pl/app/polskipro/id6749869442), fetched 2026-11-06).
  - **Mova** (B1–C1, AI writing and speaking scoring, US$9.99–14.99/month; cited above), plus PolishGo ([App Store](https://apps.apple.com/mx/app/polishgo/id6752503183), search result) and a Belarusian-built B1 prep app covered by dev.by ([dev.by](https://devby.io/news/belarus-sdelal-prilozhenie-kotoroe-pomogaet-gotovitsya-k-ekzamenu-na-b1-po-polskomu), search result); none checked hands-on.
  The job (official-format mocks + AI writing feedback + Ukrainian/Russian UI) is done; only examiner-calibrated speaking scores might still be open, and Mova claims those too.
- *Polish customers won't pay this price.* The market price is set at 30–50 PLN for one to three months (PolskiTest.pl) or ~40 PLN/month (PolskiPro); the planned 49 PLN/month or 129 PLN per 3 months is above all of them, before 15–30% app-store fees.
- *ChatGPT will absorb it.* Free past sheets plus ChatGPT voice already give most of the feedback (R3); the paid local apps are themselves thin layers on that.
- *The trigger is still not law.* The citizenship B2 + civics test draft is planned for cabinet adoption in Q4 2026 and has not been adopted (search excerpts of PAP and Bezprawnik, 2026-11-06, [PAP](https://www.pap.pl/aktualnosci/mswia-szykuje-zmiany-dot-polskiego-obywatelstwa-padl-termin)); O2 stays L. 2025 candidate numbers: still not found.
- *Western leader localizing in 12 months.* Speak or Praktika adding Polish for exam takers is unlikely and unnecessary: local developers already serve it.
- *Success signals.* Speak and Praktika are durable in English tutoring, but the host-country exam pattern shows only small apps (Kielo, YKI trainers); L2 3 is fair for the theme, not for this niche.
- *Opportunity/risk lists.* R1 should name the whole set of local apps, not only Mova; it is H×H with no answer in the MVP. O4 (app-store channel) is weaker with four exam apps already ranking for "B1" → L×M.

**Review changes (T24, 2026-11-06):** L3 2 → 1 (taken: PolskiTest.pl, PolskiPro, Mova and others sell official-format mocks with AI writing feedback and UA/RU/BE UIs); L6 3 → 2 (market price 30–50 PLN per 1–3 months undercuts the 49 PLN/month plan). Reviewed scores: L1 4 · L2 3 · L3 1 · L4 3 · L5 4 · L6 2 · L7 3 · L8 3 · L9 2 | weighted 0.48+0.36+0.12+0.45+0.60+0.20+0.24+0.24+0.16 = 2.85 → **2.9** (shortlist quick 3.1 replaced). Knock-out L3 = 1 → **<5%** whatever the score. O4 M×M → L×M; §4: O 6+3+4+2 = 15, R 29. **Rejected** (recorded in rejected.md).

**Sources** (accessed 2026-11-06 unless noted):
1. https://techcrunch.com/2024/12/10/openai-backed-speak-raises-78m-at-1b-valuation-to-help-users-learn-languages-by-talking-out-loud (accessed 2026-11-01)
2. https://techcrunch.com/2024/05/22/praktika-raises-35-5m-to-use-ai-avatars-to-make-learning-languages-feel-more-natural (accessed 2026-11-01)
3. https://www.oph.fi/en/news/2024/number-people-taking-intermediate-level-yki-test-finnish-has-increased-tests-become-fully
4. https://apps.apple.com/app/id6757133556
5. https://certyfikatpolski.pl/wp-content/uploads/2025/02/4-5.02.2024-B1_arkusz_egzaminacyjny.pdf
6. https://lazarski.pl/en/offer/language-learning/panstwowe-egzaminy-certyfikatowe-z-jezyka-polskiego-jako-obcego (accessed 2026-11-03)
7. https://lexlege.pl/ustawa-o-jezyku-polskim/art-11a/
8. https://api.sejm.gov.pl/sejm/term10/prints/2361/2361-uzasadnienie.docx (accessed 2026-11-03)
9. https://grantthornton.pl/publikacja/zatrudnianie-cudzoziemcow-2026-sejm-odrzucil-zmiany-w-obywatelstwie/
10. https://forsal.pl/kraj/aktualnosci/artykuly/11246150,dla-kogo-polskie-obywatelstwo-mswia-przygotowuje-zmiany-w-prawie.html
11. https://openrouter.ai/google/gemini-2.5-flash (accessed 2026-11-05)
12. https://artificialintelligenceact.eu/annex/3/
13. Internal: [TH40 check](../../poland-check/A/TH40-ai-speaking-language-tutors.md), R1/R2/R4/R7 catalogue rows
14. https://polskitest.pl/en/ (2026-11-06, T24)
15. https://apps.apple.com/pl/app/polskipro/id6749869442 (2026-11-06, T24)
16. https://apps.apple.com/mx/app/polishgo/id6752503183 (2026-11-06, T24, search result)
17. https://devby.io/news/belarus-sdelal-prilozhenie-kotoroe-pomogaet-gotovitsya-k-ekzamenu-na-b1-po-polskomu (2026-11-06, T24, search result)
18. https://www.pap.pl/aktualnosci/mswia-szykuje-zmiany-dot-polskiego-obywatelstwa-padl-termin (2026-11-06, T24, search excerpt)

Coverage: 4 web searches and 1 fetch for this write-up (Mova, Kielo/YKI apps, 2025 exam counts, citizenship B2 draft). Not found: 2025 candidate numbers, Mova's user numbers, audio-token price for the chosen model.
