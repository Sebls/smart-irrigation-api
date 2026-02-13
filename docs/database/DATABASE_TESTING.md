## Testing the current database implementation

This repo already contains:

- **Config loader**: `app/config/` (loads `.env`, exposes `DATABASE_URL`, `SQL_ECHO`)
- **SQLAlchemy engine/session**: `app/infrastructure/db/database.py` (`engine`, `SessionLocal`)
- **ORM models**: `app/infrastructure/models/` (tables from `docs/DATABASE_SCHEMA.md`)
- **Migrations**: `alembic/` + `alembic.ini` (schema is reproducible from git)

This document explains what you need, how it works, and how to test it.

---

## What you need

### 1) Python + venv

You need a working virtual environment with the dependencies installed.

```bash
cd /Users/usuario/Documents/github/smart-irrigation-api
source venv/bin/activate
python -m pip install -r requirements.txt
```

### 2) A `DATABASE_URL`

The database layer reads `DATABASE_URL` from env (and `.env` if present) via `app/config/__init__.py`.

You can use:

- **SQLite (local dev / easiest)**:
  - `DATABASE_URL=sqlite:///./smart_irrigation.db`
- **PostgreSQL (recommended target)**:
  - `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME`

Set it for your shell session:

```bash
export DATABASE_URL="sqlite:///./smart_irrigation.db"
```

Or create a local `.env` file (don’t commit it) with:

```text
DATABASE_URL=sqlite:///./smart_irrigation.db
SQL_ECHO=0
```

---

## How it works (mental model)

### Config

- `app/config/` calls `dotenv.load_dotenv()` once.
- Any module can import shared settings like:
  - `from app.config import DATABASE_URL, SQL_ECHO`

### SQLAlchemy engine/session

`app/infrastructure/db/database.py`:

- Builds a SQLAlchemy **engine** from `DATABASE_URL`
- Exposes `SessionLocal` (a session factory) for DB access
- Has `init_db()` as a convenience for dev, but migrations are the source of truth

### ORM models

`app/infrastructure/models/` contains one file per “area” (zones, plants, sensors, etc.).

Importing `app.infrastructure.models` ensures all models are registered on `Base.metadata`.

### Alembic migrations

- `alembic/env.py` loads `DATABASE_URL` from `app.config`
- Migration files in `alembic/versions/` describe schema changes
- Running `alembic upgrade head` applies them to the database referenced by `DATABASE_URL`

---

## The recommended way to test: run migrations

### 1) Apply the schema

```bash
cd /Users/usuario/Documents/github/smart-irrigation-api
source venv/bin/activate
export DATABASE_URL="sqlite:///./smart_irrigation.db"
python -m alembic upgrade head
```

If that succeeds, the database now has the tables defined in the initial migration.

### 2) Verify tables exist (SQLite)

```bash
sqlite3 smart_irrigation.db ".tables"
```

You should see tables like:

- `zones`, `plants`, `sensors`, `sensor_readings`
- `irrigation_jobs`
- `activity_events`
 - `devices`, `device_logs`, `device_images`

---

## A simple “smoke test” using SQLAlchemy (insert + query)

Run this from repo root after setting `DATABASE_URL`:

```bash
cd /Users/usuario/Documents/github/smart-irrigation-api
source venv/bin/activate
export DATABASE_URL="sqlite:///./smart_irrigation.db"

python - <<'PY'
from app.infrastructure.db.database import SessionLocal
from app.infrastructure.models.zones import Zone

db = SessionLocal()
try:
    z = Zone(name="Zone A", is_active=False)
    db.add(z)
    db.commit()
    db.refresh(z)
    print("Inserted zone:", z.id, z.name, z.is_active)

    zones = db.query(Zone).all()
    print("Zones count:", len(zones))
finally:
    db.close()
PY
```

If you see an inserted UUID and the zones count increments, the DB wiring is working.

---

## Testing with PostgreSQL (optional)

### 1) Ensure you have a running Postgres and a database created

You need a connection string like:

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME"
```

### 2) Apply migrations

```bash
alembic upgrade head
```

### 3) Verify tables (psql)

```bash
psql "$DATABASE_URL" -c "\dt"
```

---

## Common issues / troubleshooting

### “Missing DATABASE_URL”

- Make sure you exported `DATABASE_URL` in the same shell where you run commands, or created a local `.env`.

### “No module named …”

- Activate venv and install deps:
  - `source venv/bin/activate`
  - `python -m pip install -r requirements.txt`

### I changed models, but my DB didn’t change

- SQLAlchemy models do **not** automatically alter existing DBs.
- Add a new Alembic revision and run `alembic upgrade head`.

---

## What’s *not* included yet

- No API endpoints for these tables yet (you said you’ll add those next).
- No seed scripts yet (recommended later for dev fixtures).

