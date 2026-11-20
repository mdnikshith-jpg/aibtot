import os
from app.services.pdf_to_image import PDFToImage
from app.services.ocr_service import OCRService
from app.services.ai_analyzer import AIAnalyzer
import logging

logger = logging.getLogger(__name__)

def process_pdf(pdf_path: str, max_pages: int = 5, user_text: str = "") -> dict:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    images = PDFToImage.convert(pdf_path, max_pages=max_pages)
    ocr = OCRService()
    full_text = ""
    for idx, img_bytes in enumerate(images, start=1):
        try:
            page_text = ocr.extract_text(img_bytes)
            if page_text:
                full_text += f"\n--- Page {idx} ---\n" + page_text
        except Exception as e:
            logger.error(f"OCR failed on page {idx}: {e}")
    if not full_text.strip():
        raise Exception("No text could be extracted.")
    data = AIAnalyzer.analyze_document(full_text, filename=os.path.basename(pdf_path), user_text=user_text)
    for k in ["subject_code", "subject_name", "semester", "module"]:
        if k not in data: data[k] = "UNKNOWN"
    if "questions" not in data: data["questions"] = []
    return data

def process_timetable_pdf(pdf_path: str, max_pages: int = 5, user_text: str = "") -> dict:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    images = PDFToImage.convert(pdf_path, max_pages=max_pages)
    ocr = OCRService()
    full_text = ""
    for idx, img_bytes in enumerate(images, start=1):
        try:
            page_text = ocr.extract_text(img_bytes)
            if page_text:
                full_text += f"\n--- Page {idx} ---\n" + page_text
        except Exception as e:
            logger.error(f"OCR failed on page {idx}: {e}")
    if not full_text.strip():
        raise Exception("No text could be extracted.")
    data = AIAnalyzer.analyze_timetable(full_text, filename=os.path.basename(pdf_path), user_text=user_text)
    for k in ["semester", "subjects", "module", "schedule"]:
        if k not in data:
            data[k] = "UNKNOWN" if k not in ["subjects", "schedule"] else []
    return data