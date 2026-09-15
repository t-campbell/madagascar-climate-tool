"""Download one bounded ERA5-Land daily-statistics file."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from pipeline.era5_land import CDS_API_URL
from pipeline.sources import era5_land_period_request


def download_period(
    year: int,
    months: tuple[int, ...],
    statistic: str,
    output: Path,
    *,
    api_token: str | None = None,
) -> Path:
    import cdsapi

    token = api_token or os.environ.get("CDS_API_TOKEN")
    if not token:
        raise RuntimeError("CDS_API_TOKEN is not set")

    dataset, request = era5_land_period_request(year, months, statistic)
    output.parent.mkdir(parents=True, exist_ok=True)
    client = cdsapi.Client(url=CDS_API_URL, key=token)
    client.retrieve(dataset, request, str(output))

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("CDS request completed without a usable output file")
    print(f"downloaded {output} ({output.stat().st_size} bytes)")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--months", nargs="+", type=int, required=True)
    parser.add_argument(
        "--statistic",
        choices=("daily_minimum", "daily_maximum"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    download_period(
        arguments.year,
        tuple(arguments.months),
        arguments.statistic,
        arguments.output,
    )


if __name__ == "__main__":
    main()
