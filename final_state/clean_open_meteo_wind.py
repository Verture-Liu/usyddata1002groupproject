"""Clean the Sydney wind and rainfall data with pandas."""

import pandas as pd


SEASONS = {
    12: "summer", 1: "summer", 2: "summer",
    3: "autumn", 4: "autumn", 5: "autumn",
    6: "winter", 7: "winter", 8: "winter",
    9: "spring", 10: "spring", 11: "spring",
}


def compass(degrees):
    if pd.isna(degrees):
        return pd.NA

    labels = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    return labels[int((float(degrees) + 11.25) // 22.5) % 16]


def read_weather_csv(path):
    data = pd.read_csv(path)
    if "time" not in data.columns:
        data = pd.read_csv(path, skiprows=3)
    return data


def clean():
    daily = read_weather_csv(
        "data/raw/open_meteo_sydney/sydney_era5_daily.csv"
    )
    hourly = read_weather_csv(
        "data/raw/open_meteo_sydney/sydney_era5_hourly.csv"
    )

    daily.columns = [
        "DateParsed", "RainMm", "WindGustSpeed",
        "DailyMaxWindSpeed", "WindGustDirDegrees",
    ]
    hourly.columns = [
        "timestamp", "HourlyRainMm", "WindSpeed",
        "WindDirDegrees", "HourlyGustSpeed",
    ]

    daily["DateParsed"] = pd.to_datetime(daily["DateParsed"], errors="coerce")
    hourly["timestamp"] = pd.to_datetime(hourly["timestamp"], errors="coerce")

    daily_number_columns = [
        "RainMm", "WindGustSpeed", "DailyMaxWindSpeed", "WindGustDirDegrees"
    ]
    hourly_number_columns = [
        "HourlyRainMm", "WindSpeed", "WindDirDegrees", "HourlyGustSpeed"
    ]
    for column in daily_number_columns:
        daily[column] = pd.to_numeric(daily[column], errors="coerce")
    for column in hourly_number_columns:
        hourly[column] = pd.to_numeric(hourly[column], errors="coerce")

    daily = daily[daily["DateParsed"].between("2016-01-01", "2022-12-31")].copy()
    hourly = hourly[
        hourly["timestamp"].between("2016-01-01", "2022-12-31 23:00:00")
    ].copy()
    daily = daily.drop_duplicates("DateParsed", keep=False)
    hourly = hourly.drop_duplicates("timestamp", keep=False)

    if (daily[["RainMm", "WindGustSpeed"]] < 0).any().any():
        raise ValueError("Negative rainfall or wind values found")
    if (hourly[["HourlyRainMm", "WindSpeed", "HourlyGustSpeed"]] < 0).any().any():
        raise ValueError("Negative rainfall or wind values found")

    result = daily[
        ["DateParsed", "RainMm", "WindGustSpeed", "WindGustDirDegrees"]
    ].copy()

    for hour, label in [(9, "9am"), (15, "3pm")]:
        point = hourly[
            hourly["timestamp"].dt.hour.eq(hour)
        ][["timestamp", "WindSpeed", "WindDirDegrees"]].copy()
        point["DateParsed"] = point["timestamp"].dt.normalize()
        point = point.drop_duplicates("DateParsed").set_index("DateParsed")
        result[f"WindSpeed{label}"] = result["DateParsed"].map(point["WindSpeed"])
        result[f"WindDir{label}Degrees"] = result["DateParsed"].map(
            point["WindDirDegrees"]
        )

    next_day_rain = result["RainMm"].shift(-1)
    result["RainTomorrow"] = (next_day_rain > 0).astype("Int64")
    result.loc[next_day_rain.isna(), "RainTomorrow"] = pd.NA
    result = result[
        result["DateParsed"].between("2016-01-01", "2022-12-30")
    ].copy()

    result["WindGustDir"] = result["WindGustDirDegrees"].map(compass)
    result["WindSpeedChange"] = result["WindSpeed3pm"] - result["WindSpeed9am"]
    result["WindGustSpeedGroup"] = pd.qcut(
        result["WindGustSpeed"], 4, labels=["Q1", "Q2", "Q3", "Q4"]
    )
    result["Season"] = result["DateParsed"].dt.month.map(SEASONS)
    result["Location"] = "Sydney (ERA5 grid point)"
    result["Latitude"] = -33.848858
    result["Longitude"] = 151.19551
    result["Date"] = result["DateParsed"].map(
        lambda date: f"{date.year}-{date.month}-{date.day}"
    )

    columns = [
        "Date", "Location", "Latitude", "Longitude", "Season",
        "RainTomorrow", "RainMm", "WindGustSpeed", "WindGustSpeedGroup",
        "WindGustDir", "WindGustDirDegrees", "WindSpeed9am",
        "WindDir9amDegrees", "WindSpeed3pm", "WindDir3pmDegrees",
        "WindSpeedChange",
    ]
    result = result[columns]

    result.to_csv("data/cleaned/wind_sydney_clean.csv", index=False)
    result.to_csv("data/derived/wind_sydney_analysis.csv", index=False)

    print(f"Rows: {len(result)}")
    print(f"Dates: {result['Date'].iloc[0]} to {result['Date'].iloc[-1]}")
    return result


if __name__ == "__main__":
    clean()
