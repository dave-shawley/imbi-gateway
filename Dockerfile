FROM python:3.14-slim AS builder

COPY ./dist/ /mnt/dist/
COPY pyproject.toml /mnt/dist/
COPY uv.lock /mnt/dist/
ENV PATH=/root/.local/bin:$PATH
WORKDIR /mnt/dist/
RUN apt update \
 && apt install -y curl git \
 && curl -LsSf https://astral.sh/uv/install.sh | sh \
 && uv venv --system-site-packages --link-mode symlink /home/imbigateway \
 && . /home/imbigateway/bin/activate \
 && uv sync --active --group otel --no-dev --no-install-project --frozen \
 && uv pip install /mnt/dist/*.whl

FROM python:3.14-slim AS service

ENV PATH=/home/imbigateway/bin:$PATH
ENV OTEL_SERVICE_NAME=imbi-gateway \
    OTEL_LOGS_EXPORTER=none \
    OTEL_METRICS_EXPORTER=none \
    OTEL_TRACES_EXPORTER=none

EXPOSE 8000

COPY --from=builder /home/imbigateway/ /home/imbigateway/
RUN useradd --system --home-dir /home/imbigateway --shell /usr/sbin/nologin --uid 10001 imbigateway
WORKDIR /home/imbigateway
USER imbigateway
CMD [ "opentelemetry-instrument", "imbi-gateway", "--host", "0.0.0.0" ]
