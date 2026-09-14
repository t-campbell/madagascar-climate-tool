from datetime import date
import unittest

from pipeline.sources import (
    chirps_daily_url,
    era5_land_daily_request,
    era5_land_year_request,
)


class SourceRequestTests(unittest.TestCase):
    def test_final_chirps_cog_url(self):
        self.assertEqual(
            chirps_daily_url(date(2026, 9, 1), "final"),
            "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/rnl/cogs/2026/chirps-v3.0.rnl.2026.09.01.cog",
        )

    def test_preliminary_chirps_url(self):
        self.assertEqual(
            chirps_daily_url(date(2026, 9, 1), "preliminary"),
            "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/prelim/sat/2026/chirps-v3.0.prelim.2026.09.01.tif",
        )

    def test_era5_request_is_spatially_bounded(self):
        dataset, request = era5_land_daily_request(2020, 2, "daily_minimum")
        self.assertEqual(dataset, "derived-era5-land-daily-statistics")
        self.assertEqual(request["area"], [-11.0, 43.0, -26.0, 51.0])
        self.assertEqual(request["time_zone"], "utc+03:00")
        self.assertEqual(request["month"], ["02"])

    def test_invalid_statistic_is_rejected(self):
        with self.assertRaises(ValueError):
            era5_land_daily_request(2020, 1, "daily_guess")


    def test_era5_year_request_has_all_months_and_halo(self):
        dataset, request = era5_land_year_request(2020, "daily_minimum")
        self.assertEqual(dataset, "derived-era5-land-daily-statistics")
        self.assertEqual(request["month"], [f"{month:02d}" for month in range(1, 13)])
        self.assertEqual(request["area"], [-10.9, 42.9, -26.1, 51.1])


if __name__ == "__main__":
    unittest.main()

