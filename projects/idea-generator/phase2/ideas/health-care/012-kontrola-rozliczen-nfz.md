# 012 — Kontrola rozliczeń NFZ (pre-submission settlement check for outpatient clinics)

**One-liner:** Before a private outpatient clinic with an NFZ contract (AOS specialist clinics, rehabilitation) sends its monthly report, the agent reads the export of visits and the documentation behind them, and flags services that were performed but not reported, codes and service combinations NFZ will reject, missing documentation elements, and how far the clinic is from its contract value per product, with a plain-Polish note for the settlement clerk on what to fix. No clinical decisions and no code suggestions that raise the price without documentation.
**Field:** health-care | **Type:** SaaS | **B2B** · shortlist id L108

**Western analogues:**
- **Parallel** (FR, YC): AI agents on top of existing hospital software, starting with medical coding into the French PMSI; **€/US$20M Series A led by Index Ventures (2026-03-19)** after a US$3.5M seed (2025-04) ([Index Ventures](https://www.indexventures.com/perspectives/parallel-raises-20m-to-tackle-hospital-inefficiencies-with-ai-agents/); [Tech.eu](https://tech.eu/2026/03/19/parallel-raises-20m-to-scale-ai-solutions-for-hospital-administration/)). "Several dozen hospitals" served (profile-site excerpt, unverified).
- **Arintra** (US, YC): autonomous coding and denial prevention for health systems; **US$21M Series A led by Peak XV (2025-08)** ([HIT Consultant](https://hitconsultant.net/2025/08/12/arintra-raises-21m-to-expand-beyond-autonomous-medical-coding/)); a later US$25M round and "US$5bn annualised claims value" are from a secondary source, unverified.
- Tennr, Trellis, Candid, Codes Health (US) solve US payer problems (faxed referrals, ICD-10-CM/CPT claims) that do not exist in the Polish single-payer system (TH03 check).

**Spread:** TH03 healthcare back office: US (many), FR (Parallel), CA (Asepha) ([TH03 check](../../poland-check/B/TH03-healthcare-back-office-automation.md)). Parallel is the relevant model: one national payer's coding rules, agents on top of local software. No CEE player.

**Does the Western leader already work in Poland?** No. Parallel works on French hospital software and PMSI; its Series A funds "international expansion" but names no market (not confirmed). US coding tools are built on US code sets. Not tried hands-on (demo-led, hospital-only).

**Polish adaptation, i.e. the edge:**
- **NFZ rules are a national, changing rulebook:** zarządzenia Prezesa NFZ per service type (AOS, rehabilitation), ICD-10 and ICD-9 PL, product codes, SWIAD messages through Portal Świadczeniodawcy/SZOI (TH03 check).
- **Contract limits now matter more.** NFZ paid 1.62 bn PLN for unlimited over-contract services and 2.61 bn PLN for other limited ones (after degresja) for 2025 ([NFZ, 2026-03-03](https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/nfz-podsumowal-skale-nadwykonan-za-2025-r-platnosci-jeszcze-w-marcu,8902.html)). In March 2026 NFZ proposed paying only **40% of the value** of over-contract CT, MRI, gastroscopy and colonoscopy and moving over-contract settlement to year-end; in AOS unlimited services, the number of services rose ~20% in 2021–2025 but their value rose 152% ([NFZ, 2026-03-11](https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/zapanowac-nad-nadmiernymi-kosztami-fundusz-przedstawil-propozycje-zmian-w-finansowaniu-czesci-swiadczen-diagnostycznych,8908.html)). Whether the 40% rule was adopted was **not checked**. Limited services beyond the contract are often refused and recovered only in court (search excerpt, PDF not read; [DZP](https://www.dzp.pl/files/shares/Art/Rozliczanie_swiadczen_ponadlimitowych.pdf)).
- **The data sits in the clinic's HIS** (KAMSOFT, CGM, Optimed, MyDr, Asseco), which already produces the report; the product must read its exports. A foreign entrant would need NFZ rules, Polish code sets and HIS formats: a deep moat, but also deep work for the founder.

**Target customer in Poland:** private outpatient clinics with NFZ contracts (AOS, rehabilitation, ASDK diagnostics), with a settlement clerk or an outsourced settlement service. National count of AOS contractors **not found** in this pass. Home rehabilitation alone: 2,752 contracts in December 2024 (Sejm debate, search excerpt) and 591 → 694 providers in a year (Medical Press via search excerpt; figures disagree, unverified). Hospitals are out of scope (tenders, HIS bundles). CEE: no; each payer is different.

**Demand driver:** regulatory and financial: NFZ cost pressure, over-contract payment cuts and the AOS value surge (above); DD3 queues and DD7 scarce medical admin staff ("specjalista ds. rozliczeń z NFZ" is a common job title; job-seeker autocomplete "rozliczenia nfz praca/kurs/szkolenie", TH03 check).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| HIS vendors (KAMSOFT, CGM, Optimed, MyDr, Asseco) | build and send SWIAD reports, basic validation | licences, not checked | validate format, not completeness against documentation or limit strategy |
| JGP groupers/optimisers (e.g. SGA) | settlement variants for hospital JGP | not published | hospitals only (TH03 check) |
| NFZ tools (Portal Świadczeniodawcy, JGP query) | return errors after submission | free | after the fact |
| Settlement clerks, outsourced rozliczenia firms, training seminars | people | salaries / fees, not checked | manual |
| ChatGPT | explaining a zarządzenie | free | no access to the clinic's data; RODO problem with patient data |

**Evidence of Polish demand:** indirect only: job titles, paid courses and autocomplete (TH03 check); NFZ's own figures on over-contract volumes (above). No clinic owner asking for a tool was found.

**MVP scope (≤6 weeks), only with a pilot clinic:**
1. One service type (AOS in one specialty, or ambulatory rehabilitation) and one HIS export format; agreement with a pilot clinic for anonymised monthly exports.
2. Rules engine in code from the current zarządzenie (product codes, required ICD-9 procedures, visit-type rules, documentation fields), versioned per zarządzenie.
3. LLM reads visit notes to check that each reported service is documented and that documented services were reported (completeness both ways); never proposes a higher-priced code without a documented basis.
4. Contract dashboard: value used per product vs. plan, projected year-end, over-contract share.
5. Tests: fixtures of anonymised visits → expected flags; regression set rerun on each new zarządzenie.

**Monetization:** 399 PLN/month for a clinic up to ~1,500 NFZ visits a month, 799 PLN above; VAT invoice; budget line = settlement clerk hours and unreported services. **Unit economics:** 1,500 visits × ~1.5k tokens of notes each ≈ 2.3M input / 0.3M output tokens a month; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$1.45 (~6 PLN); EU hosting with stricter security (~100 PLN/month per clinic, estimate). Gross margin ~70–75% at 399 PLN. **Customer count:** 10k PLN MRR ≈ 25 clinics at 399 PLN; the reachable base is unknown (AOS contractor count not found), so the §3 sanity check cannot be passed with a source.

**Distribution, first 10 customers:** through the pilot clinic's network and its HIS vendor's user groups; outsourced settlement firms and NFZ-settlement trainers as resellers; regional associations of private providers (Porozumienie Zielonogórskie is primary care; AOS associations not checked).

**Regulation:** AI Act: not high-risk as long as it makes no clinical decisions and is not a medical device (administrative use, outside [Annex III](https://artificialintelligenceact.eu/annex/3/)). RODO art. 9 health data: processing agreement, EU hosting, data minimisation, audit logs. Clinics may be KSC/NIS2 entities: supplier security questionnaires. Upcoding risk: NFZ audits; the product must only check documentation against reports, never optimise codes upward.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | NFZ's 40% over-contract rule and year-end settlement make limit tracking worth real money per clinic (NFZ proposal, March 2026) | M | H | the rule is adopted for at least one service type |
| O2 | Frequent zarządzenie changes keep the rulebook moving, so clinics need the check every month | H | M | two rule changes affecting the pilot specialty within 6 months |
| O3 | An outsourced settlement firm resells it to its 20+ clinic clients | M | M | one firm agrees to a joint pilot |
| O4 | Unreported but documented services found in the pilot are worth more than the fee, a measurable ROI case | M | M | pilot shows ≥1,000 PLN/month of missed services |
| O5 | A HIS vendor offers it as an add-on in its marketplace | L | H | a vendor partner programme accepts the integration |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | No clinic gives access to exports, or HIS export formats differ so much that each clinic is custom work | H | H | no pilot signed after 15 contacts |
| R2 | HIS vendors' built-in validation already catches most errors, so the marginal value is small | M | H | pilot finds <1% of visits with a fixable issue |
| R3 | The founder lacks NFZ domain knowledge; rules mistakes cost trust in a conservative market | H | M | settlement clerks correct the rules in every review |
| R4 | Security and RODO demands (art. 9 data, NIS2 questionnaires) raise cost and slow every sale | M | M | clinics ask for ISO 27001 or a DPIA before a trial |
| R5 | Being seen as an upcoding tool attracts NFZ audit attention to customers | L | H | a pilot clinic gets an NFZ control linked to corrected reports |

O sum 6+6+4+4+3 = 23; R sum 9+6+6+4+3 = 28. R1 is H×H; the MVP's mitigation (secure the pilot before building) reduces cost, not the risk itself; R − O = 5 < 6. Applying §4.3 on the H×H risk with only partial mitigation → **band down one**.

**Success signals:**
- Western analogue durable signals: Parallel replaces coder hours in hospitals (signal 1), on a monthly, owned problem (signal 2), deployed on top of existing software in about a week (signal 6, company claim), with a large follow-on round a year after seed; Arintra sells denial prevention, value tied to recovered revenue (signal 7-like) ([Index Ventures](https://www.indexventures.com/perspectives/parallel-raises-20m-to-tackle-hospital-inefficiencies-with-ai-agents/); [HIT Consultant](https://hitconsultant.net/2025/08/12/arintra-raises-21m-to-expand-beyond-autonomous-medical-coding/)). No retention or NRR data. Durability score ~4 → **promising**.
- Hype warnings: none found.
- Polish adaptation can reproduce: replaced spend = clerk hours and unreported or unpaid services; first channel = pilot clinic network and settlement outsourcers; retention driver = monthly cycle and versioned NFZ rulebook.

**Graveyard:** none found for NFZ settlement tools; not searched for EU coding start-ups that failed.

**Scores (1–5):** L1 3 · L2 3 · L3 4 · L4 5 · L5 3 · L6 3 · L7 2 · L8 2 · L9 3 | **Weighted:** 3.3 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). The moat is the deepest in the batch and NFZ's own figures show money at stake, but the product cannot start without a pilot clinic's data and NFZ domain expertise the founder does not have, and the customer base was not sized. **Recommendation: only pursue if a clinic owner or settlement firm in the founder's network offers data and domain help; otherwise drop.**
Changes vs. quick score: L1 4 → 3 (most checks are rules, the LLM reads notes), L5 3 kept (driver now sourced, customer count still missing), L7 2 kept; weighted 3.3 → 3.3.

**Cheapest validation test (≤1 week, ≤200 PLN):** call 15 private AOS/rehabilitation clinics and 3 settlement outsourcing firms; ask what share of reported services NFZ rejected or did not pay last year, what they pay for settlement work, and whether they would share one anonymised month for a free check.

**Kill criteria:** no clinic or settlement firm willing to share anonymised data within 3 weeks; or interviewed clinics report rejections/unreported services below ~1% of contract value.

**Confidence:** low-medium (NFZ money flows and Western traction sourced; clinic count, error rates and willingness to share data not).

**Devil's advocate (T24, 2026-11-06):**
- *The driver landed, but in the wrong segment.* NFZ adopted the degression after consultation (published 2026-03-31; URL slug points to zarządzenie 34/2026/DSOZ, number not in the text): services above contract value are paid at **50% for CT/MRI and 60% for gastroscopy/colonoscopy** from 2026-04-01, paid **after year-end**, with children, the colorectal screening programme and DiLO patients excluded; ~625 M PLN expected savings ([NFZ](https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/zarzadzenie-po-konsultacjach-spolecznych-nfz-uwzglednia-czesc-uwag-i-wprowadza-nowy-sposob-rozliczania-nadwykonan-w-diagnostyce,8916.html), fetched 2026-11-06). That makes limit tracking worth money for **imaging and endoscopy providers**, a smaller set of larger firms running RIS/PACS vendors' software, not the AOS/rehabilitation clinics this MVP starts with. O1 is now H likelihood but M impact for the planned wedge.
- *It already works in Polish: NFZ publishes its own checks.* NFZ runs Centralne Warunki Walidacji and Centralne Reguły Weryfikacji, published for providers to unify checks across voivodeship branches ([NFZ](https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/sprawdzenia-z-zakresu-centralnych-warunkow-walidacji-i-centralnych-regul-weryfikacji,8286.html), search excerpt). HIS vendors can implement those rules before submission, which supports R2: the rule-based half of the product is the HIS vendor's job; only the "documented but not reported" check needs an LLM.
- *ChatGPT will absorb it.* Not directly: it has no access to the clinic's HIS data and art. 9 data blocks casual use. The real absorber is the HIS vendor (KAMSOFT, CGM, Asseco), who already owns the export. CGM launched an AI document-extraction tool in the US in January 2026 (CGM INDEX.AI, search excerpt); no Polish rollout found.
- *Polish customers won't pay this.* Unknown: the AOS contractor count is still not found, and no clinic owner asking for this was found on a second search.
- *Western leader localizing in 12 months.* Parallel's Series A funds international expansion, but a national-payer rulebook per country makes Poland unlikely soon. L.
- *Second competitor search (2026-11-06):* "sztuczna inteligencja rozliczenia NFZ weryfikacja sprawozdawczość AI KAMSOFT CGM": no Polish AI settlement-check product found; one PTI 2025 conference paper notes that AI in Polish healthcare is used "mainly for financial purposes (like NFZ settlements)" without naming products ([PTI](https://pti.org.pl/wp-content/uploads/2025/07/4_Czy-SI-nas-uleczy-i-obroni.pdf), search excerpt), which hints that hospitals already do some of this in-house.
- *Success signals.* Parallel (FR) and Arintra (US): large rounds, company-claimed customer counts, no retention or NRR. Promising, not proven; L2 3 is the cap.
- *Opportunity/risk lists.* Independent. O1 re-rated M×H → H×M (adopted, but for diagnostics). R1 H×H is honest; R3 H×M is honest given the founder's profile.

**Review changes (T24, 2026-11-06):** scores unchanged (L1 3 · L2 3 · L3 4 · L4 5 · L5 3 · L6 3 · L7 2 · L8 2 · L9 3; weighted **3.3**; shortlist quick L1 4/L2 2 replaced). O1 M×H → H×M (sum unchanged). §4: O 23, R 28, R1 H×H only partly mitigated → **<5%** unchanged. Not rejected, but if pursued the wedge should move to ASDK imaging/endoscopy limit tracking, where zarządzenie 34/2026/DSOZ now puts money at stake; the AOS completeness check needs the pilot clinic first.

**Sources** (accessed 2026-11-05):
1. https://www.indexventures.com/perspectives/parallel-raises-20m-to-tackle-hospital-inefficiencies-with-ai-agents/
2. https://tech.eu/2026/03/19/parallel-raises-20m-to-scale-ai-solutions-for-hospital-administration/
3. https://hitconsultant.net/2025/08/12/arintra-raises-21m-to-expand-beyond-autonomous-medical-coding/
4. https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/nfz-podsumowal-skale-nadwykonan-za-2025-r-platnosci-jeszcze-w-marcu,8902.html
5. https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/zapanowac-nad-nadmiernymi-kosztami-fundusz-przedstawil-propozycje-zmian-w-finansowaniu-czesci-swiadczen-diagnostycznych,8908.html
6. https://www.dzp.pl/files/shares/Art/Rozliczanie_swiadczen_ponadlimitowych.pdf
7. https://openrouter.ai/google/gemini-2.5-flash
8. https://artificialintelligenceact.eu/annex/3/
9. https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/zarzadzenie-po-konsultacjach-spolecznych-nfz-uwzglednia-czesc-uwag-i-wprowadza-nowy-sposob-rozliczania-nadwykonan-w-diagnostyce,8916.html (2026-11-06, T24)
10. https://www.nfz.gov.pl/aktualnosci/aktualnosci-centrali/sprawdzenia-z-zakresu-centralnych-warunkow-walidacji-i-centralnych-regul-weryfikacji,8286.html (2026-11-06, T24, excerpt)
11. https://pti.org.pl/wp-content/uploads/2025/07/4_Czy-SI-nas-uleczy-i-obroni.pdf (2026-11-06, T24, excerpt)
12. Internal: [TH03 check](../../poland-check/B/TH03-healthcare-back-office-automation.md)

Coverage: 6 web searches/fetches for this write-up (Parallel and Arintra funding, NFZ over-contract figures and the 40% proposal, AOS and rehabilitation contractor counts). Not found: national count of AOS contractors, NFZ rejection rates for outpatient reports, prices of HIS settlement modules or settlement outsourcing, status of the 40% rule.
