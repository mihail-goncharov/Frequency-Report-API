from __future__ import annotations

import asyncio
from typing import Optional

from app.application.report_service import build_report
from app.infastructure.job_store import Job, JobStore, JobStatus
from app.infastructure.xlsx_writter import write_report_xlsx


class JobQueue:
    def __init__(self, store: JobStore, worker_count:int = 2, max_queue_size:int = 100) -> None:
        # Queue holds Job objects; None is a sentinel to stop workers

        self._store = store
        self._queue: asyncio.Queue[Optional[Job]] = asyncio.Queue(maxsize=max_queue_size)
        self._workers: list[asyncio.Task] = []
        self._worker_count = worker_count

    async def start_workers(self) -> None:
        # Start fixed number of background workers
        for _ in range(self._worker_count):
            self._workers.append(asyncio.create_task(self._worker_loop()))

    async def stop_workers(self) -> None:
        # Send one sentinel per worker to stop them cleanly
        for _ in self._workers:
            await self._queue.put(None)
        await asyncio.gather(*self._workers, return_exceptions=True)

    async def enqueue(self, job: Job) -> None:
        await self._queue.put(job)

    async def _worker_loop(self) -> None:
        while True:
            job = await self._queue.get()
            if job is None:
                # Sentinel received -> stop worker
                break

            try:
                job.status = JobStatus.RUNNING
                self._store.update(job)

                # Build report and write xlsx
                with job.input_path.open("r", encoding="utf-8") as f:
                    rows = build_report(f)
                write_report_xlsx(rows, job.output_path)

                job.status = JobStatus.DONE
                self._store.update(job)
            except Exception as exc:
                job.status = JobStatus.FAILED
                job.error = str(exc)
                self._store.update(job)
            finally:
                self._queue.task_done()