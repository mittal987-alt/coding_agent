"""
LangSmith Observability Module

Provides structured LLM call tracing for the autonomous coding pipeline.
Wraps every agent's invoke_llm() with LangSmith RunTree context to capture:
  - Token usage (prompt_tokens, completion_tokens, total_tokens)
  - Latency per LLM call
  - Agent name and model identifier
  - Input/output content for debugging
  - Tool calls made within agent runs

Configuration (via environment variables):
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=<your-langsmith-key>
  LANGCHAIN_PROJECT=ai-software-engineer   (optional, defaults to project name)

Usage::

    from app.core.observability import traced_llm_call

    # In BaseAgent.invoke_llm():
    result = await traced_llm_call(
        agent_name="Coder",
        llm=self.llm,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LangSmith availability check
# ---------------------------------------------------------------------------

_LANGSMITH_ENABLED: bool = False

try:
    import langsmith
    from langsmith import Client as LangSmithClient
    from langsmith.run_trees import RunTree

    _api_key = os.getenv("LANGCHAIN_API_KEY", "")
    _tracing = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    if _api_key and _tracing:
        _LANGSMITH_ENABLED = True
        logger.info("LangSmith observability: ENABLED")
    else:
        logger.info(
            "LangSmith observability: DISABLED "
            "(set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY to enable)"
        )
except ImportError:
    logger.warning(
        "langsmith package not installed — observability disabled. "
        "Run: pip install langsmith"
    )


# ---------------------------------------------------------------------------
# LangSmith project name
# ---------------------------------------------------------------------------

LANGSMITH_PROJECT: str = os.getenv(
    "LANGCHAIN_PROJECT",
    "ai-software-engineer",
)


# ---------------------------------------------------------------------------
# Core traced invocation wrapper
# ---------------------------------------------------------------------------


async def traced_llm_call(
    agent_name: str,
    llm: BaseChatModel,
    system_prompt: str,
    user_prompt: str,
    metadata: Optional[dict[str, Any]] = None,
) -> str:
    """
    Execute an LLM call and emit a LangSmith trace if observability is enabled.

    Falls back to a direct (untraced) llm.ainvoke() call when LangSmith
    is not configured, ensuring zero-overhead in development.

    Args:
        agent_name:    Name of the calling agent (e.g. "Coder", "Evaluator").
        llm:           LangChain BaseChatModel instance to invoke.
        system_prompt: System message content.
        user_prompt:   Human message content.
        metadata:      Optional key-value pairs attached to the LangSmith run.

    Returns:
        String content of the LLM response.
    """
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    if not _LANGSMITH_ENABLED:
        # Fast path — no tracing overhead
        response = await llm.ainvoke(messages)
        return response.content

    # ------------------------------------------------------------------
    # LangSmith traced path
    # ------------------------------------------------------------------
    run_name = f"{agent_name}.invoke_llm"
    extra_metadata: dict[str, Any] = {
        "agent": agent_name,
        "model": _get_model_name(llm),
        "system_prompt_chars": len(system_prompt),
        "user_prompt_chars": len(user_prompt),
    }
    if metadata:
        extra_metadata.update(metadata)

    run: RunTree = RunTree(
        name=run_name,
        run_type="llm",
        inputs={
            "system": system_prompt,
            "human": user_prompt,
        },
        project_name=LANGSMITH_PROJECT,
        extra={"metadata": extra_metadata},
    )

    start_time = time.perf_counter()
    try:
        response = await llm.ainvoke(messages)
        content: str = response.content
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Extract token usage if available (OpenAI / Anthropic responses)
        usage: dict[str, Any] = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(um, "input_tokens", 0),
                "completion_tokens": getattr(um, "output_tokens", 0),
                "total_tokens": getattr(um, "total_tokens", 0),
            }
        elif hasattr(response, "response_metadata"):
            token_usage = response.response_metadata.get("token_usage", {})
            usage = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

        run.end(
            outputs={"content": content},
            extra={
                "metadata": {
                    **extra_metadata,
                    "latency_ms": round(elapsed_ms, 2),
                    **usage,
                }
            },
        )

        logger.debug(
            "LangSmith trace: agent=%s latency=%.0fms tokens=%s",
            agent_name,
            elapsed_ms,
            usage.get("total_tokens", "?"),
        )

        return content

    except Exception as exc:
        run.end(error=str(exc))
        raise

    finally:
        try:
            run.post()
        except Exception as post_exc:
            logger.warning("LangSmith trace post failed: %s", post_exc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_model_name(llm: BaseChatModel) -> str:
    """Extract model identifier from LangChain model config."""
    for attr in ("model_name", "model", "model_id"):
        val = getattr(llm, attr, None)
        if val:
            return str(val)
    return type(llm).__name__


def is_tracing_enabled() -> bool:
    """Return True if LangSmith tracing is active."""
    return _LANGSMITH_ENABLED
