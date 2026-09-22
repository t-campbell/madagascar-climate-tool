# ERA5-Land temperature progress

Snapshot: 2026-09-22 UTC. Requests are for daily 2 m air-temperature statistics, Madagascar crop, all twelve months, UTC+03:00.

| Year | Daily minimum CDS request | Daily maximum CDS request | State at snapshot | GitHub run |
| --- | --- | --- | --- | --- |
| 1992 | `6b5a0f28-1345-41dc-af98-91bb204b4019` | `f8243025-1bb0-4f63-b84f-bd6ed1ec7607` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35185606127) |
| 1993 | `3bd5aaa6-b1a5-4cff-aed5-f7e0399c6a99` | `e25fcfc9-2d65-4da6-ac25-dcb6d5d228b1` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35423067331) |
| 1994 | `ec4444bc-4f47-4fcc-8fc0-c94a31787177` | `6fa64908-ac1d-4831-94e1-f560b4124fa8` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35423067331) |
| 1995 | `c2c85577-77c6-4a2d-98fa-68be7f99cbd4` | `9a41c315-a08d-4e47-9b47-8d7fa9aa9b4e` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35486816357) |
| 1996 | `c17ab1c5-d33d-44ae-97e3-cb0b082fdf6f` | `67402314-07eb-4aa8-a420-84fbf0049fe3` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35486816357) |
| 1997 | `355436c8-bd6f-4e15-81fb-63ed7b09296e` | `b8d23139-074e-4b2c-b476-87f3c187b1ef` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35700294306) |
| 1998 | `a29c37ba-0edb-4c99-8e7d-924bf135186e` | `0d3c3f00-15bd-46e4-b213-d3a9d5aa21c9` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35700294306) |
| 1999 | `20f44651-086d-4047-ae14-37d0c8e9287a` | `e6f2ca75-117e-4cad-8426-11be3793b7b3` | minimum accepted; maximum recovered and preserved raw | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35760603428), [recovery](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35760845298) |
| 2000 | `49eff449-7357-495a-8420-144098ea4c53` | `4a7976fa-724e-45d3-843d-e2b3d9a7eba7` | minimum running; maximum recovered and preserved raw | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35760603428), [recovery](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35760845298) |
| 2001 | `9b512fce-d2f9-4cc0-84a6-760675749c4c` | `dc1df9de-7996-41c6-8970-cfe78989750e` | accepted by CDS; awaiting success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35760845298) |

1999 maximum raw result: artifact `era5-raw-1999-daily-maximum` (4,570,057-byte payload), Actions artifact digest `sha256:331f7f1dbd88d9cb147c81d45044d7916b8a9f45b72712027e60eccc96cb528d`, expires 2026-12-21. 2000 maximum raw result: artifact `era5-raw-2000-daily-maximum` (4,540,263-byte payload), Actions artifact digest `sha256:a28014d9fd0b3d3d0f0549195ff3cd414a52e76f8ca05bac3e327d8de149f035`, expires 2026-12-21. Each artifact also contains the payload's SHA-256 sidecar.

## Durable annual partials

Validated annual partials for 1991–1998 and 2020 are preserved in the versioned [`era5-land-annual-partials-v1` release](https://github.com/t-campbell/madagascar-climate-tool/releases/tag/era5-land-annual-partials-v1). The [preservation run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35761436080) downloaded the exact Actions artifact ZIPs, verified every archive, generated `SHA256SUMS`, and uploaded these immutable named assets:

| Year | Release asset SHA-256 |
| --- | --- |
| 1991 | `c232af62549483dd6304f4beb4d46306221d62fd641908ea41e02c43e59fef58` |
| 1992 | `97f3a664f39e8971bb7eb2c2063a6716a2a30055bd3fb3d67c0032faedf066a5` |
| 1993 | `d5cdd57214db472ce81ffe9e21f8b91bf1f0bab11b5ab04bd26c6f3cb1ac24c6` |
| 1994 | `1a0a2a380e1726c60cd8d8fb5c5653de3c95e7070e69cfb4eed2f5fa155f05cd` |
| 1995 | `ef998bddfe73acbf6a9760c475b5abd52404c075adecfb07ca84913a03a51fb7` |
| 1996 | `8c623bcca173f4776926708461d4af6b9bf1719ca4ca81dacde5f44bc0f68479` |
| 1997 | `98fc3b9fa892f2e07e8baa6b71941fb9a36b939177df3378d19f80ae242b7a13` |
| 1998 | `f84ad040f091465c38d02e33cb6b20912d7cb8c95088e77e72509cc5ecc6c34a` |
| 2020 | `97d874aaa7b34145114dc8f3653d7fefe0edaedb1c7cf046f9776f40cdc21bde` |

CDS rejects two-year requests at this spatial and temporal extent with “cost limits exceeded”; annual requests are the validated maximum size. Keep no more than four unfinished requests. Recover any successful existing ID before submitting at most one chronological replacement slot; never resubmit an already recorded year/statistic.

These temperature partials are not yet published on the rainfall demo site. Add each newly validated annual partial to a later versioned release before its Actions artifact expires.
