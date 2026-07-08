import unittest

from football_predictor.defaults import DEFAULT_MODEL_CONFIG
from football_predictor.model_v5 import predict_match
from football_predictor.sample_data import sample_payload
from football_predictor.types import load_matches


class ModelV5Tests(unittest.TestCase):
    def test_prediction_is_normalized(self):
        match = load_matches(sample_payload())[0]
        prediction = predict_match(match, DEFAULT_MODEL_CONFIG)
        self.assertAlmostEqual(sum(prediction.probabilities.values()), 1.0)
        self.assertEqual(len(prediction.top_scores), 5)
        self.assertGreater(prediction.xg["home"], prediction.xg["away"])


if __name__ == "__main__":
    unittest.main()
