from enum import Enum


class SnapshotStrategy(str, Enum):

    FULL = "full"

    INCREMENTAL = "incremental"

    COPY_ON_WRITE = "copy_on_write"