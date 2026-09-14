"""Dependency-free reference implementations of the methodology metrics.

Production raster processing will use vectorized arrays. These small functions
remain the testable definition of what each published statistic means.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from statistics import median
from typing import Iterable


RAINY_DAY_MM = 1.0
MONTHS = tuple(range(1, 13))


@dataclass(frozen=True)
class DailyObservation:
    day: date
    rainfall_mm: float
    minimum_c: float | None = None
    maximum_c: float | None = None


def _quantile(values: list[float], probability: float) -> float:
    """Return a linearly interpolated quantile for a non-empty list."""
    if not values:
        raise ValueError("quantile requires at least one value")
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between zero and one")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def longest_dry_spell(observations: Iterable[DailyObservation]) -> int:
    """Return the longest run of days below the rainy-day threshold."""
    longest = 0
    current = 0
    previous: date | None = None
    for observation in sorted(observations, key=lambda item: item.day):
        if previous is not None and observation.day != previous + timedelta(days=1):
            current = 0
        if observation.rainfall_mm < RAINY_DAY_MM:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
        previous = observation.day
    return longest


def monthly_climatology(
    observations: Iterable[DailyObservation],
    start_year: int = 1991,
    end_year: int = 2020,
) -> dict[str, list[float]]:
    """Calculate the version 0.1 monthly climate metrics.

    Only observations inside the inclusive normal period are used. Callers are
    responsible for rejecting incomplete years before publication.
    """
    selected = [
        item for item in observations if start_year <= item.day.year <= end_year
    ]
    by_year_month: dict[tuple[int, int], list[DailyObservation]] = defaultdict(list)
    for item in selected:
        if item.rainfall_mm < 0:
            raise ValueError("rainfall cannot be negative")
        if (
            item.minimum_c is not None
            and item.maximum_c is not None
            and item.minimum_c > item.maximum_c
        ):
            raise ValueError("minimum temperature cannot exceed maximum")
        by_year_month[(item.day.year, item.day.month)].append(item)

    monthly_total: list[float] = []
    rainy_days: list[float] = []
    wet_intensity: list[float] = []
    total_p10: list[float] = []
    total_p90: list[float] = []
    minimum_c: list[float] = []
    maximum_c: list[float] = []

    for month in MONTHS:
        groups = [
            values
            for (year, group_month), values in sorted(by_year_month.items())
            if group_month == month
        ]
        if not groups:
            raise ValueError(f"no observations for month {month}")

        totals = [sum(item.rainfall_mm for item in group) for group in groups]
        counts = [
            sum(item.rainfall_mm >= RAINY_DAY_MM for item in group) for group in groups
        ]
        wet_values = [
            item.rainfall_mm
            for group in groups
            for item in group
            if item.rainfall_mm >= RAINY_DAY_MM
        ]
        mins = [
            item.minimum_c
            for group in groups
            for item in group
            if item.minimum_c is not None
        ]
        maxes = [
            item.maximum_c
            for group in groups
            for item in group
            if item.maximum_c is not None
        ]

        monthly_total.append(round(sum(totals) / len(totals), 1))
        rainy_days.append(round(sum(counts) / len(counts), 1))
        wet_intensity.append(round(median(wet_values), 1) if wet_values else 0.0)
        total_p10.append(round(_quantile(totals, 0.1), 1))
        total_p90.append(round(_quantile(totals, 0.9), 1))
        minimum_c.append(round(sum(mins) / len(mins), 1) if mins else float("nan"))
        maximum_c.append(round(sum(maxes) / len(maxes), 1) if maxes else float("nan"))

    return {
        "monthlyTotalMm": monthly_total,
        "rainyDays": rainy_days,
        "wetDayIntensityMm": wet_intensity,
        "monthlyTotalP10Mm": total_p10,
        "monthlyTotalP90Mm": total_p90,
        "monthlyMinC": minimum_c,
        "monthlyMaxC": maximum_c,
    }

