"""API route definitions for the backend service."""

from typing import Annotated

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.api.schemas import AdminRequest
from app.core.errors import AppError
from app.core.constants import RequestType
from app.services.admin_auth import verify_admin_secret
from app.services.admin_handler import handle_admin_action
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


@router.get("/run-musts")
def run_musts() -> Response:
    """Trigger the musts processing workflow and return execution status."""
    model, status_code = handle_request(RequestType.MUSTS)
    return JSONResponse(content=model.model_dump(), status_code=status_code)


@router.post("/admin")
def run_admin_action(
    body: AdminRequest,
    x_admin_secret: Annotated[str | None, Header(alias="X-Admin-Secret")] = None,
) -> Response:
    """Execute admin actions (lock/context/settings) behind admin-secret auth."""
    try:
        verify_admin_secret(x_admin_secret)
    except AppError as err:
        if err.code == "ADMIN_SECRET_NOT_CONFIGURED":
            return JSONResponse(
                content={
                    "action": body.action.value,
                    "status": "FAILED",
                    "message": err.message,
                    "data": None,
                },
                status_code=503,
            )
        return JSONResponse(
            content={
                "action": body.action.value,
                "status": "FAILED",
                "message": err.message,
                "data": None,
            },
            status_code=401,
        )

    model, status_code = handle_admin_action(body.action, body.payload)
    return JSONResponse(content=model.model_dump(), status_code=status_code)
