# Sydney Wind Conditions and Next-Day Rainfall Analysis Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `preregistering-analysis` before execution. Then use `executing-analysis` or `subagent-driven-analysis` to run this plan step-by-step. Steps use checkbox (`- [ ]`) syntax for tracking.

**Question:** In daily Sydney weather observations, are wind speed and wind direction measured today statistically associated with whether it rains tomorrow, and are these associations consistent across seasons?

**Design:** Exploratory observational analysis of daily records, comparing wind measures by binary next-day rainfall and stratifying by season.

**Data:** Independently collected BOM Sydney daily observations, one row per date, with wind observations, date, location/station metadata, and a rainfall-derived or group-aligned `RainTomorrow` outcome coded 0/1.

**Primary analysis:** Compare `WindGustSpeed` distributions by `RainTomorrow`; estimate next-day rainfall rates across pre-specified `WindGustSpeed` quartiles, overall and within `Season`; use `WindSpeed9am`, `WindSpeed3pm`, and `WindSpeedChange` as supporting measures.

**Decision rule:** Treat the result as evidence of an exploratory association when the pre-specified group summaries show a non-zero difference and the 95% interval for the key difference/rate contrast excludes zero; describe the evidence as weak or uncertain when intervals include zero or effective sample sizes are small. Seasonal consistency is judged by the direction of the contrast being the same in at least three seasons with usable sample sizes; otherwise report inconsistency or insufficient evidence.

## Global constraints

- Date output format: `YYYY-M-D`, such as `2026-8-31`.
- Season values: lowercase `summer`, `autumn`, `winter`, `spring`.
- `RainTomorrow`: `0` means no rain; `1` means rain.
- Raw data is immutable; each transformation writes a new artifact.
- Valid observed extremes are retained; impossible values are removed only with a documented rule.
- No causal language and no finished forecasting model.

## Data-flow and files

- `data/raw/`: downloaded BOM source files and source metadata.
- `data/cleaned/wind_sydney_clean.csv`: validated daily wind table.
- `data/derived/wind_sydney_analysis.csv`: cleaned table with season, binary outcome, speed change, and speed group.
- `outputs/tables/`: quality audit and grouped descriptive summaries.
- `outputs/figures/`: two main matplotlib figures.
- `src/download_bom_wind.py`: download source files and record URLs/metadata.
- `src/clean_wind_data.py`: parse, standardise, validate, and write cleaned data.
- `src/analyse_wind.py`: generate summaries, bootstrap intervals, and figures.

## Task 1: Acquire and document the independent source

- [ ] Download BOM Sydney daily observation files for the selected overlapping date range, preserving each original file unchanged.
- [ ] Save a source manifest with URL, retrieval date, station/location description, units, date coverage, and data restrictions.
- [ ] Validate that the source contains date, maximum gust speed, 9am speed, 3pm speed, wind directions, and a rainfall field or an explicit join key for the group's `RainTomorrow` table.

## Task 2: Clean and standardise

- [ ] Parse dates and write them as `YYYY-M-D` strings while retaining a parsed date internally for sorting and next-day alignment.
- [ ] Standardise season with `month.map({12:'summer',1:'summer',2:'summer',3:'autumn',4:'autumn',5:'autumn',6:'winter',7:'winter',8:'winter',9:'spring',10:'spring',11:'spring'})`.
- [ ] Convert wind-speed fields to numeric km/h, treating source missing markers as missing.
- [ ] Reject negative wind speeds and impossible non-category values only after recording counts; retain valid high values.
- [ ] Standardise direction labels by trimming whitespace and uppercasing, then store them as categorical values.
- [ ] Remove exact duplicate rows and resolve duplicate dates using a documented station/date rule; do not silently keep the first row.
- [ ] Create `WindSpeedChange = WindSpeed3pm - WindSpeed9am` only when both values are present.
- [ ] Create `WindGustSpeedGroup` from quartiles calculated once on the cleaned overall sample, labelled `Q1`, `Q2`, `Q3`, `Q4`; do not recompute cut points by season.
- [ ] Align or derive `RainTomorrow` as integer 0/1 and exclude rows where the outcome cannot be established from the primary analysis.

## Task 3: Validate cleaning

- [ ] Print input rows, output rows, exact duplicates removed, invalid speeds removed, missingness by field, unique dates, date range, stations, and outcome counts.
- [ ] Assert that all final outcomes are in `{0, 1}`, all wind speeds are non-negative, all seasons are in the four allowed lowercase labels, and dates are unique.
- [ ] Assert that each analysis row has a documented date and location/station and that source units are km/h.
- [ ] Run the pipeline on a small simulated fixture containing a duplicate date, a missing speed, a negative speed, a valid extreme gust, and each season; confirm the expected rows and flags.

## Task 4: Produce pre-specified summaries

- [ ] For `WindGustSpeed`, `WindSpeed9am`, `WindSpeed3pm`, and `WindSpeedChange`, report `n`, mean, median, standard deviation, Q1, and Q3 by `RainTomorrow`.
- [ ] Report the same selected measures by `Season` and `RainTomorrow`, suppressing or flagging groups with fewer than 10 non-missing observations.
- [ ] For each fixed overall wind-gust quartile, report `n`, number rainy tomorrow, rainfall rate, and a 95% bootstrap interval overall and by season.
- [ ] Report the overall `RainTomorrow` rate and the effective sample size used for each estimate.

## Task 5: Create and evaluate figures

- [ ] Figure 1: matplotlib boxplot of `WindGustSpeed` by `RainTomorrow`, with labels `0 = no rain` and `1 = rain`, units `km/h`, sample sizes, and a descriptive caption.
- [ ] Figure 2: matplotlib line or grouped bar chart of next-day rainfall rate by fixed `WindGustSpeedGroup`, with one clearly labelled series per season and uncertainty bars where available.
- [ ] For each figure, document purpose, chart choice, visual encoding, strengths, weaknesses, and how it addresses the research question.

## Task 6: Interpret and package

- [ ] Write one numerical finding tied to a table/figure, one seasonal consistency/inconsistency statement, and one limitation.
- [ ] Explicitly discuss the BOM station mismatch and daily rainfall time definition.
- [ ] Save raw source files, cleaned/derived data, scripts, summaries, figures, and provenance notes under the project directory.
- [ ] Rerun the full pipeline from raw data and verify the outputs before reporting any conclusion.
