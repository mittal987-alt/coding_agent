from __future__ import annotations

import logging

from app.bootstrap.container import ApplicationContainer, ServiceContainer
from app.coding.config.settings import Settings
from app.llm.cache import LLMCache
from app.llm.manager import LLMManager
from app.llm.prompts import PromptBuilder, PromptRegistry
from app.llm.registry import LLMRegistry
from app.llm.router import LLMRouter
from app.llm.tokenizer import Tokenizer, ModelInfo
from app.llm.providers import (
    AnthropicProvider,
    GeminiProvider,
    MistralProvider,
    OllamaProvider,
    OpenAIProvider,
    OpenRouterProvider,
)

logger = logging.getLogger(__name__)


# ================================================================
# initialize_providers — used by startup.py with ApplicationContainer
# ================================================================

def initialize_providers(container: ApplicationContainer) -> None:
    """
    Initialize LLM Providers based on available config and register
    them into the ApplicationContainer.
    """

    if container.settings.OPENAI_API_KEY:
        try:
            openai_provider = OpenAIProvider(
                api_key=container.settings.OPENAI_API_KEY,
                model="gpt-4o",
            )
            container.llm_registry.register(openai_provider)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAIProvider: {e}")

    if container.settings.ANTHROPIC_API_KEY:
        try:
            anthropic_provider = AnthropicProvider(
                api_key=container.settings.ANTHROPIC_API_KEY,
            )
            container.llm_registry.register(anthropic_provider)
        except Exception as e:
            logger.error(f"Failed to initialize AnthropicProvider: {e}")

    if container.settings.GEMINI_API_KEY:
        try:
            gemini_provider = GeminiProvider(
                api_key=container.settings.GEMINI_API_KEY,
            )
            container.llm_registry.register(gemini_provider)
        except Exception as e:
            logger.error(f"Failed to initialize GeminiProvider: {e}")

    if container.settings.MISTRAL_API_KEY:
        try:
            mistral_provider = MistralProvider(
                api_key=container.settings.MISTRAL_API_KEY,
            )
            container.llm_registry.register(mistral_provider)
        except Exception as e:
            logger.error(f"Failed to initialize MistralProvider: {e}")

    if getattr(container.settings, "OLLAMA_HOST", None):
        try:
            ollama_provider = OllamaProvider(
                model=getattr(container.settings, "DEFAULT_LLM", "llama3"),
                base_url=container.settings.OLLAMA_HOST,
            )
            container.llm_registry.register(ollama_provider)
        except Exception as e:
            logger.error(f"Failed to initialize OllamaProvider: {e}")

    # Set default provider
    default_llm = getattr(container.settings, "DEFAULT_LLM", "")
    if default_llm and default_llm in container.llm_registry.providers():
        container.llm_registry.set_default(default_llm)

    # Setup LLM Manager
    default_model_info = ModelInfo(
        name=default_llm or "gpt-4o",
        context_window=128000,
        max_output_tokens=4096,
    )
    tokenizer = Tokenizer(model=default_model_info)

    container.llm_manager = LLMManager(
        registry=container.llm_registry,
        router=container.llm_router,
        tokenizer=tokenizer,
        prompt_builder=container.prompt_builder,
    )


# ================================================================
# register_services — used by bootstrap_application with ServiceContainer
# ================================================================

def register_services(
    container: ServiceContainer,
) -> None:
    """
    Register every application service.
    """

    register_settings(container)
    register_llm(container)
    register_memory(container)
    register_workspace(container)
    register_tools(container)
    register_agents(container)


def register_settings(
    container: ServiceContainer,
) -> None:
    settings = Settings()
    container.register("settings", settings)


def register_llm(
    container: ServiceContainer,
) -> None:
    settings: Settings = container.resolve("settings")

    registry = LLMRegistry()
    router = LLMRouter(registry=registry)
    cache = LLMCache()
    prompt_registry = PromptRegistry()
    prompts = PromptBuilder(registry=prompt_registry)
    tokenizer = Tokenizer()

    if settings.OPENAI_API_KEY:
        try:
            registry.register(
                OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    model="gpt-4o",
                )
            )
        except Exception as e:
            logger.error(f"Failed to register OpenAIProvider: {e}")

    if settings.ANTHROPIC_API_KEY:
        try:
            registry.register(
                AnthropicProvider(
                    api_key=settings.ANTHROPIC_API_KEY,
                )
            )
        except Exception as e:
            logger.error(f"Failed to register AnthropicProvider: {e}")

    if settings.GEMINI_API_KEY:
        try:
            registry.register(
                GeminiProvider(
                    api_key=settings.GEMINI_API_KEY,
                )
            )
        except Exception as e:
            logger.error(f"Failed to register GeminiProvider: {e}")

    if settings.MISTRAL_API_KEY:
        try:
            registry.register(
                MistralProvider(
                    api_key=settings.MISTRAL_API_KEY,
                )
            )
        except Exception as e:
            logger.error(f"Failed to register MistralProvider: {e}")

    if settings.OLLAMA_HOST:
        try:
            registry.register(
                OllamaProvider(
                    model="llama3",
                    base_url=settings.OLLAMA_HOST,
                )
            )
        except Exception as e:
            logger.error(f"Failed to register OllamaProvider: {e}")

    if getattr(settings, "OPENROUTER_API_KEY", None):
        try:
            registry.register(
                OpenRouterProvider(
                    api_key=settings.OPENROUTER_API_KEY,
                )
            )
        except Exception as e:
            logger.error(f"Failed to register OpenRouterProvider: {e}")

    manager = LLMManager(
        registry=registry,
        router=router,
        tokenizer=tokenizer,
        prompt_builder=prompts,
        cache=cache,
    )

    container.register("llm_registry", registry)
    container.register("llm_router", router)
    container.register("llm_manager", manager)
    container.register("llm_cache", cache)
    container.register("tokenizer", tokenizer)
    container.register("prompt_builder", prompts)


def register_memory(
    container: ServiceContainer,
) -> None:
    # TODO: Initialize memory system
    pass


def register_workspace(
    container: ServiceContainer,
) -> None:
    # TODO: Initialize workspace manager
    pass


def register_tools(
    container: ServiceContainer,
) -> None:
    # TODO: Initialize tool registry
    pass


def register_agents(
    container: ServiceContainer,
) -> None:
    # TODO:
    # Register Planner
    # Register Coding Agent
    # Register Reviewer
    # Register Debugger
    # Register Test Agent
    pass