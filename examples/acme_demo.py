#!/usr/bin/env python3
"""
ACME Demo: Autonomous Entity System in action.

Demonstrates:
1. Worker pool setup
2. Task creation by AI
3. Task assignment and execution
4. Event-driven coordination
5. Economics tracking
6. Security scanning component

Run: python3 examples/acme_demo.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aes_core import (
    AutonomousEntityOrchestrator,
    Worker,
    WorkerCapability,
    TaskComponent,
    EventType,
)
from aes_core.integrations import UnifiedSecurityTool


def setup_workers(acme: AutonomousEntityOrchestrator) -> None:
    """Register workers with ACME."""

    # Security scanner worker
    security_worker = Worker(
        name="security_scanner_01",
        metadata={"location": "us-east-1", "capacity": 10},
    )
    security_worker.add_capability(
        WorkerCapability(
            name="run_security_audit",
            cost_per_execution=100,
            success_rate=0.98,
        )
    )
    acme.register_worker(security_worker)

    # Code deployer worker
    deploy_worker = Worker(
        name="code_deployer_01",
        metadata={"location": "us-west-2"},
    )
    deploy_worker.add_capability(
        WorkerCapability(
            name="deploy_code",
            cost_per_execution=200,
            success_rate=0.95,
        )
    )
    acme.register_worker(deploy_worker)

    # Reporter worker
    report_worker = Worker(
        name="report_generator_01",
        metadata={"specialty": "analysis"},
    )
    report_worker.add_capability(
        WorkerCapability(
            name="generate_report",
            cost_per_execution=50,
            success_rate=0.99,
        )
    )
    acme.register_worker(report_worker)

    print(f"✓ Registered {len(acme.workers)} workers")


def setup_components(acme: AutonomousEntityOrchestrator) -> None:
    """Register task components (what work looks like)."""

    # Security audit component
    security_component = TaskComponent(
        name="run_security_audit",
        description="Scan code repository for vulnerabilities",
        input_schema={
            "target": "Repository URL or file path",
            "include_offensive": "Run offensive tests (boolean)",
        },
        output_schema={
            "findings": "Array of security findings",
            "severity_breakdown": "Count of findings by severity",
        },
        cost_estimate=100,
    )
    acme.register_component(security_component)

    # Deploy code component
    deploy_component = TaskComponent(
        name="deploy_code",
        description="Deploy code to production",
        input_schema={
            "repo": "Repository URL",
            "version": "Git tag or commit hash",
            "environment": "Deployment target",
        },
        output_schema={"deployment_id": "Tracking ID", "status": "Success or error"},
        cost_estimate=200,
    )
    acme.register_component(deploy_component)

    # Report component
    report_component = TaskComponent(
        name="generate_report",
        description="Generate comprehensive analysis report",
        input_schema={"data": "Input data to analyze"},
        output_schema={"report": "Generated report"},
        cost_estimate=50,
    )
    acme.register_component(report_component)

    print(f"✓ Registered {len(acme.component_registry.task_components)} task components")


def create_demo_tasks(acme: AutonomousEntityOrchestrator) -> None:
    """Create tasks for ACME to execute."""

    # Task 1: Security audit
    task1 = acme.create_task(
        component_name="run_security_audit",
        parameters={
            "target": "https://github.com/example/vulnerable-app",
            "include_offensive": True,
        },
        priority=10,  # High priority
        expected_value=2000,  # Revenue from client
        expected_cost=100,  # Tokens
    )
    print(f"✓ Created security audit task: {task1.id}")

    # Task 2: Deploy code
    task2 = acme.create_task(
        component_name="deploy_code",
        parameters={
            "repo": "https://github.com/example/app",
            "version": "v1.2.3",
            "environment": "production",
        },
        priority=8,
        expected_value=1500,
        expected_cost=200,
    )
    print(f"✓ Created deployment task: {task2.id}")

    # Task 3: Generate report
    task3 = acme.create_task(
        component_name="generate_report",
        parameters={"data": "Summary of findings and metrics"},
        priority=5,
        expected_value=500,
        expected_cost=50,
    )
    print(f"✓ Created report task: {task3.id}")


def simulate_execution(acme: AutonomousEntityOrchestrator) -> None:
    """Simulate task execution."""

    print("\n--- Running Orchestration Loop ---")

    # Run one iteration
    acme.iteration()

    print("✓ Completed orchestration iteration")

    # Print system state
    state = acme.get_system_state()
    print(f"\n--- System State ---")
    print(f"Workers: {len(state.workers)} online")
    print(f"Tasks pending: {len(state.tasks_pending)}")
    print(f"Tasks completed: {len(state.tasks_completed)}")
    print(f"Queue size: {acme.task_queue.get_size()}")


def demonstrate_security_tool() -> None:
    """Demonstrate unified security tool."""

    print("\n--- Security Tool Demo ---")

    security_tool = UnifiedSecurityTool()
    result = security_tool.scan_comprehensive(
        target="https://github.com/example/app",
        include_offensive=True,
    )

    print(f"Scan target: {result['target']}")
    print(f"Engines run: {', '.join(result['engines_run'])}")
    print(f"Total findings: {result['total_findings']}")
    print(f"Severity breakdown: {result['severity_breakdown']}")

    # Show findings
    if result["findings"]:
        print("\nTop findings:")
        for finding in result["findings"][:3]:
            print(f"  - [{finding['severity']}] {finding['title']}")


def print_economics(acme: AutonomousEntityOrchestrator) -> None:
    """Print economics summary."""

    print("\n--- Economics ---")
    summary = acme.economics.get_summary()
    print(f"Total cost: {summary['total_cost']:.2f} tokens")
    print(f"Total value: {summary['total_value']:.2f}")
    print(f"Net profit: {summary['net_profit']:.2f}")
    print(f"ROI: {summary['roi_percent']:.2f}%")


def main():
    """Run ACME demo."""

    print("=" * 60)
    print("ACME - Agentic Coordination Manufacturing Engine")
    print("=" * 60)

    # Create ACME instance with token budget
    acme = AutonomousEntityOrchestrator(
        ai_model_name="claude-opus-4-1",
        token_budget=10_000,  # 10k tokens budget
    )

    print("\n✓ ACME initialized")
    print(f"  Token budget: {acme.ai.token_budget}")
    print(f"  AI model: {acme.ai_model}")

    # Setup
    setup_workers(acme)
    setup_components(acme)

    # Create tasks
    print("\n--- Creating Tasks ---")
    create_demo_tasks(acme)

    # Execute
    simulate_execution(acme)

    # Demonstrate security tool
    demonstrate_security_tool()

    # Economics
    print_economics(acme)

    # Final state
    print("\n--- Final State ---")
    state = acme.get_system_state()
    print(f"Workers registered: {len(state.workers)}")
    print(f"Total tasks created: {len(acme.tasks)}")
    print(f"Orchestration iterations: {acme.total_iterations}")
    print(f"Recent events: {len(state.recent_events)}")

    print("\n" + "=" * 60)
    print("✓ ACME demo complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
