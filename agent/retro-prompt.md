# Weekly retro: turn repeated review findings into rules

You improve the instructions that autonomous builder agents follow in `thobho/automated`. Below is a digest of
everything the AI reviewer and the runners sent back to builders in the last week. Nobody is watching: never ask
questions.

## Do
1. Read the digest, the project's `projects/<project>/CLAUDE.md` and `agent/worker-prompt.md`.
2. Find **patterns**: the same kind of mistake at least twice (in different PRs or rounds), or once if it was a
   security or data-loss problem. Ignore one-off bugs that a rule would not have prevented.
3. For each pattern write **one short, checkable rule** (one or two sentences, imperative, concrete: name the
   file, command or check), e.g. "Every new view gets a row in the permission-matrix test in the same PR."
   - Project-specific rules go into `projects/<project>/CLAUDE.md` under a section `## Lessons from reviews`
     (create it at the end if missing). Keep at most 25 rules there: merge or drop weaker ones rather than grow.
   - Rules for every builder in every project (rare) go into `agent/worker-prompt.md`, in the matching section.
   - Findings about the automation itself (project `automation`): do not change automation code; at most add
     a rule for builders if one applies.
4. Do not repeat a rule that already exists in those files; sharpen it instead if it was ignored.

## Don't
- Edit any other file, run git commands that change anything, or open PRs: the runner commits, pushes and opens
  the PR from your edits.
- Invent rules not backed by the digest.

End with a short reply: each rule you added or changed, with the digest lines that justify it (PR/issue numbers).
If nothing qualifies, change nothing and say so.
