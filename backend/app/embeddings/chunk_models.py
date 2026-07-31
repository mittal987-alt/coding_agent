
from pydantic import BaseModel


class CodeChunk(BaseModel):

    id: str

    workspace_id: int

    file: str

    language: str

    symbol: str | None = None

    kind: str | None = None

    start_line: int

    end_line: int

    content: str

    metadata: dict = {}