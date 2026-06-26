from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration — loaded from .env and environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_port: int = 8000
    health_path: str = "/health"
    database_url: str = (
        "postgresql+asyncpg://worthit:worthit@localhost:5432/worthit"
    )
    google_places_api_key: str = ""

    # --- File-backed POC settings ---
    # Root directory for parquet datasets (see app/engine/paths.py).
    data_dir: str = "data"
    # Default map centre for Camden POC when the client omits lat/lon.
    default_latitude: float = 51.5390
    default_longitude: float = -0.1426


settings = Settings()
