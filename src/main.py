import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router
from src.core.constants import APP_NAME, APP_VERSION
from src.core.logger import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
    app.include_router(router)
    return app

app = create_app()