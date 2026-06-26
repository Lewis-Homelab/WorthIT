"""
POI normalisation, FHRS enrichment, and ExperienceRank scoring.

ExperienceRank (working title) scores each place 0–100 on:
  - rating      (up to 35 pts) — FHRS hygiene or default prior
  - cost        (up to 20 pts) — cheaper is better ("joy per pound")
  - weather fit (up to 15 pts) — outdoor vs indoor suitability
  - interests   (up to 15 pts) — matches user's stated preferences
  - proximity   (up to 15 pts) — closer to the day's start point

Ported from sandbox notebooks: geo_dev, food_hygene, combine_dev.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.engine.loaders.food import load_food_establishments
from app.engine.routing.network import haversine_m, snap_points_to_network
from app.engine.scoring.weather import category_weather_fit

# ---------------------------------------------------------------------------
# User interest → OSM category mapping
# Users say "coffee" or "walk"; the catalog uses amenity/tourism tags.
# ---------------------------------------------------------------------------
INTEREST_TO_CATEGORIES: dict[str, set[str]] = {
    "coffee": {"cafe"},
    "cafe": {"cafe"},
    "pub": {"pub", "bar"},
    "lunch": {"restaurant", "pub", "cafe", "fast_food"},
    "food": {"restaurant", "pub", "cafe", "fast_food"},
    "museum": {"museum", "gallery"},
    "history": {"museum", "attraction", "castle", "monument", "memorial"},
    "walk": {"viewpoint", "park", "garden", "nature_reserve"},
    "library": {"library"},
    "culture": {"museum", "gallery", "theatre", "attraction"},
}

# OSM has many tag values; only these are useful for day-plan recommendations.
RECOMMENDABLE_CATEGORIES = {
    "cafe",
    "pub",
    "bar",
    "restaurant",
    "fast_food",
    "museum",
    "gallery",
    "library",
    "viewpoint",
    "attraction",
    "park",
    "garden",
    "theatre",
    "monument",
    "memorial",
}

# POC cost estimates per stop (GBP) — real prices will come from APIs later.
ESTIMATED_COST_GBP: dict[str, float] = {
    "cafe": 4.0,
    "pub": 14.0,
    "bar": 12.0,
    "restaurant": 18.0,
    "fast_food": 10.0,
    "museum": 12.0,
    "gallery": 10.0,
    "library": 0.0,
    "viewpoint": 0.0,
    "attraction": 15.0,
    "park": 0.0,
    "garden": 6.0,
    "theatre": 25.0,
}

# Typical time spent at each stop (minutes), excluding walking between stops.
DWELL_MINUTES: dict[str, int] = {
    "cafe": 30,
    "pub": 60,
    "bar": 60,
    "restaurant": 75,
    "museum": 90,
    "gallery": 75,
    "library": 60,
    "viewpoint": 20,
    "park": 45,
    "garden": 40,
    "attraction": 90,
    "theatre": 120,
}
DEFAULT_DWELL_MINUTES = 30


def derive_category(row: pd.Series) -> str | None:
    """
    Pick the best OSM tag to describe a POI's primary category.

    Checks amenity → tourism → leisure → historic → shop in order,
    matching how OpenStreetMap tags are typically prioritised.
    """
    for col in ("amenity", "tourism", "leisure", "historic", "shop"):
        value = row.get(col)
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return None


def prepare_poi_catalog(pois: pd.DataFrame) -> pd.DataFrame:
    """
    Turn raw OSM POIs into a routable recommendation catalog.

    Steps:
      1. Derive a single category column from OSM tags
      2. Keep only recommendable categories (drop bins, benches, etc.)
      3. Snap each POI onto the walking network
      4. Attach estimated cost and dwell time per category
    """
    catalog = pois.copy()
    catalog["category"] = catalog.apply(derive_category, axis=1)
    catalog = catalog[catalog["category"].isin(RECOMMENDABLE_CATEGORIES)].copy()
    catalog = catalog.dropna(subset=["lat", "lon"])
    # Unnamed POIs still get a display label from their category.
    catalog["name"] = catalog["name"].fillna(catalog["category"].str.title())
    catalog = snap_points_to_network(catalog)
    catalog["estimated_cost_gbp"] = catalog["category"].map(ESTIMATED_COST_GBP).fillna(8.0)
    catalog["dwell_minutes"] = catalog["category"].map(DWELL_MINUTES).fillna(
        DEFAULT_DWELL_MINUTES
    )
    # Default rating prior before FHRS enrichment is applied.
    catalog["base_rating"] = 3.8
    return catalog


def enrich_with_fhrs(catalog: pd.DataFrame, max_match_m: float = 40) -> pd.DataFrame:
    """
    Attach FHRS hygiene ratings to food POIs when a nearby match exists.

    Matches by straight-line distance (≤ max_match_m). OSM names and FHRS
    business names rarely align exactly, so proximity is the best POC signal.
    """
    enriched = catalog.copy()
    enriched["hygiene_rating"] = np.nan
    enriched["hygiene_source"] = None

    try:
        fhrs = load_food_establishments()
    except FileNotFoundError:
        # FHRS is optional — scoring falls back to the default rating prior.
        return enriched

    food_mask = enriched["category"].isin({"cafe", "pub", "bar", "restaurant", "fast_food"})
    food_rows = enriched[food_mask]
    if food_rows.empty or fhrs.empty:
        return enriched

    # Only establishments with a numeric FHRS score are useful for ranking.
    rated = fhrs.dropna(subset=["rating_numeric"]).copy()
    if rated.empty:
        return enriched

    fhrs_lats = rated["Latitude"].to_numpy()
    fhrs_lons = rated["Longitude"].to_numpy()

    for idx, poi in food_rows.iterrows():
        dists = _haversine_vector(
            float(poi["lat"]),
            float(poi["lon"]),
            fhrs_lats,
            fhrs_lons,
        )
        nearest = int(np.argmin(dists))
        if dists[nearest] <= max_match_m:
            match = rated.iloc[nearest]
            enriched.at[idx, "hygiene_rating"] = float(match["rating_numeric"])
            enriched.at[idx, "hygiene_source"] = match.get("BusinessName")

    enriched["base_rating"] = enriched.apply(_rating_from_sources, axis=1)
    return enriched


def _haversine_vector(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Haversine distances (metres) from one point to many FHRS establishments."""
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    lats_r = np.radians(lats)
    lons_r = np.radians(lons)
    dlat = lats_r - lat_r
    dlon = lons_r - lon_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat_r) * np.cos(lats_r) * np.sin(dlon / 2) ** 2
    return 2 * 6_371_000 * np.arcsin(np.sqrt(a))


def _rating_from_sources(row: pd.Series) -> float:
    """Prefer FHRS hygiene rating when available; otherwise use the default prior."""
    if pd.notna(row.get("hygiene_rating")):
        # FHRS is 0–5; clamp to a sensible 1–5 display range.
        return max(1.0, min(5.0, float(row["hygiene_rating"])))
    return float(row.get("base_rating", 3.8))


def interest_categories(interests: list[str]) -> set[str]:
    """
    Expand user-facing interest strings into OSM category sets.

    Example: ["coffee", "walk"] → {"cafe", "viewpoint", "park", "garden", …}
    If no interests are given, all recommendable categories are allowed.
    """
    categories: set[str] = set()
    for interest in interests:
        key = interest.strip().lower()
        # Unknown interests are treated as literal category names.
        categories |= INTEREST_TO_CATEGORIES.get(key, {key})
    return categories or set(RECOMMENDABLE_CATEGORIES)


def score_poi(
    poi: pd.Series,
    *,
    start_lat: float,
    start_lon: float,
    weather: dict[str, Any],
    preferred_categories: set[str],
) -> float:
    """
    Compute ExperienceRank score (0–100) for a single POI.

    Component breakdown (max points):
      rating_score    35 — higher FHRS / base rating
      cost_score      20 — lower estimated spend
      weather_score   15 — category vs current forecast
      interest_score  15 — matches user's interests
      proximity_score 15 — nearer to the day start point
    """
    rating = float(poi.get("base_rating", 3.8))
    cost = float(poi.get("estimated_cost_gbp", 8.0))
    category = str(poi.get("category", ""))

    rating_score = (rating / 5.0) * 35
    cost_score = max(0.0, 20.0 - cost * 0.8)
    weather_score = category_weather_fit(category, weather) * 15
    interest_score = 15.0 if category in preferred_categories else 4.0

    if pd.notna(poi.get("node_id")):
        # Straight-line proximity is enough for scoring; graph routing is
        # reserved for itinerary leg times between consecutive stops.
        walk_m = haversine_m(start_lat, start_lon, float(poi["lat"]), float(poi["lon"]))
        proximity_score = max(0.0, 15.0 - (walk_m / 1000) * 4)
    else:
        proximity_score = 5.0

    total = rating_score + cost_score + weather_score + interest_score + proximity_score
    return round(min(100.0, total), 1)


def rank_pois(
    catalog: pd.DataFrame,
    *,
    start_lat: float,
    start_lon: float,
    weather: dict[str, Any],
    interests: list[str],
    categories: list[str] | None = None,
    limit: int = 50,
) -> pd.DataFrame:
    """
    Return the top-N POIs by experience score.

    When `categories` is set (e.g. ["viewpoint"] for a template slot),
    only POIs in those categories are considered — this ensures each
    itinerary stop has the correct type (cafe, museum, pub, etc.).

    Interest matching still affects the score via preferred_categories
    even when filtering by slot category.
    """
    if categories:
        preferred = set(categories)
    else:
        preferred = interest_categories(interests)

    filtered = catalog[catalog["category"].isin(preferred)].copy()
    if filtered.empty:
        # Last resort: don't return an empty list if data is sparse.
        filtered = catalog.copy()

    filtered["experience_score"] = filtered.apply(
        lambda row: score_poi(
            row,
            start_lat=start_lat,
            start_lon=start_lon,
            weather=weather,
            preferred_categories=interest_categories(interests),
        ),
        axis=1,
    )
    return filtered.sort_values("experience_score", ascending=False).head(limit)
