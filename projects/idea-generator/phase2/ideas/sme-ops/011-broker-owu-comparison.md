# 011 — Submission and OWU comparison agent for small SME-lines brokers

**One-liner:** For a small Polish insurance broker placing commercial lines for SMEs, the agent reads the client's questionnaire and documents, drafts the request for quotation to 5–8 insurers' underwriters, parses the offers and OWU (ogólne warunki ubezpieczenia) that come back by e-mail into a side-by-side table of sums insured, sub-limits, exclusions and deductibles (franszyzy), drafts the recommendation letter, and pre-fills the IDD needs analysis (APK). Starts with one line: OC przewoźnika drogowego (carrier's liability), then SME property and OC działalności.
**Field:** sme-ops | **Type:** SaaS (web + e-mail integration) | **B2B** · shortlist id L145 (merges L146 APK documentation, L147 claim notification)

**Western analogues:**
- **FurtherAI** (US, YC): AI workspace for insurers, MGAs and brokers (submission processing, underwriting audits, claims, policy comparisons); **US$25M Series A led by a16z, announced 2025-10-09, US$30M total**; named customers Accelerant, MSI, Leavitt Group; company claims "billions" of premium processed ([Insurance Journal](https://www.insurancejournal.com/news/national/2025/10/09/843205.htm)). Seven-figure revenue is a company claim in secondary coverage, unverified.
- **Handle** (US/MX): AI agents across e-mail, WhatsApp, CRM and insurer portals for Mexican brokers; **US$6M seed led by a16z (2026-03)**, **75+ active brokers in Mexico**, brokers report 94% less time to register a claim (company claim) ([Infor Capital](https://inforcapital.com/news/handle-raises-6m-seed-round-led-by-andreessen-horowitz/)).
- **Segura** (BR): AI platform for brokers run through WhatsApp, **US$8M seed co-led by a16z and Kaszek** ([Tech Funding News](https://techfundingnews.com/andreessen-horowitz-co-leads-seguras-8m-round-to-use-whatsapp-for-insurance-distribution/)).
- **Foliume** (UY): quotes, renewals and claims from PDFs and e-mails; clients in ES, DE, PT per the R10 catalogue row (TH55 check; not re-verified).

**Spread:** TH55 insurance operations agents: US (FurtherAI, Outmarket, Covu, Harper), MX (Handle), BR (Segura), UY with ES/DE/PT clients (Foliume) ([TH55 check](../../poland-check/B/TH55-insurance-operations-agents.md)). At least 5 countries across R1, R10 and R3/R5, mostly 2024–2026 rounds.

**Does the Western leader already work in Poland?** No. FurtherAI sells to US carriers and MGAs (UK expansion reported); Handle and Segura are tied to Mexican and Brazilian insurer portals and WhatsApp habits; no Polish client found for Foliume (TH55 check). Not tried hands-on: all are demo-led.

**Polish adaptation, i.e. the edge:**
- **OWU in Polish, per insurer and per product**, compared clause by clause; brokers' audits note overlapping-scope clauses ("kolizje zakresowe") in almost all Polish OWU (search excerpt of a broker audit offer, not read in full).
- **IDD needs analysis (APK)** must be documented before sale under the ustawa o dystrybucji ubezpieczeń; the KNF register of brokers is public (TH55 check; [art. 59 UDU via lexlege](https://lexlege.pl/dystryb-ubezpieczen/art-59/) on brokerage through qualified natural persons).
- **Commercial-lines placement runs on e-mail RFQs to underwriters**, not on comparison portals (those serve motor OC/AC retail: Rankomat, Mubi, WebCUK) (TH55 check).
- **Line-specific vocabulary:** OC przewoźnika (CMR vs. domestic), mienie od wszystkich ryzyk vs. ryzyk nazwanych, franszyza integralna/redukcyjna. A foreign team would need Polish insurance wording and insurer relationships; translation does not get there.

**Target customer in Poland:** small brokerage firms (1–10 people) placing SME lines. **Almost 1.5 thousand brokers (natural and legal persons) were active at end-2017**, earning **1.2 bn PLN** in commissions that year ([bank.pl, KNF report](https://bank.pl/?p=269725)); a KNF report for 2024 exists but its counts were not read (current number **unverified**). Warsaw alone had 270 brokers in the 2021 KNF report (search excerpt). Adjacent: multiagency networks (CUK "over 600" points, TH55 check) for L146. CEE: same IDD rules, different OWU and languages.

**Demand driver:** DD7 labour shortage in small offices (indirect; no broker-specific data found); IDD documentation burden (regulatory, ongoing, not new). No dated trigger 2026–2028 found.

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| WebCUK and multiagency systems | compare and issue policies from ~40 insurers, retail lines | agent commission model | retail motor/home, not commercial RFQs and OWU clauses |
| Insly (EE), generic CRMs (Pipedrive, Creatio) | policy admin, CRM in Polish | not checked | no document understanding of offers/OWU |
| Minte.ai (PL) | AI claims review against OWU, sells to insurers (UNIQA Polska live) | B2B, not published | insurer side, not broker placement (TH55 check) |
| Excel + Word + ChatGPT | today's broker workflow | staff hours / 20 USD | no structured table, no APK link, confidentiality worries |
No broker-side LLM product for commercial placement was found (TH55 check); broker software vendors' prices were not found in this pass.

**Evidence of Polish demand:** weak. Autocomplete "program dla multiagencji" → 2 suggestions; "program dla agenta ubezpieczeniowego" → echo only (TH55 check); broker job ads describe preparing offer comparisons and recommendations (e.g. [pracuj.pl broker ad](https://www.pracuj.pl/praca/broker-brokerka-poznan,oferta,1004969534)), showing the job step exists. Public tenders for broker services ask for an offer comparison and recommendation (search excerpts), but tenders are excluded as a channel. No direct "I want this tool" evidence.

**MVP scope (≤6 weeks):**
1. One line only: OC przewoźnika drogowego. Questionnaire template + client documents (licence, fleet list, claims history) → RFQ e-mail draft per insurer.
2. Offer/OWU parser: PDF in → JSON schema (sum insured, sub-limits, territorial scope, exclusions list, deductibles, premium) with clause citations (page and paragraph); a seeded library of the current OWU of 6–8 insurers for that line.
3. Comparison table and recommendation letter draft; every cell links to the clause it came from.
4. APK pre-fill from the questionnaire (L146 core).
5. Tests: golden files for each insurer's OWU and 20 anonymised offers; schema checks; diff alerts when an insurer publishes a new OWU version.

**Monetization:** 399 PLN/month per broker office (up to 3 users), 699 PLN for up to 10; VAT invoice, annual prepay discount. Budget line: broker staff hours on comparisons (one comparison ≈ 1–3 hours, estimate, unverified). **Unit economics:** a placement with 6 offers and 6 OWU (~40 pages each) ≈ 400k input / 20k output tokens; on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash), accessed 2026-11-05) ≈ US$0.17; OWU cached once per version. At 30 placements a month ≈ US$5 (~20 PLN) per office, plus ~30 PLN hosting; gross margin ~85–90% at 399 PLN. **Customer count:** 10k PLN MRR ≈ 25 offices at 399 PLN; the 2017 base of ~1.5k brokers is ~60× that.

**Distribution, first 10 customers:** outbound from the public KNF register to small brokerage firms in transport-heavy regions (Mazowieckie, Wielkopolska, Łódź), offering a free comparison of their next OC przewoźnika placement; broker associations (Polska Izba Brokerów, Stowarzyszenie Polskich Brokerów; membership and events not checked); LinkedIn posts with anonymised OWU comparisons.

**Regulation:** AI Act: not high-risk; Annex III covers risk assessment and pricing for **life and health** insurance of natural persons ([Annex III](https://artificialintelligenceact.eu/annex/3/)), which is out of scope for SME property and liability lines. Insurance distribution: the tool supports a licensed broker, who stays responsible for advice; no licence needed for the vendor (not checked with counsel). RODO: client data and claims history; EU hosting; data-processing agreement with each broker. Professional secrecy on insurance data applies.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Only ~25 paying offices are needed, so founder-led phone and demo sales can reach the goal | H | M | 5 demos booked from 50 outbound e-mails |
| O2 | The OWU clause library compounds: each new insurer version parsed serves every customer, a data moat | H | M | parser covers 8 insurers for one line with ≥95% field accuracy |
| O3 | Annual renewals of OC przewoźnika give each office a steady stream of placements, so usage is regular | M | M | pilot offices run ≥10 placements a month |
| O4 | APK documentation pre-fill sells on its own to multiagency agents (L146), widening the market | M | M | one multiagency network agrees to a pilot |
| O5 | A network (CUK, a broker group) licenses it for all members | L | H | a network asks for volume pricing |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | A missed exclusion in a comparison exposes the broker to a liability claim, so brokers won't trust the table | M | H | pilot brokers re-check every cell by hand |
| R2 | Small brokers place too few commercial policies a month to justify 399 PLN | M | H | median pilot office <5 placements a month |
| R3 | Conservative buyers and the founder's 40 h/month make sales slow (months per office) | H | M | <3 paying offices after 3 months |
| R4 | Insurer offers come in inconsistent PDFs, scans and portal screens, so parsing accuracy stays low | M | M | >10% of fields need manual fixes in pilots |
| R5 | A broker-software vendor or a Western player (FurtherAI expanding to the UK) adds Polish OWU parsing | L | M | Polish job ads from FurtherAI or a broker-software vendor announcing AI |

O sum 6+6+4+4+3 = 23; R sum 6+6+6+4+2 = 24. R − O = 1, no H×H risk → **band unchanged** (rule §4.5).

**Success signals:**
- Western analogue durable signals: replaces underwriting and servicing staff hours (signal 1; FurtherAI "hours of work reduced to minutes"), frequent painful problem with an owner (signal 2: every submission), integrations with portals and e-mail (signal 8, Handle), start with one workflow and expand (signal 4-like, FurtherAI, company claim) ([Insurance Journal](https://www.insurancejournal.com/news/national/2025/10/09/843205.htm); [Infor Capital](https://inforcapital.com/news/handle-raises-6m-seed-round-led-by-andreessen-horowitz/)). No retention or NRR figures. Durability score ~4 → **promising**.
- Hype warnings: none found; all traction figures are company claims.
- Polish adaptation can reproduce: replaced spend = assistant/broker hours on comparisons and APK paperwork; first channel = KNF register outbound and broker associations; retention driver = the OWU library, stored client files and renewals.

**Graveyard:** none found for broker-side AI (the theme is 2024–2026). Not searched: pre-LLM European broker comparison tools.

**Scores (1–5):** L1 4 · L2 3 · L3 4 · L4 4 · L5 2 · L6 3 · L7 3 · L8 3 · L9 3 | **Weighted:** 3.2 / 5 | **Chance band:** 5–15%. Only ~25 offices are needed and the gap is clean (no Polish or Western broker-side product), but Polish demand is unproven (broker count from 2017, no search or forum evidence) and accuracy on OWU clauses must be very high before a broker relies on it. The opportunity and risk lists roughly balance (O 23, R 24).
Changes vs. quick score: L2 2 → 3 (FurtherAI, Handle, Segura rounds in 2025–2026 across US/MX/BR), L5 3 → 2 (no current broker count, weak demand evidence), others kept; weighted 3.3 → 3.2.

**Cheapest validation test (≤1 week, ≤200 PLN):** download current OC przewoźnika OWU from 6 insurers' websites, build the comparison table by hand with an LLM, and send it to 40 small brokers from the KNF register with "want this for your next placement?"; book calls; ask what they pay for software today and how many placements they do a month.

**Kill criteria:** <3 calls from 40 e-mails; or pilot brokers report <5 commercial placements a month; or OWU field accuracy below 95% after two iterations.

**Confidence:** medium-low (Western traction and the Polish workflow sourced; broker count is old, demand and placement volumes not sourced).

**Sources** (accessed 2026-11-05):
1. https://www.insurancejournal.com/news/national/2025/10/09/843205.htm
2. https://inforcapital.com/news/handle-raises-6m-seed-round-led-by-andreessen-horowitz/
3. https://techfundingnews.com/andreessen-horowitz-co-leads-seguras-8m-round-to-use-whatsapp-for-insurance-distribution/
4. https://bank.pl/?p=269725
5. https://lexlege.pl/dystryb-ubezpieczen/art-59/
6. https://www.pracuj.pl/praca/broker-brokerka-poznan,oferta,1004969534
7. https://openrouter.ai/google/gemini-2.5-flash
8. https://artificialintelligenceact.eu/annex/3/
9. Internal: [TH55 check](../../poland-check/B/TH55-insurance-operations-agents.md)

Coverage: 8 web searches/fetches for this write-up (FurtherAI, Handle, Segura funding; KNF broker counts and commissions; Polish broker software and prices). Not found: the current number of brokers (KNF 2024 report not read), Polish broker-software prices, placements per broker office, any graveyard case.
