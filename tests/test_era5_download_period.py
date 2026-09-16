import json
from pathlib import Path
import tempfile
import unittest

from pipeline.era5_download_period import (
    RequestNotReadyError,
    parse_months_csv,
    parse_years_csv,
    recover_request,
    submit_period,
    submit_years,
)


class FakeRemote:
    def __init__(self, request_id="request-123", status="accepted", payload=b"data"):
        self.request_id = request_id
        self.status = status
        self.payload = payload

    def download(self, target):
        Path(target).write_bytes(self.payload)


class FakeDatastoreClient:
    def __init__(self, remote):
        self.remote = remote
        self.requested_id = None

    def get_remote(self, request_id):
        self.requested_id = request_id
        return self.remote


class FakeClient:
    def __init__(self, remote):
        self.remote = remote
        self.client = FakeDatastoreClient(remote)
        self.submission = None

    def retrieve(self, dataset, request):
        self.submission = (dataset, request)
        return self.remote


class Era5DownloadPeriodTests(unittest.TestCase):
    def test_month_csv_is_parsed_for_workflow_inputs(self):
        self.assertEqual(parse_months_csv("1, 2,3"), (1, 2, 3))

    def test_invalid_month_csv_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_months_csv("1,banana,3")

    def test_year_csv_is_parsed_for_block_workflows(self):
        self.assertEqual(parse_years_csv("1991, 1992,1993"), (1991, 1992, 1993))

    def test_unsorted_year_csv_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_years_csv("1992,1991")

    def test_submit_writes_resumable_manifest(self):
        remote = FakeRemote()
        client = FakeClient(remote)
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "request.json"
            manifest = submit_period(
                2020,
                (1, 2, 3),
                "daily_maximum",
                manifest_path,
                client=client,
            )
            saved = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["requestId"], "request-123")
        self.assertEqual(saved, manifest)
        self.assertEqual(saved["months"], [1, 2, 3])
        self.assertEqual(client.submission[0], "derived-era5-land-daily-statistics")

    def test_submit_writes_multi_year_manifest(self):
        remote = FakeRemote()
        client = FakeClient(remote)
        with tempfile.TemporaryDirectory() as directory:
            manifest = submit_years(
                (1991, 1992, 1993, 1994, 1995),
                tuple(range(1, 13)),
                "daily_minimum",
                Path(directory) / "request.json",
                client=client,
            )

        self.assertEqual(manifest["years"], [1991, 1992, 1993, 1994, 1995])
        self.assertNotIn("year", manifest)
        self.assertEqual(
            client.submission[1]["year"],
            ["1991", "1992", "1993", "1994", "1995"],
        )

    def test_recover_downloads_successful_request(self):
        remote = FakeRemote(status="successful", payload=b"netcdf")
        client = FakeClient(remote)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.nc"
            result = recover_request("request-456", output, client=client)
            payload = output.read_bytes()

        self.assertEqual(payload, b"netcdf")
        self.assertEqual(result["bytes"], 6)
        self.assertEqual(client.client.requested_id, "request-456")

    def test_recover_rejects_pending_request_without_download(self):
        remote = FakeRemote(status="running")
        client = FakeClient(remote)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.nc"
            with self.assertRaises(RequestNotReadyError):
                recover_request("request-789", output, client=client)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
