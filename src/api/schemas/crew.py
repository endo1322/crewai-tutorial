from pydantic import BaseModel


class RunRequest(BaseModel):
    topic: str


class JobResponse(BaseModel):
    job_id: str


class StatusResponse(BaseModel):
    job_id: str
    status: str  # "running" | "done" | "error"
    result: str | None = None
    error: str | None = None
