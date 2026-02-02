"""Application configuration (shared by API + infrastructure).

This package is the single source of truth for environment-driven configuration.
It loads `.env` (if present) and exposes config values as module-level constants.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv


# Loads `.env` if present (not committed). Safe if the file doesn't exist.
load_dotenv()


def _getenv(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def _must_getenv(name: str) -> str:
    value = _getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it in your environment or a local `.env` file."
        )
    return value


def _getenv_bool(name: str, default: bool = False) -> bool:
    raw = _getenv(name)
    if raw is None:
        return default
    return raw.strip() in {"1", "true", "True", "yes", "YES"}


# Example: ENV=dev
ENV: str = _getenv("ENV", "dev") or "dev"

# Database configuration (prod or dev)
DATABASE_URL: str = _getenv("DATABASE_URL", "sqlite:///./smart_irrigation.db")

# Example: SQL_ECHO=1 to log SQL statements in dev
SQL_ECHO: bool = _getenv_bool("SQL_ECHO", default=False)

