from pdf2image import convert_from_bytes
from io import BytesIO

async def generate_preview(file_bytes):
    images = convert_from_bytes(file_bytes, first_page=1, last_page=1)
    output = BytesIO()
    images[0].save(output, format="JPEG")
    output.seek(0)
    return output
