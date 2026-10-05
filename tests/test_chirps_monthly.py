import calendar
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    import numpy as np
except ModuleNotFoundError:
    np = None

from pipeline.chirps_monthly import complete_months, expected_latest, month_days, publish, read_month, shift_month, validate_arrays
from pipeline.publish_rainfall import ARRAY_NAMES, _sha256, publish as publish_baseline


class CalendarTests(unittest.TestCase):
    def test_complete_month_excludes_missing_day_and_partial_month(self):
        listing = " ".join(f"chirps-v3.0.rnl.2024.02.{day:02d}.cog" for day in range(1, 30))
        self.assertEqual(complete_months(listing, 2024, date(2024, 3, 1)), ["2024-02"])
        self.assertEqual(complete_months(listing, 2024, date(2024, 2, 29)), [])
        self.assertEqual(complete_months(listing.replace("2024.02.12", "2024.02.99"), 2024, date(2024, 3, 1)), [])

    def test_month_rollover_and_final_lag(self):
        self.assertEqual(shift_month("2026-01", -1), "2025-12")
        self.assertEqual(len(month_days("2024-02")), 29)
        self.assertEqual(expected_latest(date(2026, 10, 5)), "2026-08")
        self.assertEqual(expected_latest(date(2026, 10, 28)), "2026-09")


@unittest.skipIf(np is None, "publication tests require numpy")
class MonthlyPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.land = np.array([[True, False], [True, True]])
        self.baseline = self.root / "baseline.npz"
        values = {name: np.full((12, 2, 2), 1.0) for name in ARRAY_NAMES}
        np.savez_compressed(self.baseline, normal_period=np.array("1991-2020"), source=np.array("CHIRPS v3 Final RNL"),
                            land_mask=self.land, latitude=np.array([-17.375, -17.425]), longitude=np.array([49.425, 49.475]), **values)
        self.cache = self.root / "months"
        self.cache.mkdir()
        self.out = self.root / "data"
        self.out.mkdir()
        self.initial = {"status": "climate-baseline", "schemaVersion": "1.1", "productVersion": "0.4",
                        "rainfall": {"baselineSha256": _sha256(self.baseline)}, "temperature": {"baselineSha256": "fixed-temperature"},
                        "temperatureTileTemplate": "data/temperature/tiles/{tileId}.json"}
        (self.out / "manifest.json").write_text(json.dumps(self.initial))
        self.months = [shift_month("2026-08", offset) for offset in range(-11, 1)]
        for month in self.months:
            path = self.cache / f"chirps-month-{month}.npz"
            np.savez_compressed(path, format_version=np.array("1"), source=np.array("CHIRPS v3 Final RNL"),
                                month=np.array(month), baseline_sha256=np.array(_sha256(self.baseline)),
                                total_mm=np.full((2, 2), 150.0), rainy_days=np.full((2, 2), 10), heavy_days=np.full((2, 2), 2))
            path.with_suffix(".json").write_text(json.dumps({"month": month, "sha256": _sha256(path),
                "days": len(month_days(month)), "validLandCells": 3}))

    def tearDown(self):
        self.temp.cleanup()

    def test_publish_preserves_baselines_and_is_idempotent(self):
        result = publish(self.months, self.cache, self.baseline, self.out)
        first = (self.out / "manifest.json").read_bytes()
        publish(self.months, self.cache, self.baseline, self.out)
        self.assertEqual(first, (self.out / "manifest.json").read_bytes())
        manifest = json.loads(first)
        self.assertEqual(manifest["temperature"], self.initial["temperature"])
        self.assertEqual(manifest["rainfall"], self.initial["rainfall"])
        self.assertEqual(result["dataThrough"], "2026-08-31")
        tiles = list((self.out / "recent-rainfall/releases" / result["release"]).glob("S*.json"))
        self.assertTrue(tiles)
        self.assertEqual(json.loads(tiles[0].read_text())["months"], self.months)

    def test_corrupt_archive_and_missing_month_stop_publication(self):
        path = self.cache / f"chirps-month-{self.months[0]}.npz"
        path.write_bytes(path.read_bytes() + b"corrupt")
        with self.assertRaisesRegex(ValueError, "checksum"):
            read_month(path, self.months[0], _sha256(self.baseline), self.land)
        self.assertEqual(json.loads((self.out / "manifest.json").read_text()), self.initial)
        with self.assertRaises(ValueError):
            publish(self.months[:-1], self.cache, self.baseline, self.out)

    def test_bad_day_counts_and_missing_values_are_rejected(self):
        total = np.full((2, 2), 20.0)
        with self.assertRaises(ValueError):
            validate_arrays(total, np.full((2, 2), 32), np.zeros((2, 2)), self.land, 31)
        total[0, 0] = np.nan
        with self.assertRaises(ValueError):
            validate_arrays(total, np.full((2, 2), 2), np.zeros((2, 2)), self.land, 31)

    def test_rainfall_regeneration_keeps_temperature_and_recent_references(self):
        initial = {**self.initial, "recentRainfall": {"release": "existing-monthly"}}
        (self.out / "manifest.json").write_text(json.dumps(initial))
        gazetteer = self.root / "names.zip"
        gazetteer.write_bytes(b"gazetteer fixture")
        place = {"id": 1, "name": "Fenoarivo", "aliases": [], "district": "", "region": "", "lat": -17.375, "lon": 49.425, "population": 1}
        with patch("pipeline.publish_rainfall.parse_geonames", return_value=[place]):
            publish_baseline(self.baseline, gazetteer, self.out)
        manifest = json.loads((self.out / "manifest.json").read_text())
        self.assertEqual(manifest["temperature"], initial["temperature"])
        self.assertEqual(manifest["recentRainfall"], initial["recentRainfall"])
        self.assertEqual(manifest["status"], "climate-baseline")


if __name__ == "__main__":
    unittest.main()
