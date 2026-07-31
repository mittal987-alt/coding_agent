from app.tools.base import (
    BaseTool,
    ToolResult,
)

from .models import GitHubRequest
from .client import GitHubClient
from .repository import RepositoryService
from .pull_requests import PullRequestService
from .issues import IssueService
from .workflows import WorkflowService


class GitHubTool(BaseTool):

    name = "github"

    description = "Interact with GitHub repositories."

    def __init__(

        self,

        token: str,

    ):

        self.client = GitHubClient(token)

        self.repositories = RepositoryService()

        self.pull_requests = PullRequestService()

        self.issues = IssueService()

        self.workflows = WorkflowService()

    async def execute(

        self,

        **kwargs,

    ):

        request = GitHubRequest(**kwargs)

        repo = self.client.repo(

            request.owner,

            request.repository,

        )

        if request.action == "create_pull_request":

            pr = self.pull_requests.create(

                repo,

                request.title,

                request.body,

                request.head,

                request.base,

            )

            return ToolResult(

                success=True,

                output=pr.html_url,

            )

        raise NotImplementedError(
            request.action
        )