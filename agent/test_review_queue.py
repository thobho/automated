#!/usr/bin/env python3
"""Tests for review_queue.py. Run: python3 agent/test_review_queue.py"""
import unittest

import review_queue as rq


def pr(n, branch="agent/5-x", sha="abc", checks=("SUCCESS",), comments=(), files=("projects/p/app.py",),
       body="Closes #5", draft=False):
    return {"number": n, "title": f"pr {n}", "headRefName": branch, "headRefOid": sha, "body": body,
            "isDraft": draft, "statusCheckRollup": [{"conclusion": c} for c in checks],
            "comments": [{"body": b} for b in comments], "files": [{"path": f} for f in files]}


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


class Protected(unittest.TestCase):
    def test_automation_paths_are_protected(self):
        self.assertEqual(rq.protected(["agent/budget.py", "scripts/x.sh", ".github/workflows/deploy-pages.yml",
                                       "CLAUDE.md", "projects/p/a.py", ".github/workflows/artysci-dla-szkol-ci.yml"]),
                         ["agent/budget.py", "scripts/x.sh", ".github/workflows/deploy-pages.yml", "CLAUDE.md"])


class Models(unittest.TestCase):
    def test_security_always_opus(self):
        self.assertEqual(rq.review_model({"area:security", "model:opus"}), ("opus", None))

    def test_opus_built_reviewed_by_sonnet(self):
        self.assertEqual(rq.review_model({"model:opus"}), ("sonnet", None))

    def test_default_prefers_opus(self):
        self.assertEqual(rq.review_model({"model:pirx"}), ("opus", "sonnet"))


class Queue(unittest.TestCase):
    def test_only_agent_branches_oldest_first(self):
        q = rq.queue([pr(9), pr(3, branch="feature/x"), pr(4, branch="agent-setup/y")], lambda p: set())
        self.assertEqual([t["pr"] for t in q], [4, 9])


if __name__ == "__main__":
    unittest.main()
