from datetime import datetime
from pydantic import BaseModel


class ResourceMetrics(BaseModel):

    timestamp: datetime

    cpu_percent: float

    memory_mb: float

    disk_mb: float

    network_rx_bytes: int

    network_tx_bytes: int

    process_count: int