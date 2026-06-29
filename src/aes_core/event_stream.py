"""
Event stream: event-driven coordination between systems.

Events trigger state changes and AI re-evaluation.
No direct system-to-system calls; all communication via events.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional, Set
from datetime import datetime
from enum import Enum
from uuid import uuid4


class EventType(str, Enum):
    # Task events
    TASK_CREATED = "task_created"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # Worker events
    WORKER_REGISTERED = "worker_registered"
    WORKER_ONLINE = "worker_online"
    WORKER_OFFLINE = "worker_offline"
    WORKER_CAPABILITY_ADDED = "worker_capability_added"
    WORKER_FAILED = "worker_failed"

    # Economic events
    REVENUE_RECEIVED = "revenue_received"
    COST_INCURRED = "cost_incurred"
    ROI_UPDATED = "roi_updated"

    # AI events
    AI_DECISION_MADE = "ai_decision_made"
    AI_INVESTIGATION_REQUESTED = "ai_investigation_requested"

    # System events
    SYSTEM_STATE_CHANGED = "system_state_changed"
    ALERT = "alert"


@dataclass
class Event:
    """An event in the system."""

    type: EventType
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # Who emitted this event
    source: str = ""  # "worker_123", "ai_orchestrator", "task_queue"

    # What changed
    data: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    severity: str = "info"  # "info", "warning", "error", "critical"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event."""
        return {
            "type": self.type.value,
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "severity": self.severity,
        }


class EventStream:
    """
    Central event bus.

    Systems emit events. Other systems listen and react.
    This is the communication backbone.
    """

    def __init__(self):
        self.events: List[Event] = []
        self.subscriptions: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        self.subscriptions[event_type].append(handler)

    def subscribe_multiple(
        self, event_types: List[EventType], handler: Callable[[Event], None]
    ) -> None:
        """Subscribe to multiple event types with same handler."""
        for event_type in event_types:
            self.subscribe(event_type, handler)

    def emit(self, event: Event) -> None:
        """Emit an event, triggering all subscriptions."""
        self.events.append(event)

        # Call all subscribed handlers
        if event.type in self.subscriptions:
            for handler in self.subscriptions[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but don't crash
                    error_event = Event(
                        type=EventType.ALERT,
                        source="event_stream",
                        data={"error": str(e), "original_event_id": event.id},
                        severity="error",
                    )
                    self.events.append(error_event)

    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.type == event_type]

    def get_events_by_source(self, source: str) -> List[Event]:
        """Get all events from a specific source."""
        return [e for e in self.events if e.source == source]

    def get_recent_events(self, limit: int = 100) -> List[Event]:
        """Get most recent events."""
        return self.events[-limit:]

    def clear(self) -> None:
        """Clear all events (for testing or archival)."""
        self.events.clear()
