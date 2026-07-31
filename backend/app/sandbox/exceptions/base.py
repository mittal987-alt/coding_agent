from enum import Enum


class ErrorSeverity(str, Enum):

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    CRITICAL = "critical"


class SandboxException(Exception):

    def __init__(

        self,

        message,

        code,

        severity=ErrorSeverity.ERROR,

        retryable=False,

        metadata=None,

    ):

        super().__init__(message)

        self.code = code

        self.severity = severity

        self.retryable = retryable

        self.metadata = metadata or {}