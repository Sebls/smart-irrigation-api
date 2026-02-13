# General Data Pipeline — Smart Irrigation System

Your system has **three clearly separated planes**:

1. **Control plane** – configure and identify the environment (Zones, Plants, Sensors)
2. **Data plane** – ingest raw facts (telemetry, images, logs)
3. **Read / analytics plane** – populate domain insights for the dashboard

Keeping these separate is what makes the whole design solid.

---

## 1. Device onboarding & configuration (Control plane)

### Goal

Establish **trust, identity, and knowledge** between the server and a new physical device.

### Flow

1. **Device boots for the first time**

   * It has *no UUID*, no sensor IDs, no configuration.
   * It only knows its **hardware identity** (MAC, serial) and **capabilities**.

2. **Device calls provisioning endpoint**

   * **Manual Registration:** Admin calls `POST /api/v1/devices/` with name and description.
   * **Auto-registration:** If a device sends telemetry with a new UUID, the system automatically creates a `Device` record in `devices_service.py` (`_get_or_create_device`).
   * **Provisioning Request (Optional):** Sends:
     * hardware identifier
     * firmware version
     * list of *physical capabilities*
       (e.g. “I have 2 humidity sensors, 1 flow sensor, 1 camera”)

    `POST /api/v1/devices/provision` (To be fully implemented)
   ```
    {
    "hardwareId": "raspi-mac-or-serial",
    "firmware": "1.0.0",
    "capabilities": {
        "sensors": [
        { "localName": "soil_1", "type": "humidity" },
        { "localName": "flow_main", "type": "flow" }
        ],
        "cameras": ["front_cam", "irrigation_camera"]
    }
    }
    ```

3. **Server becomes the authority**

   * Creates (or updates):
     * `devices` row (UUID and metadata)
     * `sensors` rows (one per physical sensor in the device)
     * optional `cameras` metadata
   * Assigns:
     * `device_id` (UUID)
     * `sensor_id`s (UUIDs)
     * location (coordinates, timezone)
     * polling intervals
     * security credentials

4. **Server responds with configuration**

   * Returns:

     * device UUID
     * sensor UUID mapping
     * camera UUIDs
     * operational parameters

    ```
    {
        "deviceId": "uuid-generated-by-server",
        "timezone": "Europe/Paris",
        "location": {
            "lat": 4.7110,
            "lon": -74.0721
        },
        "polling": {
            "telemetryIntervalSec": 60,
            "heartbeatIntervalSec": 30
        },
        "sensors": [
            {
            "localName": "soil_1",
            "sensorId": "uuid-humidity-1",
            "type": "humidity",
            "unit": "%"
            },
            {
            "localName": "flow_main",
            "sensorId": "uuid-flow-1",
            "type": "flow",
            "unit": "L/min"
            }
        ],
        "cameras": [
            {
            "localName": "front_cam",
            "cameraId": "uuid-camera-1"
            }
        ]
    }
    ```

5. **Device persists this configuration**

   * From now on, it only talks using server-assigned UUIDs.

👉 **Result:**
The database now knows *the physical layout* of the system.
The hierarchy is established: **Zone > Plant > Sensor**.
No telemetry yet—only **domain structure** is created.

---

## 2. Normal device operation (Data plane)

Once provisioned, the device switches to data production.

---

### 2.1 Telemetry ingestion

#### Goal

Capture **raw physical measurements** as immutable facts via `POST /api/v1/external-devices/{device_id}/telemetry`.

#### Flow

1. **Device sends telemetry batch**

   * Uses:
     * device UUID (URL)
     * sensor UUIDs (payload)
   * Sends numeric values + timestamps.

   `POST /api/v1/external-devices/{device_id}/telemetry`

2. **Ingestion service processes batch**

   * Validates schema via `TelemetryRequest`
   * For each reading:
     * updates `devices.last_seen_at` (Auto-registration check)
     * resolves `sensor_id`
     * inserts into `sensor_readings`

3. **Optional side effects**

   * Liveness → update `devices.last_seen_at` and `is_online = True`.

👉 **Result:**
`sensor_readings` becomes the **single source of truth** for physics.

No business meaning yet. Just facts.

---

### 2.2 Other device data (same plane, different channels)

All still **append-only**, no domain mutation.

* **Images**
  * Route: `POST /api/v1/external-devices/{device_id}/images`
  * Stored in `uploads/devices/{device_id}/`
  * Metadata in `device_images` model.
* **Logs**
  * Route: `POST /api/v1/external-devices/{device_id}/logs`
  * Stored in `device_logs` model for diagnostics.
* **Heartbeats**
  * Route: `GET /api/v1/external-devices/{device_id}/status`
  * Returns online status and last seen timestamp.

These do **not** affect zones, plants, or dashboards directly.

---

## 3. Backend aggregation & enrichment (Analytics plane)

This is where **facts become meaning**.

Nothing here is written by devices.

---

### 3.1 Update Job

#### Goal

Transform raw readings into **query-friendly insights** (The "Populate" process).

Typical jobs (To be implemented/refined):

* **From `sensor_readings`** →
    Update `activity_events` when thresholds are met (e.g., "Critical: Low Soil Moisture").
* **Aggregation** →
    Calculate trends and health patterns for specific **Plants** and **Zones**.

These tables/views are:

* **derived**: Calculated from raw measurements.
* **recomputable**: Can be rebuilt if the analytics logic changes.
* **never authoritative**: The raw readings remain the source of truth.

---

### 3.2 Read models & views

#### Goal

Serve the dashboard efficiently.

Views combine:

* domain tables (`zones`, `plants`, `sensors`)
* latest readings
* irrigation jobs

Examples:

* `v_zone_overview`
* `v_sensor_current`

👉 These are **pure projections**, no writes.

---

## 4. Dashboard & API consumption (Read plane)

Now the UI queries:

* `/overview` → summary from views
* `/zones` → zone cards from views
* `/sensors` → current values + trends
* `/activity` → `activity_events`

At this point:

* No device interaction
* No raw telemetry
* Only **domain-level data**

---

## 5. The full lifecycle in one picture (mentally)

```text
Device boots
   ↓
Provisioning (control plane)
   → devices, sensors created
   ↓
Telemetry / images / logs (data plane)
   → sensor_readings (facts)
   ↓
Aggregation jobs (analytics plane)
   → derived insights (trends, health, alerts)
   ↓
Views & queries (read plane)
   → dashboard
```

---

## Key principles your design follows (and why it works)

* **Devices never write domain tables**
* **Telemetry is immutable**
* **Identity is server-owned**
* **Aggregates are derived, not trusted**
* **Dashboard reads projections, not raw data**

That’s the same architecture used by:

* industrial SCADA
* cloud IoT platforms
* observability stacks
---

## 6. Domain Population Guide (Control Plane)

To make the system functional, you must populate the domain models in a specific order due to their relationships.

### 1. Populate Zones (The Foundation)

* **Purpose:** Group plants and sensors by physical area (e.g., "Front Garden", "Greenhouse").
* **What is necessary:**
  * `name` (string): A unique, descriptive name.
* **Endpoint:** `POST /api/v1/zones/`

### 2. Populate Plants

* **Purpose:** Track individual plant health and requirements within a zone.
* **What is necessary:**
  * `name` (string): e.g., "Tomato A".
  * `zone_id` (UUID): Must refer to an existing Zone.
  * `health` (string): Must be one of `excellent`, `good`, `needs-attention`, or `critical`.
* **Endpoint:** `POST /api/v1/plants/`

### 3. Populate Sensors

* **Purpose:** Ingest data from physical devices and link it to the domain.
* **What is necessary:**
  * `name` (string): e.g., "Soil Probe 1".
  * `type` (string): Must be one of `humidity`, `temperature`, `air-quality`, `water-level`, or `flow`.
  * `unit` (string): e.g., `%`, `°C`.
  * **Context (Exactly one):**
    * `plant_id` (UUID): If the sensor monitors a specific plant.
    * `zone_id` (UUID): If the sensor monitors the whole zone.
* **Endpoint:** `POST /api/v1/sensors/`

### 4. Register Devices (The Hardware)

* **Manual:** Use `POST /api/v1/devices/` to register the hardware ID.
---

## Final one-liner


> Devices describe reality,
> telemetry records facts,
> the backend creates meaning,
> and the dashboard only reads projections.

That’s a production-grade data pipeline.