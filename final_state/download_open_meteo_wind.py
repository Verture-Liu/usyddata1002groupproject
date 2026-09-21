"""Download Sydney wind and rainfall data with pandas."""

import pandas as pd


DAILY_URL = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude=-33.8688&longitude=151.2093&start_date=2016-01-01&"
    "end_date=2022-12-31&timezone=Australia%2FSydney&wind_speed_unit=kmh&"
    "precipitation_unit=mm&format=csv&daily=precipitation_sum%2C"
    "wind_gusts_10m_max%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant"
)

HOURLY_URL = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude=-33.8688&longitude=151.2093&start_date=2016-01-01&"
    "end_date=2022-12-31&timezone=Australia%2FSydney&wind_speed_unit=kmh&"
    "precipitation_unit=mm&format=csv&hourly=precipitation%2Cwind_speed_10m%2C"
    "wind_direction_10m%2Cwind_gusts_10m"
)


def download():
    daily = pd.read_csv(DAILY_URL, skiprows=3)
    hourly = pd.read_csv(HOURLY_URL, skiprows=3)

    daily.to_csv(
        "data/raw/open_meteo_sydney/sydney_era5_daily.csv", index=False
    )
    hourly.to_csv(
        "data/raw/open_meteo_sydney/sydney_era5_hourly.csv", index=False
    )

    print("Daily and hourly weather data downloaded.")


if __name__ == "__main__":
    download()
