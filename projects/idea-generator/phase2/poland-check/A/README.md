# Poland check, batch A (T16)

Gap verdicts for the 23 batch-A themes of [THEMES.md](../../themes/THEMES.md). All sources accessed **2026-11-03**. Summary table at the end (filled as themes are written).

## Method
- **Leaders tried** without creating accounts: public site, pricing page, language switcher, help centre, docs and signup page read via web fetch and search (English and Polish). Nothing was signed up for, paid, or submitted. What could not be checked is listed in each file.
- **Google autocomplete** (Polish): queries sent to Google's public suggestion endpoint (`suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl`) on 2026-11-03; the suggestions returned are quoted. Empty or echo-only suggestions are read as low search volume. Google Trends, Keyword Planner, Wykop and Facebook groups need JavaScript or a login and were **not** checked; job-board and press searches were done with web search.
- **Moat IDs** (M01…) refer to [local-moats.md](../../research/poland/local-moats.md); **D/DD IDs** to [demography.md](../../research/poland/demography.md); **A/S IDs** to [ai-landscape.md](../../research/poland/ai-landscape.md); CEE check uses [R6 README](../../research/regions/R6-cee-peers/README.md) and [R6 catalogue](../../catalogue/R6-cee-peers.csv).
- **Verdicts:** *open gap* = no Polish product and the Western leader does not serve Poland; *partial* = Polish or Western products exist but miss a definable Polish segment or workflow; *taken* = a Polish-adapted product already covers the core workflow at a price a solo founder cannot beat.

## Summary
| Id | Theme | Verdict | Key reason | Seed idea |
|---|---|---|---|---|
| [TH16](TH16-ai-accountant-micro-businesses.md) | AI accountant for micro-businesses | partial | Self-service AI bookkeeping taken (inFakt 100k+ firms; Norman (DE) sells KSeF+JPK_V7+ZUS at 29–39 PLN); done-for-you with a licensed accountant open for niches | Online accounting office for foreign sole traders in UA/EN/RU |
| [TH07](TH07-legal-research-national-law.md) | Legal research on national law | taken | LEX Expert AI, Beck-Noxtua (Legalis), Gaius-Lex; Harvey at WKB | (weak) KIO-ruling monitor for bidders |
| [TH09](TH09-contract-drafting-review.md) | Contract drafting and review | partial | Global tools multilingual; no Polish-law consumer-priced checker; thin search demand | Per-document B2B/zlecenie/dzieło contract check for contractors |
| [TH01](TH01-ambient-clinical-scribe.md) | Ambient clinical scribe | taken | Noa Notes (Docplanner) with Polish site; Heidi in Polish with free tier; hospital "Skryba AI" | (adjacent) vet/physio visit-report scribe |
| [TH19](TH19-ai-native-ledger-finance-agents.md) | AI-native ledger and finance agents | taken | Comarch Optima and Symfonia AI posting on KSeF; Payhawk Warsaw office | — |
| [TH34](TH34-hr-payroll-agents.md) | HR and payroll agents | partial | Polish payroll held by local suites; Factorial/Sloneek entering without Polish payroll; foreign-worker HR duties unserved | "Legalny pracownik": permit/oświadczenie tracker and filer for employers of foreigners |
| [TH02](TH02-patient-call-scheduling-agents.md) | Patient call and scheduling agents | partial | 30+ Polish voicebots and ElevenLabs in Polish; none integrates ZnanyLekarz or Polish clinic calendars | Clinic phone agent booking into mMedica/Medfile/ZnanyLekarz + NFZ queue answers |
| [TH56](TH56-leasing-property-management-agents.md) | Leasing and property-management agents | open gap | No Polish AI product, no Western leader in PL; managers taught ChatGPT; demand evidence thin | "AI biuro zarządcy" for wspólnoty mieszkaniowe |
| [TH33](TH33-ai-recruiting-interviews-screening.md) | AI recruiting interviews and screening | partial | Polish screening works in Hirevire; Emplocity for corporates; migrant blue-collar agency hiring unserved; AI Act high-risk | Multilingual pre-screening and document intake for staffing agencies (no scoring) |
| [TH61](TH61-procurement-rfq-order-handling.md) | Procurement, RFQ and order handling | open gap | No AI RFQ-to-quote product for Polish wholesalers; Subiekt/Optima integration local; demand unproven | "Oferta z maila" for technical wholesalers |
| [TH23](TH23-enterprise-customer-service-agents.md) | Enterprise customer-service agents | taken | Tidio, Text, SentiOne, Infobip, Intercom Fin in Polish | — |
| [TH54](TH54-compliance-regtech-agents.md) | Compliance and regtech agents | partial | Quantifier.ai and law firms cover NIS2/AI Act for larger firms; small AML obliged entities unserved | AML-in-a-box for small obliged entities (KYC, risk assessment, GIIF) |
| [TH17](TH17-agents-accounting-tax-firms.md) | Agents for accounting and tax firms | partial | In-ledger posting taken (Comarch, Symfonia, Saldeo 3,000 offices); client-chasing outside the ledger open | Office–client assistant chasing missing documents and explanations |
| [TH26](TH26-ai-receptionist-smes.md) | AI receptionist for SMEs | taken | 30+ vendors at 169–499 PLN/month incl. ElevenLabs, fonio | (residue) Booksy-native salon receptionist |
| [TH24](TH24-local-language-voice-cs-agents.md) | Local-language voice and CS agents | taken | PKO/Alior in-house voicebots, Lekta, Voicetel, SentiOne; Wonderful (IL) and Born Digital (CZ, via Netia) already in PL | (residue) Polish voicebot QA/test harness for vendors |

**Not yet written (T16 continues):** TH37, TH21, TH04, TH29, TH06, TH10, TH13, TH40.
