"""Windowed CHIRPS v3 reads for validation and baseline processing.

Rasterio and GDAL are imported only inside network functions so the lightweight
methodology tests do not require geospatial binary dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import math
from typing import Iterable

from pipeline.sources import chirps_daily_url


MADAGASCAR_BOUNDS = {
    "west": 43.0,
    "south": -26.0,
    "east": 51.0,
    "north": -11.0,
}
MAX_PLAUSIBLE_DAILY_RAIN_MM = 1_000.0


@dataclass(frozen=True)
class ClimatePoint:
    id: str
    name: str
    latitude: float
    longitude: float


def validate_point(point: ClimatePoint) -> None:
    """Reject coordinates outside the supported Madagascar processing extent."""
    if not point.id or not point.name:
        raise ValueError("point id and name are required")
    if not math.isfinite(point.latitude) or not math.isfinite(point.longitude):
        raise ValueError("coordinates must be finite")
    if not MADAGASCAR_BOUNDS["south"] <= point.latitude <= MADAGASCAR_BOUNDS["north"]:
        raise ValueError(f"{point.name} latitude is outside the Madagascar extent")
    if not MADAGASCAR_BOUNDS["west"] <= point.longitude <= MADAGASCAR_BOUNDS["east"]:
        raise ValueError(f"{point.name} longitude is outside the Madagascar extent")


def validate_rainfall_mm(value: float) -> float:
    """Return a finite, non-negative rainfall value after a broad sanity check."""
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("rainfall must be finite")
    if not 0 <= value <= MAX_PLAUSIBLE_DAILY_RAIN_MM:
        raise ValueError(f"implausible daily rainfall value: {value}")
    return value


def sample_daily_rainfall(
    day: date,
    points: Iterable[ClimatePoint],
    *,
    release: str = "final",
    neighborhood_radius: int = 1,
) -> dict[str, object]:
    """Read one CHIRPS cell and its local neighborhood for each point.

    The source is a Cloud-Optimized GeoTIFF. GDAL performs HTTP range requests,
    so this reads only the blocks containing the requested cells rather than
    downloading the global raster.
    """
    if neighborhood_radius < 0 or neighborhood_radius > 4:
        raise ValueError("neighborhood_radius must be between zero and four")

    selected = list(points)
    if not selected:
        raise ValueError("at least one point is required")
    for point in selected:
        validate_point(point)

    try:
        import rasterio
        from rasterio.windows import Window
    except ImportError as error:
        raise RuntimeError(
            "rasterio is required for CHIRPS network reads; "
            "install requirements-pipeline.txt"
        ) from error

    url = chirps_daily_url(day, release)
    gdal_options = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".cog,.tif",
        "GDAL_HTTP_MULTIRANGE": "YES",
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_MAX_RETRY": "3",
        "GDAL_HTTP_RETRY_DELAY": "1",
    }

    samples: list[dict[str, object]] = []
    with rasterio.Env(**gdal_options):
        with rasterio.open(url) as dataset:
            if dataset.count != 1:
                raise ValueError(f"expected one CHIRPS band, found {dataset.count}")
            if dataset.crs is None or not dataset.crs.is_geographic:
                raise ValueError(f"expected a geographic CRS, found {dataset.crs}")

            x_resolution = abs(float(dataset.transform.a))
            y_resolution = abs(float(dataset.transform.e))
            if not (
                math.isclose(x_resolution, 0.05, abs_tol=1e-6)
                and math.isclose(y_resolution, 0.05, abs_tol=1e-6)
            ):
                raise ValueError(
                    "unexpected CHIRPS resolution: "
                    f"{x_resolution} x {y_resolution} degrees"
                )

            for point in selected:
                row, column = dataset.index(point.longitude, point.latitude)
                if not (0 <= row < dataset.height and 0 <= column < dataset.width):
                    raise ValueError(f"{point.name} does not intersect the CHIRPS raster")

                nearest_array = dataset.read(
                    1,
                    window=Window(column, row, 1, 1),
                    masked=True,
                )
                nearest_values = nearest_array.compressed()
                nearest_mm = (
                    validate_rainfall_mm(nearest_values[0])
                    if len(nearest_values)
                    else None
                )

                diameter = neighborhood_radius * 2 + 1
                neighborhood = dataset.read(
                    1,
                    window=Window(
                        column - neighborhood_radius,
                        row - neighborhood_radius,
                        diameter,
                        diameter,
                    ),
                    boundless=True,
                    masked=True,
                )
                neighborhood_values = [
                    validate_rainfall_mm(value)
                    for value in neighborhood.compressed()
                ]
                if not neighborhood_values:
                    raise ValueError(f"{point.name} has no valid nearby CHIRPS cells")

                cell_longitude, cell_latitude = dataset.xy(row, column)
                samples.append(
                    {
                        **asdict(point),
                        "cellCenter": {
                            "latitude": round(float(cell_latitude), 6),
                            "longitude": round(float(cell_longitude), 6),
                        },
                        "nearestCellMm": (
                            round(nearest_mm, 3) if nearest_mm is not None else None
                        ),
                        "neighborhoodMeanMm": round(
                            sum(neighborhood_values) / len(neighborhood_values),
                            3,
                        ),
                        "validNeighborhoodCells": len(neighborhood_values),
                    }
                )

            return {
                "source": "CHIRPS v3 Final RNL",
                "release": release,
                "date": day.isoformat(),
                "url": url,
                "crs": str(dataset.crs),
                "resolutionDegrees": {
                    "longitude": x_resolution,
                    "latitude": y_resolution,
                },
                "rasterShape": {
                    "height": dataset.height,
                    "width": dataset.width,
                },
                "samples": samples,
            }
