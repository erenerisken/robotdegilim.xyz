"""Context schema models for app-level queue and state tracking."""

from pydantic import BaseModel, Field

from app.core.constants import RequestType

S3_CONTEXT_KEY = "context.json"


def _in_queue_factory() -> dict[str, bool]:
    """Build default in-queue lookup map for all request types."""
    return {req_type.value: False for req_type in RequestType}


class AppContext(BaseModel):
    """Persistent app context state shared across request handling runs."""

    queue: list[str] = Field(default_factory=list)
    in_queue: dict[str, bool] = Field(default_factory=_in_queue_factory)
    error_count: int = 0
    suspended: bool = False
