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
                         {"unit": "mole fraction", "min": 0.12, "max": 0.85, "rows": 1147,
                          "tested": {"min": 0.12, "max": 0.85, "rows": 1147}})
        names = [f["name"] for f in body["fuels"]]
        self.assertIn("pmma", names)
        self.assertIn("ethylene", names)
        self.assertEqual(body["environments"], {"spacecraft": 0.0, "lunar": 0.17, "mars": 0.38})

    def test_tested_ranges_leave_out_the_suspect_values_the_ranking_still_scores(self):
        variables = client.get("/api/rank/options").json()["variables"]
        pressure, flow = variables["pressure"], variables["flow_velocity"]
        # The ranking's span, which sets its tolerances, still holds them (#87, option 2).
        self.assertEqual((pressure["min"], pressure["rows"]), (0.0, 1001))
        self.assertEqual((flow["min"], flow["rows"]), (-5.92, 570))
        # The tested range leaves out FLEX's 0 mmHg test and SPICE's eight negative air rates.
        self.assertEqual(pressure["tested"]["rows"], 1000)
        self.assertGreater(pressure["tested"]["min"], 0)
        self.assertEqual((flow["tested"]["min"], flow["tested"]["rows"]), (0.0, 562))
        self.assertEqual(pressure["tested"]["max"], pressure["max"])
        self.assertEqual(flow["tested"]["max"], flow["max"])


if __name__ == "__main__":
    unittest.main()
