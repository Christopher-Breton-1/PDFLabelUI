from fastapi import APIRouter
from models import Box
from typing import List

router = APIRouter()


@router.post("/add-box")
async def add_box(box: Box):
    # logic to add a new box
    return {"status": "success", "box": box}


@router.post("/merge-boxes")
async def merge_boxes(box_ids: List[int]):
    # logic to merge boxes
    return {"status": "success", "merged_box": "details here"}


@router.get("/export/json")
async def export_json():
    # logic to return annotations in JSON format
    return {"annotations": "data here"}


@router.get("/export/xml")
async def export_xml():
    # logic to return updated XML
    return {"annotations": "data here"}
