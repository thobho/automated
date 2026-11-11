#!/usr/bin/env python3
"""Tests for budget.py. Run: python3 agent/test_budget.py"""
import unittest
from datetime import datetime, timedelta, timezone

import budget

NOW = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)
HALF_WEEK = timedelta(days=3, hours=12)


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def plan(five_used, five_left, weekly_used=10, weekly_left=HALF_WEEK):
    five = {"label": "5-hour limit", "percentUsed": five_used}
    if five_left is not None:
        five["resetsAt"] = iso(NOW + five_left)
    return {"status": "ok", "windows": [
        five,
        {"label": "Weekly · all models", "percentUsed": weekly_used, "resetsAt": iso(NOW + weekly_left)},
    ]}


class Base(unittest.TestCase):
    def setUp(self):
        self.saved = budget.MODEL, budget.SLOT

    def tearDown(self):
        budget.MODEL, budget.SLOT = self.saved


class FiveHourPace(Base):
    def test_fresh_window_allows_the_buffer(self):
        r = budget.decide(plan(10, timedelta(hours=5)), NOW)
        self.assertEqual(r["five_hour_allowed_now"], 15)
        self.assertEqual(r["decision"], "RUN")

    def test_early_in_window_and_ahead_of_pace_waits(self):
        # 1 h in: allowed 70 * 0.2 + 15 = 29
        r = budget.decide(plan(30, timedelta(hours=4)), NOW)
        self.assertEqual(r["five_hour_allowed_now"], 29)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("ahead of pace", r["reason"])

    def test_late_in_window_allows_up_to_cap(self):
        r = budget.decide(plan(65, timedelta(minutes=30)), NOW)
        self.assertEqual(r["five_hour_allowed_now"], 70)
        self.assertEqual(r["decision"], "RUN")

    def test_no_open_window_runs(self):
        self.assertEqual(budget.decide(plan(0, None), NOW)["decision"], "RUN")

    def test_hard_cap_still_applies(self):
        r = budget.decide(plan(72, timedelta(minutes=5)), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("cap 70", r["reason"])


class WeeklyEvenLine(Base):
    def test_halfway_through_week(self):
        # 3.5 days in: line 5 + 90 * 0.5 = 50
        r = budget.decide(plan(0, timedelta(hours=5), 49), NOW)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(r["weekly_allowed_now"], 50)
        self.assertEqual(r["weekly_headroom"], 1)
        r = budget.decide(plan(0, timedelta(hours=5), 50), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("even line", r["reason"])

    def test_week_start_allows_only_the_base(self):
        r = budget.decide(plan(0, timedelta(hours=5), 4, timedelta(days=7)), NOW)
        self.assertEqual(r["weekly_allowed_now"], 5)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(budget.decide(plan(0, timedelta(hours=5), 5, timedelta(days=7)), NOW)["decision"], "WAIT")

    def test_front_loading_is_no_longer_allowed(self):
        # The old gate allowed ~56% after 1.2 days; the even line allows 5 + 90 * 1.2/7 = 20.4.
        r = budget.decide(plan(0, timedelta(hours=5), 30, timedelta(days=5.8)), NOW)
        self.assertEqual(r["weekly_allowed_now"], 20.4)
        self.assertEqual(r["decision"], "WAIT")

    def test_final_hours_open_up_to_cap(self):
        r = budget.decide(plan(0, timedelta(hours=5), 96, timedelta(hours=11)), NOW)
        self.assertEqual(r["weekly_allowed_now"], 98)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(budget.decide(plan(0, timedelta(hours=5), 98, timedelta(minutes=1)), NOW)["decision"], "WAIT")


class ModelsAndSlots(Base):
    def test_opus_needs_headroom(self):
        budget.MODEL = "opus"
        self.assertEqual(budget.decide(plan(0, timedelta(hours=5), 46), NOW)["decision"], "WAIT")  # headroom 4
        r = budget.decide(plan(0, timedelta(hours=5), 45), NOW)  # headroom 5
        self.assertEqual(r["decision"], "RUN")
        self.assertTrue(r["opus_ok"])

    def test_sonnet_runs_with_little_headroom(self):
        r = budget.decide(plan(0, timedelta(hours=5), 46), NOW)
        self.assertEqual(r["decision"], "RUN")
        self.assertFalse(r["opus_ok"])
        self.assertFalse(r["spillover_ok"])

    def test_second_slot_needs_headroom_and_quiet_window(self):
        budget.SLOT = 2
        self.assertEqual(budget.decide(plan(10, timedelta(hours=2), 41), NOW)["decision"], "WAIT")  # headroom 9
        self.assertEqual(budget.decide(plan(10, timedelta(hours=2), 40), NOW)["decision"], "RUN")   # headroom 10
        r = budget.decide(plan(52, timedelta(minutes=30), 30), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("slot 2", r["reason"])

    def test_spillover_flag(self):
        self.assertTrue(budget.decide(plan(0, timedelta(hours=5), 40), NOW)["spillover_ok"])


if __name__ == "__main__":
    unittest.main()
