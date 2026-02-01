from pydantic import BaseModel, Field

from app.core.constants import RequestType

def _in_queue_factory():
    return {req_type.value: False for req_type in RequestType}

class AppContext(BaseModel):
    queue: list[str] = Field(default_factory=list)
    in_queue: dict[str, bool] = Field(default_factory=_in_queue_factory)
    error_count: int = 0
    suspended: bool = False

    def enqueue(self, req_type: RequestType) -> bool:
        key = req_type.value
        if self.in_queue.get(key):
            return False
        self.queue.append(key)
        self.in_queue[key] = True
        return True

    def dequeue(self) -> str | None:
        if not self.queue:
            return None
        key = self.queue.pop(0)
        self.in_queue[key] = False
        return key

    def clear_queue(self) -> None:
        self.queue.clear()
        self.in_queue=_in_queue_factory()
    
    def increment_error_count(self) -> None:
        self.error_count += 1
    
    def reset_error_count(self) -> None:
        self.error_count = 0

    def suspend(self) -> None:
        self.suspended = True
    
    def resume(self) -> None:
        self.suspended = False
