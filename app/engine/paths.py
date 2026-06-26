"""
Resolve on-disk data paths for the file-backed POC.

All loaders read from data/raw/<source>/ via these helpers so path logic
lives in one place. Paths can be overridden via the DATA_DIR env var
(see app.config.Settings.data_dir).
"""

from pathlib import Path

from app.config import settings

# Repo root: app/engine/paths.py → app/ → WorthIT/
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def data_root() -> Path:
    """Return the root data directory (default: <repo>/data)."""
    path = Path(settings.data_dir)
    # Support both relative (repo-local) and absolute (homelab mount) paths.
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def raw_data_dir() -> Path:
    """Directory for untouched / pipeline-output raw files."""
    return data_root() / "raw"


def geo_data_dir() -> Path:
    """OpenStreetMap POIs and walking-network parquet files."""
    return raw_data_dir() / "geo_data"


def weather_data_dir() -> Path:
    """Cached Open-Meteo forecast parquet files."""
    return raw_data_dir() / "weather_data"


def fhrs_data_dir() -> Path:
    """Food Hygiene Rating Scheme (FHRS) establishment data."""
    return raw_data_dir() / "fhrs_data"
