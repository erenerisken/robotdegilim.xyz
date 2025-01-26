import inspect

class RecoverException(Exception):
    """System needs to go back to idle status without change."""

    def __init__(self, message: str, details: dict = None):
        # Add function name only if it doesn't already exist in details
        if details is None:
            details = {}
        if 'function' not in details:
            caller_function = inspect.stack()[1].function
            details['function'] = caller_function  # Add the function name
        super().__init__(message)
        self.details = details

    def __str__(self):
        return f"{self.args[0]} | Details:\n\t {self.details}" if self.details else self.args[0]
