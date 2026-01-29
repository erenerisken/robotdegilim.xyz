from app.core.constants import RequestType
from app.api.schemas import ErrorResponse, RootResponse, ScrapeResponse


def handle_request(request_type: RequestType):
    try:
        req_type = RequestType(request_type)
    except ValueError:
        return ErrorResponse(message="Invalid request type"), 400

    if req_type == RequestType.ROOT:
        return RootResponse(), 200

    if req_type == RequestType.SCRAPE:
        return ScrapeResponse(status="Scraping started", data={"sample_key": "sample_value"}), 200

    return ErrorResponse(message="Unknown request type"), 400
