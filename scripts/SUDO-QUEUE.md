# Sudo request queue

The worker runs as the unprivileged `agent` user and gets **no sudo**. When a task needs root
(firewall rule, `loginctl enable-linger`, installing a package), the worker queues a script and
the owner approves it. Nothing runs as root without the owner typing their password.

## Agent
1. Write the script (idempotent, small, one purpose) and queue it:
   `scripts/sudo-request.sh <id> <script-file> "<what it does and which issue needs it>"`
   If that script is not allowed in the sandbox, copy the two plain files yourself:
   `~/runtime/automated/sudo-queue/pending/<id>.sh` and `<id>.md`.
2. Comment on the issue with the id and the exact reason, label it `agent:blocked`, stop.
3. On a later run, read the result in `/var/lib/automated-sudo/done/<id>.out` and `<id>.status`
   (or `rejected/<id>.*`) and continue. Ids cannot be reused; pick a new one to retry.

## Owner
```
sudo ~/Projects/automated/scripts/owner-apply.sh          # review and run, one by one
sudo ~/Projects/automated/scripts/owner-apply.sh --list   # look only
```
For each request you see the sha256, the reason and the full script, then `y` (run), `N` (reject) or `s` (leave pending).
The log is `/var/lib/automated-sudo/apply.log`.

## Why it is safe
- The queue adds no `NOPASSWD` entry: `agent` cannot start the runner. (The only sudoers rule for `agent` is the root helper's, `agent/pirx/root/`, which runs a fixed list of verbs: restart listed services, install listed packages, reload the firewall, a rate-limited reboot. Everything else comes here.)
- The script is copied to a root-owned temp dir before you see it; the copy is what runs, so the agent cannot swap it after your review.
- Symlinks, files not owned by `agent`, bad ids and reused ids are skipped.
- Results are written to a root-owned directory, never into agent-writable paths.
- Review the script like any root script. Approving means you trust its contents, not the agent.

Tests: `scripts/test-owner-apply.sh`.
