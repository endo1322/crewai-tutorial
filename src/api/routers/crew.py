import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas.crew import JobResponse, RunRequest, StatusResponse
from api.services import job_store
from crewai_tutorial.crew import CrewaiTutorial

router = APIRouter()


@router.post("/run", response_model=JobResponse)
async def run(request: RunRequest):
    job_id = str(uuid.uuid4())
    job_store.create(job_id)

    async def _execute():
        try:
            inputs = {
                "topic": request.topic,
                "current_year": str(datetime.now().year),
            }
            result = await CrewaiTutorial().crew().akickoff(inputs=inputs)
            job_store.complete(job_id, str(result))
        except Exception as e:
            job_store.fail(job_id, str(e))

    asyncio.create_task(_execute())
    return JobResponse(job_id=job_id)


@router.get("/status/{job_id}", response_model=StatusResponse)
async def status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return StatusResponse(
        job_id=job.job_id,
        status=job.status,
        result=job.result,
        error=job.error,
    )
