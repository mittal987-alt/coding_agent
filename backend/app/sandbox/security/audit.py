from datetime import datetime


class AuditLogger:

    def log(

        self,

        request,

        result,

    ):

        print(

            {

                "timestamp": datetime.utcnow().isoformat(),

                "command": request.command,

                "decision": result.decision,

                "reason": result.reason,

            }

        )