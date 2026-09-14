# Operations outline

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

