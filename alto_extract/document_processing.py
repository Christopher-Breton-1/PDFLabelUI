# import pdfplumber
from collections import defaultdict

import openai
from dotenv import load_dotenv
import subprocess
import os
import shutil
import xml.etree.ElementTree as ET
import re

import numpy as np
from config import config
from chunks import build_chunks, get_embeddings_from_chunks

# Initialize the vector store and the clustering and searching instance
vector_store = config.vector_store
hnsw_cluster_search = config.cluster_search_instance
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI()


def check_with_o1_mini(query, instructions):
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": [{"type": "text", "text": instructions}]
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )
    result = completion.choices[0].message.content
    match result:
        case "True":
            return True
        case "False":
            return False
        case _:
            raise ValueError("Cannot parse o1 response of ", result)


def process_new_documents() -> None:
    """
    Process new documents in the config.doc_paths list, create chunks and embeddings,
    save them to the vector store, and update the clustering and searching index.
    """
    print("PROCESSING NEW DOCUMENTS")
    for file_path in config.doc_paths:
        print(document_files_exist(file_path))
        if not document_files_exist(file_path):
            # Create chunks and embeddings
            chunks, embeddings = get_chunks_and_embeddings(file_path)

            # Save the chunks and embeddings to the vector store
            vector_store.save_chunks_and_embeddings(file_path, chunks, embeddings)

            # Update the document index (if necessary, depending on your implementation)
            hnsw_cluster_search.update_index(file_path, embeddings)

            # Add the new document path to the config.doc_paths list NOT NEEDED ANYMORE
            # config.doc_paths.append(file_path)


def document_files_exist(document_path: str) -> bool:
    """
    Check if document files exist in the vector store.

    Args:
        document_path (str): The path to the document file.

    Returns:
        bool: True if the document files exist, False otherwise.
    """
    return vector_store.document_exists(document_path)


def get_chunks_and_embeddings(document_path: str) -> tuple[list[str], list[list[float]]]:
    """
    Get the chunks and embeddings for a given document path. If they don't exist,
    generate and save them to the vector store.

    Args:
        document_path (str): The path to the document file.

    Returns:
        tuple: A tuple containing the list of chunks and the numpy array of embeddings.
    """
    chunks, embeddings = config.vector_store.load_chunks_and_embeddings(document_path)
    if chunks is None or embeddings is None:
        print(f"Warning: Chunks or embeddings not found for {document_path}. Generating chunks and embeddings again.")
        if not document_path.endswith('.pdf'):
            with open(document_path, "r", encoding="utf-8") as file:
                _document = file.read()
            chunks, embeddings = build_chunks(_document)
        else:
            _pdf = PDF(document_path, build_sections=False)
            chunks = _pdf.paragraph_texts
            del _pdf
            embeddings = get_embeddings_from_chunks(chunks)
    return chunks, embeddings


class PDFParser:
    def __init__(self):
        self.namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v3#'}

    def run_pdfalto(self, pdf_path, xml_path):
        try:
            subprocess.run(["pdfalto", "-noImage", pdf_path, xml_path], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running pdfalto: {e}")

    def parse_blocks(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        blocks = []
        for page_idx, page in enumerate(root.findall('alto:Layout/alto:Page', self.namespace)):
            page_height = float(page.attrib.get("HEIGHT", 0))
            for block in page.findall('alto:PrintSpace/alto:TextBlock', self.namespace):
                block_text = "\n".join(
                    " ".join(token.get('CONTENT') for token in line.findall('alto:String', self.namespace))
                    for line in block.findall('alto:TextLine', self.namespace)
                ).strip()

                if block_text:
                    vpos = float(block.attrib.get("VPOS", 0))
                    position = "middle"
                    if vpos < page_height * 0.2:
                        position = "top"
                    elif vpos > page_height * 0.8:
                        position = "bottom"

                    blocks.append({
                        "page": page_idx + 1,
                        "position": position,
                        "text": block_text
                    })

        return blocks

    def identify_headers(self, blocks):
        headers = {}
        header_keywords = {"abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"}

        for block in blocks:
            text = block["text"].lower()
            if (text in header_keywords or block["text"].isupper() or
                re.match(r"^\d+\.\s*[A-Za-z]+", block["text"])):
                headers[block["text"]] = block

        return headers

    def group_sections(self, blocks, headers):
        sections = defaultdict(list)
        current_header = None

        for block in blocks:
            if block["text"] in headers:
                current_header = block["text"]
                sections[current_header] = []
            elif current_header:
                sections[current_header].append(block["text"])

        return sections

    def merge_continued_sections(self, sections):
        merged_sections = {}
        previous_header = None

        for header, content in sections.items():
            if previous_header and len(content) < 5:
                merged_sections[previous_header].extend(content)
            else:
                merged_sections[header] = content
                previous_header = header

        return merged_sections

    def clean_sections(self, sections):
        cleaned_sections = {}
        for header, content in sections.items():
            filtered_content = [line for line in content if not self.is_footer(line)]
            if filtered_content:
                cleaned_sections[header] = filtered_content

        return cleaned_sections

    @staticmethod
    def is_footer(text):
        footer_keywords = ["page", "doi", "https://", "www.", "journal"]
        return any(keyword in text.lower() for keyword in footer_keywords)

    def parse_pdf(self, pdf_path, xml_output_path):
        xml_path = os.path.join(xml_output_path, os.path.basename(pdf_path).replace(".pdf", ".xml"))
        if not os.path.exists(xml_output_path):
            os.makedirs(xml_output_path, exist_ok=True)

        self.run_pdfalto(pdf_path, xml_path)

        blocks = self.parse_blocks(xml_path)
        headers = self.identify_headers(blocks)
        sections = self.group_sections(blocks, headers)
        merged_sections = self.merge_continued_sections(sections)
        final_sections = self.clean_sections(merged_sections)

        os.remove(xml_path)
        return final_sections



if __name__ == "__main__":
    # pdf_path = "C:/Users/PC/Desktop/Papers for my memory system/clustering/wang2017.pdf.pdf"
    pdf_path = "../documents/clustering/wang2017.pdf"
    xml_path = "./xml/"
    alto = PDFParser()
    # parsed_doc, doc_metadata, sections = alto.process_pdf(pdf_path, xml_path)
    sections = alto.parse_pdf(pdf_path, xml_path)
    # print(parsed_doc)

    # print("\n", doc_metadata)

    print("\n\n")
    print(len(sections))
    for section in sections:
        print(section, ":")
        print(sections[section])
        print("\n")
