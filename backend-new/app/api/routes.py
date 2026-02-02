"""API route definitions for the backend service."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.core.constants import RequestType
from app.services.request_handler import handle_request

router = APIRouter()


@router.get("/")
def root() -> Response:
    """Return basic service metadata and available endpoints."""
    model, status_code = handle_request(RequestType.ROOT)
    return JSONResponse(content=model.model_dump(), status_code=status_code)


@router.get("/run-scrape")
def run_scrape() -> Response:
    """Trigger the scrape workflow and return execution status."""
    model, status_code = handle_request(RequestType.SCRAPE)
    return JSONResponse(content=model.model_dump(), status_code=status_code)
