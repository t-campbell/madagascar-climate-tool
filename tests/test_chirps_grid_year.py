from datetime import date
import unittest

from pipeline.chirps_grid_year import processing_days, target_days


class ChirpsGridYearTests(unittest.TestCase):
    def test_target_days_include_leap_day(self):
        days = list(target_days(2020))
        self.assertEqual(len(days), 366)
        self.assertEqual(days[0], date(2020, 1, 1))
        self.assertEqual(days[-1], date(2020, 12, 31))

    def test_processing_days_include_dry_spell_halo(self):
        days = list(processing_days(2020))
        self.assertEqual(len(days), 384)
        self.assertEqual(days[0], date(2019, 12, 23))
        self.assertEqual(days[-1], date(2021, 1, 9))


if __name__ == "__main__":
    unittest.main()
