# idea-generator

Phase 1 research to help a Polish solo developer pick one product to build and sell within a month. The work runs as a funnel: research through 9 lenses, ~200 one-line ideas, a scored shortlist of ~100, full write-ups of the top ~25, a skeptical review, and cheap validation plans for the top 3–5. Nothing gets built in this phase.

## How to read it
- **Results:** start with `reports/phase1-summary.md` (written by T17). Until it exists, the most useful files are the shortlist `ideas/shortlist.csv` and the write-ups in `ideas/<field>/`.
- **How ideas are scored:** [method/criteria.md](method/criteria.md) has the 1–5 rubric per lens, the weights, and how the weighted score maps to a chance band of reaching 10,000 PLN MRR.
- **Research behind the ideas:** `research/NN-<lens>/README.md`, one folder per lens.
- **Dropped ideas and later corrections:** [rejected.md](rejected.md) and [CHANGELOG.md](CHANGELOG.md).
- **Method and rules:** [BRIEF.md](BRIEF.md). Task instructions are in [tasks/](tasks/), and [RUNNER.md](RUNNER.md) describes the scheduled run.

## Status
Live status is in [PROGRESS.md](PROGRESS.md). So far, T01 (setup and method) has set up the folder, the scoring criteria and the link checker. Lens research (T02–T10) comes next.

## Link check
Every factual claim carries a source URL. Before a task is marked done, its changed files go through the link checker:
```
python3 tools/check_links.py <files>        # exit 1 only if a link is dead
cd tools && python3 -m unittest             # tests for the checker
```
