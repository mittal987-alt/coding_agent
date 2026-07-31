"""
Prompt Builder

Converts expanded retrieval context into
an optimized prompt for the LLM.
"""

from __future__ import annotations

from app.retrieval.models import RetrievalResult


class PromptBuilder:

    """
    Builds structured prompts for the LLM.

    Sections:

    - User Request
    - Repository Summary
    - Relevant Symbols
    - Code Context
    - Relationships
    - Instructions
    """

    def build(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> str:

        sections = []

        sections.append(
            self.user_section(query)
        )

        sections.append(
            self.repository_section(results)
        )

        sections.append(
            self.symbol_section(results)
        )

        sections.append(
            self.code_section(results)
        )

        sections.append(
            self.relationship_section(results)
        )

        sections.append(
            self.instructions()
        )

        return "\n\n".join(sections)

    def user_section(
        self,
        query: str,
    ) -> str:

        return (
            "## USER REQUEST\n"
            f"{query}"
        )

    def repository_section(
        self,
        results: list[RetrievalResult],
    ) -> str:

        files = sorted({
            r.chunk.file
            for r in results
        })

        text = ["## REPOSITORY FILES"]

        for file in files:

            text.append(
                f"- {file}"
            )

        return "\n".join(text)

    def symbol_section(
        self,
        results: list[RetrievalResult],
    ) -> str:

        text = ["## SYMBOLS"]

        for result in results:

            symbol = result.chunk.symbol

            if symbol:

                text.append(
                    f"- {symbol}"
                )

        return "\n".join(text)

    def code_section(
        self,
        results: list[RetrievalResult],
    ) -> str:

        text = ["## CODE CONTEXT"]

        for result in results:

            chunk = result.chunk

            text.append(
                f"\n### {chunk.file}"
            )

            text.append(
                f"Lines {chunk.start_line}-{chunk.end_line}"
            )

            text.append("```")

            text.append(
                chunk.content
            )

            text.append("```")

        return "\n".join(text)

    def relationship_section(
        self,
        results: list[RetrievalResult],
    ) -> str:

        text = ["## RETRIEVAL INFORMATION"]

        for result in results:

            text.append(
                f"- {result.chunk.symbol}"
            )

            text.append(
                f"  Score: {result.metadata.get('final_score', result.score):.3f}"
            )

            text.append(
                f"  Source: {', '.join(result.metadata.get('sources', []))}"
            )

        return "\n".join(text)

    def instructions(self) -> str:

        return """
## INSTRUCTIONS

You are an expert software engineer.

Answer using ONLY the provided repository context.

If information is missing,
state that explicitly.

When explaining code:

- Explain execution flow
- Mention related classes
- Mention dependencies
- Mention function calls
- Suggest improvements if appropriate

Never invent functions or files.
""".strip()