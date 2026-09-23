# ERA5-Land temperature progress

Snapshot: 2026-09-23 UTC. Requests are for daily 2 m air-temperature statistics, Madagascar crop, all twelve months, UTC+03:00.

| Year | Daily minimum CDS request | Daily maximum CDS request | State at snapshot | GitHub run |
| --- | --- | --- | --- | --- |
| 1992 | `6b5a0f28-1345-41dc-af98-91bb204b4019` | `f8243025-1bb0-4f63-b84f-bd6ed1ec7607` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35185606127) |
| 1993 | `3bd5aaa6-b1a5-4cff-aed5-f7e0399c6a99` | `e25fcfc9-2d65-4da6-ac25-dcb6d5d228b1` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35423067331) |
| 1994 | `ec4444bc-4f47-4fcc-8fc0-c94a31787177` | `6fa64908-ac1d-4831-94e1-f560b4124fa8` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35423067331) |
| 1995 | `c2c85577-77c6-4a2d-98fa-68be7f99cbd4` | `9a41c315-a08d-4e47-9b47-8d7fa9aa9b4e` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35486816357) |
| 1996 | `c17ab1c5-d33d-44ae-97e3-cb0b082fdf6f` | `67402314-07eb-4aa8-a420-84fbf0049fe3` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35486816357) |
| 1997 | `355436c8-bd6f-4e15-81fb-63ed7b09296e` | `b8d23139-074e-4b2c-b476-87f3c187b1ef` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35700294306) |
| 1998 | `a29c37ba-0edb-4c99-8e7d-924bf135186e` | `0d3c3f00-15bd-46e4-b213-d3a9d5aa21c9` | downloaded, reduced, and durably released | [recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35700294306) |
| 1999 | `20f44651-086d-4047-ae14-37d0c8e9287a` | `e6f2ca75-117e-4cad-8426-11be3793b7b3` | downloaded, reduced, validated, and durably released | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35821859181), [recovery/reduction](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35822042897) |
| 2000 | `49eff449-7357-495a-8420-144098ea4c53` | `4a7976fa-724e-45d3-843d-e2b3d9a7eba7` | downloaded, reduced, validated, and durably released | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35821859181), [recovery/reduction](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35822042897) |
| 2001 | `9b512fce-d2f9-4cc0-84a6-760675749c4c` | `dc1df9de-7996-41c6-8970-cfe78989750e` | minimum accepted; maximum recovered and preserved raw | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35821859181), [recovery](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35822042897) |
| 2002 | `fdca74ee-4b0c-46ad-a59a-03c850b0d3de` | `38a70783-3ce8-4b40-b682-1cef567e1a02` | accepted by CDS; awaiting success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35822042897) |
| 2003 | `44d20286-9d88-4fec-966a-eb7e631a816f` | not submitted | minimum accepted by CDS; awaiting success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35822042897) |

The four unfinished requests are 2001 minimum, both 2002 statistics, and 2003 minimum. Do not submit another request until one of those exact IDs succeeds and is recovered.

## Latest recoveries and manifests

| Item | Payload or manifest SHA-256 | Actions artifact digest |
| --- | --- | --- |
| 1999 daily minimum raw | `45b1cb4fac0d9d078ac2cc2ae6030d9f52ab05f449c36b239fa95fbad6859a2f` | `20c6e2185b6eb4061a2f960bec93e410be1eb95d63e56b3e548af8e6b7cd8ef0` |
| 2000 daily minimum raw | `abe93bee6f26cff08c14bed9b69033d4094c037df77f27083e80ec528f17911b` | `e79be3e18f0323d47f2579de5ab9716d547b4836de0917fe8ea4fb20c10aefe8` |
| 2001 daily maximum raw | `2159e1c3e02612db90c4a152c8582d1b38b1552e3fde466683eb2c98c475864d` | `e555424ebc7ef412ff638b8ba30bdc14aeedab7d425b2be37def91898c15ba4b` |
| 2002 daily minimum manifest | recorded in artifact | `618d3850e6e09217418474f6eccab1975c4002154ca5230376698de60f16f9c9` |
| 2002 daily maximum manifest | recorded in artifact | `cfc83410eaaa51623d475adc0b76010344eae3f41357a83e0e7edc490c97256d` |
| 2003 daily minimum manifest | recorded in artifact | `3f73716683bcd52ee6a02dcc21ea7028b276e8a4004651e7fa456c7b816ac251` |

All six artifacts above expire 2026-12-22. Earlier recovered maximum halves remain preserved: 1999 maximum payload 4,570,057 bytes, Actions digest `331f7f1dbd88d9cb147c81d45044d7916b8a9f45b72712027e60eccc96cb528d`; 2000 maximum payload 4,540,263 bytes, Actions digest `a28014d9fd0b3d3d0f0549195ff3cd414a52e76f8ca05bac3e327d8de149f035`.

## Durable annual partials

Validated annual partials for 1991–2000 and 2020 are preserved in the versioned [`era5-land-annual-partials-v1` release](https://github.com/t-campbell/madagascar-climate-tool/releases/tag/era5-land-annual-partials-v1). Annual archive checksums:

| Year | Release archive SHA-256 | Annual NPZ SHA-256 |
| --- | --- | --- |
| 1991 | `c232af62549483dd6304f4beb4d46306221d62fd641908ea41e02c43e59fef58` | recorded inside archive |
| 1992 | `97f3a664f39e8971bb7eb2c2063a6716a2a30055bd3fb3d67c0032faedf066a5` | recorded inside archive |
| 1993 | `d5cdd57214db472ce81ffe9e21f8b91bf1f0bab11b5ab04bd26c6f3cb1ac24c6` | recorded inside archive |
| 1994 | `1a0a2a380e1726c60cd8d8fb5c5653de3c95e7070e69cfb4eed2f5fa155f05cd` | recorded inside archive |
| 1995 | `ef998bddfe73acbf6a9760c475b5abd52404c075adecfb07ca84913a03a51fb7` | recorded inside archive |
| 1996 | `8c623bcca173f4776926708461d4af6b9bf1719ca4ca81dacde5f44bc0f68479` | recorded inside archive |
| 1997 | `98fc3b9fa892f2e07e8baa6b71941fb9a36b939177df3378d19f80ae242b7a13` | recorded inside archive |
| 1998 | `f84ad040f091465c38d02e33cb6b20912d7cb8c95088e77e72509cc5ecc6c34a` | recorded inside archive |
| 1999 | `c91005d0fe5dbfa81fc0c8bb741623698f5b3b7a8a3ddae192b62af4af752066` | `841f38c36f11ba26917f88e7208c855e92e16f9721f678c8a5efffb94db38e13` |
| 2000 | `6b4db6da3730c9c033e709753e9308187f4de736f008d6f2095b7797590aa366` | `33253bdeea1696a047c4d5955b18aff596a350a74e0734ab720c18107777d82a` |
| 2020 | `97d874aaa7b34145114dc8f3653d7fefe0edaedb1c7cf046f9776f40cdc21bde` | recorded inside archive |

The 1999 and 2000 Actions partial artifacts have digests `dbfa79769b9269d779804ca8851f3e8f760b7892ce41b77bbf44981edfcafb7a` and `d8364d5b7455c1a0e49a30d3037ecd56875f0000f6963f66a1fe8d137ed8cf95`, respectively. Their source and manifest checksums are in the release sidecars `era5-1999-SHA256SUMS` and `era5-2000-SHA256SUMS`.

CDS rejects two-year requests at this spatial and temporal extent with “cost limits exceeded”; annual requests are the validated maximum size. Keep no more than four unfinished requests. Recover any successful existing ID before submitting at most one chronological replacement slot; never resubmit an already recorded year/statistic.

These temperature partials are not yet published on the rainfall demo site. Add each newly validated annual partial to a versioned release before its Actions artifact expires.
