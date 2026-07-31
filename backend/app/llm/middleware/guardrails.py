# Guardrails Middleware
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.llm.exceptions import (
    GuardrailViolationError,
)
from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)

from .base import BaseMiddleware


# ============================================================
# Configuration
# ============================================================


@dataclass(slots=True)
class GuardrailConfig:
    """
    Guardrail configuration.
    """

    max_prompt_length: int = 100_000

    max_messages: int = 200

    allow_empty_response: bool = False

    blocked_patterns: list[str] = field(
        default_factory=lambda: [
            r"<script.*?>",
            r"javascript:",
        ]
    )

    blocked_tool_names: list[str] = field(
        default_factory=list
    )


# ============================================================
# Middleware
# ============================================================


class GuardrailMiddleware(BaseMiddleware):
    """
    Validates requests and responses.

    Checks:
    - Prompt size
    - Message count
    - Empty prompts
    - Dangerous patterns
    - Tool restrictions
    """

    def __init__(
        self,
        config: GuardrailConfig | None = None,
    ) -> None:

        self.config = config or GuardrailConfig()

    # ---------------------------------------------------------

    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:

        self._validate_messages(request)

        self._validate_prompt_length(request)

        self._validate_patterns(request)

        self._validate_tools(request)

        return request

    # ---------------------------------------------------------

    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:

        if (
            not self.config.allow_empty_response
            and response.message
            and not response.message.content.strip()
        ):
            raise GuardrailViolationError(
                "LLM returned an empty response."
            )

        return response

    # ---------------------------------------------------------

    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:
        """
        Nothing to do.
        """
        return None

    # =========================================================
    # Validation
    # =========================================================

    def _validate_messages(
        self,
        request: ChatRequest,
    ) -> None:

        if not request.messages:
            raise GuardrailViolationError(
                "Request contains no messages."
            )

        if (
            len(request.messages)
            > self.config.max_messages
        ):
            raise GuardrailViolationError(
                "Too many messages."
            )

    # ---------------------------------------------------------

    def _validate_prompt_length(
        self,
        request: ChatRequest,
    ) -> None:

        total = sum(
            len(message.content)
            for message in request.messages
        )

        if total > self.config.max_prompt_length:
            raise GuardrailViolationError(
                "Prompt exceeds configured limit."
            )

    # ---------------------------------------------------------

    def _validate_patterns(
        self,
        request: ChatRequest,
    ) -> None:

        for message in request.messages:

            for pattern in self.config.blocked_patterns:

                if re.search(
                    pattern,
                    message.content,
                    re.IGNORECASE,
                ):
                    raise GuardrailViolationError(
                        f"Blocked pattern detected: {pattern}"
                    )

    # ---------------------------------------------------------

    def _validate_tools(
        self,
        request: ChatRequest,
    ) -> None:

        if not request.tools:
            return

        for tool in request.tools:

            if (
                tool.name
                in self.config.blocked_tool_names
            ):
                raise GuardrailViolationError(
                    f"Tool '{tool.name}' is blocked."
                )