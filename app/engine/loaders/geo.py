"""
Geo loader — OpenStreetMap POIs and Camden walking network.

Source: sandbox/geo_dev.ipynb
Data:
  - data/raw/geo_data/camden_pois.parquet
  - data/raw/geo_data/camden_walking_edges.parquet
  - data/raw/geo_data/camden_walking_nodes.parquet

The walking network is pre-built from OSM footpaths so routing does not
need to parse the multi-GB .osm.pbf file at request time.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.engine.paths import geo_data_dir


@lru_cache(maxsize=1)
def load_pois(path: str | None = None) -> pd.DataFrame:
    """
    Load Camden points of interest extracted from OpenStreetMap.

    Each row is a cafe, pub, museum, viewpoint, etc. with lat/lon and
    assorted OSM tag columns (amenity, tourism, leisure, …).
    """
    parquet = Path(path) if path else geo_data_dir() / "camden_pois.parquet"
    if not parquet.exists():
        raise FileNotFoundError(f"POI data not found: {parquet}")
    return pd.read_parquet(parquet)


@lru_cache(maxsize=1)
def load_walking_edges(path: str | None = None) -> pd.DataFrame:
    """
    Load street segments for the Camden walking network.

    Only u, v (node IDs) and length (metres) are needed for routing —
    other OSM tags are dropped to keep memory use down.
    """
    parquet = Path(path) if path else geo_data_dir() / "camden_walking_edges.parquet"
    if not parquet.exists():
        raise FileNotFoundError(f"Walking network edges not found: {parquet}")
    return pd.read_parquet(parquet, columns=["u", "v", "length"])


@lru_cache(maxsize=1)
def load_walking_nodes(path: str | None = None) -> pd.DataFrame:
    """
    Load junction nodes for the Camden walking network.

    Used to snap POI coordinates onto the nearest walkable node so
    NetworkX can compute realistic street walking distances.
    """
    parquet = Path(path) if path else geo_data_dir() / "camden_walking_nodes.parquet"
    if not parquet.exists():
        raise FileNotFoundError(f"Walking network nodes not found: {parquet}")
    return pd.read_parquet(parquet, columns=["id", "lat", "lon"])
