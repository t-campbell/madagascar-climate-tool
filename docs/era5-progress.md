# ERA5-Land temperature progress

Snapshot: 2026-09-20 UTC. Requests are for daily 2 m air-temperature statistics, Madagascar crop, all twelve months, UTC+03:00.

| Year | Daily minimum CDS request | Daily maximum CDS request | State at snapshot | GitHub run |
| --- | --- | --- | --- | --- |
| 1992 | `6b5a0f28-1345-41dc-af98-91bb204b4019` | `f8243025-1bb0-4f63-b84f-bd6ed1ec7607` | downloaded and reduced; partial archived | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35185606127) |
| 1993 | `3bd5aaa6-b1a5-4cff-aed5-f7e0399c6a99` | `e25fcfc9-2d65-4da6-ac25-dcb6d5d228b1` | downloaded and reduced; partial archived | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35423067331) |
| 1994 | `ec4444bc-4f47-4fcc-8fc0-c94a31787177` | `6fa64908-ac1d-4831-94e1-f560b4124fa8` | downloaded and reduced; partial archived | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35423067331) |
| 1995 | `c2c85577-77c6-4a2d-98fa-68be7f99cbd4` | `9a41c315-a08d-4e47-9b47-8d7fa9aa9b4e` | downloaded and reduced; partial archived | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35486816357) |
| 1996 | `c17ab1c5-d33d-44ae-97e3-cb0b082fdf6f` | `67402314-07eb-4aa8-a420-84fbf0049fe3` | downloaded and reduced; partial archived | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35486816357) |

1991 and 2020 have earlier successful reduced partials in GitHub Actions artifacts. Reduced artifacts for 1992–1996 are named `era5-YYYY-grid-partial` in their recovery runs and are retained for 90 days. Raw downloads have shorter retention and are not needed after a validated partial exists.

CDS rejects two-year requests at this spatial and temporal extent with “cost limits exceeded”; annual requests are the validated maximum size. When both requests for a future year show `successful` in CDS, recover the existing IDs rather than submitting that year again.

These temperature partials are not yet published on the rainfall demo site. Before assembling the complete 1991–2020 normal, download or otherwise durably retain every reduced annual partial; GitHub Actions artifacts expire.