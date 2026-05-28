from services import ET
from utils.normalize_text import normalize_text as norm


def auto_label_blocks(page_blocks, metadata_path):
    # Parse the metadata XML
    metadata_tree = ET.parse(metadata_path)
    metadata_root = metadata_tree.getroot()

    metadata = {elem.tag.lower(): elem.text.strip() for elem in metadata_root if elem.text}

    for page_number in page_blocks:
        page = page_blocks[page_number]
        blocks = page["blocks"]
        for block in blocks:
            norm_block_text = norm(block["text"])
            for key, value in metadata.items():
                norm_val = norm(value)
                if norm_val in norm_block_text or norm_block_text in norm_val:
                    block["label"] = key
                    break
    return page_blocks
