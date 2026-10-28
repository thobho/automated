#!/usr/bin/env bash
# Print the agent queue in the order the worker picks tasks, with what each waits on.
set -euo pipefail
cd "$(dirname "$0")/.."
exec agent/pick_task.py "$@"
