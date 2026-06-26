"""
Weather loader — reads cached Open-Meteo forecast parquet.

Source: sandbox/weather_dev.ipynb
Data:   data/raw/weather_data/openmeteo_camden_hourly.parquet

Used to boost outdoor POIs on dry days and favour indoor stops when rain
is forecast. Live API refresh will move to pipelines/ later.
"""

from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.engine.paths import weather_data_dir


@lru_cache(maxsize=1)
def load_hourly_weather(path: str | None = None) -> pd.DataFrame:
    """
    Load the full hourly forecast table for Camden.

    Cached for the lifetime of the process — parquet is small (~10 KB).
    Raises FileNotFoundError if the pipeline has not yet written the file.
    """
    parquet = Path(path) if path else weather_data_dir() / "openmeteo_camden_hourly.parquet"
    if not parquet.exists():
        raise FileNotFoundError(f"Weather data not found: {parquet}")

    df = pd.read_parquet(parquet)
    # Normalise to timezone-aware UTC for safe comparison with request times.
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


def weather_at(
    when: datetime | None = None,
    *,
    path: str | None = None,
) -> dict[str, float | str | bool]:
    """
    Return weather metrics for the forecast hour nearest to `when`.

    If `when` is omitted, uses the current UTC time. The returned dict is
    consumed by scoring.weather and planning.day_plans for suitability
    checks and human-readable summaries on each day-plan card.
    """
    df = load_hourly_weather(path)
    target = when or datetime.now(tz=UTC)
    if target.tzinfo is None:
        target = target.replace(tzinfo=UTC)

    # Pick the closest hourly row — adequate for POC; sub-hour precision
    # is not needed for "should I do an outdoor walk today?" decisions.
    idx = (df["date"] - target).abs().idxmin()
    row = df.loc[idx]

    return {
        "forecast_time": row["date"].isoformat(),
        "temperature_c": float(row["temperature_2m"]),
        "apparent_temperature_c": float(row["apparent_temperature"]),
        "precipitation_mm": float(row["precipitation"]),
        "rain_mm": float(row["rain"]),
        "cloud_cover_pct": float(row["cloud_cover"]),
        "wind_speed_kmh": float(row["wind_speed_10m"]),
        "is_day": bool(row["is_day"]),
    }
