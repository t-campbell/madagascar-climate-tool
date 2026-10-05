# Monthly rainfall launch record

Verified on 2026-10-05. Latest complete Final month: August 2026. Active coverage: September 2025 through August 2026, with all daily observations present on all 22,526 baseline land cells and 92 transport tiles.

## Durable inputs

The historical baseline is in [chirps-baseline-v1](https://github.com/t-campbell/madagascar-climate-tool/releases/tag/chirps-baseline-v1). The NPZ SHA-256 is `e03174e20c25a86d8ca106cadce5fa9ef12f58489bdf6c4a12b9a30787a48807`. It was copied, downloaded again, and verified in [preservation run 37335294481](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/37335294481), removing reliance on the October 14 Actions artifact expiry.

All twelve monthly NPZ reductions, JSON provenance, and NPZ checksum sidecars are individually bundled in `chirps-month-YYYY-MM.zip` assets in [chirps-monthly-v1](https://github.com/t-campbell/madagascar-climate-tool/releases/tag/chirps-monthly-v1). Each upload was downloaded and verified before proceeding to the next month. No CDS request was made.

## First verified publication

- Release: `b5c52f289d21f8db01f8`.
- Publication identity SHA-256: `b5c52f289d21f8db01f8ad0e4d8ed52bbad8ac02c9cd4cf4e3cbd1e445942b39`.
- Data through: `2026-08-31`.
- Durable snapshot: `recent-release-b5c52f289d21f8db01f8.tar.gz` in `chirps-monthly-v1`, with a SHA-256 sidecar.
- Snapshot SHA-256: `fed0c85397891d81f23838b549216c40fb80c569ae2fde289550ed9ce4111efa`.
- [End-to-end verification run 37340202372](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/37340202372) passed 54 Python tests, the JavaScript comparison checks, candidate checks, staging smoke tests, production smoke tests, and an unchanged rerun that acquired no daily data and returned `publish=false`.
- August rainfall at tested cells: Fenoarivo 240.7 mm, Antananarivo 11.3 mm, Toliara 5.8 mm. The interface displays whole mm.
- Cloudflare production version: `939da996-13d9-492b-837f-f209f69f4af5`.

Initial attempts exposed an HTTP-client compatibility issue (Python requests returned 403 while curl succeeded) and an immediate post-deployment response from an older edge publication. Checks now use curl, exact expected release IDs, and bounded propagation retries. Neither issue required a second backfill. The failure issue opened automatically and closed after recovery.

The temporary push trigger and idle-test step were removed after the passing run. The permanent workflow checks Fridays at 03:17 UTC, publishes only complete new Final months or a needed recovery, and supports manual reruns. The separate read-only watchdog checks freshness and workflow continuity; routine data work needs neither an AI session nor browser sign-in.

Historical rainfall and temperature remain fixed at 1991–2020. The website's recent panel and methods are available in English and Malagasy, with observation dates visible in cached reports.
