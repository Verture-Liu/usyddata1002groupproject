"""Analyse Sydney wind data using pandas and matplotlib."""

import pandas as pd
import matplotlib.pyplot as plt


plt.switch_backend("Agg")

SEED = 20260901
N_BOOT = 2000
MEASURES = ["WindGustSpeed", "WindSpeed9am", "WindSpeed3pm", "WindSpeedChange"]
SEASONS = ["summer", "autumn", "winter", "spring"]


def bootstrap_mean(values, seed):
    values = values.dropna().reset_index(drop=True)
    if len(values) < 10:
        return float("nan"), float("nan")

    estimates = [
        values.sample(len(values), replace=True, random_state=seed + index).mean()
        for index in range(N_BOOT)
    ]
    samples = pd.Series(estimates, dtype=float)
    return float(samples.quantile(0.025)), float(samples.quantile(0.975))


def bootstrap_median_difference(first, second, seed):
    first = first.dropna().reset_index(drop=True)
    second = second.dropna().reset_index(drop=True)
    if len(first) < 10 or len(second) < 10:
        return float("nan"), float("nan")

    estimates = [
        first.sample(
            len(first), replace=True, random_state=seed + 2 * index
        ).median()
        - second.sample(
            len(second), replace=True, random_state=seed + 2 * index + 1
        ).median()
        for index in range(N_BOOT)
    ]
    differences = pd.Series(estimates, dtype=float)
    return (
        float(differences.quantile(0.025)),
        float(differences.quantile(0.975)),
    )


def summary_table(data):
    rows = []
    for (season, outcome), group in data.groupby(
        ["Season", "RainTomorrow"], observed=True
    ):
        for measure in MEASURES:
            values = group[measure].dropna()
            rows.append({
                "Season": season,
                "RainTomorrow": int(outcome),
                "Measure": measure,
                "n": len(values),
                "mean": values.mean(),
                "median": values.median(),
                "sd": values.std(ddof=1),
                "q1": values.quantile(0.25),
                "q3": values.quantile(0.75),
            })
    return pd.DataFrame(rows)


def rainfall_rate_table(data):
    rows = []
    groups = data.groupby(["Season", "WindGustSpeedGroup"], observed=True)
    for group_number, ((season, speed_group), group) in enumerate(groups):
        values = group["RainTomorrow"].dropna().astype(float)
        low, high = bootstrap_mean(values, SEED + group_number * N_BOOT)
        rows.append({
            "Season": season,
            "WindGustSpeedGroup": str(speed_group),
            "n": len(values),
            "rainy_tomorrow": int(values.sum()),
            "rainfall_rate": values.mean(),
            "ci_low": low,
            "ci_high": high,
        })
    return pd.DataFrame(rows)


def analyse():
    data = pd.read_csv("data/derived/wind_sydney_analysis.csv")
    data["RainTomorrow"] = data["RainTomorrow"].astype(int)
    data["WindGustSpeedGroup"] = pd.Categorical(
        data["WindGustSpeedGroup"],
        categories=["Q1", "Q2", "Q3", "Q4"],
        ordered=True,
    )

    summary = summary_table(data)
    summary.to_csv(
        "outputs/tables/wind_descriptive_summary_by_season_outcome.csv",
        index=False,
    )
    rates = rainfall_rate_table(data)
    rates.to_csv(
        "outputs/tables/wind_gust_group_rainfall_rates_by_season.csv",
        index=False,
    )
    overall = summary_table(data.assign(Season="all"))
    overall.to_csv(
        "outputs/tables/wind_descriptive_summary_overall.csv", index=False
    )

    figure, axis = plt.subplots(figsize=(7.5, 5.2))
    boxes = [
        data[data["RainTomorrow"].eq(outcome)]["WindGustSpeed"].dropna()
        for outcome in [0, 1]
    ]
    axis.boxplot(
        boxes,
        patch_artist=True,
        boxprops={"facecolor": "#8ecae6"},
        medianprops={"color": "#023047", "linewidth": 2},
    )
    axis.set_xticks([1, 2], ["0 = no rain", "1 = rain"])
    axis.set_xlabel("RainTomorrow")
    axis.set_ylabel("WindGustSpeed (km/h)")
    axis.set_title("Sydney wind gust speed by next-day rainfall")
    axis.text(
        0.02, 0.02,
        "Each box shows the distribution of daily maximum gust speed.",
        transform=axis.transAxes,
        fontsize=9,
    )
    figure.tight_layout()
    figure.savefig(
        "outputs/figures/figure1_windgustspeed_by_raintomorrow.png", dpi=300
    )
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8.5, 5.5))
    positions = [0, 1, 2, 3]
    width = 0.2
    colours = ["#219ebc", "#8ecae6", "#ffb703", "#fb8500"]

    for number, season in enumerate(SEASONS):
        season_rates = rates[rates["Season"].eq(season)].set_index(
            "WindGustSpeedGroup"
        ).reindex(["Q1", "Q2", "Q3", "Q4"])
        rainfall_rates = season_rates["rainfall_rate"]
        lower_errors = (rainfall_rates - season_rates["ci_low"]).tolist()
        upper_errors = (season_rates["ci_high"] - rainfall_rates).tolist()
        season_positions = [
            position + (number - 1.5) * width for position in positions
        ]
        axis.bar(
            season_positions,
            rainfall_rates.tolist(),
            width,
            yerr=[lower_errors, upper_errors],
            capsize=3,
            label=season,
            color=colours[number],
        )

    axis.set_xticks(
        positions, ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
    )
    axis.set_ylim(0, 1)
    axis.set_ylabel("RainTomorrow rate")
    axis.set_xlabel("Daily maximum wind-gust speed quartile")
    axis.set_title("Next-day rainfall rate across wind-gust groups by season")
    axis.legend(title="Season", ncol=2)
    figure.tight_layout()
    figure.savefig(
        "outputs/figures/figure2_windgust_groups_by_season.png", dpi=300
    )
    plt.close(figure)

    print(f"Rows: {len(data)}")
    print(f"Overall rain rate: {data['RainTomorrow'].mean():.3f}")


if __name__ == "__main__":
    analyse()
