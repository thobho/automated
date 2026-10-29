import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_reference_docs as brd  # noqa: E402
import check_sources  # noqa: E402

HEAD = "id,title,publisher,url,indicator_or_table_code,accessed,type,notes\n"
SRC = (HEAD
       + 'S1,Population,GUS BDL,https://bdl.example/1,BDL subject P1336; variables 60641,2026-10-28,primary,\n'
       + 'S2,A paper,Some Journal,https://j.example/2,article 10.1/x,2026-10-29,secondary,\n'
       + 'S3,Eurostat table,Eurostat,https://es.example/3,demo_gind: JAN,2026-10-29,primary,\n')


def make(root):
    root = Path(root)
    (root / "data" / "processed").mkdir(parents=True)
    (root / "data" / "raw").mkdir()
    (root / "reports").mkdir()
    (root / "sources.csv").write_text(SRC)
    (root / "data" / "processed" / "a.csv").write_text(
        "year,value_type,source_id\n2000,derived,S1;S3\n2001,reported,S1\n")
    (root / "data" / "processed" / "b.csv").write_text("year,value_type,source_id\n2000,reported,S3\n")
    (root / "data" / "raw" / "r.csv").write_text("year,value\n2000,1\n")
    (root / "reports" / "r.md").write_text("Interpretation [S2].\n")


class ReferenceDocs(unittest.TestCase):
    def setUp(self):
        self._root = brd.ROOT
        self.tmp = tempfile.TemporaryDirectory()
        make(self.tmp.name)

    def tearDown(self):
        brd.ROOT = self._root
        self.tmp.cleanup()

    def test_short_code(self):
        self.assertEqual(brd.short_code("BDL subject P1336; variables 60641"), "BDL subject P1336")
        self.assertEqual(brd.short_code("demo_gind: JAN, GROW"), "demo_gind")
        self.assertEqual(brd.short_code("BDL subjects P2426 (60562)"), "BDL subjects P2426")
        self.assertEqual(brd.short_code("SP.URB.TOTL"), "SP.URB.TOTL")

    def test_bibliography_groups_and_lists_every_source(self):
        text = brd.build_bibliography(self.tmp.name)
        self.assertLess(text.index("## Primary sources (2)"), text.index("## Secondary sources (1)"))
        for sid in ("S1", "S2", "S3"):
            self.assertIn(f"**[{sid}]**", text)
        self.assertIn("<https://bdl.example/1> (accessed 2026-10-28)", text)
        # S2 is secondary: appears after the secondary heading
        self.assertGreater(text.index("**[S2]**"), text.index("## Secondary sources"))
        self.assertIn("Used in: reports r", text)
        self.assertIn("Used in: data a.csv", text)

    def test_caption_for_every_file_with_ids_from_the_file(self):
        text = brd.build_citation_sheet(self.tmp.name)
        for name in ("a.csv", "b.csv", "r.csv"):
            self.assertIn(f"### `{name}`", text)
        self.assertIn("> Source: GUS BDL, BDL subject P1336, accessed 2026-10-28, https://bdl.example/1;"
                      " Eurostat, demo_gind, accessed 2026-10-29, https://es.example/3. Derived values", text)
        self.assertIn("> Źródło: GUS BDL, BDL subject P1336", text)

    def test_derived_note_only_for_derived_files(self):
        text = brd.build_citation_sheet(self.tmp.name)
        b_block = text.split("### `b.csv`")[1].split("###")[0]
        self.assertNotIn("Derived values", b_block)

    def test_raw_without_source_column_is_flagged_none(self):
        text = brd.build_citation_sheet(self.tmp.name)
        self.assertIn("sources: NONE", text)

    def test_check_flag(self):
        # generate into the temp root by monkeypatching ROOT
        brd.ROOT = Path(self.tmp.name)
        self.assertEqual(brd.main(["--check"]), 1)
        self.assertEqual(brd.main([]), 0)
        self.assertEqual(brd.main(["--check"]), 0)
        (Path(self.tmp.name) / "reports" / "bibliography.md").write_text("changed")
        self.assertEqual(brd.main(["--check"]), 1)

    def test_generated_files_do_not_count_as_usage(self):
        brd.ROOT = Path(self.tmp.name)
        brd.main([])
        usage = check_sources.source_usage(self.tmp.name)
        self.assertEqual(usage["S2"]["reports"], {"r.md"})
        (Path(self.tmp.name) / "reports" / "r.md").write_text("nothing\n")
        self.assertEqual(check_sources.check_unused(self.tmp.name, {"S1", "S2", "S3"})[0][:2], "S2")


if __name__ == "__main__":
    unittest.main()
