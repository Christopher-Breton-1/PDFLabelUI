import os.path
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel
from services.xml_processor import get_num_pdf_pages_from_xml

from config import PDFALTO_API_URL, SHARED_DIR, SHARED_TMP_UPLOAD_DIR

router = APIRouter()


class GenerateBatchRequest(BaseModel):
    pdf_files: list[str]
    tmp_dirname: str


@router.post("/generate")
async def generate_xml(pdf_file: str):
    # pdf_path = SHARED_DIR / pdf_file
    # TODO Shared dir is the issue here. I should move the pdfs to shared dir
    #  while alto works on them before brining them back
    pdf_path = Path(pdf_file)
    output_xml = pdf_path.with_suffix(".xml")

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found. Kbye")

    # call the pdfalto api
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(PDFALTO_API_URL, json={"pdf_path": str(pdf_file)})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"PDFalto API error: {response.json().get('error', 'Unknown error')}"
                )
            result = response.json()

            if not output_xml.exists():
                raise HTTPException(status_code=500, detail="Failed to generate XML.")
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"PDFalto error: {e}")

        return {
            "num_pages": get_num_pdf_pages_from_xml(result["xml_path"]),
            "output_xml": result["xml_path"],
            "output_metadata_xml": result["metadata_xml_path"],
            "other_data": result["other_data"],
        }


@router.post("/generate_batch")
async def generate_xml_batch(request: GenerateBatchRequest):
    results = {}

    pdf_files = request.pdf_files
    tmp_dirname = request.tmp_dirname

    for pdf_file in pdf_files:
        print("PDF PATH EXISTS: ", os.path.exists(pdf_file))
        try:
            result = await generate_xml(str(pdf_file))
            pdf_file = Path(pdf_file).relative_to(Path(SHARED_DIR))

            results[pdf_file] = {
                "num_pages":  result["num_pages"],
                "tmp_dir": "/" + tmp_dirname + "/",
                "filename": pdf_file.parts[-1],
                "xml_filepath": result["output_xml"],
                "xml_metadata_filepath": result["output_metadata_xml"],
                "other_data_filepath": result["other_data"],
            }
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code,
                                detail=f"Error in {pdf_file}: {e.detail}, files: {pdf_files}")
    return results
