from enum import Enum
from pydantic import BaseModel

class RequestType(str, Enum):
    SCRAPE = "scrape"
    ROOT = "root"

class ResponseType(str, Enum):
    ERROR = "error"
    ROOT = "root"
    SCRAPE = "scrape"

class AppContext(BaseModel):
    hello: str = "world"