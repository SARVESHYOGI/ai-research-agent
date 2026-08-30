import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import research
from app.config.settings import get_settings
from shared.redis import setup_redis

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("research-service startup", app=settings.app_name, version=settings.version)
        yield
        logger.info("research-service shutdown")

    app = FastAPI(
        title=settings.app_name,
        description="Search, fetch, extraction and verification pipeline.",
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    setup_redis(app=app, caching=True, rate_limiting=True)

    app.include_router(research.router)

    @app.get("/")
    def read_root():
        return {"service": settings.app_name}

    return app


app = create_app()
