---
name: new-task
description: Queue a task for the autonomous worker as a GitHub issue in the automated repo. Use when the user says "new task", "queue this", "add to the agent queue", or describes work they want the agent to build later.
---

# Queue a task for the worker

1. From the user's words, work out:
   - **project**: a kebab-case folder name under `projects/`. Run `ls projects/` and reuse an existing one when it fits; otherwise propose a new name.
   - **title**: short and imperative ("Add CSV export to reports").
   - **body**: what to build, plus a **Done when** list the worker can check on its own (commands that work, tests that pass).
   - **priority**: high only if the user says it's urgent or "first".
   - **model**: what the user asked for; otherwise suggest one — `haiku` for small edits, `sonnet` (default) for most tasks, `opus` only for hard design or debugging, since it uses limits fastest.
2. If the task is too vague for an unattended agent to finish, ask the user one or two short questions first. Split large requests into several small tasks (one PR each).
3. Show the user the title, project, model and body, then create it:
   `scripts/new-task.sh -p <project> -t "<title>" -b "<body>" -m <model> [--high]`
4. Reply with the issue link.
