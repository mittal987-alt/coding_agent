class EmbeddingRecord:

    id: str

    chunk: str

    symbol: str

    file: str

    vector: list[float]



class EmbeddingIndex:

    vectors = {}