#!/usr/bin/env python3
"""Send one prompt (plus file context) to an OpenRouter model.

Usage:
  openrouter.py --role planner|coder --task FILE [--context PATH ...] --out FILE [--apply]

--role picks the model (env overrides: ORCH_PLANNER_MODEL, ORCH_CODER_MODEL).
--task is a text file holding the instruction for this call.
--context files are pasted in, each wrapped in a FILE block.
--out receives the raw model reply.
--apply parses FILE blocks in the reply and writes them to disk (coder role).

The API key comes from $OPENROUTER_API_KEY or ~/.config/automated/secrets.env.
Prints token usage and cost to stderr. Standard library only.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODELS = {
    "planner": os.environ.get("ORCH_PLANNER_MODEL", "deepseek/deepseek-r1-0528"),
    "coder": os.environ.get("ORCH_CODER_MODEL", "qwen/qwen-2.5-coder-32b-instruct"),
}

SYSTEM = {
    "planner": (
        "You are a senior software architect. Read the task and code context and write a "
        "technical plan in Markdown with exactly these sections: ## Objectives, "
        "## Affected files, ## Implementation steps (numbered), ## Acceptance criteria, "
        "## Tests to add or run. Be concrete: name files, functions and commands. "
        "Output only the plan."
    ),
    "coder": (
        "You are a precise software engineer. Implement exactly what the task asks. "
        "For every file you create or change, output its COMPLETE new content in this form "
        "and nothing else:\n"
        "=== FILE: relative/path.ext ===\n<full file content>\n=== END FILE ===\n"
        "No Markdown fences, no prose, no partial files, no placeholders like '...'."
    ),
}

FILE_BLOCK = re.compile(r"^=== FILE: (.+?) ===\n(.*?)^=== END FILE ===$", re.S | re.M)


def api_key():
    # The secrets file wins over the env: a stale exported key is easy to miss.
    secrets = Path.home() / ".config/automated/secrets.env"
    if secrets.exists():
        for line in secrets.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    sys.exit("OPENROUTER_API_KEY not found in ~/.config/automated/secrets.env or the env")


def build_prompt(task_file, context):
    parts = [Path(task_file).read_text()]
    for path in context:
        p = Path(path)
        body = p.read_text() if p.exists() else "(file does not exist yet)"
        parts.append(f"=== FILE: {path} ===\n{body}\n=== END FILE ===")
    return "\n\n".join(parts)


def call(model, system, prompt):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({
            "model": model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
            "usage": {"include": True},
        }).encode(),
        headers={"Authorization": f"Bearer {api_key()}",
                 "Content-Type": "application/json",
                 "X-Title": "model-orchestrator"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"OpenRouter HTTP {e.code}: {e.read().decode()[:500]}")
    if "error" in data:
        sys.exit(f"OpenRouter error: {data['error']}")
    usage = data.get("usage", {})
    print(f"[{model}] prompt={usage.get('prompt_tokens')} completion={usage.get('completion_tokens')} "
          f"cost=${usage.get('cost', '?')}", file=sys.stderr)
    return data["choices"][0]["message"]["content"]


def apply_blocks(reply):
    root = Path.cwd().resolve()
    written = []
    for path, body in FILE_BLOCK.findall(reply):
        target = (root / path.strip()).resolve()
        if root not in target.parents:
            print(f"skipped (outside repo): {path}", file=sys.stderr)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
        written.append(str(target.relative_to(root)))
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=MODELS, required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--context", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    reply = call(MODELS[args.role], SYSTEM[args.role], build_prompt(args.task, args.context))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(reply)
    if args.apply:
        written = apply_blocks(reply)
        if not written:
            sys.exit(f"no FILE blocks found in reply; see {args.out}")
        print("\n".join(written))


if __name__ == "__main__":
    main()
