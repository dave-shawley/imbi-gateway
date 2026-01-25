FROM python:3.14-slim

EXPOSE 8000
CMD ["opentelemetry-instrument", "uvicorn", "--host", "0.0.0.0", "--log-config", "/app/log-config.yaml", "peer_app.app:app"]
ENV OTEL_SERVICE_NAME=peer \
    OTEL_LOGS_EXPORTER=none \
    OTEL_METRICS_EXPORTER=none \
    OTEL_TRACES_EXPORTER=none

COPY . /app
RUN pip install /app
