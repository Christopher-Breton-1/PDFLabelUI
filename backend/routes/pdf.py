from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from celeryApp.celery_app import celery_app
from services.tasks import process_pdf_task, process_metadata_task
from config import SHARED_TMP_UPLOAD_DIR
# from celeryApp.celery_utils.db_utils import ensure_db

router = APIRouter()


# @router.get("/metadata/{tmp_dir}/{pdf_name}/")
# async def get_pdf_metadata(tmp_dir: str, pdf_name: str):
#     pdf_path = SHARED_TMP_UPLOAD_DIR / tmp_dir / pdf_name
#     metadata_path = pdf_path.with_name(pdf_path.stem + "_metadata.xml")
#
#     if not pdf_path.exists() or not metadata_path.exists():
#         raise HTTPException(status_code=404, detail="PDF or metadata not found")
#
#     task_id = f"{tmp_dir}_{pdf_name}"
#     task = AsyncResult(task_id, app=celery_app)
#
#     if not task.successful():
#         if task.state == "PENDING":
#             task = process_pdf_task.apply_async(
#                 args=(str(pdf_path), str(metadata_path)),
#                 task_id=task_id
#             )
#             return {"status": "processing", "task_id": task.id}
#         elif task.state in ["PROGRESS", "FAILURE"]:
#             return {"status": task.state, "task_id": task_id}
#
#     result = task.result
#     metadata = result["metadata"]
#
#     return {
#         "status": "success",
#         "metadata": metadata,
#     }
@router.get("/{tmp_dir}/{pdf_name}/page/{page_number}")
# @ensure_db
async def get_pdf_page_blocks(tmp_dir: str, pdf_name: str, page_number: int):
    pdf_path = SHARED_TMP_UPLOAD_DIR / tmp_dir / pdf_name
    xml_path = pdf_path.with_suffix(".xml")
    metadata_path = pdf_path.with_name(pdf_path.stem + "_metadata.xml")

    if not pdf_path.exists() or not xml_path.exists():
        raise HTTPException(status_code=404, detail="PDF or XML not found")

    task_id = f"{tmp_dir}_{pdf_name}"
    task = AsyncResult(task_id, app=celery_app)

    if not task.successful():
        if task.state == "PENDING":
            task = process_pdf_task.apply_async(
                args=(str(pdf_path), str(xml_path), str(metadata_path)),
                task_id=task_id
            )
            return {"status": "processing", "task_id": task.id}
        elif task.state in ["PROGRESS", "FAILURE"]:
            return {"status": task.state, "task_id": task_id}

    result = task.result
    images = result["images"]
    page_blocks = result["xml_page"][page_number]["blocks"]
    page_dims = result["xml_page"][page_number]["page_dims"]

    if page_number < 1 or page_number > len(images):
        raise HTTPException(status_code=400, detail="Invalid page number")

    page_image = images[page_number - 1]
    # page_blocks = [block for block in blocks if block["page"] == page_number]

    return {
        "page_image": page_image["base64_img"],
        "xml_page_dimensions": page_dims,
        "blocks": page_blocks,
    }


@router.get("/metadata/{tmp_dir}/{pdf_name}")
# @ensure_db
async def get_pdf_metadata(tmp_dir: str, pdf_name: str):
    pdf_path = SHARED_TMP_UPLOAD_DIR / tmp_dir / pdf_name
    metadata_path = pdf_path.with_name(pdf_path.stem + "_metadata.xml")

    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata file not found")

    task_id = f"{tmp_dir}_{pdf_name}_metadata"
    task = AsyncResult(task_id, app=celery_app)

    if not task.successful():
        if task.state == "PENDING":
            task = process_metadata_task.apply_async(args=(str(metadata_path),), task_id=task_id)
            return {"status": "processing", "task_id": task.id}
        elif task.state in ["PROGRESS", "FAILURE"]:
            return {"status": task.state, "task_id": task_id}

    result = task.result
    return {
        "status": "success",
        "metadata": result["metadata"],
    }
