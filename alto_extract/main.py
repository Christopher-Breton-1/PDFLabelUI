from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import subprocess

app = FastAPI()


class GenerateRequest(BaseModel):
    pdf_path: str


@app.post("/generate")
async def generate(request: GenerateRequest):
    pdf_path = Path(request.pdf_path)
    output_path = pdf_path.with_suffix(".xml")
    metadata_output_path = pdf_path.with_name(f"{pdf_path.stem}_metadata.xml")
    other_data_output_path = pdf_path.with_suffix(".xml_data")

    # Validate the input file
    if not pdf_path.exists():
        raise HTTPException(status_code=400, detail="PDF file does not exist.")

    # Run pdfalto
    try:
        subprocess.run(["pdfalto", str(pdf_path), str(output_path)], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"PDFAlto Error: {e}")

    # Respond with success
    return {
        "xml_path": str(output_path),
        "metadata_xml_path": str(metadata_output_path),
        "other_data": str(other_data_output_path),
    }
