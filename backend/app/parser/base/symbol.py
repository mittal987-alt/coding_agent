from enum import Enum
from pydantic import BaseModel


class SymbolKind(str, Enum):

    FUNCTION = "function"

    CLASS = "class"

    METHOD = "method"

    VARIABLE = "variable"

    IMPORT = "import"

    CONSTANT = "constant"

    INTERFACE = "interface"

    ENUM = "enum"


class Symbol(BaseModel):

    id: str

    name: str

    kind: SymbolKind

    language: str

    file: str

    parent: str | None = None

    signature: str | None = None

    documentation: str | None = None

    start_line: int

    end_line: int