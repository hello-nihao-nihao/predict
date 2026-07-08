import unittest

from football_predictor.odds import movement_1x2, no_vig_1x2
from football_predictor.types import Odds1X2Point


class OddsTests(unittest.TestCase):
    def test_no_vig_probabilities_sum_to_one(self):
        probs = no_vig_1x2(1.8, 3.5, 4.7)
        self.assertAlmostEqual(sum(probs.values()), 1.0)
        self.assertGreater(probs["home"], probs["away"])

    def test_movement_uses_global_time_window(self):
        points = [
            Odds1X2Point("average", "T-48", 1.80, 3.50, 4.50),
            Odds1X2Point("average", "T-6", 1.65, 3.80, 5.20),
        ]
        movement = movement_1x2(points, {"average": 1.0})
        self.assertGreater(movement["home"], 0.0)


if __name__ == "__main__":
    unittest.main()
