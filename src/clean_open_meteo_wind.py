"""Clean Open-Meteo CSV responses into the daily wind analysis table."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd


SEASONS = {12: "summer", 1: "summer", 2: "summer", 3: "autumn", 4: "autumn", 5: "autumn", 6: "winter", 7: "winter", 8: "winter", 9: "spring", 10: "spring", 11: "spring"}


def compass(degrees: Union[float, int, None]) -> Union[str, float]:
    if pd.isna(degrees):
        return np.nan
    labels = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return labels[int((float(degrees) + 11.25) // 22.5) % 16]


def read_api_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, skiprows=3)


def clean(raw_dir: Path, cleaned_path: Path, derived_path: Path) -> pd.DataFrame:
    daily = read_api_csv(raw_dir / "sydney_era5_daily.csv")
    hourly = read_api_csv(raw_dir / "sydney_era5_hourly.csv")
    daily.columns = ["DateParsed", "RainMm", "WindGustSpeed", "DailyMaxWindSpeed", "WindGustDirDegrees"]
    hourly.columns = ["timestamp", "HourlyRainMm", "WindSpeed", "WindDirDegrees", "HourlyGustSpeed"]
    daily["DateParsed"] = pd.to_datetime(daily["DateParsed"], errors="coerce")
    hourly["timestamp"] = pd.to_datetime(hourly["timestamp"], errors="coerce")
    for col in ["RainMm", "WindGustSpeed", "DailyMaxWindSpeed", "WindGustDirDegrees"]:
        daily[col] = pd.to_numeric(daily[col], errors="coerce")
    for col in ["HourlyRainMm", "WindSpeed", "WindDirDegrees", "HourlyGustSpeed"]:
        hourly[col] = pd.to_numeric(hourly[col], errors="coerce")
    daily = daily.loc[daily["DateParsed"].between("2016-01-01", "2022-12-31")].copy()
    hourly = hourly.loc[hourly["timestamp"].between("2016-01-01", "2022-12-31 23:00:00")].copy()
    daily = daily.drop_duplicates("DateParsed", keep=False)
    hourly = hourly.drop_duplicates("timestamp", keep=False)
    if (daily[["RainMm", "WindGustSpeed"]] < 0).any().any() or (hourly[["HourlyRainMm", "WindSpeed", "HourlyGustSpeed"]] < 0).any().any():
        raise ValueError("Negative precipitation or wind values found")

    result = daily[["DateParsed", "RainMm", "WindGustSpeed", "WindGustDirDegrees"]].copy()
    for hour, label in [(9, "9am"), (15, "3pm")]:
        point = hourly.loc[hourly["timestamp"].dt.hour.eq(hour), ["timestamp", "WindSpeed", "WindDirDegrees"]].copy()
        point["DateParsed"] = point["timestamp"].dt.normalize()
        point = point.drop_duplicates("DateParsed").set_index("DateParsed")
        result[f"WindSpeed{label}"] = result["DateParsed"].map(point["WindSpeed"])
        result[f"WindDir{label}Degrees"] = result["DateParsed"].map(point["WindDirDegrees"])
    next_rain = result["RainMm"].shift(-1)
    result["RainTomorrow"] = (next_rain > 0).astype("Int64")
    result.loc[next_rain.isna(), "RainTomorrow"] = pd.NA
    result = result.loc[result["DateParsed"].between("2016-01-01", "2022-12-30")].copy()
    result["WindGustDir"] = result["WindGustDirDegrees"].map(compass)
    result["WindSpeedChange"] = result["WindSpeed3pm"] - result["WindSpeed9am"]
    result["WindGustSpeedGroup"] = pd.qcut(result["WindGustSpeed"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    result["Season"] = result["DateParsed"].dt.month.map(SEASONS)
    result["Location"] = "Sydney (ERA5 grid point)"
    result["Latitude"] = -33.848858
    result["Longitude"] = 151.19551
    result["Date"] = result["DateParsed"].map(lambda x: f"{x.year}-{x.month}-{x.day}")
    columns = ["Date", "Location", "Latitude", "Longitude", "Season", "RainTomorrow", "RainMm", "WindGustSpeed", "WindGustSpeedGroup", "WindGustDir", "WindGustDirDegrees", "WindSpeed9am", "WindDir9amDegrees", "WindSpeed3pm", "WindDir3pmDegrees", "WindSpeedChange"]
    result = result[columns]
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    derived_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(cleaned_path, index=False)
    result.to_csv(derived_path, index=False)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw/open_meteo_sydney"))
    parser.add_argument("--cleaned", type=Path, default=Path("data/cleaned/wind_sydney_clean.csv"))
    parser.add_argument("--derived", type=Path, default=Path("data/derived/wind_sydney_analysis.csv"))
    args = parser.parse_args()
    data = clean(args.raw, args.cleaned, args.derived)
    print(f"rows={len(data)} dates={data.Date.iloc[0]}..{data.Date.iloc[-1]}")
    print(data.isna().sum().to_string())
