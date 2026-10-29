# T01 — setup and method

**Model:** opus · **Needs:** —

Read `projects/idea-generator/BRIEF.md` first and follow its Rules. Commit and push often (see Rules). Run the link check on changed files before marking the task done.

Set up the rest of `projects/idea-generator/` (see the Folder layout in BRIEF.md). BRIEF.md, PROGRESS.md, RUNNER.md and tasks/ already exist.

1. (done: BRIEF.md exists)
2. README.md, CLAUDE.md (points agents to BRIEF.md; research verification = link check, no CI), empty CHANGELOG.md and rejected.md.
3. `method/criteria.md`: for each lens a 1–5 rubric (what 1, 3 and 5 mean), the weights (change them only with a stated reason), how the weighted score maps to chance bands, and a starting list of sources per lens.
4. `tools/check_links.py`: stdlib only. It finds URLs in the given markdown/csv files, fetches each (HEAD, falling back to GET, 10 s timeout, browser-like User-Agent), and reports **dead** (404/410, DNS failure) and **unverifiable** (403/429/timeouts) links. Exit 1 only if there are dead links. Add a test with a local http.server.

**Done when:** the folder exists as described, `python3 -m unittest` passes in tools/, and the checker runs on criteria.md.
