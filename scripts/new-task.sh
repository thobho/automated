#!/usr/bin/env bash
# Queue a task for the agent.
# Usage: scripts/new-task.sh -p <project> -t "<title>" [-b "<body>"] [--high]
set -euo pipefail
cd "$(dirname "$0")/.."

project="" title="" body="" high=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) project="$2"; shift 2 ;;
    -t) title="$2"; shift 2 ;;
    -b) body="$2"; shift 2 ;;
    --high) high=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done
[[ -n "$project" && -n "$title" ]] || { echo "usage: $0 -p <project> -t <title> [-b <body>] [--high]" >&2; exit 1; }

gh label create "project:$project" --color "C5DEF5" --description "Lives in projects/$project" >/dev/null 2>&1 || true

labels="agent:todo,project:$project"
[[ -n "$high" ]] && labels="$labels,priority:high"

gh issue create --title "$title" --label "$labels" --body "**Project:** \`$project\`

$body"
