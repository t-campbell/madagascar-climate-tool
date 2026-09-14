"""Download and sample ERA5-Land daily temperature data from CDS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
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
        for point in points:
            selected = temperature.sel(
                {
                    latitude_name: point.latitude,
                    longitude_name: point.longitude,
                },
                method="nearest",
            )
            value = float(selected.item())
            samples.append(
                TemperatureSample(
                    id=point.id,
                    name=point.name,
                    latitude=point.latitude,
                    longitude=point.longitude,
                    cell_latitude=float(selected[latitude_name].item()),
                    cell_longitude=float(selected[longitude_name].item()),
                    temperature_c=round(_to_celsius(value, units), 2),
                )
            )
    return samples


def samples_as_dicts(
    samples: Iterable[TemperatureSample],
) -> list[dict[str, object]]:
    return [asdict(sample) for sample in samples]
