#!/usr/bin/env python3
"""Tests for budget.py. Run: python3 agent/test_budget.py"""
import unittest
from datetime import datetime, timedelta, timezone

import budget

NOW = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def plan(five_used, five_left, weekly_used=10, weekly_left=timedelta(days=3, hours=12)):
    five = {"label": "5-hour limit", "percentUsed": five_used}
    if five_left is not None:
        five["resetsAt"] = iso(NOW + five_left)
    return {"status": "ok", "windows": [
        five,
        {"label": "Weekly · all models", "percentUsed": weekly_used, "resetsAt": iso(NOW + weekly_left)},
    ]}


class FiveHourPace(unittest.TestCase):
    def test_fresh_window_allows_the_buffer(self):
        r = budget.decide(plan(10, timedelta(hours=5)), NOW)
        self.assertEqual(r["five_hour_allowed_now"], 20)
        self.assertEqual(r["decision"], "RUN")

    def test_early_in_window_and_ahead_of_pace_waits(self):
        # 1 h in: allowed 80 * 0.2 + 20 = 36
        r = budget.decide(plan(40, timedelta(hours=4)), NOW)
        self.assertEqual(r["five_hour_allowed_now"], 36)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("ahead of pace", r["reason"])

    def test_late_in_window_allows_up_to_cap(self):
        r = budget.decide(plan(70, timedelta(minutes=30)), NOW)
        self.assertEqual(r["five_hour_allowed_now"], 80)
        self.assertEqual(r["decision"], "RUN")

    def test_no_open_window_runs(self):
        r = budget.decide(plan(0, None), NOW)
        self.assertEqual(r["decision"], "RUN")

    def test_hard_cap_still_applies(self):
        r = budget.decide(plan(85, timedelta(minutes=5)), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("cap 80", r["reason"])


class WeeklyPace(unittest.TestCase):
    def test_halfway_through_week(self):
        # 3.5 days in: allowed 80 * 0.5 + 5 = 45
        self.assertEqual(budget.decide(plan(0, timedelta(hours=5), 44), NOW)["decision"], "RUN")
        r = budget.decide(plan(0, timedelta(hours=5), 46), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertEqual(r["weekly_allowed_now"], 45)


if __name__ == "__main__":
    unittest.main()
