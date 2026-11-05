# 019 — AML-in-a-box for small obliged entities

**One-liner:** For a small biuro rachunkowe or estate agency (pośrednik w obrocie nieruchomościami), a web tool that keeps its anti-money-laundering duties under the Polish AML act current: the office-wide written risk assessment and internal procedure, KYC of each client from KRS, CRBR, CEIDG, biała lista and sanctions lists, an individual client risk score with the reasons written out, two-yearly re-assessment reminders, and drafts of GIIF notifications. The LLM drafts the risk narrative and procedure text and reads uploaded documents (umowa spółki, ID scans); the rules engine scores.
**Field:** legal-compliance | **Type:** SaaS | **B2B** · shortlist id L072 (merges L091 AML client file for estate agents)

**Western analogues:**
- **Thirdfort** (UK): ID, source-of-funds and AML checks for law firms and property; **£15M (US$20M) Series A, 2022-03**; clients grew **30 → 700** and staff 10 → 100 between 2020-01 and 2022-03; 500k+ app downloads by individuals ([Biometric Update 2022-03](https://www.biometricupdate.com/202203/thirdfort-secures-20m-in-series-a-funding-as-aml-business-scales), accessed 2026-11-06). Follow-on investment from estate agents Knight Frank and Chestertons (search excerpt). Pre-LLM product (biometrics, open banking).
- **Binderr** (MT): KYC/AML onboarding marketplace for regulated providers, 100+ providers on the platform (company); "AI screening" only in excerpts ([binderr.com](https://binderr.com/), via R5 catalogue).
- **Myriad** (CZ): agent that maps regulatory changes to company controls; US$7.8M seed, 2025-09 ([Lupa.cz](https://www.lupa.cz/aktuality/cesky-startup-byvaleho-inzenyra-v-nvidii-a-googlu-ziskal-160-milionu-na-ai-pro-zvladani-byrokracie/), via R6 catalogue). Not AML-specific.

**Spread:** TH54 compliance agents: UK, MT, CZ, DK, LU (R2, R3, R4, R5, R6). AML for small professional firms specifically: UK (Thirdfort) is the evidence; the LLM-native part of the theme is thin.

**Does the Western leader already work in Poland?** Thirdfort is UK-only (UK ID documents, UK open banking, SRA/HMRC rules); Binderr has no Polish site found; Myriad is not tied to Polish law (TH54 check, R6 row). Not tried hands-on. **But a Polish incumbent already does the core job:** **Comarch Apfino** walks an accounting office through client identification, verification against external databases, client risk scoring and the office's own risk assessment; the office enters only the client's NIP and e-mail and an employee approves the risk level ([INFOR partner article 2024-05-21](https://www.infor.pl/biura-rachunkowe/aml/6611337,comarch-apfino-zautomatyzowal-procesy-aml-oszczedzajac-czas-biurom-ra.html), fetched 2026-11-06; price and user count not stated; no AI mentioned).

**Polish adaptation, i.e. the edge:**
- **Ustawa o przeciwdziałaniu praniu pieniędzy (AML act):** every biuro rachunkowe is an obliged entity, including one that only prepares tax returns and keeps tax books ([INFOR](https://www.infor.pl/biura-rachunkowe/aml/6567138,czy-kazde-biuro-rachunkowe-ma-obowiazek-stosowania-przepisow-ustawy-am.html), search excerpt, accessed 2026-11-06); new duties since 2021-07-31; an office-wide risk assessment and an individual one per client, in writing, updated at least every two years ([Poradnik Przedsiębiorcy](https://poradnikprzedsiebiorcy.pl/-procedura-aml-czyli-nowe-obowiazki-dla-biur-rachunkowych), excerpt, accessed 2026-11-06). Estate agents are obliged entities whatever their size ([prawo.pl](https://www.prawo.pl/biznes/czy-wszyscy-posrednicy-nieruchomosci-musza-przeciwdzialac-praniu-pieniedzy,426879.html), excerpt).
- **Registries:** CRBR (beneficial owners, public and free), KRS (open API), CEIDG, biała lista VAT ([local-moats](../../research/poland/local-moats.md) M09, M10, M13); Polish sanctions list (MSWiA) next to EU lists. CRBR API availability unverified.
- **GIIF** notifications and controls (GIIF and naczelnicy urzędów celno-skarbowych may inspect offices; fines up to 1M PLN cited in guides, excerpt).
- **Dated trigger:** the EU AML Regulation (EU) 2024/1624 (**AMLR**) applies directly from **2027-07-10**, replacing parts of the Polish act's CDD rules for all obliged entities, with accountants and tax advisers explicitly in scope ([Akademia LTCA](https://akademialtca.pl/blog/zmiany-w-przepisach-aml-2027); [LearnSignal](https://www.learnsignal.com/blog/eu-amlr-accountants-what-applies-from-july-2027/), excerpts, accessed 2026-11-06). Every office's procedure will need rewriting.
A foreign entrant needs Polish registries and the Polish act; but so does any Polish rule-based vendor, which already exists.

**Target customer in Poland:** small biura rachunkowe: "slightly over 35,000 active accounting offices" (podatki.biz, undated, via [016](../accounting-tax/016-asystent-klienta-biura.md)); estate agencies (count not found, unverified); also dealers in high-value goods and tax advisers. Buyer: office owner, who is usually the designated AML officer. CEE: AMLR is identical across the EU from 2027, so the procedure layer travels; registries do not.

**Demand driver:** regulatory only (AML act since 2021 for offices; AMLR 2027-07-10). No demographic driver.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| Comarch Apfino | KYC, client risk scoring, office risk assessment for biura | not published | rule-based, Comarch ecosystem; no estate-agent version found |
| Akademia LTCA and similar | AML procedure packs with client and office risk forms, trainings | not published in excerpts ([LTCA procedury](https://akademialtca.pl/sklep/procedury-aml-pakiet-pelny)) | one-off documents, no registry checks |
| RPMS, law firms, AML auditors | procedure drafting, audits | project/hourly ([RPMS](https://rpms.pl/aml-biur-rachunkowych/)) | expensive per hour, not continuous |
| TTMS and enterprise AML vendors | transaction monitoring for banks and larger firms | enterprise | overkill for a 3-person office |
| Word templates + ChatGPT | today's default for many | free | no registry links, no audit trail |

**Evidence of Polish demand:** INFOR runs a dedicated "AML" section for biura rachunkowe ([infor.pl/biura-rachunkowe/aml](https://www.infor.pl/biura-rachunkowe/aml/)); trainers and auditors sell AML packs and courses to offices; one expert comment in search results says that for a small organisation "the best tool is a person" doing a simple manual check (excerpt). No figures on GIIF controls of small offices since 2021 were found (searched 2026-11-06), so enforcement pressure is unmeasured.

**MVP scope (≤6 weeks):**
1. Office onboarding: questionnaire → office-wide risk assessment and internal procedure drafted in Polish, versioned, with AMLR 2027 changes flagged.
2. Client KYC: NIP → KRS/CEIDG/biała lista/CRBR data pulled; beneficial-owner discrepancy check; sanctions screening; rule-based risk score; LLM writes the justification paragraph.
3. Re-assessment calendar (two years, or on change of owner), audit log, PDF export for a GIIF control.
4. Estate-agent variant: transaction-based KYC for buyers/sellers, umowa pośrednictwa checklist (L091).
5. Tests: fixture companies with known structures, golden risk scores, schema checks of drafts.

**Monetization:** 79 PLN/month for up to 100 clients, 149 PLN above; 499 PLN one-off "AMLR 2027 procedure update". **Unit economics:** client KYC ≈ 10k input / 2k output tokens; office procedure ≈ 30k / 15k tokens once; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) a 100-client office costs < US$1/month; sanctions-list data and hosting ~10 PLN. Gross margin >85%. **Customer count:** 10k PLN MRR ≈ 127 offices at 79 PLN; ~35k offices is >200×.

**Distribution, first 10 customers:** accounting-office Facebook groups and the INFOR/biura community with a free "AMLR 2027 checklist"; estate-agent associations (PFRN, regional stowarzyszenia; not checked); bundle with 016 (Asystent klienta biura) for the same buyer.

**Regulation:** AI Act: not high-risk; Annex III covers creditworthiness of natural persons, not AML risk of a client by an obliged entity ([Annex III](https://artificialintelligenceact.eu/annex/3/)); limited-risk only (own reading). RODO: processing ID data and beneficial-owner data under a legal duty; EU hosting; retention 5 years per the AML act (excerpt-level knowledge, not re-read). The office stays responsible; the tool supports.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | AMLR applies 2027-07-10, so every office must update its procedure within the first 12 months: a dated, sourced reason to buy | H | M | "AMLR 2027" checklist downloads ≥300 in a month |
| O2 | Two-yearly re-assessments and every new client create recurring use, not a one-off document | M | M | pilot offices run ≥5 KYCs a month |
| O3 | Estate agents are not covered by Apfino or by accounting-office tools, a niche with no named product | M | M | 3 of 10 agencies called say they do AML on paper |
| O4 | Cheap price (79 PLN) and self-serve setup allow impulse buying without a sales call | M | M | ≥20% of trial offices convert without a call |
| O5 | Offices become a channel for the founder's other office products (016) | L | M | cross-sell to ≥10% of AML customers |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Comarch Apfino and accounting-software vendors (Saldeo, Symfonia) already automate KYC for biura and ship AMLR updates to their base | H | H | offices answer "we have it in Apfino/Optima" |
| R2 | Offices see AML as a one-off template purchase or a training, not a subscription | H | M | most leads only want the 499 PLN procedure |
| R3 | Enforcement on small entities is weak, so urgency stays low until a control happens | M | H | no GIIF control stories in office groups |
| R4 | The duty is checklist-shaped, so rule-based tools match it and the LLM part adds little that customers pay for | H | M | users skip the generated narrative |
| R5 | A missed sanctions hit or wrong risk score is blamed on the tool | L | M | first complaint after a control |

O sum 6+4+4+4+2 = 20; R sum 9+6+6+6+2 = 29. R − O = 9 → **down one band** (rule §4.3); R1 is H×H with only a partial mitigation (estate-agent niche, non-Comarch offices).

**Success signals:**
- Western analogue durable signals: Thirdfort replaces manual checks and fines (signal 1), regulation-driven duty with a named owner (signal 2), client count 23× in two years (30 → 700) with incumbents investing (expansion-like, but no NRR; signal 4 not counted without NRR), integrations with ID and open banking (signal 8), and a hard timing window in the UK's money-laundering regulations (signal 10) ([Biometric Update](https://www.biometricupdate.com/202203/thirdfort-secures-20m-in-series-a-funding-as-aml-business-scales)). Durability score ~4 → **promising**, but not LLM-era.
- Hype warnings: none found for Thirdfort; Binderr's "AI" claim is unclear (catalogue).
- Polish adaptation can reproduce: replaced spend = the auditor or procedure pack and the owner's hours; first channel = office communities around the AMLR 2027 deadline; retention driver = the client KYC archive needed for a control (switching loses the audit trail).

**Graveyard:** none found for small-entity AML tools in Poland or abroad (searched only via TH54 and this pass).

**Scores (1–5):** L1 2 · L2 3 · L3 2 · L4 4 · L5 3 · L6 3 · L7 4 · L8 3 · L9 2 | **Weighted:** 2.9 / 5 | **Chance band:** score → 5–15%; O 20, R 29, R − O = 9 → **<5%**. The duty is real, recurring and gets a dated trigger in July 2027, but Comarch Apfino already automates KYC for accounting offices and the job is rule-shaped, so an LLM product has little edge; estate agents are the only visible unserved niche.
Changes vs. quick score: L1 3 → 2 (rule-shaped duty; the LLM drafts text only), L3 3 → 2 (Comarch Apfino found), others kept; weighted 3.1 → 2.9. Borderline collapse: kept as a write-up because the estate-agent variant and the AMLR 2027 update are testable; T24 may move it to rejected.md.

**Cheapest validation test (≤1 week, ≤200 PLN):** call 15 estate agencies and 15 small biura (from CEIDG/PKD lists) and ask how they do AML today and what they would pay for an AMLR 2027 update; publish a free "AMLR 2027 checklist for biura and pośrednicy" and count downloads and pre-orders.

**Kill criteria:** >50% of offices already use Apfino or software-vendor AML; or <3 of 15 estate agencies say AML is a pain; or <10 pre-orders for the 2027 update.

**Confidence:** medium (duties and the incumbent sourced; enforcement, prices and estate-agent counts not found).

**Devil's advocate (T24, 2026-11-06):**
- *Not innovative by the brief's own test.* The brief requires at least two of four conditions. This idea is not LLM-native (the score and the KYC pull are rules; the LLM writes a justification paragraph), its only analogue with traction (Thirdfort, Series A 2022) is pre-LLM, and it replaces no person's job step that a template does not already replace. Only "new demand" (AMLR 2027) holds. It is a Phase 1-style compliance tool, which is what Phase 2 set out to avoid.
- *It already works in Polish.* Comarch Apfino automates KYC, client scoring and the office risk assessment for biura rachunkowe; accounting-software vendors will ship AMLR 2027 updates to their own base for free or as an upsell.
- *Polish customers won't pay this monthly.* Offices buy AML as a one-off procedure pack or training (LTCA, RPMS), and podatki.biz stresses that the office risk assessment must be individual and approved by the AML officer, so a generated document is a starting draft, not the deliverable ([podatki.biz](https://www.podatki.biz/artykuly/ocena-ryzyka-wedlug-ustawy-aml-co-powinno-sie-w-niej-znalezc_34_48140.htm), search excerpt, 2026-11-06). Enforcement against small offices is unmeasured.
- *The estate-agent niche is not empty either.* A second search ("AML dla pośredników nieruchomości program … ocena ryzyka klienta", 2026-11-06) found RPMS selling AML procedures to estate agents and TTMS marketing automated client risk scoring, sanctions and PEP screening to the real-estate sector ([RPMS](https://rpms.pl/procedura-przeciwdzialania-praniu-brudnych-pieniedzy-aml-w-praktyce-posrednikow-nieruchomosci/); [TTMS](https://ttms.com/pl/ryzyka-aml-w-branzy-nieruchomosci-jak-automatyzacja-zmniejsza-podatnosc-na-naduzycia/), excerpts). The only "unserved" segment found in T23 is served by services and an enterprise vendor.
- *Success signals.* Thirdfort is durable but not an LLM product; L2 3 stays only because the rubric scores the analogue's traction.
- *Opportunity/risk lists.* Independent and honest; R1 H×H is evidenced (Apfino).

**Review changes (T24, 2026-11-06):** scores unchanged (L1 2 · L2 3 · L3 2 · L4 4 · L5 3 · L6 3 · L7 4 · L8 3 · L9 2; weighted **2.9**; band <5% after §4: O 20, R 29). **Rejected** and moved to [rejected.md](../../rejected.md): fails the brief's "at least two innovative conditions" test, the core job is taken for biura (Comarch Apfino) and the estate-agent niche has service and vendor offers. If AMLR 2027 is worth anything to the founder, it is as a free lead magnet for idea 016, not a product.

**Sources** (accessed 2026-11-06 unless noted):
1. https://www.biometricupdate.com/202203/thirdfort-secures-20m-in-series-a-funding-as-aml-business-scales
2. https://binderr.com/ (accessed 2026-11-01)
3. https://www.lupa.cz/aktuality/cesky-startup-byvaleho-inzenyra-v-nvidii-a-googlu-ziskal-160-milionu-na-ai-pro-zvladani-byrokracie/ (accessed 2026-11-01)
4. https://www.infor.pl/biura-rachunkowe/aml/6611337,comarch-apfino-zautomatyzowal-procesy-aml-oszczedzajac-czas-biurom-ra.html
5. https://www.infor.pl/biura-rachunkowe/aml/6567138,czy-kazde-biuro-rachunkowe-ma-obowiazek-stosowania-przepisow-ustawy-am.html
6. https://poradnikprzedsiebiorcy.pl/-procedura-aml-czyli-nowe-obowiazki-dla-biur-rachunkowych
7. https://www.prawo.pl/biznes/czy-wszyscy-posrednicy-nieruchomosci-musza-przeciwdzialac-praniu-pieniedzy,426879.html
8. https://akademialtca.pl/blog/zmiany-w-przepisach-aml-2027
9. https://www.learnsignal.com/blog/eu-amlr-accountants-what-applies-from-july-2027/
10. https://akademialtca.pl/sklep/procedury-aml-pakiet-pelny
11. https://rpms.pl/aml-biur-rachunkowych/
12. https://www.infor.pl/biura-rachunkowe/aml/
13. https://openrouter.ai/google/gemini-2.5-flash (accessed 2026-11-05)
14. https://artificialintelligenceact.eu/annex/3/
15. https://www.podatki.biz/artykuly/ocena-ryzyka-wedlug-ustawy-aml-co-powinno-sie-w-niej-znalezc_34_48140.htm (T24)
16. https://rpms.pl/procedura-przeciwdzialania-praniu-brudnych-pieniedzy-aml-w-praktyce-posrednikow-nieruchomosci/ (T24)
17. https://ttms.com/pl/ryzyka-aml-w-branzy-nieruchomosci-jak-automatyzacja-zmniejsza-podatnosc-na-naduzycia/ (T24)
18. Internal: [TH54 check](../../poland-check/A/TH54-compliance-regtech-agents.md), [016](../accounting-tax/016-asystent-klienta-biura.md), R5/R6 catalogue rows

Coverage: 6 web searches and 2 fetches for this write-up (Polish AML software for offices, GIIF controls, AMLR timeline, Thirdfort traction). Not found: prices of Apfino or procedure packs, number of estate agencies, GIIF control statistics after 2021, CRBR API terms.
