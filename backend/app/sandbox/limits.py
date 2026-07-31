from dataclasses import dataclass


@dataclass
class ResourceLimits:

    cpu: float

    memory_mb: int

    timeout_seconds: int

    disk_mb: int 