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