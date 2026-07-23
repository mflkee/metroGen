from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException

from app.schemas.protocol import GenerationJobAcceptedRead, GenerationJobRead, GenerationResultRead

_GENERATION_JOB_TTL = timedelta(hours=24)
_GENERATION_JOBS: dict[str, dict[str, Any]] = {}


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


def _prune_generation_jobs() -> None:
    cutoff = _utcnow() - _GENERATION_JOB_TTL
    stale_ids = [
        job_id
        for job_id, payload in _GENERATION_JOBS.items()
        if payload.get("finished_at") and payload["finished_at"] < cutoff
    ]
    for job_id in stale_ids:
        _GENERATION_JOBS.pop(job_id, None)


def _create_generation_job() -> GenerationJobAcceptedRead:
    _prune_generation_jobs()
    job_id = secrets.token_hex(8)
    started_at = _utcnow()
    _GENERATION_JOBS[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "stage": "preparation",
        "total_items": 0,
        "processed_items": 0,
        "saved_count": 0,
        "failed_count": 0,
        "started_at": started_at,
        "updated_at": started_at,
        "finished_at": None,
        "error": None,
        "result": None,
    }
    return GenerationJobAcceptedRead(
        job_id=job_id,
        status="queued",
        stage="preparation",
        started_at=started_at,
    )


def _get_generation_job(job_id: str) -> dict[str, Any]:
    payload = _GENERATION_JOBS.get(job_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Generation job not found.")
    return payload


def _update_generation_job(
    job_id: str | None,
    *,
    status: str | None = None,
    stage: str | None = None,
    total_items: int | None = None,
    processed_items: int | None = None,
    saved_count: int | None = None,
    failed_count: int | None = None,
    error: str | None = None,
    result: GenerationResultRead | None = None,
    finished: bool = False,
) -> None:
    if not job_id:
        return
    payload = _get_generation_job(job_id)
    if status is not None:
        payload["status"] = status
    if stage is not None:
        payload["stage"] = stage
    if total_items is not None:
        payload["total_items"] = total_items
    if processed_items is not None:
        payload["processed_items"] = processed_items
    if saved_count is not None:
        payload["saved_count"] = saved_count
    if failed_count is not None:
        payload["failed_count"] = failed_count
    if error is not None:
        payload["error"] = error
    if result is not None:
        payload["result"] = result.model_dump(mode="python")
    payload["updated_at"] = _utcnow()
    if finished:
        payload["finished_at"] = payload["updated_at"]


def _snapshot_generation_job(job_id: str) -> GenerationJobRead:
    return GenerationJobRead.model_validate(_get_generation_job(job_id))
