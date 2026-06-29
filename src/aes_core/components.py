"""
Components: Deterministic patterns that workers execute.

Components define HOW to do work (the logic/patterns).
Workers execute components on tasks.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, List
from abc import ABC, abstractmethod


@dataclass
class Component(ABC):
    """Base component: a deterministic execution pattern."""

    name: str
    description: str = ""
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute component logic with given parameters."""
        pass

    @abstractmethod
    def validate(self, parameters: Dict[str, Any]) -> bool:
        """Validate that parameters are correct for this component."""
        pass


@dataclass
class TaskComponent:
    """Schema for a task-level component (what work looks like)."""

    name: str  # e.g., "run_security_audit", "deploy_code", "generate_report"
    description: str
    input_schema: Dict[str, Any]  # JSON schema for parameters
    output_schema: Dict[str, Any]  # JSON schema for results
    cost_estimate: float  # Expected token/resource cost
    timeout_seconds: float = 300.0
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerComponent:
    """Schema for a worker-level component (what capability looks like)."""

    name: str  # e.g., "security_scanner", "code_deployer"
    description: str
    supported_tasks: List[str]  # Which TaskComponents this worker can handle
    max_concurrent: int = 1  # How many tasks simultaneously
    cost_per_task: float = 1.0  # Token cost per execution
    success_rate_baseline: float = 0.95
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComponentRegistry:
    """Central registry of all available components."""

    def __init__(self):
        self.task_components: Dict[str, TaskComponent] = {}
        self.worker_components: Dict[str, WorkerComponent] = {}

    def register_task_component(self, component: TaskComponent) -> None:
        """Register a task component."""
        self.task_components[component.name] = component

    def register_worker_component(self, component: WorkerComponent) -> None:
        """Register a worker component."""
        self.worker_components[component.name] = component

    def get_task_component(self, name: str) -> Optional[TaskComponent]:
        """Retrieve task component by name."""
        return self.task_components.get(name)

    def get_worker_component(self, name: str) -> Optional[WorkerComponent]:
        """Retrieve worker component by name."""
        return self.worker_components.get(name)

    def list_task_components(self) -> List[TaskComponent]:
        """List all available task components."""
        return list(self.task_components.values())

    def list_worker_components(self) -> List[WorkerComponent]:
        """List all available worker components."""
        return list(self.worker_components.values())

    def find_workers_for_task(self, task_component_name: str) -> List[str]:
        """Find which worker components can handle a task component."""
        workers = []
        for wc in self.worker_components.values():
            if task_component_name in wc.supported_tasks:
                workers.append(wc.name)
        return workers
