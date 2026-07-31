class PullRequestService:

    def create(

        self,

        repo,

        title,

        body,

        head,

        base,

    ):

        return repo.create_pull(

            title=title,

            body=body,

            head=head,

            base=base,

        )

    def comment(

        self,

        repo,

        number,

        body,

    ):

        pr = repo.get_pull(number)

        pr.create_issue_comment(body)