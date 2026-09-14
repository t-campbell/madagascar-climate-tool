import unittest

from pipeline.chirps_point_year import year_days


class ChirpsPointYearTests(unittest.TestCase):
    def test_common_year_days(self):
        days = list(year_days(2019))
        self.assertEqual(len(days), 365)
        self.assertEqual(days[0].isoformat(), "2019-01-01")
        self.assertEqual(days[-1].isoformat(), "2019-12-31")

    def test_leap_year_days(self):
        days = list(year_days(2020))
        self.assertEqual(len(days), 366)
        self.assertIn("2020-02-29", {day.isoformat() for day in days})


if __name__ == "__main__":
    unittest.main()
