## Smart Irrigation API

The Smart Irrigation API is a backend service designed to support a smart irrigation system, exposing a unified interface for ingesting and serving data related to irrigation zones, plants, and sensors.

This repository focuses on a **clean architecture** that separates routing, models, schemas, services, and database concerns.

The system follows a hierarchical data model:

* The system is composed of multiple irrigation zones.
* Each irrigation zone contains multiple plants.
* Each plant can have one or more soil humidity sensors, in addition to zone-level environmental sensors.

The API is intended to be consumed by a frontend dashboard and other services; it does not communicate directly with hardware devices.

## Project structure

This project uses a modular FastAPI layout that scales well as the codebase grows.

```text
alembic/                   # Alembic migrations
  env.py
  versions/                # Alembic versions
alembic.ini
app/
  __init__.py
  main.py                  # Application entrypoint (imports API app)
  api/                      # API layer (FastAPI app factory + routers/schemas/services)
    __init__.py
    main.py
    dependencies.py         # Shared dependencies (e.g., DB session)
    routers/
      __init__.py
    schemas/
      __init__.py
    services/
      __init__.py
  config/                   # App-level configuration package
    __init__.py
  infrastructure/           # Infrastructure layer (config/security/db/models)
    __init__.py
    config.py
    security.py
    db/                     # Database engine/session setup + migrations placeholder
      __init__.py
      base.py
      database.py
      migrations/
        README.md
    models/                 # SQLAlchemy models
      __init__.py
      _mixins.py
      activity.py
      irrigation.py
      plants.py
      sensor_readings.py
      sensors.py
      water.py
      zones.py
docs/                      # API + DB documentation
tests/
  __init__.py
  conftest.py
  test_main.py
  config/
    test_config.py
  infrastructure/
    test_config_shim.py
    test_database.py
    test_security.py
requirements.txt
run.sh
smart_irrigation.db
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

### Run the API (development)

```bash
./run.sh
```

Then open `http://127.0.0.1:8000`.

### Tests

```bash
python -m pytest -q
```
