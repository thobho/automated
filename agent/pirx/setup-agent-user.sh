#!/usr/bin/env bash
# Interactive setup of the isolated `agent` user on pirx, for unattended agent runs (Claude Code, OpenCode).
#
#   Run on pirx:   sudo bash setup-agent-user.sh
#
# It does everything in order and asks you to paste the secrets when it needs them (input is hidden,
# nothing is printed or written to logs). Safe to run again: finished steps are skipped or re-checked.
#
# The agent user gets:
#   - its own home (750); it cannot read /home/user, Hermes, your SSH keys, gh or OpenRouter config
#   - no sudo, no password, not in docker/lxd/adm/sudo (each of those is root-equivalent or close)
#   - memory and CPU caps, so Hermes and the rest of pirx stay responsive
#   - internet and localhost only: no home LAN, no tailnet
#   - SSH login only with your Mac's key
#   - its own GitHub token (only thobho/automated), its own Claude login, its own OpenRouter key
set -euo pipefail

AGENT="${AGENT:-agent}"
REPO="thobho/automated"
MAC_PUBKEY="${MAC_PUBKEY:-ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE0xpNj+dv0KPjZ6aL99KhGW3GRDgKHcDoyNrXc+Bmne mac}"
MEM_HIGH="${MEM_HIGH:-1300M}"     # soft cap for 4 GB pirx; raise after the RAM upgrade (e.g. 6G)
MEM_MAX="${MEM_MAX:-1700M}"       # hard cap: the agent's processes are killed above this, never Hermes
CPU_QUOTA="${CPU_QUOTA:-300%}"    # at most 3 of the 4 threads
BLOCK_LAN="${BLOCK_LAN:-1}"

bold() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()   { printf '   \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '   \033[33m!\033[0m %s\n' "$*"; }
as_agent() {  # run a multi-line script as the agent (login shell); the script goes in on stdin, so no quoting issues
  sudo -u "$AGENT" -H bash -l -s <<<"cd ~ || exit 1
$1"
}
ask_secret() {  # ask_secret "<prompt>" -> prints the value; input hidden
  local v; read -rsp "   $1: " v < /dev/tty; echo >&2; printf '%s' "$v"
}
pause() { read -rp "   $1 [Enter] " _ < /dev/tty; }

[[ $EUID -eq 0 ]] || { echo "Run with sudo: sudo bash $0"; exit 1; }
[[ -t 0 || -e /dev/tty ]] || { echo "Run this in a terminal (it asks for tokens)."; exit 1; }

# ---------------------------------------------------------------------------------------------
bold "1/11 Packages"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq bubblewrap socat uidmap acl git gh jq curl python3 >/dev/null
ok "bubblewrap, socat (Claude Code sandbox), uidmap (rootless containers later), git, gh, jq, curl"

bold "2/11 User $AGENT"
if id "$AGENT" >/dev/null 2>&1; then ok "exists"; else
  useradd --create-home --shell /bin/bash --comment "automated agent runs" "$AGENT"; ok "created"
fi
passwd -l "$AGENT" >/dev/null
for g in sudo adm lxd docker; do
  if id -nG "$AGENT" | tr ' ' '\n' | grep -qx "$g"; then gpasswd -d "$AGENT" "$g" >/dev/null; warn "removed from group $g"; fi
done
chmod 750 "/home/$AGENT"
case "$(stat -c %a /home/user)" in 750|700) ok "/home/user is private ($(stat -c %a /home/user))";;
  *) warn "/home/user is $(stat -c %a /home/user): the agent could read it. Fix with: chmod 750 /home/user";; esac
grep -q "^$AGENT:" /etc/subuid || usermod --add-subuids 200000-265535 --add-subgids 200000-265535 "$AGENT"
ok "no password, no sudo; groups: $(id -nG "$AGENT")"

bold "3/11 Lingering (its timers run without a login)"
loginctl enable-linger "$AGENT"; ok "on"

bold "4/11 Memory and CPU caps"
uid="$(id -u "$AGENT")"
mkdir -p "/etc/systemd/system/user-$uid.slice.d"
cat > "/etc/systemd/system/user-$uid.slice.d/50-agent-limits.conf" <<EOF
[Slice]
MemoryHigh=$MEM_HIGH
MemoryMax=$MEM_MAX
MemorySwapMax=512M
CPUQuota=$CPU_QUOTA
TasksMax=2048
EOF
systemctl daemon-reload
ok "memory $MEM_HIGH soft / $MEM_MAX hard, CPU $CPU_QUOTA"

bold "5/11 Network guard: internet and localhost only"
if [[ "$BLOCK_LAN" == 1 ]]; then
  cat > /etc/agent-netguard.nft <<EOF
table inet agent_guard
delete table inet agent_guard
table inet agent_guard {
  chain out {
    type filter hook output priority 0; policy accept;
    meta skuid $uid ip daddr 127.0.0.0/8 accept
    meta skuid $uid ip6 daddr ::1 accept
    meta skuid $uid ip daddr { 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 100.64.0.0/10, 169.254.0.0/16 } counter reject
    meta skuid $uid ip6 daddr { fc00::/7, fe80::/10 } counter reject
  }
}
EOF
  cat > /etc/systemd/system/agent-netguard.service <<'EOF'
[Unit]
Description=Block LAN and tailnet access for the agent user
After=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft -f /etc/agent-netguard.nft
ExecStop=/usr/sbin/nft delete table inet agent_guard

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable agent-netguard.service >/dev/null 2>&1
  systemctl restart agent-netguard.service
  if as_agent 'curl -s -m 5 -o /dev/null http://192.168.68.1 && echo open || echo blocked' | grep -q blocked \
     && as_agent 'curl -s -m 10 -o /dev/null -w "%{http_code}" https://api.github.com' | grep -q 200; then
    ok "LAN blocked, internet works"
  else
    warn "check the network guard: LAN should be blocked and https://api.github.com reachable"
  fi
else
  warn "skipped (BLOCK_LAN=0)"
fi

bold "6/11 SSH: only your Mac may log in as $AGENT"
install -d -m 700 -o "$AGENT" -g "$AGENT" "/home/$AGENT/.ssh"
ak="/home/$AGENT/.ssh/authorized_keys"; touch "$ak"
grep -qF "$(echo "$MAC_PUBKEY" | awk '{print $2}')" "$ak" || echo "$MAC_PUBKEY" >> "$ak"
chown "$AGENT:$AGENT" "$ak"; chmod 600 "$ak"
ok "Mac key added"
grep -qiE '^\s*AllowUsers' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null && warn "sshd has AllowUsers: add $AGENT there and run: systemctl reload ssh"

bold "7/11 Folders and git identity"
as_agent '
  mkdir -p ~/Projects ~/runtime/automated/logs ~/.config/automated && chmod 700 ~/.config/automated
  git config --global user.name "automated agent (pirx)"
  git config --global user.email "agent@pirx.local"
  git config --global init.defaultBranch main
  git config --global push.default current
  touch ~/.profile
  sed -i "/\.opencode\/bin/d" ~/.profile
  echo "export PATH=\"\$HOME/.local/bin:\$HOME/.opencode/bin:\$PATH\"" >> ~/.profile
  grep -n "opencode/bin" ~/.profile'
ok "~/Projects, ~/runtime/automated, ~/.config/automated (700)"

bold "8/11 Tools (official installers, into /home/$AGENT)"
as_agent '
  export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$PATH"
  command -v uv >/dev/null       || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
  command -v claude >/dev/null   || curl -fsSL https://claude.ai/install.sh | bash >/dev/null 2>&1
  command -v opencode >/dev/null || curl -fsSL https://opencode.ai/install | bash >/dev/null 2>&1
  for t in uv claude opencode; do printf "   %s: %s\n" "$t" "$(command -v $t || echo MISSING)"; done'

# ---------------------------------------------------------------------------------------------
bold "9/11 GitHub token (only for $REPO)"
if as_agent "gh api repos/$REPO --jq .permissions.push 2>/dev/null" | grep -q true; then
  ok "already logged in with push access to $REPO"
else
  cat <<'EOF'
   Create it in a browser (phone or Mac is fine):
     github.com -> your avatar -> Settings -> Developer settings -> Personal access tokens
     -> Fine-grained tokens -> Generate new token
       Token name:         pirx-agent
       Expiration:         90 days
       Repository access:  Only select repositories -> thobho/automated
       Permissions -> Repository:
         Contents, Issues, Pull requests, Workflows ... Read and write
         Actions, Metadata ............................ Read-only
     -> Generate token, then copy it (starts with github_pat_).
EOF
  while :; do
    tok="$(ask_secret "Paste the GitHub token (hidden)")"
    [[ "$tok" == github_pat_* ]] || { warn "that does not look like a fine-grained token (github_pat_...); try again"; continue; }
    if printf '%s\n' "$tok" | sudo -iu "$AGENT" gh auth login --hostname github.com --git-protocol https --with-token 2>/dev/null \
       && as_agent "gh api repos/$REPO --jq .permissions.push" | grep -q true; then
      unset tok; as_agent 'gh auth setup-git' >/dev/null 2>&1; ok "token works: push access to $REPO"; break
    fi
    unset tok; warn "the token was rejected or has no write access to $REPO; check the permissions and paste it again"
  done
fi
other="$(as_agent 'gh api user/repos --jq "length" 2>/dev/null' || echo 0)"
[[ "${other:-0}" -le 1 ]] && ok "the token sees only $REPO" || warn "the token sees $other repositories; it should be limited to $REPO"

bold "10/11 Claude login (your plan)"
if [[ -s "/home/$AGENT/.claude/.credentials.json" ]]; then
  ok "already logged in"
else
  cat <<'EOF'
   Claude Code opens now as the agent user. In it:
     1. type  /login  and press Enter
     2. choose your Claude subscription account, open the link it shows, approve
     3. paste the code back if it asks, then type  /exit
EOF
  pause "Ready?"
  sudo -iu "$AGENT" bash -lc 'claude' < /dev/tty || true
  [[ -s "/home/$AGENT/.claude/.credentials.json" ]] && ok "logged in" || warn "no login found; run this script again to retry"
fi
if [[ -s "/home/$AGENT/.claude/.credentials.json" ]]; then
  reply="$(as_agent 'timeout 120 claude -p "Reply with exactly: OK" --model haiku 2>/dev/null' || true)"
  [[ "$reply" == *OK* ]] && ok "test call works" || warn "test call failed: $reply"
fi

bold "11/11 OpenRouter key for OpenCode"
keyfile="/home/$AGENT/.config/automated/openrouter-opencode.key"
check_key() {  # reads the key on stdin, prints the key info JSON (the key never appears in arguments)
  sed 's/^/Authorization: Bearer /' | curl -s -m 20 -H @- https://openrouter.ai/api/v1/key
}
if [[ -s "$keyfile" ]] && check_key < "$keyfile" | jq -e '.data.usage_monthly != null' >/dev/null 2>&1; then
  ok "key present and valid"
else
  cat <<'EOF'
   Create it at https://openrouter.ai/settings/keys -> Create key:
     Name:         pirx-opencode
     Credit limit: 10
     Reset:        Monthly
   (A normal inference key, NOT a management/provisioning key.) Copy it (starts with sk-or-).
EOF
  while :; do
    key="$(ask_secret "Paste the OpenRouter key (hidden)")"
    [[ "$key" == sk-or-* ]] || { warn "that does not look like an OpenRouter key (sk-or-...); try again"; continue; }
    info="$(printf '%s\n' "$key" | check_key)"
    if ! jq -e '.data.usage_monthly != null' >/dev/null 2>&1 <<<"$info"; then unset key; warn "OpenRouter rejected the key; paste it again"; continue; fi
    if jq -e '.data.is_management_key == true or .data.is_provisioning_key == true' >/dev/null <<<"$info"; then
      unset key; warn "this is a management key; create a normal key with a 10 USD monthly limit"; continue
    fi
    ( umask 077; printf '%s\n' "$key" > "$keyfile" ); chown "$AGENT:$AGENT" "$keyfile"; unset key
    lim="$(jq -r '.data.limit // "none"' <<<"$info")"; reset="$(jq -r '.data.limit_reset // "none"' <<<"$info")"
    ok "saved (limit: $lim, reset: $reset)"
    [[ "$lim" == none || "$reset" == none ]] && warn "set a 10 USD limit with a monthly reset on this key at openrouter.ai"
    break
  done
fi

# ---------------------------------------------------------------------------------------------
bold "Done"
echo "   Agent user: $(id "$AGENT")"
echo "   Next: tell Claude on the Mac \"agent user ready\". It checks everything over SSH as $AGENT"
echo "   (without reading the secrets) and installs the runners and the daily report."
