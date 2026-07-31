from pydantic import BaseModel


class IndexedFile(BaseModel):

    path: str

    language: str

    sha256: str

    size: int

    lines: int

    modified: float

    indexed: bool = False


class FileIndex(BaseModel):

    files: dict[str, IndexedFile] = {}


    def add(
    self,
    file,
):
    self.files[file.path] = file


    def get(
    self,
    path,
):
    return self.files.get(path)