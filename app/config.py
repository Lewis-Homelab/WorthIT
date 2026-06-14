from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_port: int = 8000
    health_path: str = "/health"
    database_url: str = (
        "postgresql+asyncpg://worthit:worthit@localhost:5432/worthit"
    )
    google_places_api_key: str = ""


settings = Settings()
