#!/usr/bin/env bash
# Queue a task for the agent.
# Usage: scripts/new-task.sh -p <project> -t "<title>" [-b "<body>"] [-m haiku|sonnet|opus] [-d "#12, #14"] [--high|--low]
set -euo pipefail
cd "$(dirname "$0")/.."

project="" title="" body="" priority="" model="sonnet" deps=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) project="$2"; shift 2 ;;
    -m) model="$2"; shift 2 ;;
    -d) deps="$2"; shift 2 ;;
    --low) priority=low; shift ;;
    -t) title="$2"; shift 2 ;;
    -b) body="$2"; shift 2 ;;
    --high) priority=high; shift ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done
[[ -n "$project" && -n "$title" ]] || { echo "usage: $0 -p <project> -t <title> [-b <body>] [-m haiku|sonnet|opus] [-d \"#12, #14\"] [--high|--low]" >&2; exit 1; }
[[ "$model" =~ ^(haiku|sonnet|opus)$ ]] || { echo "model must be haiku, sonnet or opus" >&2; exit 1; }

gh label create "project:$project" --color "C5DEF5" --description "Lives in projects/$project" >/dev/null 2>&1 || true

labels="agent:todo,project:$project,model:$model"
[[ -n "$priority" ]] && labels="$labels,priority:$priority"
[[ -n "$deps" ]] && deps="Depends on: $deps
"

gh issue create --title "$title" --label "$labels" --body "**Project:** \`$project\`
$deps
$body"
