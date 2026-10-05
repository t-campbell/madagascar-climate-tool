# Methodology contract

Status: rainfall and temperature baselines plus recent Final rainfall

Version: 0.5.0-monthly-rainfall

## Product boundary

This release describes historical rainfall and temperature patterns from 1991–2020. It is not a weather forecast, seasonal forecast, crop model, or guarantee of planting success. A separate panel reports recent complete rainfall months.

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

- Climate normal: 1991-01-01 through 2020-12-31.
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
- Monthly temperatures are displayed to the nearest whole degree Celsius.
- Rounding is presentation-only. Calculations, thresholds, comparisons, and chart geometry use the unrounded baseline values.

## Temperature definitions

- Monthly minimum temperature: mean of daily minimum temperature for the month, averaged across complete years.
- Monthly maximum temperature: mean of daily maximum temperature for the month, averaged across complete years.
- The chart's shaded band spans these two monthly means; it is not a variability or forecast interval.
- Temperature is shown on a fixed 0–40 °C axis so locations remain directly comparable.
- The entered coordinate is mapped independently to the nearest ERA5-Land land cell, at most 20 km away; no interpolation is presented.

## Rainfall onset and cessation

Onset and cessation rules vary by cropping system and region. Version 0.1 will not publish a universal national onset date. The prototype will display rainfall persistence and dry-spell probabilities. A later methodology version may add region- or crop-specific onset rules after agronomic review.

This restraint is intentional. One national onset rule would create precise-looking nonsense across Madagascar's sharply different climates.

## Recent rainfall observations

- The rolling panel contains twelve consecutive complete calendar months of CHIRPS v3 Final RNL, separate from the fixed 1991–2020 normal.
- A month is accepted only when every daily file and every baseline land cell is present on the aligned native 0.05 degree grid.
- Monthly totals sum daily values; rainy and heavy-rain days count days at the same ≥1 mm and ≥20 mm thresholds as the baseline.
- Daily CHIRPS values are disaggregated estimates; day counts are indicative rather than local rain-gauge observations.
- Each observed month is compared with its corresponding calendar-month normal at the exact same CHIRPS cell. Differences are shown in whole mm and whole percent, calculated before display rounding. Percent is omitted when the normal is below 1 mm.
- Final usually follows in the third week of the next month. Weekly checks allow through day 27 before treating the normal release lag as overdue.
- The panel and offline reports display the last included observation date. Offline data can be older than the live publication.
- The recent chart uses one national scale for the whole publication: at least 1,000 mm, enlarged in 250 mm steps if any actual monthly total exceeds it. The historical chart retains its fixed 1,000 mm scale.
- Failed acquisition or validation keeps the prior verified live publication. Temperature remains a historical normal, without a current-temperature feed.

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
