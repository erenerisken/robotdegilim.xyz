from app.core.constants import RequestType
from app.api.schemas import ErrorResponse, RootResponse, ScrapeResponse
from app.storage.s3 import acquire_lock, release_lock

def handle_request(request_type: RequestType):
    try:
        req_type = RequestType(request_type)
    except ValueError:
        return ErrorResponse(message="Invalid request type"), 400

    if not acquire_lock():
        return ErrorResponse(message="Request handling failed, system is busy"), 503

    try:
        if req_type == RequestType.ROOT:
            return RootResponse(), 200

        if req_type == RequestType.SCRAPE:
            return ScrapeResponse(status="Scraping started", data={"sample_key": "sample_value"}), 200

        return ErrorResponse(message="Unknown request type"), 400
    finally:
        if not release_lock():
            # log it
            pass
