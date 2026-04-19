from dataclasses import dataclass, field
from typing import Literal

JobStatus = Literal["running", "done", "error"]


@dataclass
class Job:
    job_id: str
    status: JobStatus = "running"
    result: str | None = None
    error: str | None = None


# インメモリストア（本番では Redis に差し替える）
_store: dict[str, Job] = {}


def create(job_id: str) -> Job:
    job = Job(job_id=job_id)
    _store[job_id] = job
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
