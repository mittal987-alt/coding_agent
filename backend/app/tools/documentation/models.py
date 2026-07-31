from enum import Enum

from pydantic import BaseModel


class DocumentationProvider(str, Enum):

    FASTAPI = "fastapi"

    REACT = "react"

    NEXTJS = "nextjs"

    FLUTTER = "flutter"

    PYTORCH = "pytorch"

    SQLALCHEMY = "sqlalchemy"

    LANGCHAIN = "langchain"

    LANGGRAPH = "langgraph"

    DOCKER = "docker"

    KUBERNETES = "kubernetes"


class DocumentationRequest(BaseModel):

    provider: DocumentationProvider

    query: str

    version: str | None = None


class DocumentationChunk(BaseModel):

    title: str

    source: str

    content: str


class DocumentationResponse(BaseModel):

    chunks: list[DocumentationChunk]