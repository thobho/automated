#!/usr/bin/env bash
# Owner-side runner for the sudo request queue (see docs in scripts/SUDO-QUEUE.md).
#
# The unprivileged `agent` user writes <id>.sh (+ <id>.md: what and why) into
#   ~agent/runtime/automated/sudo-queue/pending/
# You review each one here; only a script you approve is run, as root.
#
#   sudo scripts/owner-apply.sh                      review and run pending requests, one by one (needs a terminal)
#   sudo scripts/owner-apply.sh --list               only list them, each with its sha256
#   sudo automated-owner-apply --approve <id> <sha256>   run that one request, only if its content still has
#                                                        exactly that sha256 (what you saw in --list)
#   sudo automated-owner-apply --reject <id>             reject that one request
# The installed root-owned copy /usr/local/sbin/automated-owner-apply may be run by the owner without a
# password (agent/pirx/root/install-root-helper.sh), so the owner approves from the Claude session on pirx:
# Claude shows --list, the owner says "approve <id>", Claude runs --approve with the sha it showed.
#
# Safety: the script is copied to a root-owned temp dir BEFORE you see it, and the copy is
# what runs, so the agent cannot change it between your review and the run. Results go to a
# root-owned state dir (world-readable) that the agent reads on its next run.
#
# Env (mainly for tests): AUTOMATED_AGENT_USER (default agent), SUDO_QUEUE_DIR, SUDO_STATE_DIR,
# OWNER_APPLY_ANSWER (non-interactive answer, tests only), OWNER_APPLY_TEST=1 (allow non-root).
set -uo pipefail

AGENT_USER=${AUTOMATED_AGENT_USER:-agent}
AGENT_HOME=$(getent passwd "$AGENT_USER" | cut -d: -f6 || true)
QUEUE=${SUDO_QUEUE_DIR:-${AGENT_HOME:-/home/$AGENT_USER}/runtime/automated/sudo-queue}
STATE=${SUDO_STATE_DIR:-/var/lib/automated-sudo}
LIST_ONLY=0; ONLY_ID=""; WANT_SHA=""; FORCED=""
case ${1:-} in
  --list) LIST_ONLY=1 ;;
  --approve) ONLY_ID=${2:-}; WANT_SHA=${3:-}; FORCED=y
             [[ -n $ONLY_ID && $WANT_SHA =~ ^[0-9a-f]{64}$ ]] || { echo "usage: --approve <id> <sha256 from --list>" >&2; exit 1; } ;;
  --reject) ONLY_ID=${2:-}; FORCED=n; [[ -n $ONLY_ID ]] || { echo "usage: --reject <id>" >&2; exit 1; } ;;
  "") ;;
  *) echo "usage: owner-apply.sh [--list | --approve <id> <sha256> | --reject <id>]" >&2; exit 1 ;;
esac

die() { echo "owner-apply: $*" >&2; exit 1; }

if [[ $EUID -ne 0 && ${OWNER_APPLY_TEST:-} != 1 ]]; then
  die "run as root: sudo $0"
fi
# Interactive mode reads answers from the terminal; without one (e.g. from a Claude session) an empty answer
# would reject everything, so refuse instead.
if [[ $LIST_ONLY == 0 && -z $FORCED && -z ${OWNER_APPLY_ANSWER:-} ]] && ! { : < /dev/tty; } 2>/dev/null; then
  die "no terminal: use --list, then --approve <id> <sha256> or --reject <id>"
fi
[[ -d $QUEUE/pending && ! -L $QUEUE/pending && ! -L $QUEUE ]] || { echo "Nothing pending ($QUEUE/pending does not exist)."; exit 0; }

mkdir -p "$STATE/done" "$STATE/rejected"
chmod 755 "$STATE" "$STATE/done" "$STATE/rejected"
log() { printf '%s %s\n' "$(date -Is)" "$*" >> "$STATE/apply.log"; }

work=$(mktemp -d); chmod 700 "$work"; trap 'rm -rf "$work"' EXIT

shopt -s nullglob
requests=("$QUEUE"/pending/*.sh)
[[ ${#requests[@]} -gt 0 ]] || { echo "Nothing pending."; exit 0; }

applied=0; refused=0; skipped=0
for src in "${requests[@]}"; do
  id=$(basename "$src" .sh)
  [[ -n $ONLY_ID && $id != "$ONLY_ID" ]] && continue
  if [[ ! $id =~ ^[a-z0-9][a-z0-9._-]{0,63}$ ]]; then echo "SKIP $id: bad id"; skipped=$((skipped + 1)); continue; fi
  if [[ -L $src || ! -f $src ]]; then echo "SKIP $id: not a regular file"; skipped=$((skipped + 1)); continue; fi
  if [[ $(stat -c %U "$src") != "$AGENT_USER" ]]; then echo "SKIP $id: not owned by $AGENT_USER"; skipped=$((skipped + 1)); continue; fi
  if [[ -e $STATE/done/$id.sh || -e $STATE/rejected/$id.sh ]]; then echo "SKIP $id: id already used (pick a new one)"; skipped=$((skipped + 1)); continue; fi

  # Snapshot first: everything below uses the copy, never the agent-writable original.
  copy=$work/$id.sh; note=$work/$id.md
  cp -- "$src" "$copy"; chmod 700 "$copy"
  if [[ -f $QUEUE/pending/$id.md && ! -L $QUEUE/pending/$id.md ]]; then cp -- "$QUEUE/pending/$id.md" "$note"; else echo "(no description given)" > "$note"; fi
  sum=$(sha256sum "$copy" | cut -d' ' -f1)

  echo; echo "================ request: $id ================"
  echo "sha256: $sum"; echo "---- why ----"; cat "$note"; echo "---- script ----"; cat -v "$copy"; echo "---- end ----"
  [[ $LIST_ONLY == 1 ]] && continue

  if [[ $FORCED == y && $sum != "$WANT_SHA" ]]; then
    echo "=> NOT run: the request's content has sha256 $sum, not the $WANT_SHA you approved. Run --list again."
    log "approve $id refused: sha mismatch"; skipped=$((skipped + 1)); continue
  fi
  if [[ -n $FORCED ]]; then ans=$FORCED
  elif [[ -n ${OWNER_APPLY_ANSWER:-} ]]; then ans=$OWNER_APPLY_ANSWER
  else read -r -p "Run as root? [y/N/s=skip] " ans < /dev/tty; fi
  case ${ans,,} in
    y|yes)
      log "approve $id sha256=$sum"
      bash "$copy" > "$work/$id.out" 2>&1; rc=$?
      cat "$work/$id.out"
      cp "$copy" "$STATE/done/$id.sh"; cp "$note" "$STATE/done/$id.md"; cp "$work/$id.out" "$STATE/done/$id.out"
      printf 'exit=%s\nsha256=%s\nat=%s\n' "$rc" "$sum" "$(date -Is)" > "$STATE/done/$id.status"
      chmod 644 "$STATE/done/$id".*
      rm -f -- "$QUEUE/pending/$id.sh" "$QUEUE/pending/$id.md"
      log "ran $id exit=$rc"; echo "=> exit $rc, result saved in $STATE/done/$id.*"; applied=$((applied + 1)) ;;
    s|skip) echo "=> left pending"; skipped=$((skipped + 1)) ;;
    *)
      cp "$copy" "$STATE/rejected/$id.sh"; cp "$note" "$STATE/rejected/$id.md"; chmod 644 "$STATE/rejected/$id".*
      rm -f -- "$QUEUE/pending/$id.sh" "$QUEUE/pending/$id.md"
      log "reject $id sha256=$sum"; echo "=> rejected"; refused=$((refused + 1)) ;;
  esac
done
[[ -n $ONLY_ID && $((applied + refused + skipped)) -eq 0 ]] && { echo "No pending request with id $ONLY_ID."; exit 1; }
echo; echo "Done: $applied run, $refused rejected, $skipped left."
