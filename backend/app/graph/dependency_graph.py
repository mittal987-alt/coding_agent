from app.graph.models import (
    GraphNode,
    GraphEdge,
    EdgeType,
)


class DependencyGraph:

    def __init__(self):

        self.nodes = {}

        self.edges = []

    def add_file(
        self,
        file,
    ):

        self.nodes[file] = GraphNode(

            id=file,

            name=file,

            kind="file",

            file=file,
        )

    def add_import(

        self,

        source,

        target,

    ):

        self.edges.append(

            GraphEdge(

                source=source,

                target=target,

                relation=EdgeType.IMPORT,
            )
        )
    
    graph = DependencyGraph()

    graph.add_file(
    "main.py"
)

    graph.add_file(
    "routes.py"
)

    graph.add_import(

    "main.py",

    "routes.py",
     
     ) 