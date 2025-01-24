class RecoverException(Exception):
    """System needs to go back idle status without change."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details

    def __str__(self):
        base_message = super().__str__()
        if self.details:
            return f"{base_message} | Details: {self.details}"
        return base_message
