"""
Coder Agent

Generates structured, line-diff code edits (StructuredPatch hunks)
in response to the current plan and retrieval context.

Spec injection:
  - Reads state.spec.prohibited_packages and appends to system prompt
  - Reads state.spec.coding_style_guidelines and appends to system prompt
  - Injects evaluator_feedback when in a TDD retry loop
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.prompts.coder import (
    CODER_SYSTEM_PROMPT,
    CODER_USER_TEMPLATE,
)

from app.coding.models import CodingResult

logger = logging.getLogger(__name__)


class CoderAgent(BaseAgent):

    def __init__(self, llm):
        super().__init__(llm=llm, name="Coder")

    async def run(self, state: AgentState) -> AgentState:

        # ------------------------------------------------------------------
        # Build augmented system prompt with project spec constraints
        # ------------------------------------------------------------------
        system_prompt = self._build_system_prompt(state)

        # ------------------------------------------------------------------
        # Build user prompt — include evaluator feedback on retries
        # ------------------------------------------------------------------
        user_prompt = self._build_user_prompt(state)

        # ------------------------------------------------------------------
        # Invoke LLM
        # ------------------------------------------------------------------
        response = await self.invoke_llm(system_prompt, user_prompt)

        try:
            data = json.loads(response)
            result = CodingResult.model_validate(data)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.exception("CoderAgent: failed to parse LLM response: %s", exc)
            # Surface the raw response for debugging
            state.generated_code = f"[Parse error] {exc}\n\nRaw LLM output:\n{response[:2000]}"
            return state

        state.generated_code = result.summary
        state.code_edits = result.edits
        state.modified_files = [edit.path for edit in result.edits]

        logger.info(
            "Coder: generated %d file edits (retry=%d)",
            len(result.edits),
            state.retry_count,
        )

        return state

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _build_system_prompt(self, state: AgentState) -> str:
        """
        Augment the base CODER_SYSTEM_PROMPT with project spec constraints
        extracted from state.spec (parsed from AGENTS.md).
        """
        spec = state.spec or {}
        spec_lines: list[str] = []

        prohibited = spec.get("prohibited_packages", [])
        if prohibited:
            spec_lines.append("\n## Prohibited Packages / Patterns (from AGENTS.md)")
            spec_lines.extend(f"  ✗ DO NOT use: {p}" for p in prohibited)

        style = spec.get("coding_style_guidelines", [])
        if style:
            spec_lines.append("\n## Coding Style Guidelines (from AGENTS.md)")
            spec_lines.extend(f"  • {g}" for g in style)

        arch = spec.get("architectural_rules", [])
        if arch:
            spec_lines.append("\n## Architectural Rules (from AGENTS.md)")
            spec_lines.extend(f"  • {r}" for r in arch)

        if spec_lines:
            return CODER_SYSTEM_PROMPT + "\n" + "\n".join(spec_lines)

        return CODER_SYSTEM_PROMPT

    def _build_user_prompt(self, state: AgentState) -> str:
        """
        Build the user-facing prompt, injecting EvaluatorAgent feedback
        on TDD retry iterations so the model knows exactly what to fix.
        """
        base_prompt = CODER_USER_TEMPLATE.format(
            request=state.user_request,
            plan=state.plan or "No plan available.",
            context=state.retrieval_prompt or "No retrieval context available.",
        )

        if state.retry_count > 0 and state.evaluator_feedback:
            feedback_block = f"""
## ⚠️ TDD Self-Correction Loop — Retry {state.retry_count}

The previous code changes caused test failures. The Evaluator Agent has
diagnosed the root cause and provided the following repair instructions.
You MUST address ALL points below before generating new code edits.

### Evaluator Feedback:
{state.evaluator_feedback}

### Failing Test Traceback:
{state.last_error_traceback or 'No traceback captured.'}

### Previously Modified Files:
{chr(10).join(f'  - {f}' for f in state.modified_files) or '  None'}

Generate corrected code patches that fix ALL of the above issues.
"""
            return base_prompt + feedback_block

        return base_prompt