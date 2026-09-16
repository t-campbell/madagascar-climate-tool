"""Source request construction for CHIRPS v3 and ERA5-Land.

This module performs no network calls. Keeping request construction pure makes
upstream filename or API changes visible in tests before an expensive build.
"""

from __future__ import annotations

from datetime import date


CHIRPS_BASE = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily"
MADAGASCAR_AREA = [-11.0, 43.0, -26.0, 51.0]  # north, west, south, east


def chirps_daily_url(day: date, release: str = "final") -> str:
    """Return the authoritative daily raster URL for a CHIRPS v3 release.

    Final RNL data have Cloud-Optimized GeoTIFFs suitable for spatial HTTP range
    reads. Preliminary SAT data currently use ordinary TIFFs and should only be
    acquired for recent observations.
    """
    stamp = day.isoformat().replace("-", ".")
    if release == "final":
        return (
            f"{CHIRPS_BASE}/final/rnl/cogs/{day.year}/"
            f"chirps-v3.0.rnl.{stamp}.cog"
        )
    if release == "preliminary":
        return (
            f"{CHIRPS_BASE}/prelim/sat/{day.year}/"
            f"chirps-v3.0.prelim.{stamp}.tif"
        )
    raise ValueError("release must be 'final' or 'preliminary'")


def era5_land_daily_request(
    year: int,
    month: int,
    statistic: str,
) -> tuple[str, dict[str, object]]:
    """Build a CDS request for daily 2 m temperature over Madagascar."""
    if statistic not in {"daily_minimum", "daily_maximum", "daily_mean"}:
        raise ValueError("unsupported daily statistic")
    dataset = "derived-era5-land-daily-statistics"
    request: dict[str, object] = {
        "variable": ["2m_temperature"],
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": [f"{day:02d}" for day in range(1, 32)],
        "daily_statistic": statistic,
        "time_zone": "utc+03:00",
        "frequency": "1_hourly",
        "area": MADAGASCAR_AREA,
        "data_format": "netcdf",
    }
    return dataset, request



def era5_land_period_request(
    year: int,
    months: tuple[int, ...],
    statistic: str,
) -> tuple[str, dict[str, object]]:
    """Build a bounded ERA5-Land daily request for selected months."""
    return era5_land_multi_year_request((year,), months, statistic)


def era5_land_multi_year_request(
    years: tuple[int, ...],
    months: tuple[int, ...],
    statistic: str,
) -> tuple[str, dict[str, object]]:
    """Build one bounded request spanning complete selected years and months."""
    if not years or len(years) != len(set(years)):
        raise ValueError("years must be a non-empty sequence without duplicates")
    if tuple(sorted(years)) != years:
        raise ValueError("years must be sorted")
    if not months or len(months) != len(set(months)):
        raise ValueError("months must be a non-empty sequence without duplicates")
    if any(month < 1 or month > 12 for month in months):
        raise ValueError("months must be between 1 and 12")
    dataset, request = era5_land_daily_request(years[0], months[0], statistic)
    request["year"] = [str(year) for year in years]
    request["month"] = [f"{month:02d}" for month in months]
    request["area"] = [-10.9, 42.9, -26.1, 51.1]
    return dataset, request


def era5_land_year_request(
    year: int,
    statistic: str,
) -> tuple[str, dict[str, object]]:
    """Build one complete-year ERA5-Land daily temperature request."""
    return era5_land_period_request(year, tuple(range(1, 13)), statistic)
