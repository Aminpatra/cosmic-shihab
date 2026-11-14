"""The ranking endpoints, on the real data. Run from backend/: python -m unittest discover -s tests -v"""

import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def get(**params):
    return client.get("/api/rank", params=params)


class RankingApi(unittest.TestCase):
    def test_rank_answers_with_notice_method_and_echo(self):
        body = get(oxygen=0.21, fuel="methanol").json()
        self.assertEqual(body["notice"], "A relevance score shows how closely NASA's tests match this "
                                         "scenario. It is not a safety assessment.")
        self.assertEqual(body["scenario"], {"oxygen": 0.21, "fuel": "methanol"})
        self.assertEqual(body["items"][0]["accession"], "PSI-69")
        self.assertIn("tolerances", body["method"])

    def test_empty_scenario_is_200_with_message(self):
        response = get()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual((body["items"], body["message"]), ([], "Set at least one condition to rank."))

    def test_weights_come_from_query(self):
        a = get(oxygen=0.21, flow_velocity=20, weight_flow_velocity=0).json()
        b = get(oxygen=0.21).json()
        self.assertEqual([i["score"] for i in a["items"]], [i["score"] for i in b["items"]])
        self.assertEqual(a["method"]["weights"], {"oxygen": 1.0})

    def test_out_of_range_inputs_are_422(self):
        for params in [{"oxygen": 1.5}, {"pressure": -1}, {"flow_velocity": -3}, {"weight_oxygen": -1},
                       {"environment": "venus"}, {"fuel_phase": "plasma"},
                       {"environment": "lunar", "gravity_g": 0.5}]:  # Review Focus 5
            self.assertEqual(get(**params).status_code, 422, params)

    def test_custom_gravity(self):
        self.assertIsNone(get(environment="custom", oxygen=0.21).json()["gravity_note"])
        self.assertIn("0.5 g", get(environment="custom", gravity_g=0.5, oxygen=0.21).json()["gravity_note"])

    def test_options_come_from_the_data(self):
        body = client.get("/api/rank/options").json()
        self.assertEqual(body["variables"]["oxygen"],
                         {"unit": "mole fraction", "min": 0.12, "max": 0.85, "rows": 1147})
        names = [f["name"] for f in body["fuels"]]
        self.assertIn("pmma", names)
        self.assertIn("ethylene", names)
        self.assertEqual(body["environments"], {"spacecraft": 0.0, "lunar": 0.17, "mars": 0.38})


if __name__ == "__main__":
    unittest.main()
