"""The FLEX model results endpoint, checked against the committed backend/data/flex_model/results.json.

The checks are on shape and internal consistency, never on how good the model is. Run from
backend/: python -m unittest discover -s tests -v
"""

import unittest

from fastapi.testclient import TestClient

from app import flex_model
from main import app

client = TestClient(app)
CLASSES = ["Extinction", "Disruption", "Completion"]


class FlexModelApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response = client.get("/api/flex-model")
        cls.body = cls.response.json()

    def test_serves_the_stored_results_with_the_notice(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("not a prediction of a real fire", self.body["notice"])
        self.assertEqual(self.body["classes"], CLASSES)

    def test_counts_add_up(self):
        data, split = self.body["data"], self.body["split"]
        self.assertEqual(data["tests"], 274)
        self.assertEqual(sum(data["tests_by_end"].values()), 274)
        self.assertEqual(split["train_tests"] + split["held_out_tests"], 274)
        self.assertEqual(split["train_days"] + split["held_out_days"], data["test_days"])

    def test_chosen_model_is_scored_beside_the_baseline(self):
        chosen = self.body["chosen_model"]
        self.assertNotEqual(chosen, "baseline")
        self.assertIn(chosen, self.body["cross_validation"]["scores"])
        for name in ("baseline", chosen):
            self.assertTrue(0 <= self.body["held_out"][name]["macro_f1"] <= 1)

    def test_confusion_matrices_match_the_held_out_tests(self):
        expected = [self.body["split"]["held_out_tests_by_end"][c] for c in CLASSES]
        for name, report in self.body["held_out"].items():
            self.assertEqual(report["confusion_matrix"]["labels"], CLASSES)
            self.assertEqual([sum(row) for row in report["confusion_matrix"]["matrix"]], expected, name)

    def test_shap_covers_every_end_and_feature(self):
        features = {f["name"] for f in self.body["features"]}
        self.assertEqual(set(self.body["shap"]["by_end"]), set(CLASSES))
        for items in self.body["shap"]["by_end"].values():
            self.assertEqual({i["feature"] for i in items}, features)

    def test_no_input_was_measured_during_the_test(self):
        inputs = {f["psi_column"] for f in self.body["features"]}
        outcomes = {e["psi_column"] for e in self.body["excluded"] if "outcome" in e["reason"]}
        self.assertEqual(len(outcomes), 3)
        self.assertEqual(inputs & outcomes, set())

    def test_chance_check_and_limitations_are_served(self):
        check = self.body["chance_check"]
        self.assertTrue(check["smallest_possible_p"] <= check["p_value"] <= 1)
        self.assertEqual(check["smallest_possible_p"], round(1 / (1 + check["shuffles"]), 3))
        self.assertTrue(any("completions" in note for note in self.body["limitations"]))

    def test_missing_results_are_a_clear_503(self):
        saved, flex_model.RESULTS = flex_model.RESULTS, flex_model.RESULTS.with_name("absent.json")
        try:
            response = client.get("/api/flex-model")
        finally:
            flex_model.RESULTS = saved
        self.assertEqual(response.status_code, 503)
        self.assertIn("train_flex_model", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
