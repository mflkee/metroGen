#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

read_env_value() {
  local key="$1"

  if [[ ! -f .env ]]; then
    return 1
  fi

  local line
  line="$(grep -E "^${key}=" .env | tail -n 1 || true)"
  if [[ -z "$line" ]]; then
    return 1
  fi

  printf '%s\n' "${line#*=}"
}

POSTGRES_PORT="${POSTGRES_PORT:-$(read_env_value POSTGRES_PORT || echo 5433)}"
API_PORT="${API_PORT:-$(read_env_value API_PORT || echo 8001)}"
POSTGRES_DB="${POSTGRES_DB:-$(read_env_value POSTGRES_DB || echo metrologenerator)}"
POSTGRES_USER="${POSTGRES_USER:-$(read_env_value POSTGRES_USER || echo metrologenerator)}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(read_env_value POSTGRES_PASSWORD || echo metrologenerator)}"
API_HOST="${API_HOST:-$(read_env_value API_HOST || echo 0.0.0.0)}"
API_LOG_LEVEL="${API_LOG_LEVEL:-$(read_env_value API_LOG_LEVEL || echo info)}"
ARSHIN_TIMEOUT="${ARSHIN_TIMEOUT:-$(read_env_value ARSHIN_TIMEOUT || echo 30)}"
ARSHIN_CONCURRENCY="${ARSHIN_CONCURRENCY:-$(read_env_value ARSHIN_CONCURRENCY || echo 2)}"
PROTOCOL_BUILD_CONCURRENCY="${PROTOCOL_BUILD_CONCURRENCY:-$(read_env_value PROTOCOL_BUILD_CONCURRENCY || echo 2)}"
USER_AGENT="${USER_AGENT:-$(read_env_value USER_AGENT || echo arshin-fastapi/0.1)}"

docker compose up -d db
docker compose stop api frontend >/dev/null 2>&1 || true

LOCAL_DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"

env \
  UV_CACHE_DIR=/tmp/uv-cache \
  DATABASE_URL="$LOCAL_DATABASE_URL" \
  API_PORT="$API_PORT" \
  API_HOST="$API_HOST" \
  API_LOG_LEVEL="$API_LOG_LEVEL" \
  ARSHIN_TIMEOUT="$ARSHIN_TIMEOUT" \
  ARSHIN_CONCURRENCY="$ARSHIN_CONCURRENCY" \
  PROTOCOL_BUILD_CONCURRENCY="$PROTOCOL_BUILD_CONCURRENCY" \
  USER_AGENT="$USER_AGENT" \
  uv run alembic upgrade head

env \
  UV_CACHE_DIR=/tmp/uv-cache \
  DATABASE_URL="$LOCAL_DATABASE_URL" \
  API_PORT="$API_PORT" \
  API_HOST="$API_HOST" \
  API_LOG_LEVEL="$API_LOG_LEVEL" \
  ARSHIN_TIMEOUT="$ARSHIN_TIMEOUT" \
  ARSHIN_CONCURRENCY="$ARSHIN_CONCURRENCY" \
  PROTOCOL_BUILD_CONCURRENCY="$PROTOCOL_BUILD_CONCURRENCY" \
  USER_AGENT="$USER_AGENT" \
  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port "$API_PORT"

