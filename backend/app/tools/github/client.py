from github import Github


class GitHubClient:

    def __init__(

        self,

        token: str,

    ):

        self.client = Github(token)

    def repo(

        self,

        owner,

        repository,

    ):

        return self.client.get_repo(

            f"{owner}/{repository}"

        )