# Prior-work note: Sydney wind and next-day rainfall

## Source and measurement grounding

The Bureau of Meteorology (BOM) Daily Weather Observations page provides daily maximum wind gust, 9am wind direction/speed, and 3pm wind direction/speed. The displayed unit for wind speed and gust is km/h. Wind direction is the direction the wind comes from and is therefore categorical, not an ordered numeric measurement.

The BOM Sydney daily page states that temperature, humidity and rainfall observations are from Sydney Observatory Hill (station 066214), while wind observations are from Fort Denison (station 066022). This is a known location/measurement limitation: the wind and rainfall components are both Sydney observations but are not necessarily from the same station.

Because the required study window is 2016-01-01 to 2022-12-31 and BOM's public Daily Weather Observations pages expose only the recent period, the reproducible historical source will be Open-Meteo's Historical Weather API using the ERA5 model at a fixed Sydney coordinate. The API directly provides daily maximum gust, daily dominant direction, hourly wind speed/direction, and daily precipitation, with `Australia/Sydney` timezone and km/h/mm units. This is a reanalysis product rather than a station observation, so spatial/model representation is a limitation to report.

## Adopted method

For this exploratory Stage 1 analysis, use one row per local Sydney date, retain km/h, and compare selected wind-speed distributions between `RainTomorrow = 0` and `RainTomorrow = 1`. Derive `WindGustSpeed` from the API's daily maximum gust, `WindSpeed9am` and `WindSpeed3pm` from the corresponding local hours, and `WindSpeedChange` as their difference. Report `n`, mean, median, standard deviation, quartiles, and missingness. Estimate next-day rainfall rates within wind-speed groups and repeat both summaries by lowercase `Season`. Use a boxplot for the continuous distribution and a seasonal rainfall-rate chart for grouped evidence. Report uncertainty with 95% bootstrap intervals for key differences/rates where sample size permits; avoid presenting the analysis as a causal model or finished forecast.

## Confounds and artifacts to handle

- Spatial/model provenance: retain the API coordinate, ERA5 model, elevation, timezone, and query URL; acknowledge that the series is a reanalysis grid estimate rather than a direct station observation.
- Time definition: convert timestamps to Australia/Sydney local time before daily aggregation and 9am/3pm extraction; `RainTomorrow` is the next local calendar day's precipitation sum > 0.
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
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
