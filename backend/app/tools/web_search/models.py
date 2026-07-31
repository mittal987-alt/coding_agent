from enum import Enum

from pydantic import BaseModel


class SearchType(str, Enum):

    GENERAL = "general"

    DOCUMENTATION = "documentation"

    GITHUB = "github"

    STACKOVERFLOW = "stackoverflow"

    PACKAGE = "package"

    SECURITY = "security"


class SearchRequest(BaseModel):

    query: str

    search_type: SearchType = SearchType.GENERAL

    max_results: int = 5


class SearchResult(BaseModel):

    title: str

    url: str

    snippet: str

    content: str | None = None


class SearchResponse(BaseModel):

    results: list[SearchResult]