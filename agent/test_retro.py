#!/usr/bin/env python3
"""Tests for retro.py. Run: python3 agent/test_retro.py"""
import unittest

import retro

REVIEW = """🔎 **AI review (opus, `abc1234`): 🔁 changes requested**

Summary here.

**Must change:**
1. `apps/x/views.py`: no permission check on the delete view → add the artist owner check and a test.
2. migration 0007 drops a column without a data step → split it.

**Notes:**
- minor naming
"""


class Retro(unittest.TestCase):
    def test_review_points(self):
        pts = retro.review_points(REVIEW)
        self.assertEqual(len(pts), 2)
        self.assertTrue(pts[0].startswith("`apps/x/views.py`"))

    def test_approval_has_no_points(self):
        self.assertEqual(retro.review_points("🔎 **AI review: ✅ approved**\n\n**Must change:**\n1. x"), [])

    def test_other_findings(self):
        body = "❌ pytest failed in apps/a, tried twice\nother line\n↩️ Back to the builder: CI is red. See PR #3."
        self.assertEqual(len(retro.other_findings(body)), 2)

    def test_project_of(self):
        self.assertEqual(retro.project_of(["projects/a/x.py"]), "a")
        self.assertEqual(retro.project_of([], ["project:b", "agent:todo"]), "b")
        self.assertEqual(retro.project_of(["agent/x.py"]), "automation")

    def test_only_the_automation_account_counts(self):
        self.assertTrue(retro.trusted({"author": {"login": "bot"}}, {"bot"}))
        self.assertFalse(retro.trusted({"author": {"login": "stranger"}}, {"bot"}))
        self.assertFalse(retro.trusted({}, {"bot"}))

    def test_secret_scan(self):
        self.assertTrue(retro.has_secret("token ghp_" + "a" * 36))
        self.assertTrue(retro.has_secret("-----BEGIN OPENSSH PRIVATE KEY-----"))
        self.assertTrue(retro.has_secret("value is s3cr3tvalue1", {"s3cr3tvalue1"}))
        self.assertFalse(retro.has_secret("Every new view gets a row in the permission matrix test."))

    def test_render(self):
        self.assertIn("## a (1)", retro.render({"a": ["PR #1: x"]}, 7))


if __name__ == "__main__":
    unittest.main()
