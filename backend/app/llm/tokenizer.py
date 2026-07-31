# LLM Tokenizer
from __future__ import annotations

import math
from dataclasses import dataclass

from .provider import ChatMessage


# ============================================================
# Model Information
# ============================================================


@dataclass(slots=True)
class ModelInfo:
    """
    Metadata describing an LLM.
    """

    name: str

    context_window: int

    max_output_tokens: int

    input_cost_per_1k: float = 0.0

    output_cost_per_1k: float = 0.0


# ============================================================
# Token Estimator
# ============================================================


class TokenEstimator:
    """
    Approximate token counting.

    Can later be replaced by:
    - tiktoken
    - Anthropic tokenizer
    - SentencePiece
    - HuggingFace tokenizer
    """

    @staticmethod
    def estimate_text(text: str) -> int:
        """
        Approximate token count.

        ~4 characters/token is a common heuristic.
        """

        if not text:
            return 0

        return math.ceil(len(text) / 4)

    @classmethod
    def estimate_messages(
        cls,
        messages: list[ChatMessage],
    ) -> int:

        total = 0

        for message in messages:
            total += cls.estimate_text(
                message.content
            )

            # Message formatting overhead
            total += 4

        return total


# ============================================================
# Context Manager
# ============================================================


class ContextManager:
    """
    Ensures prompts fit inside the model context window.
    """

    def __init__(
        self,
        model: ModelInfo,
    ) -> None:

        self.model = model

    def remaining_tokens(
        self,
        prompt_tokens: int,
    ) -> int:

        remaining = (
            self.model.context_window
            - prompt_tokens
        )

        return max(0, remaining)

    def exceeds_context(
        self,
        prompt_tokens: int,
    ) -> bool:

        return (
            prompt_tokens
            > self.model.context_window
        )

    def truncate_messages(
        self,
        messages: list[ChatMessage],
    ) -> list[ChatMessage]:
        """
        Remove oldest messages until the prompt fits.
        """

        result = list(messages)

        while (
            TokenEstimator.estimate_messages(result)
            > self.model.context_window
            and len(result) > 1
        ):
            result.pop(0)

        return result


# ============================================================
# Cost Estimator
# ============================================================


class CostEstimator:
    """
    Estimate request pricing.
    """

    @staticmethod
    def estimate(
        *,
        model: ModelInfo,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:

        input_cost = (
            prompt_tokens
            / 1000
        ) * model.input_cost_per_1k

        output_cost = (
            completion_tokens
            / 1000
        ) * model.output_cost_per_1k

        return round(
            input_cost + output_cost,
            6,
        )


# ============================================================
# Tokenizer
# ============================================================


class Tokenizer:
    """
    High-level tokenizer utility.
    """

    def __init__(
        self,
        model: ModelInfo,
    ) -> None:

        self.model = model

        self.context = ContextManager(model)

    def count_messages(
        self,
        messages: list[ChatMessage],
    ) -> int:

        return TokenEstimator.estimate_messages(
            messages
        )

    def count_text(
        self,
        text: str,
    ) -> int:

        return TokenEstimator.estimate_text(
            text
        )

    def available_completion_tokens(
        self,
        messages: list[ChatMessage],
    ) -> int:

        prompt_tokens = self.count_messages(
            messages
        )

        remaining = self.context.remaining_tokens(
            prompt_tokens
        )

        return min(
            remaining,
            self.model.max_output_tokens,
        )

    def prepare_messages(
        self,
        messages: list[ChatMessage],
    ) -> list[ChatMessage]:

        return self.context.truncate_messages(
            messages
        )

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:

        return CostEstimator.estimate(
            model=self.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )