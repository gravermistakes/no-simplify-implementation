"""
Core entities: Workers (executors), Tasks (work units), Capabilities (what workers can do).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from uuid import uuid4
from datetime import datetime


class WorkerState(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    FAILED = "failed"
    RECOVERING = "recovering"


class TaskState(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkerCapability:
    """Capability a worker can perform (components it understands)."""

    name: str  # e.g., "run_security_audit", "deploy_code"
    cost_per_execution: float  # tokens/resources
    success_rate: float = 0.95  # historical success
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Worker:
    """
    Independent executor in the worker pool.

    Workers are self-organizing: they advertise capabilities via components,
    request tasks from queue, execute deterministic patterns, emit events.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "worker"
    state: WorkerState = WorkerState.IDLE
    capabilities: List[WorkerCapability] = field(default_factory=list)

    # Current task being executed
    current_task_id: Optional[str] = None

    # Performance tracking
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    total_tokens_spent: float = 0.0
    total_value_produced: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if worker can accept new task."""
        return self.state == WorkerState.IDLE

    def get_success_rate(self) -> float:
        """Calculate worker's overall success rate."""
        total = self.total_tasks_completed + self.total_tasks_failed
        if total == 0:
            return 1.0
        return self.total_tasks_completed / total

    def add_capability(self, capability: WorkerCapability) -> None:
        """Register new capability."""
        if not any(c.name == capability.name for c in self.capabilities):
            self.capabilities.append(capability)

    def can_handle(self, component_name: str) -> bool:
        """Check if worker can execute component."""
        return any(c.name == component_name for c in self.capabilities)


@dataclass
class Task:
    """
    Unit of work to be executed by a worker.

    Tasks are created by the AI, picked up by workers, executed via components,
    and emit events on completion.
    """

    component_name: str  # What component/pattern to execute
    id: str = field(default_factory=lambda: str(uuid4()))
    state: TaskState = TaskState.PENDING

    # Inputs for execution
    parameters: Dict[str, Any] = field(default_factory=dict)

    # AI context
    ai_decision_id: Optional[str] = None  # Which AI decision created this
    priority: int = 0  # Higher = more important
    expected_value: float = 0.0  # AI's estimate of revenue/value
    expected_cost: float = 0.0  # AI's estimate of token cost

    # Execution tracking
    assigned_worker_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    actual_cost: float = 0.0
    actual_value: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_ready(self) -> bool:
        """Check if task is ready for execution."""
        return self.state == TaskState.PENDING

    def get_roi(self) -> float:
        """Calculate ROI: (value - cost) / cost."""
        if self.actual_cost == 0:
            return 0.0
        return (self.actual_value - self.actual_cost) / self.actual_cost

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task state."""
        return {
            "id": self.id,
            "component": self.component_name,
            "state": self.state.value,
            "priority": self.priority,
            "expected_value": self.expected_value,
            "expected_cost": self.expected_cost,
            "actual_value": self.actual_value,
            "actual_cost": self.actual_cost,
            "roi": self.get_roi(),
        }
