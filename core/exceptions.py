class USAException(Exception):
    """Base exception for the University Study Assistant app."""
    pass

class ConfigurationError(USAException):
    """Raised when the application is misconfigured (e.g., missing API key)."""
    pass

class DocumentProcessingError(USAException):
    """Raised when a document fails to be parsed or chunked."""
    pass

class RetrievalError(USAException):
    """Raised when the retrieval pipeline fails."""
    pass

class LLMError(USAException):
    """Raised when the LLM service fails or returns an invalid response."""
    pass

class ValidationError(USAException):
    """Raised when structured output validation fails."""
    pass

class DatabaseError(USAException):
    """Raised when a database operation fails."""
    pass
