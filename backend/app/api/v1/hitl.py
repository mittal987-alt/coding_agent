"""
Human-in-the-Loop (HITL) API

Endpoints for resuming or aborting LangGraph workflows that are paused
at interrupt_before checkpoint nodes (e.g. 'git', 'terminal').

Routes:
  GET  /api/v1/hitl/pending          — list all workflows awaiting approval
  POST /api/v1/hitl/{workflow_id}/approve  — resume the paused graph
  POST /api/v1/hitl/{workflow_id}/reject   — abort the paused graph
  GET  /api/v1/hitl/{workflow_id}/status   — inspect checkpoint state
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.graph.checkpoint import CheckpointManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Module-level CheckpointManager (shared with workflow execution layer)
_checkpoint_manager = CheckpointManager()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class HITLApproveRequest(BaseModel):
    """Payload for approving a HITL-interrupted workflow."""

    comment: str = Field(
        default="",
        description="Optional human reviewer comment appended to the workflow log.",
    )


class HITLRejectRequest(BaseModel):
    """Payload for rejecting a HITL-interrupted workflow."""

    reason: str = Field(
        default="Rejected by operator.",
        description="Human-readable reason for rejection.",
    )


class HITLWorkflowSummary(BaseModel):
    """Summary of a single HITL-pending workflow."""

    workflow_id: str
    hitl_node_id: str | None
    user_request: str | None
    workspace_id: int | None
    retry_count: int


class HITLPendingResponse(BaseModel):
    """List of all workflows currently awaiting HITL approval."""

    pending: list[HITLWorkflowSummary]
    count: int


class HITLActionResponse(BaseModel):
    """Response returned after an approve or reject action."""

    workflow_id: str
    action: str
    success: bool
    message: str


class HITLStatusResponse(BaseModel):
    """Snapshot of a workflow checkpoint state."""

    workflow_id: str
    exists: bool
    hitl_pending: bool
    hitl_node_id: str | None
    hitl_approved: bool | None
    retry_count: int
    tests_passed: bool
    modified_files: list[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/pending",
    response_model=HITLPendingResponse,
    summary="List all HITL-pending workflows",
    description="Returns all workflow runs that are currently paused at a HITL checkpoint awaiting human approval.",
)
async def list_pending_workflows() -> HITLPendingResponse:
    """Return all workflows with hitl_pending=True."""
    pending_ids = _checkpoint_manager.list_pending()
    summaries: list[HITLWorkflowSummary] = []

    for wid in pending_ids:
        state = _checkpoint_manager.load(wid)
        if state:
            summaries.append(
                HITLWorkflowSummary(
                    workflow_id=wid,
                    hitl_node_id=state.hitl_node_id,
                    user_request=state.user_request,
                    workspace_id=state.workspace_id,
                    retry_count=state.retry_count,
                )
            )

    return HITLPendingResponse(pending=summaries, count=len(summaries))


@router.post(
    "/{workflow_id}/approve",
    response_model=HITLActionResponse,
    summary="Approve a HITL-interrupted workflow",
    description="Resumes the paused workflow by setting hitl_approved=True and hitl_pending=False, then triggers graph resumption.",
)
async def approve_workflow(
    workflow_id: str,
    body: HITLApproveRequest,
) -> HITLActionResponse:
    """
    Approve a HITL checkpoint — unblocks the paused graph node.

    The caller is responsible for re-invoking the workflow graph
    (e.g. via the /api/v1/chat/stream endpoint with the same workflow_id).
    This endpoint updates the checkpoint state so the router no longer
    returns the blocked node.
    """
    state = _checkpoint_manager.load(workflow_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No checkpoint found for workflow_id='{workflow_id}'.",
        )

    if not state.hitl_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workflow '{workflow_id}' is not in a HITL-pending state.",
        )

    # Update checkpoint state
    state.hitl_approved = True
    state.hitl_pending = False
    if body.comment:
        logger.info(
            "HITL approved [%s] by operator. Comment: %s",
            workflow_id,
            body.comment,
        )

    _checkpoint_manager.save(workflow_id, state)

    return HITLActionResponse(
        workflow_id=workflow_id,
        action="approve",
        success=True,
        message=f"Workflow '{workflow_id}' approved. Resume execution by re-invoking the workflow.",
    )


@router.post(
    "/{workflow_id}/reject",
    response_model=HITLActionResponse,
    summary="Reject and abort a HITL-interrupted workflow",
    description="Aborts the paused workflow by setting hitl_approved=False and deleting the checkpoint.",
)
async def reject_workflow(
    workflow_id: str,
    body: HITLRejectRequest,
) -> HITLActionResponse:
    """
    Reject a HITL checkpoint — marks the workflow as aborted and cleans up.
    """
    state = _checkpoint_manager.load(workflow_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No checkpoint found for workflow_id='{workflow_id}'.",
        )

    if not state.hitl_pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workflow '{workflow_id}' is not in a HITL-pending state.",
        )

    logger.warning(
        "HITL rejected [%s]. Reason: %s",
        workflow_id,
        body.reason,
    )

    # Mark as rejected then delete checkpoint
    state.hitl_approved = False
    state.hitl_pending = False
    state.response = f"Workflow rejected by operator: {body.reason}"
    _checkpoint_manager.delete(workflow_id)

    return HITLActionResponse(
        workflow_id=workflow_id,
        action="reject",
        success=True,
        message=f"Workflow '{workflow_id}' rejected and checkpoint deleted.",
    )


@router.get(
    "/{workflow_id}/status",
    response_model=HITLStatusResponse,
    summary="Inspect workflow checkpoint state",
    description="Returns a snapshot of the current AgentState for a checkpointed workflow.",
)
async def get_workflow_status(workflow_id: str) -> HITLStatusResponse:
    """Return key state fields from the workflow checkpoint."""
    exists = _checkpoint_manager.exists(workflow_id)
    if not exists:
        return HITLStatusResponse(
            workflow_id=workflow_id,
            exists=False,
            hitl_pending=False,
            hitl_node_id=None,
            hitl_approved=None,
            retry_count=0,
            tests_passed=False,
            modified_files=[],
        )

    state = _checkpoint_manager.load(workflow_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Checkpoint file exists but could not be loaded.",
        )

    return HITLStatusResponse(
        workflow_id=workflow_id,
        exists=True,
        hitl_pending=state.hitl_pending,
        hitl_node_id=state.hitl_node_id,
        hitl_approved=state.hitl_approved,
        retry_count=state.retry_count,
        tests_passed=state.tests_passed,
        modified_files=state.modified_files,
    )
