from app.models import DataSource, PlaceType
from app.schemas import PlaceCreate


def test_place_create_schema():
    place = PlaceCreate(
        name="Snowdon Summit",
        place_type=PlaceType.HIKE,
        latitude=53.0685,
        longitude=-4.0763,
        cost_gbp=0,
        rating=4.8,
        source=DataSource.OPENSTREETMAP,
        external_id="node/123",
    )
    assert place.name == "Snowdon Summit"
    assert place.place_type == PlaceType.HIKE
