# Phase 2 progress

Markers: `[ ]` to do · `[~]` in progress · `[x]` done · `[!]` blocked (see Blocked).
A task can start when every task in its `needs` is `[x]`. Runs take the first `[~]` task, otherwise the first `[ ]` task that's ready.
Under each `[~]` task keep one indented **Resume:** line saying exactly where to continue.
Every task runs on **opus at medium effort** (see RUNNER.md).

## Tasks
- [x] T01 · setup and method · needs: — · [tasks/01-setup-and-method.md](tasks/01-setup-and-method.md)
  Unverifiable links (bot-blocked, sites exist): g2.com/best-software-companies/fastest-growing, netokracija.com, qstp.org.qa, cuti.org.uy, brutkasten.com, datanews.be, timesofmalta.com
- [ ] T02 · Poland baseline: demography and social change · needs: T01 · [tasks/02-poland-baseline-demography-and-social-ch.md](tasks/02-poland-baseline-demography-and-social-ch.md)
- [ ] T03 · Poland baseline: AI landscape and local moats · needs: T01 · [tasks/03-poland-baseline-ai-landscape-and-local-m.md](tasks/03-poland-baseline-ai-landscape-and-local-m.md)
- [ ] T04 · global trend lists · needs: T01 · [tasks/04-global-trend-lists.md](tasks/04-global-trend-lists.md)
- [ ] T05 · regional scan R1 North America · needs: T01 · [tasks/05-regional-scan-r1-north-america.md](tasks/05-regional-scan-r1-north-america.md)
- [ ] T06 · regional scan R2 UK & Ireland · needs: T01 · [tasks/06-regional-scan-r2-uk-ireland.md](tasks/06-regional-scan-r2-uk-ireland.md)
- [ ] T07 · regional scan R3 DACH & Benelux · needs: T01 · [tasks/07-regional-scan-r3-dach-benelux.md](tasks/07-regional-scan-r3-dach-benelux.md)
- [ ] T08 · regional scan R4 Nordics & Baltics · needs: T01 · [tasks/08-regional-scan-r4-nordics-baltics.md](tasks/08-regional-scan-r4-nordics-baltics.md)
- [ ] T09 · regional scan R5 France & Southern Europe · needs: T01 · [tasks/09-regional-scan-r5-france-southern-europe.md](tasks/09-regional-scan-r5-france-southern-europe.md)
- [ ] T10 · regional scan R6 CEE peers · needs: T01 · [tasks/10-regional-scan-r6-cee-peers.md](tasks/10-regional-scan-r6-cee-peers.md)
- [ ] T11 · regional scan R7 East Asia · needs: T01 · [tasks/11-regional-scan-r7-east-asia.md](tasks/11-regional-scan-r7-east-asia.md)
- [ ] T12 · regional scan R8 Oceania & Israel · needs: T01 · [tasks/12-regional-scan-r8-oceania-israel.md](tasks/12-regional-scan-r8-oceania-israel.md)
- [ ] T13 · regional scan R9 Gulf & Turkey · needs: T01 · [tasks/13-regional-scan-r9-gulf-turkey.md](tasks/13-regional-scan-r9-gulf-turkey.md)
- [ ] T14 · regional scan R10 Latin America (OECD) · needs: T01 · [tasks/14-regional-scan-r10-latin-america-oecd.md](tasks/14-regional-scan-r10-latin-america-oecd.md)
- [ ] T15 · consolidate catalogue into themes · needs: T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14 · [tasks/15-consolidate-catalogue-into-themes.md](tasks/15-consolidate-catalogue-into-themes.md)
- [ ] T16 · Poland check batch A · needs: T02, T03, T15 · [tasks/16-poland-check-batch-a.md](tasks/16-poland-check-batch-a.md)
- [ ] T17 · Poland check batch B · needs: T02, T03, T15 · [tasks/17-poland-check-batch-b.md](tasks/17-poland-check-batch-b.md)
- [ ] T18 · Poland check batch C · needs: T02, T03, T15 · [tasks/18-poland-check-batch-c.md](tasks/18-poland-check-batch-c.md)
- [ ] T19 · longlist of adaptation ideas · needs: T16, T17, T18 · [tasks/19-longlist-of-adaptation-ideas.md](tasks/19-longlist-of-adaptation-ideas.md)
- [ ] T20 · filter and shortlist · needs: T19 · [tasks/20-filter-and-shortlist.md](tasks/20-filter-and-shortlist.md)
- [ ] T21 · write-ups batch A · needs: T20 · [tasks/21-write-ups-batch-a.md](tasks/21-write-ups-batch-a.md)
- [ ] T22 · write-ups batch B · needs: T20 · [tasks/22-write-ups-batch-b.md](tasks/22-write-ups-batch-b.md)
- [ ] T23 · write-ups batch C · needs: T20 · [tasks/23-write-ups-batch-c.md](tasks/23-write-ups-batch-c.md)
- [ ] T24 · independent critical review · needs: T21, T22, T23 · [tasks/24-independent-critical-review.md](tasks/24-independent-critical-review.md)
- [ ] T25 · Phase 2 summary and validation plans · needs: T24 · [tasks/25-phase-2-summary-and-validation-plans.md](tasks/25-phase-2-summary-and-validation-plans.md)

## Blocked / questions for the owner
(none)

## Run log
<!-- newest first: YYYY-MM-DD HH:MM · task · what was done · next step -->
2026-10-30 11:00 · T01 · done: rejected.md, method/criteria.md, countries.md (51 countries), sources.md; link check 315 links, 0 dead, 7 unverifiable · next T02
2026-10-30 · T01 · owner switched the worker model from fable to opus (medium effort); T01 unblocked · next run starts T01
2026-10-30 00:46 · T01 · started; fable subagent failed with HTTP 429 (needs usage credits); nothing written; marked [!] · owner decides on credits or model (see Blocked)
