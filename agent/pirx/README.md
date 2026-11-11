# Agent runners on pirx

pirx (the always-on Linux box) builds the queue. Everything runs as the unprivileged **`agent`** user, created once with `setup-agent-user.sh` (sudo): no sudo, no access to `/home/user`, Hermes or the home LAN, memory and CPU caps, its own GitHub token (only `thobho/automated`), its own Claude login and its own OpenRouter key.

## Who runs what
| Piece | Where | Trigger | Budget |
|---|---|---|---|
| `automated-dispatcher` (scheduled task, `agent/scheduled-task.md`) | Mac desktop app | hourly at :07 | reads the plan limits, then one SSH call |
| `start-claude-run.sh` | pirx, `agent` | the dispatcher | Claude plan gate (`agent/budget.py`), memory gate, slot, task, Opus headroom |
| `claude-run.sh` | pirx, `agent` (systemd-run, ≤3 h) | `start-claude-run.sh` | one issue; Claude Code sandbox (`claude-settings.json`) |
| `opencode-worker.sh` | pirx, `agent` (timer `automated-opencode`) | hourly at :17 | OpenRouter gate (`agent/openrouter_budget.py`), per-task spend watchdog |
| `daily_report.py` | pirx, `agent` (timer `automated-report`) | 07:45 Warsaw | posts a comment on the "📋 Daily report" issue |
| `report-send.sh` | pirx, **owner's user** (timer `automated-report-send`) | 08:00 Warsaw | sends the WhatsApp part through Hermes (`hermes send`, no AI) |

The agent never talks to Hermes: the report goes through GitHub, and the owner's user forwards it.

## Isolation, in layers
1. **The `agent` user**: unprivileged, `/home/user` unreadable, LAN and tailnet blocked by nftables, caps in `user-<uid>.slice`.
2. **Claude Code sandbox** (bubblewrap): shell commands write only in the working copy and caches, and reach only GitHub and PyPI; file edits are auto-accepted in the working copy, anything needing a prompt is refused.
3. **OpenCode** (`opencode.json`): may not push, run `gh`, leave the working copy or read keys; the runner script pushes and opens the PR.
4. **GitHub**: the token reaches only `thobho/automated`; branch protection on `main` keeps agents to PRs.

## Install / update (as `agent`, from the Mac)
```
ssh agent@192.168.68.62 'gh repo clone thobho/automated ~/Projects/automated -- -q 2>/dev/null; bash ~/Projects/automated/agent/pirx/setup.sh'
```
Owner's side of the report (as `user`, once):
```
install -m 755 agent/pirx/report-send.sh ~/.local/bin/automated-report-send.sh
install -m 644 agent/pirx/systemd/automated-report-send.* ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now automated-report-send.timer
```

## Settings
`~/.config/automated/pirx.env` (agent): `PIRX_SLOTS` (1 now, 2 after the RAM upgrade), `PIRX_MIN_FREE_MB`, `OPENCODE_MODEL`, `OPENCODE_TIMEOUT_MIN`, `CLAUDE_MAX_RUN_H`, `AUTOMATED_RUNNER_REF`. After the RAM upgrade also raise `MEM_HIGH`/`MEM_MAX` by re-running `setup-agent-user.sh` with them set.

Logs: `~agent/runtime/automated/logs/` (`runner.log`, one file per run).
