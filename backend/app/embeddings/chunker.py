"""
Smart semantic chunker.

Converts parsed symbols into CodeChunks suitable for embedding.
"""

from pathlib import Path
from typing import List

from app.embeddings.chunk_models import CodeChunk
from app.parser.base.symbol import Symbol


class SmartChunker:

    """
    Builds semantic chunks from parser symbols.

    Every function/class becomes a chunk.

    Large symbols are automatically split into
    overlapping subchunks.
    """

    def __init__(
        self,
        max_lines: int = 150,
        overlap: int = 20,
    ):

        self.max_lines = max_lines
        self.overlap = overlap

    def chunk_file(
        self,
        workspace_id: int,
        file_path: Path,
        symbols: List[Symbol],
    ) -> List[CodeChunk]:

        source = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        lines = source.splitlines()

        chunks: List[CodeChunk] = []

        if not symbols:
            chunks.append(
                self._whole_file_chunk(
                    workspace_id,
                    file_path,
                    lines,
                )
            )
            return chunks

        for symbol in symbols:

            chunks.extend(

                self._chunk_symbol(

                    workspace_id,

                    file_path,

                    symbol,

                    lines,
                )

            )

        return chunks

    def _chunk_symbol(
        self,
        workspace_id: int,
        file_path: Path,
        symbol: Symbol,
        lines: List[str],
    ) -> List[CodeChunk]:

        start = symbol.start_line - 1
        end = symbol.end_line

        symbol_lines = lines[start:end]

        if len(symbol_lines) <= self.max_lines:

            return [

                CodeChunk(

                    id=f"{file_path}:{symbol.name}",

                    workspace_id=workspace_id,

                    file=str(file_path),

                    language=symbol.language,

                    symbol=symbol.name,

                    kind=symbol.kind.value,

                    start_line=symbol.start_line,

                    end_line=symbol.end_line,

                    content="\n".join(symbol_lines),

                    metadata={
                        "parent": symbol.parent,
                        "signature": symbol.signature,
                    },
                )

            ]

        return self._split_large_symbol(

            workspace_id,

            file_path,

            symbol,

            symbol_lines,
        )

    def _split_large_symbol(
        self,
        workspace_id: int,
        file_path: Path,
        symbol: Symbol,
        symbol_lines: List[str],
    ) -> List[CodeChunk]:

        chunks = []

        step = self.max_lines - self.overlap

        start = 0

        index = 0

        while start < len(symbol_lines):

            end = min(

                start + self.max_lines,

                len(symbol_lines),

            )

            content = "\n".join(

                symbol_lines[start:end]

            )

            chunks.append(

                CodeChunk(

                    id=f"{file_path}:{symbol.name}:{index}",

                    workspace_id=workspace_id,

                    file=str(file_path),

                    language=symbol.language,

                    symbol=symbol.name,

                    kind=symbol.kind.value,

                    start_line=symbol.start_line + start,

                    end_line=symbol.start_line + end - 1,

                    content=content,

                    metadata={

                        "part": index,

                        "parent": symbol.parent,

                    },
                )

            )

            index += 1

            start += step

        return chunks

    def _whole_file_chunk(
        self,
        workspace_id: int,
        file_path: Path,
        lines: List[str],
    ) -> CodeChunk:

        return CodeChunk(

            id=str(file_path),

            workspace_id=workspace_id,

            file=str(file_path),

            language=file_path.suffix.replace(".", ""),

            symbol=None,

            kind="file",

            start_line=1,

            end_line=len(lines),

            content="\n".join(lines),

            metadata={},
        )