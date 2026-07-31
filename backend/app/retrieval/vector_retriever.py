class VectorRetriever:

    def __init__(
        self,
        retriever,
    ):

        self.retriever = retriever

    def retrieve(
        self,
        query: str,
        top_k: int = 15,
    ):

        return self.retriever.retrieve(
            query,
            top_k,
        )