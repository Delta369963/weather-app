from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    OPENWEATHER_API_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/weatherapp"
    DB_NAME: str = "weatherapp"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
