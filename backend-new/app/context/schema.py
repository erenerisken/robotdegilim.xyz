from enum import Enum
from pydantic import BaseModel, Field

from app.core.constants import RequestType

S3_CONTEXT_KEY = "context.json" 

def _in_queue_factory():
    return {req_type.value: False for req_type in RequestType}

class AppContext(BaseModel):
    queue: list[str] = Field(default_factory=list)
    in_queue: dict[str, bool] = Field(default_factory=_in_queue_factory)
    error_count: int = 0
    suspended: bool = False

class ContextUpdateType(str, Enum):
    NULL = "null"
    ENQUEUE_REQUEST = "enqueue_request"
    INCREMENT_ERROR_COUNT = "increment_error_count"

class ContextUpdate(BaseModel):
    update_type: ContextUpdateType = ContextUpdateType.NULL
    request_type: RequestType | None = None