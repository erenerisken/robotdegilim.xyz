"""Application-specific error types."""
class AppError(Exception):
    """Minimal application error used only for typing/catching."""
    
    pass


class StatusError(AppError):
    """Marker subclass of AppError for recoverable failures."""

    pass

class NetworkError(AppError):
    """Marker subclass of AppError for network-related failures."""
    pass

class S3Error(NetworkError):
    """Marker subclass of NetworkError for S3 publishing failures."""
    pass

class AbortMustsError(AppError):
    """Marker subclass of AppError to abort musts fetching."""
    pass

class AbortScrapingError(AppError):
    """Marker subclass of AppError to abort scraping."""
    pass

class AbortNteError(AppError):
    """Marker subclass of AppError to abort NTE processing."""
    pass

class IOError(AppError):
    """Marker subclass of AppError for I/O-related failures."""
    pass