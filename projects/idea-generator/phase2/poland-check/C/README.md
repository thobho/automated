# Poland check, batch C (T18)

Gap verdicts for the 23 batch-C themes (ranks 47–69) of [THEMES.md](../../themes/THEMES.md). Sources accessed **2026-11-05** unless a file says otherwise. Summary table at the end.

## Method
Same as [batch A](../A/README.md#method) and [batch B](../B/README.md#method):
- **Leaders tried** without creating accounts: public site, pricing page, language switcher, help centre, docs and signup page read via web fetch and search (English and Polish). Nothing was signed up for, paid, or submitted. What could not be checked is listed in each file.
- **Google autocomplete** (Polish): queries sent to Google's public suggestion endpoint (`suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl`) on 2026-11-05; the suggestions returned are quoted. Empty suggestions are read as low search volume. Google Trends, Keyword Planner, Wykop and Facebook groups need JavaScript or a login and were **not** checked; job-board and press searches were done with web search.
- **Moat IDs** (M01…) refer to [local-moats.md](../../research/poland/local-moats.md); **D/DD IDs** to [demography.md](../../research/poland/demography.md); CEE check uses the [R6 README](../../research/regions/R6-cee-peers/README.md) and [R6 catalogue](../../catalogue/R6-cee-peers.csv).
- **Verdicts:** *open gap* = no Polish product and the Western leader does not serve Poland; *partial* = Polish or Western products exist but miss a definable Polish segment or workflow; *taken* = a Polish-adapted product already covers the core workflow at a price a solo founder cannot beat, or the theme is global and language-agnostic.
- Batch C holds the lowest-ranked themes (many hype or infrastructure themes), so several files are short: where the theme is global by nature, the check focuses on whether a Polish niche exists at all.

## Summary
| Id | Theme | Verdict | Key reason | Seed idea |
|---|---|---|---|---|
| [TH08](TH08-law-firm-ai-workspace-knowledge.md) | Law-firm AI workspace and knowledge | taken | Harvey (WKB), Legora (Wardyński), DeepJudge (Schoenherr) at top firms; LEX/Legalis bundle AI; small firms use NotebookLM/Copilot | — (residue in TH10/TH11) |
| [TH62](TH62-ai-native-engineering-design.md) | AI-native engineering design | open gap (poor fit) | No Polish design-as-outcome firm; Solvera (NO) not here; needs licensed engineers (*uprawnienia*); WT regulation in flux since 2026-09-20 | WT/EP pre-submission checker for design offices, 199–399 PLN/month |
| [TH28](TH28-car-dealer-agents.md) | Car-dealer agents | taken | 10+ Polish AI phone assistants for workshops at 159–499 PLN (Zilo/DobryMechanik 199, PilotGo with Motowarsztat); AInora (LT) here; Flai/Toma US-only | (weak) Otomoto/OLX lead follow-up for komisy |
| [TH31](TH31-sales-conversation-intelligence.md) | Sales conversation intelligence and coaching | taken | Bundled in CloudTalk (SK, PL site) and meeting recorders; Gong supports Polish; no Polish search demand; rep scoring is an AI Act employment flag | (weak) voice-note visit report into Comarch/enova for field reps |
| [TH45](TH45-natural-language-analytics-company-data.md) | Natural-language analytics over company data | partial | Comarch ChatERP (beta, Optima demo) brings NL data questions to the largest Polish ERP base; Subiekt/enova/WAPRO have none yet; Zeit AI has no Polish connectors | Read-only Polish Q&A + weekly summary for Subiekt GT/nexo, 99–199 PLN/month |
| [TH58](TH58-government-back-office-ai.md) | Government back-office AI | partial | State side closed (tenders; PLLuM/HIVE AI pilots in KPRM, Gdynia, Częstochowa, Lubuskie); private side of plan ogólny/WZ reform (deadline 2026-08-31) served only by LEX and non-LLM OnGeo | Parcel → plan ogólny/MPZP/WZ eligibility reader, 49–149 PLN per plot (overlaps TH15) |
| [TH12](TH12-immigration-casework.md) | Immigration casework | open gap | No AI drafts Polish legalisation cases for professionals; HRappka only tracks deadlines; agencies charge ~4.5k PLN by hand; MOS-only filing since 2026-04-27 and CUKR raise volume; US leaders do petition-writing | Case-file agent for legalisation agencies and staffing firms (MOS fields, voivodeship checklist, deadlines), 30–60 PLN/case |
| [TH41](TH41-meeting-notes-transcription.md) | Meeting notes and transcription | taken | Bundled in Teams/Meet; HappyScribe, Notta, tl;dv, Plaud work in Polish; only niche protocol formats remain | — (wspólnota protocol folds into TH56) |
