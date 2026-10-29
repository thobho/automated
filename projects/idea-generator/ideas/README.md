# Ideas

- [longlist.md](longlist.md): 208 one-line ideas in 22 fields (T11).
- [shortlist.csv](shortlist.csv): 108 quick-scored ideas (T12). Write-ups (T13–T15) go to `ideas/<field>/NNN-<slug>.md`.
- Every longlist ID not in shortlist.csv is in [../rejected.md](../rejected.md) with a one-line reason (merge, drop, or below the cut).

## shortlist.csv columns
| Column | Meaning |
|---|---|
| rank | Order by unrounded weighted score (ties: higher L6, then L3) |
| id, name, field | Longlist ID, name and field, unchanged |
| type | SaaS / API / library / extension / service / digital product / mobile app / marketplace |
| L1..L9 | Quick scores 1–5 per [../method/criteria.md](../method/criteria.md). Taken from the research/ findings cited in `reason`. A 4 or 5 always cites a finding; ideas whose demand rests only on an unverified complaint get L6 = 1 |
| weighted | Σ score × weight, rounded to one decimal |
| chance_band | Band from the criteria table, after knock-outs (L3 = 1 or L6 = 1 → `<5%`) |
| reason | One sentence with the finding IDs behind the scores |
| write_up | `y` for the 25 ideas that get a full write-up |
| wu_no | Write-up number 001–025 (use it as `NNN` in the file name) |
| batch | A = 001–009 (T13), B = 010–017 (T14), C = 018–025 (T15) |
| merged_ids | Longlist IDs folded into this idea (see rejected.md, "T12 merges") |
| path | Empty; each write-up task fills in its file path |

## How T12 cut and picked (2026-10-29)
- **Merges:** 16 near-duplicates folded into the kept idea; **drops:** 3 ideas outside the profile or unrealistic (I185, I177, I037). Both are in rejected.md.
- **Cut:** the remaining 189 ideas were scored; ideas with a rounded weighted score ≥ 2.4 stay (108). The other 81 are in rejected.md with their scores.
- **Scores are low.** No idea reaches 3.5. Lens 6 (pain) is the weak spot almost everywhere because Reddit, Facebook groups and review sites could not be read (see the lens 6 Gaps). The best idea scores 3.4 (I010); most of the shortlist sits at `<5%` or `5–15%`.
- **Top 25 for write-up:** taken in rank order with at most 3 ideas per field. That rule skipped I023, I011, I013 (accounting), I070 (developer tools) and I028, I029 (legal). For the last place, I122 (healthcare-admin, rank 38) was taken instead of I080 (a third accounting-office agent in ai-agents-automation, rank 31), so that one more field is covered (13 of 22 fields in all). Numbering 001–025 follows rank.
- Write-ups should re-check every score with ≥5 sources. A score may go up or down; if an idea collapses, swap in the next `write_up=n` idea in rank order (see each write-up task).
