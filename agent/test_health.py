import unittest
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


if __name__ == "__main__":
    unittest.main()
