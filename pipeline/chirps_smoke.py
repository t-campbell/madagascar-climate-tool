"""Command-line live-source smoke test for the CHIRPS COG reader."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

from pipeline.chirps import ClimatePoint, sample_daily_rainfall


VALIDATION_POINTS = (
    ClimatePoint(
        id="fenoarivo-atsinanana",
        name="Fenoarivo Atsinanana",
        latitude=-17.381,
        longitude=49.409,
    ),
    ClimatePoint(
        id="antananarivo",
        name="Antananarivo",
        latitude=-18.879,
        longitude=47.507,
    ),
    ClimatePoint(
        id="toliara",
        name="Toliara",
        latitude=-23.351,
        longitude=43.685,
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2020-01-15")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()

    result = sample_daily_rainfall(
        date.fromisoformat(arguments.date),
        VALIDATION_POINTS,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if arguments.output:
        arguments.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
