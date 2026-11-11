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
label "priority:low"  "C2E0C6" "Agent picks these last"
label "model:haiku"   "E4E669" "Build with Haiku (small, cheap tasks)"
label "model:sonnet"  "F9D0C4" "Build with Sonnet (default)"
label "model:opus"    "7057FF" "Build with Opus (hard tasks, uses limits fastest)"
label "model:pirx"    "C5DEF5" "Build with OpenCode on pirx (simple tasks, OpenRouter budget)"
label "area:security" "B60205" "Security-sensitive: never built by OpenCode, reviewed with Opus"
label "risk:low"      "D4C5F9" "Low-risk change: may auto-merge after green CI and AI review (from M1)"
label "owner:todo"    "FEF2C0" "A task for the owner (listed in the daily report)"
label "agent:report"  "C2E0C6" "The daily report issue (one comment per day)"
