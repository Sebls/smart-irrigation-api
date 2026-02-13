## Smart Irrigation API

The Smart Irrigation API is a backend service designed to support a smart irrigation system, exposing a unified interface for ingesting and serving data related to irrigation zones, plants, and sensors.

This repository focuses on a **clean architecture** that separates routing, models, schemas, services, and database concerns.

The system follows a hierarchical data model:

* The system is composed of multiple irrigation zones.
* Each irrigation zone contains multiple plants.
* Each plant can have one or more soil humidity sensors, in addition to zone-level environmental sensors.

The API is intended to be consumed by a frontend dashboard and other services; it does not communicate directly with hardware devices.

```
alembic
app
  api                    # API layer (FastAPI)
    main.py            # API app factory
    dependencies.py
    routers/           # HTTP endpoints
    schemas/           # Pydantic DTOs
    services/          # Business logic
    utils
  config                 # Environment handling
    env.py
  infrastructure         # Infra layer (DB, security, config)
    config.py
    security.py
    db/
    models/            # SQLAlchemy models
  main.py                # Entrypoint (imports API)
docs                       # Technical documentation
tests                      # Pytest test suite
  api/
  config/
  infrastructure/
  test_main.py
```

Notes:

- **Database URL via env**: set `DATABASE_URL` in `.env` (not committed) or environment variables.
- **SQLite fallback**: if `DATABASE_URL` is not set, the default is `sqlite:///./smart_irrigation.db` for local dev.
- **Env file**: create your own `.env` locally (no template included in this repo).

## Commands

### Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Alembic (database migrations)

Alembic uses `DATABASE_URL` from your environment (or a local `.env`) via `app/config/__init__.py`.

```bash
# optional: point migrations at a different DB (default is sqlite:///./smart_irrigation.db)
export DATABASE_URL="sqlite:///./smart_irrigation.db"

# show current revision
alembic current

# show migration history
alembic history

# create a new migration from model changes
alembic revision --autogenerate -m "describe change"

# apply migrations
alembic upgrade head

# rollback one migration
alembic downgrade -1
```

### Run the API (development)

```bash
./run.sh
```

Then open `http://127.0.0.1:8000`.

### Tests

```bash
python -m pytest -q
```
