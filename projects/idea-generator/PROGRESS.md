# Progress

Markers: `[ ]` to do · `[~]` in progress · `[x]` done · `[!]` blocked (see Blocked).
A task can start when every task in its `needs` is `[x]`. Runs take the first `[~]` task, otherwise the first `[ ]` task that's ready.
Under each `[~]` task keep one indented **Resume:** line saying exactly where to continue.

## Tasks
- [x] T01 · setup and method · opus · needs: — · [tasks/01-setup-and-method.md](tasks/01-setup-and-method.md)
  Unverifiable links (criteria.md): producthunt.com, g2.com, allegro.pl, trustpilot.com (403); bdl.stat.gov.pl, elektroda.pl (timeout)
- [x] T02 · research lens 01 — Proven abroad, missing in Poland · sonnet · needs: T01 · [tasks/02-research-lens-01-proven-abroad-missing-i.md](tasks/02-research-lens-01-proven-abroad-missing-i.md)
  Unverifiable links: malt.com (403, lens files); criteria.md ones as in T01
- [~] T03 · research lens 02 — Weak or no competition · sonnet · needs: T01 · [tasks/03-research-lens-02-weak-or-no-competition.md](tasks/03-research-lens-02-weak-or-no-competition.md)
  Resume: F01..F11 written (allegro-and-ecommerce-tools.md, dev-tools-and-polish-apis.md). Next: DACH/EU + PL vertical SaaS findings (F12+), then README with Seeds/Coverage/Gaps, criteria.md sources, link check
- [ ] T04 · research lens 03 — Clear monetization · sonnet · needs: T01 · [tasks/04-research-lens-03-clear-monetization.md](tasks/04-research-lens-03-clear-monetization.md)
- [ ] T05 · research lens 04 — Copy what already makes money · sonnet · needs: T01 · [tasks/05-research-lens-04-copy-what-already-makes.md](tasks/05-research-lens-04-copy-what-already-makes.md)
- [ ] T06 · research lens 05 — Why now: regulation and tech triggers · sonnet · needs: T01 · [tasks/06-research-lens-05-why-now-regulation-and.md](tasks/06-research-lens-05-why-now-regulation-and.md)
- [ ] T07 · research lens 06 — Evidence of pain and demand · sonnet · needs: T01 · [tasks/07-research-lens-06-evidence-of-pain-and-de.md](tasks/07-research-lens-06-evidence-of-pain-and-de.md)
- [ ] T08 · research lens 07 — Founder fit and feasibility · sonnet · needs: T01 · [tasks/08-research-lens-07-founder-fit-and-feasibi.md](tasks/08-research-lens-07-founder-fit-and-feasibi.md)
- [ ] T09 · research lens 08 — Cheap distribution · sonnet · needs: T01 · [tasks/09-research-lens-08-cheap-distribution.md](tasks/09-research-lens-08-cheap-distribution.md)
- [ ] T10 · research lens 09 — Unit economics and defensibility · sonnet · needs: T01 · [tasks/10-research-lens-09-unit-economics-and-defe.md](tasks/10-research-lens-09-unit-economics-and-defe.md)
- [ ] T11 · gap pass and longlist · opus · needs: T02, T03, T04, T05, T06, T07, T08, T09, T10 · [tasks/11-gap-pass-and-longlist.md](tasks/11-gap-pass-and-longlist.md)
- [ ] T12 · filter and shortlist · opus · needs: T11 · [tasks/12-filter-and-shortlist.md](tasks/12-filter-and-shortlist.md)
- [ ] T13 · write-ups batch A · sonnet · needs: T12 · [tasks/13-write-ups-batch-a.md](tasks/13-write-ups-batch-a.md)
- [ ] T14 · write-ups batch B · sonnet · needs: T12 · [tasks/14-write-ups-batch-b.md](tasks/14-write-ups-batch-b.md)
- [ ] T15 · write-ups batch C · sonnet · needs: T12 · [tasks/15-write-ups-batch-c.md](tasks/15-write-ups-batch-c.md)
- [ ] T16 · independent critical review · opus · needs: T13, T14, T15 · [tasks/16-independent-critical-review.md](tasks/16-independent-critical-review.md)
- [ ] T17 · Phase 1 summary and validation plans · opus · needs: T16 · [tasks/17-phase-1-summary-and-validation-plans.md](tasks/17-phase-1-summary-and-validation-plans.md)

## Blocked / questions for the owner
(none)

## Run log
<!-- newest first: YYYY-MM-DD HH:MM · task · model · what was done · next step -->
2026-10-29 11:57 · T02 · sonnet · lens 01: 18 findings (L1-F01..F18) in 4 topic files, 9 countries, 11 seeds, coverage, 8 gaps; link check 0 dead · next T03
2026-10-29 11:49 · T01 · opus · README, CHANGELOG, rejected, method/criteria.md (rubric, weights, bands, sources), tools/check_links.py + 13 tests passing; link check 42 ok/0 dead/6 unverifiable · next T02
