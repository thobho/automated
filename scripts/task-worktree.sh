#!/usr/bin/env bash
# Give one task its own isolated working copy, so tasks running in parallel never share a folder or branch.
# Usage: scripts/task-worktree.sh <issue> <slug>     prints the folder to work in
#        scripts/task-worktree.sh --remove <issue>   removes it after the PR is merged
# Folder: $AUTOMATED_WORK_DIR (default: ../automated-work next to the main checkout)/issue-<issue>
# Branch: agent/<issue>-<slug>, created from origin/main, or reused if it already exists.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
root="$(cd "$(git -C "$here" rev-parse --git-common-dir)/.." && pwd)"   # the main checkout, even when run from a worktree
work="${AUTOMATED_WORK_DIR:-$(dirname "$root")/automated-work}"

if [[ "${1:-}" == "--remove" ]]; then
  issue="${2:?issue number}"
  git -C "$root" worktree remove --force "$work/issue-$issue"
  echo "removed $work/issue-$issue"; exit 0
fi

issue="${1:?issue number}"; slug="${2:?slug}"
branch="agent/$issue-$slug"; path="$work/issue-$issue"

if [[ -d "$path" ]]; then echo "$path"; exit 0; fi   # reuse a working copy that already exists
mkdir -p "$work"
git -C "$root" fetch -q origin main
if git -C "$root" show-ref -q --verify "refs/heads/$branch"; then
  git -C "$root" worktree add -q "$path" "$branch"
elif git -C "$root" ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  git -C "$root" fetch -q origin "$branch"
  git -C "$root" worktree add -q -b "$branch" "$path" "origin/$branch"
else
  git -C "$root" worktree add -q -b "$branch" "$path" origin/main
fi
echo "$path"
