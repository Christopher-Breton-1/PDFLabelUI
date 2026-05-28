import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
from zipfile import ZipFile
from main import app
from services.xml_processor import extract_blocks_from_xml
from services.pdf_processor import pdf_to_images

client = TestClient(app)

UPLOAD_DIR = Path("uploads")
TEST_ZIP_PATH = UPLOAD_DIR / "test_upload.zip"
TEST_PDF_PATH = UPLOAD_DIR / "test.pdf"
TEST_XML_PATH = UPLOAD_DIR / "test.xml"
TEST_METADATA_PATH = UPLOAD_DIR / "test_metadata.xml"


@pytest.fixture(scope="module")
def setup_test_environment():
    # Create test upload directory
    UPLOAD_DIR.mkdir(exist_ok=True)

    # Create a sample zip file with PDF and XML
    with ZipFile(TEST_ZIP_PATH, "w") as zip_file:
        zip_file.write("test_data/test.pdf", arcname="test.pdf")
        zip_file.write("test_data/test.xml", arcname="test.xml")
        zip_file.write("test_data/test_metadata.xml", arcname="test_metadata.xml")

    yield

    # Cleanup after tests
    if UPLOAD_DIR.exists():
        for file in UPLOAD_DIR.iterdir():
            file.unlink()
        UPLOAD_DIR.rmdir()


def test_upload_zip(setup_test_environment):
    with open(TEST_ZIP_PATH, "rb") as file:
        response = client.post("/upload", files={"file": (TEST_ZIP_PATH.name, file)})

    assert response.status_code == 200
    data = response.json()

    assert "pdfs" in data
    assert "xmls" in data
    assert "metadata_xmls" in data
    assert len(data["pdfs"]) == 1
    assert len(data["xmls"]) == 1
    assert len(data["metadata_xmls"]) == 1

    assert Path(data["pdfs"][0]).name == "test.pdf"
    assert Path(data["xmls"][0]).name == "test.xml"
    assert Path(data["metadata_xmls"][0]).name == "test_metadata.xml"


def test_get_pdf_page_blocks(setup_test_environment):
    # Ensure the upload step works
    with open(TEST_ZIP_PATH, "rb") as file:
        client.post("/upload", files={"file": (TEST_ZIP_PATH.name, file)})

    # Request the first page's blocks
    response = client.get("/pdf/test.pdf/page/1")

    assert response.status_code == 200
    data = response.json()

    assert "page_image" in data
    assert "blocks" in data
    assert isinstance(data["blocks"], list)

    for block in data["blocks"]:
        assert "page" in block
        assert "text" in block
        assert "bbox" in block
        assert "label" in block


def test_extract_blocks_from_xml():
    # Load test XML
    blocks = extract_blocks_from_xml(TEST_XML_PATH)

    assert isinstance(blocks, list)
    assert len(blocks) > 0

    for block in blocks:
        assert "page" in block
        assert "text" in block
        assert "bbox" in block
        assert "label" in block
        assert isinstance(block["page"], int)
        assert isinstance(block["text"], str)
        assert isinstance(block["bbox"], tuple)
        assert isinstance(block["label"], str)


def test_pdf_to_images():
    # Convert PDF to images
    images = pdf_to_images(TEST_PDF_PATH)

    assert isinstance(images, list)
    assert len(images) > 0

    for image in images:
        assert isinstance(image, str)
        assert image.startswith("iVBOR")  # Check if it's a base64 PNG
