import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StaticDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "data/manifest.json").read_text())
        cls.places = json.loads((ROOT / "data/places.json").read_text())["places"]

    def test_every_place_has_a_tile_and_matching_location(self):
        for place in self.places:
            tile_path = ROOT / "data/tiles" / f"{place['tileId']}.json"
            self.assertTrue(tile_path.exists(), tile_path)
            tile = json.loads(tile_path.read_text())
            self.assertEqual(tile["tileId"], place["tileId"])
            ids = {location["id"] for location in tile["locations"]}
            self.assertIn(place["id"], ids)

    def test_month_arrays_and_ranges(self):
        for tile_path in (ROOT / "data/tiles").glob("*.json"):
            tile = json.loads(tile_path.read_text())
            for location in tile["locations"]:
                rain = location["rainfall"]
                temperature = location["temperature"]
                for key in ("monthlyTotalMm", "rainyDays", "wetDayIntensityMm", "drySpellRisk10d"):
                    self.assertEqual(len(rain[key]), 12)
                self.assertTrue(all(value >= 0 for value in rain["monthlyTotalMm"]))
                self.assertTrue(all(0 <= value <= 1 for value in rain["drySpellRisk10d"]))
                self.assertEqual(len(temperature["monthlyMinC"]), 12)
                self.assertEqual(len(temperature["monthlyMaxC"]), 12)
                self.assertTrue(all(low <= high for low, high in zip(temperature["monthlyMinC"], temperature["monthlyMaxC"])))

    def test_static_source_budget(self):
        total = sum(path.stat().st_size for path in (ROOT / "site").glob("*.*"))
        self.assertLess(total, 250_000)


if __name__ == "__main__":
    unittest.main()

