#!/usr/bin/env bash
# Queue a task for the agent.
# Usage: scripts/new-task.sh -p <project> -t "<title>" [-b "<body>"] [-m haiku|sonnet|opus] [--high]
set -euo pipefail
cd "$(dirname "$0")/.."

project="" title="" body="" high="" model="sonnet"
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) project="$2"; shift 2 ;;
    -m) model="$2"; shift 2 ;;
    -t) title="$2"; shift 2 ;;
    -b) body="$2"; shift 2 ;;
    --high) high=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done
[[ -n "$project" && -n "$title" ]] || { echo "usage: $0 -p <project> -t <title> [-b <body>] [-m haiku|sonnet|opus] [--high]" >&2; exit 1; }
[[ "$model" =~ ^(haiku|sonnet|opus)$ ]] || { echo "model must be haiku, sonnet or opus" >&2; exit 1; }

gh label create "project:$project" --color "C5DEF5" --description "Lives in projects/$project" >/dev/null 2>&1 || true

labels="agent:todo,project:$project,model:$model"
[[ -n "$high" ]] && labels="$labels,priority:high"

gh issue create --title "$title" --label "$labels" --body "**Project:** \`$project\`

$body"
