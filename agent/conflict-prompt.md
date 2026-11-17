# Resolve a merge conflict in one pull request

The current directory is a checkout of a PR branch of `thobho/automated` in the middle of `git merge origin/main`, stopped with conflicts. Another agent built the PR, and an AI reviewer will review your result. Nobody is watching: never ask questions.

## Do
1. Look at what each side wanted: `git log --oneline origin/main -10`, `git diff --name-only --diff-filter=U`, the conflicted files, `gh pr view <pr>`, and the commits on `main` that touched those files (`git log -p origin/main -3 -- <file>`).
2. Resolve every conflict so that **both sides' intent survives**. Typical cases: both added entries to a list, section or settings → keep both; one side renamed or moved code the other changed → apply the change at the new place; lock files (`uv.lock`, `package-lock.json`) → take main's version, then regenerate (`uv lock`, `npm install --package-lock-only`).
3. Run the checks of each project the conflicted files belong to (for `projects/<name>/`: its tests and lint from its README or Makefile, for example `uv run pytest` and `uv run ruff check`). Fix what the merge broke, nothing else.
4. `git add` the resolved files and commit the merge with `git commit --no-edit`. Do not push: the runner checks and pushes your commit.

## Don't
- Don't rewrite history (no rebase, no reset of commits, no amend of earlier commits) and don't switch branches.
- Don't make changes unrelated to the conflict, and don't change behaviour beyond what both sides already had.
- If a conflict cannot be resolved without a product decision, leave the merge uncommitted (`git merge --abort`) and say why in your final reply.

End with a short reply: the files you resolved, how, and the checks you ran with their result.
