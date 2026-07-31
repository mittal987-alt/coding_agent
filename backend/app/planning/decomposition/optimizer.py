# optimizer.py
from __future__ import annotations

from collections import defaultdict

from .graph import DependencyGraph
from .models import TaskGraph, TaskPriority


class TaskGraphOptimizer:
    """
    Optimizes a validated TaskGraph for execution.

    Current optimizations:
    - Priority ordering
    - Parallel execution stages
    - Agent workload balancing
    """

    PRIORITY_SCORE = {
        TaskPriority.CRITICAL: 4,
        TaskPriority.HIGH: 3,
        TaskPriority.MEDIUM: 2,
        TaskPriority.LOW: 1,
    }

    def optimize(
        self,
        graph: TaskGraph,
    ) -> TaskGraph:

        dag = DependencyGraph(graph)

        execution_levels = dag.execution_levels()

        optimized_tasks = []

        stage = 0

        for level in execution_levels:

            level = sorted(
                level,
                key=lambda task: (
                    -self.PRIORITY_SCORE[task.priority],
                    task.estimated_minutes,
                    task.title,
                ),
            )

            for task in level:

                task.metadata["execution_stage"] = stage

                optimized_tasks.append(task)

            stage += 1

        graph.tasks = optimized_tasks

        self._balance_agents(graph)

        return graph

    def _balance_agents(
        self,
        graph: TaskGraph,
    ) -> None:
        """
        Compute workload statistics.

        These statistics can later be used by the
        scheduler to distribute work.
        """

        workloads = defaultdict(int)

        for task in graph.tasks:

            workloads[task.agent] += task.estimated_minutes

        graph.goal.metadata["agent_workloads"] = dict(workloads)