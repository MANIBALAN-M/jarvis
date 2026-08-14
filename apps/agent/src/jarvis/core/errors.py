"""User-facing Error Sanitization Module."""



def sanitize_user_error(exc: Exception) -> str:
    """Format exceptions into clean, user-friendly messages without exposing raw stack traces."""
    if isinstance(exc, FileNotFoundError):
        return f"File or directory not found: {exc.filename or 'target path'}"
    if isinstance(exc, PermissionError):
        return f"Access denied: insufficient system permissions for {exc.filename or 'target operation'}"
    if isinstance(exc, TimeoutError):
        return "Task operation timed out before completion."
    if isinstance(exc, OSError):
        return f"System error occurred: {exc.strerror or 'operating system call failed'}"
    
    # Generic high-level fallback
    exc_type = type(exc).__name__
    return f"Execution error ({exc_type}): Unable to complete operation."
