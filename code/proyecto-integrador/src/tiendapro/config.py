"""Settings de la app: lee de env vars y .env.

Cosas que cambian entre entornos viven acá. El código las LEE; no las define.
Por convención del integrador, las variables se prefijan con `TIENDAPRO_`
(ej. `TIENDAPRO_DATABASE_URL`) para no chocar con otros servicios.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="TIENDAPRO_",
    )

    app_name: str = "TiendaPro"
    debug: bool = False
    database_url: str = "sqlite:///tiendapro.db"
    api_key: SecretStr = Field(default=SecretStr("change-me"))
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    enable_enrichment: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Singleton — se construye una sola vez por proceso."""
    return Settings()
