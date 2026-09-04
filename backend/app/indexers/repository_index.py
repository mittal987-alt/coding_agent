from pydantic import BaseModel, ConfigDict

from .models import RepositoryMetadata
from .file_index import FileIndex
from .symbol_index import SymbolIndex
from .graph_index import GraphIndex
from .embedding_index import EmbeddingIndex


class RepositoryIndex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metadata: RepositoryMetadata
    files: FileIndex
    symbols: SymbolIndex
    graph: GraphIndex
    embeddings: EmbeddingIndex