"""Merge ERA5-Land yearly partials into a 1991-2020 temperature normal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from pipeline.era5_grid_year import _sample_monthly


NORMAL_START_YEAR = 1991
NORMAL_END_YEAR = 2020
EXPECTED_YEARS = tuple(range(NORMAL_START_YEAR, NORMAL_END_YEAR + 1))
EXPECTED_MONTHS = tuple(range(1, 13))


def validate_years(years: list[int]) -> None:
    if len(years) != len(set(years)):
        raise ValueError("duplicate yearly partial")
    if tuple(sorted(years)) != EXPECTED_YEARS:
        missing = sorted(set(EXPECTED_YEARS) - set(years))
        extra = sorted(set(years) - set(EXPECTED_YEARS))
        raise ValueError(
            f"temperature baseline years are incomplete; missing={missing}, extra={extra}"
        )


def merge_partials(
    partial_paths: list[Path],
    output: Path,
    summary_output: Path | None = None,
) -> dict[str, object]:
    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError("numpy is required to merge ERA5-Land partials") from error

    if not partial_paths:
        raise ValueError("at least one yearly partial is required")

    started = time.monotonic()
    records: list[tuple[int, Path]] = []
    for path in partial_paths:
        with np.load(path, allow_pickle=False) as partial:
            records.append((int(partial["year"]), path))
    records.sort()
    years = [year for year, _ in records]
    validate_years(years)

    with np.load(records[0][1], allow_pickle=False) as first:
        latitude = first["latitude"].copy()
        longitude = first["longitude"].copy()
        land_mask = first["land_mask"].copy()
        shape = first["monthly_minimum_c"].shape

    minimums = np.empty((len(records), *shape), dtype=np.float32)
    maximums = np.empty((len(records), *shape), dtype=np.float32)
    for index, (year, path) in enumerate(records):
        with np.load(path, allow_pickle=False) as partial:
            if (
                str(partial["format_version"]) != "0.1"
                or tuple(int(value) for value in partial["months"]) != EXPECTED_MONTHS
                or not np.array_equal(partial["latitude"], latitude)
                or not np.array_equal(partial["longitude"], longitude)
                or not np.array_equal(partial["land_mask"], land_mask)
                or partial["monthly_minimum_c"].shape != shape
                or partial["monthly_maximum_c"].shape != shape
            ):
                raise ValueError(f"{path}: grid metadata differs from the baseline")
            minimums[index] = partial["monthly_minimum_c"]
            maximums[index] = partial["monthly_maximum_c"]

    monthly_minimum = minimums.mean(axis=0, dtype=np.float64).astype(np.float32)
    monthly_maximum = maximums.mean(axis=0, dtype=np.float64).astype(np.float32)
    if np.any(monthly_minimum[:, land_mask] > monthly_maximum[:, land_mask]):
        raise ValueError("baseline monthly minimum exceeds monthly maximum")

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        format_version=np.array("0.1"),
        source=np.array("ERA5-Land post-processed daily statistics"),
        normal_period=np.array(f"{NORMAL_START_YEAR}-{NORMAL_END_YEAR}"),
        latitude=latitude,
        longitude=longitude,
        land_mask=land_mask,
        monthly_minimum_mean_c=monthly_minimum,
        monthly_maximum_mean_c=monthly_maximum,
    )

    summary: dict[str, object] = {
        "source": "ERA5-Land post-processed daily statistics",
        "normalPeriod": f"{NORMAL_START_YEAR}-{NORMAL_END_YEAR}",
        "years": len(records),
        "grid": {
            "height": int(shape[1]),
            "width": int(shape[2]),
            "validCells": int(land_mask.sum()),
            "resolutionDegrees": 0.1,
        },
        "baselineBytes": output.stat().st_size,
        "elapsedSeconds": round(time.monotonic() - started, 1),
        "temperatureRangeC": [
            round(float(monthly_minimum[:, land_mask].min()), 1),
            round(float(monthly_maximum[:, land_mask].max()), 1),
        ],
        "validationSamples": _sample_monthly(
            monthly_minimum,
            monthly_maximum,
            land_mask,
            latitude,
            longitude,
        ),
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)
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
