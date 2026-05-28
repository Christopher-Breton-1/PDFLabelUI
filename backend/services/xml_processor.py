from pathlib import Path

from services import ET


def extract_metadata(metadata_path: str):
    """
    Extract metadata fields from an XML file.

    Args:
        metadata_path (str): Path to the metadata XML file.

    Returns:
        dict: Extracted metadata fields.
    """
    if not Path(metadata_path).exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    tree = ET.parse(metadata_path)
    root = tree.getroot()

    # Extract metadata fields (adjust according to your XML structure)
    metadata = {
        "TITLE": root.findtext("TITLE", default="Unknown"),
        "SUBJECT": root.findtext("SUBJECT", default="Unknown"),
        "KEYWORDS": root.findtext("KEYWORDS", default="Unknown"),
        "AUTHOR": root.findtext("AUTHOR", default="Unknown"),
        "CREATOR": root.findtext("CREATOR", default="Unknown"),
        "PRODUCER": root.findtext("PRODUCER", default="Unknown"),
        "CREATIONDATE": root.findtext("CREATIONDATE", default="Unknown"),
        "MODIFICATIONDATE": root.findtext("MODIFICATIONDATE", default="Unknown"),
    }

    return metadata

def get_num_pdf_pages_from_xml(xml_path):
    namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v3#'}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    return len(root.findall('alto:Layout/alto:Page', namespace))

def extract_blocks_from_xml(xml_path):
    namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v3#'}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    _page = {}
    current_block_no = 0
    for page in root.findall('alto:Layout/alto:Page', namespace):
        page_index = int(page.get('ID', 0).lower().replace("page", ""))
        _page[page_index] = {"blocks": []}
        _page[page_index]["page_dims"] = {"width": float(page.get("WIDTH")), "height": float(page.get("HEIGHT"))}
        for block in page.findall('alto:PrintSpace/alto:TextBlock', namespace):
            block_text = "\n".join(
                " ".join([token.get('CONTENT', '') for token in line.findall('alto:String', namespace)])
                for line in block.findall('alto:TextLine', namespace)
            ).strip()
            if not block_text:
                continue

            hpos = float(block.get('HPOS', 0))
            vpos = float(block.get('VPOS', 0))
            width = float(block.get('WIDTH', 0))
            height = float(block.get('HEIGHT', 0))
            bbox = (hpos, vpos, hpos + width, vpos + height)

            _page[page_index]["blocks"].append(
                {"id": current_block_no, "text": block_text, "bbox": bbox, "label": "Pick_label"})
            current_block_no += 1
    return _page
