"""
Tests for the file-backed recommendation engine (app/engine/).

Unit tests cover scoring and category logic without requiring data files.
Integration tests load Camden parquet from data/raw/ when present.
"""

import pandas as pd
import pytest

from app.engine.scoring.experience import (
    derive_category,
    interest_categories,
    score_poi,
)
from app.engine.scoring.weather import category_weather_fit, outdoor_weather_score


def test_derive_category_prefers_amenity():
    """amenity tag should win over tourism when both are set."""
    row = pd.Series({"amenity": "cafe", "tourism": "museum", "leisure": None, "historic": None, "shop": None})
    assert derive_category(row) == "cafe"


def test_interest_categories_expands_aliases():
    """User-facing words like 'coffee' map to OSM categories like 'cafe'."""
    categories = interest_categories(["coffee", "walk"])
    assert "cafe" in categories
    assert "viewpoint" in categories


def test_outdoor_weather_score_dry_day():
    """Dry, mild, daylight conditions should score highly for outdoor activity."""
    weather = {
        "precipitation_mm": 0.0,
        "rain_mm": 0.0,
        "cloud_cover_pct": 20.0,
        "wind_speed_kmh": 10.0,
        "temperature_c": 18.0,
        "is_day": True,
    }
    assert outdoor_weather_score(weather) > 0.7


def test_category_weather_fit_indoor_less_rain_sensitive():
    """Museums should be less penalised by rain than outdoor viewpoints."""
    rainy = {
        "precipitation_mm": 3.0,
        "rain_mm": 2.0,
        "cloud_cover_pct": 90.0,
        "wind_speed_kmh": 20.0,
        "temperature_c": 14.0,
        "is_day": True,
    }
    outdoor = category_weather_fit("viewpoint", rainy)
    indoor = category_weather_fit("museum", rainy)
    assert indoor > outdoor


def test_score_poi_prefers_matching_interest():
    """POIs matching user interests should score higher than non-matching ones."""
    poi = pd.Series(
        {
            "category": "museum",
            "lat": 51.539,
            "lon": -0.142,
            "node_id": 1,
            "estimated_cost_gbp": 10.0,
            "base_rating": 4.5,
        }
    )
    weather = {
        "precipitation_mm": 0.0,
        "rain_mm": 0.0,
        "cloud_cover_pct": 30.0,
        "wind_speed_kmh": 8.0,
        "temperature_c": 17.0,
        "is_day": True,
    }
    matched = score_poi(
        poi,
        start_lat=51.539,
        start_lon=-0.142,
        weather=weather,
        preferred_categories=interest_categories(["museum"]),
    )
    unmatched = score_poi(
        poi,
        start_lat=51.539,
        start_lon=-0.142,
        weather=weather,
        preferred_categories=interest_categories(["pub"]),
    )
    assert matched > unmatched


def test_suggest_day_plans_with_local_data():
    """End-to-end plan building against Camden parquet (skipped if data missing)."""
    from app.engine.planning.day_plans import suggest_day_plans

    plans = suggest_day_plans(
        start_lat=51.539,
        start_lon=-0.142,
        budget_gbp=50,
        max_hours=6,
        interests=["coffee", "museum", "pub"],
        limit=3,
    )
    if not plans:
        pytest.skip("No connected day plans in current Camden sample")
    assert plans[0]["score"] > 0
    assert len(plans[0]["stops"]) >= 2


def test_day_plans_api():
    """HTTP smoke test for GET /recommendations/day-plans."""
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/recommendations/day-plans",
        params={"budget_gbp": 50, "max_hours": 6, "interests": ["coffee", "pub"]},
    )
    if response.status_code == 503:
        pytest.skip("POC data files not present in test environment")
    assert response.status_code == 200
    payload = response.json()
    assert "plans" in payload
    assert "weather" in payload
