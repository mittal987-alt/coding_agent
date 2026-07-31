class AuditLogger:

    def log(

        self,

        request,

        result,

    ):

        print(

            request.tool,

            result.status,

        )