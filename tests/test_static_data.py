import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StaticDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "data/manifest.json").read_text())
        cls.tiles = ROOT / "data/rainfall/tiles"

    def test_national_tiles_and_place_index(self):
        self.assertEqual(self.manifest["status"], "rainfall-baseline")
        self.assertEqual(self.manifest["rainfall"]["validLandCells"], 22526)
        self.assertGreater(self.manifest["gazetteer"]["placeCount"], 20000)
        self.assertGreater(len(list(self.tiles.glob("*.json"))), 80)
        self.assertEqual(len(list((ROOT / "data/places").glob("*.json"))), len(self.manifest["searchPrefixes"]))
        for prefix in self.manifest["searchPrefixes"]:
            self.assertTrue((ROOT / "data/places" / f"{prefix}.json").exists())

    def test_month_arrays_and_ranges(self):
        for tile_path in self.tiles.glob("*.json"):
            tile = json.loads(tile_path.read_text())
            self.assertEqual(tile["id"], tile_path.stem)
            for cell in tile["cells"]:
                self.assertEqual(len(cell), 9)
                self.assertTrue(all(len(values) == 12 for values in cell[2:]))
                self.assertTrue(all(value >= 0 for value in cell[2]))
                self.assertTrue(all(low <= high for low, high in zip(cell[3], cell[4])))
                self.assertTrue(all(heavy <= rainy + 0.1 for heavy, rainy in zip(cell[6], cell[5])))
                self.assertTrue(all(0 <= value <= 1 for value in cell[8]))

    def test_static_source_budget(self):
        total = sum(path.stat().st_size for path in (ROOT / "site").glob("*.*"))
        self.assertLess(total, 250_000)


if __name__ == "__main__":
    unittest.main()
