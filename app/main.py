from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes.arshin import router as arshin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.methodologies import router as methodologies_router
from app.api.routes.owners import router as owners_router
from app.api.routes.protocols import router as protocols_router
from app.api.routes.registry import router as registry_router
from app.api.routes.system import router as system_router
from app.api.routes.users import router as users_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.seed import seed_from_config

logger = setup_logging()


def _register_frontend_routes(app: FastAPI, frontend_dist_path: Path) -> None:
    index_path = frontend_dist_path / "index.html"
    if not index_path.exists():
        return

    @app.get("/", include_in_schema=False)
    async def frontend_index() -> FileResponse:
        return FileResponse(index_path)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def frontend_spa(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        requested_path = (frontend_dist_path / full_path).resolve()
        if _is_child_path(requested_path, frontend_dist_path) and requested_path.is_file():
            return FileResponse(requested_path)
        return FileResponse(index_path)


def _is_child_path(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await seed_from_config()
    except Exception as exc:  # pragma: no cover - logged for observability
        logger.exception("Database seeding failed: {}", exc)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    if settings.backend_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.backend_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(auth_router)
    app.include_router(arshin_router)
    app.include_router(protocols_router)
    app.include_router(methodologies_router)
    app.include_router(owners_router)
    app.include_router(registry_router)
    app.include_router(system_router)
    app.include_router(users_router)

    frontend_dist_path = settings.frontend_dist_path
    if frontend_dist_path.exists():
        _register_frontend_routes(app, frontend_dist_path)
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
