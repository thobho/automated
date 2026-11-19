#!/usr/bin/env python3
"""Tests for metrics.py. Run: python3 agent/test_metrics.py"""
import json
import unittest

import metrics


def result(cost, ms, model="claude-opus-5-5", err=False, subtype="success"):
    return json.dumps({"type": "result", "total_cost_usd": cost, "duration_ms": ms, "is_error": err,
                       "subtype": subtype, "modelUsage": {model: {"costUSD": cost}}})


class Metrics(unittest.TestCase):
    def test_parse_run_takes_the_last_result(self):
        r = metrics.parse_run(['{"type":"system"}', result(1.0, 60000), result(2.5, 120000)])
        self.assertEqual((r["cost"], r["minutes"], r["model"], r["error"]), (2.5, 2.0, "opus", False))

    def test_parse_run_without_result(self):
        self.assertIsNone(metrics.parse_run(['{"type":"system"}']))

    def test_summarize_runs_adds_model_rows_for_builds(self):
        runs = [("claude", metrics.parse_run([result(3, 600000)])),
                ("claude", metrics.parse_run([result(1, 300000, "claude-sonnet-5-5", err=True)])),
                ("review", metrics.parse_run([result(0.5, 60000)]))]
        s = metrics.summarize_runs(runs)
        self.assertEqual(s["claude"]["runs"], 2)
        self.assertEqual(s["build:sonnet"]["errors"], 1)
        self.assertEqual(s["review"]["cost"], 0.5)

    def test_summarize_prs(self):
        prs = [{"createdAt": "2026-11-18T10:00:00Z", "mergedAt": "2026-11-18T12:00:00Z", "comments": []},
               {"createdAt": "2026-11-18T10:00:00Z", "mergedAt": "2026-11-18T16:00:00Z",
                "comments": [{"body": "x <!-- automated:review-changes -->"}]}]
        s = metrics.summarize_prs(prs)
        self.assertEqual((s["merged"], s["first_pass"], s["median_hours"], s["returns"]), (2, 50, 4.0, 1))

    def test_render(self):
        out = metrics.render({"prs": {"merged": 0}, "runs": {"claude": {"runs": 1, "errors": 0, "median_min": 9.0,
                                                                        "cost": 3.2}}, "main": {"p": "failure"}})
        self.assertIn("p CI red", out)
        self.assertIn("| Builds (Claude) | 1 | 0 | 9.0 | $3.20 |", out)


if __name__ == "__main__":
    unittest.main()
