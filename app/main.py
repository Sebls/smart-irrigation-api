from fastapi import FastAPI
from app.api.routers import plants


def create_app() -> FastAPI:
    app = FastAPI(title="smart-irrigation-api")

    app.include_router(plants.router)

    return app


app = create_app()
