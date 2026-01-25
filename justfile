[default]
[doc("Bootstrap the environment and run the service in the foregroud")]
[no-exit-message]
serve: docker env-file
    -uv run --env-file .env opentelemetry-instrument imbi-gateway --log-config log-config.toml

[private]
ci: lint test

[doc("Sync the virtual environment with the uv.lock")]
venv:
    uv sync --all-groups --all-extras --frozen

[doc("Start docker components")]
docker:
    docker compose up -d --wait

[doc("Construct the dot-env environment file")]
[no-exit-message]
env-file:
    #!/usr/bin/env sh
    set -eu
    get_port() {
    	if ! host_n_port=$(docker compose port "$@"); then
    		echo "docker compose port $* failed" >&2
    		echo 'You may need to run `just docker`' >&2
    		return 1
    	fi
    	echo "${host_n_port##*:}"
    }

    logs_port=$(get_port loki 3100)
    trace_port=$(get_port jaeger 4317)
    cat>.env<<-EOF
    	OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://127.0.0.1:$logs_port/otlp/v1/logs
    	OTEL_EXPORTER_OTLP_LOGS_PROTOCOL=http/protobuf
    	OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://127.0.0.1:$trace_port
    	OTEL_LOGS_EXPORTER=otlp
    	OTEL_METRICS_EXPORTER=none
    	OTEL_PROPOGATORS=baggage,tracecontext
    	OTEL_SERVICE_NAME=imbi-gateway
    	OTEL_TRACES_EXPORTER=otlp
    EOF

[doc("Run tests")]
test:
    uv run pytest

[doc("Run linters")]
lint:
    uv run pre-commit run --all-files
    uv run basedpyright
    uv run mypy

alias down := clean

[doc("Remove runtime artifacts")]
clean:
    - docker compose down --remove-orphans --volumes
    rm -f .coverage .otel-env
    rm -fR build

[confirm]
[doc("Remove caches, virtual env, and output files")]
real-clean: clean
    rm -fR .venv .*_cache dist
