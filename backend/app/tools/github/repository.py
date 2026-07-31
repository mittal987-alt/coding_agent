class RepositoryService:

    def create_branch(

        self,

        repo,

        branch,

        source="main",

    ):

        source_ref = repo.get_git_ref(

            f"heads/{source}"

        )

        repo.create_git_ref(

            ref=f"refs/heads/{branch}",

            sha=source_ref.object.sha,

        )