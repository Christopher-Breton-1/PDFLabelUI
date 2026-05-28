from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from celeryApp.celery_app import celery_app
# from celeryApp.celery_utils.db_utils import ensure_db

router = APIRouter()


@router.get("/task-status/{task_id}")
# @ensure_db
async def get_celery_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "STARTED":
        return {"status": "started"}
    elif task.state == "PROGRESS":
        return {"status": "progress"}
    elif task.state == "SUCCESS":
        return {"status": "success"}
    elif task.state == "FAILURE":
        return {"status": "failure", "error": str(task.result)}
    else:
        return {"status": task.state.lower()}
