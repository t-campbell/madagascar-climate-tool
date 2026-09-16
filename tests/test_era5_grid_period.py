from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipeline.era5_grid_period import reduce_period_files


class Era5GridPeriodTests(unittest.TestCase):
    @patch("pipeline.era5_grid_period.reduce_files")
    def test_period_is_split_into_named_yearly_partials(self, reduce_files):
        reduce_files.side_effect = [
            {"partialBytes": 100},
            {"partialBytes": 200},
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = reduce_period_files(
                (1991, 1992),
                root / "minimum.nc",
                root / "maximum.nc",
                root / "partials",
                root / "manifest.json",
            )

        self.assertEqual(manifest["years"], [1991, 1992])
        self.assertEqual(
            [partial["file"] for partial in manifest["partials"]],
            ["era5-land-grid-1991.npz", "era5-land-grid-1992.npz"],
        )
        self.assertEqual(reduce_files.call_count, 2)

    def test_period_rejects_duplicate_years(self):
        with self.assertRaises(ValueError):
            reduce_period_files(
                (1991, 1991),
                Path("minimum.nc"),
                Path("maximum.nc"),
                Path("partials"),
            )


if __name__ == "__main__":
    unittest.main()
