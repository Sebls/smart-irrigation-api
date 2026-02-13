# Telemetry Ingestion Mapping

This document explains how the telemetry service (`/api/v1/telemetry/`) processes incoming data from devices and maps it to the internal database.

## 1. Pipeline Overview

The ingestion pipeline follows these steps:
1.  **Receive JSON**: The API receives a batch of readings in `camelCase` format.
2.  **Validate Schema**: Pydantic validates the input and converts `camelCase` to internal `snake_case`.
3.  **Sensor Resolution**: For each reading, the service attempts to find a matching sensor in the database.
4.  **Create Reading**: If a sensor is found, a new row is inserted into the `sensor_readings` table.

## 2. JSON to Database Mapping

### Input Structure (`TelemetryRequest`)
The incoming JSON uses `camelCase` as shown below:

```json
{
  "deviceId": "raspi-01",
  "sentAt": "2026-01-26T12:00:00.000Z",
  "readings": [
    {
      "sensorId": "s-1-1-1",
      "type": "humidity",
      "value": 74.1,
      "unit": "%"
    }
  ]
}
```

### Sensor Resolution Logic
The service identifies sensors strictly by their **UUID**.
1.  **UUID Match**: The `sensorId` field must be a valid UUID matching `sensors.id`.

> [!WARNING]
> If a `sensorId` is not a valid UUID or does not exist in the database, the reading is **discarded** and a warning is logged:
> `Unknown sensor in telemetry: Data don't will be saved` (with sensor and device IDs).

### Table Mapping
| JSON Field | DB Table | DB Column | Note |
| :--- | :--- | :--- | :--- |
| `readings[].sensorId` | `sensors` | `id` | Must be a valid UUID |
| `readings[].value` | `sensor_readings` | `value` | The actual metric |
| `readings[].reading_at` | `sensor_readings` | `recorded_at` | Uses reading time if provided |
| `sentAt` | `sensor_readings` | `recorded_at` | Falling back to batch time if individual reading time is missing |
| `deviceId` | - | - | Currently unused (for logging/filtering in future) |

## 3. Supported Sensor Types
The system enforces valid types via a check constraint on the `sensors` table and an Enum in the schema:
- `humidity`
- `temperature`
- `flow`
- `water-level`
- `air-quality`

## 4. Response
The service returns a `TelemetryResponse` confirming the process:
- `status`: Always `"accepted"` if the batch was parsed.
- `processedCount`: Number of readings successfully mapped and saved.
- `deviceId`: Echoes the device ID.
- `id`: Unique UUID for this ingestion transaction.
