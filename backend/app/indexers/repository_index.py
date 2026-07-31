from pydantic import BaseModel

from .metadata import RepositoryMetadata

from .file_index import FileIndex

from .symbol_index import SymbolIndex

from .graph_index import GraphIndex

from .embedding_index import EmbeddingIndex


class RepositoryIndex(BaseModel):

    metadata: RepositoryMetadata

    files: FileIndex

    symbols: SymbolIndex

    graph: GraphIndex

    embeddings: EmbeddingIndex