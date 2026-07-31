# engine.py
from __future__ import annotations

from collections import defaultdict, deque

from .models import TaskGraph, TaskNode, TaskStatus


class DependencyGraph:
    """
    Represents a DAG of executable tasks.
    """

    def __init__(self, graph: TaskGraph):
        self.graph = graph

        self.task_map: dict[str, TaskNode] = {
            task.id: task
            for task in graph.tasks
        }

        self.adjacency: dict[str, list[str]] = defaultdict(list)

        self.in_degree: dict[str, int] = {
            task.id: 0
            for task in graph.tasks
        }

        self._build()

    def _build(self) -> None:
        """
        Build adjacency list.
        """

        for task in self.graph.tasks:

            for dependency in task.dependencies:

                self.adjacency[dependency].append(
                    task.id
                )

                self.in_degree[task.id] += 1

    def topological_sort(self) -> list[TaskNode]:
        """
        Returns execution order.
        """

        queue = deque(
            [
                task_id
                for task_id, degree in self.in_degree.items()
                if degree == 0
            ]
        )

        order = []

        in_degree = self.in_degree.copy()

        while queue:

            current = queue.popleft()

            order.append(
                self.task_map[current]
            )

            for child in self.adjacency[current]:

                in_degree[child] -= 1

                if in_degree[child] == 0:

                    queue.append(child)

        if len(order) != len(self.task_map):

            raise ValueError(
                "Circular dependency detected."
            )

        return order

    def ready_tasks(self) -> list[TaskNode]:
        """
        Returns executable tasks.
        """

        ready = []

        for task in self.graph.tasks:

            if task.status != TaskStatus.PENDING:

                continue

            blocked = False

            for dependency in task.dependencies:

                dep = self.task_map[dependency]

                if dep.status != TaskStatus.COMPLETED:

                    blocked = True

                    break

            if not blocked:

                ready.append(task)

        return ready

    def mark_completed(
        self,
        task_id: str,
    ) -> None:

        self.task_map[
            task_id
        ].status = TaskStatus.COMPLETED

    def mark_running(
        self,
        task_id: str,
    ) -> None:

        self.task_map[
            task_id
        ].status = TaskStatus.RUNNING

    def pending_tasks(
        self,
    ) -> list[TaskNode]:

        return [

            task

            for task in self.graph.tasks

            if task.status == TaskStatus.PENDING

        ]

    def completed_tasks(
        self,
    ) -> list[TaskNode]:

        return [

            task

            for task in self.graph.tasks

            if task.status == TaskStatus.COMPLETED

        ]

    def failed_tasks(
        self,
    ) -> list[TaskNode]:

        return [

            task

            for task in self.graph.tasks

            if task.status == TaskStatus.FAILED

        ]

    def is_complete(self) -> bool:

        return all(

            task.status == TaskStatus.COMPLETED

            for task in self.graph.tasks

        )

    def execution_levels(self) -> list[list[TaskNode]]:
        """
        Groups tasks into levels that can run in parallel.
        """

        levels = []

        temp_degree = self.in_degree.copy()

        queue = deque(
            [
                task_id
                for task_id, degree in temp_degree.items()
                if degree == 0
            ]
        )

        while queue:

            level = []

            next_queue = deque()

            while queue:

                current = queue.popleft()

                level.append(
                    self.task_map[current]
                )

                for child in self.adjacency[current]:

                    temp_degree[child] -= 1

                    if temp_degree[child] == 0:

                        next_queue.append(child)

            levels.append(level)

            queue = next_queue

        return levels