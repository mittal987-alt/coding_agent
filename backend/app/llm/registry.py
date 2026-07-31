# LLM Registry
from __future__ import annotations

import logging

from .exceptions import (
    ModelNotFoundError,
    ProviderNotFoundError,
)
from .provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class LLMRegistry:
    """
    Central registry for LLM providers.

    Responsibilities:
    - Register providers
    - Retrieve providers
    - Manage default provider
    - List providers/models
    - Health checking
    """

    def __init__(self) -> None:
        self._providers: dict[str, BaseLLMProvider] = {}
        self._default_provider: str | None = None

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        provider: BaseLLMProvider,
        *,
        default: bool = False,
    ) -> None:
        """
        Register a provider instance.
        """

        name = provider.provider_name.lower()

        self._providers[name] = provider

        logger.info("Registered LLM provider: %s", name)

        if default or self._default_provider is None:
            self._default_provider = name

    def unregister(
        self,
        provider_name: str,
    ) -> None:
        """
        Remove a provider.
        """

        provider_name = provider_name.lower()

        if provider_name in self._providers:
            del self._providers[provider_name]

            logger.info(
                "Unregistered LLM provider: %s",
                provider_name,
            )

            if self._default_provider == provider_name:
                self._default_provider = (
                    next(iter(self._providers), None)
                )

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    def get(
        self,
        provider_name: str | None = None,
    ) -> BaseLLMProvider:
        """
        Retrieve a provider by name.
        """

        if provider_name is None:
            provider_name = self._default_provider

        if provider_name is None:
            raise ProviderNotFoundError(
                "No default provider configured."
            )

        provider = self._providers.get(
            provider_name.lower()
        )

        if provider is None:
            raise ProviderNotFoundError(
                f"Provider '{provider_name}' not found."
            )

        return provider

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def providers(
        self,
    ) -> list[str]:
        """
        List registered providers.
        """

        return sorted(self._providers.keys())

    async def available_models(
        self,
        provider_name: str | None = None,
    ) -> list[str]:
        """
        List models supported by a provider.
        """

        provider = self.get(provider_name)

        return await provider.available_models()

    async def supports_model(
        self,
        provider_name: str,
        model: str,
    ) -> bool:
        """
        Check whether a provider supports a model.
        """

        provider = self.get(provider_name)

        return model in await provider.available_models()

    async def provider_for_model(
        self,
        model: str,
    ) -> BaseLLMProvider:
        """
        Find the first provider supporting a model.
        """

        for provider in self._providers.values():

            try:
                models = await provider.available_models()

                if model in models:
                    return provider

            except Exception:
                logger.exception(
                    "Failed loading models from %s",
                    provider.provider_name,
                )

        raise ModelNotFoundError(
            f"No provider supports model '{model}'."
        )

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    async def healthy_providers(
        self,
    ) -> list[str]:
        """
        Return currently healthy providers.
        """

        healthy: list[str] = []

        for name, provider in self._providers.items():

            try:
                if await provider.health_check():
                    healthy.append(name)

            except Exception:
                logger.exception(
                    "Health check failed for %s",
                    name,
                )

        return healthy

    async def is_provider_healthy(
        self,
        provider_name: str,
    ) -> bool:
        """
        Check provider health.
        """

        provider = self.get(provider_name)

        return await provider.health_check()

    # ---------------------------------------------------------
    # Defaults
    # ---------------------------------------------------------

    def set_default(
        self,
        provider_name: str,
    ) -> None:
        """
        Set the default provider.
        """

        if provider_name.lower() not in self._providers:
            raise ProviderNotFoundError(
                provider_name
            )

        self._default_provider = provider_name.lower()

    @property
    def default_provider(
        self,
    ) -> str | None:
        """
        Current default provider.
        """

        return self._default_provider

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove all providers.
        """

        self._providers.clear()
        self._default_provider = None

    def __contains__(
        self,
        provider_name: str,
    ) -> bool:
        return (
            provider_name.lower()
            in self._providers
        )

    def __len__(
        self,
    ) -> int:
        return len(self._providers) 