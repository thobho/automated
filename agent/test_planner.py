#!/usr/bin/env python3
"""Tests for agent/planner.py. Run: python3 agent/test_planner.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import planner  # noqa: E402

ROADMAP = """# Roadmap

## M1 First product features
- US-1.1: Artist registration
- US-1.2: Public artist page (depends: US-1.1)
- **US-1.3**: Catalog search (depends on: US-1.2)
- US-1.4 - Inquiries (depends: US-1.2, US-1.3)
- US-1.5: Notices

## M2 Growth
- US-2.1: Reviews

Not a story line.
"""


def issue(body="", labels=()):
    return {"number": 1, "body": body, "labels": [{"name": l} for l in labels]}


class Parse(unittest.TestCase):
    def test_stories_milestones_and_dependencies(self):
        s = planner.parse_roadmap(ROADMAP)
        self.assertEqual([x["id"] for x in s][:6], ["US-1.1", "US-1.2", "US-1.3", "US-1.4", "US-1.5", "US-2.1"])
        by = {x["id"]: x for x in s}
        self.assertEqual(by["US-1.1"]["milestone"], "M1")
        self.assertEqual(by["US-1.1"]["milestone_title"], "First product features")
        self.assertEqual(by["US-1.2"]["depends"], ["US-1.1"])
        self.assertEqual(by["US-1.2"]["title"], "Public artist page")
        self.assertEqual(by["US-1.3"]["depends"], ["US-1.2"])
        self.assertEqual(by["US-1.4"]["depends"], ["US-1.2", "US-1.3"])
        self.assertEqual(by["US-2.1"]["milestone"], "M2")

    def test_story_before_any_milestone_is_ignored(self):
        self.assertEqual(planner.parse_roadmap("- US-0.1: orphan\n## M1 x\n- US-1.1: a"),
                         [{"id": "US-1.1", "title": "a", "milestone": "M1", "milestone_title": "x", "depends": []}])

    def test_empty(self):
        self.assertEqual(planner.parse_roadmap(""), [])
        self.assertEqual(planner.parse_roadmap(None), [])


class Planned(unittest.TestCase):
    def test_story_lines(self):
        issues = [issue("**Project:** x\n\n**Story:** US-1.1, us-1.2\n**Goal:** y"),
                  issue("Story: US-2.1"), issue("Mentions US-3.1 in prose only")]
        self.assertEqual(planner.planned_ids(issues), {"US-1.1", "US-1.2", "US-2.1"})

    def test_backlog_counts_todo_and_doing_only(self):
        issues = [issue(labels=["agent:todo"]), issue(labels=["agent:doing"]),
                  issue(labels=["agent:review"]), issue(labels=["agent:blocked"]), issue(labels=["agent:done"])]
        self.assertEqual(planner.backlog_size(issues), 2)

    def test_backlog_skips_todo_waiting_on_an_open_issue(self):
        t29 = dict(issue(labels=["agent:review"]), number=140, state="OPEN")
        t30 = dict(issue("Depends on: #140", ["agent:todo"]), number=141, state="OPEN")
        t31 = dict(issue("**Depends on:** #141", ["agent:todo"]), number=142, state="OPEN")
        old = dict(issue("Depends on: #9", ["agent:todo"]), number=143, state="OPEN")
        doing = dict(issue("Depends on: #140", ["agent:doing"]), number=144, state="OPEN")
        self.assertEqual(planner.backlog_size([t29, t30, t31]), 0)
        self.assertEqual(planner.backlog_size([t29, t30, t31, old, doing]), 2)

    def test_backlog_ignores_closed_done_and_other_projects(self):
        closed = dict(issue(labels=["agent:todo", "project:a"]), state="CLOSED")
        stale = issue(labels=["agent:todo", "agent:done", "project:a"])
        other = issue(labels=["agent:todo", "project:b"])
        mine = dict(issue(labels=["agent:todo", "project:a"]), state="OPEN")
        self.assertEqual(planner.backlog_size([closed, stale, other, mine], "a"), 1)
        self.assertEqual(planner.backlog_size([closed, stale, other, mine], "b"), 1)
        self.assertEqual(planner.backlog_size([closed, stale, other, mine]), 2)


class Decide(unittest.TestCase):
    def setUp(self):
        self.stories = planner.parse_roadmap(ROADMAP)
        self.now = 1_000_000.0

    def d(self, planned=(), backlog=0, last=None, **kw):
        return planner.decide(self.stories, set(planned), backlog, last, self.now, **kw)

    def test_no_roadmap_asks_the_owner(self):
        r = planner.decide([], set(), 0, None, self.now)
        self.assertEqual(r["action"], "NEED_ROADMAP")

    def test_plans_dependency_ordered_batch_from_earliest_milestone(self):
        r = self.d(max_new=4)
        self.assertEqual(r["action"], "PLAN")
        # US-1.1 has no deps; US-1.2 needs 1.1 (chosen earlier in the batch); 1.3 needs 1.2; 1.4 needs 1.2+1.3
        self.assertEqual([s["id"] for s in r["stories"]], ["US-1.1", "US-1.2", "US-1.3", "US-1.4"])

    def test_batch_is_capped(self):
        r = self.d(max_new=2)
        self.assertEqual([s["id"] for s in r["stories"]], ["US-1.1", "US-1.2"])

    def test_skips_planned_stories_and_never_leaves_the_milestone(self):
        r = self.d(planned=["US-1.1", "US-1.2", "US-1.3", "US-1.4"])
        self.assertEqual([s["id"] for s in r["stories"]], ["US-1.5"])
        self.assertEqual(r["stories"][0]["milestone"], "M1")

    def test_moves_to_next_milestone_when_the_first_is_fully_planned(self):
        r = self.d(planned=["US-1.1", "US-1.2", "US-1.3", "US-1.4", "US-1.5"])
        self.assertEqual([s["id"] for s in r["stories"]], ["US-2.1"])

    def test_everything_planned(self):
        r = self.d(planned=[s["id"] for s in self.stories])
        self.assertEqual(r["action"], "SKIP")
        self.assertIn("already planned", r["reason"])

    def test_busy_backlog_skips(self):
        self.assertEqual(self.d(backlog=2)["action"], "SKIP")
        self.assertEqual(self.d(backlog=1)["action"], "PLAN")

    def test_cooldown(self):
        recent = self.now - 3600
        self.assertEqual(self.d(last=recent)["action"], "SKIP")
        old = self.now - 7 * 3600
        self.assertEqual(self.d(last=old)["action"], "PLAN")

    def test_dependency_outside_the_roadmap_blocks_planning(self):
        stories = planner.parse_roadmap("## M1 x\n- US-1.1: a (depends: US-0.9)\n")
        r = planner.decide(stories, set(), 0, None, self.now)
        self.assertEqual(r["action"], "SKIP")
        self.assertIn("dependencies", r["reason"])

    def test_a_dependency_planned_in_an_earlier_milestone_is_fine(self):
        stories = planner.parse_roadmap("## M1 x\n- US-1.1: a\n## M2 y\n- US-2.1: b (depends: US-1.1)\n")
        r = planner.decide(stories, {"US-1.1"}, 0, None, self.now)
        self.assertEqual([s["id"] for s in r["stories"]], ["US-2.1"])


class FormatStories(unittest.TestCase):
    def test_lines_with_dependencies(self):
        d = {"stories": [{"id": "US-1.1", "title": "Artist registration", "depends": []},
                         {"id": "US-1.2", "title": "Public page", "depends": ["US-1.1", "US-0.1"]}]}
        self.assertEqual(planner.format_stories(d),
                         "- US-1.1: Artist registration (depends on stories: none)\n"
                         "- US-1.2: Public page (depends on stories: US-1.1, US-0.1)")

    def test_empty(self):
        self.assertEqual(planner.format_stories({"stories": []}), "")
        self.assertEqual(planner.format_stories({}), "")

    def test_cli_prints_lines_and_ids(self):
        import json, subprocess, tempfile
        d = {"stories": [{"id": "US-1.1", "title": "A", "depends": []}, {"id": "US-1.2", "title": "B", "depends": ["US-1.1"]}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(d, f)
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "planner.py")
        lines = subprocess.run([sys.executable, script, "--format-stories", f.name], capture_output=True, text=True)
        ids = subprocess.run([sys.executable, script, "--format-stories", f.name, "--ids"], capture_output=True, text=True)
        os.unlink(f.name)
        self.assertEqual(lines.returncode, 0, lines.stderr)
        self.assertEqual(lines.stdout.strip().splitlines()[0], "- US-1.1: A (depends on stories: none)")
        self.assertEqual(ids.stdout.strip(), "US-1.1 US-1.2")


class RunScript(unittest.TestCase):
    def test_no_inline_python_with_escaped_quotes(self):
        """Regression: an f-string with backslash-escaped quotes inside planner-run.sh is a SyntaxError
        on Python 3.14, which left the story list empty and the model with nothing to plan."""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pirx", "planner-run.sh")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("python3 -c", text)  # logic lives in planner.py, where it is tested
        self.assertIn("--format-stories", text)


if __name__ == "__main__":
    unittest.main()
