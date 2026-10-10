import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "MediPulse"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # PostgreSQL Database URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/medipulse_db"

    # Stock Risk Thresholds (in days)
    HIGH_RISK_THRESHOLD_DAYS: float = 3.0
    MEDIUM_RISK_THRESHOLD_DAYS: float = 7.0

    # Default Target Stock Coverage (in days)
    DEFAULT_TARGET_COVERAGE_DAYS: int = 30

    # Acceleration Threshold (e.g. 1.5x increase in 7d vs prior 7d)
    ACCELERATION_THRESHOLD_RATIO: float = 1.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
