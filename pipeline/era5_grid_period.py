"""Split one recovered multi-year ERA5-Land pair into annual partials."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

from pipeline.era5_download_period import parse_months_csv, parse_years_csv
from pipeline.era5_grid_year import reduce_files


def _validate_years(years: tuple[int, ...]) -> None:
    if not years or len(years) != len(set(years)):
        raise ValueError("years must be non-empty and unique")
    if tuple(sorted(years)) != years:
        raise ValueError("years must be sorted")
    if any(year < 1950 or year >= date.today().year for year in years):
        raise ValueError("years must be complete ERA5-Land years from 1950 onward")


def reduce_period_files(
    years: tuple[int, ...],
    minimum_path: Path,
    maximum_path: Path,
    output_directory: Path,
    manifest_output: Path | None = None,
    *,
    months: tuple[int, ...] = tuple(range(1, 13)),
) -> dict[str, object]:
    """Create an independently mergeable partial for every requested year."""
    _validate_years(years)
    output_directory.mkdir(parents=True, exist_ok=True)
    partials: list[dict[str, object]] = []
    for year in years:
        output = output_directory / f"era5-land-grid-{year}.npz"
        summary_output = output_directory / f"era5-land-grid-{year}.json"
        summary = reduce_files(
            year,
            minimum_path,
            maximum_path,
            output,
            summary_output,
            months=months,
        )
        partials.append(
            {
                "year": year,
                "file": output.name,
                "summary": summary_output.name,
                "bytes": summary["partialBytes"],
            }
        )

    manifest: dict[str, object] = {
        "source": "ERA5-Land post-processed daily statistics",
        "years": list(years),
        "months": list(months),
        "partials": partials,
    }
    rendered = json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False)
    if manifest_output:
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years-csv", required=True)
    parser.add_argument("--months-csv", default="1,2,3,4,5,6,7,8,9,10,11,12")
    parser.add_argument("--minimum", type=Path, required=True)
    parser.add_argument("--maximum", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    arguments = parser.parse_args()
    reduce_period_files(
        parse_years_csv(arguments.years_csv),
        arguments.minimum,
        arguments.maximum,
        arguments.output_directory,
        arguments.manifest,
        months=parse_months_csv(arguments.months_csv),
    )


if __name__ == "__main__":
    main()
