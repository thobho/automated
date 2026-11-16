#!/usr/bin/env python3
"""Tests for usage_probe.py. Run: python3 agent/test_usage_probe.py"""
import json
import unittest
from datetime import datetime, timezone

import budget
import usage_probe as up

EVENT = {"type": "rate_limit_event", "rate_limit_info": {
    "status": "allowed", "resetsAt": 1794793200, "rateLimitType": "five_hour",
    "unifiedWindows": {"five_hour": {"utilization": 0.1, "resetsAt": 1794793200, "status": "allowed"},
                       "seven_day": {"utilization": 0.22, "resetsAt": 1795118400, "status": "allowed"}}}}


class Parse(unittest.TestCase):
    def test_event_becomes_get_usage_shape(self):
        u = up.to_usage(EVENT["rate_limit_info"])
        five, week = u["plan"]["windows"]
        self.assertEqual((five["label"], five["percentUsed"]), ("5-hour limit", 10.0))
        self.assertEqual((week["label"], week["percentUsed"]), ("Weekly · all models", 22.0))
        self.assertTrue(five["resetsAt"].endswith("Z"))

    def test_last_event_wins_and_noise_is_ignored(self):
        later = json.loads(json.dumps(EVENT))
        later["rate_limit_info"]["unifiedWindows"]["seven_day"]["utilization"] = 0.3
        lines = ["not json", json.dumps({"type": "assistant"}), json.dumps(EVENT), json.dumps(later)]
        self.assertEqual(up.to_usage(up.last_event(lines))["plan"]["windows"][1]["percentUsed"], 30.0)

    def test_event_without_windows_is_skipped(self):
        bad = {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed"}}
        self.assertIsNone(up.last_event([json.dumps(bad)]))

    def test_budget_reads_the_probe_output(self):
        u = up.to_usage(EVENT["rate_limit_info"])
        now = datetime.fromtimestamp(1794793200 - 4 * 3600, timezone.utc)  # 1 h into the 5-hour window
        r = budget.decide(u["plan"], now)
        self.assertIn(r["decision"], ("RUN", "WAIT"))
        self.assertEqual(r["five_hour_used"], 10.0)
        self.assertEqual(r["weekly_used"], 22.0)


if __name__ == "__main__":
    unittest.main()
