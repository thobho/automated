#!/usr/bin/env bash
# Print the agent queue grouped by state, in the order the worker picks tasks.
set -euo pipefail
cd "$(dirname "$0")/.."

for state in doing blocked todo review; do
  echo "== agent:$state =="
  gh issue list --label "agent:$state" --state open --limit 50 \
    --json number,title,labels,createdAt \
    --jq 'sort_by([(.labels|map(.name)|index("priority:high")|not), .createdAt])[]
          | "#\(.number)  \(.title)  [\(.labels|map(.name)|map(select(startswith("project:") or .=="priority:high"))|join(", "))]"'
done
