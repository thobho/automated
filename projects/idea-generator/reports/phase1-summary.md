# Phase 1 summary — idea generator

Written 2026-10-29 by T17. It summarises T01–T16; every number below is counted from the files on this branch, and the method of counting is given next to it. Estimates are marked as estimates.

**Bottom line.** The research mostly found that the obvious Polish compliance and SME wedges are already covered. After the skeptical review (T16) only one idea, [003 Self-hosted KSeF gateway licence](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md), stays in the `5–15%` band of reaching 10,000 PLN MRR within 12 months; every other reviewed idea is `<5%`. 15 of the 25 write-ups were rejected or merged, almost always because a second search found a free or cheap incumbent. No idea is in a band that justifies building before a validation test, so week 2 should be spent on the cheap tests below, not on code.

## 1. Method in 5 lines
1. Nine research lenses (proven abroad, competition, monetization, copy what earns, why now, pain, founder fit, distribution, unit economics) → sourced findings in `research/NN-<lens>/`, then a gap pass on lenses 1, 3 and 5 (T02–T11).
2. Findings were combined into a 208-idea longlist in 22 fields ([longlist.md](../ideas/longlist.md)); near-duplicates were merged and out-of-profile ideas dropped (T11–T12).
3. Each remaining idea got a quick 1–5 score per lens, weighted per [criteria.md](../method/criteria.md); ideas with a rounded weighted score ≥ 2.4 form the shortlist ([shortlist.csv](../ideas/shortlist.csv), T12).
4. The top 25 (at most 3 per field) got full write-ups with ≥5 sources (T13–T15), then a separate devil's-advocate review that re-scored them (T16).
5. Weighted score maps to a chance band (`<5%` below 2.8, `5–15%` from 2.8 to 3.4; L3 = 1 or L6 = 1 forces `<5%`); this report picks five ideas for ≤1-week, ≤200 PLN validation tests.

## 2. Stats
**Funnel** (counted from `ideas/longlist.md`, `ideas/shortlist.csv` and the section headings of [rejected.md](../rejected.md)):

| Stage | Count | How counted |
|---|---|---|
| Ideas dropped before the longlist (T11) | 9 | T11 lines in rejected.md |
| Longlist | 208 ideas in 22 fields | longlist.md Counts section; IDs I001–I208 |
| Merged into another idea (T12) | 16 | "T12 merges" section, excluding the "Not merged, noted" line |
| Dropped as unrealistic or out of profile (T12) | 3 | "T12 drops" section |
| Below the shortlist cut (T12, rounded weighted < 2.4) | 81 | "T12 below the shortlist cut" section |
| **Shortlisted** | **108** | rows in shortlist.csv (208 − 16 − 3 − 81) |
| Researched in depth | 27 | 25 write-ups + 2 ideas (I062, I061) that collapsed during write-up research and were swapped out (T13) |
| **Written up** | **25** | files `ideas/<field>/NNN-*.md` |
| **Rejected or merged after the review (T16)** | **15** (14 rejected, 1 merged into 001) | "T16 review" section |
| **Write-ups still standing** | **10** | 25 − 15 |
| Shortlisted ideas never researched beyond the quick score | 81 | 108 − 27 |
| Every rejection, all stages | 126 lines | 9 + 16 + 3 + 81 + 2 + 15 |

Bands in shortlist.csv after the review: 11 rows `5–15%`, 97 rows `<5%` (counted with Python `collections.Counter` on the `chance_band` column). Of the 11 `5–15%` rows, 2 are rejected (I062, I061), 1 is the reviewed survivor 003, and 8 are quick scores that were never researched.

**Research** (findings counted as distinct `## L<n>-F<nn>` headings in each lens folder; pages and searches are what each lens README's Coverage section reports, ±3 by their own statement, T02–T10 only, gap-pass pages not included):

| Lens | Findings | Pages read (Coverage) | Searches (Coverage) |
|---|---|---|---|
| [01 Proven abroad](../research/01-proven-abroad/README.md) | 26 (18 + 8 from the T11 gap pass) | 19 (+9 in the gap pass, [more-markets.md](../research/01-proven-abroad/more-markets.md)) | 26 |
| [02 Weak competition](../research/02-weak-competition/README.md) | 22 | 40 | 17 |
| [03 Monetization](../research/03-monetization/README.md) | 41 (31 + 10 gap pass) | 36 | 13 |
| [04 Copy what works](../research/04-copy-what-works/README.md) | 28 | about 33 | 11 |
| [05 Why now](../research/05-why-now/README.md) | 34 (24 + 10 gap pass) | 17 | 23 |
| [06 Pain evidence](../research/06-pain-evidence/README.md) | 26 | about 21 pages (GOFIN 4, Wykop 6, GitHub issues 10, HN 1) plus 1,260 app-store reviews (51 + 300 + 350 + 450 + 109) and API queries | 16 |
| [07 Founder fit](../research/07-founder-fit/README.md) | 28 | 24 | 15 |
| [08 Distribution](../research/08-distribution/README.md) | 25 | 27 | about 27 |
| [09 Unit economics](../research/09-unit-economics/README.md) | 27 | about 31 | 21 |
| **Total** | **257** | **about 257 + the gap pass** | **about 169** |

- **Distinct source URLs:** 698 across `research/*/*.md` and `ideas/*/*.md` (493 in research, 292 in write-ups, overlap counted once). Counted with `grep -oE 'https?://…' | sort -u` after stripping trailing punctuation; this includes a few API query URLs and links that only appear as "search summary".
- **Countries:** 18 appear in the lens Coverage sections as a source of findings or foreign analogues (union, counted by hand): Poland, Germany, US, UK, Canada, Italy, Australia, India, Denmark, Netherlands, France, Japan, Czechia, Norway, Spain, Brazil, Estonia, Romania. Germany and the US are the only foreign markets covered in more than three lenses.
- **Languages searched:** Polish, English, German in most lenses; Czech, Spanish and French only as autocomplete or a few app-store queries (lens 06).
- **Link checks:** every task T01–T16 ended with 0 dead links; unverifiable links (403/429/timeouts) are listed per task in [PROGRESS.md](../PROGRESS.md).

## 3. Top 20 (sorted by weighted score after review)
**How this table was built.** Rows of shortlist.csv sorted by its `rank` column (unrounded weighted score, ties broken by higher L6 then L3). For the 25 write-ups the scores are the post-review (T16) values; for the other rows they are the T12 quick scores. **Rejected and merged rows are excluded** (I062 at rank 1, I061 at rank 3 and I050/write-up 008 at rank 15 fall in this range), so the table runs to shortlist rank 23. Status:
- **Reviewed** = full write-up with ≥5 sources plus a devil's-advocate review.
- **Quick score only** = one-line idea scored from the lens findings, never researched further. Treat these scores as optimistic: during write-up research most scores fell by 0.0–0.6 and only one rose (008, later rejected) (T13–T15 run log), and the average competition score (L2) of the 15 rejected write-ups is 1.1 against 2.8 for the quick-scored rows (mean of the `L2` column, counted).

| # | Rank | Idea | Field | Weighted | Band | Status | Note |
|---|---|---|---|---|---|---|---|
| 1 | 2 | [003 Self-hosted KSeF gateway licence](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) (I063) | developer-tools-apis | 3.1 | 5–15% | Reviewed | Only reviewed idea above 2.8 |
| 2 | 4 | I023 Quote → Abschlagsrechnung → Lieferschein mobile app for German trades ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 3.0 | 5–15% | Quick score only | Skipped for write-up by the 3-per-field rule; German, mobile-first (L7 = 2); see Wildcards |
| 3 | 5 | I011 Client accept / query / reject workflow for purchase invoices ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.9 | 5–15% | Quick score only | Its own reason says "best as a feature of I010" (= 001) |
| 4 | 6 | I013 Bank-account mismatch alert for incoming invoices ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.9 | 5–15% | Quick score only | Pain evidence is one thread (L6-F04); the white-list API is free |
| 5 | 7 | I028 Cookie and single-consent audit for agencies (PKE) ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.8 | 5–15% | Quick score only | Cookiebot and iubenda already serve Poland |
| 6 | 8 | I029 Accessibility scan and monthly monitor for Polish e-shops ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.8 | 5–15% | Quick score only | No Polish shop heard asking |
| 7 | 9 | I021 Timesheet → invoice → KSeF for B2B IT contractors ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.8 | 5–15% | Quick score only | Pain not measured; invoicing tools are cheap |
| 8 | 10 | I080 Inbox triage agent for accounting offices ([shortlist.csv](../ideas/shortlist.csv)) | ai-agents-automation | 2.8 | 5–15% | Quick score only | Related to [012](../ideas/ai-agents-automation/012-email-to-accountant-agent-for-jdg.md), rejected in T16 because incumbents already offer client-document intake |
| 9 | 11 | I022 German E-Rechnung receiver and archive, one-off licence ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.8 | 5–15% | Quick score only | Same market where [002](../ideas/developer-tools-apis/002-xrechnung-zugferd-validator-api.md) was rejected (free hosted German tools) |
| 10 | 12 | [004 "Podgląd KSeF" viewer + paid watcher](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md) (I015) | accounting-invoicing-tax | 2.7 | <5% | Reviewed | Best-documented end-user pain; T16 suggests folding into 001 |
| 11 | 13 | [005 Self-serve whistleblower channel](../ideas/legal-compliance/005-self-serve-whistleblower-channel.md) (I025) | legal-compliance | 2.7 | <5% | Reviewed | L2 = 1: at least eight Polish providers |
| 12 | 14 | I103 Service-contract and annual-inspection CRM for heat-pump installers ([shortlist.csv](../ideas/shortlist.csv)) | energy-pv-heat-pumps | 2.7 | <5% | Quick score only | L6 = 1 (no installer heard asking) → knock-out to <5% |
| 13 | 16 | [006 Google review request and reply assistant](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md) (I004) | b2b-saas-pl-smes | 2.7 | <5% | Reviewed | Google itself is testing AI reply drafts |
| 14 | 17 | I018 Cost-document extraction API for offices ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.7 | <5% | Quick score only | T16 found SaldeoSMART, wFirma, Fakturownia and Comarch bundle intake and OCR (012 and 013 in [rejected.md](../rejected.md)) |
| 15 | 18 | I033 RODO register and breach log for micro firms, sold via outsourced IODs ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.7 | <5% | Quick score only | No IOD heard asking |
| 16 | 19 | I036 CBAM supplier-data collection for small importers ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.7 | <5% | Quick score only | Dated trigger 1 Feb 2027 (L5-F17); audience uncounted |
| 17 | 20 | I068 KSeF outage-tolerant send queue ([shortlist.csv](../ideas/shortlist.csv)) | developer-tools-apis | 2.7 | <5% | Quick score only | T13 noted it duplicates the send queue inside 003 |
| 18 | 21 | I131 Matura / egzamin ósmoklasisty open-answer grader ([shortlist.csv](../ideas/shortlist.csv)) | education-exams | 2.7 | <5% | Quick score only | Consumer, seasonal; see Wildcards |
| 19 | 22 | I002 Proposal → contract → invoice flow for freelancers and small studios ([shortlist.csv](../ideas/shortlist.csv)) | b2b-saas-pl-smes | 2.7 | <5% | Quick score only | No complaints, no Polish price evidence |
| 20 | 23 | I006 Payment reminders and wezwanie do zapłaty generator ([shortlist.csv](../ideas/shortlist.csv)) | b2b-saas-pl-smes | 2.7 | <5% | Quick score only | Invoicing tools likely cover reminders |

Ranks 24–31 also score 2.7 (quick scores, all `<5%`). The other reviewed survivors rank lower:

| Rank | Idea | Field | Weighted | Band | Why it is still standing |
|---|---|---|---|---|---|
| 34 | [015 NIS2/KSC supplier-questionnaire kit](../ideas/legal-compliance/015-nis2-supplier-questionnaire-kit.md) (I027) | legal-compliance | 2.6 | <5% | Dated 2027 duty, over 10,000 covered entities; must beat a free open-source rival (NISD2.eu) |
| 35 | [001 KSeF inbox for bookkeeping offices](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) (I010, absorbs [007](../ideas/accounting-invoicing-tax/007-delegated-ksef-access-and-token-manager.md)) | accounting-invoicing-tax | 2.6 | <5% | Offices pay per client; must beat a ~4 PLN/client reference price |
| 37 | [020 Feed manager for Polish comparison sites](../ideas/ecommerce-sellers/020-feed-manager-polish-comparison-sites.md) (I053) | ecommerce-sellers | 2.6 | <5% | Narrow Ceneo-validation wedge; nearly free to test |
| 56 | [017 Heat-pump sizing and offer generator](../ideas/energy-pv-heat-pumps/017-heat-pump-sizing-and-offer-generator.md) (I102) | energy-pv-heat-pumps | 2.6 | <5% | People pay ~800 PLN for an OZC calculation; brand tools are free |
| 78 | [011 Cash-flow forecast from KSeF](../ideas/b2b-saas-pl-smes/011-cash-flow-forecast-from-ksef.md) (I005) | b2b-saas-pl-smes | 2.4 | <5% | No Polish KSeF forecast product found; banks can add it at will |
| 80 | [014 Assembly minutes and uchwała drafts](../ideas/real-estate-construction/014-assembly-minutes-and-uchwala-drafts.md) (I093) | real-estate-construction | 2.4 | <5% | L6 = 1 knock-out; no direct Polish competitor |
