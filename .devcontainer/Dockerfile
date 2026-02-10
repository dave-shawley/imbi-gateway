ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim
EXPOSE 8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create vscode user for compatibility with devcontainer features
RUN useradd -m -s /bin/bash vscode

WORKDIR /workspace

CMD ["sleep", "infinity"]
