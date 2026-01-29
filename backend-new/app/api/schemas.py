from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class RootResponse(BaseModel):
    service: str = "robotdegilim-backend"


class ScrapeResponse(BaseModel):
    status: str
    data: dict
