import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import scoring


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(w for _, _, w in scoring.CRITERIA), 100)

    def test_scores_in_range_and_complete(self):
        for name, s in scoring.SCORES.items():
            self.assertEqual(len(s), len(scoring.CRITERIA), name)
            self.assertTrue(all(0 <= x <= 5 for x in s), name)

    def test_total_bounds(self):
        self.assertEqual(scoring.total([5] * 10), 100)
        self.assertEqual(scoring.total([0] * 10), 0)

    def test_at_least_8_libraries(self):
        self.assertGreaterEqual(len(scoring.SCORES), 8)

    def test_gate_failures_are_known_libraries(self):
        for k in list(scoring.GATE_FAIL) + list(scoring.MAP_ONLY):
            self.assertIn(k, scoring.SCORES)


if __name__ == "__main__":
    unittest.main()
