"""
Graph Edge Registration
"""

from __future__ import annotations

from langgraph.graph import END

from app.graph.router import WorkflowRouter


router = WorkflowRouter()


def register_edges(builder):

    # -----------------------
    # Workflow Entry
    # -----------------------

    builder.set_entry_point(
        "supervisor"
    )

    # -----------------------
    # Supervisor
    # -----------------------

    builder.add_conditional_edges(

        "supervisor",

        router.route,

    )

    # -----------------------
    # Planner
    # -----------------------

    builder.add_conditional_edges(

        "planner",

        router.route,

    )

    # -----------------------
    # Repository
    # -----------------------

    builder.add_conditional_edges(

        "repository",

        router.route,

    )

    # -----------------------
    # Retriever
    # -----------------------

    builder.add_conditional_edges(

        "retriever",

        router.route,

    )

    # -----------------------
    # Coder
    # -----------------------

    builder.add_conditional_edges(

        "coder",

        router.route,

    )

    # -----------------------
    # Reviewer
    # -----------------------

    builder.add_conditional_edges(

        "reviewer",

        router.route,

    )

    # -----------------------
    # Terminal
    # -----------------------

    builder.add_conditional_edges(

        "terminal",

        router.route,

    )

    # -----------------------
    # Tester
    # -----------------------

    builder.add_conditional_edges(

        "tester",

        router.route,

    )

    # -----------------------
    # Git
    # -----------------------

    builder.add_conditional_edges(

        "git",

        router.route,

    )

    # -----------------------
    # Memory
    # -----------------------

    builder.add_conditional_edges(

        "memory",

        router.route,

    )

    # -----------------------
    # Response
    # -----------------------

    builder.add_conditional_edges(

        "responder",

        router.route,

    )

    # -----------------------
    # Finish
    # -----------------------

    builder.add_edge(

        END,

        END,

    )

    return builder