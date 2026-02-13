## Environment configuration

This project reads configuration from environment variables (and loads a local `.env` if present).

### Database

Set `DATABASE_URL` to your database connection string.

Examples:

- PostgreSQL (recommended):
  - `DATABASE_URL=postgresql+psycopg://user:password@host:5432/smart_irrigation`
- SQLite (dev-only fallback):
  - `DATABASE_URL=sqlite:///./smart_irrigation.db`

Optional:

- `SQL_ECHO=1` to log SQL statements (dev/debug).

