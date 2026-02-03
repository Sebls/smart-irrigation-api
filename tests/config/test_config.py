import importlib
import sys

import dotenv
import pytest


def _import_fresh_config(
    monkeypatch: pytest.MonkeyPatch, *, env: dict[str, str] | None = None
) -> object:
    """
    Import `app.config` fresh after setting env and disabling `.env` auto-loading,
    so tests are deterministic and isolated.
    """
    # Avoid local `.env` affecting tests.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    # Apply env overrides.
    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)

    # Drop cached modules to force re-evaluation of module-level constants.
    sys.modules.pop("app.config.env", None)
    sys.modules.pop("app.config", None)

    import app.config  # noqa: WPS433 (import inside function for controlled reload)
    import app.config.env

    importlib.reload(app.config.env)
    return importlib.reload(app.config)


def test_config_defaults_when_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure expected defaults when no env vars are present.
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQL_ECHO", raising=False)

    cfg = _import_fresh_config(monkeypatch)

    assert cfg.ENV == "dev"
    assert cfg.DATABASE_URL == "sqlite:///./smart_irrigation.db"
    assert cfg.SQL_ECHO is False


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1", True),
        ("true", True),
        ("True", True),
        ("yes", True),
        ("YES", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("", False),
        ("   ", False),
    ],
)
def test_sql_echo_parsing(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: bool
) -> None:
    cfg = _import_fresh_config(
        monkeypatch,
        env={
            "SQL_ECHO": raw,
        },
    )

    assert cfg.SQL_ECHO is expected
