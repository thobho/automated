import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import check_report

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    def test_real_report_is_consistent(self):
        errs, rows, cited = check_report.check((ROOT / "report.md").read_text(), (ROOT / "sources.md").read_text())
        self.assertEqual(errs, [])
        self.assertGreaterEqual(len(rows), 50)

    def test_detects_unknown_citation(self):
        errs, _, _ = check_report.check("see [S9]", "| S1 | a | http://x | y | 2026-10-28 |")
        self.assertTrue(any("S9" in e for e in errs))

    def test_matrix_in_report_matches_scoring_script(self):
        import scoring
        text = (ROOT / "report.md").read_text()
        for total, name in scoring.ranking():
            self.assertIn(f"| {name} |", text)
            self.assertIn(f"| {total:.0f} |", text)


if __name__ == "__main__":
    unittest.main()
