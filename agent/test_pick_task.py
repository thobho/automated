#!/usr/bin/env python3
"""Tests for agent/pick_task.py. Run: python3 agent/test_pick_task.py"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pick_task  # noqa: E402


def issue(n, state="todo", body="", extra_labels=()):
    labels = [{"name": f"agent:{state}"}, {"name": "project:x"}] + [{"name": l} for l in extra_labels]
    return {"number": n, "title": f"task {n}", "body": body, "labels": labels}


def ready(queue):
    return [t["number"] for t in queue if t["ready"]]


class Resources(unittest.TestCase):
    def test_parses_uses_lines(self):
        body = "Build it.\nUses: GUS-BDL, `playwright`\nuses: eurostat <!-- note -->"
        self.assertEqual(pick_task.resources(body), {"gus-bdl", "playwright", "eurostat"})

    def test_no_uses(self):
        self.assertEqual(pick_task.resources("Mentions uses: in the middle"), set())
        self.assertEqual(pick_task.resources(None), set())


class Queue(unittest.TestCase):
    def test_without_claims_doing_comes_first(self):
        q = pick_task.build_queue([issue(12), issue(6, "doing")], lambda n: False, set())
        self.assertEqual(ready(q), [6, 12])

    def test_claimed_issue_is_running_not_ready(self):
        q = pick_task.build_queue([issue(12), issue(6, "doing")], lambda n: False, {6})
        self.assertEqual(ready(q), [12])
        self.assertEqual(pick_task.status_text(q[0]), "running")

    def test_shared_resource_waits(self):
        issues = [issue(6, "doing", "Uses: gus-bdl"), issue(7, body="Uses: gus-bdl, eurostat"),
                  issue(12), issue(13, body="Uses: osm")]
        q = pick_task.build_queue(issues, lambda n: False, {6})
        self.assertEqual(ready(q), [12, 13])
        seven = next(t for t in q if t["number"] == 7)
        self.assertEqual(seven["resource_busy"], ["gus-bdl"])
        self.assertEqual(pick_task.status_text(seven), "waits on gus-bdl")

    def test_resource_free_when_holder_not_claimed(self):
        issues = [issue(6, "doing", "Uses: gus-bdl"), issue(7, body="Uses: gus-bdl")]
        self.assertEqual(ready(pick_task.build_queue(issues, lambda n: False, set())), [6, 7])

    def test_dependencies_still_apply(self):
        issues = [issue(10, body="Depends on: #9"), issue(9, "review")]
        q = pick_task.build_queue(issues, lambda n: False, set())
        self.assertEqual(ready(q), [])
        self.assertEqual(pick_task.status_text(q[0]), "waits on #9")


class Claims(unittest.TestCase):
    def run_script(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
            f.write(text)
        old = pick_task.LOCK_SCRIPT
        pick_task.LOCK_SCRIPT = f.name
        try:
            return pick_task.claimed_issues()
        finally:
            pick_task.LOCK_SCRIPT = old
            os.unlink(f.name)

    def test_reads_claims(self):
        self.assertEqual(self.run_script("echo 6; echo 12\n"), {6, 12})

    def test_old_script_without_claimed_means_no_claims(self):
        self.assertEqual(self.run_script("echo usage >&2; exit 64\n"), set())

    def test_missing_script_means_no_claims(self):
        old = pick_task.LOCK_SCRIPT
        pick_task.LOCK_SCRIPT = "/nonexistent/worker-lock.sh"
        try:
            self.assertEqual(pick_task.claimed_issues(), set())
        finally:
            pick_task.LOCK_SCRIPT = old


if __name__ == "__main__":
    unittest.main()
