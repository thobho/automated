---
name: model-orchestrator
description: Cost-optimized multi-model playbook for building a feature or fix. Planning goes to DeepSeek-R1 and code drafting to Qwen 2.5 Coder 32B (both via OpenRouter), checks run on local CLI tools at zero LLM cost, and Claude does the final adversarial review. Use when the user asks for multi-model orchestration, a generator-critic or planner-coder-reviewer workflow, cheap-model drafting with Claude review, "save API costs" on a coding task, or calls /model-orchestrator.
---

# Model orchestrator

The point is to spend Claude tokens only where Claude adds the most: judging the result. Cheap models do the bulk token work (planning prose, full-file drafts), and deterministic tools catch everything they can catch for free.

Claude Code cannot switch its own session model from inside a skill (`/model` is a user command, and OpenRouter models are not session models). So you, Claude, stay the orchestrator and reviewer, and call the cheap models through `scripts/openrouter.py`. Keep your own work light during phases 1–3: pick context files, run commands, read short outputs. Don't rewrite the cheap models' code yourself unless the fix loop stalls — that is what spends the money.

Paths below: `S` = this skill's directory. Work from the repo root. Scratch files live in `.claude/tmp/` (create it; make sure it's git-ignored or at least not committed).

The script reads `OPENROUTER_API_KEY` from the env or `~/.config/automated/secrets.env`. Never print the key. Models can be overridden with `ORCH_PLANNER_MODEL` / `ORCH_CODER_MODEL`. It prints tokens and cost per call to stderr — keep a running total for the final summary.

## Phase 1 — Plan (DeepSeek-R1)

1. Find the files relevant to the request (grep/ls; keep it to what the planner really needs — every file is input tokens).
2. Write the user's request, plus any repo rules that matter (e.g. from CLAUDE.md), to `.claude/tmp/task-plan.txt`.
3. Run:
   `python3 S/scripts/openrouter.py --role planner --task .claude/tmp/task-plan.txt --context <files> --out .claude/tmp/plan.md`
4. Read `plan.md`. If it names files you didn't pass, or is clearly off, re-run with better context rather than patching it yourself.
5. Give the user a short summary of the plan (objectives, files, tests) before Phase 2. If the plan makes a real design choice the user might disagree with, ask; otherwise continue.

## Phase 2 — Draft code (Qwen 2.5 Coder)

1. Write `.claude/tmp/task-code.txt`: "Implement this plan:" followed by `plan.md`'s content.
2. Run with every file the plan touches as context (new files too — the script marks them as not existing):
   `python3 S/scripts/openrouter.py --role coder --task .claude/tmp/task-code.txt --context <files> --out .claude/tmp/draft.txt --apply`
   `--apply` writes each returned file in full and lists them. If it reports no FILE blocks, look at `draft.txt` and retry once with a firmer instruction.
3. Glance at `git diff --stat` to confirm only expected files changed. Revert anything outside the plan's scope.

## Phase 3 — Deterministic checks (no LLM)

Run whatever the project actually uses (check its README, CLAUDE.md, package.json, pyproject, Makefile, CI config first):
- Python: `pytest`, `ruff check .`, `mypy .`
- JS/TS: `npm test`, `npm run lint`, `npx tsc --noEmit`
- Go / Rust: `go test ./...`, `cargo test`

Skip tools the project doesn't have configured rather than introducing them.

On failure: write `.claude/tmp/task-fix.txt` with "Fix these errors without changing behaviour beyond what's needed:" plus the trimmed error output (the relevant tracebacks/lines, not 2000 lines of log), then call the coder again with `--apply` and the failing files as context. Re-run the checks.

Do not move on until everything passes. If the same failure survives 3 fix rounds, stop looping: either fix it yourself (say so in the summary) or ask the user — burning more rounds rarely helps.

## Phase 4 — Adversarial review (Claude)

You do this yourself; it's the expensive step and the one that matters. Read `git diff` and `plan.md` and actively look for reasons to reject:
- Does the diff do everything in the plan's acceptance criteria — and nothing unrequested?
- Logic errors, off-by-ones, unhandled empty/None/error cases, broken existing behaviour.
- Security: injection, path traversal, secrets in code or logs, unsafe deserialization.
- Fit with the codebase: naming, structure, idiom, tests that actually assert something.

**PASS** → tell the user what was built, files changed, check results, and the OpenRouter cost total; delete `.claude/tmp/plan.md`, `critique.md` and the task/draft files; ask whether to commit (don't commit unasked).

**FAIL** → write concrete, file-and-line feedback to `.claude/tmp/critique.md`, send it to the coder (task file = critique + plan, context = affected files, `--apply`), then repeat Phase 3 and Phase 4. After 2 failed reviews, fix the remaining issues yourself or hand the decision to the user.
