"""Publish compact static ERA5-Land temperature tiles beside rainfall data."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


HALO_DEGREES = 0.15
MONTHS = 12
MAX_CELL_DISTANCE_KM = 20


def tile_id(lat: float, lon: float) -> str:
    return f"S{abs(math.floor(lat)):02d}_E{math.floor(lon):03d}"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def publish(baseline: Path, data_directory: Path) -> dict[str, object]:
    """Write 1-degree temperature transport tiles and update the data manifest."""
    import numpy as np

    manifest_path = data_directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["normalPeriod"] != "1991-2020" or "rainfall" not in manifest:
        raise ValueError("temperature must be published beside the 1991-2020 rainfall baseline")

    with np.load(baseline, allow_pickle=False) as data:
        if str(data["normal_period"]) != "1991-2020":
            raise ValueError("unexpected temperature normal period")
        if str(data["source"]) != "ERA5-Land post-processed daily statistics":
            raise ValueError("unexpected temperature source")
        latitudes = data["latitude"].astype(float)
        longitudes = data["longitude"].astype(float)
        land = data["land_mask"]
        minimum = data["monthly_minimum_mean_c"]
        maximum = data["monthly_maximum_mean_c"]
        expected_shape = (MONTHS, *land.shape)
        if minimum.shape != expected_shape or maximum.shape != expected_shape:
            raise ValueError("unexpected temperature array shape")
        if not np.all(np.isfinite(minimum[:, land])) or not np.all(np.isfinite(maximum[:, land])):
            raise ValueError("temperature baseline contains non-finite land values")
        if np.any(minimum[:, land] > maximum[:, land]):
            raise ValueError("monthly minimum exceeds monthly maximum")
        if float(minimum[:, land].min()) < -15 or float(maximum[:, land].max()) > 50:
            raise ValueError("temperature baseline exceeds Madagascar validation range")

        tile_dir = data_directory / "temperature" / "tiles"
        tile_dir.mkdir(parents=True, exist_ok=True)
        tile_ids: set[str] = set()
        for south in range(-26, -11):
            for west in range(43, 51):
                rows = np.flatnonzero(
                    (latitudes >= south - HALO_DEGREES)
                    & (latitudes < south + 1 + HALO_DEGREES)
                )
                cols = np.flatnonzero(
                    (longitudes >= west - HALO_DEGREES)
                    & (longitudes < west + 1 + HALO_DEGREES)
                )
                if not len(rows) or not len(cols):
                    continue
                selected = land[np.ix_(rows, cols)]
                if not selected.any():
                    continue
                records = []
                for local_row, local_col in np.argwhere(selected):
                    row, col = int(rows[local_row]), int(cols[local_col])
                    records.append([
                        int(local_row),
                        int(local_col),
                        [round(float(value), 1) for value in minimum[:, row, col]],
                        [round(float(value), 1) for value in maximum[:, row, col]],
                    ])
                identifier = tile_id(south + 0.5, west + 0.5)
                tile_ids.add(identifier)
                _write_json(tile_dir / f"{identifier}.json", {
                    "id": identifier,
                    "lat": [round(float(latitudes[row]), 5) for row in rows],
                    "lon": [round(float(longitudes[col]), 5) for col in cols],
                    "cells": records,
                })

        valid_minimum = minimum[:, land]
        valid_maximum = maximum[:, land]
        manifest.update({
            "schemaVersion": "1.1",
            "productVersion": "0.4.0-climate-baseline",
            "status": "climate-baseline",
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "temperature": {
                "source": "ERA5-Land post-processed daily statistics",
                "resolutionDegrees": 0.1,
                "baselineSha256": _sha256(baseline),
                "validLandCells": int(land.sum()),
                "rangeC": [
                    round(float(valid_minimum.min()), 1),
                    round(float(valid_maximum.max()), 1),
                ],
            },
            "temperatureTileTemplate": "data/temperature/tiles/{tileId}.json",
            "maxTemperatureCellDistanceKm": MAX_CELL_DISTANCE_KM,
        })
        _write_json(manifest_path, manifest)

    return {
        "tiles": len(tile_ids),
        "validLandCells": manifest["temperature"]["validLandCells"],
        "baselineSha256": manifest["temperature"]["baselineSha256"],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--data-directory", type=Path, default=Path("data"))
    arguments = parser.parse_args()
    print(json.dumps(publish(arguments.baseline, arguments.data_directory), sort_keys=True))


if __name__ == "__main__":
    main()
