#!/usr/bin/env bash
# Root setup for the pirx dev instance (issue #71). Idempotent; run by the owner via
# `sudo scripts/owner-apply.sh` after review. It does exactly three things:
#   1. enables lingering for `agent` (user units start at boot without a login);
#   2. installs `make` if missing (`make deploy-pirx` needs it);
#   3. lets the agent user's *replies* leave on the LAN: inserts
#      `ct state established,related accept` at the top of the output chain(s) that carry the
#      agent's `skuid` network guard, now and on every boot (systemd unit ads-lan-replies).
#      New outgoing connections from agent stay blocked; only answers to inbound ones pass.
set -euo pipefail

loginctl enable-linger agent

if ! command -v make >/dev/null 2>&1; then
    apt-get install -y make
fi

cat > /usr/local/sbin/ads-allow-lan-replies <<'EOS'
#!/usr/bin/env python3
"""Insert `ct state established,related accept` into the chain(s) holding the skuid guard."""
import json
import subprocess
import sys
import time

COMMENT = "ads-lan-replies"


def find_guard_chains():
    out = subprocess.check_output(["nft", "-j", "list", "ruleset"])
    items = json.loads(out)["nftables"]
    chains, done = set(), set()
    for item in items:
        rule = item.get("rule")
        if not rule:
            continue
        key = (rule["family"], rule["table"], rule["chain"])
        if rule.get("comment") == COMMENT:
            done.add(key)
        elif '"skuid"' in json.dumps(rule["expr"]):
            chains.add(key)
    return chains, done


chains = set()
for _ in range(30):  # at boot the guard may load a moment after us
    chains, done = find_guard_chains()
    if chains:
        break
    time.sleep(1)
if not chains:
    sys.exit("no nft chain with a skuid guard found; nothing changed")
for family, table, chain in sorted(chains - done):
    subprocess.check_call(
        ["nft", "insert", "rule", family, table, chain,
         "ct", "state", "established,related", "accept", "comment", COMMENT]
    )
    print(f"inserted reply rule in {family} {table} {chain}")
EOS
chmod 755 /usr/local/sbin/ads-allow-lan-replies

cat > /etc/systemd/system/ads-lan-replies.service <<'EOS'
[Unit]
Description=Allow replies of inbound LAN connections for the agent user (artysci dev)
After=network-online.target nftables.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/sbin/ads-allow-lan-replies

[Install]
WantedBy=multi-user.target
EOS
systemctl daemon-reload
systemctl enable ads-lan-replies.service
/usr/local/sbin/ads-allow-lan-replies
