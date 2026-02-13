# Sensors API (`/sensors`)

This document defines the **backend API responses required to power the Sensors view** implemented at `app/sensors/page.tsx`.

The Sensors page renders:

- Summary stats (total sensors, avg humidity, zones monitored, plants tracked)
- Filters: zone, plant, sensor type
- Comparison chart (last 24 hours for up to 5 sensors)
- Table of all sensors with current value, status, and trend (computed from last readings)

## Conventions

- **Base path**: examples use `/api/...` (adjust to your gateway prefix).
- **Dates**: serialize timestamps as **ISO 8601 strings**.
- **Measurement**:
  - Current UI mainly uses soil humidity (`%`) even though a “sensor type” selector exists.
  - For forward compatibility, responses include `type` + `unit`.

---

## Endpoint: Sensors Filters

**GET** `/api/sensors/filters?zoneId=...`

Provides the lists needed to populate dropdowns:

- Zones dropdown always
- Plants dropdown filtered by zone (or all plants when zone is not specified)

### Query params

- `zoneId` (`string`, optional): if provided, restrict plants to this zone

### Response 200

```json
{
  "zones": [{ "id": "zone-1", "name": "Front Garden" }],
  "plants": [{ "id": "plant-1-1", "zoneId": "zone-1", "name": "Rose Bush" }]
}
```

### Field contract

- `zones[]`: `{ id: string; name: string }`
- `plants[]`: `{ id: string; zoneId: string; name: string }`

---

## Endpoint: Sensors Summary

**GET** `/api/sensors/summary?zoneId=...&plantId=...&type=...`

Returns the 4 stat-card numbers shown at the top of the Sensors page.

### Query params

- `zoneId` (`string`, optional) — omit for all zones
- `plantId` (`string`, optional) — omit for all plants
- `type` (`"humidity" | "temperature" | "air-quality"`, optional)

### Response 200

```json
{
  "summary": {
    "totalSensors": 12,
    "avgValue": 58,
    "zonesMonitored": 3,
    "plantsTracked": 6,
    "type": "humidity",
    "unit": "%"
  },
  "generatedAt": "2026-01-26T12:00:00.000Z"
}
```

### Field contract

- `summary.totalSensors` (`number`)
- `summary.avgValue` (`number`)
- `summary.zonesMonitored` (`number`)
- `summary.plantsTracked` (`number`)
- `summary.type` (`"humidity" | "temperature" | "air-quality"`)
- `summary.unit` (`string`) e.g. `"%"`, `"°C"`
- `generatedAt` (`string`, ISO 8601)

---

## Endpoint: List Sensors (table + comparison)

**GET** `/api/sensors?zoneId=...&plantId=...&type=...&includeReadings=true&readingsLimit=24`

Returns all sensors matching the filters.

The UI needs:

- `plantName` to show the Plant column
- `zoneName` to show the Zone column
- `currentValue` for “Current Value”
- enough readings to compute:
  - comparison chart (last 24 points for up to 5 sensors)
  - trend (last value - first value of last 5 points)

### Query params

- `zoneId` (`string`, optional)
- `plantId` (`string`, optional)
- `type` (`"humidity" | "temperature" | "air-quality"`, optional)
- `includeReadings` (`boolean`, default `false`)
- `readingsLimit` (`number`, optional; recommended `24`)
- `from` (`string`, ISO 8601, optional)
- `to` (`string`, ISO 8601, optional)

### Response 200

```json
{
  "sensors": [
    {
      "id": "s-1-1-1",
      "name": "Root Level",
      "type": "humidity",
      "unit": "%",
      "zone": { "id": "zone-1", "name": "Front Garden" },
      "plant": { "id": "plant-1-1", "name": "Rose Bush" },
      "currentValue": 74,
      "readings": [
        { "timestamp": "2026-01-26T11:00:00.000Z", "value": 73.2 },
        { "timestamp": "2026-01-26T12:00:00.000Z", "value": 74.1 }
      ]
    }
  ],
  "total": 1
}
```

### Field contract (per sensor)

Required for the table + charts:

- `id` (`string`)
- `name` (`string`)
- `type` (`"humidity" | "temperature" | "air-quality"`)
- `unit` (`string`)
- `zone.id` (`string`)
- `zone.name` (`string`)
- `plant.id` (`string`)
- `plant.name` (`string`)
- `currentValue` (`number`)
- `readings` (`Array<{ timestamp: string; value: number }>`), when `includeReadings=true`

### Notes (mapping to current UI)

- The current UI uses `sensor.humidity` and assumes `%`. You can map:
  - `currentValue` → the displayed value
  - `unit` → suffix (`%`, `°C`, etc.)
- “Status” can be computed client-side from thresholds. If you want server-side status, include optional:
  - `status` (`"optimal" | "moderate" | "low"`)

---

## Endpoint: Readings for a Sensor (optional)

If you prefer not to embed readings in the list response:

**GET** `/api/sensors/{sensorId}/readings?from=...&to=...&limit=24`

### Response 200

```json
{
  "sensorId": "s-1-1-1",
  "type": "humidity",
  "unit": "%",
  "readings": [{ "timestamp": "2026-01-26T12:00:00.000Z", "value": 74.1 }]
}
```

---

## Error responses (recommended)

```json
{
  "error": { "code": "VALIDATION_ERROR", "message": "Invalid query params" }
}
```

