from app.config import API_VERSION
from fastapi import FastAPI, APIRouter
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

    api_router = APIRouter(prefix=f"/api/{API_VERSION}")

    api_router.include_router(plants.router)
    api_router.include_router(zones.router)
    api_router.include_router(sensors.router)
    api_router.include_router(sensor_readings.router)
    api_router.include_router(activity.router)
    api_router.include_router(water.router)
    api_router.include_router(irrigation.router)

    app.include_router(api_router)

    return app


app = create_app()
