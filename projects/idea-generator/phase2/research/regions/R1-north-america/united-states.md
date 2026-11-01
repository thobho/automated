# United States (T05)

Index for the US scan, the region's largest source. All sources accessed **2026-11-01**. The findings are split by vertical:

| File | Vertical | New catalogue rows | R0 overlaps |
|---|---|---|---|
| [us-legal-public.md](us-legal-public.md) | legal, immigration, local-government permitting | 10 | 5 |
| [us-health-admin.md](us-health-admin.md) | scribes, front-desk voice, coding, home care, pharmacy | 11 | 8 |
| [us-finance-tax-insurance.md](us-finance-tax-insurance.md) | tax-firm automation, AI ERPs, insurance-agency ops | 11 | 8 |
| [us-smb-realestate.md](us-smb-realestate.md) | home services, dealerships, restaurants, freight, real estate | 12 | 6 |
| [us-people-education-consumer.md](us-people-education-consumer.md) | recruiting, payroll, K-12 teachers, language, consumer apps | 11 | 8 |
| **Total** | | **55** (R1-US-001…055) | **35** |

**US products researched: 90** (55 new rows + 35 already in [R0-global.csv](../../../catalogue/R0-global.csv)), meeting the task's ≥80.

## App Store chart snapshot (top-grossing, US, 2026-11-01)

Read from Apple's public RSS feeds (top 50 per genre). LLM-native apps in the top 40:

| Genre | LLM-native entries (rank) | Feed |
|---|---|---|
| Productivity | ChatGPT 1, Claude 2, Grok 4, Perplexity 6, Grammarly 11, Summary AI Note Taker 12 (Spanish developer), Speechify 13, Gemini 14, ChatOn 15, Otter 21, Plaud 23, Pocket AI 29, Copilot 37 | [genre 6007](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6007/json) |
| Medical | Freed AI scribe 20, Chartnote AI scribe 24 | [genre 6020](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6020/json) |
| Finance | Dovly AI (credit) 4; "Stocks to Buy Now AI Signals" 17 | [genre 6015](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6015/json) |
| Education | LangLearn AI English Tutor 9 (Singapore developer), Speak 11, Gauth 12 (Singapore/ByteDance), Solvely 30, Praktika 31 (UK), Gizmo 36 (UK) | [genre 6017](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6017/json) |
| Health & Fitness | Cal AI 8; Bevel AI health coach in Canada list | [genre 6013](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6013/json) |
| Business | none LLM-native in top 40: invoicing, scanning, fax, field-service apps (Jobber, Joist), Booksy Biz | [genre 6000](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6000/json) |
| Lifestyle | dating and home-security apps dominate; Astra (life advice) 24, AI Decor 35 | [genre 6012](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6012/json) |

**Reading:** consumer charts confirm general assistants and note-takers as the money-makers; vertical B2B LLM products rarely appear on charts (they sell on the web), except **AI scribes sold directly to clinicians** (Freed, Chartnote). The Business top-grossing list has no LLM-native app: invoice and estimate makers, scanners and fax apps still lead, a sign that SMB owners pay for small mobile paperwork tools (a channel for a Polish "KSeF invoice from phone" type product, outside this task). Google Play (Similarweb) was not read in this run.

## Startup media, accelerators and lists used
- Media: TechCrunch, GeekWire (blocked fetch), Crunchbase News, Axios Pro (excerpts), vertical trade press (Healthcare IT Today, Skilled Nursing News, CPA Practice Advisor, Roofing Contractor, Auto Remarketing, Legal IT Insider).
- Accelerators and lists: YC directory (covered in T04; YC company pages cited here for Broccoli AI), a16z-led rounds (Eve, Toma, HappyRobot, Probook), Sequoia-led (Freed, Rillet, Juicebox). Techstars and Forbes AI 50 were covered in T04 and not repeated.

## Local champions solving US-specific problems (the template for a Polish counterpart)
- **Law**: plaintiff personal-injury firms (Eve, Supio, EvenUp) and immigration (Manifest, Alma, Visalaw.ai) — built on US contingency fees, Arizona ABS and USCIS forms.
- **Tax**: tax-firm automation on IRS forms (Filed, Accrual, Juno, Accordance) during an accountant shortage.
- **Public services**: municipal permitting against local codes (GovWell, Govstream).
- **Health administration**: payer coding and prior auth (Arintra, Anterior, Candid) and home-care operations (Zingage, Arya).
- **Real estate**: transaction coordination (MaxHome, HouseWhisper).
- **HR/payroll**: multi-state payroll compliance (Warp).
- **Consumer finance**: credit-report disputes (Dovly AI).

## Coverage
- Products researched: 90 (55 new, 35 R0 overlaps). Sources read: ~32 pages + 7 App Store feeds; ~25 rows rest partly on search excerpts and are marked "excerpt" in the vertical files.
- Searches run: 26 web searches, ~40 page fetches (7 blocked: Business Wire 403, GeekWire 403, techleap feed 403, Eudia 404).
- Found nothing: retention/NRR for almost every US product (the exception in R1 is Spellbook, Canada); AI dental, home-health documentation, mortgage processing and IEP startups with verifiable funding; Google Play charts not read.
