"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

from fastapi import FastAPI

from app.api.routes import router
from app.core.constants import LOGGER_APP
from app.core.errors import AppError
from app.core.logging import log_item
from app.core.logging import setup_logging
from app.core.settings import get_settings
from app.services.status_service import sync_status_from_locks

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Run startup and shutdown lifecycle hooks for the FastAPI app."""
    setup_logging()
    try:
        sync_status_from_locks()
    except Exception as e:
        log_item(
            LOGGER_APP,
            logging.WARNING,
            e if isinstance(e, AppError) else AppError(
                "Failed to publish initial status on startup.",
                "STATUS_STARTUP_SYNC_FAILED",
                cause=e,
            ),
        )
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
app.include_router(router)
