# Container image — port and health path are configured via .env / compose environment.

FROM python:3.12-slim

WORKDIR /app

# curl is used by the Docker healthcheck (stack-agnostic)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

ENV APP_PORT=5001
EXPOSE 5001

CMD ["uv", "run", "python", "app/main.py"]
