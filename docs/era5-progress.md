# ERA5-Land temperature progress

Snapshot: 2026-09-17 UTC. Requests are for daily 2 m air-temperature statistics, Madagascar crop, all twelve months, UTC+03:00.

| Year | Daily minimum CDS request | Daily maximum CDS request | State at snapshot | GitHub run |
| --- | --- | --- | --- | --- |
| 1992 | `6b5a0f28-1345-41dc-af98-91bb204b4019` | `f8243025-1bb0-4f63-b84f-bd6ed1ec7607` | downloaded and reduced; partial archived | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35185606127) |
| 1993 | `3bd5aaa6-b1a5-4cff-aed5-f7e0399c6a99` | `e25fcfc9-2d65-4da6-ac25-dcb6d5d228b1` | accepted by CDS; await success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35185732011) |
| 1994 | `ec4444bc-4f47-4fcc-8fc0-c94a31787177` | `6fa64908-ac1d-4831-94e1-f560b4124fa8` | accepted by CDS; await success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35185732011) |

1991 and 2020 have earlier successful reduced partials in the GitHub Actions artifacts. The 1992 partial is named `era5-1992-grid-partial` in its recovery run. Download and retain these outside GitHub Actions before artifact retention expires; the 1992 artifact is set to 90 days. The 1993 and 1994 request manifests are named `era5-request-YYYY-minimum` and `era5-request-YYYY-maximum` and are retained for 90 days.

The two-year 1993–1994 request was rejected immediately by CDS with “cost limits exceeded”; it generated no queued data. The annual replacements above succeeded. When both requests for a year show `successful` in CDS, run `ERA5-Land period recovery` with that year, all twelve months, and the two IDs above. Do not submit that year again.

These temperature partials are not yet published on the rainfall demo site.