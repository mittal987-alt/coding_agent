from dataclasses import dataclass
from datetime import datetime


@dataclass
class ServerSession:

    session_id: str

    client_name: str

    protocol_version: str

    connected_at: datetime

    authenticated: bool = False