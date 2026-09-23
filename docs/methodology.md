# Methodology contract

Status: rainfall demo released; temperature and current season planned

Version: 0.3.0-rainfall-demo

## Product boundary

This release describes historical rainfall patterns from 1991–2020. It is not a weather forecast, seasonal forecast, crop model, or guarantee of planting success. Temperature and recent observations are planned.

## Sources

- Rainfall: CHIRPS v3.
- Temperature: ERA5-Land two-metre air temperature.
- Settlement lookup: GeoNames MG country dump, CC BY, distributed as on-demand prefix files; [GeoNames attribution](https://www.geonames.org/).

## Spatial handling

- Rainfall is retained at its native 0.05 degree grid.
- Temperature is retained at its native 0.1 degree grid.
- The entered coordinate is mapped to the nearest CHIRPS land cell, at most 12 km away.
- Geographic transport tiles are 1 degree by 1 degree and include a 0.15 degree halo. Tile boundaries must not change reported results.
- The interface reports source resolution and distance to the selected cell center. It does not describe interpolated temperature as higher-resolution data.

## Reference period

- Proposed climate normal: 1991-01-01 through 2020-12-31.
- Baseline releases are immutable and versioned.
- Changing the normal period requires a new methodology version and baseline release.

## Rainfall definitions

- Rainy day: daily rainfall greater than or equal to 1.0 mm.
- Monthly rainfall: sum of daily rainfall within the calendar month.
- Rainy-day frequency: mean count of rainy days per month across complete years.
- Heavy-rain day: daily rainfall greater than or equal to 20 mm (the ETCCDI R20mm threshold).
- Heavy-rain-day frequency: mean count of heavy-rain days per month across complete years.
- Wet-day intensity: mean daily rainfall among rainy days (the ETCCDI simple daily intensity index, SDII).
- Monthly variability shown: 10th and 90th percentiles of monthly totals across complete years.
- Dry spell: consecutive days with rainfall below 1.0 mm.
- Dry-spell risk: proportion of complete years in which a dry spell of the stated length begins or continues within the reporting period.

## Display rounding

- Rainfall totals, percentile ranges, and wet-day intensity are displayed to the nearest whole millimetre.
- Mean rainy-day and heavy-rain-day frequencies are displayed to the nearest whole day.
- Rounding is presentation-only. Calculations, thresholds, comparisons, and chart geometry use the unrounded baseline values.

## Temperature definitions

- Monthly minimum temperature: mean of daily minimum temperature for the month, averaged across complete years.
- Monthly maximum temperature: mean of daily maximum temperature for the month, averaged across complete years.
- Temperature variability: 10th and 90th percentiles of the applicable daily or monthly statistic, explicitly labeled in the report.

## Rainfall onset and cessation

Onset and cessation rules vary by cropping system and region. Version 0.1 will not publish a universal national onset date. The prototype will display rainfall persistence and dry-spell probabilities. A later methodology version may add region- or crop-specific onset rules after agronomic review.

This restraint is intentional. One national onset rule would create precise-looking nonsense across Madagascar's sharply different climates.

## Current-season observations

- CHIRPS Preliminary and Final values are stored separately from the historical baseline.
- Preliminary values are visibly labeled provisional.
- Final values replace the corresponding preliminary period after validation.
- Current-season panels display the latest included observation date.
- An anomaly is calculated against the matching baseline period, not against a whole-year average.
- Failed updates do not replace the active release.

## Agricultural interpretation

Interpretations must be traceable to explicit thresholds in this document or a crop-specific extension reference. Version 0.1 may describe relative rainfall reliability, heat exposure, and dry-spell risk. It must not issue deterministic planting dates or imply a forecast.

## Required validation locations

The first operational candidate must be checked at:

1. Fenoarivo Atsinanana or the user's nearby field site.
2. Antananarivo or another central highland location.
3. Toliara or another dry southwestern location.

## Acceptance questions

- Are the selected metrics the same ones volunteers need for planting discussions?
- Is the 1.0 mm rainy-day threshold suitable for every displayed use?
- Should agricultural interpretations remain national and general, or be region-specific?
- Should CHIRPS Preliminary appear by default or only behind a provisional-data control?
- Which languages are required at launch?
