"""Database engine + session setup (SQLAlchemy 2.x).

- Centralizes engine/session creation
- Uses DATABASE_URL from env (loaded via `app.config`)
- Keeps Base/metadata available for Alembic
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL, SQL_ECHO
from app.infrastructure.db.base import Base


def _make_engine():
    connect_args: dict[str, object] = {}
    # Accept sqlite URLs like:
    # - sqlite:///./file.db
    # - sqlite:///:memory:
    # - sqlite+pysqlite:///:memory:
    if make_url(DATABASE_URL).get_backend_name() == "sqlite":
        # Needed for SQLite when using threads (e.g., TestClient)
        connect_args["check_same_thread"] = False

    return create_engine(
        DATABASE_URL,
        echo=SQL_ECHO,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _make_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Dev helper (not a replacement for migrations).

    Prefer Alembic for schema changes; this exists to support quick local experiments.
    """

    # Ensure models are imported so Base.metadata is populated.
    from app.infrastructure import models as _  # noqa: F401

    Base.metadata.create_all(bind=engine)