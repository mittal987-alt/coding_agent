"""
Patch Apply / Reject API

Endpoints for the interactive DiffViewer — allows developers to accept
or reject AI-generated code patches before they are committed to disk.

Routes:
  POST /api/v1/patches/apply   — apply a StructuredPatch to the workspace
  POST /api/v1/patches/reject  — discard a pending patch (no-op on disk)
  GET  /api/v1/patches/{patch_id} — retrieve a pending patch for preview
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.coding.diff_engine import (
    LineDiffEngine,
    StructuredPatch,
    LineHunk,
    EditType,
    PatchEngineResult,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class PatchApplyRequest(BaseModel):
    """Request body for applying a code patch to the workspace."""

    workspace_root: str = Field(
        ...,
        description="Absolute path to the workspace root directory on the server.",
        examples=["/workspaces/my-project"],
    )
    patch: StructuredPatch = Field(
        ...,
        description="The StructuredPatch to apply (may contain multiple LineHunks).",
    )
    create_backup: bool = Field(
        default=True,
        description="When True, backs up the original file as <file>.bak before patching.",
    )


class PatchRejectRequest(BaseModel):
    """Request body for rejecting / discarding a pending patch."""

    patch_id: Optional[str] = Field(
        default=None,
        description="Optional patch ID for logging purposes.",
    )
    reason: str = Field(
        default="Rejected by developer.",
        description="Human-readable reason for rejecting the patch.",
    )


class PatchApplyResponse(BaseModel):
    """Response returned after attempting to apply a patch."""

    success: bool
    file_path: str
    edit_type: str
    hunks_applied: int
    backup_path: Optional[str] = None
    diff: Optional[str] = None
    error: Optional[str] = None


class PatchRejectResponse(BaseModel):
    """Response returned after rejecting a patch."""

    success: bool
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/apply",
    response_model=PatchApplyResponse,
    summary="Apply an AI-generated code patch to the workspace",
    description=(
        "Reads the target file from disk, applies the StructuredPatch using the "
        "LineDiffEngine (line-hunk based replacement), and writes the result back. "
        "Optionally creates a .bak backup of the original file."
    ),
)
async def apply_patch(body: PatchApplyRequest) -> PatchApplyResponse:
    """Apply a StructuredPatch to the specified file in the workspace."""

    workspace_root = Path(body.workspace_root)
    if not workspace_root.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace root not found: {body.workspace_root}",
        )

    # Resolve file path and guard against directory traversal
    resolved_root = workspace_root.resolve()
    file_path = (resolved_root / body.patch.file_path.lstrip("/\\")).resolve()
    if resolved_root != file_path and resolved_root not in file_path.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file path outside workspace: {body.patch.file_path}",
        )
    edit_type = body.patch.edit_type

    # ------------------------------------------------------------------
    # Read original content
    # ------------------------------------------------------------------
    original_content = ""
    if edit_type != EditType.CREATE:
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target file not found: {body.patch.file_path}",
            )
        original_content = file_path.read_text(encoding="utf-8", errors="replace")

    # ------------------------------------------------------------------
    # Optional backup
    # ------------------------------------------------------------------
    backup_path: Optional[str] = None
    if body.create_backup and file_path.exists() and edit_type != EditType.CREATE:
        bak = file_path.with_suffix(file_path.suffix + ".bak")
        bak.write_text(original_content, encoding="utf-8")
        backup_path = str(bak)
        logger.info("Patch backup created: %s", bak)

    # ------------------------------------------------------------------
    # Apply patch
    # ------------------------------------------------------------------
    try:
        modified_content = LineDiffEngine.apply_patch(original_content, body.patch)
    except Exception as exc:
        logger.exception("Patch apply failed for %s: %s", body.patch.file_path, exc)
        return PatchApplyResponse(
            success=False,
            file_path=body.patch.file_path,
            edit_type=edit_type.value,
            hunks_applied=0,
            error=str(exc),
        )

    # ------------------------------------------------------------------
    # Write patched content to disk
    # ------------------------------------------------------------------
    if edit_type == EditType.DELETE:
        if file_path.exists():
            file_path.unlink()
        logger.info("Patch (DELETE) applied: %s", file_path)
    else:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(modified_content, encoding="utf-8")
        logger.info(
            "Patch (%s) applied: %s (%d hunks)",
            edit_type.value,
            file_path,
            len(body.patch.hunks),
        )

    # ------------------------------------------------------------------
    # Generate unified diff for the DiffViewer response
    # ------------------------------------------------------------------
    unified_diff = LineDiffEngine.generate_unified_diff(
        original_content,
        modified_content,
        file_path=body.patch.file_path,
    ) if edit_type != EditType.DELETE else ""

    return PatchApplyResponse(
        success=True,
        file_path=body.patch.file_path,
        edit_type=edit_type.value,
        hunks_applied=len(body.patch.hunks),
        backup_path=backup_path,
        diff=unified_diff or None,
    )


@router.post(
    "/reject",
    response_model=PatchRejectResponse,
    summary="Reject and discard a pending code patch",
    description="Discards the patch without applying it. Purely a no-op on disk — used to record the developer's rejection decision in logs.",
)
async def reject_patch(body: PatchRejectRequest) -> PatchRejectResponse:
    """Reject a patch — no disk changes made."""
    logger.info(
        "Patch rejected: patch_id=%s reason=%s",
        body.patch_id or "unknown",
        body.reason,
    )
    return PatchRejectResponse(
        success=True,
        message=f"Patch rejected: {body.reason}",
    )
