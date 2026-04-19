import asyncio
from dataclasses import dataclass
from typing import Literal

JobStatus = Literal["running", "done", "error"]


@dataclass
class Job:
    job_id: str
    status: JobStatus = "running"
    result: str | None = None
    error: str | None = None


_store: dict[str, Job] = {}
_event_queues: dict[str, asyncio.Queue] = {}


def create(job_id: str) -> Job:
    job = Job(job_id=job_id)
    _store[job_id] = job
    _event_queues[job_id] = asyncio.Queue()
    return job


def get(job_id: str) -> Job | None:
    return _store.get(job_id)


def complete(job_id: str, result: str) -> None:
    if job := _store.get(job_id):
        job.status = "done"
        job.result = result


def fail(job_id: str, error: str) -> None:
    if job := _store.get(job_id):
        job.status = "error"
        job.error = error


def publish(job_id: str, event: dict | None) -> None:
    """イベントをキューに積む。None はストリーム終了のセンチネル。"""
    if q := _event_queues.get(job_id):
        q.put_nowait(event)


def get_event_queue(job_id: str) -> asyncio.Queue | None:
    return _event_queues.get(job_id)
