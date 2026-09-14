import unittest

from pipeline.era5_land import _to_celsius


class Era5LandTests(unittest.TestCase):
    def test_kelvin_units_are_converted(self):
        self.assertAlmostEqual(_to_celsius(300.0, "K"), 26.85)

    def test_kelvin_is_detected_from_value(self):
        self.assertAlmostEqual(_to_celsius(273.15, None), 0.0)

    def test_celsius_is_preserved(self):
        self.assertEqual(_to_celsius(24.5, "degree_Celsius"), 24.5)

    def test_unknown_units_raise(self):
        with self.assertRaises(ValueError):
            _to_celsius(24.5, None)


if __name__ == "__main__":
    unittest.main()
