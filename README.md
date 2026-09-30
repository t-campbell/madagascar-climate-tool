# Madagascar climate field guide

A low-bandwidth climate reference for agriculture volunteers and extension staff in Madagascar. Search for a settlement, enter coordinates, or use device location to retrieve historical rainfall and temperature patterns from precomputed geographic tiles.

## Current status

The released baseline uses CHIRPS v3 Final rainfall and ERA5-Land temperature data for 1991–2020 across Madagascar. Rainfall metrics are available at the nearest 0.05° land cell (within 12 km); monthly mean daily minimum and maximum temperature are available at the nearest 0.1° land cell (within 20 km). Current-season observations remain deferred. This historical reference is not a forecast.

## Architecture

- Plain static HTML, CSS, and JavaScript.
- No runtime server, database, user account, or external browser API.
- Historical rainfall and temperature baselines are displayed in this release.
- Rainfall remains on the native CHIRPS 0.05 degree grid.
- Temperature remains on the native ERA5-Land 0.1 degree grid.
- Data are divided into 1 degree tiles with a 0.15 degree halo.
- GeoNames Madagascar settlements are split into small prefix search files and downloaded on demand; coordinates also work for unnamed sites.
- A service worker caches the application, previously requested tiles, and searched place lists.

## Local use

```bash
npm run build
npm run serve
```

Open `http://localhost:4173`.

## Checks

```bash
npm run check
```

## Rainfall data release

`.github/workflows/publish-rainfall-demo.yml` retrieves the successful national CHIRPS baseline artifact from run 34862522613, downloads the [GeoNames MG dump](https://download.geonames.org/export/dump/), generates static tiles and search shards, checks and builds the site, commits the release, and deploys it. The artifact expires October 14, 2026; for future regenerations retain a durable baseline or rerun the CHIRPS pipeline. No CDS token is required for this rainfall-only release. Place names © GeoNames, CC BY; attribution appears on the site.

## Account setup

The production workflows expect these GitHub repository secrets:

- `CLOUDFLARE_API_TOKEN`: scoped to Workers script deployments for the program account.
- `CLOUDFLARE_ACCOUNT_ID`: the program Cloudflare account identifier.
- `CDS_API_TOKEN`: token for the designated Copernicus Climate Data Store custodian.

No secret is used by or copied into browser code.

## Repository ownership

The production repository should be owned by a Peace Corps-controlled GitHub organization with at least two staff owners. The Cloudflare account should likewise have a primary and backup staff administrator.

See `docs/methodology.md`, `docs/data-pipeline.md`, and `docs/operations.md` before treating any output as operational.
