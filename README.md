# Imbi Gateway

Inbound webhook gateway service that receives external events, records them, and routes them through a workflow engine for processing. Acts as the central integration point between external systems and internal services like imbi-automations.

## Developer Quickstart

This project uses [devcontainers](https://containers.dev/) for isolated development environments and [just](https://just.systems/man/en/) as the task runner interface. Install the required tools:

- **[devcontainer CLI](https://containers.dev/supporting)** - Required for container-based development
- **[just](https://just.systems/man/en/chapter_4.html)** - Task runner (interface for all development commands)
- **[uv](https://docs.astral.sh/uv/)** - Python package manager (optional, for local IDE support)

### Quick Start

Run development commands using `just`:

```shell
just test       # Run tests in devcontainer
just lint       # Run linters in devcontainer
just serve      # Start the service in devcontainer
```

Run `just -l` to see all available commands.

### Development Workflow

All development tasks automatically run in the devcontainer via the `justfile`. The devcontainer provides:

- PostgreSQL 17 database (pre-configured and accessible)
- Isolated Python environment with all dependencies
- Consistent development environment across machines

A local `.venv` is maintained for IDE support (code completion, linting in your editor), but all tests, linting, and execution happen in the container.
