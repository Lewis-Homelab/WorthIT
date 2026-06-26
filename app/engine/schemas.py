"""
Pydantic schemas for the recommendations API.

These models define the JSON shape for /recommendations/day-plans
requests and responses. They mirror the dicts built in planning.day_plans
but add validation (score 0–100, budget bounds, etc.).
"""

from datetime import datetime

from pydantic import BaseModel, Field


class DayPlanStop(BaseModel):
    """One venue in a suggested day plan."""

    name: str
    category: str  # OSM-derived type: cafe, museum, pub, …
    latitude: float
    longitude: float
    estimated_cost_gbp: float
    dwell_minutes: int  # time spent here, not including walking
    experience_score: float  # per-POI ExperienceRank component
    rating: float  # FHRS or default prior, 1–5
    hygiene_rating: float | None = None  # FHRS 0–5 when matched


class DayPlanCard(BaseModel):
    """A complete ranked day plan — one swipe card in the browse UI."""

    template_id: str
    title: str
    emoji: str
    score: float = Field(ge=0, le=100, description="Overall plan score 0–100")
    walk_minutes: float | None
    dwell_minutes: float | None
    total_minutes: float | None
    total_hours: float
    cost_gbp: float | None
    weather_summary: str
    stops: list[DayPlanStop]


class DayPlanRequest(BaseModel):
    """POST body for /recommendations/day-plans."""

    latitude: float | None = None  # defaults to Camden POC centre
    longitude: float | None = None
    budget_gbp: float = Field(default=50.0, gt=0, le=500)
    max_hours: float = Field(default=6.0, gt=0, le=16)
    interests: list[str] = Field(
        default_factory=lambda: ["coffee", "museum", "pub", "walk"]
    )
    when: datetime | None = None  # forecast hour; defaults to now
    limit: int = Field(default=5, ge=1, le=10)


class DayPlanResponse(BaseModel):
    """Response wrapper including forecast used for scoring."""

    area: str = "Camden (POC)"
    plans: list[DayPlanCard]
    weather: dict[str, float | str | bool]
