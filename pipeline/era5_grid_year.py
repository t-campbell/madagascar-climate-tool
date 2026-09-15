"""Build one mergeable annual ERA5-Land temperature-grid partial."""

from __future__ import annotations

import argparse
import calendar
from datetime import date
import json
import math
import os
from pathlib import Path
import tempfile
import time

from pipeline.chirps_smoke import VALIDATION_POINTS
from pipeline.era5_download_period import parse_months_csv
from pipeline.era5_land import CDS_API_URL, _coordinate_name, _temperature_variable
from pipeline.sources import era5_land_period_request


def _to_celsius_array(values, units: str | None):
    import numpy as np

    normalized = (units or "").strip().lower()
    if normalized in {"k", "kelvin"} or float(np.nanmean(values)) > 150:
        return values - 273.15
    if normalized in {"c", "°c", "degc", "degree_celsius", "degrees_celsius"}:
        return values
    raise ValueError(f"cannot determine temperature units: {units!r}")


def _download_period(
    year: int,
    months: tuple[int, ...],
    statistic: str,
    destination: Path,
    token: str,
) -> Path:
    import cdsapi

    dataset, request = era5_land_period_request(year, months, statistic)
    client = cdsapi.Client(url=CDS_API_URL, key=token)
    client.retrieve(dataset, request, str(destination))
    return destination


def _monthly_means(source: Path, selected_months: tuple[int, ...]):
    import numpy as np
    import xarray as xr

    with xr.open_dataset(source) as dataset:
        latitude_name = _coordinate_name(dataset, ("latitude", "lat"))
        longitude_name = _coordinate_name(dataset, ("longitude", "lon"))
        time_name = _coordinate_name(dataset, ("valid_time", "time", "date"))
        variable_name = _temperature_variable(dataset)
        data = dataset[variable_name].squeeze(drop=True)
        expected_dimensions = {time_name, latitude_name, longitude_name}
        if set(data.dims) != expected_dimensions:
            raise ValueError(f"unexpected ERA5-Land dimensions: {data.dims}")
        data = data.transpose(time_name, latitude_name, longitude_name)
        values = _to_celsius_array(
            np.asarray(data.values, dtype=np.float32),
            data.attrs.get("units"),
        )
        months = np.asarray(data[time_name].dt.month.values)
        expected_days = sum(
            calendar.monthrange(int(data[time_name].dt.year.values[0]), month)[1]
            for month in selected_months
        )
        if values.shape[0] != expected_days:
            raise ValueError(
                f"expected {expected_days} selected-month days, "
                f"found {values.shape[0]}"
            )
        if set(months.tolist()) != set(selected_months):
            raise ValueError(
                f"expected months {selected_months}, found {sorted(set(months.tolist()))}"
            )
        monthly_values = []
        for month in selected_months:
            selected = values[months == month]
            finite_count = np.sum(np.isfinite(selected), axis=0)
            monthly_values.append(
                np.divide(
                    np.nansum(selected, axis=0),
                    finite_count,
                    out=np.full(selected.shape[1:], np.nan, dtype=np.float32),
                    where=finite_count > 0,
                )
            )
        monthly = np.stack(monthly_values).astype(np.float32)
        latitude = np.asarray(data[latitude_name].values, dtype=np.float32)
        longitude = np.asarray(data[longitude_name].values, dtype=np.float32)
        return monthly, latitude, longitude


def _sample_monthly(minimum, maximum, land_mask, latitude, longitude):
    import numpy as np

    samples: list[dict[str, object]] = []
    for point in VALIDATION_POINTS:
        nearest_row = int(np.abs(latitude - point.latitude).argmin())
        nearest_column = int(np.abs(longitude - point.longitude).argmin())
        best: tuple[float, int, int] | None = None
        longitude_scale = math.cos(math.radians(point.latitude))
        for row in range(max(0, nearest_row - 4), min(len(latitude), nearest_row + 5)):
            for column in range(max(0, nearest_column - 4), min(len(longitude), nearest_column + 5)):
                if not land_mask[row, column]:
                    continue
                distance = (
                    (float(latitude[row]) - point.latitude) ** 2
                    + (
                        (float(longitude[column]) - point.longitude)
                        * longitude_scale
                    ) ** 2
                )
                if best is None or distance < best[0]:
                    best = (distance, row, column)
        if best is None:
            raise ValueError(f"no valid ERA5-Land cell near {point.name}")
        _, row, column = best
        samples.append(
            {
                "id": point.id,
                "name": point.name,
                "cellLatitude": round(float(latitude[row]), 6),
                "cellLongitude": round(float(longitude[column]), 6),
                "monthlyMinimumC": [
                    round(float(value), 1) for value in minimum[:, row, column]
                ],
                "monthlyMaximumC": [
                    round(float(value), 1) for value in maximum[:, row, column]
                ],
            }
        )
    return samples


def _validate_period(year: int, months: tuple[int, ...]) -> None:
    if not 1950 <= year < date.today().year:
        raise ValueError("year must be a complete ERA5-Land year from 1950 onward")
    if not months or len(months) != len(set(months)):
        raise ValueError("months must be non-empty and unique")
    if tuple(sorted(months)) != months or any(month < 1 or month > 12 for month in months):
        raise ValueError("months must be sorted values from 1 through 12")


def reduce_files(
    year: int,
    minimum_path: Path,
    maximum_path: Path,
    output: Path,
    summary_output: Path | None = None,
    *,
    months: tuple[int, ...] = tuple(range(1, 13)),
) -> dict[str, object]:
    """Reduce already-downloaded minimum and maximum files to one partial."""
    _validate_period(year, months)

    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError("numpy is required for ERA5-Land processing") from error

    started = time.monotonic()
    monthly_minimum, latitude, longitude = _monthly_means(
        minimum_path,
        months,
    )
    monthly_maximum, maximum_latitude, maximum_longitude = _monthly_means(
        maximum_path,
        months,
    )

    if not np.array_equal(latitude, maximum_latitude) or not np.array_equal(
        longitude,
        maximum_longitude,
    ):
        raise ValueError("minimum and maximum files use different grids")
    land_mask = np.all(np.isfinite(monthly_minimum), axis=0) & np.all(
        np.isfinite(monthly_maximum),
        axis=0,
    )
    if np.any(monthly_minimum[:, land_mask] > monthly_maximum[:, land_mask]):
        raise ValueError("monthly mean minimum exceeds monthly mean maximum")

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        format_version=np.array("0.1"),
        source=np.array("ERA5-Land post-processed daily statistics"),
        year=np.array(year, dtype=np.int16),
        months=np.asarray(months, dtype=np.uint8),
        latitude=latitude,
        longitude=longitude,
        land_mask=land_mask,
        monthly_minimum_c=monthly_minimum,
        monthly_maximum_c=monthly_maximum,
    )
    summary: dict[str, object] = {
        "source": "ERA5-Land post-processed daily statistics",
        "year": year,
        "months": list(months),
        "elapsedSeconds": round(time.monotonic() - started, 1),
        "partialBytes": output.stat().st_size,
        "grid": {
            "height": int(land_mask.shape[0]),
            "width": int(land_mask.shape[1]),
            "validCells": int(land_mask.sum()),
            "resolutionDegrees": 0.1,
        },
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


def reduce_year(
    year: int,
    output: Path,
    summary_output: Path | None = None,
    *,
    months: tuple[int, ...] = tuple(range(1, 13)),
    api_token: str | None = None,
) -> dict[str, object]:
    """Compatibility path that downloads both inputs synchronously."""
    _validate_period(year, months)
    token = api_token or os.environ.get("CDS_API_TOKEN")
    if not token:
        raise RuntimeError("CDS_API_TOKEN is not set")

    with tempfile.TemporaryDirectory(prefix=f"era5-land-{year}-") as directory:
        directory_path = Path(directory)
        minimum_path = _download_period(
            year,
            months,
            "daily_minimum",
            directory_path / "minimum.nc",
            token,
        )
        maximum_path = _download_period(
            year,
            months,
            "daily_maximum",
            directory_path / "maximum.nc",
            token,
        )
        return reduce_files(
            year,
            minimum_path,
            maximum_path,
            output,
            summary_output,
            months=months,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2020)
    months_group = parser.add_mutually_exclusive_group()
    months_group.add_argument("--months", nargs="+", type=int)
    months_group.add_argument("--months-csv")
    parser.add_argument("--minimum", type=Path)
    parser.add_argument("--maximum", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    arguments = parser.parse_args()
    months = (
        tuple(arguments.months)
        if arguments.months is not None
        else parse_months_csv(arguments.months_csv)
        if arguments.months_csv is not None
        else tuple(range(1, 13))
    )
    if (arguments.minimum is None) != (arguments.maximum is None):
        parser.error("--minimum and --maximum must be supplied together")
    if arguments.minimum is not None:
        reduce_files(
            arguments.year,
            arguments.minimum,
            arguments.maximum,
            arguments.output,
            arguments.summary,
            months=months,
        )
    else:
        reduce_year(
            arguments.year,
            arguments.output,
            arguments.summary,
            months=months,
        )


if __name__ == "__main__":
    main()
