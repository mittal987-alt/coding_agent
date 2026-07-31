from enum import Enum
from pydantic import BaseModel


class EdgeType(str, Enum):

    IMPORT = "import"

    CALL = "call"

    CONTAINS = "contains"

    INHERITS = "inherits"

    USES = "uses"


class GraphNode(BaseModel):

    id: str

    name: str

    type: str

    file: str


class GraphEdge(BaseModel):

    source: str

    target: str

    relation: EdgeType


class RepositoryGraph(BaseModel):

    nodes: list[GraphNode] = []

    edges: list[GraphEdge] = []