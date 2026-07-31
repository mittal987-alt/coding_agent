class IndexBuilder:

    def __init__(
        self,
        scanner,
        parser,
        graph_builder,
        embedding_builder,
    ):
        self.scanner = scanner
        self.parser = parser
        self.graph_builder = graph_builder
        self.embedding_builder = embedding_builder

    def build(
        self,
        workspace,
    ):
        ...         