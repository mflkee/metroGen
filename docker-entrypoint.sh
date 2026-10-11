#!/bin/sh
set -e

PYTHON_BIN="/app/.venv/bin/python"

# The virtualenv lives in a named volume (api_venv / api_venv_stg), which masks the
# one baked into the image. Reconcile it with the lock so that a dependency change
# actually reaches the running container instead of only the image layer.
if command -v uv >/dev/null 2>&1 && [ -f /app/uv.lock ]; then
  uv sync --frozen --no-dev --quiet || \
    echo "uv sync failed; continuing with the existing virtualenv" >&2
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Virtual environment is missing at /app/.venv. Rebuild the api image." >&2
  exit 1
fi

if [ -n "$DATABASE_URL" ]; then
  "$PYTHON_BIN" -m alembic upgrade head
fi

UVICORN_CMD="$PYTHON_BIN -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
if [ "${UVICORN_RELOAD}" = "1" ] || [ "${UVICORN_RELOAD}" = "true" ]; then
  UVICORN_CMD="$UVICORN_CMD --reload"
fi

exec sh -c "$UVICORN_CMD"
