"""
Workflow SSE Stream Endpoint

Provides real-time Server-Sent Events (SSE) for the LangGraph execution pipeline.
The frontend GraphVisualizer subscribes to this stream to animate node status
transitions live as the agent workflow progresses.

Routes:
  GET /api/v1/stream/{workflow_id}   — SSE stream for a workflow run
  POST /api/v1/stream/start          — Start a new workflow and return its ID

SSE Event types emitted:
  node_started   { node_id, node_name, role }
  node_completed { node_id, details? }
  node_failed    { node_id, error }
  hitl_interrupt { node_id, node_name }
  workflow_done  { response? }
  heartbeat      { ts }              — keepalive every 15s
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.graph.checkpoint import CheckpointManager
from app.graph.state import AgentState

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory workflow event queues: workflow_id → asyncio.Queue[dict]
# In production, replace with Redis pub/sub for multi-process deployments
_event_queues: dict[str, asyncio.Queue] = {}

# Global checkpoint manager (shared with HITL API)
_checkpoint_manager = CheckpointManager()

# SSE heartbeat interval in seconds
HEARTBEAT_INTERVAL: float = 15.0

# Agent node display metadata (id → display info)
NODE_META: dict[str, dict] = {
    "supervisor":  {"name": "Supervisor",  "role": "Routing & Orchestration"},
    "planner":     {"name": "Planner",     "role": "Task Decomposition"},
    "repository":  {"name": "Repository",  "role": "AST Indexing"},
    "retriever":   {"name": "Retriever",   "role": "Hybrid RAG Retrieval"},
    "coder":       {"name": "Coder",       "role": "Code Patch Generation"},
    "reviewer":    {"name": "Reviewer",    "role": "Code Review"},
    "terminal":    {"name": "Terminal",    "role": "Shell Execution"},
    "tester":      {"name": "Tester",      "role": "Unit Test Runner"},
    "evaluator":   {"name": "Evaluator",   "role": "TDD Self-Correction"},
    "git":         {"name": "Git",         "role": "Version Control"},
    "memory":      {"name": "Memory",      "role": "Episodic Memory"},
    "responder":   {"name": "Responder",   "role": "Final Response"},
}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class WorkflowStartRequest(BaseModel):
    """Request payload to start a new autonomous coding workflow."""

    user_request: str = Field(
        ...,
        description="Developer's natural language coding request.",
        min_length=1,
    )
    workspace_id: int = Field(
        ...,
        description="ID of the active workspace / repository.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for memory continuity.",
    )
    enable_hitl: bool = Field(
        default=True,
        description="When True, the workflow pauses before git/terminal nodes for human approval.",
    )


class WorkflowStartResponse(BaseModel):
    """Response returned when a new workflow is successfully queued."""

    workflow_id: str
    message: str
    stream_url: str


# ---------------------------------------------------------------------------
# Event queue helpers
# ---------------------------------------------------------------------------


def get_or_create_queue(workflow_id: str) -> asyncio.Queue:
    """Return existing event queue or create a new one for this workflow."""
    if workflow_id not in _event_queues:
        _event_queues[workflow_id] = asyncio.Queue(maxsize=256)
    return _event_queues[workflow_id]


async def publish_event(workflow_id: str, event: dict) -> None:
    """
    Publish a workflow event to the SSE queue for the given workflow.

    Called by the workflow execution layer as each node completes.

    Args:
        workflow_id: Target workflow stream ID.
        event:       Dict with keys: type, and type-specific fields.
    """
    queue = get_or_create_queue(workflow_id)
    try:
        queue.put_nowait(event)
    except asyncio.QueueFull:
        logger.warning("SSE queue full for workflow %s — dropping event %s", workflow_id, event.get("type"))


def format_sse(event_type: str, data: dict) -> str:
    """
    Format a Python dict as an SSE message string.

    Format:
        event: <event_type>\\n
        data: <json>\\n
        \\n

    Args:
        event_type: SSE event name (e.g. 'node_started').
        data:       Dict payload to JSON-encode as the data field.

    Returns:
        Formatted SSE message string.
    """
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# SSE Stream endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/{workflow_id}",
    summary="Subscribe to workflow SSE stream",
    description=(
        "Opens a Server-Sent Events connection for the specified workflow. "
        "Emits node_started, node_completed, node_failed, hitl_interrupt, "
        "and workflow_done events. Sends a heartbeat every 15 seconds."
    ),
    response_class=StreamingResponse,
)
async def stream_workflow(
    workflow_id: str,
    request: Request,
) -> StreamingResponse:
    """
    SSE endpoint consumed by the frontend GraphVisualizer useWorkflowStream() hook.

    The client subscribes as soon as it starts a workflow run. The backend
    publishes events via publish_event() as each LangGraph node executes.
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        queue = get_or_create_queue(workflow_id)
        last_heartbeat = time.monotonic()

        # Initial connection acknowledgement
        yield format_sse("connected", {"workflow_id": workflow_id, "ts": int(time.time())})

        try:
            while True:
                # Check for client disconnect
                if await request.is_disconnected():
                    logger.info("SSE client disconnected: workflow=%s", workflow_id)
                    break

                # Try to dequeue the next event (non-blocking)
                try:
                    event = queue.get_nowait()
                except asyncio.QueueEmpty:
                    # Send heartbeat if interval elapsed
                    now = time.monotonic()
                    if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                        yield format_sse("heartbeat", {"ts": int(time.time())})
                        last_heartbeat = now
                    await asyncio.sleep(0.1)
                    continue

                event_type = event.pop("type", "message")
                yield format_sse(event_type, event)

                # Stop streaming after terminal events
                if event_type == "workflow_done":
                    _event_queues.pop(workflow_id, None)
                    break

        except asyncio.CancelledError:
            logger.info("SSE stream cancelled: workflow=%s", workflow_id)
        finally:
            # Clean up queue if client disconnects before workflow_done
            _event_queues.pop(workflow_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",          # Disable Nginx response buffering
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",  # Adjust in prod to specific origin
        },
    )


# ---------------------------------------------------------------------------
# Workflow start endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/start",
    response_model=WorkflowStartResponse,
    summary="Start a new autonomous coding workflow",
    description=(
        "Queues a new LangGraph workflow run for the given user request and workspace. "
        "Returns a workflow_id to subscribe to the SSE stream."
    ),
)
async def start_workflow(body: WorkflowStartRequest) -> WorkflowStartResponse:
    """
    Launch a new workflow and return the workflow_id for SSE subscription.

    The actual graph execution is dispatched as a background asyncio task.
    The frontend should subscribe to /api/v1/stream/{workflow_id} before or
    immediately after calling this endpoint.
    """
    workflow_id = str(uuid.uuid4())

    # Pre-create the event queue so the SSE client can connect immediately
    get_or_create_queue(workflow_id)

    # Launch graph execution as a background task
    asyncio.create_task(
        _run_workflow_background(
            workflow_id=workflow_id,
            user_request=body.user_request,
            workspace_id=body.workspace_id,
            conversation_id=body.conversation_id,
            enable_hitl=body.enable_hitl,
        )
    )

    return WorkflowStartResponse(
        workflow_id=workflow_id,
        message="Workflow started. Subscribe to the stream_url for live updates.",
        stream_url=f"/api/v1/stream/{workflow_id}",
    )


# ---------------------------------------------------------------------------
# Background workflow executor
# ---------------------------------------------------------------------------


async def _run_workflow_background(
    workflow_id: str,
    user_request: str,
    workspace_id: int,
    conversation_id: Optional[str],
    enable_hitl: bool,
) -> None:
    """
    Execute the LangGraph AIWorkflow in the background and publish SSE events
    to the queue as each node completes.

    This function is launched as an asyncio background task by the /start endpoint.
    """
    try:
        from app.bootstrap.container import container

        # Resolve workflow dependencies from DI container
        llm = container.resolve("llm")
        repository = container.resolve("repository_manager")
        retriever = container.resolve("vector_retriever")
        memory_manager = container.resolve("memory_manager")

        from app.graph.workflow import AIWorkflow

        workflow = AIWorkflow(
            llm=llm,
            repository=repository,
            retriever=retriever,
            memory_manager=memory_manager,
            enable_hitl=enable_hitl,
        )

        # Stream node-level updates
        async for node_name, updated_state in workflow.stream(
            user_request=user_request,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
        ):
            meta = NODE_META.get(node_name, {"name": node_name, "role": ""})

            # Detect HITL interrupt
            if isinstance(updated_state, AgentState) and updated_state.hitl_pending:
                _checkpoint_manager.save(workflow_id, updated_state)
                await publish_event(workflow_id, {
                    "type": "hitl_interrupt",
                    "node_id": node_name,
                    "node_name": meta["name"],
                })
                logger.info("Workflow %s paused at HITL node: %s", workflow_id, node_name)
                return  # Graph is paused — client will resume via /hitl/approve

            # Emit node completion event
            await publish_event(workflow_id, {
                "type": "node_completed",
                "node_id": node_name,
                "details": _extract_node_details(node_name, updated_state),
            })

        # Emit final response
        final_response: str = ""
        if isinstance(updated_state, AgentState):
            final_response = updated_state.response or ""

        await publish_event(workflow_id, {
            "type": "workflow_done",
            "response": final_response,
        })

    except Exception as exc:
        logger.exception("Workflow %s failed: %s", workflow_id, exc)
        await publish_event(workflow_id, {
            "type": "node_failed",
            "node_id": "unknown",
            "error": str(exc),
        })
        await publish_event(workflow_id, {
            "type": "workflow_done",
            "response": f"Workflow failed: {exc}",
        })


def _extract_node_details(node_name: str, state) -> str:
    """Extract a brief human-readable status string from the updated state."""
    if not isinstance(state, AgentState):
        return ""
    details_map = {
        "planner":   lambda s: f"Plan ready ({len(s.tasks)} tasks)" if s.tasks else "Plan generated",
        "coder":     lambda s: f"{len(s.code_edits)} file edits generated",
        "tester":    lambda s: "Tests passed ✓" if s.tests_passed else "Tests failed ✗",
        "evaluator": lambda s: f"Retry {s.retry_count} — {(s.evaluator_feedback or '')[:80]}",
        "reviewer":  lambda s: "Review passed ✓" if s.review_passed else "Review failed — re-generating",
        "git":       lambda s: f"Committed: {s.commit_hash[:8]}" if s.commit_hash else "Commit failed",
        "retriever": lambda s: f"{len(s.retrieval_results)} chunks retrieved",
    }
    fn = details_map.get(node_name)
    try:
        return fn(state) if fn else ""
    except Exception:
        return ""
