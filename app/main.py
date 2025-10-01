from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.arshin import router as arshin_router
from app.api.routes.protocols import router as protocols_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.seed import seed_from_config

logger = setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await seed_from_config()
    except Exception as exc:  # pragma: no cover - logged for observability
        logger.exception("Database seeding failed: %s", exc)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.include_router(arshin_router)
    app.include_router(protocols_router)
    return app


app = create_app()
