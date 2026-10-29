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
| Researched in depth | 27 | 25 write-ups + 2 ideas (I062, I061, see [rejected.md](../rejected.md)) that collapsed during write-up research and were swapped out (T13) |
| **Written up** | **25** | files `ideas/<field>/NNN-*.md` |
| **Rejected or merged after the review (T16)** | **15** (14 rejected, 1 merged into [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md)) | "T16 review" section |
| **Write-ups still standing** | **10** | 25 − 15 |
| Shortlisted ideas never researched beyond the quick score | 81 | 108 − 27 |
| Every rejection, all stages | 126 lines | 9 + 16 + 3 + 81 + 2 + 15 |

Bands in shortlist.csv after the review: 11 rows `5–15%`, 97 rows `<5%` (counted with Python `collections.Counter` on the `chance_band` column). Of the 11 `5–15%` rows, 2 are rejected (I062, I061, [rejected.md](../rejected.md)), 1 is the reviewed survivor [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md), and 8 are quick scores that were never researched.

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
**How this table was built.** Rows of shortlist.csv sorted by its `rank` column (unrounded weighted score, ties broken by higher L6 then L3). For the 25 write-ups the scores are the post-review (T16) values; for the other rows they are the T12 quick scores. **Rejected and merged rows are excluded** (I062 at rank 1, I061 at rank 3 and I050/write-up [008](../ideas/ecommerce-sellers/008-woocommerce-ksef-bridge.md) at rank 15 fall in this range; reasons in [rejected.md](../rejected.md)), so the table runs to shortlist rank 23. Status:
- **Reviewed** = full write-up with ≥5 sources plus a devil's-advocate review.
- **Quick score only** = one-line idea scored from the lens findings, never researched further. Treat these scores as optimistic: during write-up research most scores fell by 0.0–0.6 and only one rose ([008](../ideas/ecommerce-sellers/008-woocommerce-ksef-bridge.md), later rejected) (T13–T15 run log), and the average competition score (L2) of the 15 rejected write-ups is 1.1 against 2.8 for the quick-scored rows (mean of the `L2` column, counted).

| # | Rank | Idea | Field | Weighted | Band | Status | Note |
|---|---|---|---|---|---|---|---|
| 1 | 2 | [003 Self-hosted KSeF gateway licence](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) (I063) | developer-tools-apis | 3.1 | 5–15% | Reviewed | Only reviewed idea above 2.8 |
| 2 | 4 | I023 Quote → Abschlagsrechnung → Lieferschein mobile app for German trades ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 3.0 | 5–15% | Quick score only | Skipped for write-up by the 3-per-field rule; German, mobile-first (L7 = 2); see Wildcards |
| 3 | 5 | I011 Client accept / query / reject workflow for purchase invoices ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.9 | 5–15% | Quick score only | Its own reason says "best as a feature of I010" (= [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md)) |
| 4 | 6 | I013 Bank-account mismatch alert for incoming invoices ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.9 | 5–15% | Quick score only | Pain evidence is one thread (L6-F04); the white-list API is free |
| 5 | 7 | I028 Cookie and single-consent audit for agencies (PKE) ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.8 | 5–15% | Quick score only | Cookiebot and iubenda already serve Poland |
| 6 | 8 | I029 Accessibility scan and monthly monitor for Polish e-shops ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.8 | 5–15% | Quick score only | No Polish shop heard asking |
| 7 | 9 | I021 Timesheet → invoice → KSeF for B2B IT contractors ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.8 | 5–15% | Quick score only | Pain not measured; invoicing tools are cheap |
| 8 | 10 | I080 Inbox triage agent for accounting offices ([shortlist.csv](../ideas/shortlist.csv)) | ai-agents-automation | 2.8 | 5–15% | Quick score only | Related to [012](../ideas/ai-agents-automation/012-email-to-accountant-agent-for-jdg.md), rejected in T16 because incumbents already offer client-document intake |
| 9 | 11 | I022 German E-Rechnung receiver and archive, one-off licence ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.8 | 5–15% | Quick score only | Same market where [002](../ideas/developer-tools-apis/002-xrechnung-zugferd-validator-api.md) was rejected (free hosted German tools) |
| 10 | 12 | [004 "Podgląd KSeF" viewer + paid watcher](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md) (I015) | accounting-invoicing-tax | 2.7 | <5% | Reviewed | Best-documented end-user pain; T16 suggests folding into [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) |
| 11 | 13 | [005 Self-serve whistleblower channel](../ideas/legal-compliance/005-self-serve-whistleblower-channel.md) (I025) | legal-compliance | 2.7 | <5% | Reviewed | L2 = 1: at least eight Polish providers |
| 12 | 14 | I103 Service-contract and annual-inspection CRM for heat-pump installers ([shortlist.csv](../ideas/shortlist.csv)) | energy-pv-heat-pumps | 2.7 | <5% | Quick score only | L6 = 1 (no installer heard asking) → knock-out to <5% |
| 13 | 16 | [006 Google review request and reply assistant](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md) (I004) | b2b-saas-pl-smes | 2.7 | <5% | Reviewed | Google itself is testing AI reply drafts |
| 14 | 17 | I018 Cost-document extraction API for offices ([shortlist.csv](../ideas/shortlist.csv)) | accounting-invoicing-tax | 2.7 | <5% | Quick score only | T16 found SaldeoSMART, wFirma, Fakturownia and Comarch bundle intake and OCR ([012](../ideas/ai-agents-automation/012-email-to-accountant-agent-for-jdg.md) and [013](../ideas/ai-agents-automation/013-bank-statement-categoriser-for-offices.md), see [rejected.md](../rejected.md)) |
| 15 | 18 | I033 RODO register and breach log for micro firms, sold via outsourced IODs ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.7 | <5% | Quick score only | No IOD heard asking |
| 16 | 19 | I036 CBAM supplier-data collection for small importers ([shortlist.csv](../ideas/shortlist.csv)) | legal-compliance | 2.7 | <5% | Quick score only | Dated trigger 1 Feb 2027 (L5-F17); audience uncounted |
| 17 | 20 | I068 KSeF outage-tolerant send queue ([shortlist.csv](../ideas/shortlist.csv)) | developer-tools-apis | 2.7 | <5% | Quick score only | T13 noted it duplicates the send queue inside [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) |
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

## 4. Top 5 for validation
**How the five were picked.** Only reviewed write-ups qualify: quick scores have fallen by up to 0.6 under research, so testing an unresearched idea first would waste the week. From the 10 survivors I took the highest score ([003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md)), then preferred ideas whose test measures *behaviour* (pre-orders, submitted feeds, reviews produced) over stated interest and that do not rely on cold e-mail. That gives [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md), [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md), [004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md), [006](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md), [020](../ideas/ecommerce-sellers/020-feed-manager-polish-comparison-sites.md). Not picked, though they score the same or higher than [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md)/020:
- [005 whistleblower channel](../ideas/legal-compliance/005-self-serve-whistleblower-channel.md) (2.7): L2 = 1 (eight or more Polish providers, sub-250 PLN plans); its test needs 40 cold HR contacts plus 100 PLN for a lawyer review. Keep as reserve if the reseller route via accounting offices comes up in the [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) interviews.
- [015 NIS2 supplier kit](../ideas/legal-compliance/015-nis2-supplier-questionnaire-kit.md) (2.6): the core feature exists free and open source (NISD2.eu); the test is 40 LinkedIn cold contacts, whose PKE status lens 08 could not settle.
- [017 heat-pump offers](../ideas/energy-pv-heat-pumps/017-heat-pump-sizing-and-offer-generator.md) (2.6): free brand tools plus seasonal churn; reserve.

**Constraints the plans respect.**
- **Cold e-mail:** PKE art. 398 requires prior consent for commercial information sent to companies as well as people ([L8-F13](../research/08-distribution/partners-lists-and-law.md)); whether a plain research-interview request without an offer counts is not settled in the research (lens 08 Gap 4: no UODO/UKE guidance found). The plans therefore use public posts, replies in public threads, in-person visits and inbound forms, and only send an offer to people who wrote first or asked for it. This is a reading of the research, not legal advice.
- **Time and money** (estimates): the five tests together need about 30–35 hours and about 400–480 PLN. That is three weeks of the 10 h/week budget and almost the whole 500 PLN monthly budget, so run them in the order given in section 5, not all at once.
- **Shared infrastructure:** one cheap domain with a sub-page per test (or a free static-host subdomain) instead of five domains; the agent stack builds each page.

### 4.1 [003 Self-hosted KSeF gateway licence](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) — 3.1, `5–15%`
**Why it is here.** The only reviewed idea above 2.8. The buyers (integrators) are visibly in pain: three KSeF API threads with 70–100 comments each on tokens, duplicates and change sync (L6-F06); a self-hosted licence model has public revenue proof (EmailEngine at 1,450 USD/year, L4-F03); it is pure backend work, a good fit for the agent stack (L7 = 4).
**Riskiest assumption.** That vendors who already shipped KSeF on the free official clients before the Feb/Apr 2026 deadlines will pay to replace or offload working code (sunk cost), at 1,500–6,000 PLN/year, rather than keep patching it.
**Plan (≤1 week, about 6–8 h, about 50 PLN for a domain, estimate).**
1. Day 1 (agent builds, you review, ~2 h): a public GitHub repo with README, OpenAPI spec of the gateway (sessions, certificates/tokens, send queue with duplicate guard, purchase-invoice mirror, webhooks), a docker-compose stub that returns mock responses, and a one-page site: "KSeF gateway: REST + webhooki w Twoim Dockerze. Licencja 3 000 PLN/rok, pilotaż bezpłatny", with a "request a pilot" form asking: what did you build for KSeF, what breaks, how many taxpayer contexts.
2. Day 1, ~1 h: record a 3-minute screencast of the API design against the KSeF test environment docs.
3. Days 2–3, ~2 h: post where the target buyers already talk, only where on topic: reply with concrete help in the open [CIRFMF/ksef-api](https://github.com/CIRFMF/ksef-api/issues) issues about tokens, duplicates and limits and link the repo; one post each in Wykop #ksef and one Polish developer forum.
4. Days 2–4, ~2 h: list 30 small vendors whose sites mention KSeF integration (Google search for "integracja z KSeF" + "program do faktur"/"ERP"); send each a research question through its own contact form, no offer ("we are mapping what vendors built for KSeF; 15 minutes?"). Send the price only to those who answer.
5. Day 5: count, and in each call ask what they built, what it costs them to maintain, and whether they would pay 3,000 PLN/year to stop maintaining it.
**Go:** ≥5 pilot requests or replies asking for details, ≥2 accept the stated price for after the pilot, ≥30 GitHub stars or ≥3 issues/forks from strangers in the week (the GitHub threshold is mine, not from the write-up). **No-go:** fewer than 3 of 30 vendors say they would use a gateway rather than the official client; or ≥2 report they already licence a comparable gateway for <1,000 PLN/year; or the ministry ships a webhook/event model (write-up kill criteria).

### 4.2 [001 KSeF inbox for bookkeeping offices](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) — 2.6, `<5%` (absorbs [007](../ideas/accounting-invoicing-tax/007-delegated-ksef-access-and-token-manager.md))
**Why it is here.** It is the largest paying audience with a per-client price model already in the market (Fakturownia, FakturaXL, wFirma charge offices per client), KSeF is a hard dated trigger (L5 = 4), and offices are a referral channel for several other ideas ([004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md), [005](../ideas/legal-compliance/005-self-serve-whistleblower-channel.md) reseller route, [011](../ideas/b2b-saas-pl-smes/011-cash-flow-forecast-from-ksef.md)). It also hosts the features of [007](../ideas/accounting-invoicing-tax/007-delegated-ksef-access-and-token-manager.md) (permissions and certificates) and of [004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md) (watcher) if those do not stand alone.
**Riskiest assumption.** That offices on desktop programs (Optima, Symfonia, Rewizor, Rachmistrz) lack a usable multi-client purchase-invoice inbox and would pay more than the ~4 PLN/client that FakturaXL charges with KSeF included.
**Plan (≤1 week, about 7–8 h, about 50 PLN, estimate).**
1. Day 1 (~2 h): landing page "Jedna skrzynka KSeF dla wszystkich klientów biura — 6 PLN/klient/mies., rocznie" with screenshots of a clickable mock (agent-built) showing all clients' new purchase invoices, accept/reject, per-client archive, certificate status; form "chcę pilotaż" plus a 10-question interview script (which program, how many clients, how you get purchase invoices today, what it costs, what you would pay).
2. Days 1–3 (~3 h): answer current KSeF questions in the [GOFIN KSeF forum](https://forum.gofin.pl/dzialy-forum/ksef) with useful content and a signature link; post one short "how do you handle 50 clients' purchase invoices in KSeF?" thread; ask the offices you or your own accountant know personally for introductions (a warm route the research did not cover).
3. Days 2–4 (~2 h): phone or visit (not e-mail) 20 local offices whose websites name a desktop program; ask only for a 15-minute research interview. Note: lens 08 did not settle whether art. 398 also covers B2B phone calls; keep calls to research, never an offer.
4. Day 5: interviews; at the end of each, state the price and ask for a paid pilot (first month invoiced after 30 days).
**Go:** ≥15 interviews done, ≥5 say the missing multi-client inbox costs them time weekly, ≥3 agree to a paid pilot at ≥6 PLN/client. **No-go:** <3 of 15 say it is a problem they would pay for; or ≥2 say their vendor ships a multi-client inbox before launch; or the first 5 want ≤4 PLN/client (write-up kill criteria, adjusted to the T16 4 PLN reference).

### 4.3 [004 "Podgląd KSeF" viewer + paid watcher](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md) — 2.7, `<5%`
**Why it is here.** The best-documented end-user pain in the whole set (12 of 51 sampled reviews of the state KSeF app ask for notifications, L6-F01), unserved "bez logowania" search phrases (L8-F16, F17), and the cheapest test to run with almost no founder time: it is a pure demand test with ads.
**Riskiest assumption.** That micro-firms who do not use an invoicing program will pay ~19 PLN/month for notifications when two free notifier apps, open-source watchers and firmly (USD 3.99/month) exist, and will trust an e-mail about KSeF invoices after CERT Polska's phishing warning.
**Plan (≤1 week, about 4–5 h, about 200 PLN, estimate).**
1. Day 1 (agent builds, ~1.5 h review): a one-page site where the XML is rendered in the browser and never uploaded (say so prominently, it answers the phishing worry), built on the free MIT [CIRFMF/ksef-pdf-generator](https://github.com/CIRFMF/ksef-pdf-generator) or [niutech/ksef-xml-pdf](https://github.com/niutech/ksef-xml-pdf); below it "Powiadom mnie o nowych fakturach w KSeF — 19 PLN/mies." with an e-mail waitlist and a Stripe pre-order link (refund promised if it does not launch).
2. Day 1 (~1 h): in Google Ads Keyword Planner record monthly volume and CPC for "podgląd faktury ksef", "ksef bez logowania", "powiadomienia ksef" and 5–10 variants; save the numbers in the write-up.
3. Days 2–6: run 150 PLN of search ads on those phrases; post the viewer once in the GOFIN forum and Wykop #ksef as a free tool.
4. Day 7 (~1 h): count visitors, sign-ups, pre-orders, cost per click.
**Go:** ≥300 visitors, ≥20 waitlist sign-ups, ≥3 paid pre-orders, and Keyword Planner shows ≥100 monthly searches for the target phrases. **No-go:** <10 sign-ups from 300 visitors; or <100 monthly searches; or the ministry announces push/e-mail notifications. If 150 PLN buys far fewer than 300 clicks, that is itself a no-go for paid acquisition; then judge only the sign-up rate. If the result is weak but the office interviews in 4.2 ask for alerts, fold this into [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) as T16 suggested.

### 4.4 [006 Google review request and reply assistant](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md) — 2.7, `<5%`
**Why it is here.** The only survivor outside KSeF/compliance with proof that the model earns (a listed Maps rank tracker at 19.1k USD/month, L4-F16), and the test produces a hard number (new reviews per 30 SMS) that decides the idea by itself. Walk-in sales avoid the cold e-mail problem.
**Riskiest assumption.** That a Polish post-visit SMS produces enough new Google reviews for owners to pay 99 PLN/month, when Google gives every profile a free review link and QR code, is testing AI reply drafts itself, and booking tools bundle review requests.
**Plan (≤1 week, about 8–10 h, about 80–130 PLN, estimate).**
1. Day 1 (~1 h): one-page offer "Więcej opinii w Google: SMS po wizycie, 99 PLN/mies." and an SMSAPI account; SMS cost 0.16–0.17 PLN each per [SMSAPI's price list](https://www.smsapi.pl/cennik) (the write-up also notes a 49 PLN/month postpaid subscription).
2. Days 1–2 (~5 h): visit 15 car workshops, dental practices and salons in one city that have fewer than 30 Google reviews (filter on Google Maps); offer a free 7-day pilot. Each sends you up to 30 recent customers' numbers **who already agreed to SMS contact from that business** (the business is the sender of record; this keeps the pilot inside PKE consent and Google's rules: no incentives, no review gating, see [Google's policy](https://support.google.com/contributionpolicy/answer/7400114?hl=pl)).
3. Day 2: send one polite SMS per customer with the business's own review link (≈450 SMS ≈ 72–77 PLN at the listed price).
4. Day 7 (~2 h): count new reviews per business, report back in person, ask for 99 PLN/month.
**Go:** ≥5% response (≥1.5 new reviews per 30 SMS) on average, ≥3 of 15 businesses get 3+ new reviews and ≥3 agree to pay 99 PLN/month. **No-go:** <3 of 15 willing to pay after seeing results; response <5%; or Google removes any pilot's reviews.

### 4.5 [020 Feed manager for Polish comparison sites](../ideas/ecommerce-sellers/020-feed-manager-polish-comparison-sites.md) — 2.6, `<5%`
**Why it is here.** The cheapest test of the five in founder time: a script and a few posts; the free audit is itself the lead magnet, the market is large (Ceneo reports about 39 thousand stores, self-reported), the product is easy to specify and test automatically (L7 = 4), and it diversifies away from KSeF. It also tells within days whether the narrow wedge (Ceneo-specific errors) exists at all.
**Riskiest assumption.** That Ceneo-specific feed errors (missing EANs, duplicate titles, wrong categories) are common and costly enough that shops pay 49 PLN/month on top of BaseLinker, plugins, Sembot or Mergado.
**Plan (≤1 week, about 4–5 h, about 0–50 PLN, estimate).**
1. Days 1–2 (agent builds, ~2 h review): "Darmowy audyt feedu Ceneo" page; the shop pastes its feed URL; a script checks it against Ceneo's published XML feed requirements (the agent must read Ceneo's own spec page; not covered in the research) and returns a report in Polish: missing EAN/GTIN, duplicate titles, empty categories, price/availability format, image URLs; at the end "Monitor co tydzień i alert o odrzuconych ofertach — 49 PLN/mies." with a pre-order button.
2. Days 2–5 (~2 h): post the free audit in Polish PrestaShop and WooCommerce groups and forums and on Wykop; the shop owner submits the feed, so every contact is inbound.
3. Day 6 (~1 h): count submissions, tally error types across audits, and reply to each submitter with the report and the offer.
**Go:** ≥20 feeds submitted, Ceneo-specific errors in at least half of them (my threshold, not from the write-up), ≥5 ask for monitoring and ≥3 accept 49 PLN/month. **No-go:** <10 feeds submitted; audits show almost no Ceneo-specific errors; or respondents say BaseLinker or their plugin export is enough.

## 5. Order of the tests and how to decide
Hours and money are estimates from the plans above; the week budget is ~10 h and the month budget 500 PLN.

| Week | Tests | Founder hours | Spend | Why this order |
|---|---|---|---|---|
| 2 | [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) gateway + [004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md) viewer/ads | ~10–13 | ~250 PLN | 003 is the strongest idea; 004 runs mostly on its own once the ads are live |
| 3 | [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) office interviews + [020](../ideas/ecommerce-sellers/020-feed-manager-polish-comparison-sites.md) feed audit | ~11–13 | ~50–100 PLN | 001 can absorb [004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md)'s result; 020 is mostly automated |
| 4 | [006](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md) concierge SMS pilot, only if nothing above passed | ~8–10 | ~80–130 PLN | Most hours, weakest moat; keep as the fallback |

**Decision rule.** Build the idea whose test hit its Go numbers with the most money committed (pre-orders or signed pilots × price). If two pass, prefer the one that needs less of your non-code time per customer (licence and self-serve before interviews and walk-ins). If none passes, do not build a `<5%` idea on hope: extend Phase 1 by researching the strongest unresearched quick-scored ideas (I023, I013, I028, I029, I021 in [shortlist.csv](../ideas/shortlist.csv)) with the same write-up and review process.

## 6. Patterns
- **Fields.** Accounting/invoicing/tax (13 shortlisted, 8 at ≥2.7, best 3.0), developer tools/APIs (11, 5 at ≥2.7, best 3.2) and legal/compliance (8, 5 at ≥2.7, best 2.8) produced most of the top ideas (counted per `field` in shortlist.csv). Ten fields have no shortlisted idea at ≥2.7: niche-b2b, local-services-booking, healthcare-admin, creators-media, data-products, agriculture, mobile-consumer-apps, hr-payroll, browser-extensions, logistics-transport; ngos-public-sector has no shortlisted idea at all.
- **KSeF dominates.** 18 of 108 shortlisted names mention KSeF, 9 of them in the top 30 by rank, and 4 of the 10 surviving write-ups build on KSeF data ([001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md), [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md), [004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md), [011](../ideas/b2b-saas-pl-smes/011-cash-flow-forecast-from-ksef.md)). The same trigger also drew the most competition: four KSeF-related write-ups were rejected or merged ([007](../ideas/accounting-invoicing-tax/007-delegated-ksef-access-and-token-manager.md), [008](../ideas/ecommerce-sellers/008-woocommerce-ksef-bridge.md), [012](../ideas/ai-agents-automation/012-email-to-accountant-agent-for-jdg.md), [013](../ideas/ai-agents-automation/013-bank-statement-categoriser-for-offices.md)) because invoicing vendors, banks and free official tools moved first.
- **Lenses that held up and lenses that broke** (mean scores from shortlist.csv). Surviving write-ups score highest on founder fit (L7 mean 3.8), why now (L5 2.9) and monetization (L3 2.8). What separated survivors from the 15 rejected write-ups was competition (L2 2.1 vs 1.1) and pain (L6 2.4 vs 2.1). Quick-scored ideas average L2 2.8 and L6 1.8: the quick scores overrate competition gaps and the whole set lacks pain evidence.
- **Lens 05 (why now) and lens 06 (pain) produced the seeds of the best ideas** (KSeF dates, KSeF GitHub threads, app-store reviews); lens 04 (copy what earns) supplied the business-model proof for [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) (EmailEngine licence) and [006](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md) (rank tracker). Lens 01 (proven abroad) found a Polish equivalent already on the market for 9 of its 26 analogues (F06, F07, F10, F12, F15, F18, F20, F23, F24 per the lens 1 README), so it seeded fewer survivors than its share of findings.
- **The typical failure** was the same in each of the 15 T16 rejections and merges: a second, more specific search found incumbents or free tools already covering the exact wedge (see the T16 section of [rejected.md](../rejected.md)). Regulation-driven ideas whose deadline has passed (whistleblower act, KSeF Feb/Apr 2026 waves) lost their "why now".
- **Types:** 88 of 108 shortlisted ideas are SaaS; the only reviewed `5–15%` idea is a self-hosted licence sold to developers, which avoids the SME churn and support load the lens 09 findings describe.

## 7. Wildcards (high risk, high upside; all quick score only, never researched)
- **I023 Quote → Abschlagsrechnung → Lieferschein app for German trades** ([shortlist.csv](../ideas/shortlist.csv), 3.0): the strongest pain signal found anywhere (292 of 350 sampled sevDesk iOS reviews are 1–2★ for missing Abschlag/Lieferschein, L6-F19) and trades already pay 55–330 EUR/month (L3-F12, F13). Against it: mobile-first (L7 = 2), German only, 13 incumbents, and German cold e-mail needs express consent (UWG § 7, L8-F14).
- **I131 Matura / egzamin ósmoklasisty open-answer grader** ([shortlist.csv](../ideas/shortlist.csv), 2.7): Polish consumer AI products do sell (Czat.ai, L4-F10) and Polish-language exam content is a moat; but demand is seasonal and parents' willingness to pay is untested.
- **I072 Missed-call voice receptionist for car workshops** ([shortlist.csv](../ideas/shortlist.csv), 2.7): new speech-to-speech and SIP prices make it possible now (L5-F25, F26); Polish voice quality and workshop demand are unproven.
- **I066 MCP spec conformance tester** ([shortlist.csv](../ideas/shortlist.csv), 2.7): founder fit 5, global developer audience, a dated breaking revision (MCP 2026-07-28, L5-F23); willingness to pay untested and the nine free Allegro MCP servers found in T16 suggest the MCP ecosystem expects free tools.

## 8. What the research covered poorly
- **Pain evidence (lens 06):** Reddit, Polish Facebook groups, Trustpilot, G2, Capterra and Google Trends could not be read (blocked or 429); no keyword volumes were measured anywhere. L6 averages 1.8 on quick-scored ideas mostly for this reason, so the [004](../ideas/accounting-invoicing-tax/004-podglad-ksef-viewer-and-watcher.md) Keyword Planner step is the first real volume data.
- **Customer counts:** bookkeeping offices (35,000–70,000 in conflicting search summaries), KSeF software vendors, heat-pump installers, wspólnoty and their managers are unverified; NIS2 entities range from >10,000 to "over 40,000". The criteria's 20× market check could therefore not be applied properly.
- **Markets:** Korea, Sweden, Finland (one page read, not used) and the Baltics beyond Estonia were not covered; no systematic discovery through Product Hunt, G2 or Capterra category lists; Chrome, WordPress and Shopify store top lists were not fetched (lens 04 Coverage). German-language sources are thin in lenses 07 and 09.
- **Churn and unit economics:** churn figures are US/global only; no Polish or German SMB churn study was found (lens 09).
- **Law on outreach:** no UODO/UKE guidance on B2B cold e-mail or LinkedIn messages under PKE art. 398 (lens 08 Gap 4).
- **Depth:** 81 shortlisted ideas, including 8 in the `5–15%` band, were never researched; 9 of 22 fields got no write-up (agriculture, logistics-transport, hospitality-tourism, creators-media, digital-products, browser-extensions, mobile-consumer-apps, ngos-public-sector, niche-b2b).
- Several pages were read through a summarising fetch tool and many figures are marked "search summary"; re-check any number before using it in a customer-facing claim.

## 9. Open questions for you
1. **Who do you want to sell to?** [003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) means selling annual licences to CTOs (few, technical, longer calls); [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md)/004 mean accountants and micro-firms (many, Polish-speaking, support-heavy). Which fits your 10 h/week better?
2. **Phone calls and walk-ins:** are you willing to do them for [001](../ideas/accounting-invoicing-tax/001-ksef-inbox-bookkeeping-offices.md) and [006](../ideas/b2b-saas-pl-smes/006-google-review-request-and-reply-assistant.md)? The plans avoid cold e-mail; without calls or visits those two tests lose most of their reach.
3. **Warm contacts:** do you personally know bookkeeping offices, ERP/e-shop software vendors or shop owners? A warm list would change the order of the tests; the research could not see your network.
4. **Legal comfort:** do you want a one-off opinion from a Polish privacy lawyer on B2B outreach under PKE art. 398 before any outbound (cost not researched)?
5. **German market:** would you sell in German (I023, I022)? It is the strongest pain signal found, but it is outside Polish-language advantages.
6. **Bar for building:** if a `<5%` idea passes its Go numbers, will you build it, or do you want Phase 1 extended to research the unresearched `5–15%` quick-scored ideas first?
7. **Licence and support:** is selling a self-hosted Docker product ([003](../ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md)) acceptable given you would support it in customers' environments, which is lighter on-call than SaaS but not zero?

