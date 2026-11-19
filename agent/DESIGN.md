# Design principles of the automation

Why the automation is shaped the way it is, and the rules for changing it. Read this before adding an
agent, a role or a step. Based on a review of multi-agent practice on 2026-11-19 (sources at the end).

## The shape: a pipeline with verification points, not a swarm
GitHub issues → planner → builder → reviewer → merge-ready → dev site, with the healer beside it.
Each step hands over a **checkable artefact** (an issue with Given/When/Then, a PR with green CI, a verdict
with evidence), so the next step can verify the result without the previous step's context.

## Rules
1. **One agent per task, split by context, not by job title.** A story is one issue built by one run. Do not
   add planner → coder → tester → reviewer chains inside a task: every handoff loses detail ("telephone game")
   and costs 3-10× the tokens. Add a separate agent only for one of three reasons: protecting context from a
   large, mostly irrelevant output; truly independent parallel work; or a separate check that must not share
   the builder's bias (the reviewer).
2. **The reviewer is an evaluator, and evaluators start lenient.** Keep it on a different model or run, give it
   hard rules it cannot talk itself out of (diff policy, evidence per criterion, the runner's `enforce()`), and
   calibrate it with real past cases in `review-prompt.md`. When it approves something it should not have,
   add that case to the calibration examples.
3. **Test like a user.** Curl and unit tests miss broken pages; user-visible changes need a browser test
   (D107). A skipped test is not evidence.
4. **Isolation is not integration.** Worktrees keep files apart, not intent. Two builds of one project run in
   parallel only on disjoint `Uses: app:` claims, approved PRs merge only against the current `main`, and a
   red `main` stops merges for that project until a fix lands (merge-ready.sh, heal.sh).
5. **Bounded tasks, explicit "done".** Small issues with observable acceptance criteria; a builder that finds
   the issue unclear decides reversibly and says so, and blocks only for money, credentials or contradictions.
6. **Humans orchestrate, they do not approve every step.** Approval prompts do not scale: give agents the
   rights they need inside the `agent` account (allowlist, root helper, sudo queue) and keep the owner for
   money, permissions and product decisions.
7. **Measure, then learn.** The health page shows first-pass approval, rounds, returns, red main and cost per
   run kind and model (metrics.py). The weekly retro turns repeated review findings into rules.
8. **Every component is an assumption about what the model cannot do alone.** When a stronger model arrives,
   try removing a step (one at a time, with the metrics as the judge) before adding one. Add complexity only
   when the metrics show a real gap.

## Sources
- Anthropic, [Building multi-agent systems: when and how to use them](https://claude.com/resources/articles/building-multi-agent-systems-when-and-how-to-use-them) (Jan 2026)
- Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Jun 2025)
- Anthropic, [Effective harnesses for long-running agents](https://anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Nov 2025)
- Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (Mar 2026)
- Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) (NeurIPS 2025)
- Practitioner reports: [Mike Mason](https://mikemason.ca/writing/ai-coding-agents-jan-2026/), [AI coding agent merge queue](https://dev.to/jackm-singularity/ai-coding-agent-merge-queue-ship-parallel-changes-without-hidden-conflicts-46c1), [Nick Jensen](https://www.nickjensen.co/posts/autonomous-coding-swarm-lessons)
