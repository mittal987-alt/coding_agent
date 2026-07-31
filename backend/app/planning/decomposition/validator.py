# validator.py
from __future__ import annotations

from collections import Counter
from typing import Iterable

from .graph import DependencyGraph
from .models import TaskGraph


SUPPORTED_AGENTS = {
    "planner",
    "coder",
    "reviewer",
    "tester",
    "terminal",
    "research",
    "repository",
    "documentation",
    "devops",
    "security",
}


class ValidationError(Exception):
    """Raised when a task graph is invalid."""


class TaskGraphValidator:
    """
    Validates task graphs before execution.
    """

    def validate(
        self,
        graph: TaskGraph,
    ) -> TaskGraph:

        self._validate_empty(graph)

        self._validate_duplicate_ids(graph)

        self._validate_dependencies(graph)

        self._validate_agents(graph)

        self._validate_cycles(graph)

        return graph

    def _validate_empty(
        self,
        graph: TaskGraph,
    ) -> None:

        if not graph.tasks:

            raise ValidationError(
                "Task graph contains no tasks."
            )

        for task in graph.tasks:

            if not task.title.strip():

                raise ValidationError(
                    f"Task {task.id} has an empty title."
                )

            if not task.description.strip():

                raise ValidationError(
                    f"Task {task.id} has an empty description."
                )

    def _validate_duplicate_ids(
        self,
        graph: TaskGraph,
    ) -> None:

        ids = [task.id for task in graph.tasks]

        duplicates = [

            task_id

            for task_id, count in Counter(ids).items()

            if count > 1

        ]

        if duplicates:

            raise ValidationError(

                f"Duplicate task ids: {duplicates}"

            )

    def _validate_dependencies(
        self,
        graph: TaskGraph,
    ) -> None:

        ids = {

            task.id

            for task in graph.tasks

        }

        for task in graph.tasks:

            for dependency in task.dependencies:

                if dependency == task.id:

                    raise ValidationError(

                        f"{task.id} depends on itself."

                    )

                if dependency not in ids:

                    raise ValidationError(

                        f"{task.id} references unknown dependency "
                        f"{dependency}"

                    )

    def _validate_agents(
        self,
        graph: TaskGraph,
    ) -> None:

        for task in graph.tasks:

            if task.agent not in SUPPORTED_AGENTS:

                raise ValidationError(

                    f"Unsupported agent '{task.agent}' "

                    f"for task '{task.title}'."

                )

    def _validate_cycles(
        self,
        graph: TaskGraph,
    ) -> None:

        dag = DependencyGraph(graph)

        # topological_sort raises if a cycle exists
        dag.topological_sort()