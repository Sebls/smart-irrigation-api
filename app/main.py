from fastapi import FastAPI
from app.api.routers import (
    plants,
    zones,
    sensors,
    sensor_readings,
    activity,
    water,
    irrigation,
)


def create_app() -> FastAPI:
    app = FastAPI(title="smart-irrigation-api")

    app.include_router(plants.router)
    app.include_router(zones.router)
    app.include_router(sensors.router)
    app.include_router(sensor_readings.router)
    app.include_router(activity.router)
    app.include_router(water.router)
    app.include_router(irrigation.router)

    return app


app = create_app()
