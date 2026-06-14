from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get(settings.health_path, response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
async def ready(db: AsyncSession = Depends(get_db)) -> ReadyResponse:
    await db.execute(text("SELECT 1"))
    return ReadyResponse(status="ok", database="connected")
