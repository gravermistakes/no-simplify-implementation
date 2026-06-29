"""
Single AI orchestrator: CEO, CTO, CFO, COO in one.

Makes strategic decisions:
- What work to pursue (which tasks to create)
- How to allocate resources (which workers to use)
- When to investigate deeper (visibility into system state)
- Risk/cost trade-offs (token economy aware)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from enum import Enum


class DecisionType(str, Enum):
    CREATE_TASK = "create_task"
    ESCALATE_INVESTIGATION = "escalate_investigation"
    PAUSE_WORK = "pause_work"
    REALLOCATE_RESOURCES = "reallocate_resources"
    ADJUST_PRICING = "adjust_pricing"
    SCALE_WORKERS = "scale_workers"


@dataclass
class Decision:
    """A decision made by the AI orchestrator."""

    id: str
    type: DecisionType
    rationale: str  # Why the AI made this decision
    confidence: float  # 0.0-1.0, how certain is the AI
    impact_estimate: Dict[str, Any]  # Expected outcome

    # Token economy
    tokens_used: float
    tokens_budgeted: float

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIOrchestrator:
    """
    Single AI making all strategic decisions.

    Philosophy:
    - Minimal interference for maximal result
    - Aware of token cost vs. wealth produced
    - Can see everything if it cares to investigate
    - Goal: maximize profit (revenue - cost)
    """

    def __init__(
        self,
        goal: str = "make money",
        token_budget: Optional[float] = None,
        investigation_threshold: float = 0.1,  # ROI threshold before investigating
    ):
        self.goal = goal
        self.token_budget = token_budget  # None = unlimited
        self.tokens_used = 0.0
        self.investigation_threshold = investigation_threshold

        # Decision history
        self.decisions: Dict[str, Decision] = {}
        self.decision_order: List[str] = []

        # System state it's aware of
        self.system_state: Dict[str, Any] = {}
        self.worker_states: Dict[str, Dict[str, Any]] = {}
        self.task_queue_state: Dict[str, Any] = {}
        self.economics_state: Dict[str, Any] = {}

    def update_system_state(self, state: Dict[str, Any]) -> None:
        """AI observes current system state."""
        self.system_state = state

    def decide_tasks_to_create(
        self,
        market_opportunities: List[Dict[str, Any]],
        available_workers: List[Dict[str, Any]],
        current_constraints: Dict[str, Any],
    ) -> List[Decision]:
        """
        Decide which tasks to create based on opportunities and resources.

        Market opportunities: [{task_type, expected_value, difficulty, ...}]
        Available workers: [{worker_id, capabilities, state, ...}]
        Current constraints: {token_budget, max_workers, ...}
        """
        decisions = []

        # Simple strategy: pursue highest ROI opportunities that we have capacity for
        for opportunity in sorted(
            market_opportunities,
            key=lambda x: x.get("expected_roi", 0.0),
            reverse=True,
        ):
            task_type = opportunity["task_type"]
            expected_value = opportunity["expected_value"]
            expected_cost = opportunity["expected_cost"]
            expected_roi = (expected_value - expected_cost) / expected_cost if expected_cost > 0 else 0

            # Check token budget
            if self.token_budget and (self.tokens_used + expected_cost) > self.token_budget:
                continue

            # Check if we have workers for this task
            capable_workers = [w for w in available_workers if task_type in w.get("capabilities", [])]
            if not capable_workers:
                continue

            # Create decision to create task
            decision = Decision(
                id=f"decision_{len(self.decisions)}",
                type=DecisionType.CREATE_TASK,
                rationale=f"High ROI opportunity: {task_type} with {expected_roi:.2%} expected ROI",
                confidence=opportunity.get("confidence", 0.8),
                impact_estimate={
                    "expected_value": expected_value,
                    "expected_cost": expected_cost,
                    "expected_roi": expected_roi,
                    "task_type": task_type,
                },
                tokens_used=expected_cost,
                tokens_budgeted=self.token_budget or float("inf"),
            )

            self.decisions[decision.id] = decision
            self.decision_order.append(decision.id)
            self.tokens_used += expected_cost
            decisions.append(decision)

        return decisions

    def decide_investigation(
        self,
        situation: Dict[str, Any],
        cost_to_investigate: float,
        potential_impact: float,
    ) -> Optional[Decision]:
        """
        Decide whether to investigate deeper into a situation.

        Minimal interference: only investigate if potential impact justifies cost.
        """
        if potential_impact < self.investigation_threshold * cost_to_investigate:
            # Not worth investigating
            return None

        # Budget check
        if self.token_budget and (self.tokens_used + cost_to_investigate) > self.token_budget:
            return None

        decision = Decision(
            id=f"decision_{len(self.decisions)}",
            type=DecisionType.ESCALATE_INVESTIGATION,
            rationale=f"Potential impact ${potential_impact} justifies investigation cost ${cost_to_investigate}",
            confidence=0.7,
            impact_estimate={"potential_impact": potential_impact},
            tokens_used=cost_to_investigate,
            tokens_budgeted=self.token_budget or float("inf"),
        )

        self.decisions[decision.id] = decision
        self.decision_order.append(decision.id)
        self.tokens_used += cost_to_investigate
        return decision

    def get_decision_history(self) -> List[Decision]:
        """Get decisions in chronological order."""
        return [self.decisions[id] for id in self.decision_order]

    def get_tokens_remaining(self) -> Optional[float]:
        """Get remaining token budget."""
        if self.token_budget is None:
            return None
        return self.token_budget - self.tokens_used

    def is_within_budget(self) -> bool:
        """Check if AI is still within token budget."""
        if self.token_budget is None:
            return True
        return self.tokens_used <= self.token_budget
