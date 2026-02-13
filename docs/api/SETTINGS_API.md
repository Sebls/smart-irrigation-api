# Settings API (`/settings`)

This document defines a **proposed backend API contract** for the Settings view.

Important:

- The UI currently links to `/settings` (see `layouts/dashboard/components/sidebar.tsx` and `layouts/dashboard/components/mobile-nav.tsx`)
- There is **no `app/settings/page.tsx` route implemented yet** in this repo

When you add the Settings page, these endpoints provide a clean contract for fetching and updating **system settings**.

Important:

- Settings are intended to be stored in **backend configuration** (e.g. `.yaml`, a config file, or a config service), **not in the database**.

## Conventions

- **Base path**: examples use `/api/...` (adjust to your gateway prefix).
- **Dates**: serialize to ISO 8601 strings.
- Prefer **PATCH** for partial updates.

---

## Endpoint: Get Settings

**GET** `/api/settings`

### Response 200

```json
{
  "settings": {
    "timezone": "UTC",
    "units": {
      "temperature": "C",
      "volume": "L"
    },
    "thresholds": {
      "soilHumidityOptimalMin": 60,
      "soilHumidityModerateMin": 40
    },
    "refresh": {
      "sensorPollSeconds": 60,
      "waterPollSeconds": 300
    },
  },
  "generatedAt": "2026-01-26T12:00:00.000Z"
}
```

### Field contract

- `settings.timezone` (`string`) IANA timezone, e.g. `"UTC"`, `"America/Bogota"`
- `settings.units.temperature` (`"C" | "F"`)
- `settings.units.volume` (`"L" | "gal"`)
- `settings.thresholds.soilHumidityOptimalMin` (`number`) default maps to UI “Optimal” when `>= 60`
- `settings.thresholds.soilHumidityModerateMin` (`number`) default maps to UI “Moderate” when `>= 40` and `< optimalMin`
- `settings.refresh.sensorPollSeconds` (`number`)
- `settings.refresh.waterPollSeconds` (`number`)

Notes:

- These thresholds match the current hard-coded UI logic used in `app/sensors/page.tsx`:
  - `>= 60` → Optimal
  - `>= 40` → Moderate
  - else → Low

---

## Endpoint: Update Settings

**PATCH** `/api/settings`

Accepts partial updates to the settings document.

### Request body (example)

```json
{
  "timezone": "America/Bogota",
  "thresholds": {
    "soilHumidityOptimalMin": 65
  }
}
```

### Response 200 (recommended)

```json
{
  "settings": {
    "timezone": "America/Bogota",
    "units": { "temperature": "C", "volume": "L" },
    "thresholds": {
      "soilHumidityOptimalMin": 65,
      "soilHumidityModerateMin": 40
    },
    "refresh": { "sensorPollSeconds": 60, "waterPollSeconds": 300 },
  },
  "updatedAt": "2026-01-26T12:05:00.000Z"
}
```

---

## Error responses (recommended)

```json
{
  "error": { "code": "VALIDATION_ERROR", "message": "Invalid settings payload" }
}
```

