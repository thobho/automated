#!/usr/bin/env bash
# Create (or update) the labels the worker uses. Safe to run again.
set -euo pipefail
cd "$(dirname "$0")/.."

label() { gh label create "$1" --color "$2" --description "$3" --force >/dev/null && echo "label: $1"; }

label "agent:todo"    "0E8A16" "Queued for the agent"
label "agent:doing"   "FBCA04" "Agent is working on it"
label "agent:review"  "1D76DB" "Agent opened a PR, waiting for your review"
label "agent:blocked" "D93F0B" "Agent needs an answer from you (see comments)"
label "agent:done"    "5319E7" "Finished"
label "agent:status"  "BFDADC" "The pinned status dashboard issue"
label "priority:high" "B60205" "Agent picks these first"
