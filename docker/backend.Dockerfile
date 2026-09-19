FROM python:3.11-slim AS base

WORKDIR /app

COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY backend/app ./app
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations

# Same image serves both the API and the worker — the CMD differs per
# service in docker-compose. One image, two processes: less to maintain
# than two separate builds for code that shares every dependency.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]