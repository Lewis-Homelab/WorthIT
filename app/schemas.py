import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import DataSource, PlaceType


class PlaceBase(BaseModel):
    name: str
    place_type: PlaceType
    latitude: float
    longitude: float
    description: str | None = None
    cost_gbp: Decimal | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    source: DataSource
    external_id: str | None = None
    metadata: dict | None = None


class PlaceCreate(PlaceBase):
    pass


class PlaceRead(PlaceBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    metadata: dict | None = Field(default=None, validation_alias="metadata_")

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    database: str
