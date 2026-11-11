#!/usr/bin/env python3
"""Daily report for the owner: what you must do, blockers, progress, improvement ideas.

Runs on pirx as the `agent` user (systemd timer, 07:45 Europe/Warsaw):
  agent/daily_report.py            build the report and post it as a comment on the "📋 Daily report" issue
  agent/daily_report.py --print    build and print it, post nothing

The comment holds the full report plus a short WhatsApp version between
<!-- whatsapp:start --> and <!-- whatsapp:end -->. At 08:00 a timer of the owner's
user (agent/pirx/report-send.sh) sends that part through Hermes, with a link to the comment.
The agent itself never talks to Hermes.

Improvement ideas: up to 3, from one small OpenRouter call on the OpenCode key (a fraction of a
cent) when the key exists, otherwise from simple rules. Only queue facts are sent, never secrets.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

REPO = os.environ.get("AUTOMATED_GH_REPO", "thobho/automated")
TZ = ZoneInfo(os.environ.get("AGENT_TZ", "Europe/Warsaw"))
RUNTIME = os.path.expanduser(os.environ.get("AUTOMATED_RUNTIME", "~/runtime/automated"))
KEY_FILE = os.path.expanduser(os.environ.get("OPENROUTER_KEY_FILE", "~/.config/automated/openrouter-opencode.key"))
IDEAS_MODEL = os.environ.get("REPORT_IDEAS_MODEL", "deepseek/deepseek-v4.1-flash-1017")
REPORT_TITLE = "📋 Daily report"
AGENT_BRANCH = re.compile(r"^agent(-setup)?/")
ACTION = re.compile(r"(?:^|\n)\s*(?:#+\s*|\*\*)Action for you(?:\*\*)?:?\s*\n?(.*?)(?=\n\s*(?:#+\s|\*\*[A-Z])|\Z)", re.S | re.I)
MARK_FAIL = re.compile(r"<!-- automated:fail:(\w+) -->")


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def gh_json(*args):
    out = gh(*args)
    return json.loads(out) if out.strip() else []


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def first_lines(text, limit=160):
    text = re.sub(r"<!--.*?-->", "", text or "", flags=re.S)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit - 1] + "…"


def collect(now):
    since = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    day = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    issues = [i for i in gh_json("api", f"repos/{REPO}/issues?state=open&per_page=100") if "pull_request" not in i]
    prs = gh_json("pr", "list", "-R", REPO, "--state", "open", "--limit", "50", "--json",
                  "number,title,url,body,createdAt,headRefName,statusCheckRollup")
    merged = gh_json("pr", "list", "-R", REPO, "--state", "merged", "--search", f"merged:>={day}", "--limit", "50",
                     "--json", "number,title,url,mergedAt")
    comments = gh_json("api", f"repos/{REPO}/issues/comments?since={since}&per_page=100")
    milestones = gh_json("api", f"repos/{REPO}/milestones?state=open&per_page=50")
    blocked = []
    for i in issues:
        if any(l["name"] == "agent:blocked" for l in i["labels"]):
            last = gh_json("api", f"repos/{REPO}/issues/{i['number']}/comments?per_page=100")
            blocked.append({"number": i["number"], "title": i["title"], "url": i["html_url"],
                            "question": first_lines(last[-1]["body"] if last else i["body"], 220)})
    runner_log = []
    try:
        with open(os.path.join(RUNTIME, "logs", "runner.log")) as f:
            runner_log = [l for l in f.read().splitlines()[-2000:] if l[1:21] >= since[:19]]
    except OSError:
        pass
    return {
        "now": now, "issues": issues, "prs": prs, "merged": merged, "comments": comments,
        "milestones": milestones, "blocked": blocked, "runner_log": runner_log,
        "claude": load(os.path.join(RUNTIME, "state", "claude-budget.json")),
        "openrouter": load(os.path.join(RUNTIME, "state", "openrouter-budget.json")),
    }


def ci_state(pr):
    checks = pr.get("statusCheckRollup") or []
    states = {(c.get("conclusion") or c.get("state") or c.get("status") or "").upper() for c in checks}
    if not checks:
        return "no CI"
    if states & {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}:
        return "red"
    if states & {"PENDING", "IN_PROGRESS", "QUEUED", "EXPECTED", ""}:
        return "running"
    return "green"


def labels(issue):
    return {l["name"] for l in issue["labels"]}


def analyse(d):
    now = d["now"]
    actions, blockers = [], []
    for b in d["blocked"]:
        actions.append(f"Answer the question in #{b['number']} ({b['title']}): {b['question']} → reply in a comment: {b['url']}")
        blockers.append(f"#{b['number']} {b['title']}: waiting for your answer")
    for i in d["issues"]:
        if "owner:todo" in labels(i):
            actions.append(f"Do: {i['title']} (#{i['number']}): {first_lines(i['body'], 200)} → close the issue when done: {i['html_url']}")
    for pr in sorted(d["prs"], key=lambda p: p["createdAt"]):
        if not AGENT_BRANCH.match(pr["headRefName"]):
            continue
        age_h = (now - datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))).total_seconds() / 3600
        ci = ci_state(pr)
        m = ACTION.search(pr["body"] or "")
        extra = first_lines(m.group(1), 220) if m else ""
        extra = "" if re.match(r"(?i)none\b", extra) else extra
        if ci == "red":
            blockers.append(f"PR #{pr['number']} {pr['title']}: CI is red ({pr['url']})")
            continue
        step = f"Review and merge PR #{pr['number']} {pr['title']} (CI {ci}, open {age_h:.0f} h)"
        actions.append(step + (f"; first: {extra}" if extra else "") + f" → {pr['url']}")
    fails, escalations = {}, []
    for c in d["comments"]:
        n = int(c["issue_url"].rsplit("/", 1)[1])
        if MARK_FAIL.search(c["body"]):
            fails[n] = fails.get(n, 0) + 1
        if c["body"].startswith(("⬆️", "🛑")):
            escalations.append(f"#{n}: {first_lines(c['body'], 120)}")
    for n, k in sorted(fails.items()):
        blockers.append(f"#{n}: {k} failed run(s) in the last 24 h")
    blockers += escalations
    waits = [l for l in d["runner_log"] if "gate" in l or "WAIT" in l or "skipped" in l]
    if len(waits) >= 6:
        blockers.append(f"Gates stopped {len(waits)} runs in 24 h (budget or memory), e.g. {first_lines(waits[-1][23:], 120)}")

    opened = [p for p in d["prs"] if (now - datetime.fromisoformat(p["createdAt"].replace("Z", "+00:00"))) <= timedelta(days=1)]
    states = {}
    for i in d["issues"]:
        for s in ("todo", "doing", "review", "blocked"):
            if f"agent:{s}" in labels(i):
                states[s] = states.get(s, 0) + 1
    progress = {
        "merged": [f"#{p['number']} {p['title']}" for p in d["merged"]],
        "opened": [f"#{p['number']} {p['title']}" for p in opened],
        "queue": states,
        "milestones": [f"{m['title']}: {m['closed_issues']}/{m['open_issues'] + m['closed_issues']} done"
                       for m in sorted(d["milestones"], key=lambda m: m["title"])],
    }
    c, o = d["claude"], d["openrouter"]
    budget = []
    if c.get("weekly_used") is not None:
        budget.append(f"Claude week {c['weekly_used']:.0f}% used, even line {c.get('weekly_allowed_now', '?')}% (resets {c.get('weekly_resets_at', '?')[:10]})")
    if o.get("usage_monthly_usd") is not None:
        budget.append(f"OpenRouter ${o['usage_monthly_usd']:.2f} of ${o.get('monthly_budget_usd', 10):.0f} this month")
    return {"actions": actions, "blockers": blockers, "progress": progress, "budget": budget,
            "fails": fails, "headroom": c.get("weekly_headroom")}


def rule_ideas(a):
    ideas = []
    for n, k in a["fails"].items():
        if k >= 2:
            ideas.append(f"#{n} failed {k} times: split it into smaller issues or make its 'Done when' more precise.")
    reviews = a["progress"]["queue"].get("review", 0)
    if reviews >= 4:
        ideas.append(f"{reviews} PRs wait for review; agents pause new work at 5. Reviewing two today keeps them busy.")
    if not a["progress"]["queue"].get("todo") and (a["headroom"] or 0) > 10:
        ideas.append("The queue is empty while budget is unused: ask Claude to refine the next milestone's tasks.")
    return ideas[:3]


def llm_ideas(a):
    try:
        with open(KEY_FILE) as f:
            key = f.read().strip()
    except OSError:
        return None
    facts = {k: a[k] for k in ("blockers", "progress", "budget")}
    facts["open_actions"] = len(a["actions"])
    body = {
        "model": IDEAS_MODEL, "max_tokens": 1200, "temperature": 0.3,
        "reasoning": {"effort": "low", "exclude": True},
        "provider": {"data_collection": "deny"},
        "messages": [
            {"role": "system", "content": "You advise the owner of an autonomous coding-agent setup. Give at most 3 concrete, "
             "actionable improvement proposals (one line each, imperative, no fluff) based only on the facts. "
             "Prefer changes to task scoping, review flow and budget use. Output a plain list, one proposal per line."},
            {"role": "user", "content": json.dumps(facts, ensure_ascii=False)},
        ],
    }
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            text = json.load(r)["choices"][0]["message"].get("content")
    except Exception:
        return None
    if not text:
        return None
    lines = [re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", l).strip() for l in text.splitlines()]
    return [l for l in lines if l][:3] or None


def render(a, ideas, now):
    day = now.astimezone(TZ).strftime("%a %d %b")
    p = a["progress"]
    def bullets(items, empty="_none_"):
        return "\n".join(f"{i}. {x}" for i, x in enumerate(items, 1)) if items else empty
    full = f"""## {REPORT_TITLE}: {day}

### ✅ What you must do ({len(a['actions'])})
{bullets(a['actions'], '_Nothing: agents are not waiting on you._')}

### 🚧 Blockers ({len(a['blockers'])})
{bullets(a['blockers'])}

### 📈 Progress (last 24 h)
- Merged: {', '.join(p['merged']) or 'none'}
- PRs opened: {', '.join(p['opened']) or 'none'}
- Queue: {', '.join(f'{k} {v}' for k, v in p['queue'].items()) or 'empty'}
- Milestones: {'; '.join(p['milestones']) or 'none yet'}
- Budget: {'; '.join(a['budget']) or 'no data yet'}

### 💡 Improvement ideas
{bullets(ideas)}
"""
    top = a["actions"][:5]
    short = [f"📋 automated, {day}"]
    short.append(f"Do today ({len(a['actions'])}):" if a["actions"] else "Nothing for you today.")
    short += [f"{i}. {first_lines(x, 180)}" for i, x in enumerate(top, 1)]
    if len(a["actions"]) > 5:
        short.append(f"…and {len(a['actions']) - 5} more in the full report")
    short.append(f"Blockers: {len(a['blockers'])}" + (f" ({first_lines(a['blockers'][0], 100)})" if a["blockers"] else ""))
    short.append(f"Done 24 h: {len(p['merged'])} merged, {len(p['opened'])} PRs opened. " + "; ".join(p["milestones"][:2]))
    if a["budget"]:
        short.append("Budget: " + "; ".join(a["budget"]))
    if ideas:
        short.append("Idea: " + first_lines(ideas[0], 160))
    return full + "\n<!-- whatsapp:start -->\n" + "\n".join(short) + "\n<!-- whatsapp:end -->\n"


def report_issue():
    found = gh_json("api", f"repos/{REPO}/issues?labels=agent:report&state=open&per_page=1")
    if found:
        return found[0]["number"]
    url = gh("issue", "create", "-R", REPO, "--title", REPORT_TITLE, "--label", "agent:report",
             "--body", "Daily reports from the agents, one comment per day. Read on WhatsApp via Hermes.").strip()
    return int(url.rsplit("/", 1)[1])


def main():
    now = datetime.now(timezone.utc)
    a = analyse(collect(now))
    ideas = llm_ideas(a) or rule_ideas(a)
    text = render(a, ideas, now)
    if "--print" in sys.argv:
        print(text)
        return
    n = report_issue()
    url = gh("issue", "comment", str(n), "-R", REPO, "--body", text).strip()
    print(url)


if __name__ == "__main__":
    main()
