from __future__ import annotations

from typing import Any

from app.config.settings import Settings
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
)
from app.services.base import BaseService
class ModelService(BaseService):
    """
    Manages LLM providers, model routing,
    benchmarking, pricing, and health.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ) -> None:

        super().__init__(
            settings=settings,
            container=container,
        )
        @property
    def router(self):
        return self.resolve("llm_router")


    @property
    def registry(self):
        return self.resolve("provider_registry")


    @property
    def llm(self):
        return self.resolve("llm_manager")
    async def providers(self):

        return await self.registry.providers()
    async def models(self):

        return await self.registry.models()
    async def get_model(
        self,
        model: str,
    ):

        info = await self.registry.get_model(
            model,
        )

        if info is None:
            raise NotFoundError(
                "Model not found."
            )

        return info
    async def default_model(self):

        return await self.router.default_model()
    async def set_default(
        self,
        model: str,
    ):

        await self.get_model(model)

        await self.router.set_default(
            model,
        )

        return True
    async def set_default(
        self,
        model: str,
    ):

        await self.get_model(model)

        await self.router.set_default(
            model,
        )

        return True

    async def default_model(self):

        return await self.router.default_model()
    async def get_model(
        self,
        model: str,
    ):

        info = await self.registry.get_model(
            model,
        )

        if info is None:
            raise NotFoundError(
                "Model not found."
            )

        return info
    async def chat(
        self,
        *,
        message: str,
        history: list,
        model: str | None = None,
    ):

        return await self.llm.chat(

            message=message,

            history=history,

            model=model,
        )
    async def stream(
        self,
        *,
        message: str,
        history: list,
        model: str | None = None,
    ):

        async for chunk in self.llm.stream(

            message=message,

            history=history,

            model=model,
        ):

            yield chunk
    async def estimate_tokens(
        self,
        text: str,
        model: str,
    ):

        return await self.llm.estimate_tokens(
            text,
            model,
        )
    async def estimate_cost(
        self,
        *,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ):

        return await self.llm.estimate_cost(

            model=model,

            prompt_tokens=prompt_tokens,

            completion_tokens=completion_tokens,
        )
    async def embedding(
        self,
        text: str,
        model: str | None = None,
    ):

        return await self.llm.embedding(

            text,

            model=model,
        )
    async def benchmark(
        self,
        prompt: str,
    ):

        return await self.router.benchmark(
            prompt,
        )
    async def provider_health(self):

        return await self.registry.health()
    async def refresh(self):

        return await self.registry.refresh()
    async def select(
        self,
        *,
        task: str,
        max_cost: float | None = None,
        max_latency: float | None = None,
    ):

        return await self.router.select(

            task=task,

            max_cost=max_cost,

            max_latency=max_latency,
        )
    async def fallback(
        self,
        failed_model: str,
    ):

        return await self.router.fallback(
            failed_model,
        )
    async def statistics(self):

        return await self.registry.statistics()
    async def health_check(self):

        return {

            "service": "ModelService",

            "healthy": True,

            "providers": True,

            "router": True,

            "llm": True,
        }