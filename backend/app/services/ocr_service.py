import requests
from app.config import OCR_API_KEYS
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.api_keys = OCR_API_KEYS

    def extract_text(self, image_content):
        last_error = None
        for idx, api_key in enumerate(self.api_keys):
            try:
                response = requests.post(
                    "https://api.ocr.space/parse/image",
                    files={"file": ("page.jpg", image_content, "image/jpeg")},
                    data={
                        "apikey": api_key,
                        "language": "eng",
                        "OCREngine": "2",
                        "scale": True,
                        "isTable": False
                    },
                    timeout=60
                )
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                result = response.json()
                if result.get("IsErroredOnProcessing"):
                    error = result.get("ErrorMessage")
                    if isinstance(error, list):
                        error = " | ".join(error)
                    raise Exception(error)
                parsed = result.get("ParsedResults", [])
                if not parsed:
                    return ""
                return parsed[0].get("ParsedText", "")
            except Exception as e:
                last_error = e
        raise Exception(f"All OCR keys failed. Last error: {last_error}")