#!/usr/bin/env python3
"""Weekly retro digest: what the AI reviewer and the runners sent back to builders in the last N days.

The digest feeds agent/pirx/retro-run.sh, where a model turns findings that repeat into rules in the
project's CLAUDE.md, so builders stop making the same mistake.
No model here: it only reads GitHub.

Sources, per project (from the PR's files or the issue's project label):
  - "Must change" points of AI reviews that requested changes,
  - "Back to the builder" reasons (red CI, clash with main),
  - builder failure notes (comments starting with ❌).

Only comments written by the automation's own account count ($AUTOMATED_BOT_LOGINS, comma-separated; default
the login of the gh token, which is the account the runners post with), so nobody else can plant a "finding".

Usage:
  agent/retro.py [--days 7]          the digest as Markdown on stdout; exit 1 when fewer than 2 findings,
                                     exit 2 when GitHub could not be read
  agent/retro.py --json [--days 7]
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys

PROJECT_PATH = re.compile(r"^projects/([a-z0-9-]+)/")
POINT = re.compile(r"^\s*\d+\.\s+(.*)$")


def gh_json(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else []


def review_points(body):
    """The numbered points under "Must change:" of one AI review comment that requested changes."""
    if "changes requested" not in body or "**Must change:**" not in body:
        return []
    section = body.split("**Must change:**", 1)[1]
    section = re.split(r"\n\*\*[A-Z][^*]*:\*\*", section, maxsplit=1)[0]
    return [re.sub(r"\s+", " ", m.group(1)).strip()[:400] for line in section.splitlines() if (m := POINT.match(line))]


def other_findings(body):
    """Back-to-builder reasons and failure notes in one comment."""
    out = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("❌") or s.startswith("↩️ Back to the builder") or s.startswith("🔁 CI is red"):
            out.append(re.sub(r"<!--.*?-->", "", s).strip()[:300])
    return out


def project_of(paths, labels=()):
    names = {m.group(1) for p in paths if (m := PROJECT_PATH.match(p))}
    names |= {l.split(":", 1)[1] for l in labels if l.startswith("project:")}
    return names.pop() if len(names) == 1 else "automation"


def bot_logins():
    env = os.environ.get("AUTOMATED_BOT_LOGINS", "").strip()
    if env:
        return {l.strip() for l in env.split(",") if l.strip()}
    out = subprocess.run(["gh", "api", "user", "--jq", ".login"], check=True, capture_output=True, text=True).stdout
    return {out.strip()}


def trusted(comment, logins):
    return ((comment.get("author") or {}).get("login") or "") in logins


def collect(days, logins=None):
    logins = logins if logins is not None else bot_logins()
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    found = {}
    prs = gh_json("pr", "list", "--state", "all", "--limit", "100", "--search", f"updated:>={since}",
                  "--json", "number,title,headRefName,files,comments")  # comments include author.login
    for pr in prs:
        if not re.match(r"^agent(-setup)?/", pr["headRefName"]):
            continue
        proj = project_of([f["path"] for f in pr.get("files") or []])
        for c in pr.get("comments") or []:
            if (c.get("createdAt") or "")[:10] < since or not trusted(c, logins):
                continue
            for p in review_points(c.get("body") or ""):
                found.setdefault(proj, []).append(f"PR #{pr['number']} ({pr['title'][:60]}): {p}")
    issues = gh_json("issue", "list", "--state", "all", "--limit", "100", "--search", f"updated:>={since}",
                     "--json", "number,title,labels,comments")
    for i in issues:
        proj = project_of([], [l["name"] for l in i.get("labels") or []])
        for c in i.get("comments") or []:
            if (c.get("createdAt") or "")[:10] < since or not trusted(c, logins):
                continue
            for f in other_findings(c.get("body") or ""):
                found.setdefault(proj, []).append(f"#{i['number']} ({i['title'][:60]}): {f}")
    return found


def render(found, days):
    out = [f"# Retro digest: findings of the last {days} days", ""]
    for proj in sorted(found):
        out += [f"## {proj} ({len(found[proj])})", ""] + [f"- {f}" for f in found[proj]] + [""]
    return "\n".join(out)


SECRET = re.compile(r"(gh[opsur]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:ant-|or-)?[A-Za-z0-9_-]{20,}"
                    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[abp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16})")


def secret_values(conf_dir):
    """Values (8+ chars) from the automation's secret files: KEY=value lines and whole-file keys."""
    vals = set()
    for name in os.listdir(conf_dir) if os.path.isdir(conf_dir) else []:
        if not (name.endswith(".env") or name.endswith(".key")):
            continue
        try:
            text = open(os.path.join(conf_dir, name), errors="replace").read()
        except OSError:
            continue
        for line in text.splitlines():
            v = line.split("=", 1)[1] if "=" in line else line
            v = v.strip().strip("'\"")
            if len(v) >= 8:
                vals.add(v)
    return vals


def has_secret(text, values=()):
    return bool(SECRET.search(text)) or any(v in text for v in values)


def main():
    if "--scan-secrets" in sys.argv:  # stdin is clean -> exit 0; anything credential-like -> exit 1
        conf = sys.argv[sys.argv.index("--scan-secrets") + 1]
        sys.exit(1 if has_secret(sys.stdin.read(), secret_values(conf)) else 0)
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
    try:
        found = collect(days)
    except (subprocess.CalledProcessError, OSError, ValueError) as e:
        print(f"retro: GitHub could not be read: {e}", file=sys.stderr)
        sys.exit(2)
    total = sum(len(v) for v in found.values())
    if "--json" in sys.argv:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        print(render(found, days))
    sys.exit(0 if total >= 2 else 1)


if __name__ == "__main__":
    main()
