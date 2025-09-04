from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes.arshin import router as arshin_router

logger = setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    app.include_router(arshin_router)
    return app

app = create_app()
