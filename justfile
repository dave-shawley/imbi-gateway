[private]
devcontainer_exec := "devcontainer exec --workspace-folder ."
[private]
compose_project_name := "imbi-gateway-dev"

[doc("Run service in the dev container")]
[group("Testing")]
serve *ARGS: devcontainer-up
    -{{ devcontainer_exec }} uv run imbi-gateway serve --host=0.0.0.0 {{ ARGS }}

[default]
[private]
ci: setup devcontainer-up lint test

[private]
setup:
    uv sync --all-groups --all-extras --frozen
    uv run pre-commit install --install-hooks --overwrite

[doc("Run linters")]
[group("Testing")]
lint: devcontainer-up
    {{ devcontainer_exec }} uv run pre-commit run --all-files
    {{ devcontainer_exec }} uv run basedpyright
    {{ devcontainer_exec }} uv run mypy

[doc("Run pytest with optional ARGS")]
[group("Testing")]
test *ARGS: devcontainer-up
    {{ devcontainer_exec }} uv run pytest {{ ARGS }}

[doc("Build the docker image")]
[group("Testing")]
build: setup
    uv build --clear
    docker build -t 'aweber/imbi-gateway:local' .

[doc("Start the devcontainer")]
[private]
devcontainer-up:
    devcontainer up --workspace-folder .

[doc("Stop the devcontainer")]
[group("Environment")]
down:
    docker compose -p {{ compose_project_name }} down --remove-orphans --volumes

[doc("Remove development artifacts")]
[group("Environment")]
clean: down
    rm -fr .env build dist

[confirm]
[doc("Wipe out the development environment")]
[group("Environment")]
real-clean: clean
    rm -fr .venv
