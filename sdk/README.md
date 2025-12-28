# LTrail SDK

LTrail is a lightweight Python library for debugging multi step decision making systems.

It provides visibility into why a system made a particular decision by capturing inputs, outputs, evaluations, and reasoning at each step of a workflow.

## Features

- End to end decision tracing
- Step level inputs, outputs, and reasoning
- Item level evaluations with pass or fail checks
- Minimal boilerplate using context managers
- JSON export for inspection or dashboards
- Minimal dependencies (core uses stdlib; `requests` optional for backend)

## Use Cases

- Debugging LLM and AI driven workflows
- Explaining filtering and ranking decisions
- Auditing automated decision pipelines
- Improving observability in complex systems
