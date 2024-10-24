from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="api_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    db_drivername: str
    db_database: str
    model: str
    device: str


@lru_cache
def get_config():
    return Config()
