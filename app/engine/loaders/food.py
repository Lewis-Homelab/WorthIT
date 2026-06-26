"""
Food hygiene loader — Camden FHRS establishment ratings.

Source: sandbox/food_hygene.ipynb
Data:   data/raw/fhrs_data/camden_fhrs.parquet

FHRS ratings (0–5) are matched to OSM food POIs by proximity in
scoring.experience.enrich_with_fhrs to improve restaurant/pub/cafe scores.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.engine.paths import fhrs_data_dir


@lru_cache(maxsize=1)
def load_food_establishments(path: str | None = None) -> pd.DataFrame:
    """
    Load Camden Food Hygiene Rating Scheme establishments.

    Adds two derived columns:
      - rating_numeric: float 0–5 where the source value is numeric
      - rating_label:   raw string (e.g. "AwaitingInspection", "Exempt")

    Rows without coordinates are dropped — they cannot be matched to map POIs.
    """
    parquet = Path(path) if path else fhrs_data_dir() / "camden_fhrs.parquet"
    if not parquet.exists():
        raise FileNotFoundError(f"FHRS data not found: {parquet}")

    df = pd.read_parquet(parquet)

    # Coordinates arrive as strings in the XML source; coerce to float.
    for col in ("Latitude", "Longitude"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "RatingValue" in df.columns:
        # Some rows are "AwaitingInspection" etc. — numeric only where valid.
        numeric = pd.to_numeric(df["RatingValue"], errors="coerce")
        df["rating_numeric"] = numeric
        df["rating_label"] = df["RatingValue"].astype(str)
    else:
        df["rating_numeric"] = pd.NA
        df["rating_label"] = ""

    df = df.dropna(subset=["Latitude", "Longitude"]).copy()
    return df
