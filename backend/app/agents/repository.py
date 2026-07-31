"""
Repository Agent

Provides repository information
to other AI agents.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.graph.state import AgentState


class RepositoryAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(

            llm=llm,

            name="Repository",

        )

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        repository = state.repository

        state.repository_summary = {

            "workspace": state.workspace_id,

            "files": repository.files.count(),

            "symbols": repository.symbols.count(),

            "chunks": repository.embeddings.count(),

            "languages": repository.metadata.languages,

        }

        return state

    def get_file(
        self,
        state: AgentState,
        path: str,
    ):

        return state.repository.files.get(path)

    def get_symbol(
        self,
        state: AgentState,
        name: str,
    ):

        return state.repository.symbols.find(name)

    def get_related_symbols(
        self,
        state: AgentState,
        symbol: str,
    ):

        return state.repository.graph.neighbors(symbol)

    def get_imports(
        self,
        state: AgentState,
        file: str,
    ):

        return state.repository.graph.imports(file)

    def get_callers(
        self,
        state: AgentState,
        symbol: str,
    ):

        return state.repository.graph.callers(symbol)

    def get_callees(
        self,
        state: AgentState,
        symbol: str,
    ):

        return state.repository.graph.callees(symbol)

    def search_files(
        self,
        state: AgentState,
        keyword: str,
    ):

        return state.repository.files.search(keyword)