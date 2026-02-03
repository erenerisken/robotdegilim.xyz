"""Context schema models for app-level queue and state tracking."""

from pydantic import BaseModel, Field

from app.core.constants import RequestType


def _in_queue_factory() -> dict[str, bool]:
    """Build default in-queue lookup map for all request types."""
    return {req_type.value: False for req_type in RequestType}


class AppContext(BaseModel):
    """Persistent app context state shared across request handling runs."""

    queue: list[str] = Field(default_factory=list)
    in_queue: dict[str, bool] = Field(default_factory=_in_queue_factory)
    error_count: int = 0
    suspended: bool = False

    def enqueue(self, request_type: RequestType) -> bool:
        """Add a request to queue if it is queueable and not already queued."""
        if request_type == RequestType.SCRAPE:
            return False
        key = request_type.value
        if self.in_queue.get(key, False):
            return False
        self.queue.append(key)
        self.in_queue[key] = True
        return True

    def dequeue(self) -> RequestType | None:
        """Remove and return the next queued request, or None when queue is empty."""
        if not self.queue:
            return None
        next_request = self.queue.pop(0)
        self.in_queue[next_request] = False
        try:
            return RequestType(next_request)
        except ValueError as exc:
            raise ValueError(f"Unknown queued request type: {next_request}") from exc

    def clear_queue(self) -> None:
        """Clear queue and reset in-queue lookup flags."""
        self.queue.clear()
        for key in self.in_queue:
            self.in_queue[key] = False

    def mark_failure(self, max_errors: int) -> bool:
        """Record a failed run and suspend when threshold is reached."""
        self.error_count += 1
        if self.error_count >= max_errors:
            self.error_count = 0
            self.suspended = True
            return True
        return False

    def mark_success(self) -> None:
        """Record a successful run by reducing accumulated error count."""
        if self.error_count > 0:
            self.error_count -= 1

    def suspend(self) -> None:
        """Suspend request processing."""
        self.suspended = True

    def unsuspend(self) -> None:
        """Lift suspension."""
        self.suspended = False

    def reset_failures(self) -> None:
        """Reset error count to zero."""
        self.error_count = 0
