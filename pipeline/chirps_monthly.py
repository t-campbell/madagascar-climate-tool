"""Acquire complete CHIRPS Final months and publish a rolling twelve-month view.

Monthly NPZ reductions are durable inputs, never Actions-cache dependencies.
The historical normal and temperature metadata are preserved unchanged.
"""
from __future__ import annotations

import argparse
import calendar
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
import subprocess
import tempfile
import zipfile
from urllib.error import HTTPError
from urllib.request import urlopen

from pipeline.chirps import MAX_PLAUSIBLE_DAILY_RAIN_MM
from pipeline.chirps_grid_year import _gdal_options, _sample_annual_totals
from pipeline.publish_rainfall import HALO_DEGREES, _sha256, _write_json, tile_id
from pipeline.sources import chirps_daily_url

SOURCE = "CHIRPS v3 Final RNL"
VERSION = "1"


def shift_month(month: str, offset: int) -> str:
    year, number = map(int, month.split("-"))
    if not 1 <= number <= 12:
        raise ValueError("invalid month")
    index = year * 12 + number - 1 + offset
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def month_days(month: str) -> list[date]:
    year, number = map(int, month.split("-"))
    return [date(year, number, day) for day in range(1, calendar.monthrange(year, number)[1] + 1)]


def complete_months(listing: str, year: int, today: date) -> list[str]:
    """Only consider months with every expected dated daily file listed."""
    found = set(re.findall(r"chirps-v3\.0\.rnl\.(\d{4}\.\d{2}\.\d{2})\.cog", listing))
    result = []
    for number in range(1, 13):
        month = f"{year:04d}-{number:02d}"
        days = month_days(month)
        if days[-1] >= today:
            continue
        if all(day.strftime("%Y.%m.%d") in found for day in days):
            result.append(month)
    return result


def discover_months(today: date) -> list[str]:
    available = []
    for year in [today.year - 2, today.year - 1, today.year]:
        url = chirps_daily_url(date(year, 1, 1)).rsplit("/", 1)[0] + "/"
        listing = None
        for attempt in range(3):
            try:
                with urlopen(url, timeout=45) as response:
                    listing = response.read().decode("utf-8")
                break
            except HTTPError as error:
                if error.code == 404 and year == today.year:
                    listing = ""
                    break
                if attempt == 2:
                    raise
            except OSError:
                if attempt == 2:
                    raise
            time.sleep(2 * (attempt + 1))
        available.extend(complete_months(listing or "", year, today))
    if not available:
        raise ValueError("source lists no complete Final months")
    return sorted(available)


def expected_latest(today: date) -> str:
    """Allow through the 27th for the normal third-week Final release lag."""
    return shift_month(today.strftime("%Y-%m"), -1 if today.day >= 28 else -2)


def validate_arrays(total, rainy, heavy, land, days: int) -> None:
    import numpy as np
    if any(array.shape != land.shape for array in [total, rainy, heavy]):
        raise ValueError("monthly grid shape mismatch")
    if not np.any(land):
        raise ValueError("empty land mask")
    if not np.all(np.isfinite(total[land])) or np.any(total[land] < 0):
        raise ValueError("invalid monthly rainfall")
    if np.any(total[land] > days * MAX_PLAUSIBLE_DAILY_RAIN_MM):
        raise ValueError("implausible monthly rainfall")
    if any(not np.all(np.isfinite(array[land])) for array in [rainy, heavy]):
        raise ValueError("nonfinite day counts")
    if np.any(rainy[land] < 0) or np.any(heavy[land] < 0) or np.any(rainy[land] > days) or np.any(heavy[land] > rainy[land]):
        raise ValueError("invalid rainy/heavy day counts")
    if any(np.any(array[land] != np.floor(array[land])) for array in [rainy, heavy]):
        raise ValueError("day counts must be integers")


def reduce_month(month: str, baseline: Path, output: Path) -> dict:
    import numpy as np
    import rasterio
    from rasterio.windows import Window
    from rasterio.transform import Affine

    days = month_days(month)
    with np.load(baseline, allow_pickle=False) as data:
        land = data["land_mask"].copy()
        transform = Affine(*data["transform"])
        lat = data["latitude"].copy()
        lon = data["longitude"].copy()
        crs = str(data["crs"])
    total = np.zeros(land.shape, dtype=np.float64)
    rainy = np.zeros(land.shape, dtype=np.uint8)
    heavy = np.zeros(land.shape, dtype=np.uint8)
    count = np.zeros(land.shape, dtype=np.uint8)
    fingerprint = hashlib.sha256()
    with rasterio.Env(**_gdal_options()):
        for day in days:
            with rasterio.open(chirps_daily_url(day)) as source:
                if source.count != 1 or str(source.crs) != crs:
                    raise ValueError(f"{day}: unexpected raster format/CRS")
                # Align to the established grid including the baseline halo.
                col, row = ~source.transform * (transform.c, transform.f)
                if abs(col - round(col)) > 1e-5 or abs(row - round(row)) > 1e-5:
                    raise ValueError(f"{day}: source grid is not aligned")
                window = Window(round(col), round(row), land.shape[1], land.shape[0])
                if not np.allclose(tuple(source.window_transform(window))[:6], tuple(transform)[:6], atol=1e-9, rtol=0):
                    raise ValueError(f"{day}: source transform changed")
                raster = source.read(1, window=window, masked=True)
                values = np.asarray(raster.filled(np.nan), dtype=np.float32)
                valid = ~np.ma.getmaskarray(raster) & np.isfinite(values) & (values != -9999)
                if not np.array_equal(valid, land):
                    raise ValueError(f"{day}: missing cells or changed land mask")
                if np.any(values[land] < 0) or np.any(values[land] > MAX_PLAUSIBLE_DAILY_RAIN_MM):
                    raise ValueError(f"{day}: invalid daily rainfall")
                total += np.where(land, values, 0)
                rainy += land & (values >= 1)
                heavy += land & (values >= 20)
                count += land
                fingerprint.update(day.isoformat().encode())
                fingerprint.update(values[land].astype("<f4").tobytes())
    if np.any(count[land] != len(days)):
        raise ValueError("incomplete month")
    validate_arrays(total, rainy, heavy, land, len(days))
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, format_version=np.array(VERSION), source=np.array(SOURCE),
                        month=np.array(month), baseline_sha256=np.array(_sha256(baseline)),
                        total_mm=total.astype(np.float32), rainy_days=rainy, heavy_days=heavy)
    summary = {"month": month, "source": SOURCE, "days": len(days),
               "baselineSha256": _sha256(baseline), "sourceWindowSha256": fingerprint.hexdigest(),
               "sha256": _sha256(output), "validLandCells": int(land.sum()),
               "validationSamples": _sample_annual_totals(total, land, lat, lon)}
    _write_json(output.with_suffix(".json"), summary)
    output.with_suffix(".sha256").write_text(f"{summary['sha256']}  {output.name}\n")
    print(json.dumps(summary), flush=True)
    return summary


def read_month(path: Path, month: str, baseline_hash: str, land):
    import numpy as np
    summary = json.loads(path.with_suffix(".json").read_text())
    if summary["sha256"] != _sha256(path):
        raise ValueError(f"{month}: archived checksum mismatch")
    with np.load(path, allow_pickle=False) as data:
        if str(data["month"]) != month or str(data["source"]) != SOURCE or str(data["format_version"]) != VERSION:
            raise ValueError("wrong monthly artifact")
        if str(data["baseline_sha256"]) != baseline_hash:
            raise ValueError("monthly artifact references a different baseline")
        arrays = [data[key].copy() for key in ["total_mm", "rainy_days", "heavy_days"]]
    validate_arrays(*arrays, land, len(month_days(month)))
    if summary["days"] != len(month_days(month)) or summary["validLandCells"] != int(land.sum()):
        raise ValueError("monthly completeness metadata mismatch")
    return arrays, summary


def publish(months: list[str], cache: Path, baseline: Path, output: Path) -> dict:
    import numpy as np
    if len(months) != 12 or months != [shift_month(months[-1], i) for i in range(-11, 1)]:
        raise ValueError("publication needs twelve consecutive complete months")
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    baseline_hash = _sha256(baseline)
    if manifest["rainfall"]["baselineSha256"] != baseline_hash or "temperature" not in manifest:
        raise ValueError("publication must preserve validated rainfall and temperature baselines")
    with np.load(baseline, allow_pickle=False) as data:
        land = data["land_mask"].copy()
        lat, lon = data["latitude"].astype(float), data["longitude"].astype(float)
    arrays, summaries = [], []
    for month in months:
        values, summary = read_month(cache / f"chirps-month-{month}.npz", month, baseline_hash, land)
        arrays.append(values)
        summaries.append(summary)
    stacked = [np.stack([values[index] for values in arrays]) for index in range(3)]
    release_hash = hashlib.sha256(json.dumps({"version": VERSION, "baseline": baseline_hash,
                                             "months": [(s["month"], s["sha256"]) for s in summaries]}, sort_keys=True).encode()).hexdigest()
    release = release_hash[:20]
    template = f"data/recent-rainfall/releases/{release}/{{tileId}}.json"
    destination = output / "recent-rainfall" / "releases" / release
    tile_count = 0
    for south in range(-26, -11):
        for west in range(43, 51):
            rows = np.flatnonzero((lat >= south - HALO_DEGREES) & (lat < south + 1 + HALO_DEGREES))
            cols = np.flatnonzero((lon >= west - HALO_DEGREES) & (lon < west + 1 + HALO_DEGREES))
            if not len(rows) or not len(cols):
                continue
            selected = land[np.ix_(rows, cols)]
            if not selected.any():
                continue
            records = []
            for local_row, local_col in np.argwhere(selected):
                row, col = int(rows[local_row]), int(cols[local_col])
                records.append([int(local_row), int(local_col),
                                [round(float(v), 1) for v in stacked[0][:, row, col]],
                                [int(v) for v in stacked[1][:, row, col]],
                                [int(v) for v in stacked[2][:, row, col]]])
            identifier = tile_id(south + 0.5, west + 0.5)
            _write_json(destination / f"{identifier}.json", {"id": identifier, "release": release,
                "months": months, "lat": [round(float(lat[row]), 5) for row in rows],
                "lon": [round(float(lon[col]), 5) for col in cols], "cells": records})
            tile_count += 1
    through = month_days(months[-1])[-1].isoformat()
    from math import ceil
    previous = manifest.get("recentRainfall", {})
    history = list(dict.fromkeys([release, *previous.get("retainedReleases", [previous.get("release")])]))
    history = [item for item in history if item][:3]
    metadata = {"retainedReleases": history, "source": SOURCE, "status": "final", "months": months, "dataThrough": through,
                "release": release, "sha256": release_hash, "tileTemplate": template,
                "axisMaxMm": max(1000, ceil(float(stacked[0][:, land].max()) / 250) * 250),
                "baselineSha256": baseline_hash, "validLandCells": int(land.sum()), "tiles": tile_count}
    _write_json(destination / "release.json", {**metadata, "monthlyArtifacts": summaries})
    manifest["recentRainfall"] = metadata
    manifest["schemaVersion"] = "1.2"
    manifest["productVersion"] = "0.5.0-monthly-rainfall"
    # Deterministic output: no new timestamp and commit on a no-op run.
    _write_json(manifest_path, manifest)
    _write_json(output / "update-status.json", {"dataThrough": through, "release": release, "source": SOURCE})
    for directory in destination.parent.iterdir():
        if directory.is_dir() and directory.name not in history:
            shutil.rmtree(directory)
    return metadata


def archive_month(path: Path, release: str) -> None:
    archive = path.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
        for suffix in [".npz", ".json", ".sha256"]:
            source = path.with_suffix(suffix)
            bundle.write(source, source.name)
    subprocess.run(["gh", "release", "upload", release, str(archive)], check=True)
    with tempfile.TemporaryDirectory() as directory:
        subprocess.run(["gh", "release", "download", release, "-p", archive.name, "-D", directory], check=True)
        if _sha256(Path(directory) / archive.name) != _sha256(archive):
            raise ValueError("durable monthly upload checksum mismatch")


def update(baseline: Path, cache: Path, output: Path, today: date, summary_path: Path, archive_release: str | None = None) -> dict:
    available = discover_months(today)
    latest = available[-1]
    months = [shift_month(latest, i) for i in range(-11, 1)]
    if any(month not in available for month in months):
        raise ValueError("source has a gap in the rolling twelve months")
    active = json.loads((output / "manifest.json").read_text()).get("recentRainfall", {})
    if active.get("months", [""])[-1] > latest:
        raise ValueError("source discovery would regress the active observation date")
    cache.mkdir(parents=True, exist_ok=True)
    new = []
    for month in months:
        path = cache / f"chirps-month-{month}.npz"
        if not path.exists():
            reduce_month(month, baseline, path)
            if archive_release:
                archive_month(path, archive_release)
            new.extend(str(path.with_suffix(suffix)) for suffix in [".npz", ".json", ".sha256"])
    metadata = publish(months, cache, baseline, output)
    result = {**metadata, "newFiles": new, "sourceLate": latest < expected_latest(today),
              "expectedThroughMonth": expected_latest(today), "checkedAt": datetime.now(timezone.utc).isoformat()}
    _write_json(summary_path, result)
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--summary", type=Path, default=Path("update-summary.json"))
    parser.add_argument("--archive-release")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    update(args.baseline, args.cache, args.output, args.today, args.summary, args.archive_release)


if __name__ == "__main__":
    main()
