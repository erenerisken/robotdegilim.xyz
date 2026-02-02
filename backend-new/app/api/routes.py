from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.constants import RequestType
from app.services.request_handler import handle_request

router = APIRouter()


@router.get("/")
def root():
    model, status_code = handle_request(RequestType.ROOT.value)
    return JSONResponse(content=model.model_dump(), status_code=status_code)

@router.get("/run-scrape")
def run_scrape():
    model, status_code = handle_request(RequestType.SCRAPE.value)
    return JSONResponse(content=model.model_dump(), status_code=status_code)
