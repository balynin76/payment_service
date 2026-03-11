import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str
    APP_NAME: str = "Payment Service"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev_payment.db")
    model_config = ConfigDict(env_file=".env", extra="ignore")
settings = Settings()