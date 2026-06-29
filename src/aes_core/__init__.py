"""
Autonomous Entity System (AES) - Revenue-Generating Autonomous Agent

Core ECS architecture for a profit-maximizing autonomous entity with:
- Single AI orchestrator (CEO/CTO/CFO/COO roles)
- Self-organizing worker pool
- Deterministic task execution
- Event-driven coordination
- Token economics tracking
"""

from .entities import Worker, Task, WorkerCapability
from .components import Component, TaskComponent, WorkerComponent
from .ai_orchestrator import AIOrchestrator, Decision
from .economics import EconomicsTracker, ResourceCost, ValueProduced
from .event_stream import Event, EventStream, EventType
from .task_queue import TaskQueue, TaskPriority

__version__ = "0.1.0"
__all__ = [
    "Worker",
    "Task",
    "WorkerCapability",
    "Component",
    "TaskComponent",
    "WorkerComponent",
    "AIOrchestrator",
    "Decision",
    "EconomicsTracker",
    "ResourceCost",
    "ValueProduced",
    "Event",
    "EventStream",
    "EventType",
    "TaskQueue",
    "TaskPriority",
]
