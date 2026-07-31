# LLM Exceptions
"""
LLM exception hierarchy.

These exceptions provide a consistent way to handle failures across
all LLM providers while allowing provider-specific errors to be
mapped into common application exceptions.
"""


class LLMError(Exception):
    """
    Base exception for all LLM-related errors.
    """

    pass


# ---------------------------------------------------------------------
# Provider Errors
# ---------------------------------------------------------------------


class ProviderError(LLMError):
    """
    Generic provider error.
    """

    pass


class ProviderNotFoundError(ProviderError):
    """
    Requested provider is not registered.
    """

    pass


class ProviderConfigurationError(ProviderError):
    """
    Provider configuration is invalid.
    """

    pass


class ProviderAuthenticationError(ProviderError):
    """
    Authentication failed.
    """

    pass


class ProviderConnectionError(ProviderError):
    """
    Could not connect to provider.
    """

    pass


class ProviderTimeoutError(ProviderError):
    """
    Request timed out.
    """

    pass


class ProviderUnavailableError(ProviderError):
    """
    Provider is temporarily unavailable.
    """

    pass


# ---------------------------------------------------------------------
# Model Errors
# ---------------------------------------------------------------------


class ModelError(LLMError):
    """
    Base model exception.
    """

    pass


class ModelNotFoundError(ModelError):
    """
    Requested model does not exist.
    """

    pass


class UnsupportedModelError(ModelError):
    """
    Model is unsupported by provider.
    """

    pass


class ModelOverloadedError(ModelError):
    """
    Model is overloaded.
    """

    pass


# ---------------------------------------------------------------------
# Request Errors
# ---------------------------------------------------------------------


class RequestError(LLMError):
    """
    Invalid request.
    """

    pass


class InvalidPromptError(RequestError):
    """
    Prompt validation failed.
    """

    pass


class PromptTooLargeError(RequestError):
    """
    Prompt exceeds model context.
    """

    pass


class InvalidParameterError(RequestError):
    """
    Invalid request parameters.
    """

    pass


class ContextWindowExceededError(RequestError):
    """
    Context window exceeded.
    """

    pass


# ---------------------------------------------------------------------
# Response Errors
# ---------------------------------------------------------------------


class ResponseError(LLMError):
    """
    Invalid model response.
    """

    pass


class EmptyResponseError(ResponseError):
    """
    Provider returned an empty response.
    """

    pass


class InvalidResponseFormatError(ResponseError):
    """
    Response format is invalid.
    """

    pass


class JSONParsingError(ResponseError):
    """
    Failed to parse structured JSON.
    """

    pass


class ToolCallError(ResponseError):
    """
    Tool/function call failed.
    """

    pass


class StreamingError(ResponseError):
    """
    Streaming response failed.
    """

    pass


# ---------------------------------------------------------------------
# Routing Errors
# ---------------------------------------------------------------------


class RoutingError(LLMError):
    """
    Model routing failed.
    """

    pass


class NoAvailableProviderError(RoutingError):
    """
    No provider is currently available.
    """

    pass


class FallbackError(RoutingError):
    """
    All fallback providers failed.
    """

    pass


# ---------------------------------------------------------------------
# Cache Errors
# ---------------------------------------------------------------------


class CacheError(LLMError):
    """
    Cache operation failed.
    """

    pass


class CacheMissError(CacheError):
    """
    Requested cache entry not found.
    """

    pass


# ---------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------


class RateLimitError(LLMError):
    """
    Rate limit exceeded.
    """

    pass


class QuotaExceededError(RateLimitError):
    """
    Provider quota exhausted.
    """

    pass


# ---------------------------------------------------------------------
# Middleware Errors
# ---------------------------------------------------------------------


class MiddlewareError(LLMError):
    """
    Middleware execution failed.
    """

    pass


class GuardrailViolationError(MiddlewareError):
    """
    Guardrail validation failed.
    """

    pass


class RetryLimitExceededError(MiddlewareError):
    """
    Retry limit exceeded.
    """

    pass