#!/usr/bin/env python3
"""Tests for review_queue.py. Run: python3 agent/test_review_queue.py"""
import unittest

import review_queue as rq


def pr(n, branch="agent/5-x", sha="abc", checks=("SUCCESS",), comments=(), files=("projects/p/app.py",),
       body="Closes #5", draft=False, mergeable="MERGEABLE", parents=None, committer="noreply@github.com",
       verified=True, approved=None, has_ci=True):
    d = {"headCommit": {"parents": parents or [], "committer": committer, "verified": verified},
         "projectHasCI": has_ci}
    if approved is not None:
        d["approvedShas"] = approved
    return {**d, "number": n, "title": f"pr {n}", "headRefName": branch, "headRefOid": sha, "body": body,
            "isDraft": draft, "mergeable": mergeable, "statusCheckRollup": [{"conclusion": c} for c in checks],
            "comments": [{"body": b} for b in comments], "files": [{"path": f} for f in files]}


class MergeSafety(unittest.TestCase):
    APPROVED = "ok <!-- automated:review:aaa1111 --> <!-- automated:approved:aaa1111 -->"
    UPD = dict(sha="bbb2222", comments=[APPROVED], parents=["aaa1111", "main999"])

    def test_github_update_of_approved_commit_merges_without_a_new_review(self):
        a = rq.assess(pr(1, **self.UPD), {"agent:review"})
        self.assertTrue(a["needs_merge"])
        self.assertFalse(a["needs_review"])
        self.assertTrue(a["update_of_approved"])

    def test_update_waits_for_ci_running_or_not_started(self):
        self.assertFalse(rq.assess(pr(1, checks=("IN_PROGRESS",), **self.UPD), set())["needs_merge"])
        self.assertFalse(rq.assess(pr(1, checks=(), **self.UPD), set())["needs_merge"])

    def test_no_checks_is_fine_when_the_project_has_no_ci(self):
        self.assertTrue(rq.assess(pr(1, checks=(), has_ci=False, **self.UPD), set())["needs_merge"])

    def test_red_ci_is_handled_once(self):
        a = rq.assess(pr(1, checks=("FAILURE",), **self.UPD), set())
        self.assertTrue(a["needs_merge"])
        done = dict(self.UPD, comments=[self.APPROVED, "red <!-- automated:merge-red:bbb2222 -->"])
        self.assertFalse(rq.assess(pr(1, checks=("FAILURE",), **done), set())["needs_merge"])

    def test_merge_not_made_by_github_needs_review(self):
        for kw in ({"committer": "agent@pirx"}, {"verified": False}):
            a = rq.assess(pr(1, **self.UPD, **kw), set())
            self.assertFalse(a["needs_merge"])
            self.assertTrue(a["needs_review"])

    def test_builder_push_after_approval_needs_a_real_review(self):
        a = rq.assess(pr(1, sha="ccc3333", comments=[self.APPROVED], parents=["aaa1111"]), set())
        self.assertFalse(a["needs_merge"])
        self.assertTrue(a["needs_review"])

    def test_merge_of_main_into_unapproved_commit_needs_review(self):
        a = rq.assess(pr(1, sha="ccc3333", comments=[self.APPROVED], parents=["fff0000", "main999"]), set())
        self.assertFalse(a["needs_merge"])
        self.assertTrue(a["needs_review"])

    def test_local_records_win_over_comment_markers(self):
        forged = rq.assess(pr(1, sha="aaa1111", comments=[self.APPROVED], approved=[]), set())
        self.assertFalse(forged["needs_merge"])
        real = rq.assess(pr(1, sha="aaa1111", comments=[], approved=["aaa1111"]), set())
        self.assertTrue(real["needs_merge"])

    def test_approved_head_waits_in_merge_ready(self):
        a = rq.assess(pr(1, sha="aaa1111", comments=[self.APPROVED]), set())
        self.assertTrue(a["needs_merge"])
        self.assertFalse(a["needs_review"])

    def test_protected_pr_is_never_merged_here(self):
        a = rq.assess(pr(1, sha="aaa1111", comments=[self.APPROVED], files=("agent/budget.py",)), set())
        self.assertFalse(a["needs_merge"])

    def test_with_builder_is_not_merged(self):
        self.assertFalse(rq.assess(pr(1, **self.UPD), {"agent:todo"})["needs_merge"])

    def test_updates_are_counted_and_red_main_fix_flagged(self):
        up = "updated <!-- automated:approved:bbb2222 --> <!-- automated:updated -->"
        a = rq.assess(pr(1, sha="ccc3333", comments=[self.APPROVED, up], parents=["bbb2222", "m"]), {"red-main"})
        self.assertTrue(a["needs_merge"])
        self.assertEqual(a["updates"], 1)
        self.assertTrue(a["red_main_fix"])

    def test_project_of(self):
        self.assertEqual(rq.project_of(["projects/a/x.py", "projects/a/y.py"]), "a")
        self.assertIsNone(rq.project_of(["projects/a/x.py", "projects/b/y.py"]))
        self.assertIsNone(rq.project_of(["agent/x.py"]))


class DiffPolicy(unittest.TestCase):
    def test_flags(self):
        files = [
            {"filename": "projects/p/tests/test_a.py", "status": "removed", "deletions": 40, "additions": 0},
            {"filename": "projects/p/apps/x/tests/test_b.py", "status": "modified", "additions": 3, "deletions": 1,
             "patch": "@@ -1 +1 @@\n+@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='no ffmpeg')\n def test_x():"},
            {"filename": ".github/workflows/p-ci.yml", "status": "modified", "patch": "+  run: pytest"},
            {"filename": "projects/p/pyproject.toml", "status": "modified", "patch": "+addopts = '-k not slow'"},
            {"filename": "projects/p/apps/x/views.py", "status": "modified", "patch": "+def view(): pass"},
        ]
        flags = rq.diff_policy(files)
        self.assertEqual(len(flags), 4)
        self.assertIn("test file deleted: projects/p/tests/test_a.py", flags)
        self.assertTrue(any("pytest.mark.skipif" in f for f in flags))

    def test_new_workflow_and_plain_code_are_not_flagged(self):
        files = [{"filename": ".github/workflows/new-ci.yml", "status": "added", "patch": "+on: push"},
                 {"filename": "projects/p/pyproject.toml", "status": "modified", "patch": "+django = '5.2'"}]
        self.assertEqual(rq.diff_policy(files), [])


class Enforce(unittest.TestCase):
    OK = {"verdict": "approve", "summary": "s", "points": [],
          "criteria": [{"criterion": "c1", "met": True, "evidence": "test_c1 passes"}]}

    def test_complete_approval_stays(self):
        self.assertEqual(rq.enforce(self.OK, [])["verdict"], "approve")

    def test_missing_evidence_becomes_changes(self):
        v = dict(self.OK, criteria=[{"criterion": "c1", "met": True, "evidence": ""}])
        out = rq.enforce(v, [])
        self.assertEqual(out["verdict"], "changes")
        self.assertEqual(len(out["points"]), 1)

    def test_unjudged_flag_becomes_changes(self):
        self.assertEqual(rq.enforce(self.OK, ["x.py: adds `pytest.mark.skip`"])["verdict"], "changes")

    def test_justified_flag_stays_approved(self):
        flag = "x.py: adds `pytest.mark.skip`"
        v = dict(self.OK, policy=[{"flag": flag, "ok": True, "why": "binary missing locally; CI sets REQUIRE_FFMPEG"}])
        self.assertEqual(rq.enforce(v, [flag])["verdict"], "approve")

    def test_changes_verdict_is_untouched(self):
        v = {"verdict": "changes", "points": [{"issue": "x"}]}
        self.assertIs(rq.enforce(v, ["f"]), v)


class Assess(unittest.TestCase):
    def test_green_unreviewed_needs_review(self):
        a = rq.assess(pr(1), set())
        self.assertTrue(a["needs_review"])
        self.assertEqual((a["issue"], a["ci"], a["protected"]), (5, "green", []))

    def test_running_ci_waits(self):
        self.assertFalse(rq.assess(pr(1, checks=("IN_PROGRESS",)), set())["needs_review"])

    def test_red_ci_still_goes_to_review_step(self):
        a = rq.assess(pr(1, checks=("SUCCESS", "FAILURE")), set())
        self.assertEqual(a["ci"], "red")
        self.assertTrue(a["needs_review"])

    def test_reviewed_for_this_sha_is_done(self):
        a = rq.assess(pr(1, comments=["ok <!-- automated:review:abc -->"]), set())
        self.assertFalse(a["needs_review"])

    def test_new_push_needs_a_new_review(self):
        a = rq.assess(pr(1, sha="def", comments=["x <!-- automated:review:abc --> <!-- automated:review-changes -->"]), set())
        self.assertTrue(a["needs_review"])
        self.assertEqual(a["rounds"], 1)

    def test_no_checks_counts_as_finished(self):
        a = rq.assess(pr(1, checks=()), set())
        self.assertEqual(a["ci"], "none")
        self.assertTrue(a["needs_review"])


class BackWithBuilder(unittest.TestCase):
    def test_task_sent_back_is_not_reviewed_again(self):
        for state in ("agent:todo", "agent:doing", "agent:blocked"):
            self.assertFalse(rq.assess(pr(1), {state})["needs_review"], state)
        self.assertTrue(rq.assess(pr(1), {"agent:review"})["needs_review"])


class Conflicts(unittest.TestCase):
    def test_conflicting_pr_is_resolved_not_reviewed(self):
        a = rq.assess(pr(1, mergeable="CONFLICTING"), {"agent:review"})
        self.assertTrue(a["needs_resolve"])
        self.assertFalse(a["needs_review"])
        self.assertEqual((a["conflict_attempts"], a["conflict_model"]), (0, "sonnet"))

    def test_second_attempt_uses_opus_and_the_limit_stops_it(self):
        one = rq.assess(pr(1, mergeable="CONFLICTING", comments=["x " + rq.CONFLICT_FAILED]), set())
        self.assertEqual((one["needs_resolve"], one["conflict_model"]), (True, "opus"))
        two = rq.assess(pr(1, mergeable="CONFLICTING", comments=[rq.CONFLICT_FAILED, rq.CONFLICT_FAILED]), set())
        self.assertFalse(two["needs_resolve"])

    def test_successes_do_not_use_up_attempts(self):
        c = [rq.CONFLICT_FAILED, rq.CONFLICT_RESOLVED, rq.CONFLICT_RESOLVED]
        a = rq.assess(pr(1, mergeable="CONFLICTING", comments=c), set())
        self.assertEqual((a["needs_resolve"], a["conflict_attempts"], a["conflict_model"]), (True, 0, "sonnet"))
        a = rq.assess(pr(1, mergeable="CONFLICTING", comments=c + [rq.CONFLICT_FAILED]), set())
        self.assertEqual((a["conflict_attempts"], a["conflict_model"]), (1, "opus"))

    def test_builder_owns_conflicts_while_it_works(self):
        for state in ("agent:todo", "agent:doing", "agent:blocked"):
            self.assertFalse(rq.assess(pr(1, mergeable="CONFLICTING"), {state})["needs_resolve"], state)

    def test_unknown_mergeable_is_not_a_conflict(self):
        a = rq.assess(pr(1, mergeable="UNKNOWN"), set())
        self.assertFalse(a["needs_resolve"])
        self.assertTrue(a["needs_review"])


class Protected(unittest.TestCase):
    def test_automation_paths(self):
        self.assertEqual(rq.automation(["agent/health.py", "scripts/x.sh", ".github/workflows/deploy-pages.yml",
                                        "CLAUDE.md", "projects/p/a.py", ".github/workflows/artysci-dla-szkol-ci.yml"]),
                         ["agent/health.py", "scripts/x.sh", ".github/workflows/deploy-pages.yml", "CLAUDE.md"])

    def test_money_and_permission_paths_need_the_owner(self):
        guarded = ["agent/budget.py", "agent/openrouter_budget.py", "agent/review_queue.py",
                   "agent/pirx/claude-settings.json", "agent/pirx/heal-settings.json", "agent/pirx/root/automated-root",
                   "agent/pirx/review-run.sh", "agent/pirx/start-claude-run.sh", "agent/pirx/heal-diagnose.sh",
                   "scripts/owner-apply.sh", ".github/workflows/deploy-pages.yml", "CLAUDE.md"]
        self.assertEqual(rq.protected(guarded), guarded)

    def test_permission_and_merge_rule_files_are_guarded(self):
        """Every file that sets a run's --settings or model, the slot lock, the root helper call, the merge
        standard, live systemd units and owner-side code needs the owner's merge (review of PR #88)."""
        paths = ["agent/pirx/claude-run.sh", "agent/pirx/conflict-run.sh", "agent/pirx/planner-run.sh",
                 "agent/pirx/heal.sh", "agent/pirx/common.sh", "agent/pirx/some-future-run.sh",
                 "agent/pirx/systemd/automated-heal.service", "agent/pirx/systemd/automated-heal.timer",
                 "agent/pirx/owner/install.sh", "agent/pirx/owner/money-notify.sh",
                 "agent/review-prompt.md", "agent/pirx/planner-settings.json"]
        for path in paths:
            self.assertEqual(rq.protected([path]), [path], path)

    def test_non_guarded_prompts_and_tests_still_merge_after_review(self):
        for path in ("agent/planner-prompt.md", "agent/worker-prompt.md", "agent/test_planner.py", "agent/planner.py"):
            self.assertEqual(rq.protected([path]), [], path)

    def test_spending_rules_are_money(self):
        self.assertEqual(rq.assess(pr(1, files=("agent/budget.py", "agent/health.py")), set())["money"], ["agent/budget.py"])

    def test_other_automation_merges_after_review(self):
        self.assertEqual(rq.protected(["agent/health.py", "agent/worker-prompt.md",
                                       "scripts/queue.sh", "projects/p/a.py"]), [])


class Models(unittest.TestCase):
    def test_security_always_opus(self):
        self.assertEqual(rq.review_model({"area:security", "model:opus"}), ("opus", None))

    def test_opus_built_reviewed_by_sonnet(self):
        self.assertEqual(rq.review_model({"model:opus"}), ("sonnet", None))

    def test_automation_always_opus(self):
        self.assertEqual(rq.review_model({"model:opus"}, ["agent/health.py"]), ("opus", None))

    def test_default_prefers_opus(self):
        self.assertEqual(rq.review_model({"model:pirx"}), ("opus", "sonnet"))


class Queue(unittest.TestCase):
    def test_only_agent_branches_oldest_first(self):
        q = rq.queue([pr(9), pr(3, branch="feature/x"), pr(4, branch="agent-setup/y")], lambda p: set())
        self.assertEqual([t["pr"] for t in q], [4, 9])


if __name__ == "__main__":
    unittest.main()
