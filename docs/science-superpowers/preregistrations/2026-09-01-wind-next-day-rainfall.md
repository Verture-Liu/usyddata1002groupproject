# Pre-registration: Sydney wind and next-day rainfall

**Frozen at commit:** 2026-09-01, before downloading or inspecting wind outcome data
**Question doc:** `docs/science-superpowers/questions/2026-09-01-wind-next-day-rainfall.md`
**Analysis plan:** `docs/science-superpowers/plans/2026-09-01-wind-next-day-rainfall.md`

## Hypotheses

- **H0:** The selected wind-speed distributions and next-day rainfall rates do not differ across `RainTomorrow` groups or fixed wind-speed groups.
- **H1:** Higher or lower wind conditions, or particular wind-direction categories, are associated with `RainTomorrow`; the contrast may differ by season. Because prior work does not justify a single direction for all wind measures, the primary prediction is a non-zero association rather than a universal positive or negative sign.

## Primary analysis (exact)

- **Primary contrast:** Compare `WindGustSpeed` between `RainTomorrow = 0` and `RainTomorrow = 1` using group `n`, mean, median, standard deviation, Q1, Q3, median difference, and a 95% bootstrap interval for the median difference.
- **Grouped rainfall contrast:** Calculate `RainTomorrow` rate within four `WindGustSpeedGroup` quartiles. Quartile cut points are computed once from the cleaned overall sample and reused for every season. Report rates, counts, and 95% bootstrap intervals overall and within each season.
- **Supporting measures:** Repeat descriptive summaries for `WindSpeed9am`, `WindSpeed3pm`, and `WindSpeedChange = WindSpeed3pm - WindSpeed9am` when both component values exist.
- **Direction:** Use `WindGustDir` only as a categorical supporting analysis if standardised category counts are adequate; never encode direction as an ordered number.
- **Season:** `summer` = December-February, `autumn` = March-May, `winter` = June-August, `spring` = September-November.
- **Date:** Store displayed dates as `YYYY-M-D`, for example `2026-8-31`.
- **Outcome:** `RainTomorrow` is integer `0` for no rain and `1` for rain.
- **Inclusion:** Keep one valid observation per agreed Sydney date with a documented station/location and an established binary outcome. Do not impute missing predictors in primary summaries.
- **Exclusion:** Remove exact duplicates, negative wind speeds, invalid dates, unrecognised outcomes, and records whose required primary field is missing. Valid extreme speeds remain unless the source marks them invalid.
- **Uncertainty:** Use a fixed random seed and 2,000 bootstrap resamples for intervals when the relevant group has at least 10 observations; otherwise report the estimate and flag it as low effective sample size without an interval.

## Prediction and falsifiability

The prediction is falsified for the primary analysis if the median difference interval includes zero and all fixed wind-speed-group rainfall-rate contrasts are zero or have intervals including zero. A result with intervals including zero is reported as no clear evidence, not as proof of no association.

## Sample size and stopping

The sample is fixed by the independently collected overlapping date range available before analysis. No optional stopping, no extending the date range after seeing results, and no changing the station/date inclusion rule after inspecting associations. Because this is a fixed observational Stage 1 dataset and no defensible prior effect size is available, no formal power target is claimed; effective sample sizes and interval widths are reported as the precision assessment.

## Multiplicity

One primary contrast is registered: `WindGustSpeed` by `RainTomorrow`. The quartile rainfall-rate chart is a co-primary descriptive display required by the assignment. Supporting wind measures and direction analyses are secondary/exploratory and will not be promoted to confirmatory findings based on apparent strength.

## Secondary and exploratory analyses

- Seasonal versions of the primary contrast.
- `WindSpeed9am`, `WindSpeed3pm`, and `WindSpeedChange` summaries.
- `WindGustDir` category rainfall rates if category counts are adequate.
- Alternative wind-speed intervals, sensitivity checks, and any additional chart are exploratory and will be labelled as such.

## Planned deviations

Any deviation caused by source format, missing variables, station coverage, or insufficient sample size will be recorded in the provenance note and report. The affected result will be labelled exploratory.
