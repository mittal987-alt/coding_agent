from pydantic import BaseModel, Field


class IndexedFile(BaseModel):
    path: str
    language: str
    sha256: str
    size: int
    lines: int
    modified: float
    indexed: bool = False


class FileIndex(BaseModel):
    files: dict[str, IndexedFile] = Field(default_factory=dict)

    def add(self, file: IndexedFile) -> None:
        self.files[file.path] = file

    def get(self, path: str) -> IndexedFile | None:
        return self.files.get(path)