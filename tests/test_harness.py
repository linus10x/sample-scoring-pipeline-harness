import datetime as dt, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from momentum import contract, generate, score  # noqa: E402


class HarnessTests(unittest.TestCase):
    def test_all_blocking_checks_pass_on_reference_scorers(self):
        harness.results.clear()
        rs = harness.run()
        self.assertTrue(all(r["ok"] for r in rs if r["blocking"]))

    def test_contract_catches_each_defect_type(self):
        _, q = contract.validate(generate.inject_defects(generate.clean_rows()), harness.AS_OF)
        self.assertTrue({"duplicate_key", "negative_count", "null:followers", "bad_date", "future_date", "type:views"} <= {x["reason"] for x in q})

    def test_harness_would_catch_a_scorer_that_counts_duplicates(self):
        # A common real bug: summing raw rows without de-duplication.
        rows = generate.clean_rows()
        def leaky(rs, as_of):
            tot = {}
            for r in rs:
                tot[r["creator_id"]] = tot.get(r["creator_id"], 0) + r["engagements"]
            return tot
        self.assertNotEqual(harness.digest(leaky(rows, harness.AS_OF)), harness.digest(leaky(rows + rows[:50], harness.AS_OF)))

    def test_golden_values(self):
        g = score.score_v1(harness.golden_rows(), harness.AS_OF)
        self.assertEqual(g["g-flat"], 50.0)
        self.assertGreater(g["g-up"], 99)
        self.assertLess(g["g-drop"], 1)


if __name__ == "__main__":
    unittest.main()
