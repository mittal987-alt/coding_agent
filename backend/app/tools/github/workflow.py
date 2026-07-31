class WorkflowService:

    def latest_runs(

        self,

        repo,

    ):

        return repo.get_workflow_runs()