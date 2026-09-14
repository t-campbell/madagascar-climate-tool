"""Merge complete CHIRPS yearly partials into a 1991-2020 grid normal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from pipeline.chirps_grid_year import _sample_annual_totals
from pipeline.chirps_smoke import VALIDATION_POINTS
from pipeline.metrics import HEAVY_RAIN_DAY_MM, RAINY_DAY_MM


NORMAL_START_YEAR = 1991
NORMAL_END_YEAR = 2020
EXPECTED_YEARS = tuple(range(NORMAL_START_YEAR, NORMAL_END_YEAR + 1))


def validate_years(years: list[int]) -> None:
    if len(years) != len(set(years)):
        raise ValueError("duplicate yearly partial")
    if tuple(sorted(years)) != EXPECTED_YEARS:
        missing = sorted(set(EXPECTED_YEARS) - set(years))
        extra = sorted(set(years) - set(EXPECTED_YEARS))
        raise ValueError(f"baseline years are incomplete; missing={missing}, extra={extra}")


def _sample_monthly_grid(metric, land_mask, latitudes, longitudes):
    import numpy as np

    results: list[dict[str, object]] = []
    for point in VALIDATION_POINTS:
        latitude_index = int(np.abs(latitudes - point.latitude).argmin())
        longitude_index = int(np.abs(longitudes - point.longitude).argmin())
        best: tuple[float, int, int] | None = None
        longitude_scale = float(np.cos(np.radians(point.latitude)))
        for row in range(max(0, latitude_index - 4), min(len(latitudes), latitude_index + 5)):
            for column in range(max(0, longitude_index - 4), min(len(longitudes), longitude_index + 5)):
                if not land_mask[row, column]:
                    continue
                distance = (
                    (float(latitudes[row]) - point.latitude) ** 2
                    + (
                        (float(longitudes[column]) - point.longitude)
                        * longitude_scale
                    ) ** 2
                )
                if best is None or distance < best[0]:
                    best = (distance, row, column)
        if best is None:
            raise ValueError(f"no valid grid cell near {point.name}")
        _, row, column = best
        results.append(
            {
                "id": point.id,
                "name": point.name,
                "cellLatitude": round(float(latitudes[row]), 6),
                "cellLongitude": round(float(longitudes[column]), 6),
                "monthly": [
                    round(float(value), 1) for value in metric[:, row, column]
                ],
            }
        )
    return results


def merge_partials(
    partial_paths: list[Path],
    output: Path,
    summary_output: Path | None = None,
) -> dict[str, object]:
    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError("numpy is required to merge CHIRPS partials") from error

    if not partial_paths:
        raise ValueError("at least one yearly partial is required")

    started = time.monotonic()
    metadata = None
    records: list[tuple[int, Path]] = []
    for path in partial_paths:
        with np.load(path, allow_pickle=False) as partial:
            year = int(partial["year"])
            records.append((year, path))
    records.sort()
    years = [year for year, _ in records]
    validate_years(years)

    with np.load(records[0][1], allow_pickle=False) as first:
        latitude = first["latitude"].copy()
        longitude = first["longitude"].copy()
        land_mask = first["land_mask"].copy()
        transform = first["transform"].copy()
        crs = str(first["crs"])
        shape = first["monthly_total_mm"].shape

    yearly_totals = np.empty((len(records), *shape), dtype=np.float32)
    rainy_sum = np.zeros(shape, dtype=np.uint32)
    heavy_sum = np.zeros(shape, dtype=np.uint32)
    wet_total_sum = np.zeros(shape, dtype=np.float64)
    wet_count_sum = np.zeros(shape, dtype=np.uint32)
    dry_spell_sum = np.zeros(shape, dtype=np.uint16)

    for index, (year, path) in enumerate(records):
        with np.load(path, allow_pickle=False) as partial:
            if (
                str(partial["format_version"]) != "0.1"
                or str(partial["crs"]) != crs
                or not np.array_equal(partial["latitude"], latitude)
                or not np.array_equal(partial["longitude"], longitude)
                or not np.array_equal(partial["land_mask"], land_mask)
                or not np.allclose(partial["transform"], transform, atol=1e-9)
            ):
                raise ValueError(f"{path}: grid metadata differs from the baseline")
            yearly_totals[index] = partial["monthly_total_mm"]
            rainy_sum += partial["rainy_day_count"]
            heavy_sum += partial["heavy_rain_day_count"]
            wet_total_sum += partial["wet_day_total_mm"]
            wet_count_sum += partial["wet_day_count"]
            dry_spell_sum += partial["dry_spell_10d"]

    years_count = len(records)
    monthly_total_mean = yearly_totals.mean(axis=0, dtype=np.float64).astype(np.float32)
    monthly_quantiles = np.quantile(
        yearly_totals,
        [0.1, 0.5, 0.9],
        axis=0,
    ).astype(np.float32)
    rainy_days_mean = (rainy_sum / years_count).astype(np.float32)
    heavy_rain_days_mean = (heavy_sum / years_count).astype(np.float32)
    wet_day_intensity = np.divide(
        wet_total_sum,
        wet_count_sum,
        out=np.zeros(shape, dtype=np.float64),
        where=wet_count_sum > 0,
    ).astype(np.float32)
    dry_spell_risk = (dry_spell_sum / years_count).astype(np.float32)

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        format_version=np.array("0.2"),
        source=np.array("CHIRPS v3 Final RNL"),
        normal_period=np.array(f"{NORMAL_START_YEAR}-{NORMAL_END_YEAR}"),
        rainy_day_threshold_mm=np.array(RAINY_DAY_MM, dtype=np.float32),
        heavy_rain_day_threshold_mm=np.array(HEAVY_RAIN_DAY_MM, dtype=np.float32),
        crs=np.array(crs),
        transform=transform,
        latitude=latitude,
        longitude=longitude,
        land_mask=land_mask,
        monthly_total_mean_mm=monthly_total_mean,
        monthly_total_p10_mm=monthly_quantiles[0],
        monthly_total_p50_mm=monthly_quantiles[1],
        monthly_total_p90_mm=monthly_quantiles[2],
        rainy_days_mean=rainy_days_mean,
        heavy_rain_days_mean=heavy_rain_days_mean,
        wet_day_intensity_mean_mm=wet_day_intensity,
        dry_spell_10d_risk=dry_spell_risk,
    )

    annual_mean = monthly_total_mean.sum(axis=0)
    summary: dict[str, object] = {
        "source": "CHIRPS v3 Final RNL",
        "normalPeriod": f"{NORMAL_START_YEAR}-{NORMAL_END_YEAR}",
        "years": years_count,
        "grid": {
            "height": int(shape[1]),
            "width": int(shape[2]),
            "validCells": int(land_mask.sum()),
            "resolutionDegrees": 0.05,
        },
        "baselineBytes": output.stat().st_size,
        "elapsedSeconds": round(time.monotonic() - started, 1),
        "annualMeanRainfallRangeMm": [
            round(float(annual_mean[land_mask].min()), 1),
            round(float(annual_mean[land_mask].max()), 1),
        ],
        "validationAnnualMean": _sample_annual_totals(
            annual_mean,
            land_mask,
            latitude,
            longitude,
        ),
        "validationHeavyRainDays": _sample_monthly_grid(
            heavy_rain_days_mean,
            land_mask,
            latitude,
            longitude,
        ),
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    if summary_output:
        summary_output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("partials", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    arguments = parser.parse_args()
    merge_partials(arguments.partials, arguments.output, arguments.summary)


if __name__ == "__main__":
    main()
