from datetime import date, timedelta
import unittest

from pipeline.metrics import DailyObservation, longest_dry_spell, monthly_climatology


class ClimateMetricTests(unittest.TestCase):
    def test_longest_dry_spell(self):
        start = date(2000, 1, 1)
        rainfall = [0, 0.5, 0, 2, 0, 0, 0, 0, 1]
        observations = [
            DailyObservation(start + timedelta(days=index), value)
            for index, value in enumerate(rainfall)
        ]
        self.assertEqual(longest_dry_spell(observations), 4)

    def test_gap_breaks_dry_spell(self):
        observations = [
            DailyObservation(date(2000, 1, 1), 0),
            DailyObservation(date(2000, 1, 2), 0),
            DailyObservation(date(2000, 1, 4), 0),
        ]
        self.assertEqual(longest_dry_spell(observations), 2)

    def test_monthly_climatology(self):
        observations = []
        for year in (1991, 1992):
            for month in range(1, 13):
                observations.extend(
                    [
                        DailyObservation(date(year, month, 1), 0, 10, 20),
                        DailyObservation(date(year, month, 2), month, 12, 22),
                    ]
                )
        result = monthly_climatology(observations)
        self.assertEqual(result["monthlyTotalMm"], list(map(float, range(1, 13))))
        self.assertEqual(result["rainyDays"], [1.0] * 12)
        self.assertEqual(result["heavyRainDays"], [0.0] * 12)
        self.assertEqual(result["monthlyMinC"], [11.0] * 12)
        self.assertEqual(result["monthlyMaxC"], [21.0] * 12)

    def test_heavy_rain_day_threshold_is_inclusive(self):
        observations = [
            DailyObservation(date(1991, month, 1), 20.0)
            for month in range(1, 13)
        ]
        result = monthly_climatology(observations)
        self.assertEqual(result["heavyRainDays"], [1.0] * 12)

    def test_invalid_temperature_is_rejected(self):
        observations = []
        for month in range(1, 13):
            observations.append(DailyObservation(date(1991, month, 1), 1, 30, 20))
        with self.assertRaises(ValueError):
            monthly_climatology(observations)


if __name__ == "__main__":
    unittest.main()

