# Madagascar climate field guide

A low-bandwidth, offline-capable climate reference for agriculture volunteers and extension staff in Madagascar. Users search for a settlement, enter coordinates, or use their device location to retrieve rainfall and temperature patterns from precomputed geographic tiles.

## Current status

This first build is an architectural and interface prototype. It contains clearly marked demonstration fixtures for Fenoarivo Atsinanana, Antananarivo, and Toliara. The fixture values exercise the complete browser flow but are not approved operational climate products.

## Architecture

- Plain static HTML, CSS, and JavaScript.
- No runtime server, database, user account, or external browser API.
- Historical baseline and current-season observations are separate releases.
- Rainfall remains on the native CHIRPS 0.05 degree grid.
- Temperature remains on the native ERA5-Land 0.1 degree grid.
- Data are divided into 1 degree tiles with a one-cell halo.
- A local gazetteer converts settlement names to coordinates.
- A service worker caches the application and previously requested tiles.

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

## Account setup

The production workflows expect these GitHub repository secrets:

- `CLOUDFLARE_API_TOKEN`: scoped to Workers script deployments for the program account.
- `CLOUDFLARE_ACCOUNT_ID`: the program Cloudflare account identifier.
- `CDS_API_TOKEN`: token for the designated Copernicus Climate Data Store custodian.

No secret is used by or copied into browser code.

## Repository ownership

The production repository should be owned by a Peace Corps-controlled GitHub organization with at least two staff owners. The Cloudflare account should likewise have a primary and backup staff administrator.

See `docs/methodology.md`, `docs/data-pipeline.md`, and `docs/operations.md` before treating any output as operational.
