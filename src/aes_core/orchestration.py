"""
Main orchestration loop: the heartbeat of the autonomous entity system.

This is where the ECS model comes alive:
1. AI observes system state
2. AI makes decisions (create tasks, investigate, reallocate)
3. Workers execute tasks
4. Events flow back to AI
5. Economics tracked throughout
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .entities import Worker, Task, WorkerCapability
from .components import ComponentRegistry, TaskComponent
from .ai_orchestrator import AIOrchestrator, DecisionType
from .event_stream import EventStream, Event, EventType
from .task_queue import TaskQueue
from .economics import EconomicsTracker, CostCategory, ValueCategory


@dataclass
class SystemState:
    """Complete state of the autonomous entity system."""

    workers: Dict[str, Worker]
    tasks_pending: List[Task]
    tasks_completed: List[Task]
    economics: Dict[str, Any]
    recent_events: List[Event]
    ai_decisions: List[Dict[str, Any]]


class AutonomousEntityOrchestrator:
    """
    The main orchestrator that runs the AES.

    Coordinates:
    - Worker pool (self-organizing)
    - Task queue (AI-driven)
    - Component execution (deterministic patterns)
    - Event stream (reactive coordination)
    - Economics tracking (profit optimization)
    """

    def __init__(
        self,
        ai_model_name: str = "claude-opus",
        token_budget: Optional[float] = None,
    ):
        # Core components
        self.ai = AIOrchestrator(token_budget=token_budget)
        self.event_stream = EventStream()
        self.task_queue = TaskQueue()
        self.economics = EconomicsTracker()
        self.component_registry = ComponentRegistry()

        # Entity pools
        self.workers: Dict[str, Worker] = {}
        self.tasks: Dict[str, Task] = {}

        # Metadata
        self.ai_model = ai_model_name
        self.created_at = datetime.now()
        self.total_iterations = 0

        # Set up event subscriptions for reactive behavior
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for reactive coordination."""

        def on_task_completed(event: Event) -> None:
            """React to task completion."""
            task_id = event.data.get("task_id")
            actual_value = event.data.get("actual_value", 0)
            actual_cost = event.data.get("actual_cost", 0)

            # Record economics
            self.economics.record_value(
                ValueCategory.COMPLETED_TASK,
                actual_value,
                related_id=task_id,
            )
            self.economics.record_cost(
                CostCategory.WORKER_EXECUTION,
                actual_cost,
                related_id=task_id,
            )

        def on_task_failed(event: Event) -> None:
            """React to task failure."""
            task_id = event.data.get("task_id")
            error = event.data.get("error", "unknown")

            # Optionally retry or escalate
            # For now, just log

        def on_worker_registered(event: Event) -> None:
            """React to new worker joining."""
            # AI might decide to create new tasks now
            pass

        self.event_stream.subscribe(EventType.TASK_COMPLETED, on_task_completed)
        self.event_stream.subscribe(EventType.TASK_FAILED, on_task_failed)
        self.event_stream.subscribe(EventType.WORKER_REGISTERED, on_worker_registered)

    def register_worker(self, worker: Worker) -> None:
        """Register a new worker in the pool."""
        self.workers[worker.id] = worker
        self.event_stream.emit(
            Event(
                type=EventType.WORKER_REGISTERED,
                source="orchestrator",
                data={"worker_id": worker.id, "capabilities": [c.name for c in worker.capabilities]},
            )
        )

    def register_component(self, component: TaskComponent) -> None:
        """Register a new task component."""
        self.component_registry.register_task_component(component)

    def create_task(
        self,
        component_name: str,
        parameters: Dict[str, Any],
        priority: int = 5,
        expected_value: float = 0.0,
        expected_cost: float = 0.0,
    ) -> Task:
        """Create a new task and enqueue it."""
        task = Task(
            component_name=component_name,
            parameters=parameters,
            priority=priority,
            expected_value=expected_value,
            expected_cost=expected_cost,
        )

        self.tasks[task.id] = task
        self.task_queue.enqueue(task)

        self.event_stream.emit(
            Event(
                type=EventType.TASK_CREATED,
                source="orchestrator",
                data={
                    "task_id": task.id,
                    "component": component_name,
                    "expected_value": expected_value,
                    "expected_cost": expected_cost,
                },
            )
        )

        return task

    def assign_task_to_worker(self, task_id: str, worker_id: str) -> bool:
        """Assign a task to a specific worker."""
        task = self.tasks.get(task_id)
        worker = self.workers.get(worker_id)

        if not task or not worker:
            return False

        if not worker.can_handle(task.component_name):
            return False

        task.assigned_worker_id = worker_id
        worker.current_task_id = task_id

        self.event_stream.emit(
            Event(
                type=EventType.TASK_ASSIGNED,
                source="orchestrator",
                data={"task_id": task_id, "worker_id": worker_id},
            )
        )

        return True

    def complete_task(self, task_id: str, result: Dict[str, Any], actual_cost: float) -> None:
        """Mark a task as completed with results."""
        task = self.tasks.get(task_id)
        if not task:
            return

        task.result = result
        task.actual_cost = actual_cost
        task.actual_value = result.get("value", 0.0)

        self.event_stream.emit(
            Event(
                type=EventType.TASK_COMPLETED,
                source="orchestrator",
                data={
                    "task_id": task_id,
                    "actual_value": task.actual_value,
                    "actual_cost": actual_cost,
                },
            )
        )

    def fail_task(self, task_id: str, error: str, cost_incurred: float) -> None:
        """Mark a task as failed."""
        task = self.tasks.get(task_id)
        if not task:
            return

        task.error = error
        task.actual_cost = cost_incurred

        self.event_stream.emit(
            Event(
                type=EventType.TASK_FAILED,
                source="orchestrator",
                data={"task_id": task_id, "error": error, "cost": cost_incurred},
                severity="error",
            )
        )

    def get_system_state(self) -> SystemState:
        """Get complete snapshot of system state."""
        return SystemState(
            workers=self.workers,
            tasks_pending=[t for t in self.tasks.values() if not t.is_ready()],
            tasks_completed=[t for t in self.tasks.values() if t.state.value == "completed"],
            economics=self.economics.get_summary(),
            recent_events=self.event_stream.get_recent_events(50),
            ai_decisions=[
                {
                    "id": d.id,
                    "type": d.type.value,
                    "confidence": d.confidence,
                    "tokens": d.tokens_used,
                }
                for d in self.ai.get_decision_history()
            ],
        )

    def iteration(self) -> None:
        """Run one iteration of the orchestration loop."""
        self.total_iterations += 1

        # Step 1: AI observes system state
        state = self.get_system_state()
        self.ai.update_system_state(
            {
                "workers_count": len(self.workers),
                "queue_size": self.task_queue.get_size(),
                "economics": state.economics,
            }
        )

        # Step 2: AI makes decisions (simplified for now)
        # In real system: LLM would analyze state and decide tasks to create
        # For now: just log that AI would decide here

        # Step 3: Assign tasks to available workers
        for worker_id, worker in self.workers.items():
            if worker.is_available():
                # Find a task this worker can handle
                tasks = self.task_queue.find_tasks_for_worker(
                    [c.name for c in worker.capabilities],
                    limit=1,
                )
                if tasks:
                    task = tasks[0]
                    self.assign_task_to_worker(task.id, worker_id)

        # Step 4: Events would trigger reactions (handled by subscriptions)
