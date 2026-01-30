FROM python:3.11-slim AS base


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev


COPY . .
CMD ["python", "-m", "src.main"]