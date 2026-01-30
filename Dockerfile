FROM python:3.11-slim AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git gcc curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.cargo/bin/uv /usr/local/bin/uv

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости с помощью uv напрямую
RUN uv pip install --system --no-cache -r pyproject.toml

# Копируем исходный код
COPY . .

CMD ["python", "-m", "src.main"]