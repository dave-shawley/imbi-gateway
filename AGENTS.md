# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) and other AI agents when working with code in this repository.

## Project Overview

Imbi Gateway is an inbound webhook gateway service that receives external events, records them, and routes them through a workflow engine for processing. It acts as the central integration point between external systems (GitHub, PagerDuty, etc.) and internal services like imbi-automations.

Built with:

- FastAPI for the web framework
- `imbi-common` library (shared across Imbi services) for server utilities and common functionality
- Typer for CLI commands
- Pydantic for data validation and settings management

## Development Commands

### Primary Interface: `just`

**All development tasks use `just` as the interface**, regardless of whether invoked by a human or automated process. The `justfile` automatically manages the devcontainer lifecycle and executes commands in the appropriate environment.

### Devcontainer-First Workflow

The project uses **devcontainers as the primary development environment**. The devcontainer provides:

- **PostgreSQL 17 database** (accessible at `postgres:5432`, pre-configured via `POSTGRES_URL` environment variable)
- **Isolated Python environment** with all dependencies installed via `uv`
- **Named volumes** for `.venv` and `build/` to prevent cross-platform conflicts
- **Automatic setup** on first start (dependencies, pre-commit hooks)

**Local `.venv` exists for IDE support only** (code completion, linting in editors). All execution, testing, and linting happens in the container.

### Common Commands

```bash
just test               # Run tests in devcontainer (auto-starts if needed)
just lint               # Run linters in devcontainer
just serve              # Run the service in devcontainer
just down               # Stop and remove devcontainer
just clean              # Stop devcontainer and remove artifacts
just real-clean         # Remove everything including local .venv
```

Run `just -l` to see all available commands with descriptions.

### How It Works

- **Automatic container management**: Commands like `just test` and `just lint` automatically start the devcontainer if not running
- **Command execution**: The `justfile` uses `devcontainer exec` to run commands inside the container
- **Workspace mounting**: Your local workspace is mounted at `/workspace` for live editing
- **No manual setup needed**: The devcontainer's `postCreateCommand` handles dependency installation and hook setup

### Maintaining the Devcontainer Stack

When modifying the devcontainer configuration:

**Key Files:**
- `.devcontainer/devcontainer.json` - Main configuration (ports, environment, post-create commands)
- `.devcontainer/compose.yaml` - Service definitions (app container, PostgreSQL)
- `.devcontainer/Dockerfile` - Container image build (Python version, base image)

**Important Patterns:**

1. **Docker Compose Project Name**: Set to `imbi-gateway-dev` in `compose.yaml` for predictable service names
2. **Named Volumes**: Use named volumes (`imbi-gateway-venv`, `imbi-gateway-build`) to persist state across rebuilds
3. **Health Checks**: PostgreSQL has a health check; app service depends on `postgres:service_healthy`
4. **Python Version**: Parameterized via `PYTHON_VERSION` build arg (defaults to 3.14)
5. **Environment Variables**: Set `POSTGRES_URL` in `devcontainer.json` for connection configuration

**Testing Configuration Changes:**

```bash
just down               # Stop current devcontainer
# Make changes to .devcontainer/*
just test               # Auto-rebuilds and tests with new configuration
```

**Rebuilding from Scratch:**

```bash
docker compose -p imbi-gateway-dev down --remove-orphans --volumes
devcontainer up --workspace-folder . --build-no-cache
```

## Architecture

### Application Structure

- **`src/imbi_gateway/app.py`**: Main application entry point
    - `create_app()`: FastAPI application factory
    - `cli`: Typer CLI with commands (currently just `serve`)
    - Uses `imbi_common.server.bind_entrypoint()` to create the `serve` command

- **`tests/helpers.py`**: Base test case using `unittest.IsolatedAsyncioTestCase`
    - All test classes should inherit from `helpers.TestCase` for async test support

### Lifespan Management Pattern

**Problem:** FastAPI's `lifespan` parameter accepts only one callable, but
applications need multiple independent resources (database pools, Redis
connections) with separate setup/teardown lifecycles.

**Solution:** The `Lifespan` class in `src/imbi_gateway/lifespan.py`
composes multiple async context managers into a single lifespan while
preserving type information through dependency injection. This enables
type-safe access to lifespan-managed resources in route handlers.

**Standard Usage Pattern:**

1. **Define a lifespan hook** as an async context manager that yields the
   resource:

   ```python
   @contextlib.asynccontextmanager
   async def postgres_lifespan() -> abc.AsyncIterator[PoolType]:
       async with psycopg_pool.AsyncConnectionPool(...) as pool:
           await pool.open(wait=True)
           yield pool
   ```

2. **Create a dependency injection function** that retrieves the resource
   using `get_state()`:

   ```python
   async def _get_postgres_cursor(
       context: lifespan.InjectLifespan
   ) -> abc.AsyncIterator[CursorType]:
       pool = context.get_state(postgres_lifespan)
       async with pool.connection() as conn:
           async with conn.cursor() as cursor:
               yield cursor
   ```

3. **Define a type alias** for dependency injection:

   ```python
   PostgresCursor = typing.Annotated[
       CursorType, fastapi.Depends(_get_postgres_cursor)
   ]
   ```

4. **Combine hooks** when creating the FastAPI application:

   ```python
   app = fastapi.FastAPI(
       lifespan=lifespan.Lifespan(postgres_lifespan, redis_lifespan)
   )
   ```

5. **Use the type alias** in route handler parameters:

   ```python
   @app.get('/data')
   async def handler(*, cursor: PostgresCursor) -> None:
       await cursor.execute('SELECT ...')
   ```

**Type Safety:** The `TypedLifespanHook[T]` type alias and generic
`get_state()` method preserve type information through the dependency
chain, enabling strict type checking and IDE autocomplete for resources.

**Key Files:**

- `src/imbi_gateway/lifespan.py` - Implementation with module docstring
- `tests/test_lifespan.py` - 10 test cases with examples and edge cases
- `docs/lifespan-pattern.md` - Comprehensive tutorial and API reference

### Shared Library: imbi-common

The project depends heavily on the `imbi-common` library (from https://github.com/AWeber-Imbi/imbi-common), which provides:

- Server utilities via `imbi_common.server`
- Database connection helpers
- Common logging and telemetry patterns
- Shared Pydantic models

When adding server features, check `imbi-common` first to reuse existing patterns.

### Code Style

- **Line length**: 79 characters (strict)
- **Quotes**: Single quotes for strings
- **Type checking**: Strict mode enabled for both basedpyright and mypy
- **Coverage requirement**: 90% minimum
- Use type hints on all functions (enforced by strict type checking)

### Pre-commit Hooks

The repository uses pre-commit with:

- Standard file checks (JSON, YAML, TOML validation, trailing whitespace, etc.)
- Ruff for linting and formatting
- Tombi for TOML formatting

Pre-commit runs automatically on commit after running `just setup`.

## Docker

Build and run with Docker:

```bash
# Build requires dist/*.whl files first
uv build
docker build -t imbi-gateway .
docker run -p 8000:8000 imbi-gateway
```

The Dockerfile uses a multi-stage build:

1. Builder stage: Installs uv, dependencies, and the wheel file
2. Service stage: Minimal runtime with Python 3.14-slim

## CI/CD

GitHub Actions workflows:

- **`.github/workflows/test.yml`**: Runs on push/PR
    - Uses devcontainers/ci action for consistent test environment
    - PostgreSQL automatically available via devcontainer compose
    - Static analysis (pre-commit, basedpyright, mypy) runs in devcontainer
    - Tests across Python 3.12, 3.13, 3.14 using matrix strategy with build args
- **`.github/workflows/docker.yml`**: Runs on release
    - Builds Python wheel
    - Publishes multi-arch Docker image to ghcr.io
    - Creates build attestations

## Project Dependencies

Key runtime dependencies (from `pyproject.toml`):

- `fastapi>=0.128.0`
- `imbi-common[server]` (git dependency, main branch)

The project uses `uv` for package management with `--frozen` flag in CI to ensure reproducible builds.
