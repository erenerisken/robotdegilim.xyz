import logging

from app.core.constants import RequestType
from app.api.schemas import ResponseModel, RootResponse
from app.storage.s3 import acquire_lock, release_lock
from app.pipelines.scrape import run_scrape
from app.core.errors import AppError
from app.core.logging import log_item
from app.context.service import load_context, queue_request, get_next_request, publish_context

_allow_context_modification = False


def handle_request(request_type: RequestType):
    global _allow_context_modification

    if request_type == RequestType.ROOT:
        return RootResponse(), 200
    
    try:
        if not acquire_lock():
            if _allow_context_modification:
                if queue_request(request_type):
                    return ResponseModel(request_type=request_type,status="REQUEST_QUEUED",message="Request queued"), 202
                else:
                    return ResponseModel(request_type=request_type,status="QUEUE_FAILED",message="Either queue is not supported for this request type or the request is already in the queue"), 503
            return ResponseModel(request_type=request_type,status="BUSY",message="System is busy processing another request"), 503

        _allow_context_modification = True
        load_context()
        from_queue, next_req = get_next_request(request_type)
        model = None
        status_code = None
        
        if next_req == RequestType.SCRAPE:
            model, status_code = run_scrape()
        # Request types can be extended here with additional elif blocks

        if from_queue:
            if not model.extra:
                model.extra = {"from_queue": True}
            else:
                model.extra["from_queue"] = True

        return model, status_code
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to handle request",
            code="REQUEST_HANDLING_FAILED",
            cause=e,
        )
        log_item("error",logging.ERROR, err)
        return ResponseModel(request_type=request_type,status="ERROR",message=err.message), 500
    finally:
        _allow_context_modification = False
        publish_context()
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
            log_item("error",logging.ERROR, err)
