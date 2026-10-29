import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_sources  # noqa: E402

HEAD = "id,title,publisher,url,indicator_or_table_code,accessed,type,notes\n"
SRC = HEAD + "S1,t,p,https://x.example,c,2026-10-28,primary,\n"


def make(root, sources=SRC, data="year,source_id\n2000,S1\n", report="cites [S1]\n"):
    root = Path(root)
    (root / "data" / "processed").mkdir(parents=True)
    (root / "reports").mkdir()
    (root / "sources.csv").write_text(sources)
    (root / "data" / "processed" / "x.csv").write_text(data)
    (root / "reports" / "r.md").write_text(report)


class CheckSources(unittest.TestCase):
    def run_check(self, **kw):
        with tempfile.TemporaryDirectory() as d:
            make(d, **kw)
            return check_sources.main(d)

    def test_ok(self):
        self.assertEqual(self.run_check(), 0)

    def test_empty_source_id(self):
        self.assertEqual(self.run_check(data="year,source_id\n2000,\n"), 1)

    def test_unknown_source_id(self):
        self.assertEqual(self.run_check(data="year,source_id\n2000,S9\n"), 1)

    def test_multi_source_ok_and_partial_unknown(self):
        self.assertEqual(self.run_check(data="year,source_id\n2000,S1;S1\n"), 0)
        self.assertEqual(self.run_check(data="year,source_id\n2000,S1;S9\n"), 1)

    def test_missing_column_in_processed(self):
        self.assertEqual(self.run_check(data="year\n2000\n"), 1)

    def test_unknown_report_citation(self):
        self.assertEqual(self.run_check(report="see [S7]\n"), 1)

    def test_unused_source_fails(self):
        src = SRC + "S2,t,p,https://y.example,c,2026-10-28,primary,\n"
        self.assertEqual(self.run_check(sources=src), 1)
        self.assertEqual(self.run_check(sources=src, report="cites [S1] and [S2]\n"), 0)
        self.assertEqual(self.run_check(sources=src, data="year,source_id\n2000,S1;S2\n"), 0)

    def test_generated_reports_do_not_count_as_use(self):
        src = SRC + "S2,t,p,https://y.example,c,2026-10-28,primary,\n"
        with tempfile.TemporaryDirectory() as d:
            make(d, sources=src)
            (Path(d) / "reports" / "bibliography.md").write_text("**[S2]** listed\n")
            self.assertEqual(check_sources.main(d), 1)


class FinalReportLint(unittest.TestCase):
    KNOWN = {"S1", "S2"}

    def lint(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "final-report.md"
            p.write_text(text)
            return check_sources.check_final_report(p, self.KNOWN)

    def test_number_needs_key(self):
        self.assertEqual(self.lint("Population fell 2.4% [S1].\n"), [])
        self.assertEqual(len(self.lint("Population fell 2.4%.\n")), 1)

    def test_exempt_lines(self):
        text = ("# Heading 12\n\n|---|---|\n```\n3.5 in code\n```\n<!-- 7 -->\n"
                "Year 2000 and code `x1` and ilc_lvho01 and EU-27 and section 3 need nothing.\n")
        self.assertEqual(self.lint(text), [])

    def test_unknown_key(self):
        self.assertEqual(len(self.lint("Fell 2.4% [S9].\n")), 1)

    def test_derived_needs_defined_d_key(self):
        defs = "| D1 | change % | (end - start) / start | S1 |\n"
        self.assertEqual(self.lint(defs + "Fell 2.4% (derived, D1) [S1].\n"), [])
        self.assertEqual(len(self.lint(defs + "Fell 2.4% (derived) [S1].\n")), 1)
        self.assertEqual(len(self.lint("Fell 2.4% (derived, D5) [S1].\n")), 1)

    def test_main_runs_lint_when_report_exists(self):
        with tempfile.TemporaryDirectory() as d:
            make(d)
            (Path(d) / "reports" / "final-report.md").write_text("Bare 12.5 number.\n")
            self.assertEqual(check_sources.main(d), 1)


if __name__ == "__main__":
    unittest.main()
