# Autonomous Entity System (AES)

A revenue-generating autonomous entity using Entity-Component-System (ECS) architecture.

## Vision

Single AI orchestrator (CEO/CTO/CFO/COO) managing a self-organizing worker pool to maximize profit.

**Core principles:**
- **Minimal interference**: AI only intervenes when needed
- **Token economy aware**: Every decision tracked for ROI
- **Worker self-organization**: Capability-based task assignment
- **Event-driven**: Pure event-based coordination, no direct system calls
- **Deterministic execution**: Workers execute component patterns, not LLM prompts

## Architecture

### Entities

- **Workers** – Independent executors with self-advertised capabilities
- **Tasks** – Units of work created by AI, executed by workers
- **Capabilities** – Deterministic patterns workers can perform

### Components

- **TaskComponent** – Schema for work (what a task looks like)
- **WorkerComponent** – Schema for capability (what a worker offers)
- **ComponentRegistry** – Central registry of all available work patterns

### Systems

- **AIOrchestrator** – Single AI making strategic decisions (minimal interference)
- **EventStream** – Event bus for reactive coordination
- **TaskQueue** – Priority queue of work
- **EconomicsTracker** – ROI tracking for every action
- **AutonomousEntityOrchestrator** – Main orchestration loop

## Project Structure

```
src/aes_core/
├── __init__.py                 # Main exports
├── entities.py                 # Worker, Task, Capability
├── components.py               # TaskComponent, WorkerComponent, Registry
├── ai_orchestrator.py          # AIOrchestrator (CEO brain)
├── event_stream.py             # Event bus
├── task_queue.py               # Priority queue
├── economics.py                # Cost/value tracking
└── orchestration.py            # Main loop + coordination
```

## Quick Start

```python
from aes_core import (
    AutonomousEntityOrchestrator,
    Worker,
    WorkerCapability,
    TaskComponent,
)

# Create orchestrator
aes = AutonomousEntityOrchestrator(token_budget=1_000_000)

# Register task components (what work looks like)
security_audit = TaskComponent(
    name="run_security_audit",
    description="Scan code for vulnerabilities",
    input_schema={"repo_url": "string"},
    output_schema={"findings": "array"},
    cost_estimate=100,
)
aes.register_component(security_audit)

# Register workers
worker = Worker(name="security_scanner")
worker.add_capability(
    WorkerCapability(name="run_security_audit", cost_per_execution=100)
)
aes.register_worker(worker)

# Create tasks
task = aes.create_task(
    component_name="run_security_audit",
    parameters={"repo_url": "https://github.com/example/repo"},
    expected_value=500,  # Revenue
    expected_cost=100,   # Tokens
)

# Run orchestration
aes.iteration()
```

## ECS Model Explained

**Entity Component System:**

- **Entities** – Workers and tasks (lightweight, just IDs + data containers)
- **Components** – Attachments defining capabilities/patterns
- **Systems** – Logic that operates on entities with matching components

**In AES:**

- Entities: Workers (have `Capability` components), Tasks (have `TaskComponent` components)
- Systems: AI orchestrator, event stream, task queue, executor
- No direct calls: everything communicates via events

## Integration with Existing Projects

- **Paperclip** – Task scheduling/state management
- **agileagents** – Worker execution engine (serverless)
- **MoMoA** – AI consensus/debate system
- **Shoggoth Foundry** – Self-hosting capability
- **Actor Runtime** – Distributed task execution
- **Security repos** – Components for security auditing

## Economics Model

Every action is tracked:

```python
# Costs
- Worker execution: tokens spent
- AI decision-making: tokens for LLM calls
- Monitoring: infrastructure overhead

# Value
- Completed tasks: revenue from clients
- Cost savings: operational efficiency
- Data value: insights produced

# ROI = (Value - Cost) / Cost
```

## Token Economy

AI is aware of:
- Total token budget (optional cap)
- Tokens spent per decision/action
- ROI of each task
- Cost vs. wealth produced trade-offs

Minimal interference: AI only investigates or creates tasks if the potential impact justifies the token cost.

## Next Steps

1. Integrate with LLM provider (Claude API)
2. Define task components for security/deployment/analysis
3. Connect to existing projects (Paperclip, agileagents, etc.)
4. Implement worker pool management
5. Test end-to-end workflow

## References

- Entity-Component-System pattern: Industry standard for game engines, now applied to autonomous systems
- Token economy: Anthropic token counting + ROI tracking
- Event-driven architecture: Proven pattern for loosely coupled systems

## License

MIT
