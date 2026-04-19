import uvicorn
from fastapi import FastAPI
from api.routers import crew

app = FastAPI(title="CrewAI API", version="0.1.0")

app.include_router(crew.router, prefix="/crew", tags=["crew"])


@app.get("/health")
async def health():
    return {"status": "ok"}


def serve():
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
