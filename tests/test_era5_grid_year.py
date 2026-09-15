import unittest

from pipeline.era5_grid_year import _to_celsius_array, reduce_year


class Era5GridYearTests(unittest.TestCase):
    def test_module_imports_without_pipeline_dependencies(self):
        self.assertTrue(callable(_to_celsius_array))


    def test_duplicate_months_are_rejected_before_network_access(self):
        with self.assertRaises(ValueError):
            reduce_year(2020, None, months=(1, 1), api_token="unused")


if __name__ == "__main__":
    unittest.main()
