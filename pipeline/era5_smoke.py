"""Run a minimal live CDS/ERA5-Land access and decoding check."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import tempfile

from pipeline.chirps_smoke import VALIDATION_POINTS
from pipeline.era5_land import (
    request_daily_temperature,
    sample_temperature_file,
    samples_as_dicts,
)


def run_smoke_test(day: date, output: Path | None = None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="era5-land-smoke-") as directory:
        source = Path(directory) / "daily-mean.nc"
        request_daily_temperature(day, "daily_mean", source)
        samples = sample_temperature_file(source, VALIDATION_POINTS)

    result: dict[str, object] = {
        "source": "ERA5-Land post-processed daily statistics",
        "date": day.isoformat(),
        "statistic": "daily_mean",
        "units": "degrees Celsius",
        "samples": samples_as_dicts(samples),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)
    if output:
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=date.fromisoformat, default=date(2020, 1, 15))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    run_smoke_test(arguments.date, arguments.output)


if __name__ == "__main__":
    main()
