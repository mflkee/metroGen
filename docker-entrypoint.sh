#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  uv run alembic upgrade head
fi

UVICORN_CMD="uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
if [ "${UVICORN_RELOAD}" = "1" ] || [ "${UVICORN_RELOAD}" = "true" ]; then
  UVICORN_CMD="$UVICORN_CMD --reload"
fi

exec sh -c "$UVICORN_CMD"
