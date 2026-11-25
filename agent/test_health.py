import io
import json
import os
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone

import health


def issue(n, label, updated):
    return {"number": n, "title": f"t{n}", "labels": [{"name": label}], "updated_at": updated}


NOW = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc).timestamp()


class StuckTest(unittest.TestCase):
    def test_old_review_is_stuck(self):
        out = health.stuck([issue(69, "agent:review", "2026-11-16T04:13:29Z")], NOW)
        self.assertEqual(len(out), 1)
        self.assertIn("#69", out[0])
        self.assertIn("stuck in review", out[0])

    def test_recent_activity_is_fine(self):
        self.assertEqual(health.stuck([issue(1, "agent:doing", "2026-11-16T10:30:00Z")], NOW), [])

    def test_todo_and_blocked_are_not_reported_here(self):
        items = [issue(1, "agent:todo", "2026-11-01T00:00:00Z"), issue(2, "agent:blocked", "2026-11-01T00:00:00Z")]
        self.assertEqual(health.stuck(items, NOW), [])


class DevInstancesTest(unittest.TestCase):
    SPEC = "app=http://127.0.0.1:8100/readyz"

    def test_ready_instance_is_a_green_row_and_no_problem(self):
        rows, problems = health.dev_instances(self.SPEC, lambda url: {"db": "ok", "migrations": "ok"})
        self.assertEqual(rows, ["| Dev instance app | ✅ | db ok, migrations ok |"])
        self.assertEqual(problems, [])

    def test_db_error_is_a_problem(self):
        rows, problems = health.dev_instances(self.SPEC, lambda url: {"db": "error", "migrations": "ok"})
        self.assertIn("❌", rows[0])
        self.assertEqual(len(problems), 1)
        self.assertIn("db error", problems[0])
        self.assertNotIn("migrations", problems[0])

    def test_503_with_json_body_is_read(self):
        def fetch(url):
            raise urllib.error.HTTPError(url, 503, "x", {}, io.BytesIO(b'{"db": "error", "migrations": "error"}'))
        rows, problems = health.dev_instances(self.SPEC, fetch)
        self.assertIn("db error, migrations error", rows[0])
        self.assertEqual(len(problems), 1)

    def test_unreachable_is_a_problem(self):
        def fetch(url):
            raise urllib.error.URLError("refused")
        rows, problems = health.dev_instances(self.SPEC, fetch)
        self.assertEqual(rows, ["| Dev instance app | ❌ | not reachable |"])
        self.assertIn("not reachable", problems[0])

    def test_empty_spec_adds_nothing(self):
        self.assertEqual(health.dev_instances("", lambda url: {}), ([], []))


class WeekTrackerTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "claude-week.json")

    def test_previous_week_is_kept_after_the_reset(self):
        self.assertIsNone(health.track_week({"weekly_used": 80, "weekly_resets_at": "2026-11-26T20:40:00Z"}, self.path))
        self.assertIsNone(health.track_week({"weekly_used": 93, "weekly_resets_at": "2026-11-26T20:40:30Z"}, self.path))
        prev = health.track_week({"weekly_used": 2, "weekly_resets_at": "2026-12-03T20:40:00Z"}, self.path)
        self.assertEqual(prev, {"resets_at": "2026-11-26T20:40:30Z", "used": 93})
        self.assertEqual(health.track_week({"weekly_used": 5, "weekly_resets_at": "2026-12-03T20:40:00Z"}, self.path), prev)
        self.assertIn("7% expired unused", health.week_summary(prev))

    def test_missing_budget_keeps_state(self):
        health.track_week({"weekly_used": 50, "weekly_resets_at": "2026-11-26T20:40:00Z"}, self.path)
        self.assertIsNone(health.track_week({}, self.path))
        self.assertEqual(json.load(open(self.path))["last_used"], 50)
        self.assertIsNone(health.week_summary(None))


if __name__ == "__main__":
    unittest.main()
