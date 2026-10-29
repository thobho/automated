# T12 — filter and shortlist

**Model:** opus · **Needs:** T11

Read `projects/idea-generator/BRIEF.md` first and follow its Rules. Commit and push often (see Rules). Run the link check on changed files before marking the task done.

1. Merge near-duplicates. Drop ideas that break "Won't do" or are clearly unrealistic → `rejected.md` with a one-line reason each.
2. Quick-score the rest on the 9 lenses (from what's in research/ plus a quick check) and write `ideas/shortlist.csv` with ~100 ideas: id, name, field, type, L1..L9, weighted, chance band, one-sentence reason, write_up (y/n), path (filled in by the write-ups).
3. Mark the **top ~25** as `write_up=y`, keeping some balance across fields. Number them 001–025 and split them into three batches: A = 001–009, B = 010–017, C = 018–025.

**Done when:** every longlist idea is either in shortlist.csv or rejected.md, and exactly ~25 are marked for write-up.
