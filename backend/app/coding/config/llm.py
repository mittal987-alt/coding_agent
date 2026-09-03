from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ProviderType = Literal[
    "openai",
    "anthropic",
    "gemini",
    "mistral",
    "ollama",
    "openrouter",
]
@dataclass(slots=True)
class RetryConfig:
    """
    Retry policy for LLM requests.
    """

    max_retries: int = 3

    initial_delay: float = 1.0

    max_delay: float = 10.0

    exponential_backoff: bool = True

    retry_on_rate_limit: bool = True

    retry_on_timeout: bool = True

@dataclass(slots=True)
class StreamingConfig:
    """
    Streaming configuration.
    """

    enabled: bool = True

    chunk_size: int = 512

    flush_interval: float = 0.1

@dataclass(slots=True)
class ProviderConfig:
    """
    Configuration for a single provider.
    """

    name: ProviderType

    enabled: bool = True

    default_model: str = ""

    temperature: float = 0.2

    top_p: float = 1.0

    max_tokens: int = 4096

    timeout: int = 120

    supports_streaming: bool = True

    supports_tools: bool = True

    supports_vision: bool = False

    supports_embeddings: bool = False

    priority: int = 100

@dataclass(slots=True)
class RouterConfig:
    """
    Router behavior.
    """

    default_provider: ProviderType = "openai"

    fallback_enabled: bool = True

    load_balancing: bool = True

    health_check_interval: int = 300

    latency_weight: float = 0.5

    cost_weight: float = 0.3

    quality_weight: float = 0.2

@dataclass(slots=True)
class CacheConfig:
    """
    LLM cache settings.
    """

    enabled: bool = True

    ttl_seconds: int = 3600

    max_entries: int = 10000

DEFAULT_PROVIDERS: dict[
    ProviderType,
    ProviderConfig,
] = {
    "openai": ProviderConfig(
        name="openai",
        default_model="gpt-5",
        priority=100,
        supports_embeddings=True,
    ),
    "anthropic": ProviderConfig(
        name="anthropic",
        default_model="claude-sonnet-4",
        priority=95,
    ),
    "gemini": ProviderConfig(
        name="gemini",
        default_model="gemini-2.5-pro",
        priority=90,
        supports_vision=True,
        supports_embeddings=True,
    ),
    "mistral": ProviderConfig(
        name="mistral",
        default_model="mistral-small-latest",
        priority=85,
        supports_embeddings=True,
    ),
    "ollama": ProviderConfig(
        name="ollama",
        default_model="qwen2.5-coder:1.5b",
        priority=100,
        supports_embeddings=True,
    ),
    "openrouter": ProviderConfig(
        name="openrouter",
        default_model="openai/gpt-5",
        priority=98,
        supports_vision=True,
        supports_embeddings=True,
    ),
}

@dataclass(slots=True)
class LLMConfig:
    """
    Complete LLM configuration.
    """

    retry: RetryConfig = field(
        default_factory=RetryConfig,
    )

    streaming: StreamingConfig = field(
        default_factory=StreamingConfig,
    )

    router: RouterConfig = field(
        default_factory=RouterConfig,
    )

    cache: CacheConfig = field(
        default_factory=CacheConfig,
    )

    providers: dict[
        ProviderType,
        ProviderConfig,
    ] = field(
        default_factory=dict,
    )



def create_llm_config() -> LLMConfig:
    """
    Create the default LLM configuration.
    """

    config = LLMConfig()

    config.providers = DEFAULT_PROVIDERS.copy()

    return config