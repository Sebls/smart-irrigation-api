import importlib
import sys

import dotenv
import pytest
import sqlalchemy
from sqlalchemy import inspect, text


def _import_fresh_db(
    monkeypatch: pytest.MonkeyPatch,
    *,
    env: dict[str, str],
):
    # Avoid local `.env` affecting tests.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    for k, v in env.items():
        monkeypatch.setenv(k, v)

    # Ensure app.config + db module are re-evaluated with the new env.
    sys.modules.pop("app.config", None)
    sys.modules.pop("app.infrastructure.db.database", None)

    captured: dict[str, object] = {}
    real_create_engine = sqlalchemy.create_engine

    def spy_create_engine(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return real_create_engine(*args, **kwargs)

    # `app.infrastructure.db.database` does `from sqlalchemy import create_engine`,
    # so patching `sqlalchemy.create_engine` before import lets us capture args.
    monkeypatch.setattr(sqlalchemy, "create_engine", spy_create_engine)

    import app.infrastructure.db.database as db  # noqa: WPS433 (controlled import)

    return importlib.reload(db), captured


def test_engine_sets_sqlite_check_same_thread_false(monkeypatch: pytest.MonkeyPatch) -> None:
    db, captured = _import_fresh_db(
        monkeypatch,
        env={
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "SQL_ECHO": "0",
        },
    )

    kwargs = captured["kwargs"]
    assert kwargs["connect_args"] == {"check_same_thread": False}
    assert db.engine.url.get_backend_name() == "sqlite"


def test_init_db_creates_expected_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    db, _ = _import_fresh_db(
        monkeypatch,
        env={
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "SQL_ECHO": "0",
        },
    )

    db.init_db()

    tables = set(inspect(db.engine).get_table_names())
    # A small, representative subset (not the full schema).
    assert {"zones", "plants", "sensors", "sensor_readings", "irrigation_jobs"} <= tables


def test_sessionlocal_can_execute_query(monkeypatch: pytest.MonkeyPatch) -> None:
    db, _ = _import_fresh_db(
        monkeypatch,
        env={
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "SQL_ECHO": "0",
        },
    )

    with db.SessionLocal() as session:
        value = session.execute(text("select 1")).scalar_one()
        assert value == 1

