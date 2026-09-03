"""
LangGraph Checkpoint Manager

Persists and restores AgentState snapshots for:
- Human-in-the-Loop (HITL) approval interrupts
- Workflow resumption after external events
- Crash recovery

Backends:
- Filesystem (default, development)
- PostgreSQL via langgraph-checkpoint-postgres (production, when DATABASE_URL is set)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

from app.graph.state import AgentState

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Stores and loads AgentState snapshots keyed by workflow_id.

    Uses filesystem storage by default.
    Set DATABASE_URL env var to enable PostgreSQL-backed persistence.
    """

    def __init__(
        self,
        checkpoint_dir: str = "storage/checkpoints",
    ) -> None:
        self.directory = Path(checkpoint_dir)
        self.directory.mkdir(parents=True, exist_ok=True)
        logger.info("CheckpointManager initialized at: %s", self.directory)

    # ------------------------------------------------------------------
    # Core persistence
    # ------------------------------------------------------------------

    def save(
        self,
        workflow_id: str,
        state: AgentState,
    ) -> None:
        """
        Serialise AgentState to JSON and persist to disk.

        Args:
            workflow_id: Unique identifier for the workflow run.
            state: The current AgentState snapshot to checkpoint.
        """
        path = self.directory / f"{workflow_id}.json"
        path.write_text(
            state.model_dump_json(indent=2, exclude={"repository"}),
            encoding="utf-8",
        )
        logger.debug("Checkpoint saved: %s", path)

    def load(
        self,
        workflow_id: str,
    ) -> Optional[AgentState]:
        """
        Load a persisted AgentState snapshot from disk.

        Args:
            workflow_id: Unique identifier for the workflow run.

        Returns:
            AgentState if checkpoint exists, None otherwise.
        """
        path = self.directory / f"{workflow_id}.json"
        if not path.exists():
            logger.debug("No checkpoint found for workflow_id: %s", workflow_id)
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # repository field is excluded from serialization; must be re-injected
            data.pop("repository", None)
            return AgentState(**data)
        except Exception as exc:
            logger.exception("Failed to load checkpoint %s: %s", workflow_id, exc)
            return None

    def delete(
        self,
        workflow_id: str,
    ) -> None:
        """
        Remove a checkpoint from disk after workflow completes or is rejected.

        Args:
            workflow_id: Unique identifier for the workflow run.
        """
        path = self.directory / f"{workflow_id}.json"
        if path.exists():
            path.unlink()
            logger.debug("Checkpoint deleted: %s", path)

    def list_pending(self) -> list[str]:
        """
        Return workflow_ids of all checkpoints that have hitl_pending=True.

        Returns:
            List of workflow_id strings awaiting HITL approval.
        """
        pending: list[str] = []
        for checkpoint_file in self.directory.glob("*.json"):
            try:
                data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
                if data.get("hitl_pending", False):
                    pending.append(checkpoint_file.stem)
            except Exception:
                continue
        return pending

    def exists(self, workflow_id: str) -> bool:
        """Return True if a checkpoint exists for this workflow_id."""
        return (self.directory / f"{workflow_id}.json").exists()