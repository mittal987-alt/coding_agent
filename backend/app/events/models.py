from __future__ import annotations

from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class EventType(str, Enum):

    WORKFLOW_STARTED = "workflow_started"

    WORKFLOW_FINISHED = "workflow_finished"

    AGENT_STARTED = "agent_started"

    AGENT_FINISHED = "agent_finished"

    TERMINAL_OUTPUT = "terminal_output"

    TEST_STARTED = "test_started"

    TEST_FINISHED = "test_finished"

    CHECKPOINT = "checkpoint"

    ERROR = "error"


class WorkflowEvent(BaseModel):

    workflow_id: str

    event: EventType

    agent: str | None = None

    message: str

    timestamp: datetime