"""
Graph Edge Registration

Wires all conditional and static edges between LangGraph nodes.

Edge map:
  supervisor  → [conditional] WorkflowRouter.route()
  planner     → [conditional] WorkflowRouter.route()
  repository  → [conditional] WorkflowRouter.route()
  retriever   → [conditional] WorkflowRouter.route()
  coder       → [conditional] WorkflowRouter.route()
  reviewer    → [conditional] WorkflowRouter.route()
  terminal    → [conditional] WorkflowRouter.route()
  tester      → [conditional] WorkflowRouter.route()
  evaluator   → [conditional] WorkflowRouter.route()  ← NEW
  git         → [conditional] WorkflowRouter.route()
  memory      → [conditional] WorkflowRouter.route()
  responder   → END (static)
"""

from __future__ import annotations

from langgraph.graph import END

from app.graph.router import WorkflowRouter


router = WorkflowRouter()


def register_edges(builder) -> None:
    """
    Register all edges on the provided StateGraph builder.

    Args:
        builder: LangGraph StateGraph builder instance.
    """

    # Entry point
    builder.set_entry_point("supervisor")

    # All orchestration nodes use the shared WorkflowRouter
    for node in [
        "supervisor",
        "planner",
        "repository",
        "retriever",
        "coder",
        "reviewer",
        "terminal",
        "tester",
        "evaluator",   # EvaluatorAgent TDD self-correction loop
        "git",
        "memory",
    ]:
        builder.add_conditional_edges(node, router.route)

    # Responder is always the terminal node — static edge to END
    builder.add_edge("responder", END)

    return builder