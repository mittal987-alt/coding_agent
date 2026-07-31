from pydantic import BaseModel


class FunctionSymbol(BaseModel):
    name: str
    class_name: Optional[str]
    parameters: list[str]
    start_line: int
    end_line: int


class ClassSymbol(BaseModel):
    name: str
    methods: list[str]
    start_line: int
    end_line: int

class ImportSymbol(BaseModel):
    module: str


class ParsedFile(BaseModel):
    path: str
    language: str
    functions: list[FunctionSymbol]
    classes: list[ClassSymbol]
    imports: list[ImportSymbol]