#!/usr/bin/env python3
"""Tests for openrouter_budget.py. Run: python3 agent/test_openrouter_budget.py"""
import unittest
from datetime import datetime, timezone

import openrouter_budget as ob


def key(used, limit_remaining=None, limit=10):
    return {"data": {"usage_monthly": used, "limit": limit, "limit_remaining": limit_remaining}}


# November has 30 days.
MID = datetime(2026, 11, 16, 0, 0, tzinfo=timezone.utc)      # 15 days in: 50%
START = datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)
END = datetime(2026, 11, 29, 12, 0, tzinfo=timezone.utc)     # 1.5 days left


class Pace(unittest.TestCase):
    def test_halfway_allows_half_plus_buffer(self):
        r = ob.decide(key(4.0), MID)
        self.assertEqual(r["allowed_now_usd"], 5.5)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(r["task_budget_usd"], 0.75)

    def test_ahead_of_pace_waits(self):
        r = ob.decide(key(5.4), MID)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("pace", r["reason"])

    def test_task_budget_shrinks_near_the_line(self):
        r = ob.decide(key(5.1), MID)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(r["task_budget_usd"], 0.4)

    def test_month_start_allows_the_buffer(self):
        r = ob.decide(key(0), START)
        self.assertEqual(r["decision"], "RUN")
        self.assertEqual(r["task_budget_usd"], 0.5)

    def test_final_days_have_no_pace_gate(self):
        r = ob.decide(key(8.0), END)
        self.assertFalse(r["pace_gate"])
        self.assertEqual(r["decision"], "RUN")


class Limits(unittest.TestCase):
    def test_key_limit_nearly_used_waits(self):
        r = ob.decide(key(1.0, limit_remaining=0.2), MID)
        self.assertEqual(r["decision"], "WAIT")
        self.assertIn("key limit", r["reason"])

    def test_key_limit_caps_task_budget(self):
        r = ob.decide(key(1.0, limit_remaining=0.3), MID)
        self.assertEqual(r["task_budget_usd"], 0.3)

    def test_monthly_budget_used_waits_even_at_month_end(self):
        self.assertEqual(ob.decide(key(10.0), END)["decision"], "WAIT")

    def test_key_without_limit_is_reported(self):
        self.assertFalse(ob.decide(key(0, limit=None), MID)["key_has_limit"])

    def test_bad_shape_waits(self):
        self.assertEqual(ob.decide({"error": "x"}, MID)["decision"], "WAIT")


if __name__ == "__main__":
    unittest.main()
