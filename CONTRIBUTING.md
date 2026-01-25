# Contributing to Imbi Gateway

Thank you for your interest in contributing to Imbi Gateway! This document provides guidelines and instructions for setting up your development environment and contributing to the project.

## Prerequisites

This project uses two essential tools for development:

1. **[just](https://just.systems/)** - A command runner that simplifies common development tasks
2. **[uv](https://docs.astral.sh/uv/)** - A fast Python package and project manager

### Installing just

Choose the installation method that works best for your system:

```bash
# macOS via Homebrew
brew install just

# macOS/Linux via cargo
cargo install just

# Linux via package manager
# Debian/Ubuntu
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# For other platforms, see: https://just.systems/man/en/chapter_4.html
```

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv

# For other installation methods, see: https://docs.astral.sh/uv/getting-started/installation/
```

## Getting Started

Once you have `just` and `uv` installed, setting up your development environment is straightforward:

1. Clone the repository:
   ```bash
   git clone https://github.com/AWeber-Imbi/imbi-gateway.git
   cd imbi-gateway
   ```

2. Set up the development environment:
   ```bash
   just venv
   ```
   This command syncs your virtual environment with the project's dependencies using `uv`.

3. Start the required Docker services:
   ```bash
   just docker
   ```
   This starts the observability stack (Loki for logs, Jaeger for traces) needed for local development.

4. Run the service:
   ```bash
   just serve
   ```
   This is the default command that bootstraps the environment and runs the service in the foreground.

## Available Commands

You can see all available commands by running:
```bash
just --list
```

### Common Development Tasks

#### Running the Service

```bash
just serve
```
Starts the gateway service with OpenTelemetry instrumentation. The service will automatically configure itself to send logs and traces to the local observability stack.

#### Running Tests

```bash
just test
```
Runs the test suite using pytest with coverage reporting. The project requires at least 90% code coverage.

#### Running Linters

```bash
just lint
```
Runs all code quality checks:
- `pre-commit` - Runs configured pre-commit hooks (including ruff formatting)
- `basedpyright` - Type checking with pyright
- `mypy` - Additional type checking

It's a good idea to run this before committing your changes.

#### Managing Docker Services

```bash
# Start Docker services
just docker

# Stop Docker services and clean up
just clean
# or
just down
```

#### Creating the Environment File

```bash
just env-file
```
This command is typically run automatically, but you can run it manually if needed. It queries the running Docker containers to determine the correct ports and creates a `.env` file with the appropriate OpenTelemetry configuration.

#### Cleaning Up

```bash
# Remove runtime artifacts (Docker containers, coverage files, build artifacts)
just clean

# Remove everything including virtual environment and caches (requires confirmation)
just real-clean
```

## Development Workflow

A typical development workflow looks like this:

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes to the code

3. Run tests to ensure everything works:
   ```bash
   just test
   ```

4. Run linters to ensure code quality:
   ```bash
   just lint
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. Push your branch and create a pull request

## Project Structure

- `src/imbi_gateway/` - Main application code
- `tests/` - Test files
- `ci/` - CI/CD configuration and Grafana dashboards
- `justfile` - Development command definitions
- `pyproject.toml` - Project configuration and dependencies
- `compose.yaml` - Docker Compose configuration for local development

## Code Quality Standards

This project maintains high code quality standards:

- **Type Safety**: All code must pass both `mypy` and `basedpyright` type checking in strict mode
- **Code Style**: Code is formatted using `ruff` with single quotes and 79-character line length
- **Test Coverage**: Minimum 90% code coverage is required
- **Pre-commit Hooks**: Run automatically on commit to catch issues early

## Python Version

This project requires Python 3.14 or later.

## Questions?

If you have questions or need help, please open an issue on the GitHub repository.

## License

By contributing to this project, you agree that your contributions will be licensed under the BSD-3-Clause License.
