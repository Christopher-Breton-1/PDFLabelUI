from celery import shared_task
from services.auto_label import auto_label_blocks
from services.pdf_processor import pdf_to_images
from services.xml_processor import extract_blocks_from_xml
from services.xml_processor import extract_metadata
from pathlib import Path


@shared_task(ignore_result=False)
def process_pdf_task(pdf_path: str, xml_path: str, metadata_path: str):
    # implement your logic for pdf to images, xml parsing, and metadata processing
    images = pdf_to_images(pdf_path)  # replace with your pdf-to-images logic
    page_blocks = extract_blocks_from_xml(xml_path)  # replace with xml parsing logic

    if Path(metadata_path).exists():
        page_blocks = auto_label_blocks(page_blocks, metadata_path)

    return {"images": images, "xml_page": page_blocks}


@shared_task(ignore_result=False)
def process_metadata_task(metadata_path: str):
    if not Path(metadata_path).exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    metadata = extract_metadata(metadata_path)
    return {"metadata": metadata}
