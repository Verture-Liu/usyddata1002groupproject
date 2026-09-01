# Prior-work note: Sydney wind and next-day rainfall

## Source and measurement grounding

The Bureau of Meteorology (BOM) Daily Weather Observations page provides daily maximum wind gust, 9am wind direction/speed, and 3pm wind direction/speed. The displayed unit for wind speed and gust is km/h. Wind direction is the direction the wind comes from and is therefore categorical, not an ordered numeric measurement.

The BOM Sydney daily page states that temperature, humidity and rainfall observations are from Sydney Observatory Hill (station 066214), while wind observations are from Fort Denison (station 066022). This is a known location/measurement limitation: the wind and rainfall components are both Sydney observations but are not necessarily from the same station.

## Adopted method

For this exploratory Stage 1 analysis, use one row per date, retain the source units, and compare selected wind-speed distributions between `RainTomorrow = 0` and `RainTomorrow = 1`. Report `n`, mean, median, standard deviation, quartiles, and missingness. Estimate next-day rainfall rates within wind-speed groups and repeat both summaries by lowercase `Season`. Use a boxplot for the continuous distribution and a seasonal rainfall-rate chart for grouped evidence. Report uncertainty with 95% bootstrap intervals for key differences/rates where sample size permits; avoid presenting the analysis as a causal model or finished forecast.

## Confounds and artifacts to handle

- Station mismatch: retain station metadata and acknowledge that wind comes from Fort Denison while BOM's Sydney rainfall field is associated with Observatory Hill.
- Time definition: BOM daily rainfall is measured over a 24-hour period ending at the local morning observation, so the operational `RainTomorrow` label must be defined consistently with the project's date convention.
- Missingness: do not impute wind speeds or wind directions for the primary summaries; report effective sample sizes.
- Direction categories: standardise labels, preserve them as categories, and combine only documented/rare categories if necessary.
- Measurement units: verify and retain km/h; do not mix knots and km/h.
- Extreme gusts: do not delete valid extremes solely because they are large; separately flag impossible values and report remaining limitations.

## Relationship to prior work

This is a local descriptive application of official station observations, not a claim of novel meteorological discovery. Its contribution is a reproducible Sydney-specific comparison aligned to the group's common next-day rainfall outcome and seasonal categories.

## Sources

- [BOM Sydney Daily Weather Observations](https://www.bom.gov.au/climate/dwo/IDCJDW2124.latest.shtml)
- [BOM Sydney area observation definitions](https://www.bom.gov.au/nsw/observations/sydney.shtml)
- [BOM Weather Station Directory](https://www.bom.gov.au/climate/data/stations/index.shtml)
