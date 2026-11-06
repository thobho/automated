# 016 — Asystent klienta biura (client chasing and month-end explanations for biura rachunkowe)

**One-liner:** For a small accounting office (biuro rachunkowe), the agent compares each client's KSeF invoices with the client's bank statement every week, lists bank lines with no document and documents with no payment, asks the client on WhatsApp or e-mail for the missing receipt or an explanation in plain Polish, reads the replies (photo, PDF, "to prywatne", "zwrot od kontrahenta"), files them for the accountant, and at month end drafts a short client letter explaining the VAT, PIT/CIT and ZUS amounts the office computed. The office approves what goes out; per-client workload is reported for repricing. Merges L006–L008, L011, L013, L154.
**Field:** accounting-tax | **Type:** SaaS | **B2B** (office pays, priced per client of the office) · shortlist id L005

**Western analogues:**
- **Basis** (US): AI agents for accounting firms (tax returns, bookkeeping tasks); **US$100M Series B led by Accel at a US$1.15bn valuation (2026-02)**, ~US$138M raised in total (search excerpts: [Bloomberg Law](https://news.bloomberglaw.com/crypto/ai-for-accounting-startup-basis-hits-1-15-billion-valuation); [Axios](https://www.axios.com/pro/fintech-deals/2026/01/06/basis-accel-series-b)). Customer counts not read.
- **Maxed AI** (US): talks to the firm's clients through a branded portal for document requests and status updates; **US$850k pre-seed (2026-04-23)** (search excerpt, [BriefGlance](https://briefglance.com/articles/maxed-ai-raises-850k-to-automate-accounting-with-ai-agents)). The closest functional match, but very early.
- **Ravical** (BE): AI across accounting firms; **US$17M seed (2026-10-29)** (search excerpt, [Runtime Wire](https://runtimewire.com/article/ravical-17m-accounting-ai)).
- Juno (US), TreuhandGPT (CH), Repodo (DK) from the longlist; not re-checked here.

**Spread:** TH17 agents for accounting and tax firms: US, BE, CH, DK, NL (DataSnipper) ([TH17 check](../../poland-check/A/TH17-agents-accounting-tax-firms.md)); three regions, mostly since 2024. Large funding rounds in 2026 show investor pull; client-facing chasing is a small part of it.

**Does the Western leader already work in Poland?** No. Basis and Juno are built around US tax forms; Ravical around Belgian practice; Maxed AI is US-only. None reads KSeF or exports to Optima/Saldeo (TH17). Not tried hands-on (demo-led).

**Polish adaptation, i.e. the edge:**
- **KSeF makes the purchase side machine-readable.** Receiving invoices through KSeF has been mandatory for all businesses since 2026-02-01, issuing since 2026-02-01 (sales >200M PLN) and 2026-04-01 (all other VAT payers), the smallest from 2027-01-01, and the KSeF number must appear in JPK from 2026-08-01 (search excerpts: [infakt](https://www.infakt.pl/blog/wdrozenie-ksef-harmonogram-2026-r/); [podatki.biz](https://www.podatki.biz/artykuly/aktualny-plan-wdrozenia-ksef-ostateczne-terminy-i-okres-przejsciowy_55_58405.htm)). What is left to chase is the bank line without a KSeF document: foreign invoices, receipts, private payments, offline24 documents (sponsored source says offices still handle 15–30% of documents outside templates, unverified).
- **Ledger and channel fit:** exports to Comarch Optima, Saldeo, Symfonia, wFirma (M41, M42, M46), MT940/CSV bank statements from Polish banks, an office acting under the client's KSeF authorisation, Polish client habits (phone, WhatsApp, "pani Kasiu, co to za przelew?"), and the line between bookkeeping and *doradztwo podatkowe* (the letter explains amounts, gives no tax advice).

**Target customer in Poland:** small biura rachunkowe (1–9 staff, 30–200 clients each). "Slightly over 35,000 active accounting offices serving over 2 million businesses" (podatki.biz, **undated**, [podatki.biz](https://www.podatki.biz/i446614/obowiazek-skladania-sprawozdania-finansowego-przez-osoby-prawne/obowiazek-skladania-sprawozdania-finansowego-przez-osoby-prawne.htm)); nearly 99% of firms in accounting and tax services employ up to 9 people (GUS "Usługi biznesowe", via [podatki.biz](https://www.podatki.biz/artykuly/gus-zbadal-rynek-uslug-ksiegowych-i-doradztwa-podatkowego_34_33161.htm)). SaldeoSMART alone serves ~3,000 offices (TH17). A GUS/REGON count for PKD 69.20 was not found. CEE: CZ/SK have their own e-invoice plans; not checked.

**Demand driver:** regulatory (KSeF 2026–2027, KSeF numbers in JPK) and DD7 (independent accountants on the shortage list, TH17). Offices price clients poorly and absorb chasing time ("1 na 60", [infor.pl](https://www.infor.pl/biura-rachunkowe/prowadze-biuro/7594837,1-na-60-dlaczego-biura-rachunkowe-nadal-nie-budzetuja-klientow.html), via TH17).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| **Comarch ERP agents** (Optima, XL, Betterfly) | a dozen-plus agents commercial since **2026-09-01**: bank-statement settlement (1,000 lines in ~3 min vs 6 h in an XL pilot), a debt-collection agent that contacts counterparties, KSeF fraud checks, document categorisation ([ITwiz](https://itwiz.pl/comarch-wpuszcza-ai-do-biur-rachunkowych/)) | not stated | no named agent for chasing the office's own clients; Optima-only |
| **Symfonia** client panel | client uploads, automatic KSeF download, **automatic notices about missing documents** and deadlines; OCR, no AI described ([Symfonia blog, 2026-07-20](https://symfonia.pl/blog/firmy/biura-rachunkowe/panel-klienta-biura-rachunkowego-jak-ograniczyc-maile-z-fakturami-bez-utraty-kontroli-nad-dokumentami/)) | not stated | template reminders, not "which bank line lacks a document" |
| **SaldeoSMART** | client document archive, upload by app/e-mail, automatic settlement information to clients from declarations ([infor.pl](https://ksiegowosc.infor.pl/rachunkowosc/zasady-ogolne/717958,5-krokow-do-optymalizacji-pracy-w-ksiegowosci-Cz-IV-Rozliczenia-ksiegowe-Firmy-czyli-jak-uniknac-wysylania-setek-identycznych-maili.html)) | not checked | no conversational chasing found |
| wFirma for offices | bulk e-mail/SMS notices to clients | in subscription | templates |
| Księgoboty, flowMEE/AutoMEE | AI agents and workflows for offices | not found | scope unclear (TH17, search) |
| ChatGPT + phone + e-mail | what offices do today | staff time | manual |

**Evidence of Polish demand:** indirect. Vendors (Symfonia, wFirma, Saldeo) all ship client-reminder features, which shows the chore is recognised; a sponsored flowMEE report says offices "must ask clients about missing information", which is time-consuming (search excerpt). No office owner quote or paid workaround specific to bank-line chasing found.

**MVP scope (≤6 weeks):**
1. Inputs: KSeF invoices via the public KSeF API under the office's authorisation, bank statements uploaded as MT940/CSV (or forwarded by the client), the office's client list.
2. Deterministic matching (amount, date, NIP, account number, KSeF number) → open items per client; the LLM only classifies hard cases and writes messages.
3. Chase flow on e-mail first, WhatsApp Business later: one message per client listing the open lines; parse replies (photo/PDF/free text) into "document attached / private / explanation", attach to the line.
4. Office dashboard: open items per client, hours saved, CSV export for Optima/Saldeo import; month-end letter draft from the office's own figures.
5. Tests: fixture statements and KSeF XML → expected open items; reply fixtures → expected classification; no advice phrases in letters.

**Monetization:** 5 PLN net per active client per month, minimum 149 PLN per office; VAT invoice. Typical office with 60–100 active clients → 300–500 PLN. Budget line = accountant hours spent chasing. **Unit economics:** per client-month ~50k input + 10k output tokens (classification of hard lines, messages, reply parsing) on Gemini 2.5 Flash (US$0.30 / US$2.50 per M, [OpenRouter](https://openrouter.ai/google/gemini-2.5-flash)) ≈ US$0.04 (~0.15 PLN); e-mail and storage ~0.3 PLN; WhatsApp message fees per client not checked (estimate <1 PLN). Gross margin ~80–90%. **Customer count:** 10k PLN MRR ≈ 2,000 active clients ≈ 25–30 offices; 20× ≈ 600 offices vs ~35,000 (undated source), so the §3 check passes on a weak source.

**Distribution, first 10 customers:** offices in the founder's area and network (one pilot office first); Facebook groups for accounting-office owners; local SKwP branches and KSeF trainings; a free "bank lines without documents" report from one uploaded statement and KSeF export as the lead magnet.

**Regulation:** AI Act: administrative bookkeeping support, not an Annex III use; transparency when the agent writes to clients as a bot ([Annex III](https://artificialintelligenceact.eu/annex/3/)). RODO: the office is the client's processor and the product a sub-processor; EU hosting; WhatsApp means Meta as a further processor. Tax-advice monopoly (A26 in local moats): the letter explains computed amounts and deadlines, no advice; the office sends it.

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | With KSeF covering most purchase invoices since 2026, the remaining open items are few and precise, so chasing becomes automatable for the first time (KSeF schedule sourced) | H | M | the pilot office's open items per client fall below 10 a month |
| O2 | Offices that cannot hire accountants pay to take on more clients with the same staff | M | H | the pilot office takes on new clients without a new hire |
| O3 | Per-client pricing grows with the office's book, so revenue per office rises over time | M | M | average billed clients per office grows 10% in 6 months |
| O4 | Saldeo or Symfonia accepts an integration or marketplace listing, opening thousands of offices | L | H | a partner-programme reply within 2 months |
| O5 | Offices become a channel for other ideas (L023, L072) | L | M | an office asks for a second module |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Comarch, Symfonia or Saldeo add a client-chasing agent; Comarch already ships a counterparty-contacting collections agent and a bank-matching agent | H | H | "agent komunikacji z klientem" in a Comarch or Saldeo release note |
| R2 | Getting statements and writing results back into each office's ledger is custom work per office | M | H | each pilot office needs a different import path |
| R3 | Offices are conservative and price-sensitive; sales take months | H | M | <3 offices start a trial after 30 contacts |
| R4 | Office clients ignore bot messages or answer in ways the agent mis-files | M | M | <40% of chase messages answered within a week |
| R5 | RODO and Meta-as-processor questions slow the WhatsApp channel | M | L | offices refuse WhatsApp and stay on e-mail |

O sum 6+6+4+3+2 = 21; R sum 9+6+6+4+2 = 27. R − O = 6 ≥ 6, and R1 is H×H; the MVP's mitigation (ledger-neutral, works with Saldeo/Symfonia/wFirma offices) narrows but does not remove it → **band down one** (§4.3; one band only).

**Success signals:**
- Western analogue durable signals: replaces accountant hours (signal 1), a weekly owned chore (signal 2), per-client pricing (signal 7), and strong investor pull (Basis valuation, Ravical seed) ([Bloomberg Law](https://news.bloomberglaw.com/crypto/ai-for-accounting-startup-basis-hits-1-15-billion-valuation)). No retention or NRR found; the chasing-specific analogue (Maxed AI) is pre-seed. Durability score ~3–4 → **unproven to promising**.
- Hype warnings: none found; funding size alone is not traction.
- Polish adaptation can reproduce: replaced spend = accountant chasing hours; first channel = pilot office plus owner groups; retention driver = weekly open-item list tied to the monthly close.

**Graveyard:** not searched specifically; Polish offices' earlier "client portal" tools survive as features of ledger vendors rather than standalone products (observation from the competition table, not a sourced failure).

**Scores (1–5):** L1 4 · L2 4 · L3 3 · L4 4 · L5 3 · L6 3 · L7 3 · L8 3 · L9 2 | **Weighted:** 3.3 / 5 | **Chance band:** <5% (score band 5–15%, moved down one by the opportunity/risk rule). KSeF finally makes the open-items list precise and Western funding shows the theme is real, but Polish ledger vendors already ship agents next to this job (bank matching, counterparty collections, template reminders), so a standalone layer is one release away from being a feature. **Recommendation: worth a one-office pilot only as a ledger-neutral tool for Saldeo/Symfonia/wFirma offices; stop if Comarch or Saldeo announce client chasing.**
Changes vs. quick score: L1 4 kept, L2 3 → 4 (Basis and Ravical rounds), L3 3 kept (Symfonia missing-document notices and Comarch agents found), L5 4 → 3 (office count only from an undated secondary source), L8 3 kept, L9 2 kept; weighted 3.2 → 3.3.

**Cheapest validation test (≤1 week, ≤200 PLN):** ask 3 offices for one anonymised client-month (KSeF export + bank statement); run the matching by script and show the open-items list and draft messages; ask how long the same took them and whether they would pay 5 PLN per client. Post the offer in one office-owner Facebook group.

**Kill criteria:** offices say their ledger already lists unmatched bank lines and the chase is <1 h per week; or no office shares data in 3 weeks; or a ledger vendor ships client chasing before the pilot.

**Confidence:** medium on competition and KSeF facts, low on office count and willingness to pay.

**Devil's advocate (T24, 2026-11-06):**
- *Half of the MVP already ships in the ledger.* Step 2 (deterministic matching of bank lines to documents) is what Comarch's bank-statement agent does commercially since 2026-09-01 (1,000 lines in ~3 minutes in an XL pilot), and Comarch's payment-settlement and collections agent already writes to counterparties about overdue payments; it does not request documents from the office's own clients (ITwiz, re-fetched 2026-11-06, [ITwiz](https://itwiz.pl/comarch-wpuszcza-ai-do-biur-rachunkowych/)). Pointing an agent that already messages people at "client, send the receipt for this line" is a small step for Comarch; Symfonia already sends automatic missing-document notices. What remains open is the conversational reply parsing for Saldeo/Symfonia/wFirma offices.
- *ChatGPT will absorb it.* The LLM part (classify a reply, write a polite chase) is the easy part; the hard part is getting statements and writing results back into the ledger, which is R2 and which incumbents get for free.
- *Polish customers won't pay this.* Offices do not even budget their own clients' hours ("1 na 60", infor.pl, cited above), so a per-client fee that has to be passed on is a hard sell; offices already pay Saldeo or Symfonia for a client panel with reminders. No office owner was found asking for this.
- *Western leader localizing in 12 months.* Basis, Ravical and Maxed AI show no CEE plans; the threat is domestic (Comarch, Symfonia, Saldeo), not Western.
- *Second competitor search (2026-11-06):* "biuro rachunkowe AI agent ... brakujących dokumentach wyciąg bankowy KSeF", "SaldeoSMART AI agent 2026", "Księgoboty": no Polish product chasing office clients by unmatched bank lines found. Found: Księgoboty.pl (tax Q&A, KSeF guidance, document classification; built on AgentX, 2026-01-07 case study, no client chasing; [AgentX](https://www.agentx.so/mcp/blog/how-ksiegoboty-pl-automates-accounting-workflows-and-compliance-in-poland-a-success-story-built-with-agentx)); autoMEE flowMEE, an AI-first office platform that checks bank account numbers automatically (partner article 2026-05-28, [podatki.biz](https://www.podatki.biz/artykuly/ksef-ai-i-automatyzacja-ksiegowosci-jak-zmienia-sie-praca-biur-rachunkowych-w-2026-roku_40_62261.htm)). No new AI features found for SaldeoSMART.
- *Claims re-checked.* Comarch agents and dates: confirmed. Office count (~35,000): still only the undated podatki.biz page; not improved. Documents outside KSeF "15–30%": still a sponsored claim (search excerpt), unverified.
- *Success signals.* Basis's US$1.15bn valuation and Ravical's seed are funding, not retention or revenue; the analogue for the actual job (Maxed AI, client document requests) is a US$850k pre-seed. No hype warning, but the durable signals for client chasing specifically are 1, 2 and 7 by design, none evidenced by figures. L2 4 is too high for the job step being copied.
- *Opportunity/risk lists.* O1 "KSeF makes chasing automatable for the first time" rated H without evidence of the effect (the KSeF schedule is sourced, the drop in open items is not), and KSeF helps the ledger vendors equally → M×M. Risks honest; R1 is better evidenced than when written.

**Review changes (T24, 2026-11-06):** L2 4 → 3 (traction is in AI bookkeeping and tax prep; the client-chasing analogue is pre-seed). Reviewed scores: L1 4 · L2 3 · L3 3 · L4 4 · L5 3 · L6 3 · L7 3 · L8 3 · L9 2 | weighted 0.48+0.36+0.36+0.60+0.45+0.30+0.24+0.24+0.16 = 3.19 → **3.2** (shortlist quick 3.2; write-up 3.3 replaced). O1 H×M → M×M. §4: O 4+6+4+3+2 = 19, R 27, R − O = 8 and R1 H×H → down one → **<5%** (unchanged). Not rejected: the conversational chase for non-Comarch offices is still open, but the one-office pilot should first check whether the office's ledger already lists unmatched lines.

**Sources** (accessed 2026-11-05/06):
1. https://news.bloomberglaw.com/crypto/ai-for-accounting-startup-basis-hits-1-15-billion-valuation (search excerpt)
2. https://www.axios.com/pro/fintech-deals/2026/01/06/basis-accel-series-b (search excerpt)
3. https://briefglance.com/articles/maxed-ai-raises-850k-to-automate-accounting-with-ai-agents (search excerpt)
4. https://runtimewire.com/article/ravical-17m-accounting-ai (search excerpt)
5. https://itwiz.pl/comarch-wpuszcza-ai-do-biur-rachunkowych/
6. https://symfonia.pl/blog/firmy/biura-rachunkowe/panel-klienta-biura-rachunkowego-jak-ograniczyc-maile-z-fakturami-bez-utraty-kontroli-nad-dokumentami/
7. https://ksiegowosc.infor.pl/rachunkowosc/zasady-ogolne/717958,5-krokow-do-optymalizacji-pracy-w-ksiegowosci-Cz-IV-Rozliczenia-ksiegowe-Firmy-czyli-jak-uniknac-wysylania-setek-identycznych-maili.html (search excerpt)
8. https://www.infakt.pl/blog/wdrozenie-ksef-harmonogram-2026-r/ (search excerpt)
9. https://www.podatki.biz/artykuly/aktualny-plan-wdrozenia-ksef-ostateczne-terminy-i-okres-przejsciowy_55_58405.htm (search excerpt)
10. https://www.podatki.biz/i446614/obowiazek-skladania-sprawozdania-finansowego-przez-osoby-prawne/obowiazek-skladania-sprawozdania-finansowego-przez-osoby-prawne.htm (search excerpt, undated)
11. https://www.podatki.biz/artykuly/gus-zbadal-rynek-uslug-ksiegowych-i-doradztwa-podatkowego_34_33161.htm (search excerpt)
12. https://www.infor.pl/biura-rachunkowe/prowadze-biuro/7594837,1-na-60-dlaczego-biura-rachunkowe-nadal-nie-budzetuja-klientow.html (via TH17)
13. https://openrouter.ai/google/gemini-2.5-flash
14. https://artificialintelligenceact.eu/annex/3/
15. Internal: [TH17 check](../../poland-check/A/TH17-agents-accounting-tax-firms.md)
16. https://itwiz.pl/comarch-wpuszcza-ai-do-biur-rachunkowych/ (2026-11-06, T24, re-fetched)
17. https://www.agentx.so/mcp/blog/how-ksiegoboty-pl-automates-accounting-workflows-and-compliance-in-poland-a-success-story-built-with-agentx (2026-11-06, T24)
18. https://www.podatki.biz/artykuly/ksef-ai-i-automatyzacja-ksiegowosci-jak-zmienia-sie-praca-biur-rachunkowych-w-2026-roku_40_62261.htm (2026-11-06, T24, partner article)

Coverage: 9 web searches/fetches (Saldeo client features, office counts, Western AI-for-accounting rounds, Polish client-portal reminders, Symfonia panel, KSeF schedule, Polish AI agents for offices, Comarch agents). Not found: a GUS/REGON count of offices for PKD 69.20, Comarch agent prices, Saldeo/Optima partner API terms, WhatsApp Business message prices for Poland, any office-owner quote on chasing time, graveyard cases.
