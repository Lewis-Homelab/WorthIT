"""
Day-plan templates and itinerary assembly.

Builds ranked "swipe card" day plans from file-backed Camden data.
Each template defines a sequence of stop types (cafe → museum → pub);
the engine picks the best-scoring POI for each slot, validates total
walk time + dwell time against the user's budget and hours, and
returns the highest-scoring feasible combination.

Ported from sandbox/geo_dev.ipynb (itinerary helpers) and
docs/PROJECT_CONTEXT.md (browse-first card UI concept).
"""

from __future__ import annotations

from datetime import datetime
from itertools import product
from typing import Any

import pandas as pd

from app.engine.loaders.geo import load_pois
from app.engine.loaders.weather import weather_at
from app.engine.routing.network import walk_time_minutes
from app.engine.scoring.experience import (
    DEFAULT_DWELL_MINUTES,
    enrich_with_fhrs,
    interest_categories,
    prepare_poi_catalog,
    rank_pois,
    score_poi,
)

# ---------------------------------------------------------------------------
# Pre-defined day-plan shapes shown as swipe cards in the UI.
# Each "slot" is an interest keyword resolved via INTEREST_TO_CATEGORIES.
# ---------------------------------------------------------------------------
DAY_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "culture-afternoon",
        "title": "Culture afternoon",
        "emoji": "🏛️",
        "slots": ["cafe", "museum", "pub"],
    },
    {
        "id": "scenic-wander",
        "title": "Scenic wander",
        "emoji": "🌿",
        "slots": ["cafe", "viewpoint", "pub"],
    },
    {
        "id": "relaxed-local",
        "title": "Relaxed local day",
        "emoji": "☕",
        "slots": ["cafe", "library", "restaurant"],
    },
    {
        "id": "full-day-out",
        "title": "Full day out",
        "emoji": "🗺️",
        "slots": ["cafe", "museum", "restaurant", "pub"],
    },
]


def _slot_candidates(
    catalog: pd.DataFrame,
    slot: str,
    *,
    start_lat: float,
    start_lon: float,
    weather: dict[str, Any],
    interests: list[str],
    used_ids: set[Any],
    top_n: int = 5,
) -> list[pd.Series]:
    """
    Return up to top_n POI candidates for one template slot (e.g. "museum").

    Excludes POIs already used in earlier slots of the same plan so we
    don't recommend the same place twice in one day.
    """
    categories = interest_categories([slot])
    ranked = rank_pois(
        catalog,
        start_lat=start_lat,
        start_lon=start_lon,
        weather=weather,
        interests=interests,
        categories=list(categories),
        limit=top_n * 4,
    )
    picks: list[pd.Series] = []
    for _, row in ranked.iterrows():
        if row["id"] in used_ids:
            continue
        picks.append(row)
        if len(picks) >= top_n:
            break
    return picks


def _itinerary_metrics(stops: list[pd.Series]) -> dict[str, float | None]:
    """
    Compute walk time, dwell time, total time, and cost for an ordered stop list.

    Returns None values for any metric if the stops are not connected on
    the walking network (invalid itinerary).
    """
    walk_minutes = 0.0
    for i in range(len(stops) - 1):
        a = stops[i]
        b = stops[i + 1]
        if pd.isna(a.get("node_id")) or pd.isna(b.get("node_id")):
            return {"walk_minutes": None, "dwell_minutes": None, "total_minutes": None, "cost_gbp": None}
        leg = walk_time_minutes(int(a["node_id"]), int(b["node_id"]))
        if leg is None:
            return {"walk_minutes": None, "dwell_minutes": None, "total_minutes": None, "cost_gbp": None}
        walk_minutes += leg

    dwell_minutes = sum(
        float(stop.get("dwell_minutes", DEFAULT_DWELL_MINUTES)) for stop in stops
    )
    cost_gbp = sum(float(stop.get("estimated_cost_gbp", 8.0)) for stop in stops)
    total_minutes = walk_minutes + dwell_minutes
    return {
        "walk_minutes": round(walk_minutes, 1),
        "dwell_minutes": round(dwell_minutes, 1),
        "total_minutes": round(total_minutes, 1),
        "cost_gbp": round(cost_gbp, 2),
    }


def _plan_score(stops: list[pd.Series], metrics: dict[str, float | None]) -> float:
    """
    Overall day-plan score (0–100).

    Mostly the average experience score across stops, with a small bonus
    for plans that require less walking between venues.
    """
    if metrics["total_minutes"] is None:
        return 0.0
    stop_scores = [float(stop.get("experience_score", 0.0)) for stop in stops]
    avg_experience = sum(stop_scores) / len(stop_scores)
    # Reward compact itineraries — less walking means more time at venues.
    walk_bonus = max(0.0, 8.0 - (metrics["walk_minutes"] or 0) / 10)
    return round(min(100.0, avg_experience * 0.85 + walk_bonus), 1)


def build_day_plan(
    template: dict[str, Any],
    catalog: pd.DataFrame,
    *,
    start_lat: float,
    start_lon: float,
    weather: dict[str, Any],
    interests: list[str],
    budget_gbp: float,
    max_hours: float,
) -> dict[str, Any] | None:
    """
    Build the best feasible day plan for a single template.

    Tries all combinations of top candidates per slot (cartesian product),
    filters by budget and max duration, and returns the highest-scoring
    valid plan. Returns None if no feasible combination exists.
    """
    max_minutes = max_hours * 60
    best: dict[str, Any] | None = None

    # Gather candidate POIs for each slot in the template.
    slot_options: list[list[pd.Series]] = []
    used_ids: set[Any] = set()
    for slot in template["slots"]:
        candidates = _slot_candidates(
            catalog,
            slot,
            start_lat=start_lat,
            start_lon=start_lon,
            weather=weather,
            interests=interests,
            used_ids=used_ids,
        )
        if not candidates:
            return None
        slot_options.append(candidates)

    # Try every combination of candidates across slots.
    for combo in product(*slot_options):
        stops = list(combo)
        # Skip plans that visit the same OSM feature twice.
        if len({stop["id"] for stop in stops}) != len(stops):
            continue

        metrics = _itinerary_metrics(stops)
        if metrics["total_minutes"] is None:
            continue
        if metrics["total_minutes"] > max_minutes:
            continue
        if (metrics["cost_gbp"] or 0) > budget_gbp:
            continue

        score = _plan_score(stops, metrics)
        plan = {
            "template_id": template["id"],
            "title": template["title"],
            "emoji": template["emoji"],
            "score": score,
            "walk_minutes": metrics["walk_minutes"],
            "dwell_minutes": metrics["dwell_minutes"],
            "total_minutes": metrics["total_minutes"],
            "total_hours": round((metrics["total_minutes"] or 0) / 60, 1),
            "cost_gbp": metrics["cost_gbp"],
            "weather_summary": _weather_summary(weather),
            "stops": [_stop_payload(stop) for stop in stops],
        }
        if best is None or plan["score"] > best["score"]:
            best = plan

    return best


def _stop_payload(stop: pd.Series) -> dict[str, Any]:
    """Serialise one POI row into the API response shape for a plan stop."""
    return {
        "name": str(stop.get("name") or stop.get("category")),
        "category": str(stop.get("category")),
        "latitude": float(stop["lat"]),
        "longitude": float(stop["lon"]),
        "estimated_cost_gbp": float(stop.get("estimated_cost_gbp", 8.0)),
        "dwell_minutes": int(stop.get("dwell_minutes", DEFAULT_DWELL_MINUTES)),
        "experience_score": float(stop.get("experience_score", 0.0)),
        "rating": float(stop.get("base_rating", 3.8)),
        "hygiene_rating": (
            float(stop["hygiene_rating"]) if pd.notna(stop.get("hygiene_rating")) else None
        ),
    }


def _weather_summary(weather: dict[str, Any]) -> str:
    """One-line weather note shown on each day-plan card."""
    temp = weather["temperature_c"]
    precip = float(weather["precipitation_mm"]) + float(weather["rain_mm"])
    if precip >= 1:
        return f"Rain expected ({temp:.0f}°C) — indoor stops favoured"
    if bool(weather["is_day"]) and temp >= 16:
        return f"Good weather ({temp:.0f}°C) — outdoor stops score well"
    return f"Forecast {temp:.0f}°C"


def suggest_day_plans(
    *,
    start_lat: float,
    start_lon: float,
    budget_gbp: float = 50.0,
    max_hours: float = 6.0,
    interests: list[str] | None = None,
    when: datetime | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Main entry point — build ranked day-plan cards from file-backed Camden data.

    Called by the /recommendations/day-plans API. Loads POIs and weather,
    enriches food venues with FHRS, scores the catalog, then runs each
    DAY_TEMPLATE through build_day_plan and returns the top `limit` plans.
    """
    interests = interests or ["coffee", "museum", "pub", "walk"]
    weather = weather_at(when)

    pois = load_pois()
    catalog = prepare_poi_catalog(pois)

    # FHRS matching is O(n×m); only enrich the first 200 food rows for speed.
    food_top = catalog[
        catalog["category"].isin({"cafe", "pub", "bar", "restaurant", "fast_food"})
    ].head(200)
    if not food_top.empty:
        enriched_food = enrich_with_fhrs(food_top)
        catalog = pd.concat(
            [catalog[~catalog.index.isin(enriched_food.index)], enriched_food]
        ).sort_index()

    # Pre-score the full catalog once; slot picking reuses these scores.
    catalog["experience_score"] = catalog.apply(
        lambda row: score_poi(
            row,
            start_lat=start_lat,
            start_lon=start_lon,
            weather=weather,
            preferred_categories=interest_categories(interests),
        ),
        axis=1,
    )

    plans: list[dict[str, Any]] = []
    for template in DAY_TEMPLATES:
        plan = build_day_plan(
            template,
            catalog,
            start_lat=start_lat,
            start_lon=start_lon,
            weather=weather,
            interests=interests,
            budget_gbp=budget_gbp,
            max_hours=max_hours,
        )
        if plan:
            plans.append(plan)

    plans.sort(key=lambda p: p["score"], reverse=True)
    return plans[:limit]
