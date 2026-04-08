from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.routes.arshin import router as arshin_router
from app.api.routes.methodologies import router as methodologies_router
from app.api.routes.owners import router as owners_router
from app.api.routes.protocols import router as protocols_router
from app.api.routes.registry import router as registry_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.seed import seed_from_config

logger = setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await seed_from_config()
    except Exception as exc:  # pragma: no cover - logged for observability
        logger.exception("Database seeding failed: {}", exc)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.include_router(arshin_router)
    app.include_router(protocols_router)
    app.include_router(methodologies_router)
    app.include_router(owners_router)
    app.include_router(registry_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.API_LOG_LEVEL,
    )


if __name__ == "__main__":  # pragma: no cover - manual invocation helper
    run()
