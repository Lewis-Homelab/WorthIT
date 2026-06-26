"""
Data loaders — read pre-processed parquet files from data/raw/.

Each loader is cached with @lru_cache so the walking graph and POI tables
are only read from disk once per API process. Pipelines will eventually
refresh these files on a schedule; the API just reads whatever is present.
"""

from app.engine.loaders.food import load_food_establishments
from app.engine.loaders.geo import load_pois, load_walking_edges, load_walking_nodes
from app.engine.loaders.weather import load_hourly_weather, weather_at

__all__ = [
    "load_food_establishments",
    "load_hourly_weather",
    "load_pois",
    "load_walking_edges",
    "load_walking_nodes",
    "weather_at",
]
