# T20 — filter and shortlist

**Model:** fable (medium effort) · **Needs:** T19

Read `projects/idea-generator/phase2/BRIEF.md` first and follow its Rules. Commit and push after every small unit and keep your Resume line in `phase2/PROGRESS.md` current. Run the link check on changed files before reporting DONE.

1. Merge near-duplicates. Drop ideas that break "Won't do" in the brief, aren't innovative by the brief's definition, or are clearly unrealistic. Each dropped idea goes to `rejected.md` with a one-line reason.
2. Quick-score the rest on L1–L9 (`method/criteria.md`) and write `ideas/shortlist.csv` with about 60 ideas. Columns: id, name, field, type, b2b_b2c, L1..L9, weighted, chance band, one-sentence reason, top opportunity, top risk, write_up (y/n), path.
3. Mark the **top ~24** as `write_up=y`, keeping a balance across fields and at least 6 B2C ideas only if they score well. Number them 001–024 and split them into batches A = 001–008, B = 009–016, C = 017–024.

**Done when:** every longlist idea is either in shortlist.csv or in rejected.md, and about 24 are marked for write-up.
