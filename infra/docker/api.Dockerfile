FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY api/app ./api/app
COPY agent/agent ./agent/agent
COPY rag/rag ./rag/rag
COPY ml/ml ./ml/ml
COPY ingest/ingest ./ingest/ingest
COPY shared/shared ./shared/shared
RUN uv sync --locked --no-dev && useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
