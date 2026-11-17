#!/usr/bin/env python3
"""Tests for heal.py. Run: python3 agent/test_heal.py"""
import unittest

import heal


class Track(unittest.TestCase):
    def test_problem_is_diagnosed_after_three_runs_then_waits(self):
        s, t = {}, 100000.0
        self.assertEqual(heal.track(s, ["unit:a"], t), (["unit:a"], []))
        self.assertEqual(heal.track(s, ["unit:a"], t), ([], []))
        self.assertEqual(heal.track(s, ["unit:a"], t), ([], ["unit:a"]))
        s["diagnosed"]["unit:a"] = t
        self.assertEqual(heal.track(s, ["unit:a"], t + 3600), ([], []))
        self.assertEqual(heal.track(s, ["unit:a"], t + 7 * 3600), ([], ["unit:a"]))

    def test_fixed_problem_starts_again_from_one(self):
        s = {}
        heal.track(s, ["disk"], 0)
        heal.track(s, ["disk"], 0)
        heal.track(s, [], 0)
        self.assertEqual(heal.track(s, ["disk"], 0), (["disk"], []))


def issue(n, labels=("agent:doing",), updated="2026-11-17T08:00:00Z"):
    return {"number": n, "labels": [{"name": l} for l in labels], "updated_at": updated}


class Stuck(unittest.TestCase):
    now = 1794909600.0  # 2026-11-17T12:00:00Z

    def test_unclaimed_old_doing_issue_is_stuck(self):
        self.assertEqual(heal.stuck([issue(5)], set(), self.now), [5])

    def test_claimed_recent_or_other_issues_are_not(self):
        issues = [issue(5), issue(6, updated="2026-11-17T11:30:00Z"), issue(7, labels=("agent:todo",)),
                  dict(issue(8), pull_request={})]
        self.assertEqual(heal.stuck(issues, {"5"}, self.now), [])


class Money(unittest.TestCase):
    def test_alert_near_the_limit(self):
        self.assertIn("$1.50 left", heal.money("app", {"data": {"limit": 10, "limit_remaining": 1.5}}))
        self.assertIn("app", heal.money("app", {"data": {"limit": 50, "limit_remaining": 4}}))

    def test_no_alert_with_room_or_without_a_limit(self):
        self.assertIsNone(heal.money("app", {"data": {"limit": 50, "limit_remaining": 30}}))
        self.assertIsNone(heal.money("app", {"data": {"limit": None, "limit_remaining": None}}))


if __name__ == "__main__":
    unittest.main()
