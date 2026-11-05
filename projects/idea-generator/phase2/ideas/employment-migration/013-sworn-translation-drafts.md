# 013 — Sworn-translation drafts for tłumacze przysięgli ("Szkic tłumaczenia poświadczonego")

**One-liner:** A sworn translator (tłumacz przysięgły) uploads a scan or photo of a Ukrainian birth or marriage certificate, diploma with supplement, driving licence or certificate of no criminal record; the tool returns an editable Polish draft in the sworn-translation layout used in Poland (descriptions of stamps, seals, signatures and handwritten notes in brackets, transliteration of names, the certification clause and repertory entry ready), plus a page count in the official 1,125-character billing page. The translator checks, corrects and certifies; the tool never certifies.
**Field:** employment-migration | **Type:** SaaS (web) | **B2B** (solo sworn translators and small translation offices) · shortlist id L052

**Western analogues:**
- **SwornTrans** (DE, Frankfurt, shipped 2026-08): AI translation and formatting of court and legal documents into editable .docx keeping layout, tables and seals, EU-hosted; one-off page packs from €30 for 10 pages to €2,000 for 1,000 pages (€3.00–2.00 per page); vendor claims >80% less retyping; **no user or revenue figures**, "limited public user reviews" ([Stork listing](https://www.stork.ai/en/sworntrans)). Languages not listed; Polish support not checked.
- **X-doc AI**: certified birth-certificate translation that mirrors layout, stamps and signatures, with optional human review ([x-doc.ai](https://x-doc.ai/use-cases/en/online-birth-certificate-translation-localization)); traction not found.
- **AcudocX / Translato.ai** (US): AcudocX, a certified-translation platform, acquired self-service Translato.ai in August 2023 ([CB Insights](https://www.cbinsights.com/company/translatoai)); figures not found.
None shows durable traction; the pattern (AI draft, licensed human certifies) is young.

**Spread:** TH69 translation and localisation: DeepL, Google, Lokalise (LV), Owll (SG) for general translation ([TH69 check](../../poland-check/C/TH69-translation-localisation.md)); certified-document AI drafts seen in DE (SwornTrans) and US (Verdacert, X-doc). Two to three countries, all since 2023.

**Does the Western leader already work in Poland?** Partly. DeepL and Google translate Ukrainian → Polish well but lose document layout, which makes them unfit for official documents (TH69 check, citing [Bluente](https://www.bluente.com/blog/translate-documents-to-ukrainian)). SwornTrans may handle Ukrainian → Polish layout drafts (not tried; supported languages not published). Polish sworn-translation conventions (bracketed descriptions of seals, repertory number, certification clause) are not mentioned by any of them.

**Polish adaptation, i.e. the edge:**
- **Ustawa o zawodzie tłumacza przysięgłego:** only a translator on the Minister of Justice's list can certify; the list is published in the BIP (except some personal data) ([lexlege, chapter 2](https://lexlege.pl/ustawa-o-zawodzie-tlumacza-przysieglego/rozdzial-2-nabywanie-i-utrata-prawa-do-wykonywania-zawodu-tlumacza-przysieglego/4972/)).
- **Billing page = 1,125 characters with spaces** (25 lines × 45 characters, from the MS regulation; secondary source, current text not re-read); market price for Ukrainian → Polish about 40–80 PLN per page net, express doubled ([Wrocław city guide](https://www.wroclaw.pl/dla-mieszkanca/tlumacz-przysiegly-gwarancja-bezpiecznego-zalatwienia-spraw-w-urzedach); [cenauslug.pl](https://cenauslug.pl/przewodnik/tlumaczenia-przysiegle)).
- **Layout conventions** for descriptions of stamps, emblems and signatures follow the TEPIS Kodeks tłumacza przysięgłego (not re-read in this pass) and translators' habits; Ukrainian document templates (Soviet-era and post-2014 birth certificates, diploma supplements) and transliteration rules for names.
A foreign tool needs these conventions plus Ukrainian document variants; months of template work, but a Polish CAT-tool user could copy the idea.

**Target customer in Poland:** sworn translators of Ukrainian (and later Russian, Belarusian, Georgian), and offices that employ them. Their number was **not found**; a 2022 prawo.pl article cites 39 "on the MS list" in its context (scope unclear) and describes shortages slowing diploma recognition, with full medical-degree documentation of 100–200 pages costing over 10,000 PLN ([prawo.pl, 2022-03-28](https://www.prawo.pl/student/nostryfikacje-dyplomow-utrudnia-brak-tlumaczy-z-ukrainskiego,514262.html)). CEE: CZ and SK have sworn-translator systems with different conventions.

**Demand driver:** DD6: ~1.5 million Ukrainians and growing Asian migration need certified translations for residence (MOS) cases, civil-status transcription and diploma recognition (TH69 check; [TH12 / idea 002](002-teczka-legalizacyjna.md)).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| DeepL, Google Translate | machine translation incl. documents | free / DeepL Pro subscription | layout and sworn conventions lost |
| Trados, memoQ (CAT tools) | translation memory, used by many translators | licences | no OCR-to-layout draft of scanned civil documents |
| SwornTrans (DE) | AI legal translation keeping layout | €2–3 per page | Polish conventions and UA templates not shown |
| Own Word templates per document type | what many translators use today (assumed, unverified) | time | retyping names, dates and stamps |
| ChatGPT | translate a photo | free / 20 USD | layout, RODO concerns with ID documents |

**Evidence of Polish demand:** autocomplete "tłumacz przysięgły online" → "24h", "tanio", "cena", "szybko" (TH69 check) shows the end-customer side; shortage of Ukrainian sworn translators (prawo.pl 2022). No translator asking for such a tool was found.

**MVP scope (≤6 weeks):**
1. Five document types first: Ukrainian birth certificate (two layouts), marriage certificate, diploma + supplement, driving licence, certificate of no criminal record.
2. Vision LLM extracts fields and non-text elements (stamps, coats of arms, signatures, handwritten notes) into a schema; transliteration of names per a rules table.
3. Template engine produces a .docx draft in the Polish sworn layout with bracketed descriptions, certification clause and repertory fields; page count at 1,125 characters.
4. Side-by-side review screen; every field links to its image region.
5. Tests: 50 synthetic or consented sample documents with golden .docx outputs; character-count tests.

**Monetization:** 99 PLN/month for up to 60 documents, 199 PLN unlimited; per-document 5 PLN without subscription. Budget line: the translator's time on retyping and layout (a birth certificate is 1–2 billing pages at 40–80 PLN; time saved goes straight to the translator's margin). **Unit economics:** one 2-page document ≈ 3k image + 2k text input / 3k output tokens; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.01; 60 documents ≈ US$0.6 (~2.5 PLN). Gross margin >90%. **Customer count:** 10k PLN MRR ≈ 101 translators at 99 PLN (or ~50 at 199); the base of Ukrainian-language sworn translators is unknown, so the §3 sanity check is not met with a source (band capped at 5–15%).

**Distribution, first 10 customers:** outbound to translators of Ukrainian from the public MS list (e-mail where listed); TEPIS (Polskie Towarzystwo Tłumaczy Przysięgłych i Specjalistycznych) events and newsletter; translator Facebook groups; agencies from idea 002 who order translations in bulk.

**Regulation:** AI Act: not high-risk (translation tools are not in [Annex III](https://artificialintelligenceact.eu/annex/3/)); the translator certifies and is liable. RODO: identity documents of third parties; EU hosting, no training on uploads, auto-delete after 30 days, processing agreement with each translator. Professional secrecy of sworn translators (ustawa) supports strict handling.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Translators of Ukrainian are overloaded by migrant demand, so time saved per document is directly more paid pages | M | M | pilot translators report >30% time saved on civil documents |
| O2 | TEPIS or translator groups spread it as a professional tool | M | M | a TEPIS newsletter or event features it |
| O3 | Templates for more migrant languages (Belarusian, Russian, Georgian, Hindi documents) widen the base | M | M | translators of other languages ask for access |
| O4 | The template library of Ukrainian document variants compounds with every customer and is hard to copy | H | L | 20+ verified layouts after 3 months |
| O5 | Legalisation agencies (idea 002) buy bundles of drafts for their translators | L | M | one agency asks for a team plan |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | SwornTrans, DeepL document translation or a CAT-tool plugin is already good enough for Ukrainian → Polish layouts | H | M | pilot translators prefer their current tool after a side-by-side test |
| R2 | The pool of Ukrainian-language sworn translators is too small for ~100 subscribers | M | H | the MS list shows fewer than ~1,000 entries for Ukrainian |
| R3 | Solo translators are price-sensitive and already pay for CAT tools, so 99 PLN/month is refused | M | M | trial-to-paid conversion <15% |
| R4 | Professional caution: translators will not upload clients' identity documents to a cloud AI | M | M | questions about RODO dominate demo calls |
| R5 | Migrant inflows and legalisation volumes fall, cutting document demand | L | M | MOS application counts fall year on year |

O sum 4+4+4+3+2 = 17; R sum 6+6+4+4+2 = 22. R − O = 5 < 6, no H×H risk → **band unchanged** (rule §4.5).

**Success signals:**
- Western analogue durable signals: SwornTrans prices per page from day one (signal 7) and targets a job step with an owner (signal 2) ([Stork](https://www.stork.ai/en/sworntrans)); AcudocX buying Translato.ai suggests consolidation in certified translation ([CB Insights](https://www.cbinsights.com/company/translatoai)). No retention, revenue or user figures. Durability score ~2 → **unproven**.
- Hype warnings: none found, but evidence is thin (one 2026 launch with no reviews).
- Polish adaptation can reproduce: replaced spend = translator hours on retyping and layout; first channel = public MS list and TEPIS; retention driver = template library and weekly document flow.

**Graveyard:** none found in this pass.

**Scores (1–5):** L1 4 · L2 2 · L3 3 · L4 4 · L5 3 · L6 3 · L7 4 · L8 3 · L9 2 | **Weighted:** 3.2 / 5 | **Chance band:** 5–15% (capped there anyway by the §3 sanity check: the reachable translator base is not sourced). The build is small and testable and the buyer list is public, but Western layout-preserving tools appeared in 2026 and may already handle Ukrainian, and ~100 paying translators of one language pair may not exist. **Recommendation: worth a one-week validation because it is cheap; count Ukrainian entries on the MS list first.**
Changes vs. quick score: L9 3 → 2 (SwornTrans exists and DeepL could add layouts); others kept; weighted 3.2 → 3.2 (3.15 rounded half up).

**Cheapest validation test (≤1 week, ≤200 PLN):** count translators of Ukrainian on the MS list; e-mail 40 of them a free draft of one sample document of a type they translate often (no client documents); compare against SwornTrans's 3 free pages on the same sample; ask for a price.

**Kill criteria:** fewer than ~1,000 Ukrainian-language sworn translators on the list; or SwornTrans already produces Polish-convention drafts of equal quality; or <5 of 40 translators reply with interest.

**Confidence:** low-medium (prices, law and Western tools sourced; translator count and willingness to pay not).

**Sources** (accessed 2026-11-05):
1. https://www.stork.ai/en/sworntrans
2. https://x-doc.ai/use-cases/en/online-birth-certificate-translation-localization
3. https://www.cbinsights.com/company/translatoai
4. https://www.bluente.com/blog/translate-documents-to-ukrainian
5. https://lexlege.pl/ustawa-o-zawodzie-tlumacza-przysieglego/rozdzial-2-nabywanie-i-utrata-prawa-do-wykonywania-zawodu-tlumacza-przysieglego/4972/
6. https://www.wroclaw.pl/dla-mieszkanca/tlumacz-przysiegly-gwarancja-bezpiecznego-zalatwienia-spraw-w-urzedach
7. https://cenauslug.pl/przewodnik/tlumaczenia-przysiegle
8. https://www.prawo.pl/student/nostryfikacje-dyplomow-utrudnia-brak-tlumaczy-z-ukrainskiego,514262.html
9. https://openrouter.ai/google/gemini-2.5-flash
10. https://artificialintelligenceact.eu/annex/3/
11. Internal: [TH69 check](../../poland-check/C/TH69-translation-localisation.md), [write-up 002](002-teczka-legalizacyjna.md)

Coverage: 5 web searches/fetches for this write-up plus the TH69 check's sources (sworn-translator counts, AI certified-translation tools, Polish page rates, shortage reports, SwornTrans pricing). Not found: number of sworn translators of Ukrainian, SwornTrans language list, any graveyard case, translator demand for such a tool.
