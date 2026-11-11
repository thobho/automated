#!/usr/bin/env python3
"""Tests for agent/pick_task.py. Run: python3 agent/test_pick_task.py"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pick_task  # noqa: E402


def issue(n, state="todo", body="", extra_labels=(), milestone=None, project="x"):
    labels = [{"name": f"agent:{state}"}, {"name": f"project:{project}"}] + [{"name": l} for l in extra_labels]
    return {"number": n, "title": f"task {n}", "body": body, "labels": labels,
            "milestone": {"title": milestone} if milestone else None}


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


class Ordering(unittest.TestCase):
    def test_priority_then_milestone_then_unblocks_then_age(self):
        issues = [
            issue(1, milestone="M2"),
            issue(2, milestone="M1"),
            issue(3, milestone="M1"),
            issue(4, milestone="M1", extra_labels=["priority:high"]),
            issue(5),
            issue(6, milestone="M10"),
            issue(7, body="Depends on #9", milestone="M1"),
            issue(8, body="Depends on: #3", milestone="M3"),
            issue(9, milestone="M1"),
        ]
        q = pick_task.build_queue(issues, lambda n: False, set())
        # #4 high priority; M1: #3 and #9 unblock one each (3 < 9), then #2; then M2, M3, M10, none.
        self.assertEqual(ready(q), [4, 3, 9, 2, 1, 6, 5])
        self.assertEqual(next(t for t in q if t["number"] == 3)["unblocks"], 1)


class Executors(unittest.TestCase):
    def test_model_routes_to_executor(self):
        q = pick_task.build_queue([issue(1, extra_labels=["model:pirx"]), issue(2, extra_labels=["model:opus"]),
                                   issue(3, body="Model: haiku"), issue(4)], lambda n: False, set())
        got = {t["number"]: (t["executor"], t["model"]) for t in q}
        self.assertEqual(got, {1: ("opencode", "pirx"), 2: ("claude", "opus"),
                               3: ("claude", "haiku"), 4: ("claude", "sonnet")})

    def test_template_model_line_is_read(self):
        q = pick_task.build_queue([issue(1, body="**Model:** pirx <!-- haiku = small -->")], lambda n: False, set())
        self.assertEqual(q[0]["model"], "pirx")

    def test_security_never_goes_to_pirx(self):
        q = pick_task.build_queue([issue(1, extra_labels=["model:pirx", "area:security"])], lambda n: False, set())
        self.assertEqual((q[0]["executor"], q[0]["model"]), ("claude", "sonnet"))

    def test_next_task_filters_by_executor(self):
        q = pick_task.build_queue([issue(1, extra_labels=["model:pirx"]), issue(2)], lambda n: False, set())
        self.assertEqual(pick_task.next_task(q, "opencode")["number"], 1)
        self.assertEqual(pick_task.next_task(q, "claude")["number"], 2)
        self.assertEqual(pick_task.next_task(q)["number"], 1)

    def test_spillover_only_when_no_claude_task(self):
        q = pick_task.build_queue([issue(1, extra_labels=["model:pirx"])], lambda n: False, set())
        self.assertIsNone(pick_task.next_task(q, "claude"))
        t = pick_task.next_task(q, "claude", spillover=True)
        self.assertEqual((t["number"], t["executor"], t["model"], t["spillover"]), (1, "claude", "sonnet", True))
        q = pick_task.build_queue([issue(1, extra_labels=["model:pirx"]), issue(2)], lambda n: False, set())
        self.assertEqual(pick_task.next_task(q, "claude", spillover=True)["number"], 2)


class ReviewLimit(unittest.TestCase):
    def test_todos_wait_while_reviews_pile_up(self):
        reviews = [issue(n, "review") for n in range(10, 15)]
        issues = reviews + [issue(1), issue(2, "doing"), issue(3, project="other")]
        q = pick_task.build_queue(issues, lambda n: False, set())
        self.assertEqual(ready(q), [2, 3])
        self.assertEqual(pick_task.status_text(next(t for t in q if t["number"] == 1)), "waits on reviews")

    def test_four_reviews_still_allow_work(self):
        issues = [issue(n, "review") for n in range(10, 14)] + [issue(1)]
        self.assertEqual(ready(pick_task.build_queue(issues, lambda n: False, set())), [1])


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
