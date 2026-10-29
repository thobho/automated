# idea-generator

Phase 1 research to help a Polish solo developer pick one product to build and sell within a month. The work runs as a funnel: research through 9 lenses, ~200 one-line ideas, a scored shortlist of ~100, full write-ups of the top ~25, a skeptical review, and cheap validation plans for the top 3–5. Nothing gets built in this phase.

## How to read it
- **Results:** start with [reports/phase1-summary.md](reports/phase1-summary.md). Read it in this order: the bottom line at the top, section 4 (five validation plans, each ≤1 week and ≤200 PLN, with Go / No-go numbers), section 5 (order of the tests and the decision rule), then section 9 (open questions for you). Section 3 is the top 20 table.
- **Reviewed vs quick-scored ideas:** only the 25 write-ups in `ideas/<field>/NNN-*.md` were researched (≥5 sources) and reviewed (each ends with a **Devil's advocate** section and a **Review changes** line; rejected ones say so at the top and are listed in [rejected.md](rejected.md)). The other 81 rows of [ideas/shortlist.csv](ideas/shortlist.csv) carry quick scores only, which tended to fall by 0.0–0.6 when researched. [ideas/README.md](ideas/README.md) explains the CSV columns.
- **How ideas are scored:** [method/criteria.md](method/criteria.md) has the 1–5 rubric per lens, the weights, and how the weighted score maps to a chance band of reaching 10,000 PLN MRR.
- **Research behind the ideas:** `research/NN-<lens>/README.md`, one folder per lens.
- **Dropped ideas and later corrections:** [rejected.md](rejected.md) and [CHANGELOG.md](CHANGELOG.md).
- **Method and rules:** [BRIEF.md](BRIEF.md). Task instructions are in [tasks/](tasks/), and [RUNNER.md](RUNNER.md) describes the scheduled run.

## Status
Phase 1 research is complete up to T17 (see [PROGRESS.md](PROGRESS.md) for live status). Outcome: 208 longlist ideas → 108 shortlisted → 25 written up → 10 still standing after the skeptical review. Only [003 Self-hosted KSeF gateway licence](ideas/developer-tools-apis/003-self-hosted-ksef-gateway-licence.md) (weighted 3.1) is in the `5–15%` chance band; every other reviewed idea is `<5%`, mostly because free or cheap incumbents already cover the obvious Polish compliance and SME wedges. Next step for the owner: run the validation tests for 003, 001, 004, 006 and 020 in the order given in the summary (weeks 2–4), then pick one or extend the research.

## Link check
Every factual claim carries a source URL. Before a task is marked done, its changed files go through the link checker:
```
python3 tools/check_links.py <files>        # exit 1 only if a link is dead
cd tools && python3 -m unittest             # tests for the checker
```

## Phase 2: innovative LLM products to adapt for Poland
Phase 1 ideas were solid but not innovative. Phase 2 scans 51 developed countries for fast-growing, mostly LLM-native products, checks each theme against Polish demand, competition and demographic change, and keeps ideas where knowing Polish realities is the edge.
- **Brief:** [phase2/BRIEF.md](phase2/BRIEF.md) · **Status:** [phase2/PROGRESS.md](phase2/PROGRESS.md) · **Run procedure:** [phase2/RUNNER.md](phase2/RUNNER.md) (every task on fable, medium effort)
- **Results:** `phase2/reports/phase2-summary.md` and the Polish `phase2/reports/podsumowanie-pl.md` once T25 is done.
