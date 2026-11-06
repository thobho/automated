# 014 — Sekretariat PISP (court-delivery inbox, deadline calendar and intake for small kancelarie)

**One-liner:** Every morning the agent picks up new deliveries for a small law firm from the Portal Informacyjny Sądów Powszechnych (PISP), classifies each pismo (wyrok, postanowienie, wezwanie do uzupełnienia braków, odpis apelacji, zawiadomienie o terminie), computes the KPC/KPK deadline from the delivery date with the rule shown, puts it in the firm's calendar, and drafts a client update and a first outline of the response for the attorney to confirm. Later modules: intake of new client enquiries and e-Doręczenia letters (merges L060, L061).
**Field:** legal-compliance | **Type:** SaaS | **B2B** · shortlist id L059 (merges L060, L061)

**Western analogues:**
- **JUPUS** (DE, Cologne): "KI-Sekretariat" for law firms (client enquiries, appointment booking, case intake, drafting documents up to full briefs). **€13M Series A led by Semapa Next, with NRW.BANK (published 2026-06-23)**, total funding over €20M; **ARR quadrupled in 2025**, users and processed cases more than doubled, headcount 70, "more than 2,000 lawyers in Germany"; plans to expand across Europe, no country named ([HTGF, 2026-06-23](https://www.htgf.de/jupus-sichert-sich-13-millionen-euro-in-series-a/)). Earlier €6.5M seed led by Acton Capital ([HTGF](https://www.htgf.de/jupus-schliesst-seed-runde-ab/)). Price in the TH10 check: 97 EUR/user/month + 149 EUR platform fee, phone AI +99 EUR/month ([jupus.de](https://www.jupus.de/), accessed 2026-11-03 in TH10).
- **LawX** (DE) appears in the TH10 check; not re-checked here.
- JUPUS's court-side job is the German beA mailbox; the Polish counterpart is PISP. JUPUS does not appear to read beA deadlines automatically (not verified; its pitch is intake and drafting).

**Spread:** TH10 law-practice operations: DE (JUPUS, LawX), CA (Clio), CL (Lemontech), TR (Safahat.ai) ([TH10 check](../../poland-check/A/TH10-law-practice-operations-ai-secretariat.md)). The "AI secretariat" form with traction is German only (since 2023).

**Does the Western leader already work in Poland?** No. JUPUS is German-only and built around German professional rules (BRAO, §203 StGB); Clio has no Polish court integration or PLN pricing (TH10 check). Not tried hands-on: JUPUS is demo-led. **But the Polish incumbent already covers the plumbing** (see Polish competition): Wolters Kluwer's LegalDesk and Kancelaria Prawna already pull PISP deliveries and hearing dates.

**Polish adaptation, i.e. the edge:**
- **PISP is now the default court channel for attorneys.** Since 14 March 2024 every practising adwokat and radca prawny must have a PISP account (art. 37d Prawo o adwokaturze and the matching radca rule), and where the court cannot deliver through its system it places the letter in the portal; delivery is effective on the confirmed reading date or **after 14 days** if unread (ustawa of 7 July 2023 amending the KPC, art. 131¹a) ([prawo.pl, 2024-02](https://www.prawo.pl/prawnicy-sady/kiedy-adwokat-radca-wniesie-pismo-procesowe-przez-portal-sadowy,525383.html); [lexlege art. 131¹a KPC](https://lexlege.pl/kpc/art-131-1a/)). The Supreme Court treats the 14-day rule as a fiction of delivery after which reading has only an informational effect (III CZ 37/22, search excerpt, [SN PDF](https://www.sn.pl/sites/orzecznictwo/Orzeczenia3/III%20CZ%2037-22.pdf)). The bar's own guide lists a 2025-09-10 amendment and changes from 1 March 2026 for filing through the portal (search excerpt of [adwokatura.pl guide](https://www.adwokatura.pl/admin/wgrane_pliki/file-poradnik-portal-30-44266.pdf); details **unverified**).
- **Deadline rules are local and unforgiving:** KPC and KPK periods (7 days for a wniosek o uzasadnienie, 14 days for apelacja from delivery of the judgment with reasons, 7 days for zażalenie; general knowledge, to be encoded from ISAP), plus the delivery fiction above and holidays. A foreign entrant would need Polish procedure, Polish legal language (M52) and the portal.
- **Professional secrecy** (tajemnica adwokacka/radcowska) and RODO push towards EU hosting and no training on client data.

**Target customer in Poland:** solo and small firms (1–5 attorneys) without a full-time secretary. About **22.9k practising adwokaci and 42.7k practising radcy prawni** (mid-2025, Sejm interpellation answer citing the bar bodies, [Sejm PDF](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDMXK2C/i12392-o1.pdf), via TH10); the share in small firms is not quantified. CEE: CZ has a comparable data box (datová schránka), but rules differ per country; expansion is a rebuild.

**Demand driver:** regulatory (mandatory PISP accounts and delivery fiction since 2024, more portal-only filings from 2026) and DD7 labour scarcity for legal secretaries (TH10). No demographic driver.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Wolters Kluwer **LegalDesk** | cloud practice management; "extended PISP integration": reading case data, **receiving deliveries, hearing dates**, participants and documents (Grow and Expand plans) | Start 85, **Grow 170**, Expand 242 PLN net/month (search excerpt of [LegalDesk versions](https://www.wolterskluwer.com/pl-pl/solutions/legaldesk/wersje)) | no sign of LLM classification, deadline computation from the content or drafted client updates (not confirmed; page blocks bots) |
| Wolters Kluwer **Kancelaria Prawna** | desktop/online suite; Portal Informacyjny module reads cases and downloads documents, overview of deliveries from all appeals (since 2021) | not published | same |
| ≥30 other practice-management programs | cases, calendars, invoicing | various | mostly manual PISP work (TH10) |
| PISP itself | inbox, notifications | free | no deadline calendar or classification |
| ChatGPT / LEX AI tools | explain a pismo if pasted | free / in LEX subscription | no portal pickup, secrecy concerns with pasting |
| Voice receptionists (Fonio, Ainora, see TH26) | phone intake | 169–499 PLN/month | no court side |
No Polish product found (two searches) that classifies PISP deliveries and computes deadlines with an LLM.

**Evidence of Polish demand:** indirect. Wolters Kluwer sells PISP delivery pickup as a paid-tier feature, which shows firms pay for this chore. Autocomplete "e-doręczenia kancelaria", "program dla kancelarii" (TH10). Practitioners discuss disciplinary exposure for not handling the portal (prawo.pl above). No attorney found asking for an AI deadline tool.

**MVP scope (≤6 weeks):**
1. Input without automated login first: the attorney forwards the PISP notification or drops the downloaded PDF into an inbox/folder (avoids the access-terms risk); automated pickup only if a sanctioned route is confirmed.
2. Classifier for the 15 most common civil-procedure document types, extraction of court, sygnatura, delivery date.
3. Rules engine in code for the KPC civil deadlines (delivery fiction, holidays, the main periods), each output with the article cited; attorney must confirm before it enters the calendar (Google/Outlook ICS).
4. Draft client update e-mail and a response outline in Polish.
5. Tests: golden files of anonymised pisma → expected type, deadline date and article.
KPK and e-Doręczenia later.

**Monetization:** 129 PLN net/month per attorney, VAT invoice; budget line = secretary hours and missed-deadline risk (malpractice insurance excess, unverified). **Unit economics:** assume ~60 deliveries per attorney per month (estimate) × ~4k input + 1k output tokens = 0.24M in / 0.06M out; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M tokens, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash)) ≈ US$0.22 (~1 PLN). EU hosting, storage, e-mail ~10 PLN per attorney (estimate). Gross margin ~90%. **Customer count:** 10k PLN MRR ≈ 78 attorneys; reachable base ~65k practising attorneys (Sejm source) ≫ 20×, so the §3 sanity check passes.

**Distribution, first 10 customers:** the founder's own contacts among attorneys; local bar chambers (ORA, OIRP) run trainings on PISP and e-Doręczenia, so a free webinar "PISP bez stresu" through one chamber; aplikant Facebook groups; LinkedIn posts with a free deadline calculator as lead magnet (SEO "termin na apelację kalkulator").

**Regulation:** AI Act: Annex III point 8 covers AI used by or for judicial authorities to research and interpret facts and law; a tool for attorneys' own calendars is not that, so **not high-risk** ([Annex III](https://artificialintelligenceact.eu/annex/3/)); transparency only. RODO and professional secrecy: processing agreement, EU hosting, no training on data. Deadline errors are the attorney's responsibility, but the product's reputation depends on zero wrong dates. Automated access with the attorney's login: PISP terms not read (unverified); MVP avoids it.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Solo attorneys without a secretary treat it as a cheaper substitute for a part-time assistant | M | H | 5 of the first 20 trial users keep using it after 30 days |
| O2 | The 2025–2026 KPC changes push more traffic and more filing obligations through the portal, raising the daily load | M | M | bar chambers schedule new trainings on portal changes |
| O3 | A bar chamber or a professional-insurance broker recommends it as a deadline-safety tool | L | H | one chamber accepts a joint webinar |
| O4 | Intake and client-update modules (JUPUS's core) raise revenue per firm | M | M | trial users ask for intake of new enquiries |
| O5 | A free deadline calculator ranks on "termin na apelację" queries and feeds sign-ups | M | L | calculator gets 500 visits/month within 3 months |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Wolters Kluwer adds LLM classification and deadline suggestions to LegalDesk/Kancelaria Prawna, which already pull PISP deliveries | H | H | "AI" appears in LegalDesk release notes |
| R2 | No sanctioned route to read PISP automatically; manual forwarding is too much friction | M | H | trial users stop forwarding within 2 weeks |
| R3 | One wrong deadline destroys trust in a word-of-mouth profession | M | M | attorneys correct >2% of computed dates |
| R4 | Secrecy and RODO questions slow every sale | M | M | firms ask for a DPIA or ISO certificate before a trial |
| R5 | Small firms buy slowly and on trust; 40 h/month of sales is not enough | H | M | <3 paying firms after 2 months of outreach |

O sum 6+4+3+4+2 = 19; R sum 9+6+4+4+6 = 29. R − O = 10 ≥ 6, and R1 is H×H without mitigation in the MVP (only positioning for firms outside Wolters Kluwer) → **band down one** (§4.3).

**Success signals:**
- Western analogue durable signals: JUPUS replaces secretary hours (signal 1, "up to 70 hours a month" company claim), a daily owned chore (signal 2), ARR ×4 and users ×2 in 2025 (signal 4-like expansion, company figure via investor) ([HTGF](https://www.htgf.de/jupus-sichert-sich-13-millionen-euro-in-series-a/)); per-user pricing. No retention or NRR. Durability score ~5 → **promising**.
- Hype warnings: none found.
- Polish adaptation can reproduce: replaced spend = secretary hours; first channel = bar chambers and personal network; retention driver = daily deliveries and the calendar it owns. Defensibility is weak because the incumbent owns the portal integration.

**Graveyard:** none found in two searches for failed AI secretariats or court-deadline tools; not searched further.

**Scores (1–5):** L1 3 · L2 4 · L3 2 · L4 4 · L5 4 · L6 3 · L7 3 · L8 3 · L9 2 | **Weighted:** 3.2 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). The problem is real, daily and mandatory for ~65k attorneys, but the hard part (PISP pickup) is already a paid feature of Wolters Kluwer's suites, so the LLM layer on top is a feature the incumbent can add in one release. **Recommendation: keep only as a module idea (deadline engine) unless a sanctioned PISP access route and firms outside the WK ecosystem are confirmed.**
Changes vs. quick score: L2 3 → 4 (JUPUS Series A and ARR ×4 sourced), L3 4 → 2 (LegalDesk and Kancelaria Prawna already pull PISP deliveries), L5 3 → 4 (attorney counts and the 2024 PISP obligation sourced, paid workaround exists), L7 2 → 3 (MVP avoids automated login), L9 2 kept; weighted 3.2 → 3.2.

**Cheapest validation test (≤1 week, ≤200 PLN):** landing page "Termin z PISP w kalendarzu w 1 minutę" plus a free online KPC deadline calculator; post in two aplikant/attorney Facebook groups and ask 10 attorneys from the founder's network whether they use LegalDesk/Kancelaria Prawna and how they log PISP deadlines today. Target: 30 waitlist sign-ups, of whom ≥10 are not on a Wolters Kluwer suite.

**Kill criteria:** most interviewed small firms already get PISP deliveries in a WK suite; or Wolters Kluwer announces AI deadline handling; or no attorney will forward deliveries for a 2-week trial.

**Confidence:** medium on the legal facts and the incumbent's features, low on willingness to pay.

**Devil's advocate (T24, 2026-11-06):**
- *The incumbent already holds every piece.* Wolters Kluwer owns the PISP pickup (LegalDesk Grow/Expand, Kancelaria Prawna), the LEX content and, since 2026, an AI layer for Polish lawyers: Libra by Wolters Kluwer launched in Poland on 2026-02-04 with LEX content, summaries of judgments and "timelines" ([Libra journal](https://libratech.ai/journal/libra-expands-to-poland-trusted-lex-content-from-wolters-kluwer-now-available-in-libra-by-wolters-kluwer), fetched 2026-11-06), and Libra features became available inside LEX on 2026-10-01 (Wolters Kluwer news title, [search result](https://www.wolterskluwer.com/en/news/lex-libra-ai-capabilities-directly-available-in-lex-poland), page 403 to fetch). LegalDesk is advertised as integrated with LEX (search excerpt of [LegalDesk page](https://wolterskluwer.com/pl-pl/solutions/legaldesk/zarzadzanie-kancelaria), 403). Neither Libra nor LegalDesk mentions deadline computation from PISP deliveries yet, but connecting an AI it already sells to deliveries it already downloads is one release away. R1 H×H is now better evidenced than when written.
- *In Germany this is an incumbent feature, not a product.* AI deadline extraction from beA mail is pitched by automation agencies and reportedly sold as an add-on to Advoware (single vendor-side source, **unverified**; [KI-Syndikat use case](https://www.ki-syndikat.de/usecases/recht/04-fristenmanagement/), search excerpt 2026-11-06); beA has no open API, only a BRAK interface for practice-software vendors (same excerpt). JUPUS's sourced traction is for intake, booking and drafting; its Series A release does not mention beA deadlines (HTGF, re-fetched 2026-11-06). So the durable Western signal belongs to the later intake module, not to the MVP wedge.
- *ChatGPT will absorb it.* An attorney can paste a pismo into ChatGPT or LEX/Libra and ask for the deadline; what is left is the portal pickup (which this MVP deliberately skips) and the calendar entry. Without automated pickup, the product is a forwarding inbox plus a rules table.
- *Polish customers won't pay this.* 129 PLN/attorney sits on top of LegalDesk Grow at 170 PLN; firms already in WK will wait for the bundled feature, and firms outside WK are the ones least likely to pay for software. No attorney found asking for it.
- *Second competitor search (2026-11-06):* "AI kancelaria PISP doręczenia terminy", "polski startup AI dla kancelarii ... terminów procesowych": no Polish product computing deadlines from PISP deliveries found. New Polish legal-AI players do document analysis, not deadlines: VAI Legal (Volaria AI S.A., commercialised 2026-03-31, [Bankier](https://www.bankier.pl/wiadomosc/VOLARIA-AI-S-A-Rozpoczecie-komercjalizacji-produktu-VAI-Legal-platformy-AI-do-analizy-dokumentow-prawnych-9107152.html), search excerpt); TTMS custom Azure OpenAI summaries of case files for one firm ([TTMS case study](https://ttms.com/pl/case-studies/ai-implementation-for-court-document-analysis-at-a-law-firm/), fetched; no deadlines or PISP). Ultima Ratio's 2024 AI plans concern online arbitration, not firm deadlines ([prawo.pl, 2024-03-09](https://www.prawo.pl/biznes/ai-juz-wkrotce-w-ultima-ratio,525852.html)).
- *Claims re-checked.* JUPUS €13M Series A, ARR ×4 in 2025, >2,000 lawyers: confirmed (HTGF). Portal filing changes from 1 March 2026: confirmed only as a topic by a prawo.pl headline "Portal informacyjny po 1 marca 2026 r." ([prawo.pl](https://www.prawo.pl/prawnicy-sady/6-marca-konferencja-ai-legal-change-summit-2026,1538419.html), search result title; content not read). LegalDesk PISP features and prices: excerpts only, page still 403.
- *Success signals.* JUPUS is durable (funding, ARR growth, user count), not hype, but for a different job step (intake). L2 4 overstates the traction behind the MVP wedge.
- *Opportunity/risk lists.* Independent; O3 (bar chamber endorsement) honestly L. R1 H×H holds; R5 H×M fair for a trust-driven profession.

**Review changes (T24, 2026-11-06):** L2 4 → 3 (JUPUS's durable traction is for intake and drafting, not court-mailbox deadlines; the German deadline feature lives inside incumbent software). Reviewed scores: L1 3 · L2 3 · L3 2 · L4 4 · L5 4 · L6 3 · L7 3 · L8 3 · L9 2 | weighted 0.36+0.36+0.24+0.60+0.60+0.30+0.24+0.24+0.16 = 3.10 → **3.1** (shortlist quick 3.2 replaced). Score band 5–15%; §4: O 19, R 29, R − O = 10 and R1 H×H unmitigated → down one → **<5%** (unchanged). Not rejected: the WK suites do not compute deadlines yet, but keep only as a deadline-engine module; new kill criterion: any WK/Libra announcement of AI handling of PISP deliveries.

**Sources** (accessed 2026-11-05/06):
1. https://www.htgf.de/jupus-sichert-sich-13-millionen-euro-in-series-a/
2. https://www.htgf.de/jupus-schliesst-seed-runde-ab/
3. https://www.jupus.de/ (via TH10 check, accessed 2026-11-03)
4. https://www.prawo.pl/prawnicy-sady/kiedy-adwokat-radca-wniesie-pismo-procesowe-przez-portal-sadowy,525383.html
5. https://lexlege.pl/kpc/art-131-1a/
6. https://www.sn.pl/sites/orzecznictwo/Orzeczenia3/III%20CZ%2037-22.pdf (search excerpt)
7. https://www.adwokatura.pl/admin/wgrane_pliki/file-poradnik-portal-30-44266.pdf (search excerpt)
8. https://www.wolterskluwer.com/pl-pl/solutions/legaldesk/wersje (search excerpt; page returns 403 to fetch)
9. https://wolterskluwer.com/pl-pl/solutions/kancelaria-prawna/program-do-zarzadzania/prowadzenie-spraw (search excerpt)
10. https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDMXK2C/i12392-o1.pdf (via TH10)
11. https://openrouter.ai/google/gemini-2.5-flash
12. https://artificialintelligenceact.eu/annex/3/
13. Internal: [TH10 check](../../poland-check/A/TH10-law-practice-operations-ai-secretariat.md)
14. https://libratech.ai/journal/libra-expands-to-poland-trusted-lex-content-from-wolters-kluwer-now-available-in-libra-by-wolters-kluwer (2026-11-06, T24)
15. https://www.wolterskluwer.com/en/news/lex-libra-ai-capabilities-directly-available-in-lex-poland (2026-11-06, T24, search title; 403 to fetch)
16. https://wolterskluwer.com/pl-pl/solutions/legaldesk/zarzadzanie-kancelaria (2026-11-06, T24, search excerpt; 403)
17. https://www.ki-syndikat.de/usecases/recht/04-fristenmanagement/ (2026-11-06, T24, search excerpt)
18. https://www.bankier.pl/wiadomosc/VOLARIA-AI-S-A-Rozpoczecie-komercjalizacji-produktu-VAI-Legal-platformy-AI-do-analizy-dokumentow-prawnych-9107152.html (2026-11-06, T24, search excerpt)
19. https://ttms.com/pl/case-studies/ai-implementation-for-court-document-analysis-at-a-law-firm/ (2026-11-06, T24)
20. https://www.prawo.pl/biznes/ai-juz-wkrotce-w-ultima-ratio,525852.html (2026-11-06, T24)
21. https://www.prawo.pl/prawnicy-sady/6-marca-konferencja-ai-legal-change-summit-2026,1538419.html (2026-11-06, T24, search title)

Coverage: 8 web searches/fetches (JUPUS funding, PISP obligations and the delivery fiction, PISP integrations in Polish software, LegalDesk prices, Polish AI-secretariat start-ups). Not found: an official PISP API for vendors or PISP automation terms, the share of attorneys in small firms, the contents of the 2026 KPC change, any failed analogue.
