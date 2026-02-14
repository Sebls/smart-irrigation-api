# Backend overview (Smart Irrigation API)

This backend is a **FastAPI + SQLAlchemy** service that exposes CRUD APIs for the irrigation domain (zones, plants, sensors, readings, irrigation jobs, activity events) and a dedicated set of **external device ingestion** endpoints for telemetry, logs, and images.

The codebase is intentionally structured in layers:

- **Routers** (`app/api/routers/*`): HTTP endpoints (request/response, status codes, dependency injection).
- **Schemas** (`app/api/schemas/*`): Pydantic v2 DTOs used as API contracts.
- **Services** (`app/api/services/*`): business logic, validation, DB queries/transactions.
- **Infrastructure** (`app/infrastructure/*`): DB setup, ORM models, security utilities.
- **Config** (`app/config/*`): environment variables and simple settings.

The API is mounted under a versioned prefix:

- **Base path**: `/api/{API_VERSION}` (currently `API_VERSION="v1"`)
- In code: `app/main.py` creates an `APIRouter(prefix=f"/api/{API_VERSION}")` and includes all routers.

---

## Runtime entrypoints & app architecture

- **Uvicorn entrypoint**: the repository runs `uvicorn app.main:app ...` (see `app/main.py`).
- **App factory**: `create_app()` in `app/main.py` constructs the FastAPI app and includes all routers.
- **Note**: there is also `app/api/main.py` which includes a router named `items`; it is not referenced by `app/main.py` and appears to be a leftover/alternative app factory.

Typical request flow:

1. Router validates input using a Pydantic schema and injects a DB session with `Depends(get_db)`.
2. Router calls a service function (e.g. `zones_service.create_zone`).
3. Service writes/reads via SQLAlchemy ORM models and returns a Pydantic response model (often via `ModelSchema.model_validate(db_row)`).

---

## Configuration

Configuration is loaded from environment variables and optionally a local `.env`.

- **`.env` loading**: `python-dotenv` is used in `app/config/env.py` (`load_dotenv()`).
- **Key env vars**:
  - `ENV` (default: `"dev"`)
  - `DATABASE_URL` (default: `sqlite:///./smart_irrigation.db`)
  - `SQL_ECHO` (default: `False`) — set to `1/true/yes` to log SQL in dev

See also:

- `docs/config/ENVIRONMENT.md` (examples for Postgres/SQLite)

---

## Database connection, ORM models, and migrations

### Connection/session management

The DB stack is **SQLAlchemy 2.x**:

- `app/infrastructure/db/database.py` creates a global `engine` and `SessionLocal`.
- `app/api/dependencies.py:get_db()` yields a request-scoped SQLAlchemy `Session` and always closes it.
- SQLite special-casing: when `DATABASE_URL` is SQLite, `check_same_thread=False` is set to support threaded use (e.g. FastAPI `TestClient`).
- `pool_pre_ping=True` is enabled to reduce stale-connection issues (notably for Postgres).

### Models

ORM models live in `app/infrastructure/models/*` and use mixins:

- `UUIDPrimaryKeyMixin`: UUID primary key
- `TimestampMixin`: `created_at` / `updated_at`
- `SoftDeleteMixin`: `deleted_at` used by some entities

Soft-delete behavior is **model/service specific**:

- **Soft-deleted** (filters `deleted_at is NULL` in services): zones, sensors (and some others that use `SoftDeleteMixin`)
- **Hard-deleted** (actual `db.delete()`): plants, sensor readings, irrigation jobs, activity events, devices (device delete currently hard-deletes)

### Migrations

- Alembic is present (`alembic/` folder).
- There is a migrations readme at `app/infrastructure/db/migrations/README.md`.
- Recommended workflow is Alembic for schema changes; `init_db()` exists as a convenience to `create_all()` for quick local experiments.

See also:

- `docs/database/DATABASE_SCHEMA.md`
- `docs/database/DATABASE_TESTING.md`
- `docs/guidelines/DATABASE_GUIDELINE.md`

---

## Tests

The project uses **pytest** with FastAPI’s `TestClient`.

Patterns used in the suite:

- **App-level smoke tests**: `tests/test_main.py` verifies `/openapi.json` and `/docs` are reachable.
- **Endpoint tests**: `tests/api/test_*.py` cover CRUD and external endpoints.
- **DB isolation** for API tests:
  - Many tests create an **in-memory SQLite** engine (`sqlite:///:memory:`) with `StaticPool`.
  - Foreign keys are enabled via `PRAGMA foreign_keys=ON`.
  - The FastAPI dependency `get_db` is overridden (`app.dependency_overrides[get_db] = override_get_db`) to force the test session.
  - Tables are created and dropped per test for isolation (`Base.metadata.create_all` / `drop_all`).

Test guidance docs:

- `docs/guidelines/TEST_GUIDELINE.md`

---

## API surface (routers, endpoints, and CRUD)

All endpoints below are mounted under:

- `/api/v1` (because `API_VERSION = "v1"`)

### Zones (`/zones`) — CRUD (soft delete)

- `POST /zones/`: create zone
- `GET /zones/?skip=0&limit=100`: list zones (filters out `deleted_at`)
- `GET /zones/{zone_id}`: fetch zone by UUID
- `PUT /zones/{zone_id}`: update zone
- `DELETE /zones/{zone_id}`: **soft-delete** (sets `deleted_at`)

### Plants (`/plants`) — CRUD (hard delete)

- `POST /plants/`: create plant (requires `zone_id`)
- `GET /plants/`: list plants
- `GET /plants/{plant_id}`: get plant
- `PUT /plants/{plant_id}`: update plant
- `DELETE /plants/{plant_id}`: hard delete

### Sensors (`/sensors`) — CRUD (soft delete)

- `POST /sensors/`: create sensor (may reference `zone_id` and/or `plant_id`)
- `GET /sensors/?skip=0&limit=100`: list sensors (filters out `deleted_at`)
- `GET /sensors/{sensor_id}`: get sensor
- `PUT /sensors/{sensor_id}`: update sensor
- `DELETE /sensors/{sensor_id}`: **soft-delete** (sets `deleted_at`)

### Sensor readings (`/sensor-readings`) — create/list/get/delete

Sensor readings are treated as “mostly immutable”, but a delete endpoint exists for completeness.

- `POST /sensor-readings/`: create reading
- `GET /sensor-readings/?sensor_id=<uuid>&skip=0&limit=100`: list readings (optionally filtered by sensor)
- `GET /sensor-readings/{reading_id}`: get reading
- `DELETE /sensor-readings/{reading_id}`: hard delete

### Irrigation jobs (`/irrigation`) — CRUD

- `POST /irrigation/`: create irrigation job
- `GET /irrigation/?status=&zone_id=&plant_id=&skip=0&limit=100`: list irrigation jobs (filterable)
- `GET /irrigation/{job_id}`: get job
- `PUT /irrigation/{job_id}`: update job
- `DELETE /irrigation/{job_id}`: hard delete

### Activity events (`/activity`) — create/list/get/delete

- `POST /activity/`: create event
- `GET /activity/?type=&zone_id=&plant_id=&sensor_id=&skip=0&limit=100`: list events (filterable)
- `GET /activity/{event_id}`: get event
- `DELETE /activity/{event_id}`: hard delete

---

## Devices endpoints (CRUD + images + provisioning)

Router: `/devices` (`app/api/routers/devices.py`)

### Device CRUD

- `POST /devices/`: create device
- `GET /devices/`: list devices
- `GET /devices/{device_id}`: get device
- `PUT /devices/{device_id}`: update device
- `DELETE /devices/{device_id}`: delete device (currently hard delete)

### Device images (API-side retrieval)

These endpoints are for the dashboard/backend consumer to browse images already ingested via the external endpoints:

- `GET /devices/{device_id}/images`: list image metadata for the device
- `GET /devices/{device_id}/images/{image_id}`: get one image metadata record
- `GET /devices/{device_id}/images/{image_id}/file`: download/stream image file from disk
- `GET /devices/{device_id}/images/by-type/{image_type}/file`: download the latest image for a device and type

Images are stored on disk under:

- `uploads/devices/<device_id>/...`

There is path safety logic to prevent reading files outside `uploads/` when serving files.

### Provisioning endpoint

- `POST /devices/provision`

Purpose: allow a physical device (or provisioning client) to register itself by **hardware id**, declare **capabilities**, and receive server-assigned identifiers.

Current behavior (service-level):

- Finds or creates a `DeviceModel` by `hardware_id` (idempotent per hardware id).
- Ensures a default zone exists named **`"Primary Zone"`** (global, not per-device).
- Registers sensors based on `capabilities.sensors`:
  - Creates sensors named `"{hardwareId}-{localName}"` in the `"Primary Zone"`.
  - Sets `unit` by sensor type (e.g. humidity → `%`, flow → `L/min`).
- Cameras are currently treated as metadata-only:
  - Response includes camera `local_name` and a **placeholder UUID**.

The provisioning flow is tested in `tests/api/test_provisioning.py` (including idempotency expectations).

---

## External endpoints (device-to-backend ingestion)

Router: `/external-devices` (`app/api/routers/external_devices.py`)

These endpoints are designed to be called by **hardware devices** or an edge agent.

### Telemetry ingestion

- `POST /external-devices/{device_id}/telemetry`

Behavior:

- Ensures the device exists (creates it if missing) and updates liveness (`last_seen_at`, `is_online`).
- For each reading:
  - Accepts only `sensorId` values that parse as UUID and match an existing sensor.
  - Writes accepted readings via `sensor_readings_service.create_sensor_reading`.
  - Unknown sensors are ignored (a warning is logged) and do not block ingestion.

### Image ingestion (multipart/form-data)

- `POST /external-devices/{device_id}/images`

Fields:

- `file`: uploaded image file
- `type`: string (e.g. `"tank"`, `"plant"`, `"zone"`)
- `captured_at`: datetime
- optional: `plant_id`, `zone_id`, `metadata` (JSON string)

Behavior:

- Writes image bytes to `uploads/devices/<device_id>/<type>.jpg`.
- Upserts **one “current image” per (device, type)** in `device_images`.
- Stores `metadata_json` as JSON string when provided.

### Device logs

- `POST /external-devices/{device_id}/logs`

Behavior:

- Ensures the device exists and updates liveness.
- Inserts a row into `device_logs`.

### Device status

- `GET /external-devices/{device_id}/status`

Behavior:

- If device is unknown: returns `isOnline=false` with name `"Unknown Device"`.
- If known: marks device online if last seen within ~5 minutes (simple heuristic).

External ingestion behavior is covered in `tests/api/test_external_devices.py` (telemetry accepted/ignored, images written to disk, logs, and status).

See also:

- `docs/external-devices.md`
- `docs/api/TELEMETRY_INGESTION.md`

---

## “Frontend endpoints” documentation vs implemented endpoints

This repository includes several docs that define **expected backend endpoints for a frontend**, for example:

- `docs/api/OVERVIEW_API.md` (e.g. `GET /api/overview/summary`, `GET /api/overview/zones`)
- `docs/frontend_endpoints.md`

These documents are **contracts/requirements** for the frontend integration and may describe endpoints that are **not yet implemented** in `app/api/routers/*`.

---

## Security utilities (current scope)

The backend includes password hashing helpers in `app/infrastructure/security.py`:

- PBKDF2-HMAC-SHA256 hashing (`hash_password`)
- constant-time verification (`verify_password`)

There is currently **no authentication/authorization middleware** wired into the routers (no JWT/session/roles visible in the routing layer).

