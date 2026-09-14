"""Build one complete CHIRPS year for the three validation points."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import sys
import time

from pipeline.chirps import ClimatePoint, sample_daily_rainfall
from pipeline.chirps_smoke import VALIDATION_POINTS
from pipeline.metrics import DailyObservation, longest_dry_spell, monthly_climatology


def year_days(year: int):
    """Yield every calendar day in a year."""
    current = date(year, 1, 1)
    end = date(year + 1, 1, 1)
    while current < end:
        yield current
        current += timedelta(days=1)


def build_point_year(
    year: int,
    points: tuple[ClimatePoint, ...] = VALIDATION_POINTS,
) -> dict[str, object]:
    observations: dict[str, list[DailyObservation]] = defaultdict(list)
    point_metadata: dict[str, dict[str, object]] = {}
    days = list(year_days(year))
    started = time.monotonic()

    for index, day in enumerate(days, start=1):
        result = sample_daily_rainfall(day, points)
        for sample in result["samples"]:
            rainfall = sample["nearestCellMm"]
            if rainfall is None:
                rainfall = sample["neighborhoodMeanMm"]
            observations[sample["id"]].append(
                DailyObservation(day=day, rainfall_mm=float(rainfall))
            )
            point_metadata[sample["id"]] = {
                "id": sample["id"],
                "name": sample["name"],
                "latitude": sample["latitude"],
                "longitude": sample["longitude"],
                "cellCenter": sample["cellCenter"],
            }

        if index == 1 or index % 25 == 0 or index == len(days):
            elapsed = time.monotonic() - started
            print(
                f"processed {index}/{len(days)} days in {elapsed:.1f}s",
                file=sys.stderr,
                flush=True,
            )

    locations: list[dict[str, object]] = []
    for point in points:
        series = observations[point.id]
        if len(series) != len(days):
            raise RuntimeError(
                f"{point.name} has {len(series)} observations; expected {len(days)}"
            )
        metrics = monthly_climatology(series, start_year=year, end_year=year)
        locations.append(
            {
                **point_metadata[point.id],
                "days": len(series),
                "annualTotalMm": round(
                    sum(item.rainfall_mm for item in series),
                    1,
                ),
                "annualRainyDays": sum(
                    item.rainfall_mm >= 1.0 for item in series
                ),
                "longestDrySpellDays": longest_dry_spell(series),
                "monthly": metrics,
            }
        )

    return {
        "source": "CHIRPS v3 Final RNL",
        "year": year,
        "completeDays": len(days),
        "elapsedSeconds": round(time.monotonic() - started, 1),
        "locations": locations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2020)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()

    result = build_point_year(arguments.year)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if arguments.output:
        arguments.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
