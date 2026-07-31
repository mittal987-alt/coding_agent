from datetime import datetime

from pydantic import BaseModel


class IndexStats(BaseModel):

    files: int = 0

    symbols: int = 0

    chunks: int = 0

    imports: int = 0

    calls: int = 0

    classes: int = 0

    functions: int = 0

    embeddings: int = 0


class RepositoryMetadata(BaseModel):

    workspace_id: int

    repository_name: str

    indexed_at: datetime

    last_scan: datetime

    repository_hash: str

    languages: dict[str, int]

    stats: IndexStats