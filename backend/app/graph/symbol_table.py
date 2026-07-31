from asyncio import graph
from app.graph.models import EdgeType
class SymbolTable:

    def __init__(self):

        self.table = {}

    def register(
        self,
        symbol,
    ):

        self.table[
            symbol.name
        ] = symbol

    def resolve(
        self,
        name,
    ):

        return self.table.get(name)

    
    graph.add_edge(

    source="login",

    target="generate",

    relation=EdgeType.CALL,
)