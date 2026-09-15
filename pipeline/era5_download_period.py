"""Submit and recover bounded ERA5-Land daily-statistics requests."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from pipeline.era5_land import CDS_API_URL
from pipeline.sources import era5_land_period_request


READY_STATUS = "successful"
PENDING_STATUSES = frozenset({"accepted", "running"})


class RequestNotReadyError(RuntimeError):
    """Raised when a submitted CDS request has not finished processing."""


def parse_months_csv(value: str) -> tuple[int, ...]:
    """Parse a comma-separated month list used by GitHub workflow inputs."""
    try:
        months = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    except ValueError as error:
        raise ValueError("months must be comma-separated integers") from error
    if not months:
        raise ValueError("at least one month is required")
    return months


def _api_token(api_token: str | None) -> str:
    token = api_token or os.environ.get("CDS_API_TOKEN")
    if not token:
        raise RuntimeError("CDS_API_TOKEN is not set")
    return token


def _client(token: str, *, wait_until_complete: bool):
    try:
        import cdsapi
    except ImportError as error:
        raise RuntimeError("cdsapi is required for ERA5-Land requests") from error

    return cdsapi.Client(
        url=CDS_API_URL,
        key=token,
        wait_until_complete=wait_until_complete,
        delete=False,
    )


def _write_manifest(manifest: dict[str, object], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def submit_period(
    year: int,
    months: tuple[int, ...],
    statistic: str,
    manifest_output: Path,
    *,
    api_token: str | None = None,
    client=None,
) -> dict[str, object]:
    """Submit without blocking and preserve the request ID for later recovery."""
    dataset, request = era5_land_period_request(year, months, statistic)
    active_client = client or _client(
        _api_token(api_token),
        wait_until_complete=False,
    )
    remote = active_client.retrieve(dataset, request)
    manifest: dict[str, object] = {
        "dataset": dataset,
        "requestId": remote.request_id,
        "statusAtSubmission": remote.status,
        "year": year,
        "months": list(months),
        "statistic": statistic,
    }
    _write_manifest(manifest, manifest_output)
    print(json.dumps(manifest, sort_keys=True))
    return manifest


def recover_request(
    request_id: str,
    output: Path,
    *,
    api_token: str | None = None,
    client=None,
) -> dict[str, object]:
    """Download a previously submitted request once CDS marks it successful."""
    active_client = client or _client(
        _api_token(api_token),
        wait_until_complete=False,
    )
    datastore_client = getattr(active_client, "client", None)
    if datastore_client is None or not hasattr(datastore_client, "get_remote"):
        raise RuntimeError("installed cdsapi client cannot recover requests by ID")
    remote = datastore_client.get_remote(request_id)
    status = remote.status
    if status in PENDING_STATUSES:
        raise RequestNotReadyError(f"CDS request {request_id} is still {status}")
    if status != READY_STATUS:
        raise RuntimeError(f"CDS request {request_id} ended with status {status}")

    output.parent.mkdir(parents=True, exist_ok=True)
    remote.download(str(output))
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("CDS request completed without a usable output file")
    result: dict[str, object] = {
        "requestId": request_id,
        "status": status,
        "output": str(output),
        "bytes": output.stat().st_size,
    }
    print(json.dumps(result, sort_keys=True))
    return result


def download_period(
    year: int,
    months: tuple[int, ...],
    statistic: str,
    output: Path,
    *,
    api_token: str | None = None,
) -> Path:
    """Compatibility helper for a synchronous request and download."""
    token = _api_token(api_token)
    dataset, request = era5_land_period_request(year, months, statistic)
    output.parent.mkdir(parents=True, exist_ok=True)
    client = _client(token, wait_until_complete=True)
    client.retrieve(dataset, request, str(output))
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("CDS request completed without a usable output file")
    print(f"downloaded {output} ({output.stat().st_size} bytes)")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit = subparsers.add_parser("submit")
    submit.add_argument("--year", type=int, required=True)
    submit_months = submit.add_mutually_exclusive_group(required=True)
    submit_months.add_argument("--months", nargs="+", type=int)
    submit_months.add_argument("--months-csv")
    submit.add_argument(
        "--statistic",
        choices=("daily_minimum", "daily_maximum"),
        required=True,
    )
    submit.add_argument("--manifest", type=Path, required=True)

    recover = subparsers.add_parser("recover")
    recover.add_argument("--request-id", required=True)
    recover.add_argument("--output", type=Path, required=True)

    arguments = parser.parse_args()
    if arguments.command == "submit":
        months = (
            tuple(arguments.months)
            if arguments.months is not None
            else parse_months_csv(arguments.months_csv)
        )
        submit_period(
            arguments.year,
            months,
            arguments.statistic,
            arguments.manifest,
        )
    else:
        recover_request(arguments.request_id, arguments.output)


if __name__ == "__main__":
    main()
