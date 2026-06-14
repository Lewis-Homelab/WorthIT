import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlaceType(str, enum.Enum):
    ATTRACTION = "attraction"
    RESTAURANT = "restaurant"
    HIKE = "hike"
    VIEWPOINT = "viewpoint"


class DataSource(str, enum.Enum):
    GOOGLE_PLACES = "google_places"
    OPENSTREETMAP = "openstreetmap"


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    place_type: Mapped[PlaceType] = mapped_column(
        Enum(PlaceType, name="place_type"), nullable=False, index=True
    )
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cost_gbp: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    rating: Mapped[float | None] = mapped_column()
    source: Mapped[DataSource] = mapped_column(
        Enum(DataSource, name="data_source"), nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
