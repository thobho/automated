# R7 East Asia (T11): patterns and coverage

Japan, South Korea, Taiwan, Singapore, Hong Kong (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R7-east-asia.csv](../../../catalogue/R7-east-asia.csv), **40 rows** (JP 10, KR 10, TW 8, SG 7, HK 5), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [japan.md](japan.md) | AI phone receptionist at 50,000 accounts (IVRy), spend-management agents (Bakuraku), contract review at ¥10bn ARR (LegalOn), legal research (Legalscape), hospital paperwork AI (Ubie), AI inventory (zaico), AI-native tax firm (AIBOS), English-speaking apps (SpeakBUDDY, Mochispi), care-record voice AI (NAGARA) (JP-001…010) |
| [south-korea.md](south-korea.md) | tax-refund app used by 24M people with RAG tax Q&A (삼쩜삼), case-law AI (LBox), lawyer marketplace turned legal AI (SuperLawyer), Wrtn, Korean notetakers (daglo, Tiro), patient record copilot (Persly), AI phone-call tutor (Heyring), licensing-exam AI (MyMersi), study app (Univ AI) (KR-001…010) |
| [taiwan.md](taiwan.md) | LLM anti-fraud (Whoscall), legal research under litigation (Lawsnote), Kolr, Appier, Toko, notetaker (Atter), taxi-driver voice bookkeeping, AI baby log (TW-001…008) |
| [singapore.md](singapore.md) | AI-native corporate services and accounting (Osome, Sleek), SEA voice agents (WIZ.AI), Owll translator, TalkMe, state tools Pair and LawNet GPT-Legal (SG-001…007) |
| [hong-kong.md](hong-kong.md) | chat-commerce agents (Omnichat), Cantonese speech (Fano Labs), government LLM (HKGAI), Chinese dictation app, AI trading signals; why HK is thin (HK-001…005) |

## Choices recorded
- IDs `R7-<ISO>-NNN`, numbered per country. JP-010 (NAGARA) and KR-010 (Univ AI) were added last to reach the 40-row floor; NAGARA was chosen for its ageing/care relevance to Poland despite trial-only traction.
- Same extra fields as T10: each row's `pl_adaptation_angle` starts with `adapts: <Western product or 'no single leader'>; PL: entered / no / unknown`; the country files repeat them as "Adapts" and "Poland" columns. **No R7 product was found to have entered Poland.** "Unknown" is used for global apps where a Polish presence was not checked.
- `works_in_polish` comes from App Store language lists where looked up (iTunes lookup API); no product was tried hands-on (time budget). Persly (KR-007) lists Polish as an app language; that is the only R7 product with a Polish UI found.
- Omnichat is filed under Hong Kong (Series A release datelined Hong Kong) although Taiwan is its biggest LINE market. Toko is filed under Taiwan (Taiwanese market and accelerator; company also lists a Brooklyn office).
- State programmes catalogued like Bürokratt (R4) and BgGPT (R6): Pair (SG-006), HKGAI/HKPilot (HK-003); LawNet GPT-Legal (SG-007) is run by a statutory body.
- Rows with no or unclear LLM core kept for the local pattern, flagged in `llm_role`/`hype_warnings`: zaico (JP-007, pre-LLM with AI capture), Whoscall (TW-001, LLM layer on an older app), Appier (TW-004, ML ad-tech), Fano Labs (HK-002, speech/NLP). That is 4 of 40.
- Weak-traction rows (chart rank or trials only, small rating base): AIBOS (JP-008), NAGARA (JP-010), MyMersi (KR-009), Atter, 運將助手, 初日手帳 (TW-006…008), 默書啦喂 (HK-004), Intellectia (HK-005). That is 8 of 40; T15 should weight them low.
- Out of founder scope but kept as pattern evidence: Intellectia (investment signals, licence risk), Appier, state products.
- Search engine summaries were used where pages blocked bots or for figures in Asian-language media; those are marked "excerpt" in the country files.

## Poland signal
Unlike R6, **no East Asian product is entering Poland**. East Asian champions expand within Asia (IVRy and LegalOn: Japan + US/UK; Whoscall: Thailand; Heyring: Japan, Taiwan; Osome/Sleek: SG, HK, UK, AU). The signal for Poland is therefore **pattern evidence, not entry risk**: what national-data and national-rule products look like when they reach scale.

Most important for Poland: **national tax/compliance products that own the citizen or SME relationship and add an LLM on top.** 삼쩜삼 (KR) reached 24M sign-ups and >2 trillion KRW of refunds by checking "hidden refunds" for freelancers and gig workers and charging on the outcome; its RAG tax assistant (510,000 laws/rulings + 20,000 expert-checked answers) is the LLM layer, not the product. Bakuraku (JP) and Osome/Sleek (SG) do the same for SME back offices on national invoice and corporate rules. Polish equivalents would sit on Twój e-PIT/e-Urząd Skarbowy (ulgi, zwroty for umowy zlecenie, JDG, migrants), KSeF and KRS/S24, a combination no foreign entrant handles.

## Cross-country patterns
1. **National-data champions add LLMs to an existing monopoly-like asset**: 삼쩜삼 (tax filings), LBox (case law), Law&Company (lawyer marketplace, ~69% of Korean lawyers), LegalOn (contract playbooks, 30% of Japanese listed companies), LawNet (SG law reports), Lawsnote (TW, sued by the incumbent database over scraping). The moat is data and distribution; the LLM is the newest layer. In Poland, open court data (SAOS) lowers the data barrier while LEX/Legalis hold the commentaries.
2. **AI-native accounting and corporate services with licensed professionals in the loop**: AIBOS (JP), Osome and Sleek (SG/HK), Bakuraku agents for accounting offices (JP). Same as Declaro/Bookkeepie (R6), Accountable/mika (R3). Osome's public numbers (S$29M revenue, still loss-making) show the model needs scale and price discipline.
3. **AI phone answering and voice agents for phone-first cultures**: IVRy (JP SMB, 50,000 accounts), WIZ.AI (SEA banks/telcos), Fano Labs (Cantonese call analytics). With Linca/Lorela/Born Digital (R6) and fonio (R3) this theme now spans R3, R6, R7.
4. **Healthcare and care paperwork**: Ubie (JP hospitals: certificates -50%, rehab summaries 23 -> 10 min), NAGARA (JP care records by voice), Persly (KR patient-side copilot over hospital records). Ageing Japan is the leading indicator for Polish DPS/ZOL and home-care documentation.
5. **Anti-fraud as a national LLM use case**: Whoscall (TW/TH, NT$867M revenue, 24M MAU). Poland has the same senior-targeted scams (BLIK, "na wnuczka/policjanta").
6. **Paid consumer AI = speaking practice and exams**: English speaking apps top every R7 Education chart (Speak, SpeakBUDDY, Mochispi, Toko, Heyring, TalkMe, Praktika, Loora), plus national-exam tools (TOEIC Speaking graders, nursing licensing exam AI, HK dictation app on the Education Bureau list). Category crowded; the national-curriculum micro-apps are the adaptable part.
7. **Local-language notetakers beat global ones in their own chart** (daglo, Tiro in KR; Atter in TW); Tiro reports ~90% subscription renewal.
8. **States build their own LLM tools for civil servants** (Pair SG, HKGAI HK), matching Bürokratt (R4), mAigov (R5), BgGPT (R6).
9. **Retail AI investing signals** fill the finance top-grossing charts in SG, HK and KR: a hype-prone, licence-heavy category to avoid.

## Products also in R0–R6 (spread signal)
Not re-catalogued, seen in R7 charts or sources: **Manus** (R0-SG-011, Singapore-based; top-30 Productivity in JP, KR, TW, SG, HK), **Genspark** (R0; JP #10, KR #9, HK, TW), **Plaud** (R1; top-10 Productivity in all five), **Speak** (R1; Education #2 in JP, TW, HK), **Praktika** (R2; JP, TW, HK, SG), **Astra AI** (R6-SI-001; KR Education #17, TW #47), **Loora** (seen in R6 charts; JP, KR, TW, HK, SG), **Harvey** (R0) as the model for SuperLawyer/LBox AI. Themes repeating from R1–R6: AI receptionists (IVRy vs Linca, fonio), AI-native accounting (AIBOS/Osome/Sleek vs Declaro, Accountable), national legal AI (LegalOn/LBox/Lawsnote vs Lexroom, Doctrine, DirectCase), healthcare documentation (Ubie vs Abridge/Nabla), state LLMs (Pair/HKGAI vs Bürokratt/BgGPT).

## Polish adaptation angles from R7 (for T15–T18)
- **Zwrot podatku / ulgi finder for umowy zlecenie, JDG, students and migrants** on Twój e-PIT data with a fee on the refund (삼쩜삼). Check KAS rules and doradca podatkowy licensing for advice.
- **KSeF-native AP and expense agents for SMEs sold through biura rachunkowe** (Bakuraku); Payhawk covers only mid-market in PL (R6).
- **Online biuro rachunkowe + KRS/S24/CRBR/eKRS compliance for sp. z o.o.** with free incorporation as funnel (Osome, Sleek, AIBOS).
- **Polish-voice AI receptionist for gabinety, warsztaty, salony** (IVRy); cross-region theme now.
- **Voice documentation for DPS/ZOL and home care** (NAGARA, Ubie): ageing and carer shortage; AI Act/RODO health data.
- **Anti-scam assistant for seniors and their families** (Whoscall) with CERT Polska data; bank/telco partners.
- **Dyktanda/ortografia and exam micro-apps on the Polish curriculum** (默書啦喂, MyMersi for LEK/PES/nursing exams).
- **Messenger/WhatsApp sales agent for Polish e-shops** wired to Allegro, InPost, BLIK (Omnichat).

## Coverage

| Country | Status | New rows | R0–R6 overlaps seen | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Japan | done | 10 | 6 (Manus, Genspark, Plaud, Speak, Praktika, Loora) | 16 | 7 pages + 5 feeds | 11 | real-estate and care AI with funding: none/1 |
| South Korea | done | 10 | 5 (Astra AI, Manus, Genspark, Plaud, Loora) | 19 | 5 pages + 5 feeds | 10 | no Google Play source; thevc.kr 403 |
| Taiwan | done | 8 | 6 | 16 | 4 pages + 5 feeds | 7 | 3 rows are single-developer apps |
| Singapore | done | 7 | 4 | 14 | 3 pages + 5 feeds | 8 | 2 state products; sal.org.sg 403 |
| Hong Kong | done (thin) | 5 | 6 | 15 | 2 pages + 5 feeds | 6 | AI capital goes to mainland model IPOs; no vertical LLM startups found |
| **R7** | done | **40** | 8 distinct | 80 | 21 pages + 25 feeds | 42 | |

- Region total **40** is at the 40–80 floor. Reasons it is not higher: Hong Kong yields 5 (vertical AI startups absent from public sources; capital goes to mainland model IPOs); Taiwan's software AI is mostly listed ad-tech/anti-fraud firms; the one-hour budget limited depth; Japanese and Korean primary pages were often read via search summaries (marked excerpt).
- App Store top-grossing feeds read for all 5 countries × 5 genres (Business 6000, Productivity 6007, Education 6017, Finance 6015, Medical 6020) on 2026-11-01, plus iTunes lookups for ratings, release dates and languages. Similarweb Google Play pages, J-Startup, K-Startup, Startup SG, HKSTP/Cyberport cohorts and INITIAL/THE VC rankings were **not screened**.
- Durable signals: mostly 1 (replaced spend), 2 (frequent problem), 8 (hard to absorb), 10 (timing). Retention/expansion (signals 3/4): LegalOn (ARR > ¥10bn), LayerX (ARR ¥100M -> ¥10bn in 4 years, CEO), zaico (92% retention), Tiro (~90% renewal), Heyring (D14 retention 58%, job ad), Gogolook (46% subscription revenue, 24M MAU), Osome (S$29M revenue), daglo (revenue x4), WIZ.AI (revenue x2), Law&Company (first half-year profit). Hype warnings: Wrtn's character-chat revenue, Owll's single-day peak ranks, TalkMe's self-reported 1000% growth, Intellectia's backtested returns, Lawsnote's criminal case, Sleek's inconsistent aggregator figures, Osome still loss-making.
- Searched and found nothing: LLM startups with funding for HR/payroll (KR 노무, TW, HK), real estate (JP 不動産, HK 物業), accounting AI startups in TW and HK, legal/insurance AI startups in HK; any public cohort retention curve.
- Bot-blocked or failed fetches: thevc.kr (403), sal.org.sg (403), archive.opengovasia.com (403), tech.slator.com (403), info.gov.hk (empty page to the fetch tool), thebridge.jp English article (404 on the slug tried).
