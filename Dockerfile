FROM python:3.11-slim

# Установка системных зависимостей (особенно для tree-sitter и gitpython)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml README.md uv.lock ./

# Синхронизация зависимостей без dev-зависимостей
RUN uv sync --frozen --no-dev

# Копируем исходный код
COPY src/ ./src/

# Настройка окружения
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

ENTRYPOINT ["python", "-m", "src.main"]

CMD ["--help"]