class AIProviderError(Exception):
    """Base exception for errors coming from the AI provider."""


class AIProviderQuotaError(AIProviderError):
    """Raised when the AI provider quota or billing limit is exceeded."""


class AIProviderConfigurationError(AIProviderError):
    """Raised when the AI provider is not configured correctly."""