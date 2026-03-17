from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse

from app.infastructure.job_queue import JobQueue
from app.infastructure.job_store import JobStore, JobStatus

router = APIRouter(prefix="/public/report", tags=["report"])


def get_job_store(request: Request) -> JobStore:
    from main import app
    return app.state.job_store


def get_job_queue(request: Request) -> JobQueue:
    from main import app
    return app.state.job_queue



@router.post("/export")
async def export_report(
        upload: UploadFile = File(...),
        store: JobStore = Depends(get_job_store),
        queue: JobQueue = Depends(get_job_queue),
    ):
    data_dir = Path("data")
    upload_dir = data_dir / "uploads"
    output_dir = data_dir / "outputs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file to disk
    input_path = upload_dir / upload.filename
    with input_path.open("wb") as f:
        while chunk := await upload.read(1024 * 1024):
            f.write(chunk)

    # Create job + output path
    output_path = output_dir / f"{input_path.stem}.xlsx"
    job = store.create(input_path=input_path, output_path=output_path)
    await queue.enqueue(job)

    return {"job_id": str(job.id), "status": job.status}


@router.get("/status/{job_id}")
def job_status(job_id: UUID, store: JobStore = Depends(get_job_store)):
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": str(job.id), "status": job.status, "error":job.error}


@router.get("/download/{job_id}")
def download(job_id: UUID, store: JobStore = Depends(get_job_store)):
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=400, detail=f"Job status is {job.status}")
    if not job.output_path.exists():
        raise HTTPException(status_code=404, detail="Output file missing")

    return FileResponse(
        path=job.output_path,
        filename=job.output_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


