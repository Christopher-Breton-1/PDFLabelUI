from pdf2image import convert_from_path
from io import BytesIO
import base64


def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=150)
    image_data = []
    for image in images:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        image_data.append({"base64_img": encoded_image})
    return image_data

