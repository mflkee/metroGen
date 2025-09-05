from fastapi import FastAPI

from app.api.routes.arshin import router as arshin_router
from app.api.routes.protocols import router as protocols_router
from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    app.include_router(arshin_router)
    app.include_router(protocols_router)
    return app


app = create_app()
