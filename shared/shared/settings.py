"""Central environment configuration; constructing settings performs no network I/O."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read environment variables, then a UTF-8 .env in the working directory.

    Future integrations are optional during scaffolding. Each service must validate
    its required configuration at startup when that integration is implemented.
    The agent must use database_url_readonly with no fallback to database_url.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    data_version: str = "unloaded"

    database_url: SecretStr | None = None
    database_url_readonly: SecretStr | None = None
    redis_url: SecretStr | None = None
    s3_bucket: str | None = None
    aws_region: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    reranker_model: str | None = None
    jwt_secret: SecretStr | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_base_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Load settings once per process, on first use rather than import."""
    return Settings()
