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


if __name__ == "__main__":
    unittest.main()
