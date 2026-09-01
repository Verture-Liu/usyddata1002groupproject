"""Download Open-Meteo ERA5 historical wind and precipitation data for Sydney."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
PARAMS = {
    "latitude": -33.8688,
    "longitude": 151.2093,
    "start_date": "2016-01-01",
    "end_date": "2022-12-31",
    "timezone": "Australia/Sydney",
    "wind_speed_unit": "kmh",
    "precipitation_unit": "mm",
    "format": "csv",
}


def fetch(params: dict[str, object]) -> bytes:
    response = requests.get(BASE_URL, params=params, timeout=180)
    response.raise_for_status()
    return response.content


def download(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    daily_params = {**PARAMS, "daily": "precipitation_sum,wind_gusts_10m_max,wind_speed_10m_max,wind_direction_10m_dominant"}
    hourly_params = {**PARAMS, "hourly": "precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m"}
    manifest = {"source": "Open-Meteo Historical Weather API", "model": "ERA5", "files": []}
    for name, params in [("sydney_era5_daily.csv", daily_params), ("sydney_era5_hourly.csv", hourly_params)]:
        content = fetch(params)
        target = output_dir / name
        target.write_bytes(content)
        manifest["files"].append(
            {
                "file": name,
                "url": f"{BASE_URL}?{urlencode(params)}",
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw/open_meteo_sydney"))
    download(parser.parse_args().output)
