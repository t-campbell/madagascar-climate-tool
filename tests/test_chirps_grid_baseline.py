import unittest

from pipeline.chirps_grid_baseline import EXPECTED_YEARS, validate_years


class ChirpsGridBaselineTests(unittest.TestCase):
    def test_expected_normal_is_accepted(self):
        validate_years(list(EXPECTED_YEARS))

    def test_missing_year_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_years(list(EXPECTED_YEARS[:-1]))

    def test_duplicate_year_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_years(list(EXPECTED_YEARS) + [1991])


if __name__ == "__main__":
    unittest.main()
