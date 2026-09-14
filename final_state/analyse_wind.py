"""Run the preregistered descriptive wind analysis and make two figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


SEED = 20260901
N_BOOT = 2000
MEASURES = ["WindGustSpeed", "WindSpeed9am", "WindSpeed3pm", "WindSpeedChange"]
SEASONS = ["summer", "autumn", "winter", "spring"]


def bootstrap_mean(values: pd.Series, seed: int) -> tuple[float, float]:
    values = values.dropna().reset_index(drop=True)
    if len(values) < 10:
        return (float("nan"), float("nan"))
    estimates = [
        values.sample(len(values), replace=True, random_state=seed + index).mean()
        for index in range(N_BOOT)
    ]
    samples = pd.Series(estimates, dtype=float)
    return (float(samples.quantile(0.025)), float(samples.quantile(0.975)))


def bootstrap_median_difference(
    a: pd.Series, b: pd.Series, seed: int
) -> tuple[float, float]:
    a = a.dropna().reset_index(drop=True)
    b = b.dropna().reset_index(drop=True)
    if len(a) < 10 or len(b) < 10:
        return (float("nan"), float("nan"))
    estimates = [
        a.sample(len(a), replace=True, random_state=seed + 2 * index).median()
        - b.sample(
            len(b), replace=True, random_state=seed + 2 * index + 1
        ).median()
        for index in range(N_BOOT)
    ]
    differences = pd.Series(estimates, dtype=float)
    return (
        float(differences.quantile(0.025)),
        float(differences.quantile(0.975)),
    )


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby(["Season", "RainTomorrow"], observed=True):
        season, outcome = keys
        for measure in MEASURES:
            values = group[measure].dropna()
            rows.append({"Season": season, "RainTomorrow": int(outcome), "Measure": measure, "n": len(values), "mean": values.mean(), "median": values.median(), "sd": values.std(ddof=1), "q1": values.quantile(0.25), "q3": values.quantile(0.75)})
    return pd.DataFrame(rows)


def rainfall_rate_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(["Season", "WindGustSpeedGroup"], observed=True)
    for group_index, (keys, group) in enumerate(grouped):
        season, speed_group = keys
        values = group["RainTomorrow"].dropna().astype(float)
        low, high = bootstrap_mean(values, SEED + group_index * N_BOOT)
        rows.append({"Season": season, "WindGustSpeedGroup": str(speed_group), "n": len(values), "rainy_tomorrow": int(values.sum()), "rainfall_rate": values.mean(), "ci_low": low, "ci_high": high})
    return pd.DataFrame(rows)


def main(input_path: Path, table_dir: Path, figure_dir: Path) -> None:
    df = pd.read_csv(input_path)
    df["RainTomorrow"] = df["RainTomorrow"].astype(int)
    df["WindGustSpeedGroup"] = pd.Categorical(df["WindGustSpeedGroup"], categories=["Q1", "Q2", "Q3", "Q4"], ordered=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    summary = summary_table(df)
    summary.to_csv(table_dir / "wind_descriptive_summary_by_season_outcome.csv", index=False)
    rates = rainfall_rate_table(df)
    rates.to_csv(table_dir / "wind_gust_group_rainfall_rates_by_season.csv", index=False)
    overall = summary_table(df.assign(Season="all"))
    overall.to_csv(table_dir / "wind_descriptive_summary_overall.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    boxes = [df.loc[df["RainTomorrow"].eq(outcome), "WindGustSpeed"].dropna() for outcome in [0, 1]]
    ax.boxplot(boxes, patch_artist=True, boxprops={"facecolor": "#8ecae6"}, medianprops={"color": "#023047", "linewidth": 2})
    ax.set_xticks([1, 2], ["0 = no rain", "1 = rain"])
    ax.set_xlabel("RainTomorrow")
    ax.set_ylabel("WindGustSpeed (km/h)")
    ax.set_title("Sydney wind gust speed by next-day rainfall")
    ax.text(0.02, 0.02, "Each box shows the distribution of daily maximum gust speed.", transform=ax.transAxes, fontsize=9)
    fig.tight_layout()
    fig.savefig(figure_dir / "figure1_windgustspeed_by_raintomorrow.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    x = [0, 1, 2, 3]
    width = 0.2
    colors = ["#219ebc", "#8ecae6", "#ffb703", "#fb8500"]
    for i, season in enumerate(SEASONS):
        subset = rates.loc[rates["Season"].eq(season)].set_index("WindGustSpeedGroup").reindex(["Q1", "Q2", "Q3", "Q4"])
        y = subset["rainfall_rate"]
        lower = (y - subset["ci_low"]).tolist()
        upper = (subset["ci_high"] - y).tolist()
        positions = [value + (i - 1.5) * width for value in x]
        ax.bar(positions, y.tolist(), width, yerr=[lower, upper], capsize=3, label=season, color=colors[i])
    ax.set_xticks(x, ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("RainTomorrow rate")
    ax.set_xlabel("Daily maximum wind-gust speed quartile (fixed overall cut points)")
    ax.set_title("Next-day rainfall rate across wind-gust groups by season")
    ax.legend(title="Season", ncol=2)
    fig.tight_layout()
    fig.savefig(figure_dir / "figure2_windgust_groups_by_season.png", dpi=300)
    plt.close(fig)

    (figure_dir / "chart_evaluations.md").write_text("""# Chart evaluations\n\n## Figure 1\nThe boxplot compares the continuous daily maximum gust-speed distribution for `RainTomorrow=0` and `RainTomorrow=1`. Position encodes wind speed and the median line makes the central contrast easy to compare. It preserves distribution shape better than a mean-only chart, but it does not show time order or prove causation.\n\n## Figure 2\nThe grouped bar chart compares the proportion of rainy next days across fixed overall wind-gust quartiles and seasons. Colour separates seasons and error bars show 95% bootstrap intervals. The fixed quartile boundaries make seasonal comparisons consistent, but categorisation loses continuous detail and small subgroup sizes can make intervals wide.\n""", encoding="utf-8")

    print(f"rows={len(df)} overall_rain_rate={df['RainTomorrow'].mean():.3f}")
    print(summary.loc[summary["Measure"].eq("WindGustSpeed")].to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/derived/wind_sydney_analysis.csv"))
    parser.add_argument("--tables", type=Path, default=Path("outputs/tables"))
    parser.add_argument("--figures", type=Path, default=Path("outputs/figures"))
    args = parser.parse_args()
    main(args.input, args.tables, args.figures)
