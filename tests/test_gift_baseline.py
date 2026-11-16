import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tracker"))
import fetch_gift

class GiftBaselineTests(unittest.TestCase):
    def test_current_official_baseline_retains_the_same_normalization(self):
        models = [
            {"name":"Seasonal_Naive","config":{},"rows":{"dataset":{"mase":2.0,"crps":4.0}}},
            {"name":"Example","config":{},"rows":{"dataset":{"mase":1.0,"crps":2.0}}},
        ]
        results = {row["name"]:row for row in fetch_gift.aggregate(models)}
        self.assertEqual(results["Seasonal_Naive"]["mase"],1.0)
        self.assertEqual(results["Seasonal_Naive"]["crps"],1.0)
        self.assertEqual(results["Example"]["mase"],0.5)
        self.assertEqual(results["Example"]["crps"],0.5)
    def test_missing_official_baseline_still_blocks_publication(self):
        with self.assertRaises(RuntimeError):
            fetch_gift.aggregate([{"name":"Example","config":{},"rows":{}}])

if __name__ == "__main__": unittest.main()
