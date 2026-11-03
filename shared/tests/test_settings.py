"""Check configuration boundaries without any running services or real secrets."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from shared.settings import Settings


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Avoid reading developer environment variables or the repository's .env."""
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
        monkeypatch.delenv(name.lower(), raising=False)
    monkeypatch.chdir(tmp_path)


def test_environment_overrides_dotenv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("APP_ENV=test\nLOG_LEVEL=DEBUG\n", encoding="utf-8")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

    settings = Settings()

    assert settings.app_env == "test"
    assert settings.log_level == "WARNING"


def test_blank_credentials_are_unset(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("LLM_API_KEY=\nDATABASE_URL_READONLY=\n", encoding="utf-8")

    settings = Settings()

    assert settings.llm_api_key is None
    assert settings.database_url_readonly is None


def test_write_database_url_is_not_a_readonly_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://app_rw:fake-password@localhost/test")

    settings = Settings()

    assert settings.database_url is not None
    assert settings.database_url_readonly is None


def test_secrets_are_redacted(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-only-not-a-real-key"
    monkeypatch.setenv("LLM_API_KEY", secret)

    settings = Settings()

    assert settings.llm_api_key is not None
    assert settings.llm_api_key.get_secret_value() == secret
    assert secret not in repr(settings)
    assert secret not in settings.model_dump_json()


def test_invalid_environment_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "prodution")

    with pytest.raises(ValidationError, match="app_env"):
        Settings()
