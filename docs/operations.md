# Operations

## Active products

The site serves fixed 1991–2020 CHIRPS Final rainfall and ERA5-Land temperature baselines, a GeoNames place index, and the latest twelve complete CHIRPS Final RNL rainfall months. It has no runtime CDS dependency or daily observation job. The historical normal never advances with the recent panel.

## Autonomous monthly update

The `update monthly rainfall` GitHub Actions workflow checks weekly on Friday at 03:17 UTC (06:17 Madagascar). Final data normally arrive in week three of the following month. Only complete Final months are accepted; the pipeline neither publishes partial months nor requests CDS data.

Each month is reduced on the established CHIRPS grid and uploaded immediately to the durable `chirps-monthly-v1` release with provenance and SHA-256. The baseline is downloaded from `chirps-baseline-v1` and verified against `SHA256SUMS`. Actions artifacts contain diagnostics only and are never the sole copy of input data.

A candidate has twelve consecutive complete months, matching immutable tile URLs, preserved historical references, and `data/update-status.json`. Tests and three sample locations must pass on staging before the data commit and production deployment. Production is smoke-tested afterward. No new month and no missed deployment means no commit or deploy.

GitHub and Cloudflare secrets already used for deployment are sufficient. The browser receives no secrets. The monthly updater needs repository contents/issue write permissions and the production environment. Keep `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` valid.

## Failures and freshness

A failed acquisition, changed grid/mask, missing day, bad checksum, or failed validation stops the run. The previous verified live release remains usable. A production deploy failure after the data commit is retried on the next run by comparing the live health endpoint against the candidate release.

One GitHub issue titled `Monthly rainfall update needs attention` is opened for a failed run or an upstream Final delay beyond day 27. It links the run and last available date, and closes after recovery. Watch repository issues/Actions for notifications. The website also flags stale data and always displays the observation date; the health endpoint permits independent monitoring.

To retry, run `update monthly rainfall` with its Run workflow button. Archived months are restored and validated rather than downloaded again. For a corrected upstream month or methodology change, create a new versioned monthly archive and rebuild explicitly. Never overwrite a known monthly asset silently.

GitHub can disable scheduled workflows after 60 days without repository activity in a public repository. Normal monthly data commits keep the repository active. An independent read-only freshness watchdog checks the repository on Sundays and notifies the project owner about a disabled/missing workflow, ten days without an updater run, unresolved failures, inconsistent health metadata, or overdue data. This watchdog is separate from GitHub cron; include its ownership in a staff handoff. A cron workflow cannot monitor its own disabled state.

Smoke checks use curl, an expected release identifier on manifest/health requests, and short retries for edge propagation. A passing response from an older valid release does not count as success. Manual Run workflow supports `force_deploy` for a validated application change without new monthly data.

## Caching

The service worker uses network-first application/manifest/health requests and caches immutable recent tile paths. Returning online visitors receive the active release; offline visitors retain the last cached report with its data-through date. Bump the service-worker cache version when publishing changed historical tile paths or an incompatible application release.

## Rollback

The active publication and two preceding recent tile releases are retained in the repository. Full checksummed publication snapshots remain durable in `chirps-monthly-v1`. To roll back, restore the earlier snapshot's manifest, health endpoint, and recent tiles in a reviewed commit, run checks/build, and run `deploy production`. Preserve the fixed historical rainfall and temperature tiles. Investigate and pause the monthly workflow before rollback so its next run does not immediately advance again.

## Monthly custodian check

- Confirm the workflow is enabled and the latest expected monthly release reached production.
- Open Fenoarivo Atsinanana, Antananarivo, and Toliara; inspect rainfall, recent comparison, and temperature.
- Review unresolved update issues and secret expiration.
- Confirm durable release assets remain available and a backup administrator can rerun and roll back.

## Ownership and handoff

Assign a primary and backup custodian in both GitHub and Cloudflare. Repository and hosting ownership should move to the program organization if currently personal. Enable repository issue/Actions notifications for the custodians and test access before a handoff. CDS access is needed only for a future temperature-source rebuild, not ordinary rainfall maintenance.

Incoming custodians should confirm deployment/rollback access, rotate scoped credentials where appropriate, run a staging update, and only then remove a departing administrator. Keep the project methodology and provenance alongside the release assets.
