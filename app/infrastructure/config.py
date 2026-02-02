"""Backward-compatible config shim.

Prefer importing from `app.config` (shared by API + infrastructure).
"""

from app.config import DATABASE_URL, ENV, SQL_ECHO  # noqa: F401