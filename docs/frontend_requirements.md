# Frontend viewing requirements (based on data currently saved)

1. Show a **Devices list** view.
2. In the Devices list, display (at minimum) `device.id`, `device.name`, `device.description`, `device.is_active`, `device.is_online`, `device.last_seen_at`, `device.uptime`, `device.created_at`, `device.updated_at`.
3. In the Devices list and Device detail, display the device **hardware identifier** (`device.hardware_id`, e.g. MAC/serial) when available.
4. Provide a **Device detail** page per `device.id`.
5. In Device detail, show a **liveness/health panel** including: online/offline, last seen timestamp, uptime, and a simple “health” indicator derived from recent logs (e.g., recent error/critical count).
6. In Device detail, show **all related sensor provisioning/telemetry identity info** you have (sensor UUIDs, local names if known, and the mapping used by telemetry such as `TelemetryRequest.readings[].sensorId`).
7. Provide a **Zones list** view.
8. In the Zones list, display `zone.id`, `zone.name`, `zone.is_active`, `zone.created_at`, `zone.updated_at`, `zone.deleted_at`.
9. Provide a **Zone detail** page per `zone.id`.
10. In Zone detail, show **all plants** in the zone with: `plant.id`, `plant.name`, `plant.zone_id`, `plant.image_url`, `plant.health`.
11. In Zone detail, show **all sensors** attached to the zone with: `sensor.id`, `sensor.name`, `sensor.type`, `sensor.unit`, `sensor.is_active`, `sensor.zone_id`, `sensor.plant_id`, `sensor.created_at`, `sensor.updated_at`, `sensor.deleted_at`.
12. Provide a **Sensor detail** view per `sensor.id`.
13. In Sensor detail, show a **latest reading** card (most recent `sensor_readings` record) including: `reading.id`, `reading.sensor_id`, `reading.recorded_at`, `reading.value`.
14. In Sensor detail, show a **historical readings chart/table** for `sensor_readings` with filtering by time range (e.g., last hour/day/week) and pagination/limits.
15. Provide a **Device images / cameras** section in Device detail.
16. In Device images, group images **by `device_images.type`** (camera/type), and for each type show the latest image preview plus: `device_image.id`, `device_image.device_id`, `device_image.type`, `device_image.image_url`, `device_image.captured_at`, `device_image.plant_id`, `device_image.zone_id`.
17. In Device images, show any available **image metadata** (stored as `device_images.metadata_json`) in a readable JSON panel.
18. Provide a **Device logs** section in Device detail showing a time-ordered list of `device_logs`.
19. In Device logs, display: `device_log.id`, `device_log.device_id`, `device_log.level`, `device_log.message`, `device_log.recorded_at` (and allow filtering by level + time range).
20. Provide an **Irrigation jobs** view (global list + per Zone + per Plant) showing: `irrigation_jobs.id`, `scope`, `zone_id`, `plant_id`, `action`, `duration_seconds`, `status`, `requested_at`, `started_at`, `ended_at`, `error_message`.
21. Provide an **Activity feed** view (global + filtered by zone/plant/sensor) showing: `activity_events.id`, `type`, `message`, `zone_id`, `plant_id`, `sensor_id`, `occurred_at`.
22. Everywhere an entity is displayed (device/zone/plant/sensor/reading/job/event/log/image), include a way to **copy IDs** (UUIDs) and key identifiers (e.g., `hardware_id`, sensor name/type/unit).
23. Support **empty states** for devices with no images yet, no logs yet, and sensors with no readings yet (telemetry only persists readings for known/provisioned sensors).

