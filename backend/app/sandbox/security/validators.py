from abc import ABC, abstractmethod

from .models import SecurityDecision, SecurityResult

class BaseValidator(ABC):

    @abstractmethod
    async def validate(

        self,

        request,



    ):

        ...



class CommandValidator(

    BaseValidator,

):

    async def validate(

        self,

        request,

    ):

        for blocked in BLOCKED_COMMANDS:

            if blocked in request.command:

                return SecurityResult(

                    decision=SecurityDecision.DENY,

                    reason=f"Blocked command: {blocked}",

                )

        return SecurityResult(

            decision=SecurityDecision.ALLOW,

        )