"""Reduce one CHIRPS year to compact Madagascar-grid partial statistics."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import math
from pathlib import Path
import sys
import time

from pipeline.chirps import MADAGASCAR_BOUNDS, MAX_PLAUSIBLE_DAILY_RAIN_MM
from pipeline.chirps_smoke import VALIDATION_POINTS
from pipeline.metrics import HEAVY_RAIN_DAY_MM, RAINY_DAY_MM
from pipeline.sources import chirps_daily_url


DRY_SPELL_DAYS = 10
HALO_DAYS = DRY_SPELL_DAYS - 1
GRID_HALO_CELLS = 1


def target_days(year: int):
    current = date(year, 1, 1)
    end = date(year + 1, 1, 1)
    while current < end:
        yield current
        current += timedelta(days=1)


def processing_days(year: int):
    """Include nine days on either side to resolve cross-year dry spells."""
    current = date(year, 1, 1) - timedelta(days=HALO_DAYS)
    end = date(year + 1, 1, 1) + timedelta(days=HALO_DAYS)
    while current < end:
        yield current
        current += timedelta(days=1)


def _gdal_options() -> dict[str, str]:
    return {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".cog",
        "GDAL_HTTP_MULTIRANGE": "YES",
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_MAX_RETRY": "3",
        "GDAL_HTTP_RETRY_DELAY": "1",
    }


def _sample_annual_totals(
    annual_total,
    land_mask,
    latitudes,
    longitudes,
) -> list[dict[str, object]]:
    import numpy as np

    samples: list[dict[str, object]] = []
    for point in VALIDATION_POINTS:
        latitude_index = int(np.abs(latitudes - point.latitude).argmin())
        longitude_index = int(np.abs(longitudes - point.longitude).argmin())
        best: tuple[float, int, int] | None = None
        longitude_scale = math.cos(math.radians(point.latitude))
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
            raise ValueError(f"no valid CHIRPS grid cell near {point.name}")
        _, row, column = best
        samples.append(
            {
                "id": point.id,
                "name": point.name,
                "cellLatitude": round(float(latitudes[row]), 6),
                "cellLongitude": round(float(longitudes[column]), 6),
                "annualTotalMm": round(float(annual_total[row, column]), 1),
            }
        )
    return samples


def reduce_year(year: int, output: Path, summary_output: Path | None = None) -> dict[str, object]:
    """Stream remote daily COG windows and write a compressed yearly partial."""
    try:
        import numpy as np
        import rasterio
        from rasterio.windows import from_bounds
    except ImportError as error:
        raise RuntimeError(
            "numpy and rasterio are required; install requirements-pipeline.txt"
        ) from error

    if not 1981 <= year < date.today().year:
        raise ValueError("year must be a complete CHIRPS year from 1981 onward")

    month_shape: tuple[int, int, int] | None = None
    window = None
    window_transform = None
    crs = None
    land_mask = None
    monthly_total = None
    rainy_days = None
    heavy_rain_days = None
    wet_day_total = None
    wet_day_count = None
    valid_day_count = None
    dry_spell_10d = None
    dry_run = None
    latitudes = None
    longitudes = None

    all_days = list(processing_days(year))
    year_day_count = len(list(target_days(year)))
    started = time.monotonic()

    with rasterio.Env(**_gdal_options()):
        for index, day in enumerate(all_days, start=1):
            url = chirps_daily_url(day)
            with rasterio.open(url) as dataset:
                if dataset.count != 1:
                    raise ValueError(f"{day}: expected one band")
                if dataset.crs is None or not dataset.crs.is_geographic:
                    raise ValueError(f"{day}: expected geographic CRS")
                resolution_x = abs(float(dataset.transform.a))
                resolution_y = abs(float(dataset.transform.e))
                if not (
                    math.isclose(resolution_x, 0.05, abs_tol=1e-6)
                    and math.isclose(resolution_y, 0.05, abs_tol=1e-6)
                ):
                    raise ValueError(
                        f"{day}: unexpected resolution {resolution_x} x {resolution_y}"
                    )

                if window is None:
                    padding = GRID_HALO_CELLS * resolution_x
                    window = from_bounds(
                        MADAGASCAR_BOUNDS["west"] - padding,
                        MADAGASCAR_BOUNDS["south"] - padding,
                        MADAGASCAR_BOUNDS["east"] + padding,
                        MADAGASCAR_BOUNDS["north"] + padding,
                        dataset.transform,
                    ).round_offsets().round_lengths()
                    window_transform = dataset.window_transform(window)
                    crs = str(dataset.crs)
                    height, width = int(window.height), int(window.width)
                    month_shape = (12, height, width)
                    monthly_total = np.zeros(month_shape, dtype=np.float32)
                    rainy_days = np.zeros(month_shape, dtype=np.uint16)
                    heavy_rain_days = np.zeros(month_shape, dtype=np.uint16)
                    wet_day_total = np.zeros(month_shape, dtype=np.float32)
                    wet_day_count = np.zeros(month_shape, dtype=np.uint16)
                    valid_day_count = np.zeros(month_shape, dtype=np.uint16)
                    dry_spell_10d = np.zeros(month_shape, dtype=np.bool_)
                    dry_run = np.zeros((height, width), dtype=np.uint16)
                    rows = np.arange(height)
                    columns = np.arange(width)
                    longitudes = (
                        window_transform.c
                        + (columns + 0.5) * window_transform.a
                    ).astype(np.float32)
                    latitudes = (
                        window_transform.f
                        + (rows + 0.5) * window_transform.e
                    ).astype(np.float32)
                else:
                    transform = dataset.window_transform(window)
                    if str(dataset.crs) != crs or not np.allclose(
                        tuple(transform)[:6],
                        tuple(window_transform)[:6],
                        atol=1e-9,
                    ):
                        raise ValueError(f"{day}: source grid changed")

                raster = dataset.read(1, window=window, masked=True)
                valid = ~np.ma.getmaskarray(raster)
                values = np.asarray(raster.filled(np.nan), dtype=np.float32)
                if land_mask is None:
                    land_mask = valid.copy()
                elif not np.array_equal(valid, land_mask):
                    raise ValueError(f"{day}: valid-data mask changed")
                if np.any(values[valid] < 0) or np.any(
                    values[valid] > MAX_PLAUSIBLE_DAILY_RAIN_MM
                ):
                    raise ValueError(f"{day}: implausible rainfall value")

                dry = valid & (values < RAINY_DAY_MM)
                dry_run[:] = np.where(dry, dry_run + 1, 0)
                qualified = dry_run >= DRY_SPELL_DAYS
                if day.year == year:
                    dry_spell_10d[day.month - 1] |= qualified
                newly_qualified = dry_run == DRY_SPELL_DAYS
                spell_start = day - timedelta(days=DRY_SPELL_DAYS - 1)
                if (
                    spell_start.year == year
                    and (spell_start.year, spell_start.month) != (day.year, day.month)
                ):
                    dry_spell_10d[spell_start.month - 1] |= newly_qualified

                if day.year == year:
                    month = day.month - 1
                    safe_values = np.where(valid, values, 0.0)
                    wet = valid & (values >= RAINY_DAY_MM)
                    heavy = valid & (values >= HEAVY_RAIN_DAY_MM)
                    monthly_total[month] += safe_values
                    rainy_days[month] += wet
                    heavy_rain_days[month] += heavy
                    wet_day_total[month] += np.where(wet, values, 0.0)
                    wet_day_count[month] += wet
                    valid_day_count[month] += valid

            if index == 1 or index % 25 == 0 or index == len(all_days):
                print(
                    f"processed {index}/{len(all_days)} source days in "
                    f"{time.monotonic() - started:.1f}s",
                    file=sys.stderr,
                    flush=True,
                )

    if any(
        value is None
        for value in (
            month_shape,
            window_transform,
            land_mask,
            monthly_total,
            rainy_days,
            heavy_rain_days,
            wet_day_total,
            wet_day_count,
            valid_day_count,
            dry_spell_10d,
            latitudes,
            longitudes,
        )
    ):
        raise RuntimeError("no source data were processed")

    expected_days = np.array(
        [
            (date(year + (month == 12), month % 12 + 1, 1) - date(year, month, 1)).days
            for month in range(1, 13)
        ],
        dtype=np.uint16,
    )
    if np.any(valid_day_count[:, land_mask] != expected_days[:, None]):
        raise ValueError("one or more land cells have an incomplete month")

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        format_version=np.array("0.1"),
        source=np.array("CHIRPS v3 Final RNL"),
        year=np.array(year, dtype=np.int16),
        crs=np.array(crs),
        transform=np.array(tuple(window_transform)[:6], dtype=np.float64),
        latitude=latitudes,
        longitude=longitudes,
        land_mask=land_mask,
        monthly_total_mm=monthly_total,
        rainy_day_count=rainy_days,
        heavy_rain_day_count=heavy_rain_days,
        wet_day_total_mm=wet_day_total,
        wet_day_count=wet_day_count,
        dry_spell_10d=dry_spell_10d,
        valid_day_count=valid_day_count,
    )

    annual_total = monthly_total.sum(axis=0)
    valid_annual = annual_total[land_mask]
    summary: dict[str, object] = {
        "source": "CHIRPS v3 Final RNL",
        "year": year,
        "targetDays": year_day_count,
        "sourceDaysIncludingDrySpellHalo": len(all_days),
        "elapsedSeconds": round(time.monotonic() - started, 1),
        "grid": {
            "height": int(month_shape[1]),
            "width": int(month_shape[2]),
            "validCells": int(land_mask.sum()),
            "resolutionDegrees": 0.05,
            "haloCells": GRID_HALO_CELLS,
        },
        "partialBytes": output.stat().st_size,
        "annualRainfallRangeMm": [
            round(float(valid_annual.min()), 1),
            round(float(valid_annual.max()), 1),
        ],
        "validationSamples": _sample_annual_totals(
            annual_total,
            land_mask,
            latitudes,
            longitudes,
        ),
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    if summary_output:
        summary_output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2020)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    arguments = parser.parse_args()
    reduce_year(arguments.year, arguments.output, arguments.summary)


if __name__ == "__main__":
    main()
