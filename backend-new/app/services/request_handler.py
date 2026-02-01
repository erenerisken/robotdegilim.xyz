from app.core.constants import RequestType
from app.api.schemas import ErrorResponse, RootResponse, ScrapeResponse
from app.storage.s3 import acquire_lock, release_lock
from app.pipelines.scrape import run_scrape
from app.core.errors import AppError
from app.core.logging import get_logger

_allow_context_modification = False


def handle_request(request_type: RequestType):
    global _allow_context_modification
    try:
        req_type = RequestType(request_type)
    except ValueError:
        return ErrorResponse(message="Invalid request type"), 400

    if req_type == RequestType.ROOT:
        return RootResponse(), 200

    if not acquire_lock():
        if _allow_context_modification:
            # queue logic will be added later
            return ErrorResponse(message="Request queued"), 202
        return ErrorResponse(message="Request handling failed, system is busy"), 503

    _allow_context_modification = True
    # in here fetch and look at the ctx to see what to run
    try:
        if req_type == RequestType.SCRAPE:
            model, status_code = run_scrape()
            return model, status_code
    finally:
        _allow_context_modification = False
        # in here ctx updates
        if not release_lock():
            logger = get_logger("app")
            err = AppError(
                message="Failed to release lock after request handling",
                code="LOCK_RELEASE_FAILED",
            )
            logger.warning(err.to_log())

    return ErrorResponse(message="Unknown request type"), 400
