"""
Task queue: FIFO queue with priority support.

AI creates tasks, workers pull from queue, execution emits events.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from .entities import Task


class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10
    CRITICAL = 20


class TaskQueue:
    """
    Priority queue of tasks waiting for execution.

    Workers request tasks from the queue based on their capabilities.
    """

    def __init__(self):
        self.tasks: List[Task] = []

    def enqueue(self, task: Task) -> None:
        """Add task to queue."""
        self.tasks.append(task)
        # Re-sort by priority (higher first, then by creation time)
        self.tasks.sort(
            key=lambda t: (-t.priority, t.created_at),
        )

    def dequeue(self) -> Optional[Task]:
        """Remove and return highest priority task."""
        if self.tasks:
            return self.tasks.pop(0)
        return None

    def peek(self) -> Optional[Task]:
        """View highest priority task without removing."""
        if self.tasks:
            return self.tasks[0]
        return None

    def find_tasks_for_worker(
        self, worker_capabilities: List[str], limit: int = 1
    ) -> List[Task]:
        """
        Find tasks that a worker can handle.

        Returns up to `limit` tasks that match worker capabilities,
        sorted by priority (highest first).
        """
        matching = []
        for task in self.tasks:
            if task.component_name in worker_capabilities and task.is_ready():
                matching.append(task)
                if len(matching) >= limit:
                    break
        return matching

    def get_size(self) -> int:
        """Get number of pending tasks."""
        return len(self.tasks)

    def get_priority_distribution(self) -> Dict[str, int]:
        """Get breakdown of tasks by priority."""
        distribution = {}
        for task in self.tasks:
            key = f"priority_{task.priority}"
            distribution[key] = distribution.get(key, 0) + 1
        return distribution

    def remove_task(self, task_id: str) -> bool:
        """Remove a specific task from queue."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_all_pending(self) -> List[Task]:
        """Get all pending tasks in order."""
        return [t for t in self.tasks if t.is_ready()]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize queue state."""
        return {
            "size": self.get_size(),
            "priority_distribution": self.get_priority_distribution(),
            "tasks": [t.to_dict() for t in self.tasks[:10]],  # First 10
        }
