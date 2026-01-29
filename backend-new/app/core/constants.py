from enum import Enum
from pydantic import BaseModel


class RequestType(str, Enum):
    SCRAPE = "scrape"
    ROOT = "root"


class AppContext(BaseModel):
    hello: str = "world"
