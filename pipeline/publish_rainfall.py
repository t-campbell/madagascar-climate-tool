"""Publish compact, static Madagascar CHIRPS tiles and a searchable gazetteer."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
import zipfile


HALO_DEGREES = 0.15
MAX_CELL_DISTANCE_KM = 12
MAX_PLACE_SHARD_BYTES = 85_000
MONTHS = 12
ARRAY_NAMES = (
    "monthly_total_mean_mm",
    "monthly_total_p10_mm",
    "monthly_total_p90_mm",
    "rainy_days_mean",
    "heavy_rain_days_mean",
    "wet_day_intensity_mean_mm",
    "dry_spell_10d_risk",
)


def normalize(value: str) -> str:
    letters = unicodedata.normalize("NFKD", value)
    letters = "".join(char for char in letters if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", letters.lower()).strip()


def tile_id(lat: float, lon: float) -> str:
    return f"S{abs(math.floor(lat)):02d}_E{math.floor(lon):03d}"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _short_name(value: str) -> str:
    return re.sub(r" (Region|District)$", "", value)


def parse_geonames(source: Path) -> list[dict[str, object]]:
    """Use populated-place entries and short Latin aliases from the country dump."""
    with zipfile.ZipFile(source) as archive:
        rows = [row.split("\t") for row in archive.read("MG.txt").decode("utf-8").splitlines()]
    regions = {row[10]: _short_name(row[1]) for row in rows if row[7] == "ADM1"}
    districts = {row[11]: _short_name(row[1]) for row in rows if row[7] == "ADM2"}
    places = []
    for row in rows:
        if row[6] != "P" or row[7] not in {"PPL", "PPLX", "PPLA", "PPLA2", "PPLA3", "PPLC"}:
            continue
        lat, lon = float(row[4]), float(row[5])
        if not (-26 <= lat <= -11 and 43 <= lon <= 51):
            continue
        aliases = []
        for alias in row[3].split(","):
            alias = alias.strip()
            if (
                alias and alias != row[1] and len(alias) <= 50
                and normalize(alias) and all(ord(char) < 256 for char in alias)
                and normalize(alias) not in {normalize(name) for name in [row[1], *aliases]}
            ):
                aliases.append(alias)
            if len(aliases) >= 12:
                break
        places.append({
            "id": int(row[0]),
            "name": row[1],
            "aliases": aliases,
            "district": districts.get(row[11], ""),
            "region": regions.get(row[10], ""),
            "lat": lat,
            "lon": lon,
            "population": int(row[14]) if row[14] else 0,
        })
    return places


def publish(baseline: Path, gazetteer: Path, output: Path) -> dict[str, object]:
    import numpy as np

    with np.load(baseline, allow_pickle=False) as data:
        assert str(data["normal_period"]) == "1991-2020"
        assert str(data["source"]) == "CHIRPS v3 Final RNL"
        latitudes = data["latitude"].astype(float)
        longitudes = data["longitude"].astype(float)
        land = data["land_mask"]
        arrays = [data[key] for key in ARRAY_NAMES]
        assert all(arr.shape == (MONTHS, *land.shape) for arr in arrays)
        assert all(np.all(np.isfinite(arr[:, land])) for arr in arrays)
        assert np.all(arrays[2][:, land] >= arrays[1][:, land])
        assert np.all(arrays[4][:, land] <= arrays[3][:, land] + 0.1)
        assert np.all((arrays[6][:, land] >= 0) & (arrays[6][:, land] <= 1))

        tile_dir = output / "rainfall" / "tiles"
        tile_dir.mkdir(parents=True, exist_ok=True)
        tile_ids: set[str] = set()
        for south in range(-26, -11):
            for west in range(43, 51):
                rows = np.flatnonzero((latitudes >= south - HALO_DEGREES) & (latitudes < south + 1 + HALO_DEGREES))
                cols = np.flatnonzero((longitudes >= west - HALO_DEGREES) & (longitudes < west + 1 + HALO_DEGREES))
                if not len(rows) or not len(cols):
                    continue
                selected = land[np.ix_(rows, cols)]
                if not selected.any():
                    continue
                records = []
                for local_row, local_col in np.argwhere(selected):
                    row, col = int(rows[local_row]), int(cols[local_col])
                    record = [int(local_row), int(local_col)]
                    for index, array in enumerate(arrays):
                        precision = 3 if index == 6 else 1
                        record.append([round(float(value), precision) for value in array[:, row, col]])
                    records.append(record)
                identifier = tile_id(south + 0.5, west + 0.5)
                tile_ids.add(identifier)
                _write_json(tile_dir / f"{identifier}.json", {
                    "id": identifier,
                    "lat": [round(float(latitudes[row]), 5) for row in rows],
                    "lon": [round(float(longitudes[col]), 5) for col in cols],
                    "cells": records,
                })

        places = parse_geonames(gazetteer)
        # Every suggested settlement must resolve to a nearby CHIRPS land cell.
        searchable = []
        for place in places:
            lat, lon = place["lat"], place["lon"]
            nearest_row = int(np.abs(latitudes - lat).argmin())
            nearest_col = int(np.abs(longitudes - lon).argmin())
            rows = slice(max(0, nearest_row - 4), min(len(latitudes), nearest_row + 5))
            cols = slice(max(0, nearest_col - 4), min(len(longitudes), nearest_col + 5))
            nearby = land[rows, cols]
            if not nearby.any():
                continue
            scale = math.cos(math.radians(lat))
            distance = (latitudes[rows, None] - lat) ** 2 + ((longitudes[None, cols] - lon) * scale) ** 2
            if float(distance[nearby].min()) ** 0.5 * 111.2 > MAX_CELL_DISTANCE_KM:
                continue
            if tile_id(lat, lon) in tile_ids:
                searchable.append(place)

    # Keep the familiar spellings available even if the upstream name varies.
    curated = {
        "Fenoarivo Atsinanana": ["Fenerive Est", "Fénérive-Est"],
        "Antananarivo": ["Tana"],
        "Toliara": ["Tuléar", "Tulear"],
    }
    for place in searchable:
        if place["name"] in curated and (
            place["name"] != "Antananarivo" or place["population"] > 100000
        ):
            place["aliases"] = list(dict.fromkeys([*place["aliases"], *curated[place["name"]]]))

    shards: dict[str, list[tuple[str, dict[str, object]]]] = defaultdict(list)
    for place in searchable:
        for name in [place["name"], *place["aliases"]]:
            normalized = normalize(name)
            key = normalized[:3]
            if len(key) == 3:
                shards[key].append((normalized, place))
    place_dir = output / "places"
    place_dir.mkdir(parents=True, exist_ok=True)
    shard_keys: list[str] = []

    def write_shard(prefix: str, entries: list[tuple[str, dict[str, object]]]) -> None:
        unique = {place["id"]: place for _, place in entries}
        result = {"places": sorted(unique.values(), key=lambda place: (-place["population"], place["name"], place["id"]))}
        encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) <= MAX_PLACE_SHARD_BYTES:
            _write_json(place_dir / f"{prefix}.json", result)
            shard_keys.append(prefix)
            return
        exact = [(name, place) for name, place in entries if len(name) <= len(prefix)]
        if exact:
            write_shard(prefix, exact)
        children: dict[str, list[tuple[str, dict[str, object]]]] = defaultdict(list)
        for name, place in entries:
            if len(name) > len(prefix):
                children[name[: len(prefix) + 1]].append((name, place))
        for child, members in children.items():
            write_shard(child, members)

    for prefix, entries in shards.items():
        write_shard(prefix, entries)

    manifest = {
        "schemaVersion": "1.0",
        "productVersion": "0.3.0-rainfall-demo",
        "status": "rainfall-baseline",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "normalPeriod": "1991-2020",
        "rainfall": {
            "source": "CHIRPS v3 Final RNL",
            "resolutionDegrees": 0.05,
            "rainyDayThresholdMm": 1,
            "heavyRainDayThresholdMm": 20,
            "baselineSha256": _sha256(baseline),
            "validLandCells": int(land.sum()),
        },
        "gazetteer": {
            "source": "GeoNames MG country dump",
            "url": "https://download.geonames.org/export/dump/MG.zip",
            "sha256": _sha256(gazetteer),
            "placeCount": len(searchable),
        },
        "tileTemplate": "data/rainfall/tiles/{tileId}.json",
        "placesTemplate": "data/places/{prefix}.json",
        "searchPrefixes": sorted(shard_keys),
        "defaultLocation": {"name": "Fenoarivo Atsinanana", "lat": -17.38095, "lon": 49.40826},
        "maxCellDistanceKm": MAX_CELL_DISTANCE_KM,
    }
    _write_json(output / "manifest.json", manifest)
    return {"tiles": len(tile_ids), "places": len(searchable), "shards": len(shard_keys), "baselineSha256": manifest["rainfall"]["baselineSha256"]}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--gazetteer", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data"))
    args = parser.parse_args()
    print(json.dumps(publish(args.baseline, args.gazetteer, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
