class IssueService:

    def create(

        self,

        repo,

        title,

        body,

    ):

        return repo.create_issue(

            title=title,

            body=body,

        )