"""
Shared pytest configuration for WorthIT.

POC integration tests need parquet files under data/raw/ (gitignored).
They are skipped automatically when those files are absent — e.g. in GitHub CI.
Run them locally after generating data:  uv run pytest -m integration
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Repo root: tests/conftest.py → tests/ → WorthIT/
REPO_ROOT = Path(__file__).resolve().parent.parent

# Minimum file set for suggest_day_plans / recommendations API smoke tests.
POC_DATA_FILES = (
    REPO_ROOT / "data/raw/weather_data/openmeteo_camden_hourly.parquet",
    REPO_ROOT / "data/raw/geo_data/camden_pois.parquet",
    REPO_ROOT / "data/raw/geo_data/camden_walking_edges.parquet",
    REPO_ROOT / "data/raw/geo_data/camden_walking_nodes.parquet",
)


def poc_data_available() -> bool:
    """True when all gitignored POC parquet files are present on disk."""
    return all(path.exists() for path in POC_DATA_FILES)


def poc_data_missing() -> list[Path]:
    """Return which expected POC files are absent."""
    return [path for path in POC_DATA_FILES if not path.exists()]


@pytest.fixture
def require_poc_data() -> None:
    """Skip the test when data/raw/ has not been populated locally."""
    missing = poc_data_missing()
    if missing:
        pytest.skip(
            "POC parquet data not available (gitignored). "
            f"Missing: {missing[0].relative_to(REPO_ROOT)}. "
            "Generate locally or run: uv run pytest -m integration"
        )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: requires data/raw parquet files; skipped in CI when absent",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip integration tests when POC data is not on disk (unless explicitly requested)."""
    if config.getoption("-m") and "integration" in config.getoption("-m"):
        return
    if poc_data_available():
        return
    skip_marker = pytest.mark.skip(
        reason="POC data not available (gitignored) — integration tests skipped"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)
