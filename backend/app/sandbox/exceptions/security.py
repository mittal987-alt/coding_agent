from .base import SandboxException


class SecurityViolation(SandboxException):

    pass


class CommandBlocked(SecurityViolation):

    pass


class NetworkAccessDenied(SecurityViolation):

    pass


class SecretLeakDetected(SecurityViolation):

    pass