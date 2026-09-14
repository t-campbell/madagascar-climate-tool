import unittest

from pipeline.era5_grid_year import _to_celsius_array


class Era5GridYearTests(unittest.TestCase):
    def test_module_imports_without_pipeline_dependencies(self):
        self.assertTrue(callable(_to_celsius_array))


if __name__ == "__main__":
    unittest.main()
