from fastapi import FastAPI

from app.api.routers import items


def create_app() -> FastAPI:
    app = FastAPI(title="smart-irrigation-api")

    app.include_router(items.router)

    return app


app = create_app()

