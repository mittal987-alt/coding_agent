from __future__ import annotations

from pydantic import BaseModel


class FinalResponse(BaseModel):

    summary: str

    completed_tasks: list[str]

    modified_files: list[str]

    review_status: str

    testing_status: str

    commit: str | None = None

    next_steps: list[str]