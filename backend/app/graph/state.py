"""
Shared LangGraph State

Every agent reads and writes to this object.
"""

from __future__ import annotations

from typing import Any

from app.review.models import ReviewIssue

from app.coding.models import FileEdit
from pydantic import BaseModel

from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import RetrievalResult


class AgentState(BaseModel):
    """
    Shared workflow state.

    Passed through every LangGraph node.
    """

    # -------------------------
    # User
    # -------------------------

    user_request: str

    conversation_id: str | None = None

    workspace_id: int

    # -------------------------
    # Repository
    # -------------------------

    repository: RepositoryIndex

# -------------------------
# Review
# -------------------------

    review: str | None = None

    review_passed: bool = False

    review_issues: list[ReviewIssue] = []

    # -------------------------
    # Retrieval
    # -------------------------

    retrieval_prompt: str | None = None

    retrieval_results: list[RetrievalResult] = []

    # -------------------------
    # Planning
    # -------------------------

    plan: str | None = None

    tasks: list[str] = []

    # -------------------------
    # Coding
    # -------------------------

    generated_code: str | None = None

    modified_files: list[str] = []

    # -------------------------
    # Review
    # -------------------------

    review: str | None = None

    review_passed: bool = False

    # -------------------------
    # Terminal
    # -------------------------

    terminal_output: str | None = None

    terminal_success: bool = False

    # -------------------------
    # Testing
    # -------------------------

    test_output: str | None = None

    tests_passed: bool = False

    # -------------------------
# Final Response
# -------------------------

    response: str | None = None
    # -------------------------
    # -------------------------
    # Git
    # --------------------- ----

    commit_hash: str | None = None

    git_commit_message: str | None = None

    # -------------------------
    # Git
    # -------------------------

    commit_hash: str | None = None

    git_commit_message: str | None = None

    # -------------------------
# Testing
# -------------------------

    test_output: str | None = None

    tests_passed: bool = False

    test_recommendations: list[str] = []

    test_suite: str | None = None

    # -------------------------
# Terminal
# -------------------------

    terminal_output: str | None = None

    terminal_success: bool = False

    last_command: str | None = None

    # -------------------------
    # Workflow
    # -------------------------

    current_agent: str | None =     None

    next_agent: str | None = None

    completed_agents: list[str] = []

    failed_agents: list[str] = []

# -------------------------
# Coding
# -------------------------

    generated_code: str | None = None

    code_edits: list[FileEdit] = []

    modified_files: list[str] = []

    # -------------------------
    # Repository
    # -------------------------

    repository_summary: dict = {}

    # -------------------------
    # Git
    # -------------------------

    git_status: dict[str, Any] = {}

    commit_hash: str | None = None

    # -------------------------
    # Final
    # -------------------------

    response: str | None = None