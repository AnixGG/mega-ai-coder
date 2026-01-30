FROM python:3.11-slim AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем uv и зависимости
RUN pip install --no-cache-dir uv \
    && uv venv \
    && .venv/bin/pip install --no-cache-dir -e .

# Копируем исходный код
COPY . .

# Используем виртуальное окружение для запуска
CMD ["/app/.venv/bin/python", "-m", "src.main"]