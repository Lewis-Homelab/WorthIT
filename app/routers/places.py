import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Place
from app.schemas import PlaceCreate, PlaceRead

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=list[PlaceRead])
async def list_places(
    place_type: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Place]:
    query = select(Place).order_by(Place.name)
    if place_type:
        query = query.where(Place.place_type == place_type)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def create_place(
    payload: PlaceCreate,
    db: AsyncSession = Depends(get_db),
) -> Place:
    data = payload.model_dump()
    metadata = data.pop("metadata", None)
    place = Place(**data, metadata_=metadata)
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return place


@router.get("/{place_id}", response_model=PlaceRead)
async def get_place(
    place_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Place:
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return place
