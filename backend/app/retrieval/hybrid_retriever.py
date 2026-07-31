"""
Hybrid Retriever

Coordinates the complete retrieval pipeline.

Pipeline

Query
   │
   ▼
Query Analyzer
   │
   ▼
Vector Retriever
   +
Symbol Retriever
   +
Graph Retriever
   │
   ▼
Result Merger
   │
   ▼
Hybrid Ranker
   │
   ▼
Context Expander
   │
   ▼
Prompt Builder
"""

from __future__ import annotations

from app.indexers.repository_index import RepositoryIndex

from app.retrieval.query_analyzer import (
    QueryAnalyzer,
    QueryIntent,
)

from app.retrieval.vector_retriever import (
    VectorRetriever,
)

from app.retrieval.symbol_retriever import (
    SymbolRetriever,
)

from app.retrieval.graph_retriever import (
    GraphRetriever,
)

from app.retrieval.result_merger import (
    ResultMerger,
)

from app.retrieval.ranker import (
    HybridRanker,
)

from app.retrieval.context_expander import (
    ContextExpander,
)

from app.retrieval.prompt_builder import (
    PromptBuilder,
)


class HybridRetriever:

    """
    Complete repository retrieval pipeline.
    """

    def __init__(
        self,
        repository: RepositoryIndex,
        vector_retriever: VectorRetriever,
    ):

        self.repository = repository

        self.query_analyzer = QueryAnalyzer()

        self.vector = vector_retriever

        self.symbol = SymbolRetriever(repository)

        self.graph = GraphRetriever(repository)

        self.merger = ResultMerger()

        self.ranker = HybridRanker(repository)

        self.expander = ContextExpander(repository)

        self.prompt_builder = PromptBuilder()

    def retrieve(
        self,
        query: str,
    ) -> str:

        intent = self.query_analyzer.analyze(
            query
        )

        vector_results = self.vector.retrieve(
            query,
            top_k=self.vector_limit(intent),
        )

        symbol_results = self.symbol.retrieve(
            query,
        )

        graph_results = []

        if symbol_results:

            for result in symbol_results:

                graph_results.extend(

                    self.graph.retrieve(

                        result.chunk.symbol,

                    )

                )

        merged = self.merger.merge(

            vector_results,

            symbol_results,

            graph_results,

        )

        ranked = self.ranker.rank(

            query,

            merged,

        )

        expanded = self.expander.expand(

            ranked,

        )

        return self.prompt_builder.build(

            query,

            expanded,

        )

    def vector_limit(
        self,
        intent: QueryIntent,
    ) -> int:

        if intent == QueryIntent.FIND_SYMBOL:
            return 5

        if intent == QueryIntent.EXPLAIN:
            return 20

        if intent == QueryIntent.IMPLEMENT:
            return 25

        if intent == QueryIntent.DEBUG:
            return 30

        return 15