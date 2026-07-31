from app.tools.base import ToolResult

from .dispatcher import ToolDispatcher
from .metrics import MetricsCollector
from .retries import RetryPolicy
from .audit import AuditLogger
from .approvals import ApprovalManager


class ToolExecutor:

    def __init__(

        self,

        registry,

    ):

        self.dispatcher = ToolDispatcher(registry)

        self.metrics = MetricsCollector()

        self.retry = RetryPolicy()

        self.audit = AuditLogger()

        self.approvals = ApprovalManager()

    async def execute(

        self,

        request,

    ):

        tool = self.dispatcher.dispatch(

            request.tool

        )

        await self.approvals.check(

            tool

        )

        start = self.metrics.start()

        async def run():

            return await tool.execute(

                **request.parameters

            )

        result = await self.retry.execute(run)

        duration = self.metrics.finish(start)

        self.audit.log(

            request,

            result,

        )

        return ToolResult(

            success=result.success,

            output=result.output,

            metadata={

                **result.metadata,

                "duration": duration,

            },

        )