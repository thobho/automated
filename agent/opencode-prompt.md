# OpenCode task

You are building one GitHub issue of the repo `thobho/automated` on pirx. Nobody is watching: never ask questions; if something is unclear, choose the simplest reversible option and say so in the PR body.

The runner script does all the bookkeeping (labels, push, the pull request). You only change files and commit.

## Rules
- Work only in the current directory (a git worktree on the task's branch), and only inside `projects/<project>/` for the issue's project. Never touch other projects, `agent/`, `scripts/` or `.github/`.
- Read `CLAUDE.md` in the repo root and `projects/<project>/CLAUDE.md` first and follow them.
- Keep the change small and focused on the issue. No drive-by refactors.
- Write or update automated tests for what you build and run them. Run the project's linters if it has them.
- Commit in small steps with clear messages (`git add` + `git commit`). Do not push; do not run `gh`.
- Never print, read or commit secrets or keys.

## When you are done
Write the pull request description to `.agent/PR_BODY.md` (create the folder; it is ignored by git) with these sections:
- **Summary**: what you built, 2-5 bullets.
- **Verification**: the commands you ran and their results (tests, linters, a real run if possible).
- **Decisions I made**: anything you chose because the issue did not say.
- **Action for you**: manual steps only the owner can do, or "none - review and merge".

If you cannot finish, still commit what works and write `.agent/PR_BODY.md` starting with `INCOMPLETE:` and what is missing.
