# Frontend endpoints contract (to satisfy `docs/frontend_requirements.md`)

This document explains the **API endpoints** (current + missing) needed to satisfy the viewing requirements in `docs/frontend_requirements.md`.

## Base path

- **Base path**: `/api/v1`
- **IDs**: UUID strings (path params or JSON strings depending on schema)
- **Dates**: ISO-8601 strings in JSON

---

## Devices (dashboard-managed devices)

### List devices

- **GET** `/api/v1/devices`
- **Query params**: none
- **200 response**: `Device[]`
  - `id: uuid`
  - `name: string`
  - `description: string | null`
  - `is_active: boolean`
  - `last_seen_at: datetime | null`
  - `is_online: boolean`
  - `uptime: number | null`
  - `created_at: datetime`
  - `updated_at: datetime`
  - **Missing today**: `hardware_id` is not included in the response schema but is required for the frontend requirement “MAC/serial”.

### Create device

- **POST** `/api/v1/devices`
- **Body**: `DeviceCreate`
  - `name: string`
  - `description?: string | null`
  - `is_active?: boolean`
- **201 response**: `Device`

### Get device by id

- **GET** `/api/v1/devices/{device_id}`
- **Path params**
  - `device_id: uuid`
- **200 response**: `Device`

### Update device

- **PUT** `/api/v1/devices/{device_id}`
- **Path params**
  - `device_id: uuid`
- **Body**: `DeviceUpdate`
  - `name?: string | null`
  - `description?: string | null`
  - `is_active?: boolean | null`
- **200 response**: `Device`

### Delete device

- **DELETE** `/api/v1/devices/{device_id}`
- **Path params**
  - `device_id: uuid`
- **200 response**: `Device`

### Provision device (creates device + ensures default zone + registers sensors)

- **POST** `/api/v1/devices/provision`
- **Body**: `ProvisionRequest`
  - `hardwareId: string` (device MAC/serial)
  - `firmware: string`
  - `capabilities`
    - `sensors: { localName: string, type: "humidity" | "temperature" | "flow" | "water-level" | "air-quality" }[]`
    - `cameras?: string[]`
- **200 response**: `ProvisionResponse`
  - `deviceId: uuid`
  - `timezone: string`
  - `location: object | null`
  - `polling: { telemetryIntervalSec: number, heartbeatIntervalSec: number }`
  - `sensors: { localName: string, sensorId: uuid, type: SensorType, unit: string }[]`
  - `cameras: { localName: string, cameraId: uuid }[]` (cameraId is currently a placeholder UUID)

### Device images (read/list + fetch full image bytes)

The ingestion endpoint `POST /api/v1/external-devices/{device_id}/images` stores:

- an entry in `device_images` (metadata)
- a file on disk (currently referenced by `imageUrl`, typically `uploads/devices/{device_id}/{type}.jpg`)

For the frontend, **do not** use `imageUrl` directly in an `<img src="...">` (it’s a server-local path). Use the file endpoints below to fetch the **full image bytes**.

#### List image metadata for a device

- **GET** `/api/v1/devices/{device_id}/images`
- **Path params**
  - `device_id: uuid`
- **200 response**: `DeviceImageResponse[]`

#### Get image metadata by id

- **GET** `/api/v1/devices/{device_id}/images/{image_id}`
- **Path params**
  - `device_id: uuid`
  - `image_id: uuid`
- **200 response**: `DeviceImageResponse`

#### Download image file by image id (returns bytes)

- **GET** `/api/v1/devices/{device_id}/images/{image_id}/file`
- **Path params**
  - `device_id: uuid`
  - `image_id: uuid`
- **200 response**: binary image (e.g. `image/jpeg`)

#### Download latest image file by type (returns bytes)

- **GET** `/api/v1/devices/{device_id}/images/by-type/{image_type}/file`
- **Path params**
  - `device_id: uuid`
  - `image_type: string` (same value as the upload form field `type`)
- **200 response**: binary image (e.g. `image/jpeg`)

---

## External device ingestion (telemetry/logs/images + status)

### Ingest telemetry (saves into `sensor_readings`)

- **POST** `/api/v1/external-devices/{device_id}/telemetry`
- **Path params**
  - `device_id: uuid`
- **Body**: `TelemetryRequest`
  - `sentAt: datetime`
  - `readings: SensorReading[]`
    - `sensorId: string` (the backend currently expects this to be a UUID string for an existing sensor)
    - `type: SensorType`
    - `value: number`
    - `unit: string`
    - `readingAt?: datetime | null`
- **201 response**: `TelemetryResponse`
  - `id: uuid`
  - `deviceId: string`
  - `status: string` (defaults to `"accepted"`)
  - `processedCount: number`

### Ingest device log (saves into `device_logs`)

- **POST** `/api/v1/external-devices/{device_id}/logs`
- **Path params**
  - `device_id: uuid`
- **Body**: `DeviceLogCreate`
  - `level: string` (e.g. `info|warning|error|critical`)
  - `message: string`
  - `recordedAt?: datetime | null`
- **201 response**: `DeviceLogResponse`
  - `id: uuid`
  - `deviceId: uuid`
  - `level: string`
  - `message: string`
  - `recordedAt: datetime`
- **Missing today (needed for frontend)**: a **read/list endpoint** for logs (see “Missing endpoints”).

### Upload device image (saves into `device_images` + writes file to disk)

- **POST** `/api/v1/external-devices/{device_id}/images`
- **Path params**
  - `device_id: uuid`
- **Content-Type**: `multipart/form-data`
- **Form fields**
  - `file: file` (required)
  - `type: string` (required; used by frontend to group “cameras by type”)
  - `captured_at: datetime` (required)
  - `plant_id?: uuid`
  - `zone_id?: uuid`
  - `metadata?: string` (optional JSON string)
- **201 response**: `DeviceImageResponse`
  - `id: uuid`
  - `deviceId: uuid`
  - `plantId: uuid | null`
  - `zoneId: uuid | null`
  - `imageUrl: string` (currently a server-local path like `uploads/devices/{id}/{type}.jpg`)
  - `type: string`
  - `capturedAt: datetime`
- **Missing today (needed for frontend)**:
  - response field for `metadata_json` (to “view metadata”)
  - (optional) if you want `imageUrl` to be directly usable in the browser, serve `uploads/` as static; otherwise use the file download endpoints documented under **Devices → Device images**.

### Get device status (online/last seen/uptime)

- **GET** `/api/v1/external-devices/{device_id}/status`
- **Path params**
  - `device_id: uuid`
- **200 response**: `DeviceStatusResponse`
  - `deviceId: uuid`
  - `name: string`
  - `isOnline: boolean`
  - `lastSeenAt: datetime | null`
  - `uptime: number | null`

---

## Zones

### List zones

- **GET** `/api/v1/zones`
- **Query params**
  - `skip?: number` (default `0`)
  - `limit?: number` (default `100`)
- **200 response**: `Zone[]`
  - `id: uuid`
  - `name: string`
  - `is_active: boolean`
  - `created_at: datetime`
  - `updated_at: datetime`
  - `deleted_at: datetime | null`

### Create zone

- **POST** `/api/v1/zones`
- **Body**: `ZoneCreate`
  - `name: string`
  - `is_active?: boolean`
- **201 response**: `Zone`

### Get zone / update zone / delete zone

- **GET** `/api/v1/zones/{zone_id}` (zone_id is a UUID string)
- **PUT** `/api/v1/zones/{zone_id}` with body `ZoneUpdate` (`name?`, `is_active?`)
- **DELETE** `/api/v1/zones/{zone_id}` (soft delete)
- **Responses**: `Zone`

---

## Plants

### List plants

- **GET** `/api/v1/plants`
- **Query params**: none
- **200 response**: `Plant[]`
  - `id: uuid`
  - `name: string`
  - `zone_id: uuid`
  - `image_url: string | null`
  - `health: string`
- **Note**: There is no server-side filter by zone today; the frontend can filter client-side by `zone_id` or you can add `?zone_id=...`.

### Create / get / update / delete plant

- **POST** `/api/v1/plants` body `PlantCreate` (`name`, `zone_id`, `image_url?`, `health`)
- **GET** `/api/v1/plants/{plant_id}`
- **PUT** `/api/v1/plants/{plant_id}` body `PlantUpdate` (`name?`, `image_url?`, `health?`)
- **DELETE** `/api/v1/plants/{plant_id}`
- **Responses**: `Plant`

---

## Sensors

### List sensors

- **GET** `/api/v1/sensors`
- **Query params**
  - `skip?: number` (default `0`)
  - `limit?: number` (default `100`)
- **200 response**: `Sensor[]`
  - `id: uuid`
  - `name: string`
  - `type: string`
  - `unit: string`
  - `is_active: boolean`
  - `plant_id: uuid | null`
  - `zone_id: uuid | null`
  - `created_at: datetime`
  - `updated_at: datetime`
  - `deleted_at: datetime | null`
- **Note**: There is no server-side filter by `zone_id` / `plant_id` today; the frontend can filter client-side or you can add query params.

### Create / get / update / delete sensor

- **POST** `/api/v1/sensors` body `SensorCreate` (`name`, `type`, `unit`, `is_active?`, `plant_id?`, `zone_id?`)
- **GET** `/api/v1/sensors/{sensor_id}`
- **PUT** `/api/v1/sensors/{sensor_id}` body `SensorUpdate` (any fields optional)
- **DELETE** `/api/v1/sensors/{sensor_id}` (soft delete)
- **Responses**: `Sensor`

---

## Sensor readings (time series)

### Create reading (mainly for testing; production writes via telemetry)

- **POST** `/api/v1/sensor-readings`
- **Body**: `SensorReadingCreate`
  - `sensor_id: string` (UUID string)
  - `value: number`
  - `recorded_at?: datetime | null`
- **201 response**: `SensorReading`
  - `id: uuid`
  - `sensor_id: uuid`
  - `recorded_at: datetime`
  - `value: number`

### List readings (supports sensor filter)

- **GET** `/api/v1/sensor-readings`
- **Query params**
  - `sensor_id?: string` (UUID string)
  - `skip?: number` (default `0`)
  - `limit?: number` (default `100`)
- **200 response**: `SensorReading[]`

### Get reading / delete reading

- **GET** `/api/v1/sensor-readings/{reading_id}`
- **DELETE** `/api/v1/sensor-readings/{reading_id}`
- **Response**: `SensorReading`

---

## Irrigation jobs

### Create job / list jobs / get job / update job / delete job

- **POST** `/api/v1/irrigation` body `IrrigationJobCreate`
  - `scope: "zone" | "plant"`
  - `zone_id?: string | null`
  - `plant_id?: string | null`
  - `action: "start" | "stop"`
  - `duration_seconds?: number | null`
  - `status?: string` (defaults to `"accepted"`)
- **GET** `/api/v1/irrigation`
  - query: `status?`, `zone_id?`, `plant_id?`, `skip?`, `limit?`
- **GET** `/api/v1/irrigation/{job_id}`
- **PUT** `/api/v1/irrigation/{job_id}` body `IrrigationJobUpdate` (`status?`, `started_at?`, `ended_at?`, `error_message?`)
- **DELETE** `/api/v1/irrigation/{job_id}`
- **Responses**: `IrrigationJob` (fields: ids + action/duration/status + timestamps + error_message)

---

## Activity events

### Create event / list events / get event / delete event

- **POST** `/api/v1/activity` body `ActivityEventCreate`
  - `type: string`
  - `message: string`
  - `zone_id?: string | null`
  - `plant_id?: string | null`
  - `sensor_id?: string | null`
  - `occurred_at?: datetime | null`
- **GET** `/api/v1/activity`
  - query: `type?`, `zone_id?`, `plant_id?`, `sensor_id?`, `skip?`, `limit?`
- **GET** `/api/v1/activity/{event_id}`
- **DELETE** `/api/v1/activity/{event_id}`
- **Responses**: `ActivityEvent`

---

## Missing endpoints / contract gaps (required by the frontend requirements)

To fully satisfy `docs/frontend_requirements.md`, you still need one of the following approaches.

1. **Expose device hardware id in device responses**
   - Either add `hardware_id` to the `Device` response model (and populate it), or add a dedicated endpoint (e.g. `GET /api/v1/devices/{id}/identity`).

2. **List device logs**
   - Add: **GET** `/api/v1/devices/{device_id}/logs`
   - Suggested query params: `level?`, `since?`, `until?`, `limit?`, `offset?`
   - Suggested response: `DeviceLogResponse[]`

3. **List device images (group by type in the UI)**
   - Implemented: **GET** `/api/v1/devices/{device_id}/images`

4. **Return and display image metadata**
   - Extend `DeviceImageResponse` to include `metadataJson: object | null` (or `metadata_json: string | null`).

5. **Make `imageUrl` browser-accessible**
   - Option A: serve `uploads/` as static (e.g., mount `StaticFiles`) so `imageUrl` becomes a real public URL.
   - Option B (implemented): **GET** `/api/v1/devices/{device_id}/images/{image_id}/file` returning the image bytes.
   - Also available (implemented): **GET** `/api/v1/devices/{device_id}/images/by-type/{image_type}/file`

