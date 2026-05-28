import os
import zipfile
import uuid
from fastapi import APIRouter, UploadFile, HTTPException
from config import SHARED_TMP_UPLOAD_DIR

router = APIRouter()


@router.post("/")
async def upload_zip(file: UploadFile):
    # ensure only zip files are accepted
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed.")

    # generate a unique temp directory for this upload
    _uuid = str(uuid.uuid4())
    temp_dir = SHARED_TMP_UPLOAD_DIR / _uuid
    temp_dir.mkdir(parents=True, exist_ok=True)

    # save the uploaded zip file to the temp directory
    zip_file_path = temp_dir / file.filename
    with open(zip_file_path, "wb") as f:
        f.write(file.file.read())

    # extract the zip contents into the same temp directory
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            print(zip_ref.infolist())
            zip_ref.extractall(temp_dir)
    except zipfile.BadZipFile:
        os.rmdir(temp_dir)
        raise HTTPException(status_code=400, detail="Invalid ZIP file.")

    # remove the uploaded zip file after extraction
    os.remove(zip_file_path)

    # collect all pdfs in the temp directory
    pdfs = list(temp_dir.glob("*.pdf"))

    # ensure all pdfs have corresponding metadata files (we will generate xml later)
    if not pdfs:
        # remove temp directory if no pdfs found as well as any files in that directory
        for file in temp_dir.iterdir():
            file.unlink()
        os.rmdir(temp_dir)
        raise HTTPException(status_code=400, detail="No PDFs found in the ZIP file.")

    print("UPLOAD SUCCESSFUL:", file.filename)
    print("Extracted to:", temp_dir)
    print("PDFS:", pdfs)
    # could perhaps have a move_to_shared function that moves the pdf files to shared dir and also validates them or somehting.
    # for now i  will simply directly place the files in shared dir.

    return {
        "filename": file.filename,
        "temp_dirname": _uuid,
        "upload_dir": str(temp_dir),
        "pdfs": [str(pdf) for pdf in pdfs],
    }
