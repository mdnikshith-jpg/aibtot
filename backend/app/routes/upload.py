import os
import uuid
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import File as DBFile
from app.auth import verify_bot_api_key
from app.services.pdf_processor import process_pdf
from app.config import BACKEND_URL
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Upload"])

@router.post("/upload")
async def upload_file(
    file = File(...),
    semester: str = Form(None),
    subject: str = Form(None),
    module: str = Form(None),
    user_text: str = Form(""),
    is_bot: bool = Depends(verify_bot_api_key)
):
    temp_dir = "/tmp" if os.name == "posix" else "C:\\temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        try:
            ai_data = process_pdf(temp_path, max_pages=5, user_text=user_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

        final_semester = semester if semester else ai_data.get("semester", "Unknown")
        final_subject = subject if subject else ai_data.get("subject_name", "Unknown")
        final_module = module if module else ai_data.get("module", "Unknown")

        # 🚀 Upload to Cloudinary instead of local storage
        result = cloudinary.uploader.upload(
            temp_path, 
            resource_type="raw", 
            public_id=f"notes/{uuid.uuid4()}_{file.filename}",
            folder=f"{final_semester}/{final_subject}"
        )
        file_url = result['secure_url']

        db: Session = next(get_db())
        db_file = DBFile(
            original_filename=file.filename,
            saved_filename=file.filename,
            semester=final_semester,
            subject=final_subject,
            module=final_module,
            file_url=file_url,  # Save Cloudinary URL
            uploaded_by=None,
            file_size=os.path.getsize(temp_path),
            mime_type=file.content_type
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return {
            "id": db_file.id,
            "filename": db_file.original_filename,
            "semester": db_file.semester,
            "subject": db_file.subject,
            "module": db_file.module,
            "download_url": f"{BACKEND_URL}/download/{db_file.id}",
            "preview_url": f"{BACKEND_URL}/preview/{db_file.id}"
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))