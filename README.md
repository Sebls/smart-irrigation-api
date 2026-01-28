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
app/
  __init__.py
  main.py              # FastAPI app factory + router registration
  dependencies.py      # Shared dependencies
  routers/             # Public routers
    __init__.py
    items.py
  internal/            # Internal/non-public routers
    __init__.py
  core/                # Configuration + security helpers
    __init__.py
    config.py
    security.py
  models/              # SQLAlchemy models
    __init__.py
    item.py
  schemas/             # Pydantic schemas (request/response models)
    __init__.py
    item.py
  services/            # Business logic (called by routes)
    __init__.py
    item_service.py
  db/                  # Database engine/session setup + migrations placeholder
    __init__.py
    database.py
    migrations/
      README.md
tests/
  __init__.py
  conftest.py
  test_main.py
  test_items.py
requirements.txt
run.sh
smart_irrigation.db
```

Notes:

- **Minimal API implemented**: `GET /items/` and `POST /items/` are implemented in `app/routers/items.py`.
- **SQLite by default**: if `DATABASE_URL` is not set, the default is `sqlite:///./smart_irrigation.db`.
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
