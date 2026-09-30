import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from pipeline.publish_temperature import publish


class PublishTemperatureTests(unittest.TestCase):
    def test_writes_tiles_and_updates_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_directory = root / "data"
            data_directory.mkdir()
            (data_directory / "manifest.json").write_text(json.dumps({
                "normalPeriod": "1991-2020",
                "rainfall": {"source": "test"},
            }))
            baseline = root / "temperature.npz"
            land = np.array([[True, False], [True, True]])
            minimum = np.full((12, 2, 2), 18.25, dtype=np.float32)
            maximum = np.full((12, 2, 2), 27.75, dtype=np.float32)
            np.savez_compressed(
                baseline,
                normal_period=np.array("1991-2020"),
                source=np.array("ERA5-Land post-processed daily statistics"),
                latitude=np.array([-17.4, -17.5]),
                longitude=np.array([49.4, 49.5]),
                land_mask=land,
                monthly_minimum_mean_c=minimum,
                monthly_maximum_mean_c=maximum,
            )

            summary = publish(baseline, data_directory)
            manifest = json.loads((data_directory / "manifest.json").read_text())
            tile = json.loads(
                (data_directory / "temperature" / "tiles" / "S18_E049.json").read_text()
            )

            self.assertEqual(summary["validLandCells"], 3)
            self.assertEqual(manifest["status"], "climate-baseline")
            self.assertEqual(manifest["temperature"]["resolutionDegrees"], 0.1)
            self.assertEqual(tile["cells"][0][2], [18.2] * 12)
            self.assertEqual(tile["cells"][0][3], [27.8] * 12)


if __name__ == "__main__":
    unittest.main()
