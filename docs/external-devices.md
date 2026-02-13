# External Devices Behavior Documentation

This document describes the current state, behavior, and data flow of the **External Devices** component in the Smart Irrigation API.

## Overview

The `external-devices` module provides a set of endpoints designed for peripheral hardware (e.g., ESP32, Arduino, Raspberry Pi) to communicate with the system. It handles telemetry data, operational logs, device images, and liveness monitoring.

## Core Entities & Models

### 1. Device (`DeviceModel`)
Represents a physical device in the field.
- **Attributes**: `id` (UUID), `name`, `description`, `is_active`.
- **Liveness**: Tracks `last_seen_at`, `is_online`, and `uptime`.
- **Behavior**: Any interaction with the `/external-devices` endpoints automatically registers a new device or updates the `last_seen_at` timestamp for an existing one.

### 2. Device Logs (`DeviceLogModel`)
Stores diagnostic messages from the hardware.
- **Attributes**: `level` (info, warning, error, critical), `message`, `recorded_at`.
- **Purpose**: Helps in remote debugging of connectivity or hardware failures without physical access to the device.

### 3. Device Images (`DeviceImageModel`)
Stores references to images captured by the device.
- **Attributes**: `image_url` (local path), `type` (plant, tank, zone), `captured_at`, `metadata`.
- **Storage**: Physical images are saved in `uploads/devices/{id}/{type}.jpg`.
- **Behavior**: The system keeps the most recent image for each `type` per device (Upsert logic).

### 4. Telemetry & Sensor Readings
While not a dedicated "external device" model, telemetry ingestion is a primary function.
- **Data Flow**: `TelemetryRequest` -> `save_telemetry` -> `SensorReadingModel`.
- **Validation**: Incoming telemetry only saves data for `sensor_id`s that already exist in the `sensors` table.

## Data Schema & Expectations

### Telemetry Request
Sent to `POST /api/v1/external-devices/{device_id}/telemetry`
```json
{
  "sentAt": "2024-02-04T12:00:00Z",
  "readings": [
    {
      "sensorId": "uuid-here",
      "type": "humidity",
      "value": 45.2,
      "unit": "%",
      "readingAt": "2024-02-04T11:59:00Z"
    }
  ]
}
```

### Log Request
Sent to `POST /api/v1/external-devices/{device_id}/logs`
```json
{
  "level": "error",
  "message": "Wifi reconnection failed 3 times",
  "recordedAt": "2024-02-04T12:05:00Z"
}
```

### Image Request
Sent to `POST /api/v1/external-devices/{device_id}/images`
```json
{
  "imageBase64": "data:image/jpeg;base64,...",
  "type": "plant",
  "capturedAt": "2024-02-04T12:00:00Z",
  "plantId": "uuid-here"
}
```

## Database Impact

1. **Device Upsert**: Every call to these endpoints ensures the device exists in the `devices` table and marks it as `is_online` (within a 5-minute window).
2. **Persistence**:
   - Telemetry -> `sensor_readings` table.
   - Logs -> `device_logs` table.
   - Images -> `device_images` table + File System storage.

## What to do with this data? (Future Usage)

The data collected in the database serves several critical purposes:

### 1. Visualization & Monitoring
- **Dashboards**: Use `sensor_readings` to plot historical humidity, temperature, and water level charts for a zone, plant, sensor, water views.
