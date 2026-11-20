import os
import tempfile
import logging
import fitz
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PDFToImage:
    @classmethod
    def convert(cls, pdf_path: str, max_pages: int = 5):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise Exception("Failed to open PDF.")

        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            raise Exception("PDF has 0 pages.")

        result = []
        pages_to_convert = min(max_pages, total_pages)

        for page_num in range(pages_to_convert):
            try:
                page = doc.load_page(page_num)
                dpi_settings = [300, 250, 200, 150]
                image_data = None

                for dpi in dpi_settings:
                    scale = dpi / 72
                    mat = fitz.Matrix(scale, scale)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img_bytes = pix.tobytes("png")
                    if len(img_bytes) / (1024 * 1024) < 1.0:
                        image_data = img_bytes
                        break

                if image_data is None:
                    scale = 150 / 72
                    mat = fitz.Matrix(scale, scale)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    pil_img = Image.open(io.BytesIO(pix.tobytes("png")))
                    for quality in range(95, 10, -5):
                        buffer = io.BytesIO()
                        pil_img.save(buffer, format="JPEG", quality=quality)
                        if len(buffer.getvalue()) / (1024 * 1024) < 1.0:
                            image_data = buffer.getvalue()
                            break

                if image_data is None:
                    width, height = pil_img.size
                    while True:
                        width = int(width * 0.9)
                        height = int(height * 0.9)
                        resized_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
                        buffer = io.BytesIO()
                        resized_img.save(buffer, format="JPEG", quality=40)
                        if len(buffer.getvalue()) / (1024 * 1024) < 1.0:
                            image_data = buffer.getvalue()
                            break

                if image_data:
                    result.append(image_data)

            except Exception as e:
                logger.error(f"Failed to convert page {page_num+1}: {e}")
                continue

        doc.close()
        if not result:
            raise Exception("Could not extract any images from the PDF.")
        return result