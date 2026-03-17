from fastapi import FastAPI

from app.api.routes import router as report_router
from app.infastructure.job_queue import JobQueue
from app.infastructure.job_store import JobStore


def create_app() -> FastAPI:
    app = FastAPI(title="Report Export API")
    app.include_router(report_router)

    @app.on_event("startup")
    async def startup() -> None:
        store = JobStore()
        queue = JobQueue(store=store, worker_count=2, max_queue_size=100)
        await queue.start_workers()
        app.state.job_store = store
        app.state.job_queue = queue


    @app.on_event("shutdown")
    async def shutdown() -> None:
        queue: JobQueue = app.state.job_queue
        await queue.stop_workers()

    return app


app = create_app()