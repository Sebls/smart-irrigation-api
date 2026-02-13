# Overview API (Dashboard Home `/`)

This document defines the **backend API responses required to power the Overview route** implemented at `app/page.tsx`.

The Overview page renders:

- `StatsCards` (`features/overview/components/stats-cards.tsx`): derived stats computed from all zones
- `ZoneCard` grid (`features/zones/components/zone-card.tsx`): a preview card for each zone

The frontend currently uses deterministic mocks (`mockZones`), but the API below describes what the real backend must return.

## Conventions

- **Base path**: examples use `/api/...` (adjust to your gateway prefix).
- **Dates**: `Date` values in TypeScript **must be serialized as ISO 8601 strings** in JSON (`string`), e.g. `"2026-01-26T12:00:00.000Z"`.
- **Numbers**: all percentages are `0..100` (integer or float).
- **Optional vs required**: if a field can be unknown, return `null` (preferred) rather than omitting it.

---

## Endpoint: Get Overview Summary

**GET** `/api/overview/summary`

Provides the stats displayed in the four top cards (active zones, total plants, avg soil humidity, avg temperature).

### Response 200 (JSON)

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

`summary`:

- `zonesTotal` (`number`): total count of irrigation zones.
- `zonesActive` (`number`): count of zones where irrigation is active (`isActive=true`).
- `plantsTotal` (`number`): sum of `plantCount` across all zones.
- `avgSoilHumidity` (`number`): average of zone soil humidity percentages (what the UI calls “Avg Soil Humidity”).
- `avgTemperatureC` (`number`): average temperature in °C across zones.

`generatedAt`:

- `generatedAt` (`string`, ISO 8601): server timestamp for the payload (useful for caching/debugging).

### Notes (mapping to frontend)

- These values correspond to what `StatsCards` currently computes from the zones array:
  - `zonesActive/zonesTotal`
  - `plantsTotal`
  - `avgSoilHumidity`
  - `avgTemperatureC`

---

## Endpoint: List Zones for Overview

**GET** `/api/overview/zones`

Returns a list of zones with the **minimum data required** to render each `ZoneCard` on the Overview page.

### Query params

- `limit` (`number`, optional): max zones to return (if omitted, return all).
- `offset` (`number`, optional): pagination offset (default `0`).

### Response 200 (JSON)

```json
{
  "zones": [
    {
      "id": "zone-1",
      "name": "Front Garden",
      "isActive": true,
      "plantCount": 2,
      "avgHumidity": 68,
      "temperature": 24,
      "lastIrrigated": "2026-01-26T10:00:00.000Z"
    }
  ],
  "total": 1
}
```

### Field contract (per zone)

These fields are required by `ZoneCard` and/or `StatsCards`:

- `id` (`string`): used for routing and React keys.
- `name` (`string`): display name.
- `isActive` (`boolean`): determines “Active/Idle” badge.
- `plantCount` (`number`): displayed in the card, and used by summary stats.
- `avgHumidity` (`number`): displayed and used to color the “Soil Humidity” bar.
- `temperature` (`number`): displayed in °C.
- `lastIrrigated` (`string`, ISO 8601): used to show “Last Watered” (frontend computes time-since).

Envelope:

- `zones` (`Array<ZoneOverview>`): zone list.
- `total` (`number`): total zones available (for pagination/UI).

### Notes (mapping to frontend)

- The UI derives “Last Watered” from `lastIrrigated` client-side, so the backend only needs to supply the timestamp.
- If you prefer to avoid client-side time math, you can additionally include:
  - `lastIrrigatedDisplay` (`string`) like `"2h ago"` (optional), but the current UI does not require it.

---

## Error responses (recommended)

Return consistent error envelopes so the UI can show toasts or empty states.

### 4xx/5xx (JSON)

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Failed to load overview data"
  }
}
```

`error.code` (`string`) examples:

- `VALIDATION_ERROR`
- `NOT_FOUND`
- `INTERNAL_ERROR`

---

## Type references

The domain model lives in `types/index.ts`. Note that those types use `Date`, but API payloads must serialize dates as ISO strings:

- `IrrigationZone.lastIrrigated: Date` → JSON `lastIrrigated: string`

The Overview endpoints intentionally return **a subset** of the full zone model to keep payloads small.

