"""
Workflow Router

Determines which node executes next.
"""

from __future__ import annotations

from langgraph.graph import END

from app.graph.state import AgentState


class WorkflowRouter:

    """
    Determines the next node in the workflow.
    """

    def route(
        self,
        state: AgentState,
    ) -> str:

        # -------------------------
        # Planning
        # -------------------------

        if not state.plan:

            return "planner"

        # -------------------------
        # Retrieval
        # -------------------------

        if not state.retrieval_prompt:

            return "retriever"

        # -------------------------
        # Coding
        # -------------------------

        if not state.code_edits:

            return "coder"

        # -------------------------
        # Review
        # -------------------------

        if not state.review:

            return "reviewer"

        # -------------------------
        # Review Failed
        # -------------------------

        if not state.review_passed:

            return "coder"

        # -------------------------
        # Terminal
        # -------------------------

        if not state.terminal_output:

            return "terminal"

        # -------------------------
        # Testing
        # -------------------------

        if not state.test_output:

            return "tester"

        # -------------------------
        # Tests Failed
        # -------------------------

        if not state.tests_passed:

            return "coder"

        # -------------------------
        # Git
        # -------------------------

        if not state.commit_hash:

            return "git"

        # -------------------------
        # Memory
        # -------------------------

        if state.memory_count == 0:

            return "memory"

        # -------------------------
        # Response
        # -------------------------

        if not state.response:

            return "responder"

        return END