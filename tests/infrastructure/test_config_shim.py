import importlib
import sys

import dotenv
import pytest


def _import_fresh(monkeypatch: pytest.MonkeyPatch, module_name: str, *, env: dict[str, str] | None = None):
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)

    sys.modules.pop(module_name, None)
    module = importlib.import_module(module_name)
    return importlib.reload(module)


def test_infrastructure_config_shim_exports_app_config_values(monkeypatch: pytest.MonkeyPatch) -> None:
    env = {"ENV": "test", "DATABASE_URL": "sqlite+pysqlite:///:memory:", "SQL_ECHO": "1"}

    cfg = _import_fresh(monkeypatch, "app.config", env=env)
    infra_cfg = _import_fresh(monkeypatch, "app.infrastructure.config", env=env)

    assert infra_cfg.ENV == cfg.ENV
    assert infra_cfg.DATABASE_URL == cfg.DATABASE_URL
    assert infra_cfg.SQL_ECHO == cfg.SQL_ECHO

