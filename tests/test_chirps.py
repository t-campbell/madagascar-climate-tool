import unittest

from pipeline.chirps import (
    ClimatePoint,
    validate_point,
    validate_rainfall_mm,
)


class ChirpsReaderTests(unittest.TestCase):
    def test_validation_points_are_inside_processing_extent(self):
        points = (
            ClimatePoint("fenoarivo", "Fenoarivo", -17.381, 49.409),
            ClimatePoint("antananarivo", "Antananarivo", -18.879, 47.507),
            ClimatePoint("toliara", "Toliara", -23.351, 43.685),
        )
        for point in points:
            validate_point(point)

    def test_point_outside_madagascar_extent_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_point(ClimatePoint("paris", "Paris", 48.8566, 2.3522))

    def test_rainfall_sanity_check(self):
        self.assertEqual(validate_rainfall_mm(12.5), 12.5)
        with self.assertRaises(ValueError):
            validate_rainfall_mm(-0.1)
        with self.assertRaises(ValueError):
            validate_rainfall_mm(float("nan"))


if __name__ == "__main__":
    unittest.main()
