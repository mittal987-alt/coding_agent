from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class GitHubAction(str, Enum):

    CLONE = "clone"

    CREATE_BRANCH = "create_branch"

    CREATE_PULL_REQUEST = "create_pull_request"

    COMMENT_PULL_REQUEST = "comment_pull_request"

    CREATE_ISSUE = "create_issue"

    GET_WORKFLOW_STATUS = "get_workflow_status"


class GitHubRequest(BaseModel):

    action: GitHubAction

    owner: str

    repository: str

    branch: str | None = None

    title: str | None = None

    body: str | None = None

    head: str | None = None

    base: str | None = None

    issue_number: int | None = None

    pull_number: int | None = None


class GitHubResult(BaseModel):

    success: bool

    output: str

    metadata: dict = {}