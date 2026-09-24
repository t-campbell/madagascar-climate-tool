# ERA5-Land temperature progress

Snapshot: 2026-09-24 UTC. Requests are for daily 2 m air-temperature statistics, Madagascar crop, all twelve months, UTC+03:00.

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
| 2001 | `9b512fce-d2f9-4cc0-84a6-760675749c4c` | `dc1df9de-7996-41c6-8970-cfe78989750e` | downloaded, reduced, validated, and durably released | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35895586792), [recovery/reduction](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35895837602) |
| 2002 | `fdca74ee-4b0c-46ad-a59a-03c850b0d3de` | `38a70783-3ce8-4b40-b682-1cef567e1a02` | downloaded, reduced, validated, and durably released | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35895586792), [recovery/reduction](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35895837602) |
| 2003 | `44d20286-9d88-4fec-966a-eb7e631a816f` | `ebc41bdc-27b3-40e3-bc64-ecfd50151bac` | downloaded, reduced, validated, and durably released | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35959946119), [recovery/reduction](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/35960052314) |
| 2004 | `064dae72-c369-4418-9e5a-235e53b3dbff` | `bf2b6c96-f6dc-49eb-b582-f31f39f57801` | downloaded, reduced, validated, and durably released | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032319335), [recovery/reduction](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032461975) |
| 2005 | `75155360-f455-490c-93b2-f0d89bf8cb83` | `5f0de974-378e-40e4-90a5-cb2039d43e18` | minimum recovered and preserved raw; maximum accepted | [probe](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032319335), [minimum recovery](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032461975) |
| 2006 | `87c55b03-0837-4ca5-b85b-34dc184866c7` | `043fd5e2-a3cf-4e83-ba59-dea3c23f4d1d` | accepted by CDS; awaiting success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032461975) |
| 2007 | `078cf2e1-2cef-4b69-bc36-227c3ecf2408` | not submitted | minimum accepted by CDS; awaiting success | [submission run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032461975) |

The four unfinished requests are 2005 maximum, both 2006 statistics, and 2007 minimum. Do not submit another request until one of those exact IDs succeeds and is recovered.

## Latest recoveries and manifests

The [2004–2005 recovery run](https://github.com/t-campbell/madagascar-climate-tool/actions/runs/36032461975) preserved the three successful raw results and the three replacement manifests below. All expire 2026-12-23.

| Item | Payload SHA-256 or request ID | Actions artifact digest |
| --- | --- | --- |
| 2004 daily minimum raw | `71f12d218b1aa84173a05f17a3ec819bc215df013e67260edccca8c4fb08a2a0` | `036fa6ec51a6aec25105684810c8b68ad522455db28c72da08aa16898c6056da` |
| 2004 daily maximum raw | `7a8f9722a79e2c49266b7753d4dbf6963d9caf47adae5c100f3a42b2be32afac` | `c5870733884aaeba8b376a5f5d7c70770ddea55e7c02abc6da7cc934846d5f80` |
| 2005 daily minimum raw | `847d5359ba984066d6ed80a724c01a3de2ac4943d4f6a4278134dc3c403eac11` | `7bec7c24579fc5892c2311d8bd8788f06705d1c98af5663d45312ec2ee4dc8e9` |
| 2006 daily minimum manifest | `87c55b03-0837-4ca5-b85b-34dc184866c7` | `561b9fc66bbbe7bb920a0d2001f21b59cf8a381c7be7296c7213c5f176b07b59` |
| 2006 daily maximum manifest | `043fd5e2-a3cf-4e83-ba59-dea3c23f4d1d` | `857b073cc3ae70f3c91ddb9c7e5165e51cffdf35ef8aa8f159188453491bdc1c` |
| 2007 daily minimum manifest | `078cf2e1-2cef-4b69-bc36-227c3ecf2408` | `956cc605f032bbf884c55beaf629d8618cc1ad362169e800f827898a4214ca35` |

## Durable annual partials

Validated annual partials for 1991–2004 and 2020 are preserved in the versioned [`era5-land-annual-partials-v1` release](https://github.com/t-campbell/madagascar-climate-tool/releases/tag/era5-land-annual-partials-v1). Annual archive checksums:

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
| 2001 | `5bd2e1bd1c3952921236730aca2989e55ce66561bad5f27c1b576aaffad4d915` | `8dccfd42eef26378b2230ba1c03619fd2c94cf77eea84a1e0d2c6af59808ddb2` |
| 2002 | `8456c517d2234a38e4b6fb66b7962dc3171c3e53785091f8ce59a4549f0b0c51` | `fe26a4928784e343464828d5d21cf9e72a80951bfa367562c309081945e0ad4b` |
| 2003 | `d451cc26d2785c90dcdb39d9219731b89f53d4b54509f30e7cb7ff10da87a145` | `47223c77a8837ee2150935b8cc682c13862baa1532bfd3d22e06b56448b032e8` |
| 2004 | `7543d9456e7c3ff8ec2ed22a944ce99b55697ac8082986a9f2cfc4021801cb14` | `e9f9ee739dce1b4bb9bec9dd39f8782ab3a2788c4a6b1aa7ecd5a5b9cc404b35` |
| 2020 | `97d874aaa7b34145114dc8f3653d7fefe0edaedb1c7cf046f9776f40cdc21bde` | recorded inside archive |

The 1999–2004 Actions partial artifact digests are `dbfa79769b9269d779804ca8851f3e8f760b7892ce41b77bbf44981edfcafb7a`, `d8364d5b7455c1a0e49a30d3037ecd56875f0000f6963f66a1fe8d137ed8cf95`, `3613271f4d32629d06e93331681ff3a77505896795fcc040880802d1818bf542`, `e6aa55613134c78129409e9f7a3a0dde4528b107bc442e0f4d48893388166cd2`, `ce9d58a6fd35652beaa88ca648286f4cfe810a5a09c9c07c39f5010f6b2ce307`, and `f842b9684151230c69da78a698eb75d6dc3e235c2f5cfc808c4aaf2a9d2528ea`. Source and manifest checksums are in their matching release sidecars.

CDS rejects two-year requests at this spatial and temporal extent with “cost limits exceeded”; annual requests are the validated maximum size. Keep no more than four unfinished requests. Recover any successful existing ID before submitting at most one chronological replacement slot; never resubmit an already recorded year/statistic.

These temperature partials are not yet published on the rainfall demo site. Add each newly validated annual partial to a versioned release before its Actions artifact expires.
