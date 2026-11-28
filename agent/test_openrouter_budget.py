#!/usr/bin/env python3
"""Tests for openrouter_budget.py. Run: python3 agent/test_openrouter_budget.py"""
import unittest
from datetime import datetime, timezone

import openrouter_budget as ob


def key(today, month=None, limit_remaining=None, limit=None):
    return {"data": {"usage_daily": today, "usage_monthly": today if month is None else month,
                     "limit": limit, "limit_remaining": limit_remaining}}


NOW = datetime(2026, 11, 28, 12, 0, tzinfo=timezone.utc)


class Daily(unittest.TestCase):
    def test_fresh_day_gives_a_full_task(self):
        r = ob.decide(key(0.0, month=3.0), NOW)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(r["task_budget_usd"], 0.5)
        self.assertEqual(r["daily_budget_usd"], 0.5)

    def test_task_budget_is_what_is_left_today(self):
        r = ob.decide(key(0.32, month=3.0), NOW)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(r["task_budget_usd"], 0.18)

    def test_daily_budget_used_waits(self):
        r = ob.decide(key(0.47, month=3.0), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("daily budget used", r["reason"])

    def test_no_monthly_pacing_any_more(self):
        # Early in the month with a lot already spent: the old pace gate would wait, the daily cap does not.
        r = ob.decide(key(0.0, month=6.0), datetime(2026, 11, 3, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(r["decision"], "RUN")

    def test_missing_daily_usage_waits(self):
        r = ob.decide({"data": {"usage_monthly": 1.0}}, NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("usage_daily", r["reason"])


class Limits(unittest.TestCase):
    def test_key_limit_nearly_used_waits(self):
        r = ob.decide(key(0.0, month=9.97, limit_remaining=0.03, limit=10), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("key limit", r["reason"])

    def test_key_limit_caps_task_budget(self):
        r = ob.decide(key(0.0, month=9.8, limit_remaining=0.2, limit=10), NOW)
        self.assertEqual(r["task_budget_usd"], 0.2)

    def test_monthly_safety_cap_waits(self):
        r = ob.decide(key(0.0, month=15.5), NOW)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("monthly safety cap", r["reason"])

    def test_key_without_limit_is_reported(self):
        self.assertFalse(ob.decide(key(0), NOW)["key_has_limit"])

    def test_bad_shape_waits(self):
        self.assertEqual(ob.decide({"error": "x"}, NOW)["decision"], "WAIT")


if __name__ == "__main__":
    unittest.main()
