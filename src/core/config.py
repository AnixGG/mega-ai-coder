import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    MODEL_NAME: str
    GH_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
DEBUG=True
# NORMAL=True
