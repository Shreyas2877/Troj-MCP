"""Custom exceptions for Macro-Man MCP Server."""


class MacroManError(Exception):
    """Base exception for Macro-Man MCP Server."""
    
    def __init__(self, message: str, error_code: str = "GENERIC_ERROR") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(MacroManError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None) -> None:
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(MacroManError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(MacroManError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Authorization failed") -> None:
        super().__init__(message, "AUTHORIZATION_ERROR")


class ServiceError(MacroManError):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str, service: str = None) -> None:
        self.service = service
        super().__init__(message, "SERVICE_ERROR")


class ConfigurationError(MacroManError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, "CONFIGURATION_ERROR")
