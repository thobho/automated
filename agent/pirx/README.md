# Agent runners on pirx

pirx (the always-on Linux box) builds the queue and heals itself; the owner hears from it only when money is needed. Everything runs as the **`agent`** user, created once with `setup-agent-user.sh` (sudo): no sudo except the root helper's fixed verbs, no access to `/home/user`, Hermes or the home LAN, memory and CPU caps, its own GitHub token (only `thobho/automated`), its own Claude login and its own OpenRouter key.

Design principles (why it is a pipeline with checks, not a swarm, and the rules for changing it): [`agent/DESIGN.md`](../DESIGN.md).

## Who runs what
| Piece | Where | Trigger | Budget |
|---|---|---|---|
| `dispatch.sh` (timer `automated-dispatch`) | pirx, `agent` | hourly at :07 | reads the plan limits (`agent/usage_probe.py`), then `start-claude-run.sh` |
| `start-claude-run.sh` | pirx, `agent` | the dispatcher | Claude plan gate (`agent/budget.py`), memory gate, slot, task, Opus headroom |
| `claude-run.sh` | pirx, `agent` (systemd-run, ≤3 h) | `start-claude-run.sh` | one issue; command allowlist (`claude-settings.json`) |
| `opencode-worker.sh` | pirx, `agent` (timer `automated-opencode`) | hourly at :17 | OpenRouter gate (`agent/openrouter_budget.py`), per-task spend watchdog |
| `review-run.sh` | pirx, `agent` (systemd-run, ≤1 h) | `start-claude-run.sh`, before any build | AI review on another model; merges approved PRs, protected ones wait for the owner |
| `conflict-run.sh` | pirx, `agent` (systemd-run, ≤1 h) | `start-claude-run.sh`, before reviews | merges `main` into a conflicting PR; Claude resolves with wide permissions in the agent account (`conflict-settings.json`; its push deny is soft, the script's checks before its own push are the guarantee); 2 failed attempts in a row (Sonnet, then Opus), then blocked |
| `planner-run.sh` | pirx, `agent` (systemd-run, ≤1 h) | `start-claude-run.sh`, when nothing is ready | Turns unplanned stories of `projects/<project>/ROADMAP.md` into issues (`agent/planner.py` decides: fewer than 2 queued tasks, 6 h cooldown, at most 4 stories, earliest milestone first). Creates issues only (`planner-settings.json`: no edits, pushes or PRs); no roadmap → one `owner:todo` issue asks for it. Opus if it has plan headroom, else Sonnet |
| `retro-run.sh` (timer `automated-retro`) | pirx, `agent` | Monday 05:30 Warsaw | Claude plan gate; `agent/retro.py` collects the week's review findings (no model); with 2 or more, Sonnet turns repeated ones into rules in `projects/<p>/CLAUDE.md` (`retro-settings.json`: only those files; it only proposes worker-prompt rules); only comments by the automation's own account count, and output that looks like a credential is discarded; the script commits and opens an `agent-setup/retro-<date>` PR for the AI review |
| `daily_report.py` | pirx, `agent` (timer `automated-report`) | 07:45 Warsaw | posts a comment on the "📋 Daily report" issue |
| `heal.sh` (timer `automated-heal`) | pirx, `agent` | :20 and :50, and when another unit fails | fixed fixes, no model: units and timers, stuck tasks, worktrees, disk, health page, the owner's services and the firewall (root helper), OpenRouter keys near their limit → `owner:money` |
| `heal-diagnose.sh` | pirx, `agent` (systemd-run, ≤1 h) | `heal.sh`, when a problem survives 3 runs (once per 6 h each) | Claude plan gate; Sonnet with wide permissions in the agent account (`heal-settings.json`) and the root helper; posts its report on the health issue |
| `root/automated-root` | pirx, root, via `sudo -n` | `heal.sh`, `heal-diagnose.sh` | fixed verbs only; lists in `/etc/automated/root-helper.conf`; phone-farm never listed. Installed by the owner: `sudo bash agent/pirx/root/install-root-helper.sh` |
| `owner/money-notify.sh` | pirx, **owner's user** (timer `automated-money-notify`) | every 15 min | sends each open `owner:money` issue once to WhatsApp through Hermes (no AI). The only alert to the owner |
| `report-send.sh` | retired | | the daily report stays on GitHub; `owner/install.sh` disables its timer |

The agent never talks to Hermes: the report goes through GitHub, and the owner's user forwards it.

## Isolation, in layers
1. **The `agent` user**: unprivileged, `/home/user` unreadable, LAN and tailnet blocked by nftables, caps in `user-<uid>.slice`.
2. **Claude Code allowlist** (`claude-settings.json`, `dontAsk` mode): file edits only in the working copy, only listed shell commands, everything else refused. (Claude Code's OS sandbox can't start on Ubuntu 26.04 without relaxing its user-namespace restriction; the owner chose the allowlist.)
5. **AI review**: every agent PR is reviewed by a separate run on another model; it merges only on approval with green CI. Automation PRs are reviewed by Opus only; those that touch money or permission rules (`review_queue.GUARDED`) wait for the owner's one-tap merge, and spending-rule changes also open an `owner:money` alert.
6. **Root helper** (`root/`): the agent's only root access, a root-owned script with fixed verbs; the agent cannot change it.
3. **OpenCode** (`opencode.json`): may not push, run `gh`, leave the working copy or read keys; the runner script pushes and opens the PR.
4. **GitHub**: the token reaches only `thobho/automated`; branch protection on `main` keeps agents to PRs.

## Install / update (as `agent`, from the Mac)
```
ssh agent@192.168.68.62 'gh repo clone thobho/automated ~/Projects/automated -- -q 2>/dev/null; bash ~/Projects/automated/agent/pirx/setup.sh'
```
Owner's side (as `user`, once; no sudo): the money alert to WhatsApp, and the daily WhatsApp report off:
```
bash ~/Projects/automated/agent/pirx/owner/install.sh
```
Root helper (as `user`, once and after each change to `agent/pirx/root/`):
```
(umask 022; d=$(mktemp -d) && git -C ~/Projects/automated fetch -q && git -C ~/Projects/automated worktree add --detach "$d/ah" origin/main && sudo bash "$d/ah/agent/pirx/root/install-root-helper.sh"; git -C ~/Projects/automated worktree remove --force "$d/ah"; rmdir "$d")
```

## Settings
`~/.config/automated/pirx.env` (agent): `PIRX_SLOTS` (2 since the RAM upgrade to 11 GB), `PIRX_MIN_FREE_MB`, `OPENCODE_MODEL`, `OPENCODE_TIMEOUT_MIN`, `CLAUDE_MAX_RUN_H`, `AUTOMATED_RUNNER_REF`. Two slots need the agent memory cap of `setup-agent-user.sh` (default `MEM_HIGH=6G`, `MEM_MAX=7G`); with less RAM set `PIRX_SLOTS=1` and lower both.

Logs: `~agent/runtime/automated/logs/` (`runner.log`, one file per run).
