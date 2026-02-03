"""Request orchestration service for top-level API request types."""

from dataclasses import dataclass
import logging

from app.api.schemas import ResponseModel, RootResponse
from app.context.service import (
    enqueue_request,
    load_context_state,
    publish_context_state,
    record_failure,
    record_success,
    resolve_request,
)
from app.core.constants import RequestType, LOGGER_ERROR
from app.core.errors import AppError
from app.core.logging import log_item
from app.pipelines.scrape import run_scrape
from app.pipelines.musts import run_musts
from app.storage.s3 import acquire_lock, release_lock

_allow_context_modification: bool = False

INCREMENT_ERROR_STATUS_CODES = (500,)
DECREMENT_ERROR_STATUS_CODES = (200,)


@dataclass
class ErrorFlags:
    """Internal error counter flags used during request orchestration."""

    increment: bool = False
    decrement: bool = False
    suspended: bool = False


def _finalize_response(response_model: ResponseModel, status_code: int, *, flags: ErrorFlags) -> tuple[ResponseModel, int]:
    """Set internal error flags from status code and return response tuple."""
    if status_code in DECREMENT_ERROR_STATUS_CODES:
        flags.decrement = True
    elif status_code in INCREMENT_ERROR_STATUS_CODES:
        flags.increment = True
    return response_model, status_code

def _apply_public_extra(model: ResponseModel, from_queue: bool) -> None:
    """Attach only public extra metadata to response model."""
    if not from_queue:
        return
    if model.extra is None:
        model.extra = {"from_queue": True}
        return
    model.extra["from_queue"] = True

def handle_request(request_type: RequestType) -> tuple[RootResponse | ResponseModel, int]:
    """Handle a request type, coordinating lock, queue, execution, and persistence."""
    global _allow_context_modification

    if request_type == RequestType.ROOT:
        return RootResponse(), 200

    lock_owned = False
    error_flags = ErrorFlags()
    try:
        if not acquire_lock():
            if _allow_context_modification:
                if enqueue_request(request_type):
                    return _finalize_response(ResponseModel(request_type=request_type, status="REQUEST_QUEUED", message="Request queued"), 202, flags=error_flags)
                else:
                    return _finalize_response(ResponseModel(request_type=request_type, status="QUEUE_FAILED", message="Either queue is not supported for this request type or the request is already in the queue"), 503, flags=error_flags)
            return _finalize_response(ResponseModel(request_type=request_type, status="BUSY", message="System is busy processing another request"), 503, flags=error_flags)

        lock_owned = True
        _allow_context_modification = True
        load_context_state()
        from_queue, next_req = resolve_request(request_type)
        model: ResponseModel | None = None
        status_code: int | None = None

        if next_req == RequestType.SCRAPE:
            model, status_code = run_scrape()
        elif next_req == RequestType.MUSTS:
            model, status_code = run_musts()
        # Request types can be extended here with additional elif blocks

        if model is None or status_code is None:
            return _finalize_response(ResponseModel(request_type=request_type, status="UNSUPPORTED", message="Request type is not supported"), 501, flags=error_flags)

        _apply_public_extra(model, from_queue)
    
        return _finalize_response(model, status_code, flags=error_flags)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to handle request",
            code="REQUEST_HANDLING_FAILED",
            cause=e,
        )
        if err.code == "CONTEXT_SUSPENDED":
            error_flags.suspended = True
            return _finalize_response(ResponseModel(request_type=request_type, status="CONTEXT_SUSPENDED", message="AppContext is suspended due to excessive errors"), 503, flags=error_flags)
        log_item(LOGGER_ERROR, logging.ERROR, err)
        return _finalize_response(ResponseModel(request_type=request_type, status="ERROR", message=err.message), 500, flags=error_flags)
    finally:
        _allow_context_modification = False
        if lock_owned:
            try:
                if not error_flags.suspended:
                    if error_flags.increment:
                        record_failure()
                    if error_flags.decrement:
                        record_success()
                publish_context_state()
            except Exception as e:
                err = e if isinstance(e, AppError) else AppError(
                    message="Failed to publish context after request handling",
                    code="CONTEXT_PUBLISH_FAILED",
                    cause=e,
                )
                log_item(LOGGER_ERROR, logging.ERROR, err)
            try:
                if not release_lock():
                    raise AppError(
                        message="Failed to release lock after request handling",
                        code="LOCK_RELEASE_FAILED",
                    )
            except Exception as e:
                err = e if isinstance(e, AppError) else AppError(
                    message="Failed to release lock after request handling",
                    code="LOCK_RELEASE_FAILED",
                    cause=e,
                )
                log_item(LOGGER_ERROR, logging.ERROR, err)
