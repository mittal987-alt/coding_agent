"""
Shared LangGraph State

Every agent reads and writes to this object.
All fields are defined exactly once. Pydantic v2 model — no duplicates.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.coding.models import FileEdit
from app.review.models import ReviewIssue
from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import RetrievalResult


class AgentState(BaseModel):
    """
    Canonical shared workflow state passed through every LangGraph node.

    Design rules:
    - Each field is defined exactly once.
    - Optional fields default to None / [] / {}.
    - Fields required at creation: user_request, workspace_id.
    - repository is injected by the RepositoryAgent node.
    """

    model_config = {"arbitrary_types_allowed": True}

    # -------------------------
    # User Input
    # -------------------------

    user_request: str
    """The raw developer request triggering this workflow run."""

    conversation_id: Optional[str] = None
    """Linked conversation session ID for memory retrieval."""

    workspace_id: int
    """ID of the active workspace / repository."""

    # -------------------------
    # Repository Index
    # -------------------------

    repository: Optional[RepositoryIndex] = None
    """Populated by RepositoryAgent: AST + symbol graph index of the workspace."""

    repository_summary: dict[str, Any] = Field(default_factory=dict)
    """High-level metadata about the indexed repository (language breakdown, file count, etc.)."""

    # -------------------------
    # Project Specification
    # -------------------------

    spec: Optional[dict[str, Any]] = None
    """Parsed ProjectSpecification from AGENTS.md / .cursorrules injected by SupervisorAgent."""

    # -------------------------
    # Planning
    # -------------------------

    plan: Optional[str] = None
    """Structured implementation plan produced by PlannerAgent."""

    tasks: list[str] = Field(default_factory=list)
    """Decomposed sub-task list derived from the plan."""

    # -------------------------
    # Retrieval (RAG)
    # -------------------------

    retrieval_prompt: Optional[str] = None
    """Assembled context prompt built from hybrid retrieval results."""

    retrieval_results: list[RetrievalResult] = Field(default_factory=list)
    """Raw ranked retrieval result objects for downstream inspection."""

    # -------------------------
    # Coding
    # -------------------------

    generated_code: Optional[str] = None
    """Human-readable summary of all code edits produced by CoderAgent."""

    code_edits: list[FileEdit] = Field(default_factory=list)
    """Structured list of FileEdit patch objects (StructuredPatch hunks)."""

    modified_files: list[str] = Field(default_factory=list)
    """Relative paths of all files touched by code_edits."""

    # -------------------------
    # Code Review
    # -------------------------

    review: Optional[str] = None
    """Full code review output from ReviewerAgent."""

    review_passed: bool = False
    """True when ReviewerAgent approves all code_edits."""

    review_issues: list[ReviewIssue] = Field(default_factory=list)
    """Specific review issues flagged by the ReviewerAgent."""

    # -------------------------
    # Terminal Execution
    # -------------------------

    terminal_output: Optional[str] = None
    """Raw stdout/stderr captured from terminal command execution."""

    terminal_success: bool = False
    """True when the terminal command exited with code 0."""

    last_command: Optional[str] = None
    """The last shell command dispatched to the terminal."""

    # -------------------------
    # Test Execution
    # -------------------------

    test_output: Optional[str] = None
    """Raw pytest / jest output from the TesterAgent sandbox run."""

    tests_passed: bool = False
    """True when the test runner reports zero failures."""

    test_suite: Optional[str] = None
    """Generated test suite code produced by TesterAgent."""

    test_recommendations: list[str] = Field(default_factory=list)
    """Additional test cases recommended by TesterAgent."""

    # -------------------------
    # Self-Correction & TDD Loop
    # -------------------------

    retry_count: int = 0
    """Current EvaluatorAgent retry iteration (max enforced by EvaluatorAgent.max_retries)."""

    should_retry: bool = False
    """Set to True by EvaluatorAgent to re-route back to CoderAgent."""

    evaluator_feedback: Optional[str] = None
    """Actionable repair instructions produced by EvaluatorAgent for CoderAgent."""

    last_error_traceback: Optional[str] = None
    """Extracted stack trace from the failing test/terminal run."""

    # -------------------------
    # Human-in-the-Loop (HITL)
    # -------------------------

    hitl_pending: bool = False
    """True when workflow is paused at an interrupt_before checkpoint awaiting human approval."""

    hitl_node_id: Optional[str] = None
    """The graph node name that triggered the HITL interrupt."""

    hitl_approved: Optional[bool] = None
    """Set to True/False when the human approves or rejects via /api/v1/hitl/approve|reject."""

    # -------------------------
    # Git
    # -------------------------

    git_status: dict[str, Any] = Field(default_factory=dict)
    """Output of `git status --porcelain` parsed into a structured dict."""

    commit_hash: Optional[str] = None
    """SHA of the commit created by GitAgent after applying code_edits."""

    git_commit_message: Optional[str] = None
    """Auto-generated commit message produced by GitAgent."""

    # -------------------------
    # Memory
    # -------------------------

    memory_count: int = 0
    """Number of memories stored in this session (used by router to skip duplicate memory writes)."""

    # -------------------------
    # Workflow Routing
    # -------------------------

    current_agent: Optional[str] = None
    """Name of the currently executing agent node."""

    next_agent: Optional[str] = None
    """Name of the next agent node to execute (set by SupervisorAgent)."""

    completed_agents: list[str] = Field(default_factory=list)
    """Ordered list of agent names that have completed execution in this run."""

    failed_agents: list[str] = Field(default_factory=list)
    """Agent names that raised exceptions during safe_run()."""

    # -------------------------
    # Final Response
    # -------------------------

    response: Optional[str] = None
    """Final formatted response streamed back to the developer by ResponderAgent."""