# complexity.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Goal, TaskGraph


class ComplexityLevel(str, Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class ComplexityReport:
    complexity: ComplexityLevel
    risk: RiskLevel

    estimated_hours: float

    estimated_tokens: int

    estimated_cost: float

    recommended_agents: int

    parallel_execution: bool

    requires_human_approval: bool


class ComplexityAnalyzer:
    """
    Estimates execution complexity.

    Used by:

    - Planner
    - Scheduler
    - LangGraph
    - Human approval
    """

    ENTERPRISE_KEYWORDS = {
        "microservice",
        "kubernetes",
        "terraform",
        "aws",
        "azure",
        "gcp",
        "distributed",
    }

    AI_KEYWORDS = {
        "llm",
        "rag",
        "langgraph",
        "pytorch",
        "tensorflow",
        "transformer",
        "vision",
        "agent",
    }

    def analyze(
        self,
        goal: Goal,
        graph: TaskGraph,
    ) -> ComplexityReport:

        score = 0

        task_count = len(graph.tasks)

        score += task_count

        if goal.framework:
            score += 2

        if goal.language:
            score += 1

        score += len(goal.requirements)

        text = (
            f"{goal.title} "
            f"{goal.description} "
            f"{' '.join(goal.requirements)}"
        ).lower()

        for word in self.ENTERPRISE_KEYWORDS:
            if word in text:
                score += 5

        for word in self.AI_KEYWORDS:
            if word in text:
                score += 4

        estimated_hours = sum(
            task.estimated_minutes
            for task in graph.tasks
        ) / 60

        estimated_tokens = max(
            3000,
            task_count * 2500,
        )

        estimated_cost = round(
            estimated_tokens / 1000 * 0.02,
            2,
        )

        if score <= 10:
            complexity = ComplexityLevel.TRIVIAL

        elif score <= 20:
            complexity = ComplexityLevel.SIMPLE

        elif score <= 40:
            complexity = ComplexityLevel.MODERATE

        elif score <= 70:
            complexity = ComplexityLevel.COMPLEX

        else:
            complexity = ComplexityLevel.ENTERPRISE

        if complexity in (
            ComplexityLevel.TRIVIAL,
            ComplexityLevel.SIMPLE,
        ):
            risk = RiskLevel.LOW

        elif complexity == ComplexityLevel.MODERATE:
            risk = RiskLevel.MEDIUM

        elif complexity == ComplexityLevel.COMPLEX:
            risk = RiskLevel.HIGH

        else:
            risk = RiskLevel.CRITICAL

        recommended_agents = min(
            8,
            max(
                1,
                task_count // 4,
            ),
        )

        parallel = task_count >= 5

        approval = (
            complexity == ComplexityLevel.ENTERPRISE
            or risk == RiskLevel.CRITICAL
        )

        return ComplexityReport(
            complexity=complexity,
            risk=risk,
            estimated_hours=estimated_hours,
            estimated_tokens=estimated_tokens,
            estimated_cost=estimated_cost,
            recommended_agents=recommended_agents,
            parallel_execution=parallel,
            requires_human_approval=approval,
        )