"""Download and sample ERA5-Land daily temperature data from CDS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import math
import os
from pathlib import Path
from typing import Iterable

from pipeline.chirps import ClimatePoint
from pipeline.sources import era5_land_daily_request


CDS_API_URL = "https://cds.climate.copernicus.eu/api"


@dataclass(frozen=True)
class TemperatureSample:
    id: str
    name: str
    latitude: float
    longitude: float
    cell_latitude: float
    cell_longitude: float
    temperature_c: float
    used_land_fallback: bool


def _coordinate_name(dataset, candidates: tuple[str, ...]) -> str:
    for name in candidates:
        if name in dataset.coords:
            return name
    raise ValueError(f"none of the expected coordinates are present: {candidates}")


def _temperature_variable(dataset) -> str:
    candidates = [
        name
        for name, variable in dataset.data_vars.items()
        if variable.dtype.kind in "fiu"
    ]
    if len(candidates) != 1:
        raise ValueError(
            "expected exactly one numeric temperature variable, "
            f"found {candidates}"
        )
    return candidates[0]


def _to_celsius(value: float, units: str | None) -> float:
    normalized = (units or "").strip().lower()
    if normalized in {"k", "kelvin"} or value > 150:
        return value - 273.15
    if normalized in {"c", "°c", "degc", "degree_celsius", "degrees_celsius"}:
        return value
    raise ValueError(f"cannot determine temperature units: {units!r}")


def request_daily_temperature(
    day: date,
    statistic: str,
    destination: Path,
    *,
    api_token: str | None = None,
) -> Path:
    """Request one daily statistic for all of Madagascar as NetCDF."""
    token = api_token or os.environ.get("CDS_API_TOKEN")
    if not token:
        raise RuntimeError("CDS_API_TOKEN is not set")

    try:
        import cdsapi
    except ImportError as error:
        raise RuntimeError("cdsapi is required for live ERA5-Land requests") from error

    dataset, request = era5_land_daily_request(day.year, day.month, statistic)
    request["day"] = [f"{day.day:02d}"]
    destination.parent.mkdir(parents=True, exist_ok=True)

    client = cdsapi.Client(url=CDS_API_URL, key=token)
    client.retrieve(dataset, request, str(destination))
    return destination


def sample_temperature_file(
    source: Path,
    points: Iterable[ClimatePoint],
) -> list[TemperatureSample]:
    """Sample a downloaded ERA5-Land NetCDF at the nearest native grid cell."""
    try:
        import xarray as xr
    except ImportError as error:
        raise RuntimeError("xarray is required to read ERA5-Land NetCDF") from error

    with xr.open_dataset(source) as dataset:
        latitude_name = _coordinate_name(dataset, ("latitude", "lat"))
        longitude_name = _coordinate_name(dataset, ("longitude", "lon"))
        variable_name = _temperature_variable(dataset)
        temperature = dataset[variable_name].squeeze(drop=True)
        units = temperature.attrs.get("units")

        extra_dimensions = set(temperature.dims) - {
            latitude_name,
            longitude_name,
        }
        if extra_dimensions:
            raise ValueError(
                "temperature variable has unexpected dimensions after squeeze: "
                f"{sorted(extra_dimensions)}"
            )

        samples: list[TemperatureSample] = []
        latitude = temperature[latitude_name]
        longitude = temperature[longitude_name]
        for point in points:
            nearest_latitude = int(abs(latitude - point.latitude).argmin().item())
            nearest_longitude = int(abs(longitude - point.longitude).argmin().item())
            best: tuple[float, float, float, float, bool] | None = None
            longitude_scale = math.cos(math.radians(point.latitude))

            for latitude_index in range(
                max(0, nearest_latitude - 2),
                min(latitude.size, nearest_latitude + 3),
            ):
                for longitude_index in range(
                    max(0, nearest_longitude - 2),
                    min(longitude.size, nearest_longitude + 3),
                ):
                    selected = temperature.isel(
                        {
                            latitude_name: latitude_index,
                            longitude_name: longitude_index,
                        }
                    )
                    value = float(selected.item())
                    if not math.isfinite(value):
                        continue
                    cell_latitude = float(latitude.isel(
                        {latitude_name: latitude_index}
                    ).item())
                    cell_longitude = float(longitude.isel(
                        {longitude_name: longitude_index}
                    ).item())
                    distance = (
                        (cell_latitude - point.latitude) ** 2
                        + (
                            (cell_longitude - point.longitude)
                            * longitude_scale
                        ) ** 2
                    )
                    candidate = (
                        distance,
                        value,
                        cell_latitude,
                        cell_longitude,
                        latitude_index != nearest_latitude
                        or longitude_index != nearest_longitude,
                    )
                    if best is None or candidate[0] < best[0]:
                        best = candidate

            if best is None:
                raise ValueError(
                    f"no valid ERA5-Land cell within 0.2 degrees of {point.name}"
                )

            _, value, cell_latitude, cell_longitude, used_land_fallback = best
            samples.append(
                TemperatureSample(
                    id=point.id,
                    name=point.name,
                    latitude=point.latitude,
                    longitude=point.longitude,
                    cell_latitude=cell_latitude,
                    cell_longitude=cell_longitude,
                    temperature_c=round(_to_celsius(value, units), 2),
                    used_land_fallback=used_land_fallback,
                )
            )
    return samples


def samples_as_dicts(
    samples: Iterable[TemperatureSample],
) -> list[dict[str, object]]:
    return [asdict(sample) for sample in samples]
