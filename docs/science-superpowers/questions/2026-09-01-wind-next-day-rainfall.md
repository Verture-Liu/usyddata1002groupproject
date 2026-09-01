# Sydney Wind Conditions and Next-Day Rainfall

**Research question:** In daily Sydney weather observations, are wind speed and wind direction measured today statistically associated with whether it rains tomorrow, and are these associations consistent across seasons?

**Background / motivation:** This is the wind-variable contribution to the DATA1002/DATA1902 Sydney next-day rainfall project. The analysis is descriptive and exploratory. It is intended to identify patterns that may support next-day outdoor planning, not to establish causation or produce a finished forecasting model.

**Hypotheses:**
- **H0 (null):** Wind-speed distributions and next-day rainfall rates do not differ meaningfully across `RainTomorrow` groups, wind-speed groups, or wind-direction groups.
- **H1 (alternative):** At least one selected wind measure or wind-direction category is statistically associated with `RainTomorrow`; the strength or direction of the association may vary by season.

**Population & unit of analysis:** One daily observation for the agreed Sydney location/station. Each row represents one date and is aligned with the group's shared `RainTomorrow` outcome.

**Key variables (operationalized):**
- **Date:** calendar date, standardised to the project format `YYYY-M-D` (for example, `2026-8-31`).
- **Location:** the agreed Sydney location/station definition used for merging.
- **Outcome:** `RainTomorrow`, encoded as `0` for no rain and `1` for rain.
- **Season:** lowercase English category: `summer`, `autumn`, `winter`, or `spring`; December-February is summer, March-May autumn, June-August winter, and September-November spring.
- **Predictors:** `WindGustSpeed`, `WindSpeed9am`, and `WindSpeed3pm`, using documented source units.
- **Optional predictor:** `WindGustDir`, treated as a categorical variable rather than an ordered numeric value.
- **Derived measure:** `WindSpeedChange = WindSpeed3pm - WindSpeed9am` when both source values are available.
- **Derived grouping:** wind-speed groups based on documented quantiles or defensible meteorological intervals.

**What counts as an answer:** The analysis will report effective sample sizes and descriptive summaries by `RainTomorrow`, then check the same patterns by `Season`. The two main figures will be (1) a `WindGustSpeed` boxplot by the binary outcome and (2) seasonal next-day rainfall rates across wind-speed groups. A wind-direction plot may replace or supplement the second plot only if direction labels and sample sizes support it. The answer will state at least one numerical finding, one seasonal consistency or inconsistency finding, and one limitation.

**Scope & exclusions:** The analysis focuses on wind variables and does not treat observed associations as causal or as evidence of a completed prediction model. Temperature, humidity, pressure, rainfall, cloud, and sunshine are outside this individual analysis. Wind direction is supplementary and will not be analysed as an ordinary numeric scale.

**Data and provenance requirements:** The independently collected wind dataset must document source, URL or citation, collection method, units, location/station, date coverage, restrictions, and relevance. It must contain enough overlapping dates to merge with the group's shared `RainTomorrow` data. The final contribution will retain the original data, cleaned data, reproducible Python code, summary outputs, and figures.

**Open questions for prior-work survey:** Check appropriate handling of daily wind measurements, missing wind observations, wind-direction categories, justified wind-speed grouping, and the limitations of using grouped rainfall rates for an exploratory association analysis.
