"""
Recommendations API — ranked day-plan cards for the WorthIT POC.

Exposes the file-backed engine to the frontend. Reads from data/raw/
parquet files; does not require PostgreSQL. Returns 503 if datasets
are missing (e.g. fresh clone before running pipelines).
"""

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.engine.loaders.weather import weather_at
from app.engine.planning.day_plans import suggest_day_plans
from app.engine.schemas import DayPlanCard, DayPlanRequest, DayPlanResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/day-plans", response_model=DayPlanResponse)
def get_day_plans(
    latitude: float | None = Query(default=None, description="Start latitude"),
    longitude: float | None = Query(default=None, description="Start longitude"),
    budget_gbp: float = Query(default=50.0, gt=0, le=500),
    max_hours: float = Query(default=6.0, gt=0, le=16),
    interests: list[str] = Query(
        default=["coffee", "museum", "pub", "walk"],
        description="User interests (repeat param for multiple)",
    ),
    limit: int = Query(default=5, ge=1, le=10),
) -> DayPlanResponse:
    """
    Return ranked day-plan cards (GET — convenient for browser/curl testing).

    Query params map directly to user constraints: budget, hours, interests.
    Start location defaults to Camden POC centre from config.
    """
    try:
        plans = suggest_day_plans(
            start_lat=latitude or settings.default_latitude,
            start_lon=longitude or settings.default_longitude,
            budget_gbp=budget_gbp,
            max_hours=max_hours,
            interests=interests,
            limit=limit,
        )
        weather = weather_at()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"POC data not available: {exc}",
        ) from exc

    return DayPlanResponse(
        plans=[DayPlanCard.model_validate(plan) for plan in plans],
        weather=weather,
    )


@router.post("/day-plans", response_model=DayPlanResponse)
def post_day_plans(payload: DayPlanRequest) -> DayPlanResponse:
    """
    Return ranked day-plan cards (POST — richer JSON body).

    Same as GET but supports an explicit `when` datetime for weather
    lookup and is easier to call from the Next.js frontend.
    """
    try:
        plans = suggest_day_plans(
            start_lat=payload.latitude or settings.default_latitude,
            start_lon=payload.longitude or settings.default_longitude,
            budget_gbp=payload.budget_gbp,
            max_hours=payload.max_hours,
            interests=payload.interests,
            when=payload.when,
            limit=payload.limit,
        )
        weather = weather_at(payload.when)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"POC data not available: {exc}",
        ) from exc

    return DayPlanResponse(
        plans=[DayPlanCard.model_validate(plan) for plan in plans],
        weather=weather,
    )
