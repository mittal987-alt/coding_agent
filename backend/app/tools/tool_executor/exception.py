class ToolExecutionError(Exception):
    pass


class ToolTimeoutError(ToolExecutionError):
    pass


class ToolSecurityError(ToolExecutionError):
    pass


class ToolApprovalError(ToolExecutionError):
    pass