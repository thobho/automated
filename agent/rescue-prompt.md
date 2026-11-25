## Rescue round

ultrathink. This task has had 3 review rounds without approval, so this is its **rescue round**: one more
build with the strongest model and a larger budget, before the owner has to decide. If the next review
still asks for changes, the task goes to the owner. Spend effort on understanding the problem first, not on
typing code.

Work in this order and do not skip a step:

1. **Read everything.** Read the issue, the PR description, and **every** review comment on the PR (all
   rounds, not only the last one), plus your earlier replies. `gh pr view <pr> --comments` and
   `gh pr diff <pr>`.
2. **List every point.** Write `.agent/RESCUE.md` in the working copy (it is not committed: `.agent/` is
   excluded). It holds a table of every "Must change" point from all rounds: round, file, the point in one
   line, status now (fixed / regressed / still open / new in a later round), and the evidence (a test name or
   a command and its output).
3. **Find the pattern.** In the same file, answer in a few lines: why did the earlier rounds not converge?
   Typical causes: a fix that covered the reported example but not the class of inputs; a fix in one code
   path while a second path (admin, API, a background job, another view) still allows the same thing; a
   test that checks the helper but not the real entry point; a missing acceptance criterion. Name the
   cause for this task.
4. **Reproduce first.** For every open or regressed point, write a failing test through the real entry
   point the reviewer used (view, admin change view, management command, job), and see it fail. Then
   look for the same weakness in the sibling code paths you named in step 3, and add tests there too.
5. **Fix the cause, not the example.** Make all the tests pass. Keep the change focused on the issue's
   scope. Do not weaken, skip or delete an existing test.
6. **Self-review like the reviewer.** Before pushing, go through the table again, point by point, and
   through the issue's acceptance criteria one by one. Run the project's full test suite, the linters and
   the migrations check. Each row needs evidence.
7. **Hand over.** Push to the same branch. In one PR comment, answer each point from the table with what
   changed and the test that proves it, and give the cause from step 3. Then label the issue `agent:review`.

If a point cannot be done inside the sandbox or contradicts the issue, do not work around it: say so in the
PR comment and in the issue, and label the issue `agent:blocked` with the exact question for the owner.
