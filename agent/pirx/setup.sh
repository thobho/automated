#!/usr/bin/env bash
# Set up (or update) the agent runners on pirx. Run as the `agent` user, safe to repeat, no sudo:
#   bash agent/pirx/setup.sh
#   AUTOMATED_RUNNER_REF=origin/<branch> bash agent/pirx/setup.sh     to test a branch
# What it does:
#   - clones thobho/automated to ~/Projects/automated if missing (the agent's own shared checkout);
#   - a runner worktree (~/Projects/automated-work/runner) pinned to RUNNER_REF, so the tooling never
#     depends on which branch the shared checkout is on;
#   - the slot lock in ~/.config/automated/ with PIRX_SLOTS slots (1 while pirx has 4 GB, 2 after the upgrade);
#   - ~/.config/automated/pirx.env with defaults (kept if it exists);
#   - systemd user timers: OpenCode worker (hourly at :17) and the daily report (07:45 Warsaw).
# The owner's side (sending the report via Hermes) is installed separately, see agent/pirx/README.md.
set -euo pipefail
source "$(dirname "$0")/common.sh"

for tool in git gh python3 jq curl claude opencode bwrap socat; do
  command -v "$tool" >/dev/null || { echo "missing: $tool"; exit 1; }
done

if [[ ! -d "$REPO_ROOT/.git" ]]; then
  mkdir -p "$(dirname "$REPO_ROOT")"
  gh repo clone "$GH_REPO" "$REPO_ROOT" -- -q
fi
grep -qx '.agent/' "$REPO_ROOT/.git/info/exclude" 2>/dev/null || echo '.agent/' >> "$REPO_ROOT/.git/info/exclude"

mkdir -p "$CONF_DIR/state" "$(dirname "$RUNNER_DIR")"
chmod 700 "$CONF_DIR"
if [[ ! -f "$CONF_DIR/pirx.env" ]]; then
  cat > "$CONF_DIR/pirx.env" <<'EOF'
# Agent runner settings for pirx (not in git).
PIRX_SLOTS=1                 # 1 while pirx has 4 GB RAM; 2 after the upgrade
PIRX_MIN_FREE_MB=1000        # a run starts only with this much MemAvailable
OPENCODE_MODEL=openrouter/deepseek/deepseek-v4.1-flash-1017
OPENCODE_TIMEOUT_MIN=40
CLAUDE_MAX_RUN_H=3
EOF
  echo "wrote $CONF_DIR/pirx.env"
fi
source "$CONF_DIR/pirx.env"
echo "${PIRX_SLOTS:-1}" > "$CONF_DIR/state/slots.conf"

git -C "$REPO_ROOT" fetch -q origin
if [[ ! -d "$RUNNER_DIR" ]]; then
  git -C "$REPO_ROOT" worktree add -q --detach "$RUNNER_DIR" "$RUNNER_REF"
else
  git -C "$RUNNER_DIR" checkout -q --detach "$RUNNER_REF"
fi
install -m 755 "$RUNNER_DIR/scripts/worker-lock.sh" "$LOCK"
# The ref is remembered in pirx.env so later updates (start-claude-run.sh) stay on it.
sed -i '/^AUTOMATED_RUNNER_REF=/d' "$CONF_DIR/pirx.env"
echo "AUTOMATED_RUNNER_REF=$RUNNER_REF" >> "$CONF_DIR/pirx.env"

units="$HOME/.config/systemd/user"
mkdir -p "$units"
for u in automated-opencode.service automated-opencode.timer automated-report.service automated-report.timer; do
  install -m 644 "$RUNNER_DIR/agent/pirx/systemd/$u" "$units/"
done
systemctl --user daemon-reload
systemctl --user enable --now automated-opencode.timer automated-report.timer >/dev/null 2>&1

echo "runner: $RUNNER_DIR at $(git -C "$RUNNER_DIR" rev-parse --short HEAD) ($RUNNER_REF)"
echo "slots: $(cat "$CONF_DIR/state/slots.conf"); memory available: $(free_mb) MB (gate $PIRX_MIN_FREE_MB MB)"
[[ -s "$CONF_DIR/openrouter-opencode.key" ]] && echo "OpenCode key: present" || echo "OpenCode key: MISSING"
systemctl --user list-timers 'automated-*' --no-pager | head -4
