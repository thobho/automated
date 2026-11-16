#!/usr/bin/env bash
# Agent side of the sudo request queue: queue a script that needs root, for the owner to review.
# Usage: scripts/sudo-request.sh <id> <script-file> "<why: what it does and which task needs it>"
# The id is lowercase letters, digits, . _ - (e.g. t09-firewall-ct-rule) and can be used only once.
# This does NOT run anything. The owner runs `sudo scripts/owner-apply.sh`; the result appears in
# /var/lib/automated-sudo/done/<id>.{out,status} (or rejected/<id>.*).
# Request format is plain files, so `mkdir/cp` into the queue dir works too if this script is not allowed.
set -euo pipefail

id=${1:?usage: sudo-request.sh <id> <script-file> "<why>"}
script=${2:?missing script file}
why=${3:?missing explanation}
[[ $id =~ ^[a-z0-9][a-z0-9._-]{0,63}$ ]] || { echo "bad id: $id" >&2; exit 1; }
[[ -f $script ]] || { echo "no such file: $script" >&2; exit 1; }

queue=${SUDO_QUEUE_DIR:-$HOME/runtime/automated/sudo-queue}
state=${SUDO_STATE_DIR:-/var/lib/automated-sudo}
for d in done rejected; do
  [[ -e $state/$d/$id.sh ]] && { echo "id $id was already used ($state/$d)" >&2; exit 1; }
done
[[ -e $queue/pending/$id.sh ]] && { echo "id $id is already pending" >&2; exit 1; }

mkdir -p "$queue/pending"
cp -- "$script" "$queue/pending/$id.sh"
printf '%s\n' "$why" > "$queue/pending/$id.md"
echo "queued $id. Next: label the issue agent:blocked and ask the owner to run: sudo scripts/owner-apply.sh"
