from .base import SandboxException


class ExecutionException(SandboxException):

    pass


class BuildFailed(ExecutionException):

    pass


class TestFailed(ExecutionException):

    pass


class CommandExecutionFailed(ExecutionException):

    pass