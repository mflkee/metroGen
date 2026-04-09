#!/bin/sh
set -e

PYTHON_BIN="/app/.venv/bin/python"

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
