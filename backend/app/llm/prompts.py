# LLM Prompts
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# Prompt Types
# ============================================================


class PromptType(str, Enum):
    """
    Supported prompt categories.
    """

    SYSTEM = "system"

    CHAT = "chat"

    PLANNING = "planning"

    CODING = "coding"

    REVIEW = "review"

    DEBUGGING = "debugging"

    REFACTORING = "refactoring"

    TESTING = "testing"

    DOCUMENTATION = "documentation"

    RAG = "rag"

    TOOL = "tool"

    MEMORY = "memory"


# ============================================================
# Prompt Template
# ============================================================


@dataclass(slots=True)
class PromptTemplate:
    """
    Prompt template with placeholders.
    """

    name: str

    prompt_type: PromptType

    template: str

    description: str = ""

    variables: list[str] = field(
        default_factory=list,
    )

    version: str = "1.0"

    def render(
        self,
        **kwargs: str,
    ) -> str:
        """
        Render template.
        """

        result = self.template

        for variable in self.variables:

            value = kwargs.get(variable, "")

            result = result.replace(
                f"{{{{{variable}}}}}",
                str(value),
            )

        return result


# ============================================================
# Prompt Registry
# ============================================================


class PromptRegistry:
    """
    Stores prompt templates.
    """

    def __init__(self) -> None:

        self._templates: dict[
            str,
            PromptTemplate,
        ] = {}

    def register(
        self,
        template: PromptTemplate,
    ) -> None:

        self._templates[
            template.name
        ] = template

    def get(
        self,
        name: str,
    ) -> PromptTemplate:

        return self._templates[name]

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._templates

    def list(
        self,
    ) -> list[str]:

        return sorted(
            self._templates.keys()
        )

    def remove(
        self,
        name: str,
    ) -> None:

        self._templates.pop(
            name,
            None,
        )


# ============================================================
# Prompt Builder
# ============================================================


class PromptBuilder:
    """
    Composes prompts from reusable parts.
    """

    def __init__(
        self,
        registry: PromptRegistry,
    ) -> None:

        self.registry = registry

    def build(
        self,
        name: str,
        **kwargs: str,
    ) -> str:

        template = self.registry.get(name)

        return template.render(
            **kwargs
        )

    def combine(
        self,
        *parts: str,
    ) -> str:

        return "\n\n".join(
            p.strip()
            for p in parts
            if p.strip()
        )


# ============================================================
# Built-in Templates
# ============================================================


DEFAULT_SYSTEM_PROMPT = """\
You are an autonomous AI Software Engineer.

Responsibilities:

- Analyze repositories
- Write production-quality code
- Review code
- Fix bugs
- Generate tests
- Plan software architecture
- Use available tools responsibly
- Ask for clarification only when necessary
- Produce concise, correct, maintainable solutions.
"""


PLANNING_PROMPT = """\
Goal:

{{goal}}

Context:

{{context}}

Generate an execution plan.

Requirements:

- Break into steps
- Identify dependencies
- Estimate complexity
- Highlight risks
"""


CODING_PROMPT = """\
Task:

{{task}}

Repository Context:

{{repository}}

Relevant Memory:

{{memory}}

Write production-ready code.

Requirements:

- Clean architecture
- Type hints
- Error handling
- Logging
- Tests where appropriate
"""


REVIEW_PROMPT = """\
Review the following code.

{{code}}

Evaluate:

- Bugs
- Performance
- Security
- Maintainability
- Style
- Suggested improvements
"""


DEBUGGING_PROMPT = """\
Problem:

{{problem}}

Logs:

{{logs}}

Code:

{{code}}

Identify the root cause.

Explain your reasoning.

Provide a fix.
"""


RAG_PROMPT = """\
Question:

{{question}}

Retrieved Context:

{{context}}

Answer using only supported evidence.
"""


# ============================================================
# Factory
# ============================================================


def create_default_registry() -> PromptRegistry:
    """
    Create registry with default templates.
    """

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="system",
            prompt_type=PromptType.SYSTEM,
            template=DEFAULT_SYSTEM_PROMPT,
        )
    )

    registry.register(
        PromptTemplate(
            name="planning",
            prompt_type=PromptType.PLANNING,
            template=PLANNING_PROMPT,
            variables=[
                "goal",
                "context",
            ],
        )
    )

    registry.register(
        PromptTemplate(
            name="coding",
            prompt_type=PromptType.CODING,
            template=CODING_PROMPT,
            variables=[
                "task",
                "repository",
                "memory",
            ],
        )
    )

    registry.register(
        PromptTemplate(
            name="review",
            prompt_type=PromptType.REVIEW,
            template=REVIEW_PROMPT,
            variables=[
                "code",
            ],
        )
    )

    registry.register(
        PromptTemplate(
            name="debugging",
            prompt_type=PromptType.DEBUGGING,
            template=DEBUGGING_PROMPT,
            variables=[
                "problem",
                "logs",
                "code",
            ],
        )
    )

    registry.register(
        PromptTemplate(
            name="rag",
            prompt_type=PromptType.RAG,
            template=RAG_PROMPT,
            variables=[
                "question",
                "context",
            ],
        )
    )

    return registry