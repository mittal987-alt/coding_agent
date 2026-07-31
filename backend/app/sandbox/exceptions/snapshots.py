class SnapshotException(SandboxException):

    pass


class SnapshotCreateFailed(SnapshotException):

    pass


class SnapshotRestoreFailed(SnapshotException):

    pass