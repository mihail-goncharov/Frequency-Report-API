from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional
from uuid import UUID, uuid4


class JobStatus(str, Enum):
    # Job lifecycle states
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class Job:
    # Metadata for one export job
    id: UUID
    input_path: Path
    output_path: Path
    status: JobStatus = JobStatus.PENDING
    error: Optional[str] = None


class JobStore:
    # Simply in-memory store
    def __init__(self) -> None:
        self._jobs: Dict[UUID, Job] = {}

    def create(self, input_path: Path, output_path: Path) -> Job:
        job = Job(id=uuid4(), input_path=input_path, output_path=output_path)
        self._jobs[job.id] = job
        return job

    def get(self, job_id: UUID) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update(self, job: Job) -> None:
        self._jobs[job.id] = job