"""
Walking-network routing — graph build, POI snapping, and travel times.

Ported from sandbox/geo_dev.ipynb:
  - Build an undirected NetworkX graph from walking edges
  - Snap POI lat/lon onto the nearest network node
  - Shortest-path walking distance and time between stops

First graph build takes ~1 s; subsequent calls use @lru_cache.
"""

from functools import lru_cache

import networkx as nx
import numpy as np
import pandas as pd

from app.engine.loaders.geo import load_walking_edges, load_walking_nodes

# Mean Earth radius for haversine distance calculations.
EARTH_RADIUS_M = 6_371_000
# Typical urban walking speed used to convert metres → minutes.
WALK_SPEED_MPS = 1.4  # ~5 km/h


@lru_cache(maxsize=1)
def get_walk_graph() -> nx.Graph:
    """
    Build and cache the undirected Camden walking graph.

    Edge weight = street length in metres (not hop count) so the shortest
    path reflects realistic walking distance.
    """
    edges = load_walking_edges()
    return nx.from_pandas_edgelist(
        edges,
        source="u",
        target="v",
        edge_attr="length",
    )


@lru_cache(maxsize=1)
def get_walking_nodes() -> pd.DataFrame:
    """Return cached walking-network node table (id, lat, lon)."""
    return load_walking_nodes()


def _haversine_vector_m(
    lat: float,
    lon: float,
    lats: np.ndarray,
    lons: np.ndarray,
) -> np.ndarray:
    """
    Vectorised haversine distance from one point to many candidates.

    Returns an array of distances in metres, one per (lat, lon) pair
    in the input arrays. Used for POI→node snapping.
    """
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    lats_r = np.radians(lats)
    lons_r = np.radians(lons)
    dlat = lats_r - lat_r
    dlon = lons_r - lon_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat_r) * np.cos(lats_r) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def snap_points_to_network(
    points: pd.DataFrame,
    *,
    lat_col: str = "lat",
    lon_col: str = "lon",
    max_distance_m: float = 100,
) -> pd.DataFrame:
    """
    Attach the nearest walking-network node ID to each lat/lon point.

    POIs farther than max_distance_m from any network node are dropped —
    they cannot be routed realistically (e.g. inside a building block
    with no nearby footpath). Adds columns:
      - snap_dist_m: straight-line distance to snapped node
      - node_id:     OSM network node used for routing
    """
    nodes = get_walking_nodes()
    node_lats = nodes["lat"].to_numpy()
    node_lons = nodes["lon"].to_numpy()
    node_ids = nodes["id"].to_numpy()

    routable = points.dropna(subset=[lat_col, lon_col]).copy()
    if routable.empty:
        return routable

    snap_dists: list[float] = []
    snapped_nodes: list[int] = []
    for _, row in routable.iterrows():
        # Find nearest junction node by straight-line distance.
        dists = _haversine_vector_m(
            float(row[lat_col]),
            float(row[lon_col]),
            node_lats,
            node_lons,
        )
        idx = int(np.argmin(dists))
        snap_dists.append(float(dists[idx]))
        snapped_nodes.append(int(node_ids[idx]))

    routable["snap_dist_m"] = snap_dists
    routable["node_id"] = snapped_nodes
    # Keep only POIs that are plausibly on or beside the walking network.
    return routable[routable["snap_dist_m"] <= max_distance_m].copy()


def walk_distance_m(node_a: int, node_b: int) -> float | None:
    """
    Shortest walking distance between two network nodes, in metres.

    Returns None if no footpath route exists (disconnected subgraph).
    """
    graph = get_walk_graph()
    try:
        return nx.shortest_path_length(graph, node_a, node_b, weight="length")
    except nx.NetworkXNoPath:
        return None


def walk_time_minutes(node_a: int, node_b: int) -> float | None:
    """Convert shortest-path walking distance to minutes at WALK_SPEED_MPS."""
    metres = walk_distance_m(node_a, node_b)
    if metres is None:
        return None
    return metres / WALK_SPEED_MPS / 60


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Straight-line distance between two coordinates, in metres.

    Used for proximity scoring and FHRS matching where graph routing
    between arbitrary points is not required.
    """
    return float(
        _haversine_vector_m(lat1, lon1, np.array([lat2]), np.array([lon2]))[0]
    )
