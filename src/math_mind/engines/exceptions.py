class GradingEngineError(Exception):
    """Base exception for all grading engine errors."""
    pass

class ConfigurationError(GradingEngineError):
    """Raised when API key or model name is invalid."""
    pass

class RateLimitExceededError(GradingEngineError):
    """Raised when the API rate limit is exceeded after retries."""
    pass