import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from app.database import get_db
from app.models import File as DBFile, User
from app.auth import get_current_admin_user

router = APIRouter(tags=["Files"])

@router.get("/semesters")
def list_semesters(db: Session = Depends(get_db)):
    sems = db.query(DBFile.semester).distinct().all()
    return [s[0] for s in sems if s[0] and s[0] != "Unknown"]

@router.get("/subjects/{semester}")
def list_subjects(semester: str, db: Session = Depends(get_db)):
    subjects = db.query(DBFile.subject).filter(DBFile.semester == semester).distinct().all()
    return [s[0] for s in subjects if s[0] and s[0] != "Unknown"]

@router.get("/files/{semester}/{subject}")
def list_files(semester: str, subject: str, db: Session = Depends(get_db)):
    files = db.query(DBFile).filter(DBFile.semester == semester, DBFile.subject == subject).all()
    return [{"id": f.id, "filename": f.original_filename, "module": f.module, "upload_date": f.upload_date} for f in files]

@router.get("/preview/{file_id}")
async def preview_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return RedirectResponse(url=db_file.file_url)  # Redirects to Cloudinary

@router.get("/download/{file_id}")
async def download_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return RedirectResponse(url=db_file.file_url)  # Redirects to Cloudinary

# ... keep DELETE and PUT endpoints as they were (just remove file path deletion)