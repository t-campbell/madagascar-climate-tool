# Operations outline

## Rainfall demo now live

The site currently serves the fixed 1991–2020 CHIRPS Final baseline and a GeoNames place index. There is no daily data job or CDS dependency in this demo. The live site's historical label does not advance each month. Temperature and current-season observations are future work.

Check the public site after any release: search for Fenoarivo Atsinanana or enter coordinates, then confirm rainfall, rainy days, and days with at least 20 mm render. The GitHub `checks` workflow validates static data; `deploy production` publishes the existing release manually. `publish rainfall demo` regenerates the static release manually from the CHIRPS workflow artifact and the latest GeoNames dump, commits it, and deploys it. The CHIRPS artifact from run 34862522613 expires October 14, 2026; preserve a durable copy or rerun the CHIRPS baseline pipeline before attempting a later regeneration.

When publishing updated data at the same file paths, increment `CACHE_NAME` in `site/sw.js` so returning visitors receive the new cached files.

GitHub and Cloudflare staff administrators should monitor deployment failures and token expiration. The rainfall demo uses the GitHub Actions token and existing Cloudflare deployment secrets; the CDS token is not needed to run the site or release rainfall. The static site has no runtime account, server, or paid database.

The sections below describe the planned current-season update pipeline and are not active in this rainfall demo.

## Normal update

1. The scheduled workflow checks for newly available source observations.
2. If no new observations exist, it exits without publishing.
3. If data exist, it produces a versioned candidate release.
4. Automated checks verify completeness, ranges, schemas, checksums, sample locations, and file sizes.
5. The candidate is deployed to staging.
6. Smoke tests request representative locations.
7. Only a passing release becomes active.

## Failure behavior

The active manifest is not changed when acquisition, processing, validation, or deployment fails. Users continue receiving the last verified release. The interface displays the observation date of that release.

An ERA5-Land submission that outlives a GitHub runner is not resubmitted. The historical baseline is submitted one year at a time, with one request each for daily minimum and maximum temperature. Staff copy the preserved CDS request IDs into the period-recovery workflow after both requests show `successful` in the CDS dashboard. Recovery downloads the existing results and builds an independently mergeable annual partial without repeating the data request.

## Rollback

A production rollback changes the active manifest to a previously verified release and redeploys the static site. At least three verified releases should be retained.

## Monthly staff check

- Confirm the latest scheduled workflow succeeded.
- Confirm the website's data-through date advanced when a source update was expected.
- Open one known location and confirm the report renders.
- Escalate only after one manual rerun also fails.

## Staff turnover

1. Add the incoming custodian to GitHub and Cloudflare.
2. Have the incoming custodian create or assume the appropriate CDS access.
3. Replace `CDS_API_TOKEN` and `CLOUDFLARE_API_TOKEN`.
4. Trigger a staging deployment.
5. Confirm rollback access.
6. Remove the departing custodian.
