import inspect
from typing import Optional, Dict, Any


class RecoverException(Exception):
    """Exception used to indicate that the system should safely return to idle without making state changes."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        # Create a copy to avoid side effects
        self.details = dict(details) if details else {}

        # Automatically add the caller function name if not provided
        if 'function' not in self.details:
            caller_function = inspect.stack()[1].function
            self.details['function'] = caller_function

        super().__init__(message)

    def __str__(self) -> str:
        base_message = self.args[0]
        if self.details:
            return f"{base_message} | Details: {self._format_details()}"
        return base_message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.args[0]!r}, details={self.details!r})"

    def _format_details(self) -> str:
        """Formats the details dictionary, nicely indenting multiline error strings."""
        formatted = "{"
        error_str = None

        for key, value in self.details.items():
            if key == "error":
                error_str = str(value).replace('\n', '\n\t')
                continue
            formatted += f"'{key}': '{value}', "

        if error_str is not None:
            formatted += f"'error': \n\t'{error_str}'"

        return formatted.rstrip(", ") + "}"
