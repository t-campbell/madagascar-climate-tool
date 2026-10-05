"""Check candidate files or production responses at three contrasting locations."""
import argparse
from datetime import date
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

from pipeline.chirps_monthly import expected_latest, shift_month

POINTS = [("Fenoarivo", -17.38095, 49.40826), ("Antananarivo", -18.8792, 47.5079), ("Toliara", -23.351, 43.6714)]


def verify(load):
    manifest = load("data/manifest.json")
    recent = manifest["recentRainfall"]
    if manifest["status"] != "climate-baseline" or "temperature" not in manifest:
        raise ValueError("historical temperature/rainfall references were lost")
    months = recent["months"]
    if len(months) != 12 or months != [shift_month(months[-1], offset) for offset in range(-11, 1)]:
        raise ValueError("incomplete twelve-month coverage")
    status = load("data/update-status.json")
    if status["release"] != recent["release"] or status["dataThrough"] != recent["dataThrough"]:
        raise ValueError("health endpoint and active manifest disagree")
    results = []
    for name, lat, lon in POINTS:
        tile_id = f"S{abs(math.floor(lat)):02d}_E{math.floor(lon):03d}"
        historical = load(manifest["tileTemplate"].replace("{tileId}", tile_id))
        temperature = load(manifest["temperatureTileTemplate"].replace("{tileId}", tile_id))
        tile = load(recent["tileTemplate"].replace("{tileId}", tile_id))
        if tile["release"] != recent["release"] or tile["months"] != months:
            raise ValueError("mixed publication versions")
        def nearest(data):
            return min(data["cells"], key=lambda c: (data["lat"][c[0]] - lat) ** 2 + ((data["lon"][c[1]] - lon) * math.cos(math.radians(lat))) ** 2)
        rain = nearest(historical)
        current = nearest(tile)
        temp = nearest(temperature)
        if (tile["lat"][current[0]], tile["lon"][current[1]]) != (historical["lat"][rain[0]], historical["lon"][rain[1]]):
            raise ValueError("historical and recent cells differ")
        if any(not math.isfinite(v) for v in current[2]) or len(current[2]) != 12:
            raise ValueError("bad rainfall series")
        if max(current[2]) > recent["axisMaxMm"]:
            raise ValueError("chart scale clips rainfall")
        if any(high < low for low, high in zip(temp[2], temp[3])):
            raise ValueError("invalid temperature values")
        results.append({"location": name, "lastMonthRainfallMm": current[2][-1], "dataThrough": recent["dataThrough"]})
    print(json.dumps(results))
    return recent


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--directory", type=Path)
    group.add_argument("--base-url")
    parser.add_argument("--freshness", action="store_true")
    args = parser.parse_args()
    def load(path):
        if args.directory:
            return json.loads((args.directory / path).read_text())
        request = Request(args.base_url.rstrip("/") + "/" + path, headers={"Cache-Control": "no-cache"})
        with urlopen(request, timeout=45) as response:
            return json.load(response)
    recent = verify(load)
    if args.freshness and recent["months"][-1] < expected_latest(date.today()):
        raise SystemExit("rainfall data-through date is older than the normal Final release schedule")


if __name__ == "__main__":
    main()
