# Zones API (`/zones`, `/zones/:zoneId`, `/zones/:zoneId/plants/:plantId`)

This document defines the **backend API responses required to power the Zones views**:

- Zones list: `app/zones/page.tsx`
- Zone detail: `app/zones/[zoneId]/page.tsx`
- Plant detail: `app/zones/[zoneId]/plants/[plantId]/page.tsx`
- Shared cards: `features/zones/components/zone-card.tsx`, `features/zones/components/plant-card.tsx`
- Sensor mini-chart on plant detail: `features/sensors/components/sensor-chart.tsx`

## Conventions

- **Base path**: examples use `/api/...` (adjust to your gateway prefix).
- **Dates**: serialize `Date` values to **ISO 8601 strings** in JSON.
- **Percentages**: `0..100` (`number`).
- **Units**:
  - Temperatures are **°C** (`temperatureC`), matching current UI.

---

## Endpoint: Zones Summary (for `/zones` stat cards)

**GET** `/api/zones/summary`

Powers the 4 stat cards at the top of the Zones page (active zones, total plants, avg humidity, avg temperature).

### Response 200

```json
{
  "summary": {
    "zonesTotal": 3,
    "zonesActive": 2,
    "plantsTotal": 12,
    "avgSoilHumidity": 61,
    "avgTemperatureC": 24
  },
  "generatedAt": "2026-01-26T12:00:00.000Z"
}
```

### Field contract

- `summary.zonesTotal` (`number`)
- `summary.zonesActive` (`number`)
- `summary.plantsTotal` (`number`)
- `summary.avgSoilHumidity` (`number`)
- `summary.avgTemperatureC` (`number`)
- `generatedAt` (`string`, ISO 8601)

---

## Endpoint: List Zones (for `/zones` grid)

**GET** `/api/zones`

Returns the list of zones displayed as cards (`ZoneCard`) on the Zones page.

### Query params (recommended)

- `limit` (`number`, optional)
- `offset` (`number`, optional)
- `include` (`string`, optional): e.g. `"preview"` to request the minimal shape

### Response 200

```json
{
  "zones": [
    {
      "id": "zone-1",
      "name": "Front Garden",
      "isActive": true,
      "plantCount": 2,
      "avgHumidity": 68,
      "temperatureC": 24,
      "lastIrrigated": "2026-01-26T10:00:00.000Z"
    }
  ],
  "total": 1
}
```

### Field contract (per zone)

Required by `ZoneCard` and list stats:

- `id` (`string`)
- `name` (`string`)
- `isActive` (`boolean`)
- `plantCount` (`number`)
- `avgHumidity` (`number`)
- `temperatureC` (`number`)
- `lastIrrigated` (`string`, ISO 8601)

---

## Endpoint: Get Zone Detail (for `/zones/:zoneId`)

**GET** `/api/zones/{zoneId}`

Returns everything needed to render the Zone detail header + metric cards + environmental block.

### Response 200

```json
{
  "zone": {
    "id": "zone-1",
    "name": "Front Garden",
    "isActive": true,
    "plantCount": 2,
    "avgHumidity": 68,
    "temperatureC": 24,
    "airHumidity": 62,
    "airQuality": 92,
    "lastIrrigated": "2026-01-26T10:00:00.000Z"
  }
}
```

### Field contract

Required by `app/zones/[zoneId]/page.tsx`:

- `id` (`string`)
- `name` (`string`)
- `isActive` (`boolean`)
- `plantCount` (`number`)
- `avgHumidity` (`number`)
- `temperatureC` (`number`)
- `airHumidity` (`number`)
- `airQuality` (`number`)
- `lastIrrigated` (`string`, ISO 8601)

Notes:

- The UI displays “Last Watered” as time-since; it only needs the timestamp.

---

## Endpoint: List Plants in Zone (for `/zones/:zoneId` plant grid)

**GET** `/api/zones/{zoneId}/plants`

Returns the plants shown in the Zone detail “Plants in Zone” grid (`PlantCard`).

### Response 200

```json
{
  "plants": [
    {
      "id": "plant-1-1",
      "zoneId": "zone-1",
      "name": "Rose Bush",
      "humidity": 72,
      "health": "excellent",
      "imageUrl": "/placeholder.svg?height=200&width=200",
      "sensorsCount": 2,
      "sensorsPreview": [
        { "id": "s-1-1-1", "name": "Root Level", "humidity": 74 },
        { "id": "s-1-1-2", "name": "Mid Level", "humidity": 70 }
      ]
    }
  ],
  "total": 1
}
```

### Field contract (per plant)

Required by `PlantCard`:

- `id` (`string`)
- `zoneId` (`string`)
- `name` (`string`)
- `humidity` (`number`)
- `health` (`"excellent" | "good" | "needs-attention" | "critical"`)
- `imageUrl` (`string | null`)
- `sensorsCount` (`number`)
- `sensorsPreview` (`Array<{ id: string; name: string; humidity: number }>`): provide up to 4

---

## Endpoint: Get Plant Detail (for `/zones/:zoneId/plants/:plantId`)

**GET** `/api/zones/{zoneId}/plants/{plantId}`

Returns the plant header + overview card.

### Response 200

```json
{
  "plant": {
    "id": "plant-1-1",
    "zoneId": "zone-1",
    "name": "Rose Bush",
    "humidity": 72,
    "health": "excellent",
    "imageUrl": "/placeholder.svg?height=200&width=200"
  },
  "zone": { "id": "zone-1", "name": "Front Garden" }
}
```

### Field contract

Required by `app/zones/[zoneId]/plants/[plantId]/page.tsx`:

- `plant.id` (`string`)
- `plant.zoneId` (`string`)
- `plant.name` (`string`)
- `plant.humidity` (`number`)
- `plant.health` (union string)
- `plant.imageUrl` (`string | null`)
- `zone.id` (`string`)
- `zone.name` (`string`)

---

## Endpoint: List Plant Sensors (for plant sensor cards + readings list)

**GET** `/api/plants/{plantId}/sensors?includeReadings=true&from=...&to=...`

Returns the soil sensors used by:

- “Soil Humidity Sensors” card grid (each `SensorChart`)
- “Sensor Readings” list
- “Avg Sensor Reading” computed client-side

### Query params (recommended)

- `includeReadings` (`boolean`, default `false`)
- `from` (`string`, ISO 8601, optional)
- `to` (`string`, ISO 8601, optional)
- `limit` (`number`, optional): cap number of readings returned per sensor (e.g. 24)

### Response 200

```json
{
  "sensors": [
    {
      "id": "s-1-1-1",
      "plantId": "plant-1-1",
      "name": "Root Level",
      "humidity": 74,
      "readings": [
        { "timestamp": "2026-01-26T11:00:00.000Z", "value": 73.2 },
        { "timestamp": "2026-01-26T12:00:00.000Z", "value": 74.1 }
      ]
    }
  ]
}
```

### Field contract (per sensor)

Based on `types/index.ts` (with JSON date strings):

- `id` (`string`)
- `plantId` (`string`)
- `name` (`string`)
- `humidity` (`number`) current value displayed as `%`
- `readings` (`Array<{ timestamp: string; value: number }>`), when `includeReadings=true`

---

## Actions: Start/Stop Irrigation

The UI has a zone-level Start/Stop button and a plant-level Start button (when attention required).

### Start irrigation for a zone

**POST** `/api/zones/{zoneId}/irrigation/start`

Body (recommended):

```json
{
  "durationSeconds": 600
}
```

### Stop irrigation for a zone

**POST** `/api/zones/{zoneId}/irrigation/stop`

### Start irrigation for a plant (optional but matches Plant detail UI)

**POST** `/api/plants/{plantId}/irrigation/start`

Body (recommended):

```json
{
  "durationSeconds": 600
}
```

### Action response 200 (recommended)

```json
{
  "status": "accepted",
  "jobId": "job_123",
  "requestedAt": "2026-01-26T12:00:00.000Z"
}
```

---

## Endpoint: Zone Activity Feed (recommended)

The Zone detail page currently shows placeholder “Recent Activity”. For real data:

**GET** `/api/zones/{zoneId}/activity?limit=20`

### Response 200

```json
{
  "events": [
    {
      "id": "evt_1",
      "type": "irrigation.completed",
      "message": "Irrigation completed",
      "occurredAt": "2026-01-26T10:00:00.000Z"
    }
  ]
}
```

### Event fields

- `id` (`string`)
- `type` (`string`)
- `message` (`string`)
- `occurredAt` (`string`, ISO 8601)

---

## Error responses (recommended)

```json
{
  "error": { "code": "NOT_FOUND", "message": "Zone not found" }
}
```

