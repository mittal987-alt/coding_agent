from datetime import datetime
from pydantic import BaseModel


class RepositoryFile(BaseModel):
    path: str
    extension: str
    language: str
    size: int
    lines: int
    sha256: str
    modified: datetime