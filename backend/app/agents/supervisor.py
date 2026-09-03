"""
Supervisor Agent

Orchestrates the LangGraph workflow by:
1. Parsing AGENTS.md / .cursorrules project specification from the workspace
2. Injecting architectural rules + style guidelines into agent system prompts
3. Deciding the next agent to activate based on current workflow state
"""

from __future__ import annotations

import json
import logging

from app.agents.base import BaseAgent
from app.graph.state import AgentState
from app.parser.spec_parser import SpecParser
from app.prompts.supervisor import SUPERVISOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):

    def __init__(self, llm):
        super().__init__(llm=llm, name="Supervisor")

    async def run(self, state: AgentState) -> AgentState:

        # ------------------------------------------------------------------
        # Step 1: Parse AGENTS.md / project spec and inject into state
        # ------------------------------------------------------------------
        spec = self._parse_project_spec(state)
        state.spec = spec.model_dump() if spec.has_spec else None

        if spec.has_spec:
            logger.info(
                "Supervisor: loaded spec from '%s' (%d arch rules, %d style rules)",
                spec.source_file,
                len(spec.architectural_rules),
                len(spec.coding_style_guidelines),
            )

        # ------------------------------------------------------------------
        # Step 2: Build context summary for LLM routing decision
        # ------------------------------------------------------------------
        spec_context = self._format_spec_context(spec) if spec.has_spec else ""

        summary = f"""{spec_context}
User Request:
{state.user_request}

Current Plan:
{state.plan}

Tasks:
{state.tasks}

Review Passed:
{state.review_passed}

Tests Passed:
{state.tests_passed}

Terminal Success:
{state.terminal_success}

Retry Count:
{state.retry_count}

Modified Files:
{state.modified_files}
"""

        # ------------------------------------------------------------------
        # Step 3: Ask LLM for routing decision
        # ------------------------------------------------------------------
        response = await self.invoke_llm(SUPERVISOR_SYSTEM_PROMPT, summary)

        try:
            decision = json.loads(response)
            state.next_agent = decision.get("next_agent")
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Supervisor: failed to parse LLM routing decision: %s", exc)
            # Fallback: let the WorkflowRouter handle routing via state inspection
            state.next_agent = None

        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_project_spec(self, state: AgentState):
        """
        Discover and parse the workspace AGENTS.md / .cursorrules spec file.

        Uses workspace_id to derive workspace root path. Falls back gracefully
        if no spec file is found (returns empty ProjectSpecification).
        """
        from app.parser.spec_parser import ProjectSpecification

        # Derive workspace path from workspace_id
        # In production this should resolve via WorkspaceRepository
        workspace_path = f"storage/workspaces/{state.workspace_id}"

        try:
            return SpecParser.discover_and_parse(workspace_path)
        except Exception as exc:
            logger.warning("Supervisor: spec discovery failed: %s", exc)
            return ProjectSpecification(has_spec=False)

    def _format_spec_context(self, spec) -> str:
        """Format project specification as a system prompt context block."""
        lines = ["=== Project Specification (from {}) ===".format(spec.source_file)]

        if spec.architectural_rules:
            lines.append("\nArchitectural Rules:")
            lines.extend(f"  • {r}" for r in spec.architectural_rules)

        if spec.coding_style_guidelines:
            lines.append("\nCoding Style Guidelines:")
            lines.extend(f"  • {g}" for g in spec.coding_style_guidelines)

        if spec.prohibited_packages:
            lines.append("\nProhibited Packages / Patterns:")
            lines.extend(f"  ✗ {p}" for p in spec.prohibited_packages)

        if spec.custom_test_commands:
            lines.append("\nCustom Test Commands:")
            lines.extend(f"  $ {c}" for c in spec.custom_test_commands)

        lines.append("=" * 50)
        return "\n".join(lines)